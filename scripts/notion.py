"""Notion adapter. GET retry; writes reconcile before any retry after ambiguity."""
from __future__ import annotations

import json
import os
import random
import time
from uuid import UUID
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .core import MD, PublisherError, digest, read_json, safe_path, update_indexes, write_json


class AmbiguousWrite(PublisherError):
    pass


def rich(text, **kwargs):
    result = []
    for pos in range(0, len(text), 1800):
        part = {"type": "text", "text": {"content": text[pos:pos+1800]}}
        if kwargs.get("link"):
            part["text"]["link"] = {"url": kwargs["link"]}
        annotations = {k: v for k, v in kwargs.items() if k in ("bold", "italic", "code", "strikethrough") and v}
        if annotations:
            part["annotations"] = annotations
        result.append(part)
    return result or [{"type": "text", "text": {"content": ""}}]


def inline(children):
    result, flags, link = [], {}, None
    for token in children or []:
        if token.type in ("strong_open", "em_open", "s_open"):
            flags[{"strong_open": "bold", "em_open": "italic", "s_open": "strikethrough"}[token.type]] = True
        elif token.type in ("strong_close", "em_close", "s_close"):
            flags.pop({"strong_close": "bold", "em_close": "italic", "s_close": "strikethrough"}[token.type], None)
        elif token.type == "link_open":
            link = token.attrGet("href")
        elif token.type == "link_close":
            link = None
        elif token.type in ("text", "code_inline", "softbreak", "hardbreak"):
            content = "\n" if token.type.endswith("break") else token.content
            if content:
                result += rich(content, **{**flags, "code": token.type == "code_inline", "link": link})
        else:
            raise PublisherError("unsupported-inline-markdown:" + token.type)
    if len(result) > 100:
        raise PublisherError("notion-rich-text-array-too-large")
    return result or rich("")


def block(kind, text=None, **extra):
    return {"object": "block", "type": kind, kind: {**({"rich_text": text} if text is not None else {}), **extra}}


def markdown_blocks(text, *, parse_followups=True):
    if parse_followups:
        from .learning import parse_guide
        guide = parse_guide(text)
        if guide is not None:
            result = markdown_blocks(guide.prefix, parse_followups=False)
            for q in guide.questions:
                title = inline(MD.parseInline(f"Q{q.number}. " + q.title)[0].children)
                result.append(block("toggle", title, children=markdown_blocks(q.answer, parse_followups=False)))
            return result + markdown_blocks(guide.references, parse_followups=False)
    tokens = MD.parse(text)
    i = 0

    def parse(stop=None):
        nonlocal i
        output = []
        while i < len(tokens):
            t = tokens[i]
            if t.type == stop:
                i += 1
                return output
            if t.type in ("heading_open", "paragraph_open"):
                kind = "paragraph" if t.type == "paragraph_open" else "heading_" + str(min(int(t.tag[1:]), 3))
                children = tokens[i+1].children or []
                if kind == "paragraph" and len(children) == 1 and children[0].type == "image":
                    image = children[0]
                    output.append(block("image", type="external", external={"url": image.attrGet("src")}, caption=rich(image.content)))
                else:
                    output.append(block(kind, inline(children)))
                i += 3
            elif t.type in ("fence", "code_block"):
                language = t.info.strip().split()[0] if t.info.strip() else "plain text"
                language = {"sh": "shell", "bash": "shell", "text": "plain text", "py": "python", "yml": "yaml"}.get(language, language)
                if language not in {"java", "sql", "python", "shell", "json", "yaml", "javascript", "xml", "html", "css", "c", "cpp", "plain text"}:
                    language = "plain text"
                output.append(block("code", rich(t.content), language=language)); i += 1
            elif t.type in ("bullet_list_open", "ordered_list_open"):
                kind = "bulleted_list_item" if t.type.startswith("bullet") else "numbered_list_item"
                end = t.type.replace("open", "close"); i += 1
                while tokens[i].type != end:
                    if tokens[i].type != "list_item_open":
                        raise PublisherError("invalid-list-token")
                    i += 1
                    children = parse("list_item_close")
                    first = children.pop(0) if children and children[0]["type"] == "paragraph" else block("paragraph", rich(""))
                    extra = {"children": children} if children else {}
                    output.append(block(kind, first["paragraph"]["rich_text"], **extra))
                i += 1
            elif t.type == "blockquote_open":
                i += 1
                children = parse("blockquote_close")
                first = children.pop(0) if children and children[0]["type"] == "paragraph" else block("paragraph", rich(""))
                output.append(block("quote", first["paragraph"]["rich_text"], **({"children": children} if children else {})))
            elif t.type == "hr":
                output.append(block("divider")); i += 1
            elif t.type == "table_open":
                rows = []; row = []
                i += 1
                while tokens[i].type != "table_close":
                    current = tokens[i]
                    if current.type == "tr_open":
                        row = []
                    elif current.type == "inline":
                        row.append(inline(current.children))
                    elif current.type == "tr_close":
                        rows.append(block("table_row", cells=row))
                    i += 1
                i += 1
                for start in range(1, len(rows), 90):
                    subset = [rows[0]] + rows[start:start+90]
                    output.append(block("table", table_width=len(rows[0]["table_row"]["cells"]),
                                        has_column_header=True, has_row_header=False, children=subset))
                if len(rows) == 1:
                    output.append(block("table", table_width=len(rows[0]["table_row"]["cells"]),
                                        has_column_header=True, has_row_header=False, children=rows))
            else:
                raise PublisherError("unsupported-block-markdown:" + t.type)
        return output
    return parse()


def chunks(body, github_url):
    blocks = markdown_blocks(body)
    if blocks and blocks[0]["type"] == "heading_1":
        blocks.pop(0)
    groups, title, current = [], "학습 내용", []
    for b in blocks:
        if b["type"] == "heading_2":
            if current:
                groups.append((title, current))
            title = "".join(x["text"]["content"] for x in b["heading_2"]["rich_text"])
            current = []
        else:
            current.append(b)
    if current:
        groups.append((title, current))
    result = []
    for title, group in groups:
        for offset in range(0, len(group), 70):
            subset = group[offset:offset+70]
            index = len(result)
            fingerprint = digest(json.dumps(subset, sort_keys=True, ensure_ascii=False))
            marker = f"{github_url}?cs_chunk={index:03d}-{fingerprint}"
            result.append((marker, block("toggle", rich(title, link=marker), children=subset)))
    return result


class NotionClient:
    def __init__(self, token, *, opener=urlopen, sleeper=time.sleep, max_attempts=5):
        if not token:
            raise PublisherError("missing-NOTION_API_KEY")
        self.token, self.opener, self.sleep, self.max_attempts = token, opener, sleeper, max_attempts

    def request(self, method, path, payload=None):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
        if data is not None and len(data) > 450_000:
            raise PublisherError("notion-payload-too-large")
        headers = {"Authorization": "Bearer " + self.token, "Notion-Version": "2025-09-03", "Content-Type": "application/json"}
        for attempt in range(self.max_attempts):
            try:
                self.sleep(0.35)
                with self.opener(Request("https://api.notion.com/v1/" + path, data=data, headers=headers, method=method), timeout=30) as response:
                    return json.load(response)
            except HTTPError as exc:
                # Do not log response bodies: they can echo request content.
                status = exc.code
                blocked = False
                if status == 429:
                    try:
                        detail = json.loads(exc.read())
                        blocked = detail.get("additional_data", {}).get("rate_limit_reason") == "public_api_request_blocked"
                    except (ValueError, AttributeError):
                        pass
                retry = not blocked and (status in (429, 529) or (method == "GET" and status in (500, 502, 503, 504)))
                if retry and attempt + 1 < self.max_attempts:
                    delay = float(exc.headers.get("Retry-After", min(2 ** attempt, 30)))
                    self.sleep(max(delay, 0) + random.random() * 0.2)
                    continue
                if method != "GET" and status >= 500 and status != 529:
                    raise AmbiguousWrite("notion-write-uncertain") from None
                raise PublisherError(f"notion-http-{status}") from None
            except (URLError, TimeoutError, OSError):
                if method != "GET":
                    raise AmbiguousWrite("notion-write-uncertain") from None
                if attempt + 1 == self.max_attempts:
                    raise PublisherError("notion-network-unavailable") from None
                self.sleep(min(2 ** attempt, 30))

    def children(self, parent):
        result, cursor = [], None
        while True:
            path = f"blocks/{parent}/children?page_size=100"
            if cursor:
                path += "&start_cursor=" + cursor
            response = self.request("GET", path)
            result.extend(response["results"])
            if not response.get("has_more"):
                return result
            cursor = response["next_cursor"]

    def create_page(self, parent, title, children=None):
        return self.request("POST", "pages", {"parent": {"type": "page_id", "page_id": parent},
            "properties": {"title": {"type": "title", "title": rich(title)}}, "children": children or []})


def links_from_block(b):
    data = b.get(b.get("type"), {})
    return [r.get("text", {}).get("link", {}).get("url") for r in data.get("rich_text", [])
            if r.get("text", {}).get("link")]


def ensure_hierarchy(client, state, parent, title, save, created=None, existing_only=False):
    key = parent + ":" + title
    # Always verify under the actual parent instead of trusting a stale cache.
    matches = [b for b in client.children(parent) if b.get("type") == "child_page" and b["child_page"]["title"] == title]
    if len(matches) > 1:
        raise PublisherError("notion-duplicate-hierarchy-review-required")
    if matches:
        page_id = matches[0]["id"]
    else:
        if existing_only:
            raise PublisherError("revision-hierarchy-missing")
        if key in state["notion_uncertain"]:
            raise PublisherError("notion-hierarchy-uncertain-review-required")
        # Persist the intent locally before a remote write. Commit checkpoints in finally.
        state["notion_uncertain"][key] = True; save()
        try:
            page_id = client.create_page(parent, title)["id"]
            if created is not None:
                created.append(page_id)
        except AmbiguousWrite:
            raise
        except PublisherError:
            state["notion_uncertain"].pop(key, None); save()
            raise
    state["notion_hierarchy"][key] = page_id
    state["notion_uncertain"].pop(key, None); save()
    return page_id


def preflight(root, state, config, topic, policy, client=None, parent=None, existing_topic=None):
    """Authenticate and verify the intended hierarchy before any study document is pushed."""
    parent = parent or os.environ.get("NOTION_PARENT_PAGE_ID")
    if not parent:
        raise PublisherError("missing-NOTION_PARENT_PAGE_ID")
    try:
        canonical_parent = str(UUID(parent.strip()))
        expected_parent = str(UUID(policy["expected_notion_parent_page_id"]))
    except (ValueError, AttributeError, KeyError):
        raise PublisherError("notion-parent-identifier-invalid") from None
    client = client or NotionClient(os.environ.get("NOTION_API_KEY"))
    identity = client.request("GET", "users/me")
    if identity.get("object") != "user" or not identity.get("id"):
        raise PublisherError("notion-authentication-response-invalid")
    if canonical_parent != expected_parent:
        raise PublisherError("notion-parent-does-not-match-approved-page")
    page = client.request("GET", "pages/" + canonical_parent)
    try:
        page_id = str(UUID(page.get("id", "")))
    except ValueError:
        raise PublisherError("notion-parent-response-invalid") from None
    if page_id != expected_parent:
        raise PublisherError("notion-parent-does-not-match-approved-page")
    if page.get("archived") or page.get("in_trash"):
        raise PublisherError("notion-parent-archived")
    title = ""
    for value in page.get("properties", {}).values():
        if value.get("type") == "title" or "title" in value:
            title = "".join(t.get("plain_text", t.get("text", {}).get("content", "")) for t in value.get("title", []))
            break
    if title.strip() != policy["expected_notion_parent_title"]:
        raise PublisherError("notion-parent-title-does-not-match-approved-page")
    # These are the real approved category pages, reused by the later sync step.
    # A successful create proves insert capability without creating disposable test pages.
    created = []
    state["notion_parent_url"] = "https://www.notion.so/" + canonical_parent.replace("-", "")
    def save():
        update_indexes(root, state, config)
        write_json(safe_path(root, ".publisher/state.json"), state)
    category = ensure_hierarchy(client, state, canonical_parent, config["categories"][topic["category"]], save, created, existing_only=existing_topic is not None)
    subcategory = ensure_hierarchy(client, state, category, topic["subcategory"], save, created, existing_only=existing_topic is not None)
    if existing_topic is not None:
        matches = [b for b in client.children(subcategory) if b.get("type") == "child_page" and b["child_page"]["title"] == topic["title_ko"]]
        if len(matches) != 1 or matches[0]["id"] != existing_topic.get("notion_page_id"):
            raise PublisherError("revision-page-identity-mismatch")
        actual = client.request("GET", "pages/" + existing_topic["notion_page_id"])
        if actual.get("archived") or actual.get("in_trash"):
            raise PublisherError("revision-page-archived")
    return {"authentication": "passed", "approved_parent_identity": "matched", "parent_title": "matched",
            "parent_active": True, "hierarchy_readable": True, "hierarchy_pages_created": len(created),
            "insert_permission": "verified-by-created-page" if created else "existing-hierarchy-reused"}


def sync_topic(root, state, entry, config, parent, client, save):
    if entry["notion_status"] == "complete" or entry.get("publication_status") == "withdrawn":
        return
    if entry.get("revision"):
        from .maintenance import sync_revision
        return sync_revision(root, state, entry, config, parent, client, save)
    category_id = ensure_hierarchy(client, state, parent, config["categories"][entry["category"]], save)
    parent_id = ensure_hierarchy(client, state, category_id, entry["subcategory"], save)
    candidates = [b for b in client.children(parent_id)
                  if b.get("type") == "child_page" and b["child_page"]["title"] == entry["title_ko"]]
    matches = []
    for page in candidates:
        existing = client.children(page["id"])
        if any(entry["github_url"] in links_from_block(b) for b in existing):
            matches.append((page["id"], existing))
    if len(matches) > 1:
        raise PublisherError("notion-duplicate-topic-review-required")
    if not matches:
        if candidates:
            raise PublisherError("notion-existing-manual-page-protected")
        intent = "topic:" + entry["topic_id"]
        if intent in state["notion_uncertain"] or entry.get("notion_page_id"):
            raise PublisherError("notion-page-uncertain-review-required")
        header = [block("paragraph", rich("GitHub 원문", link=entry["github_url"])),
                  block("paragraph", rich("기술 블로그", link=entry["blog_url"]))]
        state["notion_uncertain"][intent] = True; save()
        try:
            page = client.create_page(parent_id, entry["title_ko"], header)
        except AmbiguousWrite:
            raise
        except PublisherError:
            state["notion_uncertain"].pop(intent, None); save()
            raise
        page_id, existing = page["id"], header
    else:
        page_id, existing = matches[0]
    entry["notion_page_id"] = page_id
    state["notion_uncertain"].pop("topic:" + entry["topic_id"], None)
    entry["notion_url"] = "https://www.notion.so/" + page_id.replace("-", "")
    entry.pop("notion_error", None); save()
    body = safe_path(root, entry["target_path"]).read_text(encoding="utf-8")
    if digest(body) != entry["content_hash"]:
        raise PublisherError("published-source-changed-review-required")
    expected = chunks(body, entry["github_url"])
    markers = [link for b in existing for link in links_from_block(b) if "?cs_chunk=" in link]
    if len(markers) != len(set(markers)) or set(markers) - {m for m, _ in expected}:
        raise PublisherError("notion-chunk-conflict-review-required")
    for marker, b in expected:
        if marker in markers:
            if entry.get("notion_pending_chunk") == marker:
                entry.pop("notion_pending_chunk", None); save()
            continue
        if entry.get("notion_pending_chunk") == marker:
            raise PublisherError("notion-chunk-uncertain-review-required")
        entry["notion_pending_chunk"] = marker; save()
        try:
            client.request("PATCH", f"blocks/{page_id}/children", {"children": [b]})
        except AmbiguousWrite:
            raise
        except PublisherError:
            entry.pop("notion_pending_chunk", None); save()
            raise
        entry.pop("notion_pending_chunk", None); save()
    entry["notion_status"] = "complete"
    entry.pop("notion_error", None); save()


def sync(root, state, config, client=None, parent=None):
    parent = parent or os.environ.get("NOTION_PARENT_PAGE_ID")
    if not parent:
        raise PublisherError("missing-NOTION_PARENT_PAGE_ID")
    client = client or NotionClient(os.environ.get("NOTION_API_KEY"))
    # Fail before creating hierarchy if the integration cannot access its root.
    root_page = client.request("GET", "pages/" + parent)
    if root_page.get("archived") or root_page.get("in_trash"):
        raise PublisherError("notion-parent-archived")
    state["notion_parent_url"] = "https://www.notion.so/" + parent.replace("-", "")
    def save():
        update_indexes(root, state, config)
        write_json(safe_path(root, ".publisher/state.json"), state)
    failed = False
    for entry in state["topics"].values():
        if entry["github_status"] != "complete" or entry["notion_status"] == "complete":
            continue
        try:
            sync_topic(root, state, entry, config, parent, client, save)
        except PublisherError as exc:
            entry["notion_status"] = "failed"
            entry["notion_error"] = str(exc)
            failed = True
        finally:
            save()
    if failed:
        raise PublisherError("notion-sync-incomplete-see-state")
