# tests/test_semantic_options.py

"""
Code file for TestSemanticOptions class.

Tests all semantic flags (quick actions) that are shown in gt -h:
    - --full
    - --emoji
    - --copy
    - --only-types
"""

from tests.base_setup import BaseCLISetup
from pathlib import Path


class TestSemanticOptions(BaseCLISetup):
    """
    Tests semantic flags / quick action options, including:
        - Full tree display (--full)
        - Emoji output (--emoji)
        - Copy to clipboard (--copy)
        - Filter by file types (--only-types)
    """

    def setUp(self):
        """
        Set up test environment with sample files.
        """
        super().setUp()
        
        # Create sample directory structure
        (self.root / "src").mkdir()
        (self.root / "src" / "main.py").write_text("print('hello')")
        (self.root / "src" / "utils.py").write_text("def helper(): pass")
        (self.root / "src" / "app.js").write_text("console.log('test')")
        
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_main.py").write_text("def test(): pass")
        
        (self.root / "README.md").write_text("# Project")
        (self.root / "config.json").write_text('{"key": "value"}')


    def test_full(self):
        """
        Test --full flag
        Should set max-depth to 5
        """
        # Vars
        args_str = "--full"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

        # Should show directory structure
        self.assertIn("src", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Expected 'src' in output: \n\n{result.stdout}")


    def test_emoji(self):
        """
        Test --emoji flag
        Should display emojis in output
        """
        # Vars
        args_str = "--emoji"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

        # Check for emoji characters
        has_emoji = any(ord(c) > 127 for c in result.stdout)
        self.assertTrue(has_emoji,
            msg=self.failed_run_msg(args_str) +
                f"No emojis found in output: \n\n{result.stdout}")


    def test_copy(self):
        """
        Test --copy flag
        Should copy to clipboard
        """
        # Vars
        args_str = "--copy"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))


    def test_combined_semantic_flags(self):
        """
        Test combining multiple semantic flags together
        Should enable both --full and --emoji
        """
        # Vars
        args_str = "--full --emoji"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

        # Should show directory and have emojis
        self.assertIn("src", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Expected 'src' in output: \n\n{result.stdout}")

        has_emoji = any(ord(c) > 127 for c in result.stdout)
        self.assertTrue(has_emoji,
            msg=self.failed_run_msg(args_str) +
                f"No emojis found in combined flag output: \n\n{result.stdout}")


    def test_only_types(self):
        """
        Test --only-types flag
        Should include only Python files
        """
        # Vars
        args_str = "--only-types py"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

        # Should show Python files
        self.assertIn("main.py", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Expected 'main.py' in output: \n\n{result.stdout}")

        self.assertIn("utils.py", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Expected 'utils.py' in output: \n\n{result.stdout}")

        # Should not show JavaScript files
        self.assertNotIn("app.js", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Did not expect 'app.js' in output: \n\n{result.stdout}")


    def test_types_alias(self):
        """
        Test --types alias for --only-types
        Should work the same as --only-types
        """
        # Vars
        args_str = "--types py"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        # Should show Python files
        self.assertIn("main.py", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Expected 'main.py' in output: \n\n{result.stdout}")


    def test_t_alias(self):
        """
        Test -t alias for --only-types
        Should work the same as --only-types
        """
        # Vars
        args_str = "-t py"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        # Should show Python files
        self.assertIn("main.py", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Expected 'main.py' in output: \n\n{result.stdout}")


    def test_only_types_multiple_extensions(self):
        """
        Test --only-types with multiple file extensions
        Should include both Python and JavaScript files
        """
        # Vars
        args_str = "-t py js"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        # Should show both Python and JavaScript files
        self.assertIn("main.py", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Expected 'main.py' in output: \n\n{result.stdout}")

        self.assertIn("app.js", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Expected 'app.js' in output: \n\n{result.stdout}")

        # Should not show markdown or json
        self.assertNotIn("README.md", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Did not expect 'README.md' in output: \n\n{result.stdout}")

        self.assertNotIn("config.json", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Did not expect 'config.json' in output: \n\n{result.stdout}")
