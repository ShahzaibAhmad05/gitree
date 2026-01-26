# gitree/services/items_selection/filter_applier.py

"""
Filter application logic for items selection.
"""

# Default libs
from pathlib import Path
from typing import List

# Deps from this project
from ...objects.app_context import AppContext
from ...objects.config import Config
from ...utilities.gitignore_utility import GitIgnoreMatcher
from .path_resolver import PathResolver


class FilterApplier:
    """
    Applies various filters (hidden, gitignore, include/exclude) to paths.
    
    Optimized for:
    - Fast filter checks with minimal redundant operations
    - Early exit on common cases
    - Batch checking when possible
    """
    
    def __init__(self, ctx: AppContext, config: Config, path_resolver: PathResolver):
        self.ctx = ctx
        self.config = config
        self.path_resolver = path_resolver
        
        # Preprocess file extensions for fast lookup
        self.file_extensions_set = None
        if self.config.file_extensions:
            # Use a set for O(1) lookups, normalize to lowercase
            self.file_extensions_set = {ext.lower().lstrip('.') for ext in self.config.file_extensions}
            self.ctx.logger.log(self.ctx.logger.DEBUG,
                               f"FilterApplier: Initialized with extensions: {self.file_extensions_set}")
    
    def should_include_item(self, 
                           item_path: Path,
                           curr_depth: int,
                           is_dir: bool,
                           gitignore_matcher: GitIgnoreMatcher,
                           exclude_paths: List[Path],
                           resolved_include_paths: List[Path],
                           dir_under_given_paths: bool) -> bool:
        """
        Determine if an item should be included based on all filters.
        
        Args:
            item_path: Path to check
            curr_depth: Current traversal depth
            is_dir: Whether the path is a directory
            gitignore_matcher: GitIgnore matcher instance
            exclude_paths: List of excluded paths
            resolved_include_paths: List of included paths
            dir_under_given_paths: Whether parent dir is in given paths
            
        Returns:
            True if item should be included, False otherwise
        """
        
        # Filter 1: Skip files if --no-files is used
        if not is_dir and self.config.no_files:
            return False
        
        # Filter 1.5: File extension filtering (OPTIMIZED - happens early)
        # Only check files, not directories
        if not is_dir and self.file_extensions_set:
            # Get file extension efficiently using string operations
            # This is faster than Path.suffix for hot paths
            name = item_path.name
            dot_idx = name.rfind('.')
            if dot_idx > 0:  # Ensure dot is not at the start (hidden files)
                file_ext = name[dot_idx + 1:].lower()
                if file_ext not in self.file_extensions_set:
                    return False
            else:
                # No extension, so not in allowed extensions
                return False
        
        # Filter 2: Handle paths not explicitly given
        # OPTIMIZATION: Skip this check if using file_extensions filtering
        # because we're scanning the whole tree and filtering by extension
        if not dir_under_given_paths and not self.file_extensions_set:
            # Skip files not in resolved paths
            if not is_dir and item_path not in resolved_include_paths:
                return False
            
            # Skip dirs with no included files under them
            # NOTE: This check is expensive but necessary for correctness
            if is_dir and not any(
                self.path_resolver.is_under(t, [item_path]) 
                for t in resolved_include_paths
            ):
                return False
        
        # Filter 3: Hidden items filter
        if (not self.config.hidden_items and 
            self.path_resolver.is_hidden(item_path) and 
            item_path not in resolved_include_paths):
            return False
        
        # Filter 4: Exclude paths filter (within depth)
        if (curr_depth <= self.config.exclude_depth and 
            self.path_resolver.is_under(item_path, exclude_paths)):
            return False
        
        # Filter 5: Gitignore filter (within depth)
        if (curr_depth <= self.config.gitignore_depth and 
            gitignore_matcher.excluded(item_path)):
            return False
        
        # Filter 6: Include paths filter
        # OPTIMIZATION: Skip this check if using file_extensions filtering
        # because the extension check already filtered files
        if not self.file_extensions_set:
            if not self.path_resolver.is_under(item_path, resolved_include_paths):
                return False
        
        return True
    
    def check_depth_limit(self, curr_depth: int) -> bool:
        """
        Check if current depth exceeds max depth.
        
        Args:
            curr_depth: Current traversal depth
            
        Returns:
            True if depth limit is exceeded, False otherwise
        """
        if self.config.no_max_depth:
            return False
        return curr_depth > self.config.max_depth - 1
    
    def check_item_limit(self, items_added: int) -> bool:
        """
        Check if item limit is reached.
        
        Args:
            items_added: Number of items added so far
            
        Returns:
            True if item limit is reached, False otherwise
        """
        if self.config.no_max_items:
            return False
        return items_added >= self.config.max_items
    
    def check_entry_limit(self, entries_count: int) -> bool:
        """
        Check if entry limit is reached.
        
        Args:
            entries_count: Number of entries processed so far
            
        Returns:
            True if entry limit is reached, False otherwise
        """
        if self.config.no_max_entries:
            return False
        return entries_count >= self.config.max_entries
