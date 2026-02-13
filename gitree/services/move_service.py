# gitree/services/move_service.py

"""
Code file for housing MoveService class. Handles changing the terminal's working directory.
"""

# Default libs
import os
import sys
from pathlib import Path

# Deps from this project
from ..objects.app_context import AppContext
from ..objects.config import Config
from ..utilities.logging_utility import Logger


class MoveService:
    """
    Service to handle changing the terminal's working directory to the determined root directory.
    """

    @staticmethod
    def run(ctx: AppContext, config: Config, resolved_root: dict) -> None:
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
        root_dir = resolved_root.get('root_directory')
        
        if not root_dir:
            ctx.logger.log(Logger.WARNING, "No root directory found to move to")
            return

        root_path = Path(root_dir)
        
        if not root_path.exists() or not root_path.is_dir():
            ctx.logger.log(Logger.WARNING, f"Root directory does not exist or is not a directory: {root_path}")
            return

        try:
            # Change the working directory
            os.chdir(root_path)
            
            # Print the change for user feedback (only if not in silent mode)
            if not config.no_printing:
                print(f"Changed working directory to: {root_path}")
            
            ctx.logger.log(Logger.INFO, f"Successfully changed working directory to: {root_path}")
            
        except OSError as e:
            ctx.logger.log(Logger.ERROR, f"Failed to change directory to {root_path}: {e}")
            if not config.no_printing:
                print(f"Error: Failed to change directory to {root_path}: {e}", file=sys.stderr)