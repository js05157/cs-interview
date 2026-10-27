"""Check the real Jekyll output, including project-site asset URLs."""
import argparse
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ("href", "src") and value:
                self.links.append(value)


class Archive(HTMLParser):
    def __init__(self):
        super().__init__()
        self.category = None
        self.links = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section" and "archive-category" in attrs.get("class", "").split():
            self.category = attrs["id"]
            self.links[self.category] = []
        if tag == "a" and self.category and "archive-row" in attrs.get("class", "").split():
            self.links[self.category].append(attrs["href"])

    def handle_endtag(self, tag):
        if tag == "section":
            self.category = None


def verify(site, baseurl="/cs-interview"):
    site = Path(site)
    for name in ("index.html", "about/index.html", "projects/index.html", "learning/index.html",
                 "assets/style.css", "assets/app.js", "sitemap.xml", "robots.txt", "feed.xml", "search.json"):
        if not (site / name).is_file():
            raise ValueError("missing-built-file:" + name)
    if any(p.name in {"pending", ".git", ".publisher", "manifests", "private-content"} for p in site.rglob("*")):
        raise ValueError("private-or-runtime-directory-in-site")
    for file in site.rglob("*.html"):
        text = file.read_text(encoding="utf-8")
        if "{%" in text or "{{" in text and "topics" not in file.parts:
            raise ValueError("unrendered-liquid:" + file.name)
        parser = Links(); parser.feed(text)
        for link in parser.links:
            uri = urlsplit(link)
            if uri.scheme or uri.netloc or not uri.path or not uri.path.startswith("/"):
                continue
            if not uri.path.startswith(baseurl + "/"):
                raise ValueError("baseurl-missing:" + uri.path)
            path = site / unquote(uri.path[len(baseurl)+1:])
            if not path.is_file() and not (path / "index.html").is_file():
                raise ValueError("broken-built-link:" + uri.path)
    posts = json.loads((site / "search.json").read_text(encoding="utf-8"))
    archive = Archive()
    archive.feed((site / "learning/index.html").read_text(encoding="utf-8"))
    expected = {category: [] for category in archive.links}
    for post in posts:
        if not post["url"].startswith(baseurl + "/topics/"):
            raise ValueError("invalid-search-url")
        dest = site / post["url"][len(baseurl)+1:] / "index.html"
        if not dest.is_file():
            raise ValueError("search-post-not-built")
        if post["category"] not in expected:
            raise ValueError("post-category-not-in-archive")
        expected[post["category"]].append(post["url"])
    if {k: sorted(v) for k, v in archive.links.items()} != {k: sorted(v) for k, v in expected.items()}:
        raise ValueError("category-archive-posts-mismatch")
    return {"html_pages": len(list(site.rglob("*.html"))), "posts": len(posts), "baseurl": baseurl}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.site)))
