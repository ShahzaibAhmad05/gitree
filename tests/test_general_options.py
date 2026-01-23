# tests/test_general_options.py

"""
Code file for TestGeneralOptions class.

Tests general CLI options shown in gt -h:
    - No arguments (default behavior)
    - --version
    - --help
    - --verbose
    - --no-config
"""

from tests.base_setup import BaseCLISetup


class TestGeneralOptions(BaseCLISetup):
    """
    Tests general CLI behavior & options, including:
        - Running gitree with no arguments
        - Displaying version information (--version)
        - Displaying help information (--help)
        - Enabling verbose logging (--verbose)
        - Config options (--no-config)
    """

    def test_no_arg(self):
        """
        Test if it is working without any CLI arguments.
        It should print a tree structure (root name in this case),
        which includes the name "tmp"
        """
        # Vars
        args_str = ""

        # Test
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(0, result.returncode,
            msg="Failed default run. " +
                self.non_zero_exitcode_msg(result.returncode))

        self.assertIn("tmp", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"'tmp' not found in output: \n\n{result.stdout}")


    def test_version(self):
        """
        Test if it prints the version using: --version
        Should work for developer version too.
        """
        # Vars
        args_str = "--version"

        # Test
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

        self.assertIn(".", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"No dots found in the output: \n\n{result.stdout}")


    def test_help(self):
        """
        Test if help is displayed using: --help
        """
        # Vars
        args_str = "--help"

        # Test
        result = self.run_gitree(args_str)

        # Validate - help exits with 0
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        # Should contain help-related text
        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

        # Check for help content indicators
        self.assertTrue(
            "Usage" in result.stdout or "GITREE" in result.stdout or "help" in result.stdout.lower(),
            msg=self.failed_run_msg(args_str) +
                f"Expected help content not found in output: \n\n{result.stdout}")


    def test_verbose(self):
        """
        Test if the logging utility is working properly
        using: --verbose.
        """
        # Vars
        args_str = "--verbose"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
            self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

        self.assertIn("LOG", result.stdout,
            msg=self.failed_run_msg(args_str) +
                f"Expected str 'LOG' not found in output: \n\n{result.stdout}")


    def test_no_config(self):
        """
        Test if --no-config flag works properly.
        Should ignore config.json files and use default values.
        """
        # Vars
        args_str = "--no-config"

        # Run
        result = self.run_gitree(args_str)

        # Validate
        self.assertEqual(result.returncode, 0,
            msg=self.failed_run_msg(args_str) +
                self.non_zero_exitcode_msg(result.returncode))

        self.assertTrue(result.stdout.strip(),
            msg=self.failed_run_msg(args_str) +
                self.no_output_msg())

