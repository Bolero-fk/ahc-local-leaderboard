from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator
from unittest.mock import patch

import pytest

from ahc_local_leaderboard.models.test_file import TestFile, TestFiles


@pytest.fixture
def temp_directories() -> Generator[tuple[Path, Path], None, None]:
    with TemporaryDirectory() as input_dir, TemporaryDirectory() as submit_dir:
        yield Path(input_dir), Path(submit_dir)


def generate_dummy_file(directory: Path, file_name: str) -> Path:
    file_path = directory / file_name
    with open(file_path, "w") as f:
        f.write("test content")
    return file_path


def test_initialization(temp_directories: tuple[Path, Path]) -> None:
    input_dir, submit_dir = temp_directories
    test_files = TestFiles(input_dir, submit_dir)
    assert test_files.input_dir_path == input_dir
    assert test_files.submit_dir_path == submit_dir
    assert test_files.file_count == 0
    assert test_files.test_files == []


@pytest.mark.parametrize("seed_num", ["0000", "1010", "0"])
def test_get_seed_number(seed_num: str) -> None:

    test_file = TestFile(seed_num + ".txt", Path("in.txt"), Path("out.txt"))
    assert test_file.get_seed_number() == int(seed_num)


@pytest.mark.parametrize("file_name", ["test_file.txt", "12345.txt", "file_name.in"])
def test_add_file(temp_directories: tuple[Path, Path], file_name: str) -> None:
    input_dir, submit_dir = temp_directories
    test_files = TestFiles(input_dir, submit_dir)

    input_file_path = generate_dummy_file(input_dir, file_name)
    submit_file_path = generate_dummy_file(submit_dir, file_name)

    test_files.add_file(file_name)

    assert test_files.file_count == 1
    assert len(test_files.test_files) == 1
    assert test_files.test_files[0].file_name == file_name
    assert test_files.test_files[0].input_file_path == input_file_path
    assert test_files.test_files[0].submit_file_path == submit_file_path


@pytest.mark.parametrize(
    "file_names",
    [
        ["file1.txt", "file2.txt", "file3.txt"],
        ["_very_long_file_name_to_test_limits.txt"],
        [],
    ],
)
def test_fetch_file_names_from_directory(temp_directories: tuple[Path, Path], file_names: list[str]) -> None:
    input_dir, submit_dir = temp_directories

    for file_name in file_names:
        generate_dummy_file(input_dir, file_name)
        generate_dummy_file(submit_dir, file_name)

    test_files = TestFiles(input_dir, submit_dir)
    test_file_names = test_files.fetch_file_names_from_directory()

    assert len(test_file_names) == len(file_names)
    assert all(test_file_name in file_names for test_file_name in test_file_names)


@pytest.mark.parametrize(
    "file_names",
    [
        ["file1.txt", "file2.txt", "file3.txt"],
        ["_very_long_file_name_to_test_limits.txt"],
        [],
    ],
)
def test_add_all_files(temp_directories: tuple[Path, Path], file_names: list[str]) -> None:
    input_dir, submit_dir = temp_directories

    for file_name in file_names:
        generate_dummy_file(input_dir, file_name)
        generate_dummy_file(submit_dir, file_name)

    test_files = TestFiles(input_dir, submit_dir)
    test_files.add_all_files()

    assert test_files.file_count == len(file_names)
    assert len(test_files.test_files) == len(file_names)
    assert all(isinstance(f, TestFile) for f in test_files.test_files)
    assert [f.file_name for f in test_files.test_files] == sorted(file_names)


def test_iteration(temp_directories: tuple[Path, Path]) -> None:
    input_dir, submit_dir = temp_directories
    test_files = TestFiles(input_dir, submit_dir)

    with patch("builtins.iter", wraps=iter) as mock_iter:
        list(test_files)  # __iter__を呼び出している
        mock_iter.assert_called_once_with(test_files.test_files)
