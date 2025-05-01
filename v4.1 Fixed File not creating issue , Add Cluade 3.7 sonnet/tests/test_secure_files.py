import unittest
import os
import tempfile
import shutil
from pathlib import Path

from utils.secure_files import (
    SecureFileHandler, secure_read_file, secure_write_file,
    secure_edit_file, secure_list_files, secure_get_file_info
)

class TestSecureFiles(unittest.TestCase):
    """Test cases for secure file operations utility functions."""

    def setUp(self):
        """Set up test environment with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files and directories
        self.test_file = os.path.join(self.temp_dir, "test_file.txt")
        with open(self.test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\nTest content\nLine 5\n")
            
        # Create a subdirectory
        self.sub_dir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(self.sub_dir, exist_ok=True)
        
        # Create a file in the subdirectory
        self.sub_file = os.path.join(self.sub_dir, "sub_file.txt")
        with open(self.sub_file, "w") as f:
            f.write("Subdir file content\nTest line\n")
            
        # Create a secure file handler for testing
        self.secure_handler = SecureFileHandler(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory after tests."""
        shutil.rmtree(self.temp_dir)

    def test_validate_path(self):
        """Test validate_path method."""
        # Test valid paths
        is_valid, _ = self.secure_handler.validate_path(self.test_file)
        self.assertTrue(is_valid)
        
        is_valid, _ = self.secure_handler.validate_path(self.sub_file)
        self.assertTrue(is_valid)
        
        # Test invalid paths (outside base directory)
        parent_dir = os.path.dirname(self.temp_dir)
        outside_file = os.path.join(parent_dir, "outside.txt")
        is_valid, _ = self.secure_handler.validate_path(outside_file)
        self.assertFalse(is_valid)
        
        # Test path traversal
        traversal_path = os.path.join(self.temp_dir, "..", "traversal.txt")
        is_valid, _ = self.secure_handler.validate_path(traversal_path)
        self.assertFalse(is_valid)

    def test_read_file(self):
        """Test secure read_file method."""
        # Test reading entire file
        content, lines = self.secure_handler.read_file(self.test_file)
        self.assertEqual(content, "Line 1\nLine 2\nLine 3\nTest content\nLine 5\n")
        self.assertEqual(lines, 5)
        
        # Test reading specific lines
        content, _ = self.secure_handler.read_file(self.test_file, start_line=1, end_line=3)
        self.assertEqual(content, "Line 2\nLine 3\n")
        
        # Test reading file outside base directory
        parent_dir = os.path.dirname(self.temp_dir)
        outside_file = os.path.join(parent_dir, "outside.txt")
        with open(outside_file, "w") as f:
            f.write("Content outside base dir")
        
        content, lines = self.secure_handler.read_file(outside_file)
        self.assertIn("cannot read file", content.lower())
        self.assertEqual(lines, 0)
        
        # Clean up outside file
        os.remove(outside_file)

    def test_write_file(self):
        """Test secure write_file method."""
        # Test writing to a file
        new_file = os.path.join(self.temp_dir, "new_secure_file.txt")
        result = self.secure_handler.write_file(new_file, "Secure content")
        self.assertTrue("successfully" in result.lower())
        self.assertTrue(os.path.exists(new_file))
        
        # Test writing to a file outside base directory
        parent_dir = os.path.dirname(self.temp_dir)
        outside_file = os.path.join(parent_dir, "outside_write.txt")
        result = self.secure_handler.write_file(outside_file, "Outside content")
        self.assertIn("cannot write to file", result.lower())
        self.assertFalse(os.path.exists(outside_file))
        
        # Test creating directories
        nested_file = os.path.join(self.temp_dir, "nested", "dir", "file.txt")
        result = self.secure_handler.write_file(nested_file, "Nested content", create_dirs=True)
        self.assertTrue("successfully" in result.lower())
        self.assertTrue(os.path.exists(nested_file))

    def test_edit_file(self):
        """Test secure edit_file method."""
        # Test editing a file
        result = self.secure_handler.edit_file(self.test_file, "Edited securely", start_line=2, end_line=3)
        self.assertTrue("successfully" in result.lower())
        
        # Verify the content
        with open(self.test_file, "r") as f:
            content = f.read()
            self.assertIn("Line 1\nLine 2\nEdited securelyTest content\nLine 5", content)
        
        # Test editing a file outside base directory
        parent_dir = os.path.dirname(self.temp_dir)
        outside_file = os.path.join(parent_dir, "outside_edit.txt")
        with open(outside_file, "w") as f:
            f.write("Outside content")
            
        result = self.secure_handler.edit_file(outside_file, "Edited outside")
        self.assertIn("cannot edit file", result.lower())
        
        # Clean up outside file
        os.remove(outside_file)

    def test_list_files(self):
        """Test secure list_files method."""
        # Test listing all files
        files = self.secure_handler.list_files(self.temp_dir)
        self.assertIn(self.test_file, files)
        self.assertIn(self.sub_file, files)
        
        # Test listing with pattern
        files = self.secure_handler.list_files(self.temp_dir, pattern=r".*\.txt$")
        self.assertIn(self.test_file, files)
        
        # Test listing outside base directory
        parent_dir = os.path.dirname(self.temp_dir)
        files = self.secure_handler.list_files(parent_dir)
        self.assertEqual(len(files), 1)
        self.assertIn("cannot list directory", files[0].lower())

    def test_get_file_info(self):
        """Test secure get_file_info method."""
        # Test getting info for a file
        info = self.secure_handler.get_file_info(self.test_file)
        self.assertTrue(info["exists"])
        self.assertTrue(info["is_file"])
        self.assertEqual(info["extension"], ".txt")
        
        # Test getting info for a directory
        info = self.secure_handler.get_file_info(self.sub_dir)
        self.assertTrue(info["exists"])
        self.assertTrue(info["is_dir"])
        
        # Test getting info for a file outside base directory
        parent_dir = os.path.dirname(self.temp_dir)
        outside_file = os.path.join(parent_dir, "outside_info.txt")
        with open(outside_file, "w") as f:
            f.write("Outside content")
            
        info = self.secure_handler.get_file_info(outside_file)
        self.assertIn("error", info)
        self.assertIn("cannot get file info", info["error"].lower())
        
        # Clean up outside file
        os.remove(outside_file)

    def test_convenience_functions(self):
        """Test the convenience functions."""
        # Create a new file for testing convenience functions
        conv_file = os.path.join(self.temp_dir, "convenience.txt")
        with open(conv_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")
        
        # Make sure the default handler's base directory includes our temp directory
        # This is a bit of a hack for testing, normally you wouldn't modify this
        import utils.secure_files
        utils.secure_files.default_secure_handler = SecureFileHandler(self.temp_dir)
        
        # Test secure_read_file
        content, lines = secure_read_file(conv_file)
        self.assertEqual(content, "Line 1\nLine 2\nLine 3\n")
        self.assertEqual(lines, 3)
        
        # Test secure_write_file
        new_conv_file = os.path.join(self.temp_dir, "new_convenience.txt")
        result = secure_write_file(new_conv_file, "New content")
        self.assertTrue("successfully" in result.lower())
        self.assertTrue(os.path.exists(new_conv_file))
        
        # Test secure_edit_file
        result = secure_edit_file(conv_file, "Edited line", start_line=1, end_line=1)
        self.assertTrue("successfully" in result.lower())
        
        # Test secure_list_files
        files = secure_list_files(self.temp_dir)
        self.assertIn(conv_file, files)
        self.assertIn(new_conv_file, files)
        
        # Test secure_get_file_info
        info = secure_get_file_info(conv_file)
        self.assertTrue(info["exists"])
        self.assertTrue(info["is_file"])


if __name__ == "__main__":
    unittest.main() 