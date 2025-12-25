import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


class TestListingFlags(unittest.TestCase):
    def test_entry_point_emoji(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "file.txt").write_text("hello")

            result = subprocess.run(
                [sys.executable, "-m", "gitree.main", "--emoji"],
                cwd=root,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(result.stdout.strip())
            self.assertIn("file.txt", result.stdout)

    def test_entry_point_no_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "file.txt").write_text("hello")
            (root / "folder").mkdir()
            (root / "folder" / "nested.txt").write_text("nested")

            result = subprocess.run(
                [sys.executable, "-m", "gitree.main", "--no-files"],
                cwd=root,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(result.stdout.strip())
            self.assertIn("folder", result.stdout)
            self.assertNotIn("file.txt", result.stdout)
            self.assertNotIn("nested.txt", result.stdout)

    def test_entry_point_max_depth(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "file.txt").write_text("hello")
            (root / "folder").mkdir()
            (root / "folder" / "nested.txt").write_text("nested")

            result = subprocess.run(
                [sys.executable, "-m", "gitree.main", "--max-depth", "1"],
                cwd=root,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(result.stdout.strip())
            self.assertIn("file.txt", result.stdout)
            self.assertIn("folder", result.stdout)
            self.assertNotIn("nested.txt", result.stdout)

    def test_entry_point_no_limit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "folder").mkdir()
            for i in range(30):  # Since the current default limit is 20
                (root / "folder" / f"file{i}.txt").write_text("data")

            result = subprocess.run(
                [sys.executable, "-m", "gitree.main", "--no-limit"],
                cwd=root,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(result.stdout.strip())
            for i in range(30):
                self.assertIn(f"file{i}.txt", result.stdout)
