"""Five-section parsing, escaping, platform equivalence and revision recovery contracts."""
import copy,re,unittest
from html.parser import HTMLParser
from scripts import core,notion,maintenance
from scripts.learning import parse_guide,render_followups
import test_maintenance as fixture

GUIDE='''# 테스트

## 정의

실행할 작업을 관리하는 단위입니다. 다른 실행과 자원 경계를 만듭니다.

## 설명

같은 객체를 여러 실행 흐름에서 함께 사용하면 순서를 조정해야 합니다.

## 적용 예시

카운터를 두 번 증가시키는 상황을 생각합니다.

## 정리

작업의 경계를 먼저 정합니다. 공유 범위에 따라 동기화가 필요합니다. 실행 개수만으로 속도를 판단하지 않습니다.

## 꼬리 질문

### Q1. `join()` 없이 읽으면 어떤 문제가 있을까요?

작업이 아직 끝나지 않았을 수 있습니다. [공식 문서](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Thread.html)를 확인하고 완료를 기다립니다.

```java
System.out.println("answer");
```

### Q2. 같은 값을 함께 바꾸면 어떤 일이 생길까요?

두 실행이 같은 이전 값을 읽을 수 있습니다. 이때 덮어쓰기로 증가가 유실될 수 있습니다.

---

**참고 자료**

- [Thread](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Thread.html)
'''

class Details(HTMLParser):
 def __init__(self):super().__init__();self.details=[]
 def handle_starttag(self,t,attrs):
  if t=='details':self.details.append(dict(attrs))

class LearningTests(unittest.TestCase):
 def test_built_contract_ignores_search_dialog_but_rejects_an_open_answer(self):
  from scripts.verify_site import LearningMarkup
  html='<article data-learning-format="five-section-v1">'+render_followups(GUIDE)+'</article><dialog><h2>글 검색</h2></dialog>'
  # The parser sees rendered H2 elements, as provided by Jekyll.
  import markdown_it
  html=html.replace('## 정의','<h2>정의</h2>').replace('## 설명','<h2>설명</h2>').replace('## 적용 예시','<h2>적용 예시</h2>').replace('## 정리','<h2>정리</h2>').replace('## 꼬리 질문','<h2>꼬리 질문</h2>')
  p=LearningMarkup();p.feed(html);p.verify()
  with self.assertRaises(ValueError):LearningMarkup().feed(html.replace('<details class="cs-followup">','<details class="cs-followup" open>',1))
 def test_html_is_generated_closed_and_independent_with_code_and_link(self):
  core.validate_markdown(GUIDE);rendered=render_followups(GUIDE);p=Details();p.feed(rendered)
  self.assertEqual(len(p.details),2);self.assertTrue(all('open' not in a and 'name' not in a for a in p.details))
  self.assertIn('<code>join()</code>',rendered);self.assertIn('language-java',rendered);self.assertIn('https://docs.oracle.com/',rendered)
  self.assertEqual(rendered.count('System.out.println'),1)
 def test_notion_question_order_answers_code_and_link_are_preserved(self):
  q=[b for b in notion.markdown_blocks(GUIDE) if b['type']=='toggle']
  self.assertEqual([b['toggle']['rich_text'][0]['text']['content'] for b in q],['Q1. ','Q2. 같은 값을 함께 바꾸면 어떤 일이 생길까요?'])
  self.assertEqual([b['type'] for b in q[0]['toggle']['children']],['paragraph','code'])
  self.assertTrue(any(x.get('text',{}).get('link') for x in q[0]['toggle']['children'][0]['paragraph']['rich_text']))
  self.assertEqual(len(notion.chunks(GUIDE,'https://example.test/test.md')),5)
 def test_source_html_and_liquid_boundary_remain_rejected(self):
  for bad in ('<details>bad</details>','<script>alert(1)</script>','{% endraw %}'):
   with self.subTest(bad=bad),self.assertRaises(core.PublisherError):core.validate_markdown(GUIDE.replace('작업이 아직',bad+'\n작업이 아직'))
 def test_missing_reordered_or_short_questions_and_answers_fail_closed(self):
  for body in (GUIDE.replace('## 설명','## 다른 설명'),GUIDE.replace('Q2.','Q3.'),GUIDE.replace('두 실행이 같은 이전 값을 읽을 수 있습니다. 이때 덮어쓰기로 증가가 유실될 수 있습니다.',''),GUIDE.replace('### Q2. 같은 값을 함께 바꾸면 어떤 일이 생길까요?','### Q1. 같은 값을 함께 바꾸면 어떤 일이 생길까요?'),GUIDE.replace('## 정리','## 핵심 요약'),GUIDE.replace('**참고 자료**','**출처**')):
   with self.subTest(body=body[-150:]),self.assertRaises(core.PublisherError):core.validate_markdown(body)
 def test_heading_like_code_is_not_a_real_question(self):
  body=GUIDE.replace('System.out.println("answer");','// ### Q4. Not a question\nSystem.out.println("answer");')
  self.assertEqual(len(parse_guide(body).questions),2)
 def test_html_in_question_is_escaped_in_standalone_renderer(self):
  text=GUIDE.replace('`join()` 없이 읽으면 어떤 문제가 있을까요?','<img src=x onerror=alert(1)>')
  self.assertNotIn('<img',render_followups(text));self.assertIn('&lt;img',render_followups(text))
 def test_render_v2_stays_plain_and_v3_produces_details(self):
  entry={'title_ko':'테스트','published_date':'2026-10-27','topic_id':'test-001','category':'Java','subcategory':'Thread','permalink':'/topics/test-001/','github_url':'https://example.test/test.md','render_version':2}
  self.assertNotIn('<details',core.make_post(entry,GUIDE));entry['render_version']=3
  self.assertEqual(core.make_post(entry,GUIDE).count('<details'),2)

class LearningRecoveryTests(unittest.TestCase):
 setUp=fixture.MaintenanceTests.setUp
 tearDown=fixture.MaintenanceTests.tearDown
 write_catalog=fixture.MaintenanceTests.write_catalog
 publish=fixture.MaintenanceTests.publish
 state=fixture.MaintenanceTests.state
 setup_revision=fixture.MaintenanceTests.setup_revision
 sync=fixture.MaintenanceTests.sync
 # Reuse the real revision mocks, including append/archive response loss and manual notes.
 def test_five_section_revision_repeat_preserves_page_and_previous_revision(self):
  before=self.setup_revision();maintenance.maintenance_prepare(self.root,self.private,self.state(),core.load_catalog(self.private)[0],dry_run=False,today='2026-10-29')
  state=self.sync();state['topics']['test-001']['blog_status']='complete';core.write_json(self.root/'.publisher/state.json',state)
  previous=copy.deepcopy(state['topics']['test-001']);(self.root/'second-old.md').write_text((self.root/previous['target_path']).read_text(encoding='utf-8'),encoding='utf-8')
  body=GUIDE.replace('# 테스트','# '+previous['title_ko']);(self.private/self.topics[0]['source_path']).write_text(body,encoding='utf-8')
  core.write_json(self.root/maintenance.PLAN_FILE,{'schema_version':1,'kind':'revision','topic_id':'test-001','from_hash':previous['content_hash'],'to_hash':core.digest(body),'notion_page_id':previous['notion_page_id'],'previous_body_path':'second-old.md'})
  maintenance.maintenance_prepare(self.root,self.private,self.state(),core.load_catalog(self.private)[0],dry_run=False,today='2026-10-30')
  self.fake.lose_chunk_response=True;self.fake.lose_archive=True
  with self.assertRaises(core.PublisherError):self.sync()  # appended but response lost
  with self.assertRaises(core.PublisherError):self.sync()  # archive succeeded but response lost
  after=self.sync();again=self.sync();entry=again['topics']['test-001']
  self.assertEqual(entry['notion_page_id'],before['notion_page_id']);self.assertEqual(entry['published_date'],before['published_date']);self.assertEqual(entry['render_version'],3)
  self.assertEqual(entry['revision_history'][-1]['revision'],previous['revision'])
  self.assertEqual(after,again);self.assertEqual(entry['notion_status'],'complete')

if __name__=='__main__':unittest.main()
