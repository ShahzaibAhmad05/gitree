# gitree/services/parsing/parsing_service.py

"""
Code file for housing ParsingService class. Handles argument parsing setup.
"""

# Default libs
import argparse
import sys
from pathlib import Path

# Imports from this project
from ...utilities.functions_utility import max_items_int, max_entries_int
from ...objects.config import Config
from ...objects.app_context import AppContext
from .rich_help_formatter import RichHelpFormatter
from .fixing_service import FixingService
from .semantic_processing_service import SemanticProcessingService


class CustomArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser that shows concise error messages instead of full help."""
    
    def error(self, message):
        """Override error method to show only the error message."""
        self.exit(2, f"Error: {message}\nUse 'gt --help' for more information.\n")


class ParsingService:
    """
    CLI parsing service for gitree tool. 

    Handles argument parsing setup and delegates to specialized services
    for semantic processing and argument fixing.
    """

    @staticmethod
    def run(ctx: AppContext) -> Config:
        """
        Public function to parse command-line arguments for the gitree tool.

        Returns:
            Config: Configuration object to be used in-place of args
        """
        
        # Handle help flag early before argparse processes it
        if '-h' in sys.argv or '--help' in sys.argv:
            formatter = RichHelpFormatter('gt')
            formatter.format_help()

        ap = CustomArgumentParser(
            prog='gt',
            description="Print a directory tree (does not respect .gitignore by default).",
            formatter_class=RichHelpFormatter,
            add_help=False  # Disable default help to use our custom one
        )

        ParsingService._add_positional_args(ctx, ap)
        ParsingService._add_general_options(ctx, ap)
        ParsingService._add_io_flags(ctx, ap)
        ParsingService._add_listing_flags(ctx, ap)
        ParsingService._add_listing_control_flags(ctx, ap)
        ParsingService._add_semantic_flags(ctx, ap)

        args = ap.parse_args()
        ctx.logger.log(ctx.logger.DEBUG, f"Parsed arguments: {args}")

        # Process semantic flags first (e.g., --full, --no-limit, --only-types)
        args = SemanticProcessingService.process_semantic_flags(ctx, args)

        # Then correct the arguments (e.g., fix output paths)
        args = FixingService.correct_args(ctx, args)

        # Prepare the config object to return from this function
        config = Config(ctx, args)
        config.no_printing = config.copy or config.export or config.zip 
        if not config.no_color:
            config.no_color = config.copy or config.export

        # Fix any contradicting arguments
        return FixingService.fix_contradicting_args(ctx, config)

    @staticmethod
    def _add_positional_args(ctx: AppContext, ap: argparse.ArgumentParser):
        ap.add_argument(
            "paths",
            nargs="*",
            default=["."],
            help="Root paths (supports multiple directories and file patterns), "
                "defaults to the current working directory",
        )


    @staticmethod
    def _add_general_options(ctx: AppContext, ap: argparse.ArgumentParser):
        general = ap.add_argument_group("GENERAL OPTIONS")
        
        general.add_argument("-h", "--help", action="store_true",
            default=argparse.SUPPRESS,
            help="Show this help message and exit")
        
        general.add_argument("-v", "--version", action="store_true",
            default=argparse.SUPPRESS,
            help="Display the version number of the tool")

        general.add_argument("--config-user", action="store_true", 
            default=argparse.SUPPRESS, 
            help="Create a default config.json file in the current directory"
                " and open that file in the default editor")
        
        general.add_argument("--no-config", action="store_true", 
            default=argparse.SUPPRESS, 
            help="Ignore both user-level and global-level config.json and use"
                " default and cli values for configuration")
        
        general.add_argument("--verbose", "--log", action="store_true", 
            default=argparse.SUPPRESS, 
            help="Enable logger output to the console. Enabling this prints a log"
            " after the full workflow run. Helpful for debugging.")


    @staticmethod
    def _add_io_flags(ctx: AppContext, ap: argparse.ArgumentParser):
        io = ap.add_argument_group("output & export options")

        io.add_argument("-z", "--zip", 
            default=argparse.SUPPRESS, 
            help="Create a zip archive of the given directory (respects gitignore if -g is used).")
        
        io.add_argument("-x", "--export", 
            default=argparse.SUPPRESS, 
            help="Save project structure along with it's contents to a file"
                " with the format specified using --format")


    @staticmethod
    def _add_listing_flags(ctx: AppContext, ap: argparse.ArgumentParser):
        listing = ap.add_argument_group("listing options")

        listing.add_argument("--format", choices=["tree", "json", "md"], 
            default="tree", help="Format output only")

        listing.add_argument("--max-items", type=max_items_int, 
            default=argparse.SUPPRESS, 
            help="Limit items to be selected per directory")
        
        listing.add_argument("--max-entries", type=max_entries_int, 
            default=argparse.SUPPRESS, 
            help="Limit entries (files/dirs) to be selected for the overall output")
        
        listing.add_argument("--max-depth", type=int, 
            default=argparse.SUPPRESS, 
            help="Maximum depth to traverse when selecting files")
        
        listing.add_argument("--gitignore-depth", type=int, 
            default=argparse.SUPPRESS, 
            help="Limit depth to look for during .gitignore processing")
        
        listing.add_argument("-a", "--hidden-items", "--all",
            action="store_true",
            default=argparse.SUPPRESS,
            help="Show hidden files and directories")

        listing.add_argument("--exclude", nargs="*", 
            default=argparse.SUPPRESS, help="Patterns of files to specifically exclude")
        
        listing.add_argument("--exclude-depth", type=int, 
            default=argparse.SUPPRESS, help="Limit depth for exclude patterns")
        
        listing.add_argument("--include", nargs="*", 
            default=argparse.SUPPRESS, help="Patterns of files to specifically include")
        
        listing.add_argument("--include-file-types", "--include-file-type", nargs="*", 
            default=argparse.SUPPRESS, dest="include_file_types", 
            help="Include files of certain types")
        
        listing.add_argument("--files-first", action="store_true", 
            default=argparse.SUPPRESS, help="Print files before directories")
        
        listing.add_argument("--no-color", action="store_true", 
            default=argparse.SUPPRESS, help="Disable colored output")
        
        listing.add_argument("--no-contents", action="store_true", 
            default=argparse.SUPPRESS, help="Don't include file contents in export/copy")
        
        listing.add_argument("--no-contents-for", nargs="+",
            default=argparse.SUPPRESS, metavar="PATH",
            help="Exclude contents for specific files for export/copy")
        
        listing.add_argument("--max-file-size", type=float,
            default=argparse.SUPPRESS, metavar="MB", dest="max_file_size",
            help="Maximum file size in MB to include in exports (default: 1.0)")
        
        listing.add_argument("--override-files", action="store_true",
            default=argparse.SUPPRESS, help="Override existing files") 


    @staticmethod
    def _add_listing_control_flags(ctx: AppContext, ap: argparse.ArgumentParser):
        listing_control = ap.add_argument_group("listing override options")

        listing_control.add_argument("--no-max-entries", action="store_true", 
            default=argparse.SUPPRESS, help="Disable --max-entries limit")
        
        listing_control.add_argument("--no-max-items", action="store_true", 
            default=argparse.SUPPRESS, help="Disable --max-items limit")
        
        listing_control.add_argument("--no-max-depth", action="store_true", 
            default=argparse.SUPPRESS, help="Disable --max-depth limit (risky)")
        
        listing_control.add_argument("-g", "--gitignore", action="store_true", 
            default=argparse.SUPPRESS, help="Enable .gitignore rules (respects .gitignore files)")
        
        listing_control.add_argument("--no-files", "--only-dirs", action="store_true", 
            default=argparse.SUPPRESS, help="Hide files (show only directories)")


    @staticmethod
    def _add_semantic_flags(ctx: AppContext, ap: argparse.ArgumentParser):
        """
        Add semantic flags that provide quick, intuitive shortcuts for common operations.
        """
        semantic = ap.add_argument_group("SEMANTIC FLAGS (QUICK ACTIONS)")

        semantic.add_argument("-f", "--full", action="store_true",
            default=argparse.SUPPRESS,
            help="Shortcut for --max-depth 5 - show full directory tree up to 5 levels deep")

        semantic.add_argument("-n", "--no-limit", action="store_true",
            default=argparse.SUPPRESS,
            help="Shortcut for --no-max-depth and --no-max-entries")
        
        semantic.add_argument("-e", "--emoji", action="store_true", 
            default=argparse.SUPPRESS, 
            help="Show emojis in the output for better visual clarity")
        
        semantic.add_argument("-i", "--interactive", action="store_true", 
            default=argparse.SUPPRESS, 
            help="Use interactive mode for manual file selection after automatic filtering")
        
        semantic.add_argument("-c", "--copy", action="store_true", 
            default=argparse.SUPPRESS, 
            help="Copy file contents and project structure to clipboard (great for LLM prompts)")
        
        semantic.add_argument(
            "-t", "--types", "--only-types",
            nargs="+",
            metavar="EXT",
            dest="only_types",
            default=argparse.SUPPRESS,
            help="Include only specific code extensions (e.g., -t py cpp tsx)"
        )