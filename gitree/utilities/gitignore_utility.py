# gitree/utilities/gitignore_utility.py

"""
Code file for housing GitIgnoreMatcher.
"""

# Default libs
from pathlib import Path

# Deps from this project
from ..objects.gitignore import GitIgnore
from ..objects.app_context import AppContext
from ..objects.config import Config


class GitIgnoreMatcher:

    def __init__(self):
        self.gitignores: list[GitIgnore] = []
        self.ignored_count: int = 0

    
    def add_gitignore(self, gitignore: GitIgnore):
        self.gitignores.append(gitignore)

    
    def excluded(self, item_path: Path) -> bool:
        for gitignore in self.gitignores:
            if gitignore.excluded(item_path):
                self.ignored_count += 1
                return True
            
        return False

