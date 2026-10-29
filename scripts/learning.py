"""Strict, shared five-section Markdown contract and safe Pages rendering."""
from dataclasses import dataclass
import re
from markdown_it import MarkdownIt
from .core import MD,PublisherError

HEADINGS=('정의','설명','적용 예시','정리','꼬리 질문')
@dataclass(frozen=True)
class Question:
    number:int
    title:str
    answer:str
@dataclass(frozen=True)
class Guide:
    sections:dict
    prefix:str
    questions:tuple
    references:str

def sentence_count(text):
    text=re.sub(r'```.*?```|~~~.*?~~~','',text,flags=re.S)
    return len([s for s in re.split(r'(?<=[.!?])\s+',text.strip()) if s])

def parse_guide(text,*,required=False):
    tokens=MD.parse(text);lines=text.splitlines(keepends=True)
    heads=[(t,tokens[i+1].content) for i,t in enumerate(tokens) if t.type=='heading_open' and t.tag=='h2' and t.level==0]
    if not required and not any(title in HEADINGS for _,title in heads):return None
    if tuple(title for _,title in heads)!=HEADINGS:raise PublisherError('five-section-order-required')
    sections={title:''.join(lines[t.map[1]:heads[j+1][0].map[0] if j+1<len(heads) else len(lines)]).strip() for j,(t,title) in enumerate(heads)}
    if not 2<=sentence_count(sections['정의'])<=3:raise PublisherError('definition-two-to-three-sentences-required')
    if not 3<=sentence_count(sections['정리'])<=5:raise PublisherError('summary-three-to-five-sentences-required')
    if any(not sections[h] for h in HEADINGS):raise PublisherError('empty-learning-section')
    if any(term in text for term in ('30초 답변','1분 답변','면접 답변','면접용 요약','핵심 요약')):raise PublisherError('interview-script-forbidden')
    qa_start=heads[-1][0].map[1]
    dividers=[t for t in tokens if t.type=='hr' and t.level==0 and t.map[0]>=qa_start]
    if len(dividers)!=1:raise PublisherError('reference-footer-divider-required')
    boundary=dividers[0].map[0];references=''.join(lines[boundary:])
    footer=references.splitlines()[2:] if references.startswith('---\n\n') else []
    if not footer or footer[0].strip()!='**참고 자료**':raise PublisherError('reference-footer-label-required')
    if not re.search(r'\[[^\]]+\]\(https://[^\s)]+\)',references):raise PublisherError('references-missing')
    qheads=[(t,tokens[i+1].content) for i,t in enumerate(tokens) if t.type=='heading_open' and t.tag=='h3' and t.level==0 and qa_start<=t.map[0]<boundary]
    if not 2<=len(qheads)<=4:raise PublisherError('two-to-four-followup-answers-required')
    if ''.join(lines[qa_start:qheads[0][0].map[0]]).strip():raise PublisherError('unexpected-followup-preamble')
    questions=[]
    for j,(t,title) in enumerate(qheads):
        match=re.fullmatch(r'Q([1-4])\. (.+)',title)
        if not match or int(match[1])!=j+1 or len(match[2])>220:raise PublisherError('invalid-question-number-or-title')
        answer=''.join(lines[t.map[1]:qheads[j+1][0].map[0] if j+1<len(qheads) else boundary]).strip()
        if not answer or not any(tok.type in ('paragraph_open','fence','bullet_list_open','ordered_list_open') for tok in MD.parse(answer)):raise PublisherError('followup-answer-missing')
        if any(tok.type=='heading_open' for tok in MD.parse(answer)):raise PublisherError('heading-inside-answer-forbidden')
        if sentence_count(answer)<2:raise PublisherError('followup-answer-too-short')
        questions.append(Question(j+1,match[2],answer))
    if len({q.title for q in questions})!=len(questions):raise PublisherError('duplicate-followup-question')
    return Guide(sections,''.join(lines[:qheads[0][0].map[0]]),tuple(questions),references)

def render_followups(text):
    guide=parse_guide(text,required=True)
    # Source HTML is never trusted. Markdown renderer escapes text and filters unsafe link protocols.
    renderer=MarkdownIt('commonmark',{'html':False}).enable('table')
    details=[]
    for q in guide.questions:
        title=renderer.renderInline(f'Q{q.number}. '+q.title)
        details.append('<details class="cs-followup">\n<summary>'+title+'</summary>\n<div class="cs-followup-answer">\n'+renderer.render(q.answer)+'</div>\n</details>')
    return guide.prefix+'\n'+'\n\n'.join(details)+'\n\n'+guide.references
