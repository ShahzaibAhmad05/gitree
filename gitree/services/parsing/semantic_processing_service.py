# gitree/services/parsing/semantic_processing_service.py

"""
Service for processing semantic flags into concrete argument values.
Handles interpretation of convenient semantic flags like --full, --no-limit, --only-types.
"""

# Default libs
import argparse

# Imports from this project
from ...objects.app_context import AppContext


class SemanticProcessingService:
    """
    Service responsible for processing semantic flags into other flags.
    Semantic flags are convenience shortcuts that set multiple other flags.
    """

    @staticmethod
    def process_semantic_flags(ctx: AppContext, args: argparse.Namespace) -> argparse.Namespace:
        """
        Process semantic flags and convert them into concrete argument values.
        
        Args:
            ctx: Application context
            args: Parsed arguments namespace
            
        Returns:
            Arguments with semantic flags processed
        """

        # Set dependent semantics: uses other flags to set new semantics
        # Simulation of smart behaviour
        SemanticProcessingService._set_dependent_semantics(ctx, args)
        

        # Implementation for --no-limit flag
        if getattr(args, "no_limit", False):
            args.no_max_entries = True
            args.no_max_items = True
            args.no_max_depth = True
            ctx.logger.log(ctx.logger.DEBUG, 
                          "--no-limit: Setting no_max_entries=True and no_max_items=True")
            
            del args.no_limit


        # Implementation for --full flag
        if getattr(args, "full", False):
            args.max_depth = 5
            ctx.logger.log(ctx.logger.DEBUG, "--full: Setting max_depth=5")
            del args.full


        # Implementation for --only-types flag
        if getattr(args, "only_types", None):
            args.paths = []
            exts = []

            for e in args.only_types:
                e = e.lower().lstrip(".")
                if e:
                    exts.append(e)

            patterns = [f"**/*.{e}" for e in exts]

            # merge with existing includes (don't overwrite)
            if getattr(args, "include", None) is not None:
                args.include = list(dict.fromkeys(args.include + patterns))
            else:
                args.include = patterns
                
            ctx.logger.log(ctx.logger.DEBUG, 
                          f"--only-types: Generated patterns {patterns} and merged with includes")
            del args.only_types


        return args


    def _set_dependent_semantics(ctx: AppContext, args: argparse.Namespace) -> argparse.Namespace:
        """
        Set dependent argument values based on semantic flags.
        
        Args:
            ctx: Application context
            args: Parsed arguments namespace
            
        Returns:
            Arguments with dependent semantics set
        """
        
        # Use no-limit if outputting to file or zip or copy
        if getattr(args, "zip", False) or getattr(args, "export", False) or getattr(args, "copy", False):
            args.no_limit = True
            ctx.logger.log(ctx.logger.DEBUG, 
                          "--detailed: Setting verbose=True")


        return args 
    