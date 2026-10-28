"""Explicit existing-topic revisions and site deployments; never chooses a new topic."""
from pathlib import Path
import re
import hashlib
from .core import (PublisherError, digest, load_state, make_post, read_json, safe_path,
                   update_indexes, validate_markdown, write_json)

SITE_FILE = '.publisher/site.json'
PLAN_FILE = 'config/maintenance.json'


def site_digest(root):
    root = Path(root)
    pairs = []
    for p in sorted((root/'blog').rglob('*')):
        if p.is_symlink():
            raise PublisherError('site-symlink-forbidden')
        if p.is_file() and not any(x in {'.jekyll-cache', '.sass-cache', 'vendor', '_site'} for x in p.relative_to(root/'blog').parts):
            data=p.read_bytes()
            if p.suffix.lower() in {'.md','.html','.css','.js','.json','.yml','.yaml','.svg','.xml','.txt'} or p.name in {'Gemfile','Gemfile.lock','markdown-it.LICENSE'}:
                data=data.replace(b'\r\n',b'\n')
            pairs.append(p.relative_to(root).as_posix() + ':' + hashlib.sha256(data).hexdigest())
    return digest('\n'.join(pairs))


def site_pending(root):
    p = Path(root)/SITE_FILE
    return p.exists() and read_json(p).get('deployed_digest') != site_digest(root)


def assert_published_files(root, entry):
    from .assets import verify_assets
    verify_assets(root,entry)
    body = safe_path(root, entry['target_path']).read_text(encoding='utf-8')
    if digest(body) != entry['content_hash']:
        raise PublisherError('published-source-changed-review-required')
    if safe_path(root, entry['post_path']).read_text(encoding='utf-8') != make_post(entry, body):
        raise PublisherError('published-post-changed-review-required')
    return body


def maintenance_prepare(root, private, state, catalog, *, dry_run, today):
    root = Path(root)
    if (root/PLAN_FILE).exists():
        plan = read_json(root/PLAN_FILE)
        if plan.get('schema_version') != 1 or plan.get('kind') not in {'revision', 'withdraw'}:
            raise PublisherError('invalid-maintenance-plan')
        key = plan['topic_id']
        if key not in state['topics'] or key not in catalog:
            raise PublisherError('maintenance-requires-existing-topic')
        entry = state['topics'][key]
        applied = entry.get('revision', {}).get('plan_hash') == digest((root/PLAN_FILE).read_text(encoding='utf-8'))
        if not applied:
            if any(t.get('publication_status') != 'withdrawn' and any(t[k] != 'complete' for k in ('github_status','notion_status','blog_status')) for t in state['topics'].values()):
                raise PublisherError('finish-current-publication-before-revision')
            old = assert_published_files(root, entry)
            if entry['content_hash'] != plan['from_hash'] or entry.get('notion_page_id') != plan['notion_page_id']:
                raise PublisherError('revision-baseline-mismatch')
            for field in ('title_ko','category','subcategory','target_path'):
                if entry[field] != catalog[key][field]:
                    raise PublisherError('revision-identity-mismatch')
            if state.get('notion_uncertain') or entry.get('notion_pending_chunk'):
                raise PublisherError('resolve-uncertainty-before-revision')
            backup = safe_path(root, plan['previous_body_path']).read_text(encoding='utf-8')
            if digest(backup) != digest(old):
                raise PublisherError('revision-backup-mismatch')
            body = safe_path(private, catalog[key]['source_path']).read_text(encoding='utf-8')
            validate_markdown(body)
            if plan['kind'] == 'revision' and (digest(body) != plan['to_hash'] or digest(body) == digest(old)):
                raise PublisherError('revision-candidate-mismatch')
            if plan['kind'] == 'withdraw':
                body = old
            result = {'action':plan['kind'], 'topic_id':key,'date':today,'dry_run':dry_run}
            if dry_run:
                return result
            from .assets import resolve_assets, copy_assets
            source_content_hash=digest(body)
            body, assets=resolve_assets(root,private,catalog[key],body)
            copy_assets(root,private,assets,entry.get("assets",[]))
            revision = {'plan_hash':digest((root/PLAN_FILE).read_text(encoding='utf-8')),
                        'from_hash':entry['content_hash'],'previous_body_path':plan['previous_body_path'],
                        'notion_page_id':entry['notion_page_id'], 'old_blocks':{},'archived_blocks':{},'status':'pending'}
            if assets:entry.update(assets=assets, source_content_hash=source_content_hash)
            entry.update(render_version=2,revision=revision,content_hash=digest(body),blog_status='pending')
            if plan['kind'] == 'revision':
                entry['notion_status'] = 'pending'
            else:
                entry['publication_status'] = 'withdrawn'
                revision['status'] = 'withdrawn-notion-preserved'
            safe_path(root,entry['target_path']).write_text(body,encoding='utf-8')
            safe_path(root,entry['post_path']).write_text(make_post(entry,body),encoding='utf-8')
            update_indexes(root,state,read_json(root/'config/publisher.json'))
            write_json(root/'.publisher/state.json',state)
            if (root/SITE_FILE).exists():
                site = read_json(root/SITE_FILE);site['pending_digest'] = site_digest(root);write_json(root/SITE_FILE,site)
            return result
    # Existing platform recovery must finish before a site-only update or new topic.
    if any(t.get('publication_status') != 'withdrawn' and any(t[k] != 'complete' for k in ('github_status','notion_status','blog_status')) for t in state['topics'].values()):
        return None
    if site_pending(root):
        result = {'action':'site-update','topic_id':None,'date':today,'dry_run':dry_run}
        if not dry_run:
            site = read_json(root/SITE_FILE);site['pending_digest'] = site_digest(root);write_json(root/SITE_FILE,site)
        return result
    return None


def normalized(value):
    """Ignore API bookkeeping but retain text, formatting, links, colors and block contents."""
    if isinstance(value,list):
        return [normalized(v) for v in value]
    if not isinstance(value,dict):
        return value
    ignored = {'object','id','parent','created_time','last_edited_time','created_by','last_edited_by',
               'has_children','archived','in_trash','plain_text','href','request_id'}
    result = {}
    for k,v in value.items():
        if k in ignored or k == 'children':continue
        if k == 'annotations':
            v = {a:b for a,b in v.items() if b is True or (a == 'color' and b != 'default')}
            if not v:continue
        if k == 'icon' and v is None:continue
        if k == 'color' and v == 'default':continue
        if k == 'is_toggleable' and v is False:continue
        if k in {'caption','link'} and not v:continue
        result[k] = normalized(v)
    return result


def first_difference(actual, expected, path="block"):
    if isinstance(actual,dict) and isinstance(expected,dict):
        if set(actual) != set(expected):
            return path + ".keys(actual=" + ",".join(sorted(set(actual)-set(expected))) + ";expected=" + ",".join(sorted(set(expected)-set(actual))) + ")"
        for key in expected:
            if actual[key] != expected[key]:return first_difference(actual[key],expected[key],path+"."+key)
    if isinstance(actual,list) and isinstance(expected,list):
        if len(actual) != len(expected):return path+".length"
        for i,(a,b) in enumerate(zip(actual,expected)):
            if a != b:return first_difference(a,b,path+"["+str(i)+"]")
    return path + ".value"


def block_matches(client, actual, expected):
    observed, planned = normalized(actual), normalized(expected)
    if observed != planned:
        # Field names/indices only: never log payloads, tokens or user text.
        raise PublisherError("notion-manual-edit-protected:" + first_difference(observed,planned))
    children = expected[expected['type']].get('children',[])
    if children or actual.get('has_children'):
        observed = client.children(actual['id'])
        if len(observed) != len(children):
            raise PublisherError("notion-manual-edit-protected:children.length")
        return all(block_matches(client,a,b) for a,b in zip(observed,children))
    return True


def sync_revision(root, state, entry, config, parent, client, save):
    from .notion import chunks, links_from_block, AmbiguousWrite
    revision = entry['revision']
    if entry.get('notion_page_id') != revision['notion_page_id']:
        raise PublisherError('revision-page-id-changed')
    page_id = entry['notion_page_id']
    # Revisions never create or rediscover a replacement page/hierarchy.
    expected_parent = parent
    for title in (config['categories'][entry['category']],entry['subcategory']):
        pages = [b for b in client.children(expected_parent) if b.get('type') == 'child_page' and b['child_page']['title'] == title]
        if len(pages) != 1:raise PublisherError('revision-hierarchy-mismatch')
        expected_parent = pages[0]['id']
    pages = [b for b in client.children(expected_parent) if b.get('type') == 'child_page' and b['child_page']['title'] == entry['title_ko']]
    if len(pages) != 1 or pages[0]['id'] != page_id:raise PublisherError('revision-page-identity-mismatch')
    page = client.request('GET','pages/'+page_id)
    if page.get('archived') or page.get('in_trash'):raise PublisherError('revision-page-archived')
    existing = client.children(page_id)
    if not any(entry['github_url'] in links_from_block(b) for b in existing):raise PublisherError('revision-header-mismatch')
    body = assert_published_files(root,entry)
    old = safe_path(root,revision['previous_body_path']).read_text(encoding='utf-8')
    if digest(old) != revision['from_hash']:raise PublisherError('revision-backup-mismatch')
    old_expected = dict(chunks(old,entry['github_url']))
    expected = dict(chunks(body,entry['github_url']))
    def indexed(blocks):
        found = {}
        for b in blocks:
            for marker in links_from_block(b):
                if '?cs_chunk=' in marker:
                    if marker in found:raise PublisherError('notion-duplicate-revision-marker')
                    if marker not in old_expected and marker not in expected:raise PublisherError('notion-unknown-revision-marker')
                    found[marker] = b
        return found
    found = indexed(existing)
    # Persist old marker-to-block identities before appending or archiving anything.
    for marker, payload in old_expected.items():
        if marker in expected:continue
        if marker in found:
            b = found[marker]
            if not block_matches(client,b,payload):raise PublisherError('notion-manual-edit-protected')
            known = revision['old_blocks'].get(marker)
            if known and known != b['id']:raise PublisherError('notion-revision-block-id-changed')
            revision['old_blocks'][marker] = b['id']
        elif marker not in revision['archived_blocks'] and marker not in revision['old_blocks']:
            raise PublisherError('notion-previous-chunk-missing')
    save()
    for marker,payload in expected.items():
        if marker in found:
            if not block_matches(client,found[marker],payload):raise PublisherError('notion-manual-edit-protected')
            if entry.get('notion_pending_chunk') == marker:entry.pop('notion_pending_chunk');save()
            continue
        if entry.get('notion_pending_chunk') == marker:raise PublisherError('notion-chunk-uncertain-review-required')
        entry['notion_pending_chunk'] = marker;save()
        try:client.request('PATCH','blocks/'+page_id+'/children',{'children':[payload]})
        except AmbiguousWrite:raise
        except PublisherError:
            entry.pop('notion_pending_chunk',None);save();raise
        entry.pop('notion_pending_chunk',None);save()
    found = indexed(client.children(page_id))
    if not set(expected) <= set(found):raise PublisherError('notion-new-chunks-not-visible')
    for marker,payload in expected.items():
        if not block_matches(client,found[marker],payload):raise PublisherError('notion-new-chunks-mismatch')
    for marker,block_id in revision['old_blocks'].items():
        if marker in revision['archived_blocks']:continue
        current = client.request('GET','blocks/'+block_id)
        if current.get('archived') or current.get('in_trash'):
            if revision.get('archive_pending') != block_id:raise PublisherError('notion-unexpected-archive-review-required')
            revision['archived_blocks'][marker] = block_id;revision.pop('archive_pending',None);save();continue
        if revision.get('archive_pending') == block_id:raise PublisherError('notion-archive-uncertain-review-required')
        if not block_matches(client,current,old_expected[marker]):raise PublisherError('notion-manual-edit-protected')
        revision['archive_pending'] = block_id;save()
        try:client.request('PATCH','blocks/'+block_id,{'archived':True})
        except AmbiguousWrite:raise
        except PublisherError:
            revision.pop('archive_pending',None);save();raise
        confirmed = client.request('GET','blocks/'+block_id)
        if not (confirmed.get('archived') or confirmed.get('in_trash')):raise PublisherError('notion-archive-not-confirmed')
        revision['archived_blocks'][marker] = block_id;revision.pop('archive_pending',None);save()
    visible = indexed(client.children(page_id))
    if set(visible) != set(expected):raise PublisherError('notion-revision-final-marker-mismatch')
    revision['status'] = 'notion-complete'
    entry['notion_status'] = 'complete';entry.pop('notion_error',None);save()
