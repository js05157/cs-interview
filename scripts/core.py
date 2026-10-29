"""Deterministic queue, validation and local preparation. No network side effects."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlsplit

import yaml
from markdown_it import MarkdownIt

KST = timezone(timedelta(hours=9))
SECTIONS = ["핵심 개념", "동작 원리", "기술적 특징", "코드 예시", "실무 활용",
            "기술 면접 답변", "예상 꼬리 질문", "자주 하는 오해", "핵심 요약", "참고 자료"]
COUNTS = {"Operating-System": 10, "Network": 12, "Database": 12, "Java": 14,
          "Spring": 14, "Data-Structure": 8, "Algorithm": 8,
          "Software-Architecture": 10, "DevOps": 6, "Data-Engineering": 6}
MD = MarkdownIt("commonmark").enable("table")


class PublisherError(Exception):
    pass


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def safe_path(root, relative):
    p = PurePosixPath(relative)
    if p.is_absolute() or not p.parts or any(x in ("..", ".") for x in p.parts) or "\\" in relative or ":" in relative:
        raise PublisherError("unsafe-relative-path")
    root = Path(root).resolve()
    result = root.joinpath(*p.parts).resolve()
    if not result.is_relative_to(root):
        raise PublisherError("path-outside-root")
    return result


def load_catalog(private, initial=False):
    topics = read_json(Path(private) / "manifests/topics.json")
    queue = read_json(Path(private) / "manifests/publish_queue.json")
    if not topics or not isinstance(topics, list):
        raise PublisherError("empty-catalog")
    ids, titles, paths, orders = set(), set(), set(), set()
    by_id = {}
    required = {"topic_id", "title_ko", "title_en", "category", "subcategory", "difficulty",
                "priority", "prerequisites", "publish_order", "source_path", "target_path"}
    for t in topics:
        if not required.issubset(t) or not re.fullmatch(r"[a-z][a-z0-9-]{2,79}", t["topic_id"]):
            raise PublisherError("invalid-topic-schema")
        title = re.sub(r"[\W_]", "", t["title_ko"].casefold())
        en_title = re.sub(r"[\W_]", "", t["title_en"].casefold())
        if t["topic_id"] in ids or title in titles or en_title in titles or t["target_path"].casefold() in paths or t["publish_order"] in orders:
            raise PublisherError("duplicate-topic")
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]+", t["category"]) or not re.fullmatch(r"[A-Za-z0-9-]+", t["subcategory"]):
            raise PublisherError("invalid-category")
        if t["difficulty"] not in ("basic", "intermediate", "advanced") or t["priority"] not in (1, 2, 3):
            raise PublisherError("invalid-topic-level")
        target = f'{t["category"]}/{t["subcategory"]}/{t["topic_id"]}.md'
        if t["target_path"] != target or t["source_path"] != "pending/" + target:
            raise PublisherError("invalid-classification")
        safe_path(private, t["source_path"])
        ids.add(t["topic_id"]); titles.update((title, en_title)); paths.add(target.casefold()); orders.add(t["publish_order"])
        by_id[t["topic_id"]] = t
    if orders != set(range(1, len(topics) + 1)) or len(queue) != len(ids) or set(queue) != ids:
        raise PublisherError("invalid-queue")
    if queue != [t["topic_id"] for t in sorted(topics, key=lambda t: t["publish_order"])]:
        raise PublisherError("queue-order-mismatch")
    for t in topics:
        for pre in t["prerequisites"]:
            if pre not in by_id or by_id[pre]["publish_order"] >= t["publish_order"]:
                raise PublisherError("invalid-prerequisite-order")
    if initial and (len(topics) != 100 or Counter(t["category"] for t in topics) != COUNTS):
        raise PublisherError("initial-category-count-mismatch")
    return by_id, queue


def validate_markdown(text):
    if not text.startswith("# ") or "\x00" in text:
        raise PublisherError("invalid-markdown-title")
    # markdown-it accepts an unclosed fence; publishing policy rejects it.
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
        if not match:
            continue
        mark, rest = match.groups()
        if fence is None:
            fence = mark
            if not rest.strip():
                raise PublisherError("code-language-required")
        elif mark[0] == fence[0] and len(mark) >= len(fence) and not rest.strip():
            fence = None
    if fence:
        raise PublisherError("unclosed-code-fence")
    tokens = MD.parse(text)
    headings = [tokens[i+1].content for i, t in enumerate(tokens) if t.type == "heading_open" and t.tag == "h2"]
    legacy = any(h.startswith("6. 기술 면접") for h in headings)
    if legacy and headings != [f"{i}. {s}" for i, s in enumerate(SECTIONS, 1)]:
        raise PublisherError("required-sections-missing-or-reordered")
    if legacy and ("30초 답변" not in text or "1분 답변" not in text):
        raise PublisherError("interview-answers-missing")
    followups = text.split("## 7. 예상 꼬리 질문", 1)[-1].split("## 8. 자주 하는 오해", 1)[0]
    if legacy and not 3 <= len(re.findall(r"^### ", followups, re.M)) <= 5:
        raise PublisherError("three-to-five-followup-answers-required")
    if not legacy:
        from .learning import parse_guide
        guide = parse_guide(text)
        if guide is None and ("참고 자료" not in headings or len(headings) < 2 or len(set(headings)) != len(headings)):
            raise PublisherError("editorial-sections-required")
        if re.search(r"^#{1,6} .*?(30초|1분 답변|핵심 요약|기술 면접 답변)", text, re.M):
            raise PublisherError("interview-script-heading-forbidden")
    if re.search(r"{%-?\s*endraw\b", text):
        raise PublisherError("liquid-raw-boundary-needs-editorial-review")
    for tok in tokens:
        for child in tok.children or []:
            if child.type == "link_open":
                href = child.attrGet("href") or ""
                if href.startswith(("http:", "https:")) and (urlsplit(href).scheme != "https" or not urlsplit(href).netloc):
                    raise PublisherError("invalid-reference-link")
            if child.type == "image":
                src = urlsplit(child.attrGet("src") or "")
                if not child.content.strip() or (src.scheme != "cs-asset" and (src.scheme != "https" or not src.netloc or src.username or src.password)):
                    raise PublisherError("image-alt-and-safe-https-required")
    references = guide.references if not legacy and guide is not None else text.split("## 10. 참고 자료" if legacy else "## 참고 자료", 1)[-1]
    if not re.search(r"\[[^\]]+\]\(https://[^\s)]+\)", references):
        raise PublisherError("references-missing")
    if any(t.type == "html_block" or any(c.type == "html_inline" for c in t.children or []) for t in tokens):
        raise PublisherError("raw-html-needs-editorial-review")


def load_state(root):
    state = read_json(Path(root) / ".publisher/state.json")
    if state.get("schema_version") != 1 or not isinstance(state.get("topics"), dict):
        raise PublisherError("invalid-state-schema")
    dates = Counter()
    allowed = {"topic_id", "title_ko", "category", "subcategory", "target_path", "post_path",
               "permalink", "github_status", "notion_status", "blog_status", "github_url",
               "notion_page_id", "notion_url", "blog_url", "published_date", "content_hash",
               "notion_error", "blog_error", "notion_pending_chunk", "render_version", "revision", "publication_status", "assets", "source_content_hash", "revision_history"}
    for key, item in state["topics"].items():
        if item.get("render_version",1) not in (1,2,3) or item.get("publication_status","active") not in ("active","withdrawn"):
            raise PublisherError("invalid-publication-lifecycle")
        if item.get("revision"):
            allowed_revision = {"plan_hash","from_hash","previous_body_path","notion_page_id","old_blocks","archived_blocks","status","archive_pending"}
            if set(item["revision"]) - allowed_revision or item["revision"].get("notion_page_id") != item.get("notion_page_id"):
                raise PublisherError("unsafe-revision-state")
        if set(item) - allowed or key != item.get("topic_id"):
            raise PublisherError("unsafe-state-fields")
        for previous in item.get("revision_history",[]):
            if set(previous)-{"content_hash","render_version","revision"} or not re.fullmatch(r"[a-f0-9]{64}",previous.get("content_hash","")) or previous.get("revision",{}).get("notion_page_id") != item.get("notion_page_id"):
                raise PublisherError("unsafe-revision-history")
        if not re.fullmatch(r"[a-f0-9]{64}", item["content_hash"]):
            raise PublisherError("invalid-content-hash")
        datetime.strptime(item["published_date"], "%Y-%m-%d")
        dates[item["published_date"]] += 1
    if any(count > 1 for count in dates.values()):
        raise PublisherError("daily-limit-state-violation")
    return state


def select_topic(by_id, queue, state, today):
    incomplete = [t for t in state["topics"].values()
                  if t.get("publication_status") != "withdrawn" and any(t[x] != "complete" for x in ("github_status", "notion_status", "blog_status"))]
    if incomplete:
        return "recover", sorted(incomplete, key=lambda t: (t["published_date"], t["topic_id"]))[0]["topic_id"]
    if any(t["published_date"] == today for t in state["topics"].values()):
        return "daily-limit", None
    for key in queue:
        if key not in state["topics"]:
            return "new", key
    return "exhausted", None


def make_post(t, body):
    meta = {"layout": "post", "title": t["title_ko"], "date": t["published_date"] + " 00:00:00 +0900",
            "topic_id": t["topic_id"], "categories": [t["category"]], "tags": [t["subcategory"]],
            "description": f'{t["title_ko"]}: 동작 원리와 설계 판단, Java 백엔드 면접 답변.',
            "permalink": t["permalink"], "github_url": t["github_url"]}
    if t.get("render_version") in (2,3):
        meta.update(content_type="cs", description=re.sub(r"[*`]", "", next((line.strip() for line in body.splitlines()[1:] if line.strip() and not line.startswith("#")), t["title_ko"]))[:160], excerpt="")
        if t.get("publication_status") == "withdrawn":
            meta["published"] = False
        body = body.split("\n", 1)[1].lstrip()
        if t.get("render_version") == 3:
            meta["learning_format"] = "five-section-v1"
            from .learning import render_followups
            # Render with the original H1 so the shared Markdown contract can be checked.
            body = render_followups("# " + t["title_ko"] + "\n\n" + body).split("\n",1)[1].lstrip()
    # GitHub Pages currently builds with Jekyll 3. Preserve literal template examples.
    return "---\n" + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + "---\n\n{% raw %}\n" + body + "\n{% endraw %}\n"


def update_indexes(root, state, config):
    root = Path(root)
    entries = sorted((t for t in state["topics"].values() if t["github_status"] == "complete" and t.get("publication_status") != "withdrawn"),
                     key=lambda t: (t["published_date"], t["topic_id"]), reverse=True)
    lines = [f'## CS 학습 기록 · {len(entries)}개', "", f'[기술 블로그]({config["blog_url"]}/)', ""]
    if state.get("notion_parent_url"):
        lines += [f'[Notion 학습 페이지]({state["notion_parent_url"]})', ""]
    lines += ["### 최근 게시 문서", ""]
    for t in entries[:5]:
        lines.append(f'- {t["published_date"]} · [{t["title_ko"]}]({quote(t["target_path"])})')
    if not entries:
        lines += ["아직 게시된 학습 문서가 없습니다."]
    for category, label in config["categories"].items():
        found = [t for t in entries if t["category"] == category]
        lines += ["", f"### {label} · {len(found)}개", ""]
        lines += [f'- [{t["title_ko"]}]({quote(t["target_path"])})' for t in found]
    block = "<!-- CS-PUBLISHER:START -->\n" + "\n".join(lines) + "\n<!-- CS-PUBLISHER:END -->"
    path = root / "README.md"
    old = path.read_text(encoding="utf-8") if path.exists() else "# CS Interview\n"
    start, end = "<!-- CS-PUBLISHER:START -->", "<!-- CS-PUBLISHER:END -->"
    if old.count(start) != old.count(end) or old.count(start) > 1:
        raise PublisherError("readme-marker-conflict")
    if start in old:
        old = old[:old.index(start)] + block + old[old.index(end) + len(end):]
    else:
        old = old.rstrip() + "\n\n" + block + "\n"
    path.write_text(old, encoding="utf-8")
    write_json(root / "blog/_data/publisher.json", {"count": len(entries), "notion_url": state.get("notion_parent_url", "")})


@contextmanager
def lock(root):
    path = Path(root) / ".publisher/.lock"
    path.parent.mkdir(exist_ok=True)
    try:
        f = path.open("x", encoding="utf-8")
    except FileExistsError as exc:
        raise PublisherError("publisher-already-running") from exc
    try:
        with f:
            f.write("local-process-lock\n")
        yield
    finally:
        path.unlink(missing_ok=True)


def prepare(root, private, *, dry_run=True, now=None):
    root, private = Path(root), Path(private)
    config = read_json(root / "config/publisher.json")
    by_id, queue = load_catalog(private)
    state = load_state(root)
    now = now or datetime.now(KST)
    if now.tzinfo is None:
        raise PublisherError("timezone-aware-time-required")
    today = now.astimezone(KST).date().isoformat()
    from .maintenance import maintenance_prepare
    maintenance = maintenance_prepare(root, private, state, by_id, dry_run=dry_run, today=today)
    if maintenance is not None:
        return maintenance
    mode, key = select_topic(by_id, queue, state, today)
    result = {"action": mode, "topic_id": key, "date": today, "dry_run": dry_run}
    if not key:
        return result
    if mode == "recover":
        t = state["topics"][key]
        from .assets import verify_assets
        verify_assets(root,t)
        source = safe_path(root, t["target_path"])
        if not source.exists() or digest(source.read_text(encoding="utf-8")) != t["content_hash"]:
            raise PublisherError("published-source-changed-review-required")
        post = safe_path(root, t["post_path"])
        if not post.exists() or post.read_text(encoding="utf-8") != make_post(t, source.read_text(encoding="utf-8")):
            raise PublisherError("published-post-changed-review-required")
        return result
    t = by_id[key]
    path = safe_path(private, t["source_path"])
    if not path.is_file():
        # Never silently skip an unfinished prerequisite in the queue.
        raise PublisherError("next-content-not-ready:" + key)
    body = path.read_text(encoding="utf-8")
    validate_markdown(body)
    source_content_hash = digest(body)
    from .assets import resolve_assets, copy_assets
    body, assets = resolve_assets(root, private, t, body)
    # Private links must not become broken relative links or reveal future topics.
    if re.search(r'\]\((?!https://|#)[^)]+\)', body):
        raise PublisherError("relative-links-must-be-resolved-before-publish")
    entry = {"topic_id": key, "title_ko": t["title_ko"], "category": t["category"], "subcategory": t["subcategory"],
             "target_path": t["target_path"], "post_path": f"blog/_posts/{today}-{key}.md",
             "permalink": f"/topics/{key}/", "github_status": "complete", "notion_status": "pending",
             "blog_status": "pending", "github_url": f'https://github.com/{config["public_repository"]}/blob/{config["branch"]}/{quote(t["target_path"])}',
             "notion_page_id": None, "notion_url": None, "blog_url": f'{config["blog_url"]}/topics/{key}/',
             "published_date": today, "content_hash": digest(body)}
    if assets:
        entry.update(assets=assets, source_content_hash=source_content_hash)
    if "## 6. 기술 면접 답변" not in body:
        entry["render_version"] = 2
        from .learning import parse_guide
        if parse_guide(body) is not None:entry["render_version"] = 3
    for rel in (entry["target_path"], entry["post_path"]):
        if safe_path(root, rel).exists():
            raise PublisherError("existing-file-protected:" + rel)
    for p in (root / "blog/_posts").glob("*.md"):
        contents = p.read_text(encoding="utf-8")
        if contents.startswith("---\n"):
            meta = yaml.safe_load(contents.split("---", 2)[1]) or {}
            if meta.get("permalink") == entry["permalink"] or meta.get("topic_id") == key:
                raise PublisherError("existing-permalink-protected")
    if dry_run:
        return result
    copy_assets(root, private, assets)
    for rel, text in ((entry["target_path"], body), (entry["post_path"], make_post(entry, body))):
        dest = safe_path(root, rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
    state["topics"][key] = entry
    update_indexes(root, state, config)
    write_json(root / ".publisher/state.json", state)
    return result
