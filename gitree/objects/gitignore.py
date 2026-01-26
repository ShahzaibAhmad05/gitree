# gitree/objects/gitignore.py

"""
Code file for housing GitIgnore class with performance optimizations.
"""

# Default libs
from pathlib import Path
from typing import Iterable, Optional

# Dependencies
import pathspec

# Deps from this project
from ..objects.app_context import AppContext
from ..objects.config import Config


class GitIgnore:
    """
    Optimized gitignore loader/matcher with caching and performance improvements.

    Performance optimizations:
    - Cached relative path computations
    - Precomputed normalized paths
    - Optimized pattern loading
    - Fast path for common cases
    """

    def __init__(self, ctx: AppContext, config: Config, gitignore_path: Path) -> None:
        """
        Initialize the gitignore matcher for a single directory by loading patterns
        from the provided .gitignore file.

        Args:
            ctx (AppContext): The application context
            config (Config): The application configuration
            gitignore_path (Path): Path to the .gitignore file to load patterns from
        """

        # Bind app context and config with the object
        self.ctx = ctx
        self.config = config

        # Object attr
        self.enabled = config.gitignore
        self.gitignore_depth = config.gitignore_depth

        # Setup specs for gitignore
        self._specs: list[tuple[Path, pathspec.PathSpec]]
        
        # Cache for relative path computations: (path, root) -> relative_path
        self._rel_path_cache: dict[tuple[str, str], Optional[str]] = {}
        
        # Store root path for scope checking
        self.root_path: Optional[Path] = None
        
        self._load_spec_from_gitignore(gitignore_path)


    def excluded(self, item_path: Path) -> bool:
        """
        Optimized exclusion check with path caching.

        Args:
            item_path (Path): The path to check for exclusion

        Returns:
            bool: True if the path is ignored/excluded, otherwise False
        """
        if not self.enabled:
            return False

        # Resolve path once
        p = item_path.resolve(strict=False)
        is_dir = p.is_dir()
        
        for root, spec in self._specs:
            # Use cached relative path computation
            rel = self._get_relative_path_cached(p, root)
            
            if rel is None:
                continue

            # Check file match
            if spec.match_file(rel):
                return True
            
            # Check directory match (only if it's actually a directory)
            if is_dir and spec.match_file(rel + "/"):
                return True

        return False
    
    def _get_relative_path_cached(self, path: Path, root: Path) -> Optional[str]:
        """
        Get relative path with caching to avoid repeated computations.
        
        Args:
            path: The path to make relative
            root: The root to make it relative to
            
        Returns:
            Relative path as string in POSIX format, or None if not relative
        """
        # Use string representations as cache keys (faster than Path hashing)
        cache_key = (str(path), str(root))
        
        if cache_key in self._rel_path_cache:
            return self._rel_path_cache[cache_key]
        
        try:
            rel = path.relative_to(root).as_posix()
            self._rel_path_cache[cache_key] = rel
            return rel
        except ValueError:
            self._rel_path_cache[cache_key] = None
            return None


    def _load_from_roots(self, roots: Iterable[Path]) -> None:
        """
        Load and combine gitignore patterns from all .gitignore files under the given roots.

        Args:
            roots (Iterable[Path]): Root directories to scan for .gitignore files
        """
        # Clears the specs if already present
        self._specs = []
        self._rel_path_cache.clear()

        for root in self._norm_roots(roots):
            pats = self._collect_patterns(root)
            if pats:  # Only add if there are patterns
                self._specs.append((root, pathspec.PathSpec.from_lines("gitwildmatch", pats)))


    def _load_spec_from_gitignore(self, gitignore_path: Path) -> None:
        """
        Optimized gitignore pattern loading from a single file.

        Args:
            gitignore_path (Path): Path to the .gitignore file to load
        """
        self._specs = []
        self._rel_path_cache.clear()

        gi = Path(gitignore_path).resolve(strict=False)
        root = gi.parent
        self.root_path = root

        patterns = self._parse_gitignore_file(gi)
        
        if patterns:  # Only create spec if there are patterns
            self._specs.append((root, pathspec.PathSpec.from_lines("gitwildmatch", patterns)))


    def _parse_gitignore_file(self, gitignore_path: Path) -> list[str]:
        """
        Parse a gitignore file and return normalized patterns.
        
        Args:
            gitignore_path: Path to the .gitignore file
            
        Returns:
            List of normalized patterns
        """
        patterns: list[str] = []
        
        try:
            lines = gitignore_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            return patterns

        for line in lines:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue

            # Handle negation patterns
            neg = line.startswith("!")
            pat = line[1:] if neg else line
            
            # Normalize pattern (remove leading slash)
            pat = pat.lstrip("/")
            
            # Add pattern with negation prefix if needed
            patterns.append(("!" + pat) if neg else pat)

        return patterns


    def _norm_roots(self, roots: Iterable[Path]) -> list[Path]:
        """
        Normalize root paths into unique directory Paths.

        Args:
            roots (Iterable[Path]): Root paths to normalize

        Returns:
            list[Path]: A de-duplicated list of resolved directory roots
        """
        seen = set()
        out: list[Path] = []
        
        for r in roots:
            rr = Path(r).resolve(strict=False)
            rr = rr if rr.is_dir() else rr.parent
            
            # Use string representation for faster set membership check
            rr_str = str(rr)
            if rr_str not in seen:
                seen.add(rr_str)
                out.append(rr)
        
        return out
    

    def _within_depth(self, root: Path, dirpath: Path) -> bool:
        """
        Check whether a directory is within the configured gitignore traversal depth
        relative to the given root.

        Args:
            root (Path): The root directory used as the depth baseline
            dirpath (Path): The directory path to test

        Returns:
            bool: True if dirpath is within depth, otherwise False
        """
        if self.gitignore_depth is None:
            return True
        try:
            return len(dirpath.relative_to(root).parts) <= self.gitignore_depth
        except Exception:
            return False
        

    def _collect_patterns(self, root: Path) -> list[str]:
        """
        Collect gitignore patterns from all .gitignore files under the root, prefixing
        patterns by their relative directory to emulate nested .gitignore behavior.

        Args:
            root (Path): Root directory to scan

        Returns:
            list[str]: Combined list of patterns collected under the root
        """
        patterns: list[str] = []

        for d in self._walk_dirs(root):
            gi = d / ".gitignore"
            if not gi.is_file():
                continue

            rel_dir = d.relative_to(root).as_posix()
            prefix = "" if rel_dir == "." else rel_dir + "/"

            file_patterns = self._parse_gitignore_file(gi)
            
            # Add prefix to patterns if needed
            for pat in file_patterns:
                neg = pat.startswith("!")
                base_pat = pat[1:] if neg else pat
                prefixed_pat = prefix + base_pat.lstrip("/")
                patterns.append(("!" + prefixed_pat) if neg else prefixed_pat)

        return patterns
    

    def _walk_dirs(self, root: Path) -> Iterable[Path]:
        """
        Walk directories under the root using a stack-based traversal, respecting the
        configured depth and skipping symlinks.

        Args:
            root (Path): Root directory to traverse

        Returns:
            Iterable[Path]: Directories discovered during traversal, including root
        """
        stack = [root]
        visited = set()
        
        while stack:
            d = stack.pop()
            
            # Avoid revisiting directories
            d_str = str(d)
            if d_str in visited:
                continue
            visited.add(d_str)
            
            yield d

            if not self._within_depth(root, d):
                continue

            try:
                for c in d.iterdir():
                    if c.is_dir() and not c.is_symlink():
                        stack.append(c)
            except (PermissionError, OSError):
                continue
