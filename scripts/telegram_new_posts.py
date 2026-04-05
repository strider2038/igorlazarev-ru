#!/usr/bin/env python3
"""Announce newly added Hugo posts in Telegram via OpenRouter summaries."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path


ZERO_SHA = "0" * 40


@dataclass
class Post:
    path: Path
    title: str
    slug: str
    draft: bool
    body: str
    url: str


@dataclass
class PreparedAnnouncement:
    post: Post
    summary: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send Telegram announcements for newly added Hugo posts."
    )
    parser.add_argument("--repo-root", default=".", help="Path to repository root")
    parser.add_argument("--before", required=True, help="Previous commit SHA")
    parser.add_argument("--after", required=True, help="Current commit SHA")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prepared announcements instead of sending them",
    )
    return parser.parse_args()


def run_git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def parse_hugo_config(config_path: Path) -> tuple[str, str]:
    base_url = None
    post_permalink = None
    in_permalinks = False

    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if not raw_line.startswith(" "):
            in_permalinks = stripped == "permalinks:"

        if stripped.startswith("baseurl:"):
            base_url = stripped.split(":", 1)[1].strip().strip("'\"")
            continue

        if in_permalinks and stripped.startswith("post:"):
            post_permalink = stripped.split(":", 1)[1].strip().strip("'\"")

    if not base_url:
        raise ValueError("Failed to parse baseurl from hugo.yaml")
    if not post_permalink:
        raise ValueError("Failed to parse post permalink pattern from hugo.yaml")

    return base_url.rstrip("/"), post_permalink


def detect_new_post_files(repo_root: Path, before: str, after: str) -> list[Path]:
    if before == ZERO_SHA:
        print("Skipping announcement: before SHA is all zeros.", file=sys.stderr)
        return []

    diff_output = run_git(
        repo_root,
        "diff",
        "--name-only",
        "--diff-filter=A",
        before,
        after,
        "--",
        "content/post",
    )

    files = []
    for line in diff_output.splitlines():
        stripped = line.strip()
        if stripped and stripped.startswith("content/post/") and stripped.endswith("/index.md"):
            files.append(repo_root / stripped)
    return files


def parse_front_matter_and_body(text: str) -> tuple[dict[str, object], str]:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        raise ValueError("Expected YAML front matter delimited by ---")

    front_lines: list[str] = []
    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
        front_lines.append(lines[idx])

    if end_idx is None:
        raise ValueError("Unclosed YAML front matter")

    metadata: dict[str, object] = {}
    for raw_line in front_lines:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        metadata[key.strip()] = parse_scalar(value.strip())

    body = "\n".join(lines[end_idx + 1 :]).strip()
    return metadata, body


def parse_scalar(value: str) -> object:
    if not value:
        return ""
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if (value.startswith("'") and value.endswith("'")) or (
        value.startswith('"') and value.endswith('"')
    ):
        return value[1:-1]
    return value


def clean_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_lead_text(raw_body: str) -> str:
    lead = raw_body
    if "<!--more-->" in lead:
        lead = lead.split("<!--more-->", 1)[0]
    lead = clean_markdown(lead)
    return lead[:2000].strip()


def build_post_url(base_url: str, post_permalink: str, slug: str) -> str:
    path = post_permalink.replace(":slug", slug)
    return f"{base_url}{path}"


def load_post(path: Path, base_url: str, post_permalink: str) -> Post:
    text = path.read_text(encoding="utf-8")
    metadata, body = parse_front_matter_and_body(text)
    title = str(metadata.get("title") or "").strip()
    slug = str(metadata.get("slug") or "").strip()
    draft = bool(metadata.get("draft") is True)

    if not title:
        raise ValueError(f"Missing title in {path}")
    if not slug:
        raise ValueError(f"Missing slug in {path}")

    return Post(
        path=path,
        title=title,
        slug=slug,
        draft=draft,
        body=clean_markdown(body),
        url=build_post_url(base_url, post_permalink, slug),
    )


def request_openrouter_summary(post: Post) -> str:
    api_key = required_env("OPENROUTER_API_KEY")
    model = os.environ.get("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    raw_text = post.path.read_text(encoding="utf-8")
    _, raw_body = parse_front_matter_and_body(raw_text)
    lead_text = extract_lead_text(raw_body)

    prompt = (
        "Сожми начало статьи в короткое сообщение для Telegram-канала на русском языке.\n"
        "Требования:\n"
        "- 2-4 предложения\n"
        "- максимально сохраняй формулировки и смысл из начала статьи\n"
        "- главная задача: аккуратно сократить текст до формата короткого Telegram-сообщения\n"
        "- не пересказывай статью заново своими словами без необходимости\n"
        "- допустимы только минимальные правки ради краткости, связности и читабельности\n"
        "- живой, естественный тон\n"
        "- без хэштегов\n"
        "- без markdown и кавычек-елочек\n"
        "- не добавляй фактов, которых нет в тексте\n\n"
        f"Заголовок: {post.title}\n"
        f"Начало статьи: {lead_text}\n\n"
        f"Полный текст статьи для контекста: {post.body[:6000]}"
    )

    payload = {
        "model": model,
        "temperature": 0.5,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты готовишь короткие Telegram-анонсы новых публикаций технического блога. "
                    "Нужно бережно сжимать начало статьи, не искажая смысл и не добавляя новых "
                    "утверждений от себя."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    }

    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://igorlazarev.ru",
            "X-OpenRouter-Title": "igorlazarev.ru post announcements",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_data = json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenRouter request failed: {exc.code} {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"OpenRouter request failed: {exc}") from exc

    try:
        content = response_data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected OpenRouter response: {response_data}") from exc

    summary = re.sub(r"\s+", " ", str(content)).strip()
    if not summary:
        raise RuntimeError("OpenRouter returned an empty summary")

    return summary


def send_telegram_message(text: str) -> None:
    token = required_env("TELEGRAM_BOT_TOKEN")
    chat_id = required_env("TELEGRAM_CHAT_ID")

    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "false",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram request failed: {exc.code} {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Telegram request failed: {exc}") from exc

    if not data.get("ok"):
        raise RuntimeError(f"Telegram API returned error: {data}")


def format_message(post: Post, summary: str) -> str:
    return f"{post.title}\n\n{summary}\n\n{post.url}"


def required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable is missing: {name}")
    return value


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    base_url, post_permalink = parse_hugo_config(repo_root / "hugo.yaml")
    new_files = detect_new_post_files(repo_root, args.before, args.after)

    if not new_files:
        print("No newly added posts detected.")
        return 0

    posts = [
        load_post(path, base_url=base_url, post_permalink=post_permalink)
        for path in new_files
    ]
    posts = [post for post in posts if not post.draft]

    if not posts:
        print("No publishable new posts detected after draft filtering.")
        return 0

    prepared: list[PreparedAnnouncement] = []
    for post in posts:
        summary = request_openrouter_summary(post)
        prepared.append(PreparedAnnouncement(post=post, summary=summary))

    if args.dry_run:
        for item in prepared:
            print("---")
            print(format_message(item.post, item.summary))
        return 0

    for item in prepared:
        send_telegram_message(format_message(item.post, item.summary))
        print(f"Sent Telegram announcement for {item.post.path.relative_to(repo_root)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
