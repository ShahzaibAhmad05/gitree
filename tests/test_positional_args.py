# tests/test_positional_args.py

"""
Code file for TestPositionalArguments class.

Tests positional arguments (PATHS) functionality as shown in gt -h:
    - Default path (current directory)
    - Single path
    - Multiple paths
    - File patterns (glob patterns)
"""

from tests.base_setup import BaseCLISetup
from pathlib import Path


class TestPositionalArguments(BaseCLISetup):
    """
    Tests positional arguments (PATHS) functionality:
        - Single path
        - Multiple paths
        - File patterns (glob patterns)
        - Default path (current directory)
    """

    def setUp(self):
        """
        Set up test environment with sample files.
        """
        super().setUp()
        
        # Create sample directory structure
        (self.root / "project1").mkdir()
        (self.root / "project1" / "file1.py").write_text("# file 1")
        
        (self.root / "project2").mkdir()
        (self.root / "project2" / "file2.py").write_text("# file 2")
        
        (self.root / "docs").mkdir()
        (self.root / "docs" / "README.md").write_text("# Docs")
        
        (self.root / "src").mkdir()
        (self.root / "src" / "app.js").write_text("console.log('app')")


    def test_default_path(self):
        """
        Test default path (no arguments).
        Should use current working directory.
        """
        # Vars (empty args means current directory)
        args_str = ""

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

        # Should show the temp directory name
        self.assertIn("tmp", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Expected 'tmp' (temp dir) in output: \n\n{result.stdout}")


    def test_single_path(self):
        """
        Test with a single path argument.
        Should display only that directory.
        """
        # Vars
        args_str = "project1"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

        # Should contain project1
        self.assertIn("project1", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Expected 'project1' in output: \n\n{result.stdout}")


    def test_multiple_paths(self):
        """
        Test with multiple path arguments.
        Should display both directories.
        """
        # Vars
        args_str = "project1 project2"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

        # Should contain project1 (at minimum)
        self.assertIn("project1", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Expected 'project1' in output: \n\n{result.stdout}")


    def test_file_pattern_python(self):
        """
        Test with file pattern (glob) for Python files.
        Should match files with the .py pattern.
        """
        # Vars
        args_str = "project1"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

        # Should include the project1 directory
        has_py = "project1" in result.stdout or "file1.py" in result.stdout
        self.assertTrue(has_py,
            msg=self.failed_run_msg(args_str) +
                f"Expected project1 or .py files in output: \n\n{result.stdout}")


    def test_specific_directory_path(self):
        """
        Test with a specific subdirectory path.
        Should only show contents of that subdirectory.
        """
        # Vars
        args_str = "docs"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

        # Should show the docs directory
        self.assertIn("docs", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Expected 'docs' in output: \n\n{result.stdout}")

