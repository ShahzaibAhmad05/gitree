# gitree/services/parsing/fixing_service.py

"""
Service for correcting and fixing CLI arguments.
Handles output path corrections and argument validation.
"""

# Default libs
import argparse
from pathlib import Path

# Imports from this project
from ...objects.app_context import AppContext
from ...objects.config import Config


class FixingService:
    """
    Service responsible for correcting and validating parsed arguments.
    Handles output path corrections and fixing contradicting arguments.
    """

    @staticmethod
    def correct_args(ctx: AppContext, args: argparse.Namespace) -> argparse.Namespace:
        """
        Correct and validate CLI arguments in place.
        
        Args:
            ctx: Application context
            args: Parsed arguments namespace
            
        Returns:
            Corrected arguments namespace
        """
        
        # Correcting export path
        if getattr(args, "export", None) is not None:
            args.export = FixingService._fix_output_path(
                ctx, args.export,
                default_extensions={"tree": ".txt", "json": ".json", "md": ".md"},
                format_str=args.format)
            
        # Correcting zip path
        if getattr(args, "zip", None):
            args.zip = FixingService._fix_output_path(ctx, args.zip, default_extension=".zip")

        ctx.logger.log(ctx.logger.DEBUG, f"Corrected arguments: {args}")
        return args
    

    @staticmethod
    def _fix_output_path(
        ctx: AppContext, 
        output_path: str, 
        default_extension: str = "",
        default_extensions: dict | None = None, 
        format_str: str = ""
    ) -> str:
        """
        Ensure the output path has a correct extension.
        
        Args:
            ctx: Application context
            output_path: Path to fix
            default_extension: Single default extension to use
            default_extensions: Dict of format -> extension mappings
            format_str: Format string to look up in default_extensions
            
        Returns:
            Fixed output path as string
        """
        default_extensions = default_extensions or {}
        path = Path(output_path)

        if path.suffix == "":
            if default_extension:
                path = path.with_suffix(default_extension)
            elif format_str and format_str in default_extensions:
                path = path.with_suffix(default_extensions[format_str])

        return str(path)


    @staticmethod
    def fix_contradicting_args(ctx: AppContext, config: Config) -> Config:
        """
        Prevents unexpected behaviour of the tool if contradictory options are used.
        
        Args:
            ctx: Application context
            config: Configuration object to fix
            
        Returns:
            Fixed configuration object
        """
        # Remove intersecting values for include and exclude patterns
        include_set = set(config.include)
        exclude_set = set(config.exclude)
        common_values = include_set & exclude_set

        if common_values:
            ctx.logger.log(
                ctx.logger.WARNING,
                "--include and --exclude patterns have overlapping values. "
                "These values will be removed from both lists"
            )
            config.include = list(include_set - common_values)
            config.exclude = list(exclude_set - common_values)

        return config
