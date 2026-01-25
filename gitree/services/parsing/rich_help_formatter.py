# gitree/services/parsing/rich_help_formatter.py

"""
Rich-based help formatter for argparse.
Provides beautiful, color-coded help output using the Rich library.
"""

# Default libs
import argparse
import sys

# Dependencies
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box


class RichHelpFormatter(argparse.HelpFormatter):
    """
    Custom ArgumentParser formatter using Rich for beautiful, colorful help output.
    """

    def __init__(self, prog):
        super().__init__(prog, max_help_position=40, width=100)
        self.console = Console()

    def format_help(self):
        """Override to create a fully Rich-formatted help display."""
        self.console.print()
        
        # Header with tool name and description
        self._print_header()
        
        # Usage section
        self._print_usage()
        
        # Positional arguments
        self._print_positional_args()
        
        # Options sections - Only show General and Semantic options
        self._print_general_options()
        self._print_semantic_flags()
        
        # Exit after displaying help
        sys.exit(0)

    def _print_header(self):
        """Print the main header with tool name and description."""
        title = Text("""
     ██████╗ ██╗████████╗██████╗ ███████╗███████╗
    ██╔════╝ ██║╚══██╔══╝██╔══██╗██╔════╝██╔════╝
    ██║  ███╗██║   ██║   ██████╔╝█████╗  █████╗
    ██║   ██║██║   ██║   ██╔══██╗██╔══╝  ██╔══╝
    ╚██████╔╝██║   ██║   ██║  ██║███████╗███████╗
     ╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝
            """, style="blue")
        # subtitle = Text("Print a directory tree (does not respect .gitignore by default)", style="cyan italic")
        
        header_text = Text()
        header_text.append(title)
        # header_text.append("\n")
        # header_text.append(subtitle)
        
        self.console.print(header_text)

    def _print_usage(self):
        """Print usage information."""
        usage_text = Text()
        usage_text.append("gitree ", style="bold yellow")
        usage_text.append("[OPTIONS] ", style="green")
        usage_text.append("[PATHS...]", style="cyan")
        
        panel = Panel(
            usage_text,
            title="[bold white]Usage[/bold white]",
            title_align="left",
            box=box.ROUNDED,
            border_style="yellow",
            padding=(0, 2)
        )
        self.console.print(panel)

    def _print_positional_args(self):
        """Print positional arguments section."""
        table = Table(
            show_header=False,
            box=box.SIMPLE,
            padding=(0, 2),
            collapse_padding=True
        )
        table.add_column("Argument", style="bold cyan", width=20)
        table.add_column("Description", style="white")
        
        table.add_row(
            "PATHS",
            "Root paths (supports multiple directories and file patterns).\nDefaults to the current working directory."
        )
        
        panel = Panel(
            table,
            title="[bold white]Positional Arguments[/bold white]",
            title_align="left",
            box=box.ROUNDED,
            border_style="cyan",
            padding=(0, 1)
        )
        self.console.print(panel)

    def _print_general_options(self):
        """Print general options section."""
        table = Table(
            show_header=False,
            box=box.SIMPLE,
            padding=(0, 1),
            collapse_padding=True
        )
        table.add_column("Flag", style="bold green", width=25)
        table.add_column("Description", style="white")
        
        table.add_row(
            "-h, --help",
            "Show this help message and exit"
        )
        table.add_row(
            "-v, --version",
            "Display the version number of the tool"
        )
        table.add_row(
            "--config-user",
            "Create a default config.json file in the current directory\nand open that file in the default editor"
        )
        table.add_row(
            "--no-config",
            "Ignore both user-level and global-level config.json\nand use default and CLI values for configuration"
        )
        table.add_row(
            "--verbose",
            "Enable logger output to the console. Prints a log after\nthe full workflow run. Helpful for debugging."
        )
        
        panel = Panel(
            table,
            title="[bold white]General Options[/bold white]",
            title_align="left",
            box=box.ROUNDED,
            border_style="green",
            padding=(0, 1)
        )
        self.console.print(panel)

    def _print_semantic_flags(self):
        """Print semantic flags (quick actions) section."""
        table = Table(
            show_header=False,
            box=box.SIMPLE,
            padding=(0, 1),
            collapse_padding=True
        )
        table.add_column("Flag", style="bold cyan", width=25)
        table.add_column("Description", style="white")
        
        table.add_row(
            "-f, --full",
            "Shortcut for --max-depth 5 - show full directory tree\nup to 5 levels deep"
        )
        table.add_row(
            "-e, --emoji",
            "Show emojis in the output for better visual clarity"
        )
        table.add_row(
            "-i, --interactive",
            "Use interactive mode for manual file selection\nafter automatic filtering"
        )
        table.add_row(
            "-c, --copy",
            "Copy file contents and project structure to clipboard\n(great for LLM prompts)"
        )
        table.add_row(
            "--only-types [EXT...]",
            "Include only specific file types\n(e.g., --only-types py cpp tsx)"
        )
        
        panel = Panel(
            table,
            title="[bold white]Semantic Flags (Quick Actions)[/bold white]",
            title_align="left",
            box=box.ROUNDED,
            border_style="cyan",
            padding=(0, 1)
        )
        self.console.print(panel)

    def _print_output_options(self):
        """Print output & export options section."""
        table = Table(
            show_header=False,
            box=box.SIMPLE,
            padding=(0, 1),
            collapse_padding=True
        )
        table.add_column("Flag", style="bold yellow", width=25)
        table.add_column("Description", style="white")
        
        table.add_row(
            "-z, --zip [FILE]",
            "Create a zip archive of the given directory\n(respects gitignore if -g is used)"
        )
        table.add_row(
            "--export [FILE]",
            "Save project structure along with its contents to a file\nwith the format specified using --format"
        )
        table.add_row(
            "-c, --copy",
            "Copy file contents and project structure to clipboard.\nSimilar to --export but copies to clipboard instead"
        )
        
        panel = Panel(
            table,
            title="[bold white]Output & Export Options[/bold white]",
            title_align="left",
            box=box.ROUNDED,
            border_style="yellow",
            padding=(0, 1)
        )
        self.console.print(panel)

    def _print_listing_options(self):
        """Print listing options section."""
        table = Table(
            show_header=False,
            box=box.SIMPLE,
            padding=(0, 1),
            collapse_padding=True
        )
        table.add_column("Flag", style="bold magenta", width=30)
        table.add_column("Description", style="white")
        
        table.add_row(
            "--format [tree|json|md]",
            "Format output (default: tree)"
        )
        table.add_row(
            "--max-items N",
            "Limit items to be selected per directory"
        )
        table.add_row(
            "--max-entries N",
            "Limit entries (files/dirs) for the overall output"
        )
        table.add_row(
            "--max-depth N",
            "Maximum depth to traverse when selecting files"
        )
        table.add_row(
            "-f, --full",
            "Shortcut for --max-depth 5"
        )
        table.add_row(
            "--gitignore-depth N",
            "Limit depth to look for during .gitignore processing"
        )
        table.add_row(
            "--hidden-items, --all",
            "Show hidden files and directories"
        )
        table.add_row(
            "--exclude [PATTERNS...]",
            "Patterns of files to specifically exclude"
        )
        table.add_row(
            "--exclude-depth N",
            "Limit depth for exclude patterns"
        )
        table.add_row(
            "--include [PATTERNS...]",
            "Patterns of files to specifically include"
        )
        table.add_row(
            "--include-file-types [TYPES...]",
            "Include files of certain types"
        )
        table.add_row(
            "-e, --emoji",
            "Show emojis in the output"
        )
        table.add_row(
            "-i, --interactive",
            "Use interactive mode for further file selection"
        )
        table.add_row(
            "--files-first",
            "Print files before directories"
        )
        table.add_row(
            "--no-color",
            "Disable colored output"
        )
        table.add_row(
            "--no-contents",
            "Don't include file contents in export/copy"
        )
        table.add_row(
            "--no-contents-for [PATHS...]",
            "Exclude contents for specific files for export/copy"
        )
        table.add_row(
            "--max-file-size MB",
            "Maximum file size in MB to include in exports (default: 1.0)"
        )
        table.add_row(
            "--override-files",
            "Override existing files"
        )
        
        panel = Panel(
            table,
            title="[bold white]Listing Options[/bold white]",
            title_align="left",
            box=box.ROUNDED,
            border_style="magenta",
            padding=(0, 1)
        )
        self.console.print(panel)

    def _print_listing_override_options(self):
        """Print listing override options section."""
        table = Table(
            show_header=False,
            box=box.SIMPLE,
            padding=(0, 1),
            collapse_padding=True
        )
        table.add_column("Flag", style="bold red", width=25)
        table.add_column("Description", style="white")
        
        table.add_row(
            "--no-max-entries",
            "Disable --max-entries limit"
        )
        table.add_row(
            "--no-max-items",
            "Disable --max-items limit"
        )
        table.add_row(
            "-g, --gitignore",
            "Enable .gitignore rules (respects .gitignore files)"
        )
        table.add_row(
            "--no-files",
            "Hide files (show only directories)"
        )
        
        panel = Panel(
            table,
            title="[bold white]Listing Override Options[/bold white]",
            title_align="left",
            box=box.ROUNDED,
            border_style="red",
            padding=(0, 1)
        )
        self.console.print(panel)
