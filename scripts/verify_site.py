"""Validate the built personal blog, including existing project-site paths and images."""
import argparse,json,re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit

class Links(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.ids=set();self.images=[];self.rows=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get("id"):self.ids.add(a["id"])
        for key in ("href","src"):
            if a.get(key):self.links.append(a[key])
        if tag=="img":self.images.append(a)
        if tag=="a" and "post-row" in a.get("class","").split():self.rows.append((a.get("href"),a.get("data-kind")))

class Archive(HTMLParser):
    """Legacy report compatibility; current layout groups by content type."""
    def __init__(self):
        super().__init__();self.category=None;self.links={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="section" and "archive-category" in a.get("class","").split():
            self.category=a["id"];self.links[self.category]=[]
        if tag=="a" and self.category and "archive-row" in a.get("class","").split():self.links[self.category].append(a["href"])
    def handle_endtag(self,tag):
        if tag=="section":self.category=None

class LearningMarkup(HTMLParser):
    def __init__(self):
        super().__init__();self.enabled=False;self.in_article=False;self.questions=[];self.current=None;self.in_summary=False;self.h2=False;self.headings=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="article" and a.get("data-learning-format")=="five-section-v1":self.enabled=True;self.in_article=True
        if tag=="h2" and self.in_article:self.h2=True;self.headings.append("")
        if tag=="details" and self.in_article and "cs-followup" in a.get("class","").split():
            if "open" in a or "name" in a:raise ValueError("followups-must-start-closed-and-independent")
            self.current={"question":"","answer":""};self.questions.append(self.current)
        if tag=="summary" and self.current is not None:self.in_summary=True
    def handle_data(self,data):
        if self.h2:self.headings[-1]+=data
        if self.current is not None:self.current["question" if self.in_summary else "answer"]+=data
    def handle_endtag(self,tag):
        if tag=="article":self.in_article=False
        if tag=="summary":self.in_summary=False
        if tag=="details":self.current=None
        if tag=="h2":self.h2=False
    def verify(self):
        if self.enabled and (self.headings!=["정의","설명","적용 예시","정리","꼬리 질문"] or not 2<=len(self.questions)<=4 or any(not q["question"].strip() or not q["answer"].strip() for q in self.questions)):
            raise ValueError("built-learning-question-answer-contract-mismatch")

def verify(site,baseurl="/cs-interview"):
    site=Path(site)
    required=("index.html","posts/index.html","projects/index.html","ssafy/index.html","manage/index.html",
              "learning/index.html","about/index.html","assets/style.css","assets/app.js","assets/editor.js",
              "assets/lib/markdown-it.min.js","search.json","feed.xml","sitemap.xml","robots.txt")
    for rel in required:
        if not (site/rel).is_file():raise ValueError("missing-built-file:"+rel)
    if any(p.name in {"pending",".git",".publisher","manifests","private-content"} for p in site.rglob("*")):
        raise ValueError("private-or-runtime-directory-in-site")
    pages={}
    for file in site.rglob("*.html"):
        text=file.read_text(encoding="utf-8")
        safe_text=re.sub(r"<(pre|code)\b[^>]*>.*?</\1>","",text,flags=re.S)
        if "{%" in safe_text or "{{" in safe_text:raise ValueError("unrendered-liquid:"+file.name)
        parser=Links();parser.feed(text);pages[file]=parser
        learning=LearningMarkup();learning.feed(text);learning.verify()
        if '<aside class="sidebar"' in text or 'class="category-grid"' in text:raise ValueError("legacy-cs-navigation-present")
        for img in parser.images:
            if not img.get("alt","").strip():raise ValueError("image-alt-required:"+file.name)
        for link in parser.links:
            uri=urlsplit(link)
            own=uri.netloc=="js05157.github.io"
            if uri.netloc and not own:continue
            if uri.scheme and not own:continue
            if not uri.path:
                if uri.fragment and unquote(uri.fragment) not in parser.ids:raise ValueError("broken-local-anchor:"+link)
                continue
            if not uri.path.startswith("/"):continue
            if not uri.path.startswith(baseurl+"/"):raise ValueError("baseurl-missing:"+uri.path)
            dest=site/unquote(uri.path[len(baseurl)+1:])
            if not dest.is_file() and not (dest/"index.html").is_file():raise ValueError("broken-built-link:"+uri.path)
    posts=json.loads((site/"search.json").read_text(encoding="utf-8"))
    kinds={"cs","development","project","ssafy","essay"}
    for post in posts:
        if not post["url"].startswith((baseurl+"/topics/",baseurl+"/posts/")):raise ValueError("invalid-search-url")
        if post.get("kind") not in kinds:raise ValueError("invalid-post-content-type")
        if not (site/post["url"][len(baseurl)+1:]/"index.html").is_file():raise ValueError("search-post-not-built")
    archive=pages[site/"posts/index.html"]
    expected=sorted((post["url"],post["kind"]) for post in posts)
    if sorted(archive.rows)!=expected:raise ValueError("post-archive-mismatch")
    ssafy=pages[site/"ssafy/index.html"]
    if sorted(ssafy.rows)!=sorted((p["url"],"ssafy") for p in posts if p["kind"]=="ssafy"):raise ValueError("ssafy-archive-mismatch")
    for svg in (site/"assets").rglob("*.svg"):
        text=svg.read_text(encoding="utf-8")
        if re.search(r"<(?:script|foreignObject)\b|\bon\w+\s*=",text,re.I):raise ValueError("unsafe-svg:"+svg.name)
    return {"html_pages":len(pages),"posts":len(posts),"content_types":sorted({p["kind"] for p in posts}),"baseurl":baseurl}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--site",required=True,type=Path)
    print(json.dumps(verify(p.parse_args().site)))
