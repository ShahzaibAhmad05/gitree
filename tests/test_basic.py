import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


class TestBasic(unittest.TestCase):
    def test_entry_point_runs_and_lists_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "file.txt").write_text("hello")

            result = subprocess.run(
                [sys.executable, "-m", "gitree.main"],
                cwd=root,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(result.stdout.strip())
            self.assertIn("file.txt", result.stdout)

    def test_entry_point_help(self):
        result = subprocess.run(
            [sys.executable, "-m", "gitree.main", "--help"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.strip())
        self.assertIn("--help", result.stdout)

    def test_entry_point_version(self):
        result = subprocess.run(
            [sys.executable, "-m", "gitree.main", "--version"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.strip())
        # Keeping your original check; consider asserting a known version pattern if you want stricter.
        self.assertIn(".", result.stdout)
