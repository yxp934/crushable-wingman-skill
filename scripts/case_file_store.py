#!/usr/bin/env python3
"""
Case File Store for crushable-wingman

Persist wingman "Case Files" across sessions as Markdown files on disk.

Default storage directory:
  ~/.codex/state/crushable-wingman/case-files

Override with:
  CRUSHABLE_WINGMAN_MEMORY_DIR=/path/to/case-files
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def _slugify(value: str) -> str:
    v = value.strip().lower()
    v = re.sub(r"[^a-z0-9]+", "-", v)
    v = v.strip("-")
    v = re.sub(r"-{2,}", "-", v)
    return v or "case-file"


def _default_store_dir() -> Path:
    env = os.environ.get("CRUSHABLE_WINGMAN_MEMORY_DIR", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return (Path.home() / ".codex" / "state" / "crushable-wingman" / "case-files").resolve()


def _read_template(skill_dir: Path) -> str:
    template_path = skill_dir / ".." / "references" / "case-file-template.md"
    try:
        return template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return "# Case File\n\n"


@dataclass(frozen=True)
class ResolveResult:
    handle: str
    path: Path


def _resolve_case_file(store_dir: Path, handle_or_name: str) -> ResolveResult:
    handle = _slugify(handle_or_name)
    path = store_dir / f"{handle}.md"
    return ResolveResult(handle=handle, path=path)


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def cmd_list(args: argparse.Namespace) -> int:
    store_dir = _default_store_dir() if args.root is None else Path(args.root).expanduser().resolve()
    if not store_dir.exists():
        print(str(store_dir))
        return 0

    files = sorted(store_dir.glob("*.md"))
    print(str(store_dir))
    for f in files:
        print(f.name)
    return 0


def cmd_path(args: argparse.Namespace) -> int:
    store_dir = _default_store_dir() if args.root is None else Path(args.root).expanduser().resolve()
    resolved = _resolve_case_file(store_dir, args.handle)
    print(str(resolved.path))
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    store_dir = _default_store_dir() if args.root is None else Path(args.root).expanduser().resolve()
    resolved = _resolve_case_file(store_dir, args.handle)
    if not resolved.path.exists():
        print(f"[ERROR] Case file not found: {resolved.path}", file=sys.stderr)
        return 2
    print(resolved.path.read_text(encoding="utf-8"))
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    store_dir = _default_store_dir() if args.root is None else Path(args.root).expanduser().resolve()
    _ensure_dir(store_dir)

    handle = args.handle.strip()
    if not handle:
        print("[ERROR] --handle is required", file=sys.stderr)
        return 2

    resolved = _resolve_case_file(store_dir, handle)
    if resolved.path.exists() and not args.force:
        print(f"[ERROR] Case file already exists: {resolved.path}", file=sys.stderr)
        return 2

    skill_dir = Path(__file__).resolve().parent
    template = _read_template(skill_dir)

    header = f"# Case File: {args.name.strip()} ({resolved.handle})\n\n" if args.name else f"# Case File ({resolved.handle})\n\n"
    content = header + template.strip() + "\n"
    resolved.path.write_text(content, encoding="utf-8")
    print(str(resolved.path))
    return 0


def cmd_upsert(args: argparse.Namespace) -> int:
    store_dir = _default_store_dir() if args.root is None else Path(args.root).expanduser().resolve()
    _ensure_dir(store_dir)
    resolved = _resolve_case_file(store_dir, args.handle)

    incoming = sys.stdin.read()
    if not incoming.strip():
        print("[ERROR] No content provided on stdin", file=sys.stderr)
        return 2

    resolved.path.write_text(incoming, encoding="utf-8")
    print(str(resolved.path))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Persist crushable-wingman case files as local Markdown files.")
    parser.add_argument("--root", help="Override case file directory (default: CRUSHABLE_WINGMAN_MEMORY_DIR or ~/.codex/state/...).")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List case files")
    p_list.set_defaults(func=cmd_list)

    p_path = sub.add_parser("path", help="Print the path for a handle/name")
    p_path.add_argument("--handle", required=True, help="Handle or name (will be slugified)")
    p_path.set_defaults(func=cmd_path)

    p_show = sub.add_parser("show", help="Print a case file")
    p_show.add_argument("--handle", required=True, help="Handle or name (will be slugified)")
    p_show.set_defaults(func=cmd_show)

    p_init = sub.add_parser("init", help="Create a new case file from the template")
    p_init.add_argument("--handle", required=True, help="Short stable handle (e.g., alex-work)")
    p_init.add_argument("--name", help="Display name (for the file header)")
    p_init.add_argument("--force", action="store_true", help="Overwrite if exists")
    p_init.set_defaults(func=cmd_init)

    p_upsert = sub.add_parser("upsert", help="Write case file content from stdin (creates or overwrites)")
    p_upsert.add_argument("--handle", required=True, help="Handle or name (will be slugified)")
    p_upsert.set_defaults(func=cmd_upsert)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
