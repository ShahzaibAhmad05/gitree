# gitree/services/items_selection/items_selection_service.py

"""
Refactored ItemsSelectionService - main coordinator for path resolution and traversal.
"""

# Default libs
from typing import Any
import time, os, sys
from pathlib import Path

# Deps from this project
from ...objects.app_context import AppContext
from ...objects.config import Config
from ...utilities.logging_utility import Logger
from ...utilities.gitignore_utility import GitIgnoreMatcher
from .path_resolver import PathResolver
from .filter_applier import FilterApplier
from .directory_traverser import DirectoryTraverser


class ItemsSelectionService:
    """
    Refactored static class for resolving args and forming an items dict.
    
    This is now a coordinator that delegates to specialized components:
    - PathResolver: Handles path resolution and glob patterns
    - FilterApplier: Applies include/exclude/hidden/gitignore filters
    - DirectoryTraverser: Performs optimized iterative directory traversal
    
    Performance improvements:
    - Modular architecture for better maintainability
    - Iterative traversal instead of deep recursion
    - Comprehensive caching at multiple levels
    - Optimized gitignore matching with scope awareness
    """

    @staticmethod
    def run(ctx: AppContext, config: Config, start_time: float) -> dict[str, Any]:
        """
        Resolves the items to include in the output using the config object.

        Args:
            ctx: Application context
            config: Configuration object
            start_time: Relative time value to log performance of the service

        Returns:
            dict: A dict of the resolved items
        """

        ctx.logger.log(Logger.DEBUG, 
            f"Entered ItemsSelectionService at: {round((time.time()-start_time)*1000, 2)} ms")

        # Initialize components
        path_resolver = PathResolver(ctx, config)
        filter_applier = FilterApplier(ctx, config, path_resolver)
        directory_traverser = DirectoryTraverser(ctx, config, path_resolver, filter_applier)

        # Resolve include paths (includes root path appended at end)
        resolved_include_paths = path_resolver.resolve_paths(
            config.paths + config.include)
        ctx.logger.log(Logger.DEBUG, 
            f"Selected includes at: {round((time.time()-start_time)*1000, 2)} ms")

        # Print root path
        ctx.output_buffer.write(f"    Root: {resolved_include_paths[-1]}\n")

        # Resolve exclude paths
        resolved_exclude_paths = path_resolver.resolve_paths(config.exclude)
        ctx.logger.log(Logger.DEBUG, 
            f"Selected excludes at: {round((time.time()-start_time)*1000, 2)} ms")

        # Safety check
        if not resolved_include_paths:
            print("Error: no included paths were found matching given args")
            exit(1)

        # Initialize gitignore matcher
        gitignore_matcher = GitIgnoreMatcher()

        # Perform iterative traversal
        resolved_items = directory_traverser.traverse(
            root_dir=resolved_include_paths[-1],
            resolved_include_paths=resolved_include_paths,
            exclude_paths=resolved_exclude_paths[:-1],
            gitignore_matcher=gitignore_matcher,
            start_time=start_time
        )
        
        # Add root directory to the resolved items for potential use by MoveService
        resolved_items['root_directory'] = str(resolved_include_paths[-1])

        ctx.logger.log(Logger.DEBUG, 
            f"Exited ItemsSelectionService at: {round((time.time()-start_time)*1000, 2)} ms")

        return resolved_items

    @staticmethod
    def move_service(ctx: AppContext, config: Config, resolved_root: dict) -> None:
        """
        Changes the terminal's working directory to the root directory determined by gitree.

        Args:
            ctx: Application context
            config: Configuration object
            resolved_root: Dictionary containing resolved items with root directory info
        """
        if not config.move:
            return

        # Get the root directory from resolved_root
        root_dir = resolved_root.get("root_directory")

        if not root_dir:
            ctx.logger.log(Logger.WARNING, "No root directory found to move to")
            return

        root_path = Path(root_dir)

        if not root_path.exists() or not root_path.is_dir():
            ctx.logger.log(
                Logger.WARNING,
                f"Root directory does not exist or is not a directory: {root_path}",
            )
            return

        try:
            # Change the working directory
            os.chdir(root_path)

            # Print the change for user feedback (only if not in silent mode)
            if not config.no_printing:
                print(f"Changed working directory to: {root_path}")

            ctx.logger.log(
                Logger.INFO, f"Successfully changed working directory to: {root_path}"
            )

        except OSError as e:
            ctx.logger.log(
                Logger.ERROR, f"Failed to change directory to {root_path}: {e}"
            )
            if not config.no_printing:
                print(
                    f"Error: Failed to change directory to {root_path}: {e}",
                    file=sys.stderr,
                )
