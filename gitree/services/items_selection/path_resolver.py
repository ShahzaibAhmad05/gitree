# gitree/services/items_selection/path_resolver.py

"""
Path resolution and glob pattern handling with caching.
"""

# Default libs
import os
import glob
from pathlib import Path
from typing import List

# Deps from this project
from ...objects.app_context import AppContext
from ...objects.config import Config
from ...utilities.logging_utility import Logger
from ...utilities.functions_utility import error_and_exit


class PathResolver:
    """
    Optimized path resolver with caching and efficient glob handling.
    
    Responsible for:
    - Resolving CLI path arguments
    - Handling glob patterns
    - Computing common parent paths
    - Path validation
    """
    
    def __init__(self, ctx: AppContext, config: Config):
        self.ctx = ctx
        self.config = config
        self.base_path = Path(os.getcwd())
        
        # Cache for resolved paths
        self._resolved_cache: dict[str, Path] = {}
        
        # Cache for glob pattern results
        self._glob_cache: dict[str, List[Path]] = {}
    
    def resolve_paths(self, path_strings: list[str]) -> list[Path]:
        """
        Resolve a list of path strings to Path objects, handling globs.
        
        Args:
            path_strings: List of path strings (may include glob patterns)
            
        Returns:
            List of resolved Path objects with common parent appended at end
        """
        if not path_strings:
            return [self.base_path]
        
        calculated_paths: list[Path] = []
        
        for path_str in path_strings:
            if self._is_glob(path_str):
                # Handle glob patterns
                paths = self._resolve_glob(path_str)
                calculated_paths.extend(paths)
            else:
                # Handle regular paths
                path = self._resolve_single_path(path_str)
                calculated_paths.append(path)
        
        # Add common parent at the end
        if calculated_paths:
            try:
                common_parent = Path(os.path.commonpath(calculated_paths))
                calculated_paths.append(common_parent)
            except ValueError as e:
                print(e)
                exit(1)
        
        return calculated_paths
    
    def _resolve_single_path(self, path_str: str) -> Path:
        """
        Resolve a single path string to a Path object with caching.
        
        Args:
            path_str: Path string to resolve
            
        Returns:
            Resolved Path object
        """
        # Check cache first
        if path_str in self._resolved_cache:
            return self._resolved_cache[path_str]
        
        path = Path(path_str)
        
        # Validate path exists
        if not path.exists():
            error_and_exit(f"Given value for path does not exist: {path}")
        
        resolved_path = (self.base_path / path).resolve(strict=False)
        
        # Cache the result
        self._resolved_cache[path_str] = resolved_path
        
        return resolved_path
    
    def _resolve_glob(self, pattern: str) -> list[Path]:
        """
        Resolve a glob pattern to matching paths with caching.
        
        Args:
            pattern: Glob pattern string
            
        Returns:
            List of matching Path objects
        """
        # Check cache first
        if pattern in self._glob_cache:
            return self._glob_cache[pattern]
        
        # Resolve glob pattern
        matched_paths = glob.glob(pattern, recursive=True, include_hidden=True)
        
        if not matched_paths:
            self.ctx.logger.log(Logger.WARNING, 
                f"No matches found for glob pattern '{pattern}'")
            return []
        
        # Convert to Path objects
        result = [Path(p).resolve(strict=False) for p in matched_paths]
        
        # Cache the result
        self._glob_cache[pattern] = result
        
        return result
    
    @staticmethod
    def _is_glob(path_str: str) -> bool:
        """Check if a string contains glob pattern characters."""
        return any(c in path_str for c in "*?[")
    
    @staticmethod
    def is_under(path: Path, parents: list[Path]) -> bool:
        """
        Check if a path is under any of the given parent paths.
        
        Args:
            path: Path to check
            parents: List of potential parent paths
            
        Returns:
            True if path is under any parent
        """
        return any(path == p or path.is_relative_to(p) for p in parents)
    
    @staticmethod
    def is_hidden(path: Path) -> bool:
        """Check if a path represents a hidden file/directory."""
        return path.name.startswith(".")
