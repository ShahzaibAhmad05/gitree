# gitree/services/items_selection/performance_cache.py

"""
Centralized performance caching for items selection operations.
"""

# Default libs
from pathlib import Path
from typing import Optional, Set
from functools import lru_cache


class PerformanceCache:
    """
    Centralized cache for performance-critical operations.
    
    This class provides various caching strategies to avoid redundant:
    - Path operations (is_dir, exists, stat)
    - String conversions
    - Path relationship checks
    """
    
    def __init__(self, max_cache_size: int = 50000):
        self.max_cache_size = max_cache_size
        
        # Cache for is_dir() checks: path_str -> bool
        self._is_dir_cache: dict[str, bool] = {}
        
        # Cache for path.exists() checks: path_str -> bool
        self._exists_cache: dict[str, bool] = {}
        
        # Cache for resolved paths: path_str -> Path
        self._resolved_path_cache: dict[str, Path] = {}
        
        # Cache for parent-child relationships: (child_str, parent_str) -> bool
        self._is_under_cache: dict[tuple[str, str], bool] = {}
        
        # Set of known directories for fast lookup
        self._known_dirs: Set[str] = set()
        
        # Set of known files for fast lookup
        self._known_files: Set[str] = set()
    
    def is_dir_cached(self, path: Path) -> bool:
        """
        Cached version of path.is_dir().
        
        Args:
            path: Path to check
            
        Returns:
            True if path is a directory
        """
        path_str = str(path)
        
        # Check known sets first (fastest)
        if path_str in self._known_dirs:
            return True
        if path_str in self._known_files:
            return False
        
        # Check cache
        if path_str in self._is_dir_cache:
            return self._is_dir_cache[path_str]
        
        # Compute and cache
        result = path.is_dir()
        self._cache_with_limit(self._is_dir_cache, path_str, result)
        
        # Add to known sets
        if result:
            self._known_dirs.add(path_str)
        else:
            self._known_files.add(path_str)
        
        return result
    
    def exists_cached(self, path: Path) -> bool:
        """
        Cached version of path.exists().
        
        Args:
            path: Path to check
            
        Returns:
            True if path exists
        """
        path_str = str(path)
        
        if path_str in self._exists_cache:
            return self._exists_cache[path_str]
        
        result = path.exists()
        self._cache_with_limit(self._exists_cache, path_str, result)
        
        return result
    
    def resolve_cached(self, path: Path) -> Path:
        """
        Cached version of path.resolve(strict=False).
        
        Args:
            path: Path to resolve
            
        Returns:
            Resolved path
        """
        path_str = str(path)
        
        if path_str in self._resolved_path_cache:
            return self._resolved_path_cache[path_str]
        
        result = path.resolve(strict=False)
        self._cache_with_limit(self._resolved_path_cache, path_str, result)
        
        return result
    
    def is_under_cached(self, child: Path, parent: Path) -> bool:
        """
        Cached check if child is under parent directory.
        
        Args:
            child: Child path to check
            parent: Parent path to check against
            
        Returns:
            True if child is under parent
        """
        cache_key = (str(child), str(parent))
        
        if cache_key in self._is_under_cache:
            return self._is_under_cache[cache_key]
        
        # Check if paths are equal or child is relative to parent
        try:
            result = (child == parent) or (child.is_relative_to(parent))
        except (ValueError, AttributeError):
            result = False
        
        # Cache with limit
        if len(self._is_under_cache) < self.max_cache_size:
            self._is_under_cache[cache_key] = result
        else:
            # Clear a portion of cache
            self._is_under_cache.clear()
            self._is_under_cache[cache_key] = result
        
        return result
    
    def _cache_with_limit(self, cache: dict, key, value):
        """
        Add to cache with size limit management.
        
        Args:
            cache: The cache dictionary to update
            key: Cache key
            value: Cache value
        """
        if len(cache) < self.max_cache_size:
            cache[key] = value
        else:
            # Clear cache when limit reached
            cache.clear()
            cache[key] = value
    
    def get_stats(self) -> dict:
        """
        Get cache statistics for debugging.
        
        Returns:
            Dictionary with cache sizes
        """
        return {
            'is_dir_cache_size': len(self._is_dir_cache),
            'exists_cache_size': len(self._exists_cache),
            'resolved_path_cache_size': len(self._resolved_path_cache),
            'is_under_cache_size': len(self._is_under_cache),
            'known_dirs_count': len(self._known_dirs),
            'known_files_count': len(self._known_files)
        }
    
    def clear_all(self):
        """Clear all caches."""
        self._is_dir_cache.clear()
        self._exists_cache.clear()
        self._resolved_path_cache.clear()
        self._is_under_cache.clear()
        self._known_dirs.clear()
        self._known_files.clear()
