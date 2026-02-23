import pytest
from pathlib import Path
from unittest import mock
from types import SimpleNamespace
from src.file_organizer import FileOrganizer


@pytest.fixture
def organizer(tmp_path):
    # tmp_path is a built-in pytest fixture — a real temporary directory
    return FileOrganizer(base_dir=tmp_path)


@pytest.fixture
def populated_dir(tmp_path):
    # Create a fake directory with known files for organize_dir to sort
    (tmp_path / "report.pdf").write_text("pdf content")
    (tmp_path / "photo.jpg").write_text("image content")
    (tmp_path / "song.mp3").write_text("audio content")
    (tmp_path / "archive.zip").write_text("archive content")
    (tmp_path / "notes.txt").write_text("text content")
    (tmp_path / "mystery.xyz").write_text("unknown content")
    return tmp_path


class TestOrganizeDir:

    def test_files_moved_to_correct_folders(self, organizer, populated_dir):
        args = SimpleNamespace(directory=str(populated_dir))
        organizer.organize_dir(args)

        assert (populated_dir / "Documents" / "report.pdf").exists()
        assert (populated_dir / "Images" / "photo.jpg").exists()
        assert (populated_dir / "Audios" / "song.mp3").exists()
        assert (populated_dir / "Archives" / "archive.zip").exists()
        assert (populated_dir / "Others" / "mystery.xyz").exists()

    def test_original_files_no_longer_in_root(self, organizer, populated_dir):
        args = SimpleNamespace(directory=str(populated_dir))
        organizer.organize_dir(args)

        assert not (populated_dir / "report.pdf").exists()
        assert not (populated_dir / "photo.jpg").exists()

    def test_nonexistent_directory(self, organizer, capsys):
        # capsys is another built-in pytest fixture that captures stdout/stderr
        args = SimpleNamespace(directory="/this/does/not/exist")
        organizer.organize_dir(args)

        captured = capsys.readouterr()
        assert "does not exist" in captured.out

    def test_path_is_file_not_directory(self, organizer, tmp_path, capsys):
        fake_file = tmp_path / "iam_a_file.txt"
        fake_file.write_text("hello")
        args = SimpleNamespace(directory=str(fake_file))
        organizer.organize_dir(args)

        captured = capsys.readouterr()
        assert "file not a directory" in captured.out


class TestConvertToBytes:

    def test_kilobytes(self, organizer):
        result = organizer._convert_to_bytes("100KB")
        assert result[0] == 100 * 1024

    def test_megabytes(self, organizer):
        result = organizer._convert_to_bytes("1.5MB")
        assert result[0] == 1.5 * 1024**2

    def test_invalid_unit(self, organizer, capsys):
        result = organizer._convert_to_bytes("100XB")
        assert result is None
        captured = capsys.readouterr()
        assert "not a valid unit" in captured.out

    def test_invalid_format(self, organizer, capsys):
        result = organizer._convert_to_bytes("oneKB")
        assert result is None


class TestDeletePath:

    def test_delete_all(self, organizer, tmp_path):
        f1 = tmp_path / "file1.txt"
        f2 = tmp_path / "file2.txt"
        f1.write_text("a")
        f2.write_text("b")

        with mock.patch("builtins.input", return_value="A"):
            organizer._delete_path([f1, f2], "files")

        assert not f1.exists()
        assert not f2.exists()

    def test_delete_selected_yes(self, organizer, tmp_path):
        f1 = tmp_path / "file1.txt"
        f1.write_text("a")

        # First input() is the menu choice (B), second is the per-file confirmation (y)
        with mock.patch("builtins.input", side_effect=["B", "y"]):
            organizer._delete_path([f1], "files")

        assert not f1.exists()

    def test_delete_selected_no(self, organizer, tmp_path):
        f1 = tmp_path / "file1.txt"
        f1.write_text("a")

        with mock.patch("builtins.input", side_effect=["B", "N"]):
            organizer._delete_path([f1], "files")

        assert f1.exists()  # Should still be there

    def test_continue_without_deleting(self, organizer, tmp_path):
        f1 = tmp_path / "file1.txt"
        f1.write_text("a")

        with mock.patch("builtins.input", return_value="C"):
            organizer._delete_path([f1], "files")

        assert f1.exists()