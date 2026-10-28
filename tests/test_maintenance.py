import copy
import json
from datetime import timedelta
from pathlib import Path
import unittest
from scripts import core,cli,notion,maintenance
import test_publisher as fixture
FakeNotion=fixture.FakeNotion
sample=fixture.sample

EDITORIAL = '''# 검증용 문서

실행 중인 자원과 실행 흐름을 구분하면 공유 범위를 이해할 수 있습니다.

## 공유와 분리

같은 힙 객체를 여러 스레드가 참조할 수 있습니다.

![공유 범위를 나타내는 직접 작성 도식](https://example.com/diagram.svg)

```java
System.out.println(2);
```

## 참고 자료

- [공식 자료](https://docs.oracle.com/en/java/javase/17/docs/api/)
'''

class RevisionNotion(FakeNotion):
    def __init__(self):
        super().__init__();self.entities={};self.lose_archive=False;self.reject_archive=False
    def children(self,parent):
        return [copy.deepcopy(b) for b in self.blocks.get(parent,[]) if not b.get('archived')]
    def add(self,parent,children):
        for item in children:
            item=copy.deepcopy(item);self.count+=1;item['id']='b'+str(self.count)
            nested=item[item['type']].pop('children',[])
            item['has_children']=bool(nested)
            self.entities[item['id']]=item;self.blocks.setdefault(parent,[]).append(item)
            if nested:self.add(item['id'],nested)
    def create_page(self,parent,title,children=None):
        self.count+=1;self.posts+=1;key='p'+str(self.count)
        self.blocks.setdefault(parent,[]).append({'type':'child_page','id':key,'child_page':{'title':title}})
        self.blocks[key]=[];self.add(key,children or [])
        return {'id':key}
    def request(self,method,path,payload=None):
        if method=='GET' and path.startswith('pages/'):return {'id':path.split('/')[1]}
        if method=='GET' and path.startswith('blocks/'):return copy.deepcopy(self.entities[path.split('/')[1]])
        if method=='PATCH' and path.endswith('/children'):
            self.patches+=1;self.add(path.split('/')[1],payload['children'])
            if self.lose_chunk_response:
                self.lose_chunk_response=False;raise notion.AmbiguousWrite('notion-write-uncertain')
            return {}
        if method=='PATCH' and payload=={'archived':True}:
            if self.reject_archive:raise core.PublisherError('notion-http-403')
            item=self.entities[path.split('/')[1]];item['archived']=True
            if self.lose_archive:
                self.lose_archive=False;raise notion.AmbiguousWrite('notion-write-uncertain')
            return copy.deepcopy(item)
        raise AssertionError((method,path))

class MaintenanceTests(unittest.TestCase):
    setUp=fixture.PublisherTests.setUp
    tearDown=fixture.PublisherTests.tearDown
    write_catalog=fixture.PublisherTests.write_catalog
    publish=fixture.PublisherTests.publish
    state=fixture.PublisherTests.state

    def setup_revision(self):
        self.publish();self.fake=RevisionNotion();self.config=core.read_json(self.root/'config/publisher.json')
        state=self.state();notion.sync(self.root,state,self.config,client=self.fake,parent='root')
        entry=state['topics']['test-001'];entry['blog_status']='complete'
        core.write_json(self.root/'.publisher/state.json',state)
        (self.root/'old.md').write_text(sample(),encoding='utf-8')
        self.plan={'schema_version':1,'kind':'revision','topic_id':'test-001','from_hash':entry['content_hash'],
                   'to_hash':core.digest(EDITORIAL),'notion_page_id':entry['notion_page_id'],'previous_body_path':'old.md'}
        core.write_json(self.root/maintenance.PLAN_FILE,self.plan)
        (self.private/self.topics[0]['source_path']).write_text(EDITORIAL,encoding='utf-8')
        return copy.deepcopy(entry)
    def sync(self):
        state=self.state();notion.sync(self.root,state,self.config,client=self.fake,parent='root');return state
    def test_editorial_arbitrary_headings_and_image(self):
        core.validate_markdown(EDITORIAL)
        self.assertIn('image',{b['type'] for b in notion.markdown_blocks(EDITORIAL)})
        for unsafe in (EDITORIAL.replace('![공유 범위를 나타내는 직접 작성 도식]','![]'),EDITORIAL+'\n<script>x</script>',EDITORIAL.replace('## 공유와 분리','## 핵심 요약')):
            with self.assertRaises(core.PublisherError):core.validate_markdown(unsafe)
    def test_revision_dry_run_unchanged(self):
        self.setup_revision();before={p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result=core.prepare(self.root,self.private,now=self.now)
        self.assertEqual(result['action'],'revision');self.assertEqual(before,{p:p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def test_revision_keeps_identity_and_new_hash(self):
        before=self.setup_revision();self.publish();entry=self.state()['topics']['test-001']
        for key in ('topic_id','published_date','notion_page_id','post_path','permalink','target_path','blog_url','github_url'):
            self.assertEqual(before[key],entry[key])
        self.assertEqual(entry['content_hash'],core.digest(EDITORIAL));self.assertEqual(self.publish()['action'],'recover')
        self.assertEqual(len(self.state()['topics']),1)
    def test_revision_wrong_baseline_stops(self):
        self.setup_revision();self.plan['from_hash']='a'*64;core.write_json(self.root/maintenance.PLAN_FILE,self.plan)
        with self.assertRaisesRegex(core.PublisherError,'baseline'):self.publish()
    def test_revision_reuses_page_and_keeps_manual_blocks(self):
        before=self.setup_revision();page=before['notion_page_id'];self.fake.add(page,[notion.block('paragraph',notion.rich('수동 메모'))])
        count=self.fake.posts;self.publish();state=self.sync();self.assertEqual(self.fake.posts,count)
        entry=state['topics']['test-001'];self.assertEqual(entry['notion_status'],'complete')
        self.assertEqual(len(entry['revision']['archived_blocks']),10)
        self.assertTrue(any('수동 메모' in json.dumps(b,ensure_ascii=False) for b in self.fake.children(page)))
        patches=self.fake.patches;self.sync();self.assertEqual(self.fake.patches,patches)
    def test_append_response_loss_reconciles(self):
        self.setup_revision();self.publish();before=self.fake.patches;self.fake.lose_chunk_response=True
        with self.assertRaises(core.PublisherError):self.sync()
        self.assertEqual(self.sync()['topics']['test-001']['notion_status'],'complete')
        self.assertEqual(self.fake.patches-before,len(notion.chunks(EDITORIAL,self.state()['topics']['test-001']['github_url'])))
    def test_archive_response_loss_reconciles(self):
        self.setup_revision();self.publish();self.fake.lose_archive=True
        with self.assertRaises(core.PublisherError):self.sync()
        self.assertEqual(self.sync()['topics']['test-001']['notion_status'],'complete')
    def test_old_manual_edit_stops_before_new_chunks(self):
        before=self.setup_revision();page=before['notion_page_id'];toggle=next(b for b in self.fake.children(page) if b['type']=='toggle')
        child=self.fake.blocks[toggle['id']][0];child['paragraph']['rich_text']=notion.rich('사람이 편집한 내용')
        patches=self.fake.patches;self.publish()
        with self.assertRaises(core.PublisherError):self.sync()
        self.assertEqual(self.fake.patches,patches);self.assertEqual(len(self.fake.children(page)),12)
    def test_revision_missing_page_never_recreates(self):
        before=self.setup_revision();self.publish();posts=self.fake.posts
        for blocks in self.fake.blocks.values():blocks[:]=[b for b in blocks if b.get('id')!=before['notion_page_id']]
        with self.assertRaises(core.PublisherError):self.sync()
        self.assertEqual(self.fake.posts,posts)
    def test_site_only_no_private_source_read_or_new_topic(self):
        self.publish();state=self.state();state['topics']['test-001'].update(notion_status='complete',blog_status='complete');core.write_json(self.root/'.publisher/state.json',state)
        core.write_json(self.root/maintenance.SITE_FILE,{'schema_version':1,'deployed_digest':None})
        (self.private/self.topics[1]['source_path']).unlink()
        result=core.prepare(self.root,self.private,now=self.now+timedelta(days=1),dry_run=False)
        self.assertEqual(result['action'],'site-update');self.assertIsNone(result['topic_id']);self.assertEqual(len(self.state()['topics']),1)
        receipt=cli.receipt(self.root);cli.mark_blog(self.root,'success',receipt);self.assertFalse(maintenance.site_pending(self.root))
    def test_stale_site_receipt_rejected(self):
        self.publish();core.write_json(self.root/maintenance.SITE_FILE,{'schema_version':1,'deployed_digest':None})
        receipt=cli.receipt(self.root);(self.root/'blog/new.txt').write_text('concurrent edit')
        with self.assertRaisesRegex(core.PublisherError,'site-receipt'):cli.mark_blog(self.root,'success',receipt)
    def test_withdraw_tombstone_no_recreation_or_notion_delete(self):
        before=self.setup_revision();self.plan['kind']='withdraw';core.write_json(self.root/maintenance.PLAN_FILE,self.plan)
        core.write_json(self.root/maintenance.SITE_FILE,{'schema_version':1,'deployed_digest':None})
        posts=self.fake.posts;self.publish();state=self.state();entry=state['topics']['test-001']
        self.assertEqual(entry['publication_status'],'withdrawn');self.assertIn('published: false',(self.root/entry['post_path']).read_text(encoding='utf-8'))
        self.assertNotIn('test-001',cli.receipt(self.root));self.assertEqual(self.publish()['action'],'site-update')
        notion.sync(self.root,state,self.config,client=self.fake,parent='root');self.assertEqual(self.fake.posts,posts)
        cli.mark_blog(self.root,'success',cli.receipt(self.root))
        self.assertEqual(core.prepare(self.root,self.private,now=self.now)['action'],'daily-limit')
        self.assertTrue((self.root/entry['target_path']).exists())

if __name__=='__main__':unittest.main()
