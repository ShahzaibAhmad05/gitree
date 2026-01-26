# gitree/utilities/gitignore_utility.py

"""
Code file for housing GitIgnoreMatcher with performance optimizations.
"""

# Default libs
from pathlib import Path
from typing import Optional

# Deps from this project
from ..objects.gitignore import GitIgnore
from ..objects.app_context import AppContext
from ..objects.config import Config


class GitIgnoreMatcher:
    """
    Optimized GitIgnore matcher with caching and scope-based matching.
    
    Performance improvements:
    - Path-based caching to avoid redundant pattern matching
    - Scope-based matching to only check relevant gitignores
    - Precomputed path strings to avoid repeated conversions
    """

    def __init__(self):
        # Store gitignores with their root paths for scope-based matching
        self.gitignores: list[tuple[Path, GitIgnore]] = []
        
        # Cache for path exclusion results: path -> is_excluded
        self._exclusion_cache: dict[str, bool] = {}
        
        # Cache size limit to prevent memory bloat
        self._max_cache_size: int = 10000
    
    def add_gitignore(self, gitignore: GitIgnore, root_path: Path):
        """
        Add a gitignore with its root path for scope-based matching.
        
        Args:
            gitignore: The GitIgnore object to add
            root_path: The root directory path where this gitignore applies
        """
        self.gitignores.append((root_path, gitignore))
        # Clear cache when new gitignore is added
        self._exclusion_cache.clear()
    
    def excluded(self, item_path: Path) -> bool:
        """
        Check if a path is excluded by any applicable gitignore, with caching.
        
        Args:
            item_path: Path to check for exclusion
            
        Returns:
            True if the path is excluded, False otherwise
        """
        # Use string representation for cache key (faster than Path hashing)
        path_key = str(item_path)
        
        # Check cache first
        if path_key in self._exclusion_cache:
            return self._exclusion_cache[path_key]
        
        # Only check gitignores that are ancestors of this path (scope-based matching)
        result = False
        for root_path, gitignore in self.gitignores:
            # Skip gitignores that don't apply to this path's scope
            if not self._is_path_in_scope(item_path, root_path):
                continue
                
            if gitignore.excluded(item_path):
                result = True
                break
        
        # Cache the result (with size limit)
        if len(self._exclusion_cache) < self._max_cache_size:
            self._exclusion_cache[path_key] = result
        else:
            # Clear cache when it gets too large
            self._exclusion_cache.clear()
            self._exclusion_cache[path_key] = result
        
        return result
    
    def _is_path_in_scope(self, item_path: Path, gitignore_root: Path) -> bool:
        """
        Check if a path is within the scope of a gitignore root.
        
        Args:
            item_path: The path to check
            gitignore_root: The root path of the gitignore
            
        Returns:
            True if item_path is under gitignore_root
        """
        try:
            item_path.relative_to(gitignore_root)
            return True
        except ValueError:
            return False
    
    def clear_cache(self):
        """Clear the exclusion cache. Useful when switching directories."""
        self._exclusion_cache.clear()
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics for debugging/monitoring."""
        return {
            'cache_size': len(self._exclusion_cache),
            'gitignore_count': len(self.gitignores)
        }
