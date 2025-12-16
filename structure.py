from __future__ import annotations

import argparse
import fnmatch
import sys
from pathlib import Path
from typing import List, Optional

import pathspec


# drawing characters
BRANCH = "├─ "
LAST   = "└─ "
VERT   = "│  "
SPACE  = "   "


class GitIgnoreMatcher:
    def __init__(self, root: Path, enabled: bool = True):
        self.root = root
        self.enabled = enabled
        self._spec = None

        if not enabled:
            return

        gi_path = root / ".gitignore"
        if gi_path.is_file():
            lines = gi_path.read_text(encoding="utf-8", errors="ignore").splitlines()
            self._spec = pathspec.PathSpec.from_lines("gitwildmatch", lines)

    def is_ignored(self, path: Path) -> bool:
        if not self.enabled or self._spec is None:
            return False

        rel = path.relative_to(self.root).as_posix()
        # match file; also match directories against patterns ending with '/'
        return self._spec.match_file(rel) or (path.is_dir() and self._spec.match_file(rel + "/"))


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Print a directory tree (respects .gitignore).")
    ap.add_argument("path", nargs="?", default=".", help="Root path (default: .)")
    ap.add_argument("--max-depth", type=int, default=None, help="Limit recursion depth")
    ap.add_argument("--all", "-a", action="store_true", help="Include hidden files/dirs (still respects .gitignore)")
    ap.add_argument(
        "--ignore",
        nargs="*",
        default=[],
        help="Additional glob patterns to ignore (e.g., --ignore __pycache__ *.pyc build/)",
    )
    ap.add_argument("--no-gitignore", action="store_true", help="Do not read or apply .gitignore")
    return ap.parse_args()


def iter_dir(directory: Path) -> List[Path]:
    try:
        return list(directory.iterdir())
    except PermissionError:
        return []


def matches_extra(p: Path, root: Path, patterns: List[str]) -> bool:
    if not patterns:
        return False
    try:
        rel = p.relative_to(root).as_posix()
    except Exception:
        rel = p.name
    return any(fnmatch.fnmatchcase(rel, pat) or fnmatch.fnmatchcase(p.name, pat) for pat in patterns)


def list_entries(
    directory: Path,
    *,
    root: Path,
    gi: GitIgnoreMatcher,
    show_all: bool,
    extra_ignores: List[str],
) -> List[Path]:
    out: List[Path] = []
    for e in iter_dir(directory):
        if not show_all and e.name.startswith("."):
            continue
        if gi.is_ignored(e):
            continue
        if matches_extra(e, root, extra_ignores):
            continue
        out.append(e)

    out.sort(key=lambda x: (x.is_file(), x.name.lower()))
    return out


def draw_tree(
    root: Path,
    *,
    max_depth: Optional[int],
    show_all: bool,
    extra_ignores: List[str],
    respect_gitignore: bool,
) -> None:
    gi = GitIgnoreMatcher(root, enabled=respect_gitignore)

    print(root.name)

    def rec(dirpath: Path, prefix: str, depth: int) -> None:
        if max_depth is not None and depth >= max_depth:
            return

        entries = list_entries(
            dirpath,
            root=root,
            gi=gi,
            show_all=show_all,
            extra_ignores=extra_ignores,
        )

        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1)
            connector = LAST if is_last else BRANCH
            suffix = "/" if entry.is_dir() else ""
            print(prefix + connector + entry.name + suffix)

            if entry.is_dir():
                rec(entry, prefix + (SPACE if is_last else VERT), depth + 1)

    if root.is_dir():
        rec(root, "", 0)


def main() -> None:
    args = parse_args()
    root = Path(args.path).resolve()

    if not root.exists():
        print(f"Error: path not found: {root}", file=sys.stderr)
        raise SystemExit(1)

    draw_tree(
        root=root,
        max_depth=args.max_depth,
        show_all=args.all,
        extra_ignores=args.ignore,
        respect_gitignore=not args.no_gitignore,
    )


if __name__ == "__main__":
    main()
