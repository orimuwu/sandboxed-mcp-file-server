
import unittest
import tempfile
from pathlib import Path
from server import ROOT, safe_path, list_files, search_files

class TestSafePath(unittest.TestCase):

    def test_write_overwrites_existing_file(self):
        from server import write_file, read_file, delete_file

        path = "notes/overwrite_test.txt"

        try:
            write_file(path, "Original content")
            write_file(path, "Updated content")
            self.assertEqual(read_file(path), "Updated content")
        finally:
            file = ROOT / path
            if file.exists():
                delete_file(path)


    def test_delete_normal_file(self):
        from server import write_file, delete_file

        path = "notes/delete_test.txt"

        try:
            write_file(path, "Delete test")
            delete_file(path)
            self.assertFalse((ROOT / path).exists())
        finally:
            file = ROOT / path
            if file.exists():
                file.unlink()

    def test_str_replace_normal_file(self):
        from server import write_file, read_file, str_replace, delete_file

        path = "notes/replace_test.txt"

        try:
            write_file(path, "Hello world")
            str_replace(path, "world", "Python")
            self.assertEqual(read_file(path), "Hello Python")
        finally:
            file = ROOT / path
            if file.exists():
                delete_file(path)


    def test_write_normal_file(self):
        from server import write_file, read_file, delete_file

        path = "notes/write_test.txt"

        try:
            write_file(path, "Write test passed")
            self.assertEqual(read_file(path), "Write test passed")
        finally:
            file = ROOT / "notes" / "write_test.txt"
            if file.exists():
                delete_file(path)

    def test_read_normal_file(self):
        from server import read_file

        content = read_file("notes/test.txt")
        self.assertIn("Sandbox test passed", content)

    def test_list_files_in_subfolder(self):
        from server import list_files

        results = list_files("notes")

        expected = str(Path("notes") / "test.txt")
        self.assertIn(expected, results)

    def test_search_finds_matching_file(self):
        from server import search_files

        results = search_files("Sandbox test passed")

        self.assertIn(str(Path("notes") / "test.txt"), results)

    def test_delete_workspace_root_rejected(self):
        from server import delete_file

        with self.assertRaises(ValueError):
            delete_file(".")

    def test_write_to_workspace_root_rejected(self):
        from server import write_file

        with self.assertRaises(ValueError):
            write_file(".", "should not be written")

    def test_search_rejects_empty_query(self):
        from server import search_files

        with self.assertRaises(ValueError):
            search_files("")

    def test_str_replace_rejects_no_matches(self):
        from server import str_replace

        file = ROOT / "notes" / "security-test.txt"
        original = file.read_text(encoding="utf-8")

        try:
            file.write_text("apple", encoding="utf-8")

            with self.assertRaises(ValueError):
                str_replace("notes/security-test.txt", "banana", "orange")

            self.assertEqual(
                file.read_text(encoding="utf-8"),
                "apple"
            )
        finally:
            file.write_text(original, encoding="utf-8")

    def test_str_replace_rejects_multiple_matches(self):
        from server import str_replace

        file = ROOT / "notes" / "security-test.txt"
        original = file.read_text(encoding="utf-8")

        try:
            file.write_text("apple apple", encoding="utf-8")

            with self.assertRaises(ValueError):
                str_replace("notes/security-test.txt", "apple", "orange")

            self.assertEqual(
                file.read_text(encoding="utf-8"),
                "apple apple"
            )
        finally:
            file.write_text(original, encoding="utf-8")

    def test_windows_parent_traversal(self):
        with self.assertRaises(ValueError):
            safe_path(r"notes\..\..\server.py")

    def test_windows_drive_path_rejected(self):
        with self.assertRaises(ValueError):
            safe_path("C:Windows\\secret.txt")

    def test_delete_symlink_rejected(self):
        from server import delete_file

        with tempfile.TemporaryDirectory() as temp:
            outside = Path(temp) / "outside.txt"
            outside.write_text("secret", encoding="utf-8")

            link = ROOT / "security_delete_link_test.txt"

            try:
                link.symlink_to(outside)

                with self.assertRaises(ValueError):
                    delete_file("security_delete_link_test.txt")

                self.assertTrue(outside.exists())
                self.assertEqual(
                    outside.read_text(encoding="utf-8"),
                    "secret"
                )
            except OSError:
                self.skipTest(
                    "Symlink creation is not permitted on this system."
                )
            finally:
                if link.is_symlink():
                    link.unlink()

    def test_write_through_symlink_rejected(self):
        from server import write_file

        with tempfile.TemporaryDirectory() as temp:
            outside = Path(temp) / "outside.txt"
            outside.write_text("secret", encoding="utf-8")

            link = ROOT / "security_write_link_test.txt"

            try:
                link.symlink_to(outside)

                with self.assertRaises(ValueError):
                    write_file("security_write_link_test.txt", "modified")

                self.assertEqual(
                    outside.read_text(encoding="utf-8"),
                    "secret"
                )
            except OSError:
                self.skipTest(
                    "Symlink creation is not permitted on this system."
                )
            finally:
                if link.is_symlink():
                    link.unlink()

    def test_read_outside_workspace_rejected(self):
        from server import read_file

        with self.assertRaises(ValueError):
            read_file("../server.py")

    def test_str_replace_outside_workspace_rejected(self):
        from server import str_replace

        with self.assertRaises(ValueError):
            str_replace("../outside_test.txt", "old", "new")

    def test_delete_outside_workspace_rejected(self):
        from server import delete_file

        with self.assertRaises(ValueError):
            delete_file("../outside_test.txt")

    def test_write_outside_workspace_rejected(self):
        with self.assertRaises(ValueError):
            from server import write_file
            write_file("../outside_test.txt", "should not be written")

    def test_git_hidden_from_search(self):
        results = search_files("refs/heads")
        self.assertFalse(
            any(".git" in Path(item).parts for item in results)
        )

    def test_git_hidden_from_listing(self):
        files = list_files(".")
        self.assertFalse(
            any(".git" in Path(item).parts for item in files)
        )

    def test_git_metadata_rejection(self):
        with self.assertRaises(ValueError):
            safe_path(".git/HEAD")

    def test_nested_file(self):
        result = safe_path("notes/test.txt")
        self.assertEqual(result, ROOT / "notes" / "test.txt")

    def test_parent_traversal(self):
        with self.assertRaises(ValueError):
            safe_path("../server.py")

    def test_deep_traversal(self):
        with self.assertRaises(ValueError):
            safe_path("../../server.py")

    def test_absolute_path(self):
        with self.assertRaises(ValueError):
            safe_path(str(ROOT.parent / "server.py"))

    def test_normal_file(self):
        result = safe_path("test.txt")
        self.assertEqual(result, ROOT / "test.txt")

    def test_symlink_rejection(self):
        with tempfile.TemporaryDirectory() as temp:
            outside = Path(temp) / "outside.txt"
            outside.write_text("secret", encoding="utf-8")

            link = ROOT / "security_link_test.txt"

            try:
                link.symlink_to(outside)

                with self.assertRaises(ValueError):
                    safe_path("security_link_test.txt")
            except OSError:
                self.skipTest(
                    "Symlink creation is not permitted on this system."
                )
            finally:
                if link.is_symlink():
                    link.unlink()


if __name__ == "__main__":
    unittest.main()
