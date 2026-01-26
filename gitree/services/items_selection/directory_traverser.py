# gitree/services/items_selection/directory_traverser.py

"""
Optimized iterative directory traversal with stack-based approach.
"""

# Default libs
from pathlib import Path
from typing import Any, Dict, List
import time

# Deps from this project
from ...objects.app_context import AppContext
from ...objects.config import Config
from ...objects.gitignore import GitIgnore
from ...utilities.gitignore_utility import GitIgnoreMatcher
from ...utilities.logging_utility import Logger
from .filter_applier import FilterApplier
from .path_resolver import PathResolver
from .performance_cache import PerformanceCache


class DirectoryTraverser:
    """
    Optimized directory traversal using iterative stack-based approach.
    
    Performance improvements over recursion:
    - No function call overhead
    - Better memory usage
    - Explicit state management
    - Early termination support
    - Batch processing capabilities
    - Integrated performance caching
    """
    
    def __init__(self, ctx: AppContext, config: Config, 
                 path_resolver: PathResolver, filter_applier: FilterApplier):
        self.ctx = ctx
        self.config = config
        self.path_resolver = path_resolver
        self.filter_applier = filter_applier
        self.perf_cache = PerformanceCache(max_cache_size=50000)

        # gitignore tip flag
        self.gitignore_tip_added = False
        
    
    def traverse(self,
                root_dir: Path,
                resolved_include_paths: List[Path],
                exclude_paths: List[Path],
                gitignore_matcher: GitIgnoreMatcher,
                start_time: float) -> Dict[str, Any]:
        """
        Traverse directory tree iteratively using a stack-based approach.
        
        Args:
            root_dir: Root directory to start traversal from
            resolved_include_paths: Paths to include
            exclude_paths: Paths to exclude
            gitignore_matcher: GitIgnore matcher instance
            start_time: Start time for performance logging
            
        Returns:
            Dictionary representing the directory tree structure
        """
        
        # Global counters
        total_entries = 0
        truncated_entries = False
        
        # Stack item: (dir_path, depth, parent_result_dict)
        # We use a stack to simulate recursion iteratively
        stack: List[tuple[Path, int, Dict[str, Any]]] = []
        
        # Initialize root result
        root_result = {
            "self": root_dir,
            "remaining_items": 0,
            "children": [],
            "truncated_entries": False
        }
        
        # Start with root directory
        stack.append((root_dir, 0, root_result))
        
        # Track processed directories to avoid duplicate processing
        processed: set[str] = set()
        
        while stack:
            curr_dir, curr_depth, result_dict = stack.pop()
            
            # Skip if already processed (can happen with certain path structures)
            dir_key = str(curr_dir)
            if dir_key in processed:
                continue
            processed.add(dir_key)
            
            self.ctx.logger.log(Logger.DEBUG, 
                f"Processing {curr_dir.name} at: {round((time.time()-start_time)*1000, 2)} ms")
            
            # Check depth limit
            if self.filter_applier.check_depth_limit(curr_depth):
                continue
            
            # Determine if directory is under given paths
            dir_under_given_paths = self._is_dir_under_given_paths(curr_dir)
            
            # Get sorted children (files first, then alphabetically)
            # OPTIMIZATION: Avoid lambda overhead, use list comprehension + sort
            try:
                children = list(curr_dir.iterdir())
                # Sort in place: files first (is_dir=False sorts before True), then by name
                children.sort(key=lambda p: (self.perf_cache.is_dir_cached(p), p.name.lower()))
            except (PermissionError, OSError):
                continue
            
            # Check for .gitignore in current directory
            gitignore_path = curr_dir / ".gitignore"
            if (curr_depth <= self.config.gitignore_depth and 
                self.perf_cache.exists_cached(gitignore_path)):
                # Create a new GitIgnore and add to matcher
                new_gitignore = GitIgnore(self.ctx, self.config, gitignore_path)
                gitignore_matcher.add_gitignore(new_gitignore, curr_dir)

                # Add tip if gitignores found but not used
                if not self.config.gitignore and not self.gitignore_tip_added: 
                    self.ctx.tips_buffer.write(
                        "gitignore files were found, use '-g' to apply .gitignore rules")
                    self.gitignore_tip_added = True
            
            items_added = 0
            
            # OPTIMIZATION: When using file_extensions filter, we can batch-filter
            # all non-matching files before detailed checks
            if self.config.file_extensions:
                file_extensions_set = self.filter_applier.file_extensions_set
                filtered_children = []
                for item_path in children:
                    is_dir = self.perf_cache.is_dir_cached(item_path)
                    if is_dir:
                        # Always include directories for traversal
                        filtered_children.append((item_path, is_dir))
                    else:
                        # Check extension quickly
                        name = item_path.name
                        dot_idx = name.rfind('.')
                        if dot_idx > 0:
                            file_ext = name[dot_idx + 1:].lower()
                            if file_ext in file_extensions_set:
                                filtered_children.append((item_path, is_dir))
                children = filtered_children
            else:
                # Add is_dir flag to avoid recalculation
                children = [(p, self.perf_cache.is_dir_cached(p)) for p in children]
            
            # Process children
            for item_path, is_dir in children:
                # Check entry limit (global)
                if self.filter_applier.check_entry_limit(total_entries):
                    truncated_entries = True
                    break
                
                # Check item limit (per directory)
                if self.filter_applier.check_item_limit(items_added):
                    result_dict["remaining_items"] = len(children) - items_added
                    break
                
                # is_dir already computed above, no need to recalculate
                
                # Apply all filters
                if not self.filter_applier.should_include_item(
                    item_path=item_path,
                    curr_depth=curr_depth,
                    is_dir=is_dir,
                    gitignore_matcher=gitignore_matcher,
                    exclude_paths=exclude_paths,
                    resolved_include_paths=resolved_include_paths,
                    dir_under_given_paths=dir_under_given_paths
                ):
                    continue
                
                # Item passed all filters
                items_added += 1
                total_entries += 1
                
                if is_dir:
                    # Create result dict for subdirectory
                    subdir_result = {
                        "self": item_path,
                        "remaining_items": 0,
                        "children": []
                    }
                    result_dict["children"].append(subdir_result)
                    
                    # Add to stack for processing (with incremented depth)
                    stack.append((item_path, curr_depth + 1, subdir_result))
                else:
                    # Add file directly
                    result_dict["children"].append(item_path)
        
        # Set truncation flag on root
        root_result["truncated_entries"] = truncated_entries
        
        return root_result
    
    def _is_dir_under_given_paths(self, dir_path: Path) -> bool:
        """
        Check if directory path was explicitly given by user.
        
        Args:
            dir_path: Directory path to check
            
        Returns:
            True if path was given by user
        """
        given_paths: List[Path] = []
        
        for path_str in self.config.paths:
            if not self.path_resolver._is_glob(path_str):
                given_paths.append(Path(path_str).resolve(strict=False))
        
        return self.path_resolver.is_under(dir_path, given_paths)
