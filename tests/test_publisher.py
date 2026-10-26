import copy
import io
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import yaml

from scripts import cli, core, notion

BASE = Path(__file__).resolve().parents[1]


def sample():
    bodies = {
        "핵심 개념": "검증용으로 만든 공개 테스트 문서입니다. 실제 학습 대기열과 분리합니다.",
        "동작 원리": "1. 입력을 받습니다.\n2. 결과를 확인합니다.",
        "기술적 특징": "| 기준 | 내용 |\n| --- | --- |\n| 정확성 | **검증** |",
        "코드 예시": "```java\nSystem.out.println(1 + 1);\n```",
        "실무 활용": "[공식 문서](https://docs.github.com/)와 `topic_id`를 연결합니다.",
        "기술 면접 답변": "### 30초 답변\n테스트 문서입니다.\n\n### 1분 답변\n다시 실행해도 결과를 중복 생성하지 않습니다.",
        "예상 꼬리 질문": "### 질문 1\n답변 1\n\n### 질문 2\n답변 2\n\n### 질문 3\n답변 3",
        "자주 하는 오해": "API 성공과 상태 파일 저장은 하나의 트랜잭션이 아닙니다.",
        "핵심 요약": "- 입력, 상태, 외부 결과를 함께 확인합니다.",
        "참고 자료": "- [GitHub 공식 문서](https://docs.github.com/)"
    }
    return "# 검증용 문서\n\n" + "\n\n".join(f"## {i}. {s}\n\n{bodies[s]}" for i,s in enumerate(core.SECTIONS,1)) + "\n"


class FakeNotion:
    def __init__(self):
        self.blocks = {"root": []}
        self.count = 0
        self.posts = 0
        self.patches = 0
        self.lose_page_response = False
        self.lose_chunk_response = False

    def children(self, parent):
        return copy.deepcopy(self.blocks.get(parent, []))

    def create_page(self, parent, title, children=None):
        self.count += 1; self.posts += 1
        page = str(self.count)
        self.blocks.setdefault(parent, []).append({"type":"child_page","id":page,"child_page":{"title":title}})
        self.blocks[page] = copy.deepcopy(children or [])
        if children and self.lose_page_response:
            self.lose_page_response = False
            raise notion.AmbiguousWrite("notion-write-uncertain")
        return {"id":page}

    def request(self, method, path, payload=None):
        if method == "GET" and path.startswith("pages/"):
            return {"id":"root"}
        if method == "PATCH":
            self.patches += 1
            parent = path.split('/')[1]
            self.blocks[parent].extend(copy.deepcopy(payload['children']))
            if self.lose_chunk_response:
                self.lose_chunk_response = False
                raise notion.AmbiguousWrite("notion-write-uncertain")
            return {}
        raise AssertionError((method, path))


class PublisherTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "public"
        self.private = Path(self.temp.name) / "private"
        self.root.mkdir(); self.private.mkdir()
        for path in ("config/publisher.json", ".publisher/state.json", "README.md"):
            dest = self.root / path; dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(BASE / path, dest)
        # Tests must always start with empty state even after the repository publishes real posts.
        core.write_json(self.root / '.publisher/state.json', dict(schema_version=1,topics={},notion_hierarchy={},notion_uncertain={}))
        (self.root / "blog/_posts").mkdir(parents=True)
        self.topics = []
        for category,count in core.COUNTS.items():
            for j in range(count):
                order = len(self.topics) + 1
                key = f"test-{order:03d}"
                target = f"{category}/Testing/{key}.md"
                self.topics.append(dict(topic_id=key,title_ko=f"검증 주제 {order}",title_en=f"Synthetic Topic {order}",
                    category=category,subcategory="Testing",difficulty="basic",priority=1,prerequisites=[],publish_order=order,
                    source_path="pending/"+target,target_path=target))
        self.write_catalog()
        for t in self.topics[:2]:
            p = self.private / t['source_path']; p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(sample(),encoding='utf-8')
        self.now = datetime(2026,10,27,2,0,tzinfo=timezone.utc)

    def tearDown(self):
        self.temp.cleanup()

    def write_catalog(self):
        core.write_json(self.private / "manifests/topics.json", self.topics)
        core.write_json(self.private / "manifests/publish_queue.json", [t['topic_id'] for t in self.topics])

    def publish(self):
        return core.prepare(self.root,self.private,dry_run=False,now=self.now)

    def state(self):
        return core.load_state(self.root)

    def test_initial_100_topics_and_counts(self):
        self.assertEqual(len(core.load_catalog(self.private,initial=True)[0]),100)

    def test_duplicate_topic_rejected(self):
        self.topics[1]['title_ko'] = self.topics[0]['title_ko']; self.write_catalog()
        with self.assertRaisesRegex(core.PublisherError,'duplicate'): core.load_catalog(self.private)

    def test_forward_prerequisite_rejected(self):
        self.topics[0]['prerequisites']=['test-002']; self.write_catalog()
        with self.assertRaisesRegex(core.PublisherError,'prerequisite'): core.load_catalog(self.private)

    def test_invalid_category_folder_rejected(self):
        self.topics[0]['source_path']='pending/Network/test.md'; self.write_catalog()
        with self.assertRaisesRegex(core.PublisherError,'classification'): core.load_catalog(self.private)

    def test_read_only_private_content_and_one_topic_selected(self):
        before = {str(p.relative_to(self.private)):p.read_bytes() for p in self.private.rglob('*') if p.is_file()}
        self.assertEqual(self.publish()['topic_id'],'test-001')
        after = {str(p.relative_to(self.private)):p.read_bytes() for p in self.private.rglob('*') if p.is_file()}
        self.assertEqual(before,after)
        self.assertEqual(len(self.state()['topics']),1)

    def test_required_sections(self):
        with self.assertRaisesRegex(core.PublisherError,'sections'):
            core.validate_markdown(sample().replace('## 1. 핵심 개념','## 1. 누락'))

    def test_unclosed_code_fence(self):
        with self.assertRaisesRegex(core.PublisherError,'unclosed'):
            core.validate_markdown(sample()+'\n```java\nhello')

    def test_reference_links_and_markdown(self):
        core.validate_markdown(sample())

    def test_dry_run_no_files_no_state_no_network(self):
        before={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        with patch('urllib.request.urlopen',side_effect=AssertionError('no network')):
            self.assertTrue(core.prepare(self.root,self.private,now=self.now)['dry_run'])
        after={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_same_topic_reexecution_recovers(self):
        self.publish(); self.assertEqual(self.publish()['action'],'recover')
        self.assertEqual(len(list((self.root/'blog/_posts').glob('*.md'))),1)

    def test_one_new_topic_per_korean_day(self):
        self.publish(); state=self.state()
        state['topics']['test-001'].update(notion_status='complete',blog_status='complete')
        core.write_json(self.root/'.publisher/state.json',state)
        # 14:59 UTC is still 23:59 KST on the same date.
        result=core.prepare(self.root,self.private,dry_run=False,now=datetime(2026,10,27,14,59,tzinfo=timezone.utc))
        self.assertEqual(result['action'],'daily-limit')
        result=core.prepare(self.root,self.private,dry_run=False,now=datetime(2026,10,27,15,0,tzinfo=timezone.utc))
        self.assertEqual(result['topic_id'],'test-002')

    def test_readme_preserves_manual_text_and_hides_pending(self):
        (self.root/'README.md').write_text('# My own notes\nmanual\n',encoding='utf-8')
        self.publish(); text=(self.root/'README.md').read_text(encoding='utf-8')
        self.assertIn('manual',text); self.assertIn('test-001',text); self.assertNotIn('test-002',text)

    def test_existing_manual_document_protected(self):
        p=self.root/self.topics[0]['target_path']; p.parent.mkdir(parents=True); p.write_text('manual')
        with self.assertRaisesRegex(core.PublisherError,'existing-file'): self.publish()
        self.assertEqual(p.read_text(),'manual')

    def test_existing_permalink_protected(self):
        (self.root/'blog/_posts/manual.md').write_text('---\npermalink: /topics/test-001/\n---\nmanual',encoding='utf-8')
        with self.assertRaisesRegex(core.PublisherError,'permalink'): self.publish()

    def test_jekyll_front_matter_uses_publication_date(self):
        self.publish(); t=self.state()['topics']['test-001']
        text=(self.root/t['post_path']).read_text(encoding='utf-8')
        meta=yaml.safe_load(text.split('---',2)[1])
        self.assertEqual(meta['date'],'2026-10-27 00:00:00 +0900')
        self.assertEqual(meta['permalink'],'/topics/test-001/')
        self.assertEqual(text.split('---',2)[2].strip(),'{% raw %}\n'+sample()+'\n{% endraw %}')

    def test_markdown_to_notion_headings_lists_code_table_styles(self):
        blocks=notion.markdown_blocks(sample())
        kinds={b['type'] for b in blocks}
        self.assertTrue({'heading_1','heading_2','heading_3','paragraph','numbered_list_item','table','code'} <= kinds)
        table=next(b['table'] for b in blocks if b['type']=='table')
        self.assertEqual(table['table_width'],2)
        self.assertTrue(table['children'][1]['table_row']['cells'][1][0]['annotations']['bold'])

    def test_notion_rich_text_2000_character_limit(self):
        self.assertTrue(all(len(x['text']['content'])<=2000 for x in notion.rich('가'*5500)))

    def test_notion_hierarchy_and_duplicate_detection(self):
        self.publish(); fake=FakeNotion(); state=self.state(); config=core.read_json(self.root/'config/publisher.json')
        notion.sync(self.root,state,config,client=fake,parent='root')
        self.assertEqual(fake.posts,3)
        self.assertEqual(state['topics']['test-001']['notion_status'],'complete')
        patches=fake.patches
        state['topics']['test-001']['notion_status']='pending'
        notion.sync(self.root,state,config,client=fake,parent='root')
        self.assertEqual(fake.posts,3); self.assertEqual(fake.patches,patches)

    def test_notion_page_success_state_lost_recovers_existing(self):
        self.publish(); before=self.state(); fake=FakeNotion(); config=core.read_json(self.root/'config/publisher.json')
        notion.sync(self.root,copy.deepcopy(before),config,client=fake,parent='root')
        notion.sync(self.root,before,config,client=fake,parent='root')
        self.assertEqual(fake.posts,3)

    def test_notion_page_response_lost_reconciles(self):
        self.publish(); fake=FakeNotion(); fake.lose_page_response=True
        state=self.state(); config=core.read_json(self.root/'config/publisher.json')
        with self.assertRaises(core.PublisherError): notion.sync(self.root,state,config,client=fake,parent='root')
        notion.sync(self.root,state,config,client=fake,parent='root')
        self.assertEqual(fake.posts,3)

    def test_partial_notion_append_response_lost_recovers_without_duplication(self):
        self.publish(); fake=FakeNotion(); fake.lose_chunk_response=True
        state=self.state(); config=core.read_json(self.root/'config/publisher.json')
        with self.assertRaises(core.PublisherError): notion.sync(self.root,state,config,client=fake,parent='root')
        notion.sync(self.root,state,config,client=fake,parent='root')
        self.assertEqual(fake.patches,len(notion.chunks(sample(),state['topics']['test-001']['github_url'])))

    def test_github_success_notion_failure_keeps_reservation(self):
        self.publish(); state=self.state(); state['topics']['test-001']['notion_status']='failed'
        core.write_json(self.root/'.publisher/state.json',state)
        self.assertEqual(self.publish()['action'],'recover')
        self.assertTrue((self.root/self.topics[0]['target_path']).exists())

    def test_blog_failure_retries_same_topic(self):
        self.publish(); included=cli.receipt(self.root)
        cli.mark_blog(self.root,'failure',included)
        self.assertEqual(self.state()['topics']['test-001']['blog_status'],'failed')
        self.assertEqual(self.publish()['action'],'recover')
        cli.mark_blog(self.root,'success',included)
        self.assertEqual(self.state()['topics']['test-001']['blog_status'],'complete')

    def test_deployment_receipt_hash_mismatch_rejected(self):
        self.publish()
        with self.assertRaisesRegex(core.PublisherError,'receipt'):
            cli.mark_blog(self.root,'success',{'test-001':'a'*64})

    def test_duplicate_local_workflow_lock(self):
        with core.lock(self.root):
            with self.assertRaisesRegex(core.PublisherError,'already-running'):
                with core.lock(self.root): pass

    def test_queue_exhaustion(self):
        by_id,queue=core.load_catalog(self.private)
        state={'topics':{key:dict(topic_id=key,published_date='2026-01-01',github_status='complete',notion_status='complete',blog_status='complete') for key in queue}}
        self.assertEqual(core.select_topic(by_id,queue,state,'2026-10-27'),('exhausted',None))

    def test_missing_next_document_does_not_skip(self):
        (self.private/self.topics[0]['source_path']).unlink()
        with self.assertRaisesRegex(core.PublisherError,'not-ready'): self.publish()

    def test_private_symlink_escape_blocked(self):
        with self.assertRaises(core.PublisherError): core.safe_path(self.private,'../secret')
        with self.assertRaises(core.PublisherError): core.safe_path(self.private,'C:/secret')

    def test_published_manual_edit_is_protected(self):
        self.publish(); path=self.root/self.topics[0]['target_path']
        path.write_text(sample()+'\nmy edits',encoding='utf-8')
        with self.assertRaisesRegex(core.PublisherError,'changed'): self.publish()

    def test_workflow_gates_permissions_and_timezone(self):
        text=(BASE/'.github/workflows/publish.yml').read_text(encoding='utf-8')
        data=yaml.safe_load(text)
        self.assertIn('timezone: Asia/Seoul',text)
        self.assertIn("cron: '30 10 * * *'",text)
        self.assertIn("$AUTO\" == 'true'",text)
        self.assertNotIn('pull_request',text)
        self.assertFalse(data['concurrency']['cancel-in-progress'])
        self.assertNotIn('contents',data['jobs']['deploy']['permissions'])
        self.assertEqual(data['jobs']['deploy']['environment']['name'],'github-pages')


class RequestTests(unittest.TestCase):
    def test_rate_limit_retry_after(self):
        attempts=[]; delays=[]
        def opener(*args,**kwargs):
            attempts.append(1)
            if len(attempts)==1: raise HTTPError('https://api.notion.com',429,'rate limit',{'Retry-After':'2'},io.BytesIO(b'{}'))
            return io.BytesIO(b'{"results":[]}')
        client=notion.NotionClient('hidden',opener=opener,sleeper=delays.append)
        client.request('GET','blocks/root/children')
        self.assertEqual(len(attempts),2); self.assertTrue(any(x>=2 for x in delays))

    def test_expired_token_not_retried_or_leaked(self):
        attempts=[]
        def opener(*args,**kwargs):
            attempts.append(1); raise HTTPError('https://api.notion.com',401,'hidden-value',{},None)
        client=notion.NotionClient('hidden-value',opener=opener,sleeper=lambda _:None)
        with self.assertRaisesRegex(core.PublisherError,'notion-http-401') as exc: client.request('GET','pages/root')
        self.assertNotIn('hidden-value',str(exc.exception)); self.assertEqual(len(attempts),1)

    def test_write_503_never_blindly_retried(self):
        attempts=[]
        def opener(*args,**kwargs):
            attempts.append(1); raise HTTPError('https://api.notion.com',503,'unavailable',{},None)
        client=notion.NotionClient('hidden',opener=opener,sleeper=lambda _:None)
        with self.assertRaises(notion.AmbiguousWrite): client.request('POST','pages',{})
        self.assertEqual(len(attempts),1)

    def test_missing_token_fails_before_network(self):
        with self.assertRaisesRegex(core.PublisherError,'missing'): notion.NotionClient('')


if __name__=='__main__': unittest.main()
