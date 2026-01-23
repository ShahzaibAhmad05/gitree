# gitree/services/copy_service.py

"""
Code file for housing CopyService Class. 

Static methods; copies exported output to clipboard
"""

# Dependencies
import pyperclip

# Deps from this project
from ..objects.app_context import AppContext
from ..objects.config import Config
from ..services.export_service import ExportService
from ..utilities.logging_utility import Logger


class FlushService:
    """
    This class contains methods to help flush the output buffers
    in AppContext based on configuration.
    """
    
    @staticmethod
    def run(ctx: AppContext, config: Config) -> None:
        """
        Flush the output buffers based on configuration.

        Args:
            ctx (AppContext): The application context
            config (Config): The application configuration
        """

        if not config.no_printing and not ctx.output_buffer.empty(): print()

        # print the export only if not in no_printing and buffer not empty
        if not config.no_printing and not ctx.output_buffer.empty():
            ctx.output_buffer.flush()

        # print the log if verbose mode
        if config.verbose:
            if not config.no_printing and not ctx.output_buffer.empty():
                print()
            print("LOG:")
            ctx.logger.flush()

        if not config.no_printing and not ctx.output_buffer.empty(): print()
