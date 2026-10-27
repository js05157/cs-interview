"""python -m scripts.cli --help"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from .core import (PublisherError, digest, load_catalog, load_state, lock, prepare, read_json,
                   safe_path, update_indexes, validate_markdown, write_json)


def git(root, *args):
    completed = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if completed.returncode:
        # Git errors may contain credential helpers' private data. Keep diagnostics categorical.
        raise PublisherError("git-operation-failed:" + args[0])
    return completed.stdout.strip()


def enforce_approval(state, preview, policy):
    allowed = set(policy.get("allowed_topic_ids", []))
    if not allowed or set(state["topics"]) - allowed:
        raise PublisherError("publication-state-outside-approved-scope")
    if preview.get("topic_id") is not None and preview["topic_id"] not in allowed:
        raise PublisherError("topic-not-approved-for-publication")


def commit(root, message):
    config = read_json(root / "config/publisher.json")
    if git(root, "branch", "--show-current") != config["branch"]:
        raise PublisherError("master-branch-required")
    origin = git(root, "remote", "get-url", "origin")
    if origin.removesuffix(".git") != "https://github.com/" + config["public_repository"]:
        raise PublisherError("unexpected-origin")
    state = load_state(root)
    files = [".publisher/state.json", "README.md", "blog/_data/publisher.json"]
    for t in state["topics"].values():
        files += [t["target_path"], t["post_path"]]
    git(root, "add", "--", *files)
    staged = git(root, "diff", "--cached", "--name-only")
    if set(staged.splitlines()) - set(files):
        raise PublisherError("unrelated-staged-files-protected")
    if staged:
        git(root, "-c", "user.name=github-actions[bot]", "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
            "commit", "-m", message)
    # Push even after a previous interrupted commit. No force or automatic rebase.
    git(root, "push", "origin", "HEAD:" + config["branch"])


def receipt(root):
    state = load_state(root)
    result = {}
    for key, t in state["topics"].items():
        if t["github_status"] != "complete":
            continue
        source = safe_path(root, t["target_path"]).read_text(encoding="utf-8")
        from .core import make_post
        if digest(source) != t["content_hash"] or safe_path(root, t["post_path"]).read_text(encoding="utf-8") != make_post(t, source):
            raise PublisherError("deployment-source-mismatch")
        result[key] = t["content_hash"]
    return result


def mark_blog(root, result, included):
    state = load_state(root)
    for key, content_hash in included.items():
        if key not in state["topics"] or state["topics"][key]["content_hash"] != content_hash:
            raise PublisherError("deployment-receipt-mismatch")
    for key, entry in state["topics"].items():
        if key in included:
            entry["blog_status"] = "complete" if result == "success" else "failed"
            if result != "success":
                entry["blog_error"] = "pages-build-or-deploy-failed"
            else:
                entry.pop("blog_error", None)
    update_indexes(root, state, read_json(root / "config/publisher.json"))
    write_json(root / ".publisher/state.json", state)


def main(argv=None):
    parser = argparse.ArgumentParser(description="CS publisher. dry-run is the default; no AI API is used.")
    parser.add_argument("command", choices=["validate", "prepare", "sync-notion", "receipt", "mark-blog", "add-topic"])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--private", type=Path)
    parser.add_argument("--mode", choices=["dry-run", "publish"], default="dry-run")
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--initial", action="store_true")
    parser.add_argument("--result", choices=["success", "failure"], default="failure")
    parser.add_argument("--topic-file", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "validate":
            catalog, queue = load_catalog(args.private, initial=args.initial)
            count, hashes = 0, set()
            missing = []
            for key in queue:
                path = safe_path(args.private, catalog[key]["source_path"])
                if path.exists():
                    body = path.read_text(encoding="utf-8")
                    validate_markdown(body)
                    if digest(body) in hashes:
                        raise PublisherError("duplicate-document-body")
                    hashes.add(digest(body)); count += 1
                else:
                    missing.append(key)
            print(json.dumps({"topics": len(catalog), "documents": count, "remaining": len(missing)}, ensure_ascii=False))
            return 0
        if args.command == "receipt":
            print(json.dumps(receipt(root), separators=(",", ":")))
            return 0
        if args.command == "add-topic":
            catalog, queue = load_catalog(args.private)
            entry = read_json(args.topic_file)
            if entry["topic_id"] in catalog:
                raise PublisherError("duplicate-topic")
            entry["publish_order"] = len(queue) + 1
            topics_path = args.private / "manifests/topics.json"
            queue_path = args.private / "manifests/publish_queue.json"
            old_topics, old_queue = read_json(topics_path), read_json(queue_path)
            if args.mode != "publish":
                print("dry-run: catalog unchanged")
                return 0
            try:
                write_json(topics_path, old_topics + [entry]); write_json(queue_path, old_queue + [entry["topic_id"]])
                load_catalog(args.private)
            except Exception:
                write_json(topics_path, old_topics); write_json(queue_path, old_queue)
                raise
            print("topic-added-to-private-catalog")
            return 0
        if args.mode == "dry-run":
            if args.command != "prepare":
                raise PublisherError("publish-mode-required-for-mutation")
            print(json.dumps(prepare(root, args.private, dry_run=True), ensure_ascii=False))
            return 0
        if args.commit:
            # Reject dirty worktrees before preparation; state retries use clean clones.
            if git(root, "status", "--porcelain"):
                raise PublisherError("clean-worktree-required")
        with lock(root):
            if args.command == "prepare":
                # Missing auth fails before a public reservation is made.
                if args.commit:
                    for variable in ("NOTION_API_KEY", "NOTION_PARENT_PAGE_ID", "CONTENT_REPO_TOKEN"):
                        if not os.environ.get(variable):
                            raise PublisherError("missing-" + variable)
                    policy = read_json(root / "config/publication_policy.json")
                    preview = prepare(root, args.private, dry_run=True)
                    state = load_state(root)
                    enforce_approval(state, preview, policy)
                    key = preview["topic_id"]
                    if key and state["topics"].get(key, {}).get("notion_status") != "complete":
                        from .notion import preflight
                        catalog, _ = load_catalog(args.private)
                        try:
                            checked = preflight(root, state, read_json(root / "config/publisher.json"), catalog[key], policy)
                        except PublisherError as preflight_error:
                            print("notion-preflight-failed: " + str(preflight_error), file=sys.stderr, flush=True)
                            # No study document has been created yet. Preserve only
                            # hierarchy/ambiguous-write metadata when that has changed.
                            if git(root, "status", "--porcelain"):
                                try:
                                    commit(root, "chore: checkpoint Notion preflight metadata")
                                except PublisherError:
                                    print("notion-preflight-checkpoint-push-failed", file=sys.stderr, flush=True)
                            raise preflight_error
                        print("notion-preflight: " + json.dumps(checked, ensure_ascii=True), flush=True)
                result = prepare(root, args.private, dry_run=False)
                if args.commit and result["topic_id"]:
                    state = load_state(root)
                    commit(root, "docs: add daily CS topic - " + state["topics"][result["topic_id"]]["title_ko"]
                           if result["action"] == "new" else "chore: reconcile CS publication")
                state = load_state(root)
                result["needs_notion"] = any(t["notion_status"] != "complete" for t in state["topics"].values())
                result["needs_blog"] = any(t["blog_status"] != "complete" for t in state["topics"].values())
                if os.environ.get("GITHUB_OUTPUT"):
                    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output:
                        for key in ("action", "needs_notion", "needs_blog"):
                            output.write(f"{key}={str(result[key]).lower()}\n")
                print(json.dumps(result, ensure_ascii=False))
            elif args.command == "sync-notion":
                from .notion import sync
                try:
                    sync(root, load_state(root), read_json(root / "config/publisher.json"))
                finally:
                    if args.commit:
                        commit(root, "chore: checkpoint Notion publication state")
            elif args.command == "mark-blog":
                included = json.loads(os.environ.get("CS_DEPLOYMENT_RECEIPT", "{}"))
                if not included and load_state(root)["topics"]:
                    raise PublisherError("deployment-receipt-required")
                mark_blog(root, args.result, included)
                if args.commit:
                    commit(root, "chore: checkpoint GitHub Pages publication state")
        return 0
    except (PublisherError, FileNotFoundError, KeyError, ValueError, TypeError) as exc:
        # Do not include raw payloads, exception reprs, API responses or secrets.
        message = str(exc) if isinstance(exc, PublisherError) else "configuration-or-file-invalid"
        print("publisher-error: " + message, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
