# gitree/services/interactive_selection_service.py

"""
InteractiveSelectionService (no prompt_toolkit)

Works on the already-resolved tree produced by ItemsSelectionService (resolved_root dict):
{
  "self": Path,
  "remaining_items": int,
  "children": [Path | dict, ...],
  "truncated_entries": bool (only at top currently)
}

UI (ANSI):
- ↑/↓ move
- Space toggle (dirs toggle recursively)
- Enter confirm, Ctrl+C exit (returns current selection)

Default behavior:
- All resolved FILES start selected (checked=True), so user can deselect.
- Dirs are derived as checked if all descendant files are checked; otherwise partial.

Viewport behavior:
- Uses up to VIEWPORT_LINES for list area, but CLAMPS to terminal height so rendering never
  prints more lines than the terminal can show (prevents scroll-on-render).
- Re-renders in-place using ANSI cursor positioning (no full-screen clears per keypress).

Enhancements:
- The viewport list is rendered inside a box (Unicode box drawing).
- A scroll indicator column is shown inside the box:
  - ▲ on the first visible row when there are items above
  - ▼ on the last visible row when there are items below
  - A small thumb (█) indicates approximate scroll position when scrolling is possible
"""

from __future__ import annotations

import os
import sys
import shutil
import re
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from collections import defaultdict

from ..objects.app_context import AppContext
from ..objects.config import Config


CSI = "\x1b["

# Maximum viewport height (list area only). Actual viewport clamps to terminal rows.
VIEWPORT_LINES = 999

_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def _strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s)


def _visible_len(s: str) -> int:
    return len(_strip_ansi(s))


def _truncate_ansi(s: str, width: int) -> str:
    """
    Truncate to `width` visible characters while preserving ANSI sequences.
    """
    if width <= 0:
        return ""

    out: List[str] = []
    vis = 0
    i = 0
    n = len(s)

    while i < n and vis < width:
        ch = s[i]
        if ch == "\x1b":
            # Copy CSI sequence (best-effort)
            m = _ANSI_RE.match(s, i)
            if m:
                seq = m.group(0)
                out.append(seq)
                i = m.end()
                continue
            # Unknown escape; drop it to avoid infinite loops
            i += 1
            continue

        out.append(ch)
        vis += 1
        i += 1

    return "".join(out)


def _pad_ansi(s: str, width: int) -> str:
    """
    Right-pad to `width` visible characters. Does not trim.
    """
    pad = max(0, width - _visible_len(s))
    return s + (" " * pad)


def _ansi_hide_cursor() -> str:
    return CSI + "?25l"


def _ansi_show_cursor() -> str:
    return CSI + "?25h"


def _ansi_invert(s: str) -> str:
    return CSI + "7m" + s + CSI + "0m"


def _ansi_dim(s: str) -> str:
    return CSI + "2m" + s + CSI + "0m"


def _ansi_green(s: str) -> str:
    return CSI + "32m" + s + CSI + "0m"


def _ansi_home() -> str:
    # Move cursor to row 1, col 1
    return CSI + "H"


def _ansi_clear_screen() -> str:
    # Clear entire screen + home
    return CSI + "2J" + CSI + "H"


def _ansi_clear_to_end() -> str:
    # Clear from cursor to end of screen
    return CSI + "J"


def _ansi_clear_line() -> str:
    # Clear entire current line
    return CSI + "2K"


def _term_size() -> Tuple[int, int]:
    ts = shutil.get_terminal_size(fallback=(80, 24))
    return ts.columns, ts.lines


class _RawMode:
    """
    Minimal raw-mode wrapper for stdin.
    POSIX: termios/tty raw. Windows: no-op (uses msvcrt).
    """

    def __init__(self) -> None:
        self.is_windows = os.name == "nt"
        self._fd = None
        self._old = None

    def __enter__(self):
        if self.is_windows:
            return self
        import termios
        import tty

        self._fd = sys.stdin.fileno()
        self._old = termios.tcgetattr(self._fd)
        tty.setraw(self._fd)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.is_windows:
            return False
        import termios

        if self._fd is not None and self._old is not None:
            termios.tcsetattr(self._fd, termios.TCSADRAIN, self._old)
        return False


def _read_key() -> str:
    """
    Returns normalized key names:
      'UP','DOWN','SPACE','ENTER','CTRL_C'
    or '' if unknown.
    """
    if os.name == "nt":
        import msvcrt

        ch = msvcrt.getwch()
        if ch == "\x03":
            return "CTRL_C"
        if ch in ("\r", "\n"):
            return "ENTER"
        if ch == " ":
            return "SPACE"
        if ch in ("\x00", "\xe0"):
            ch2 = msvcrt.getwch()
            return {
                "H": "UP",    # arrow up
                "P": "DOWN",  # arrow down
            }.get(ch2, "")
        return ""

    ch = sys.stdin.read(1)
    if ch == "\x03":
        return "CTRL_C"
    if ch in ("\r", "\n"):
        return "ENTER"
    if ch == " ":
        return "SPACE"
    if ch != "\x1b":
        return ""

    nxt = sys.stdin.read(1)
    if nxt != "[":
        return ""
    code = sys.stdin.read(1)

    if code == "A":
        return "UP"
    if code == "B":
        return "DOWN"

    # Anything else (including PgUp/PgDn sequences) is ignored.
    return ""


class InteractiveSelectionService:
    @staticmethod
    def run(ctx: AppContext, config: Config, resolved_root: Dict[str, Any]) -> Dict[str, Any]:
        os.system("cls" if os.name == "nt" else "clear")
        sys.stdout.flush()

        # Build a flat view tree from already-resolved_root (no filesystem scanning)
        root_path = resolved_root.get("self")
        if not isinstance(root_path, Path):
            root_path = Path(str(root_path))

        tree: List[dict] = []
        folder_to_files: Dict[int, List[int]] = defaultdict(list)
        folder_to_subdirs: Dict[int, List[int]] = defaultdict(list)

        # Collect all resolved files for default selection state
        resolved_files = InteractiveSelectionService._collect_files(resolved_root)

        # Build flat tree with all file nodes checked by default
        InteractiveSelectionService._build_tree_from_resolved(
            resolved_node=resolved_root,
            root=root_path,
            depth=0,
            tree=tree,
            folder_to_files=folder_to_files,
            folder_to_subdirs=folder_to_subdirs,
            default_checked_files=resolved_files,
        )

        if not tree:
            return resolved_root

        # After tree is built, compute dir checked/partial state from descendants
        InteractiveSelectionService._sync_dir_states(tree, folder_to_files, folder_to_subdirs)

        cursor = 0
        scroll = 0
        first_render = True

        def _dir_desc_files(dir_index: int) -> List[int]:
            acc: List[int] = []
            acc.extend(folder_to_files.get(dir_index, []))
            for d in folder_to_subdirs.get(dir_index, []):
                acc.extend(_dir_desc_files(d))
            return acc

        def toggle_dir(index: int, state: bool) -> None:
            # Apply state to all descendant files; dirs will be recomputed
            for f in _dir_desc_files(index):
                tree[f]["checked"] = state
            InteractiveSelectionService._sync_dir_states(tree, folder_to_files, folder_to_subdirs)

        def _scroll_thumb_pos(view_h: int) -> int:
            """
            Map current scroll position to a thumb row in [0, view_h-1].
            """
            total = len(tree)
            if total <= view_h:
                return 0
            denom = max(1, total - view_h)
            ratio = scroll / denom
            return int(round(ratio * (view_h - 1)))

        def _compute_view_h(term_rows: int) -> int:
            """
            Ensure our whole UI block fits in the terminal to prevent scrolling.

            We print:
              header (1)
              top border (1)
              viewport lines (view_h)
              bottom border (1)
              footer (1)
            => view_h + 4 total lines

            Clamp view_h so (view_h + 4) <= term_rows.
            """
            min_rows_for_ui = 5  # gives view_h=1
            if term_rows < min_rows_for_ui:
                return 1
            max_h_by_term = max(1, term_rows - 4)
            return max(1, min(VIEWPORT_LINES, max_h_by_term))

        def render() -> None:
            nonlocal scroll, first_render

            cols, rows = _term_size()

            # Clamp viewport height to terminal rows so we never scroll when rendering.
            view_h = _compute_view_h(rows)

            if cursor < scroll:
                scroll = cursor
            if cursor >= scroll + view_h:
                scroll = cursor - view_h + 1

            start = scroll
            end = min(len(tree), scroll + view_h)

            selected_count = 0
            total_files = 0
            for it in tree:
                if it["type"] == "file":
                    total_files += 1
                    if it["checked"]:
                        selected_count += 1

            header = "↑/↓ Move | Space Toggle | Enter Confirm | Ctrl+C Exit"
            header = header[:cols]
            footer = f"Selected files: {selected_count}/{total_files}"
            footer = footer[:cols]

            # Box sizing:
            # We draw a box with left+right borders, and inside we reserve 1 column for a scroll indicator.
            # Minimum width to look sane: 6 columns.
            box_w = max(6, cols)
            inner_w = max(2, box_w - 2)              # area between borders
            indicator_w = 1
            content_w = max(0, inner_w - indicator_w)

            can_scroll = len(tree) > view_h
            thumb = _scroll_thumb_pos(view_h) if can_scroll else -1

            # Re-render in place:
            # - On first render: clear screen + home
            # - Thereafter: just home + overwrite the same block, clearing each line.
            if first_render:
                sys.stdout.write(_ansi_hide_cursor())
                sys.stdout.write(_ansi_clear_screen())
                first_render = False
            else:
                sys.stdout.write(_ansi_home())

            # HEADER
            sys.stdout.write(_ansi_clear_line())
            sys.stdout.write(_ansi_dim(header) + "\n")

            # TOP BORDER
            sys.stdout.write(_ansi_clear_line())
            sys.stdout.write("┌" + ("─" * inner_w) + "┐" + "\n")

            # VIEWPORT LINES (always exactly view_h lines)
            for row in range(view_h):
                idx = start + row

                # Determine scroll indicator char for this row
                ind = " "
                if can_scroll:
                    if row == 0 and scroll > 0:
                        ind = "▲"
                    elif row == view_h - 1 and end < len(tree):
                        ind = "▼"
                    elif row == thumb:
                        ind = "█"
                    else:
                        ind = "│"

                sys.stdout.write(_ansi_clear_line())
                if idx < end:
                    item = tree[idx]
                    indent = "  " * item["depth"]
                    name = item["name"]

                    if item["type"] == "dir":
                        if item.get("partial"):
                            box = "[~]"
                        else:
                            box = "[✓]" if item["checked"] else "[ ]"
                    else:
                        box = "[✓]" if item["checked"] else "[ ]"

                    box = _ansi_green(box) if (not item.get("partial") and item["checked"]) else box
                    line = f"{indent}{box} {name}"

                    # Fit into content_w visible columns while preserving ANSI
                    line = _truncate_ansi(line, content_w)
                    line = _pad_ansi(line, content_w)

                    # Highlight cursor row (invert only the content area, not borders)
                    if idx == cursor:
                        line = _ansi_invert(line)

                    sys.stdout.write("│" + line + ind + "│" + "\n")
                else:
                    # Past end of tree: blank content area to fully overwrite old content
                    blank = " " * content_w
                    sys.stdout.write("│" + blank + ind + "│" + "\n")

            # BOTTOM BORDER
            sys.stdout.write(_ansi_clear_line())
            sys.stdout.write("└" + ("─" * inner_w) + "┘" + "\n")

            # FOOTER (NO trailing newline to reduce accidental scroll on tight terminals)
            sys.stdout.write(_ansi_clear_line())
            sys.stdout.write(_ansi_dim(footer))

            # Clear anything below our block (so resizing / prior prints don't linger)
            sys.stdout.write(_ansi_clear_to_end())
            sys.stdout.flush()

        def finalize() -> Dict[str, Any]:
            selected_files: Set[Path] = set()
            for item in tree:
                if item["type"] == "file" and item["checked"]:
                    selected_files.add(item["abs_path"])
            return InteractiveSelectionService._filter_resolved_root_keep_meta(resolved_root, selected_files)

        try:
            with _RawMode():
                render()
                while True:
                    k = _read_key()
                    if not k:
                        continue

                    if k == "CTRL_C":
                        return finalize()

                    if k == "ENTER":
                        return finalize()

                    if k == "UP":
                        cursor = max(0, cursor - 1)
                        render()
                        continue

                    if k == "DOWN":
                        cursor = min(len(tree) - 1, cursor + 1)
                        render()
                        continue

                    if k == "SPACE":
                        item = tree[cursor]
                        if item["type"] == "dir":
                            # If partial or unchecked => turn ON, else turn OFF
                            if item.get("partial") or not item["checked"]:
                                toggle_dir(cursor, True)
                            else:
                                toggle_dir(cursor, False)
                        else:
                            item["checked"] = not item["checked"]
                            InteractiveSelectionService._sync_dir_states(tree, folder_to_files, folder_to_subdirs)
                        render()
                        continue
        finally:
            # Restore terminal visuals and leave it in a clean state.
            sys.stdout.write(_ansi_show_cursor())
            sys.stdout.write(CSI + "0m")
            sys.stdout.write("\n")
            sys.stdout.flush()
            os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def _collect_files(resolved_node: Dict[str, Any]) -> Set[Path]:
        out: Set[Path] = set()

        def walk(node: Dict[str, Any]) -> None:
            for ch in node.get("children", []):
                if isinstance(ch, dict):
                    walk(ch)
                else:
                    p = ch if isinstance(ch, Path) else Path(str(ch))
                    out.add(p)

        walk(resolved_node)
        return out

    @staticmethod
    def _build_tree_from_resolved(
        resolved_node: Dict[str, Any],
        root: Path,
        depth: int,
        tree: List[dict],
        folder_to_files: Dict[int, List[int]],
        folder_to_subdirs: Dict[int, List[int]],
        default_checked_files: Set[Path],
    ) -> None:
        dir_path = resolved_node.get("self")
        if not isinstance(dir_path, Path):
            dir_path = Path(str(dir_path))

        folder_index = len(tree)
        rel_dir = dir_path.relative_to(root).as_posix() or "(root)"
        name = rel_dir.split("/")[-1] + ("/" if rel_dir != "(root)" else "")

        tree.append({
            "type": "dir",
            "abs_path": dir_path,
            "name": name if rel_dir != "(root)" else "(root)/",
            "depth": depth,
            "checked": False,   # computed later
            "partial": False,   # computed later
        })

        children = resolved_node.get("children", [])
        for child in children:
            if not isinstance(child, dict):
                continue

            child_index = len(tree)
            folder_to_subdirs[folder_index].append(child_index)
            InteractiveSelectionService._build_tree_from_resolved(
                resolved_node=child,
                root=root,
                depth=depth + 1,
                tree=tree,
                folder_to_files=folder_to_files,
                folder_to_subdirs=folder_to_subdirs,
                default_checked_files=default_checked_files,
            )

        for child in children:
            if isinstance(child, dict):
                continue
            
            child_path = child if isinstance(child, Path) else Path(str(child))
            rel_path = child_path.relative_to(root).as_posix()
            file_index = len(tree)

            tree.append({
                "type": "file",
                "abs_path": child_path,
                "name": rel_path.split("/")[-1],
                "depth": depth + 1,
                "checked": (child_path in default_checked_files),
            })
            folder_to_files[folder_index].append(file_index)

    @staticmethod
    def _sync_dir_states(
        tree: List[dict],
        folder_to_files: Dict[int, List[int]],
        folder_to_subdirs: Dict[int, List[int]],
    ) -> None:
        """
        Recompute dir checked/partial based on descendant files.
        - checked=True only if ALL descendant files are checked and at least one exists
        - partial=True if SOME but not all descendant files are checked
        - unchecked if none checked
        """
        sys.setrecursionlimit(max(2000, sys.getrecursionlimit()))

        def desc_files(dir_index: int) -> List[int]:
            acc: List[int] = []
            acc.extend(folder_to_files.get(dir_index, []))
            for d in folder_to_subdirs.get(dir_index, []):
                acc.extend(desc_files(d))
            return acc

        # dirs are stored in tree in preorder; compute from bottom up for efficiency
        dir_indices = [i for i, it in enumerate(tree) if it["type"] == "dir"]
        for i in reversed(dir_indices):
            files = desc_files(i)
            if not files:
                tree[i]["checked"] = False
                tree[i]["partial"] = False
                continue
            checked = sum(1 for f in files if tree[f]["checked"])
            if checked == 0:
                tree[i]["checked"] = False
                tree[i]["partial"] = False
            elif checked == len(files):
                tree[i]["checked"] = True
                tree[i]["partial"] = False
            else:
                tree[i]["checked"] = False
                tree[i]["partial"] = True

    @staticmethod
    def _filter_resolved_root_keep_meta(resolved_root: Dict[str, Any], selected_files: Set[Path]) -> Dict[str, Any]:
        """
        Filter resolved_root to keep only selected file Paths and dirs that contain them.
        Preserves per-node 'remaining_items' if present.
        Preserves top-level 'truncated_entries' if present.
        """

        def filt(node: Dict[str, Any]) -> Dict[str, Any]:
            node_self = node.get("self")
            if not isinstance(node_self, Path):
                node_self = Path(str(node_self))

            node_remaining = node.get("remaining_items", 0)

            new_children: List[Any] = []
            for ch in node.get("children", []):
                if isinstance(ch, dict):
                    fc = filt(ch)
                    if fc.get("children"):
                        new_children.append(fc)
                else:
                    p = ch if isinstance(ch, Path) else Path(str(ch))
                    if p in selected_files:
                        new_children.append(ch)

            out = {
                "self": node_self,
                "remaining_items": node_remaining,
                "children": new_children,
            }
            return out

        out_root = filt(resolved_root)
        if "truncated_entries" in resolved_root:
            out_root["truncated_entries"] = resolved_root["truncated_entries"]
        return out_root
