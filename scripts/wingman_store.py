#!/usr/bin/env python3
"""
wingman_store.py

Local Markdown persistence for the crushable-wingman skill:
- user profile + user long-term memory snapshot
- per-crush profile + per-crush long-term memory snapshot + append-only logs
- active crush handle selection

Default state directory:
  ~/.codex/state/crushable-wingman

Override with:
  CRUSHABLE_WINGMAN_STATE_DIR=/path/to/state
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional


def _slugify(value: str) -> str:
    v = value.strip().lower()
    v = re.sub(r"[^a-z0-9]+", "-", v)
    v = v.strip("-")
    v = re.sub(r"-{2,}", "-", v)
    return v or "case"


def _state_dir() -> Path:
    env = os.environ.get("CRUSHABLE_WINGMAN_STATE_DIR", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return (Path.home() / ".codex" / "state" / "crushable-wingman").resolve()


def _skill_root() -> Path:
    # .../crushable-wingman-skill/scripts/wingman_store.py -> .../crushable-wingman-skill
    return Path(__file__).resolve().parent.parent


def _refs_dir() -> Path:
    return _skill_root() / "references"


def _read_template(filename: str) -> str:
    p = _refs_dir() / filename
    return p.read_text(encoding="utf-8")


def _render_template(template: str, *, date: str, handle: str = "", crush_name: str = "", title: str = "") -> str:
    return (
        template.replace("{{DATE}}", date)
        .replace("{{DATE_TIME}}", date)
        .replace("{{HANDLE}}", handle)
        .replace("{{CRUSH_NAME}}", crush_name)
        .replace("{{TITLE}}", title)
    )


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _active_handle_path(root: Path) -> Path:
    return root / "active_handle.txt"


def _user_dir(root: Path) -> Path:
    return root / "user"


def _user_profile_path(root: Path) -> Path:
    return _user_dir(root) / "profile.md"


def _user_memory_path(root: Path) -> Path:
    return _user_dir(root) / "memory.md"


def _crushes_dir(root: Path) -> Path:
    return root / "crushes"


def _crush_dir(root: Path, handle: str) -> Path:
    return _crushes_dir(root) / _slugify(handle)


def _crush_profile_path(root: Path, handle: str) -> Path:
    return _crush_dir(root, handle) / "profile.md"


def _crush_memory_path(root: Path, handle: str) -> Path:
    return _crush_dir(root, handle) / "memory.md"


def _crush_log_dir(root: Path, handle: str) -> Path:
    return _crush_dir(root, handle) / "log"


def _now_stamp() -> str:
    return datetime.now().strftime("%Y-%m-%d-%H%M")


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _read_stdin() -> str:
    try:
        return sys.stdin.read()
    except KeyboardInterrupt:
        return ""


def _write_text(path: Path, content: str) -> None:
    _ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def _print_path(path: Path) -> int:
    print(str(path))
    return 0


def _print_file(path: Path) -> int:
    if not path.exists():
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        return 2
    print(path.read_text(encoding="utf-8"))
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    _ensure_dir(root)
    _ensure_dir(_user_dir(root))
    _ensure_dir(_crushes_dir(root))

    date = _today()

    profile_path = _user_profile_path(root)
    if not profile_path.exists() or args.force:
        tmpl = _read_template("user-profile-template.md")
        content = _render_template(tmpl, date=date)
        _write_text(profile_path, content.rstrip() + "\n")

    memory_path = _user_memory_path(root)
    if not memory_path.exists() or args.force:
        tmpl = _read_template("user-memory-template.md")
        content = _render_template(tmpl, date=date)
        _write_text(memory_path, content.rstrip() + "\n")

    print(str(root))
    return 0


def cmd_paths(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    print(f"STATE_DIR={root}")
    print(f"ACTIVE_HANDLE={_active_handle_path(root)}")
    print(f"USER_PROFILE={_user_profile_path(root)}")
    print(f"USER_MEMORY={_user_memory_path(root)}")
    print(f"CRUSHES_DIR={_crushes_dir(root)}")
    return 0


def cmd_user_init(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    _ensure_dir(_user_dir(root))
    date = _today()

    profile_path = _user_profile_path(root)
    if profile_path.exists() and not args.force:
        print(f"[ERROR] User profile already exists: {profile_path}", file=sys.stderr)
        return 2
    tmpl = _read_template("user-profile-template.md")
    content = _render_template(tmpl, date=date)
    _write_text(profile_path, content.rstrip() + "\n")
    return _print_path(profile_path)


def cmd_user_show_profile(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    return _print_file(_user_profile_path(root))


def cmd_user_show_memory(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    return _print_file(_user_memory_path(root))


def cmd_user_upsert_profile(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    incoming = _read_stdin()
    if not incoming.strip():
        print("[ERROR] No content provided on stdin", file=sys.stderr)
        return 2
    _write_text(_user_profile_path(root), incoming.rstrip() + "\n")
    return _print_path(_user_profile_path(root))


def cmd_user_upsert_memory(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    incoming = _read_stdin()
    if not incoming.strip():
        print("[ERROR] No content provided on stdin", file=sys.stderr)
        return 2
    _write_text(_user_memory_path(root), incoming.rstrip() + "\n")
    return _print_path(_user_memory_path(root))


_FIELD_LINE_RE = re.compile(r"^\s*-\s+([a-z0-9_]+)\s*:\s*(.*)\s*$")


def _iter_field_lines(markdown: str) -> Iterable[tuple[str, str]]:
    for line in markdown.splitlines():
        m = _FIELD_LINE_RE.match(line)
        if not m:
            continue
        yield (m.group(1), m.group(2).strip())


def _is_missing_value(v: str) -> bool:
    if v == "":
        return True
    lowered = v.lower()
    if lowered in {"null", "none"}:
        return True
    if lowered.replace(" ", "") in {"[]", "[ ]"}:
        return True
    return False


def cmd_user_missing(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    p = _user_profile_path(root)
    if not p.exists():
        print("[ERROR] User profile not found. Run: python scripts/wingman_store.py user init", file=sys.stderr)
        return 2
    txt = p.read_text(encoding="utf-8")
    missing = [k for (k, v) in _iter_field_lines(txt) if _is_missing_value(v)]
    for k in missing:
        print(k)
    return 0


def cmd_crush_list(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    d = _crushes_dir(root)
    if not d.exists():
        print(str(d))
        return 0
    print(str(d))
    for child in sorted(d.iterdir()):
        if child.is_dir():
            print(child.name)
    return 0


def cmd_crush_init(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    handle = _slugify(args.handle)
    crush_name = (args.name or handle).strip()
    date = _today()

    cdir = _crush_dir(root, handle)
    if cdir.exists() and not args.force:
        print(f"[ERROR] Crush already exists: {cdir}", file=sys.stderr)
        return 2

    _ensure_dir(cdir)
    _ensure_dir(_crush_log_dir(root, handle))

    profile_tmpl = _read_template("crush-profile-template.md")
    profile = _render_template(profile_tmpl, date=date, handle=handle, crush_name=crush_name)
    _write_text(_crush_profile_path(root, handle), profile.rstrip() + "\n")

    memory_tmpl = _read_template("crush-memory-template.md")
    memory = _render_template(memory_tmpl, date=date, handle=handle, crush_name=crush_name)
    _write_text(_crush_memory_path(root, handle), memory.rstrip() + "\n")

    print(str(cdir))
    return 0


def cmd_crush_set_active(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    handle = _slugify(args.handle)
    _ensure_dir(root)
    _write_text(_active_handle_path(root), handle + "\n")
    return 0


def cmd_crush_get_active(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    p = _active_handle_path(root)
    if not p.exists():
        return 0
    print(p.read_text(encoding="utf-8").strip())
    return 0


def cmd_crush_show_profile(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    return _print_file(_crush_profile_path(root, args.handle))


def cmd_crush_show_memory(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    return _print_file(_crush_memory_path(root, args.handle))


def cmd_crush_upsert_profile(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    incoming = _read_stdin()
    if not incoming.strip():
        print("[ERROR] No content provided on stdin", file=sys.stderr)
        return 2
    _write_text(_crush_profile_path(root, args.handle), incoming.rstrip() + "\n")
    return _print_path(_crush_profile_path(root, args.handle))


def cmd_crush_upsert_memory(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    incoming = _read_stdin()
    if not incoming.strip():
        print("[ERROR] No content provided on stdin", file=sys.stderr)
        return 2
    _write_text(_crush_memory_path(root, args.handle), incoming.rstrip() + "\n")
    return _print_path(_crush_memory_path(root, args.handle))


def cmd_crush_missing(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    p = _crush_profile_path(root, args.handle)
    if not p.exists():
        print("[ERROR] Crush profile not found. Run: python scripts/wingman_store.py crush init --handle ...", file=sys.stderr)
        return 2
    txt = p.read_text(encoding="utf-8")
    missing = [k for (k, v) in _iter_field_lines(txt) if _is_missing_value(v)]
    for k in missing:
        print(k)
    return 0


def cmd_crush_append_log(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    handle = _slugify(args.handle)
    log_dir = _crush_log_dir(root, handle)
    _ensure_dir(log_dir)

    incoming = _read_stdin()
    stamp = _now_stamp()
    filename = f"{stamp}.md"
    path = log_dir / filename

    if incoming.strip():
        content = incoming
    else:
        tmpl = _read_template("memory-log-template.md")
        title = (args.title or "Session").strip()
        # crush name is optional here; keep handle if unknown
        content = _render_template(tmpl, date=stamp, handle=handle, crush_name=args.crush_name or handle, title=title)

    _write_text(path, content.rstrip() + "\n")
    return _print_path(path)


@dataclass(frozen=True)
class SnapshotLimits:
    max_chars: int = 1200
    max_key_memories: int = 20
    max_open_loops: int = 5
    max_next_steps: int = 1


def _section_lines(text: str, heading_prefix: str) -> list[str]:
    lines = text.splitlines()
    start: Optional[int] = None
    for i, line in enumerate(lines):
        if line.strip().startswith("## ") and line.strip()[3:].startswith(heading_prefix):
            start = i + 1
            break
    if start is None:
        return []
    out: list[str] = []
    for j in range(start, len(lines)):
        if lines[j].strip().startswith("## "):
            break
        out.append(lines[j])
    return out


def _count_bullets(lines: list[str]) -> int:
    return sum(1 for l in lines if l.lstrip().startswith("- "))


def _validate_snapshot(path: Path, limits: SnapshotLimits) -> list[str]:
    if not path.exists():
        return [f"Missing snapshot: {path}"]
    txt = path.read_text(encoding="utf-8").strip()
    errors: list[str] = []

    if len(txt) > limits.max_chars:
        errors.append(f"{path.name}: too long ({len(txt)} chars > {limits.max_chars})")

    key_lines = _section_lines(txt, "Key Memories")
    open_lines = _section_lines(txt, "Open Loops")
    next_lines = _section_lines(txt, "Next Step")

    key_count = _count_bullets(key_lines)
    open_count = _count_bullets(open_lines)
    next_count = _count_bullets(next_lines)

    if key_count > limits.max_key_memories:
        errors.append(f"{path.name}: too many Key Memories ({key_count} > {limits.max_key_memories})")
    if open_count > limits.max_open_loops:
        errors.append(f"{path.name}: too many Open Loops ({open_count} > {limits.max_open_loops})")
    if next_count > limits.max_next_steps:
        errors.append(f"{path.name}: too many Next Step bullets ({next_count} > {limits.max_next_steps})")

    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    root = _state_dir() if args.root is None else Path(args.root).expanduser().resolve()
    limits = SnapshotLimits()
    errors: list[str] = []

    # User snapshot
    errors.extend(_validate_snapshot(_user_memory_path(root), limits))

    # Crush snapshot (optional)
    if args.handle:
        errors.extend(_validate_snapshot(_crush_memory_path(root, args.handle), limits))

    if errors:
        for e in errors:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 2

    print("OK")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Local Markdown store for crushable-wingman (profiles + long-term memory).")
    p.add_argument("--root", help="Override state directory (default: CRUSHABLE_WINGMAN_STATE_DIR or ~/.codex/state/...).")

    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize state dir + user templates")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing user templates")
    p_init.set_defaults(func=cmd_init)

    p_paths = sub.add_parser("paths", help="Print key paths")
    p_paths.set_defaults(func=cmd_paths)

    p_validate = sub.add_parser("validate", help="Validate snapshot constraints (user + optional crush)")
    p_validate.add_argument("--handle", help="Validate this crush snapshot too")
    p_validate.set_defaults(func=cmd_validate)

    # user
    p_user = sub.add_parser("user", help="User profile + memory")
    user_sub = p_user.add_subparsers(dest="user_cmd", required=True)

    pu_init = user_sub.add_parser("init", help="Create user profile template")
    pu_init.add_argument("--force", action="store_true", help="Overwrite if exists")
    pu_init.set_defaults(func=cmd_user_init)

    pu_show_profile = user_sub.add_parser("show-profile", help="Print user profile.md")
    pu_show_profile.set_defaults(func=cmd_user_show_profile)

    pu_show_memory = user_sub.add_parser("show-memory", help="Print user memory.md")
    pu_show_memory.set_defaults(func=cmd_user_show_memory)

    pu_upsert_profile = user_sub.add_parser("upsert-profile", help="Write user profile.md from stdin")
    pu_upsert_profile.set_defaults(func=cmd_user_upsert_profile)

    pu_upsert_memory = user_sub.add_parser("upsert-memory", help="Write user memory.md from stdin")
    pu_upsert_memory.set_defaults(func=cmd_user_upsert_memory)

    pu_missing = user_sub.add_parser("missing", help="Print missing user profile field keys")
    pu_missing.set_defaults(func=cmd_user_missing)

    # crush
    p_crush = sub.add_parser("crush", help="Crush profiles, memory snapshots, and logs")
    crush_sub = p_crush.add_subparsers(dest="crush_cmd", required=True)

    pc_list = crush_sub.add_parser("list", help="List crush handles")
    pc_list.set_defaults(func=cmd_crush_list)

    pc_init = crush_sub.add_parser("init", help="Create crush folder + templates")
    pc_init.add_argument("--handle", required=True, help="Stable hyphen-case handle (will be slugified)")
    pc_init.add_argument("--name", help="Display name")
    pc_init.add_argument("--force", action="store_true", help="Overwrite if exists")
    pc_init.set_defaults(func=cmd_crush_init)

    pc_set_active = crush_sub.add_parser("set-active", help="Set active handle")
    pc_set_active.add_argument("--handle", required=True)
    pc_set_active.set_defaults(func=cmd_crush_set_active)

    pc_get_active = crush_sub.add_parser("get-active", help="Print active handle")
    pc_get_active.set_defaults(func=cmd_crush_get_active)

    pc_show_profile = crush_sub.add_parser("show-profile", help="Print crush profile.md")
    pc_show_profile.add_argument("--handle", required=True)
    pc_show_profile.set_defaults(func=cmd_crush_show_profile)

    pc_show_memory = crush_sub.add_parser("show-memory", help="Print crush memory.md")
    pc_show_memory.add_argument("--handle", required=True)
    pc_show_memory.set_defaults(func=cmd_crush_show_memory)

    pc_upsert_profile = crush_sub.add_parser("upsert-profile", help="Write crush profile.md from stdin")
    pc_upsert_profile.add_argument("--handle", required=True)
    pc_upsert_profile.set_defaults(func=cmd_crush_upsert_profile)

    pc_upsert_memory = crush_sub.add_parser("upsert-memory", help="Write crush memory.md from stdin")
    pc_upsert_memory.add_argument("--handle", required=True)
    pc_upsert_memory.set_defaults(func=cmd_crush_upsert_memory)

    pc_missing = crush_sub.add_parser("missing", help="Print missing crush profile field keys")
    pc_missing.add_argument("--handle", required=True)
    pc_missing.set_defaults(func=cmd_crush_missing)

    pc_append_log = crush_sub.add_parser("append-log", help="Append a new log entry (from stdin or template)")
    pc_append_log.add_argument("--handle", required=True)
    pc_append_log.add_argument("--title", help="Title when generating from template")
    pc_append_log.add_argument("--crush-name", help="Crush name when generating from template")
    pc_append_log.set_defaults(func=cmd_crush_append_log)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())

