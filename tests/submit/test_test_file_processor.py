from typing import Optional
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from ahc_local_leaderboard.submit.test_file_processor import (
    AtCoderTestFileProcessor,
    TestFileProcessorInterface,
    TestFilesProcessor,
)


@pytest.fixture
def test_file_processor() -> AtCoderTestFileProcessor:
    return AtCoderTestFileProcessor()


@pytest.fixture
def mock_test_file_processor() -> Mock:
    return Mock(spec=TestFileProcessorInterface)


def generate_mock_test_file(file_name: str) -> MagicMock:
    return MagicMock(input_file_path="sample.txt", submit_file_path="sample.txt", file_name=file_name)


def generate_mock_test_files(file_names: list[str]) -> MagicMock:
    test_files = [generate_mock_test_file(file_name) for file_name in file_names]

    mock_files = MagicMock()
    mock_files.file_count = len(file_names)
    mock_files.__iter__.return_value = iter(test_files)
    mock_files.add_all_files = MagicMock()

    return mock_files


@pytest.mark.parametrize("decoded_output", ["Score = 1\n", "Score = 100\n", "Score = -100\n", "Score = 0\n"])
def test_is_valid_output(decoded_output: str, test_file_processor: AtCoderTestFileProcessor) -> None:
    test_file_processor.validate_output_format(decoded_output)


@pytest.mark.parametrize(
    "decoded_output",
    [
        "Unexpected EOF\nScore = 0\n",
        "Invalid operation: P\nScore = 100\n",
        "Invalid operation length\nScore = -100\n",
    ],
)
def test_is_valid_output_invalid(decoded_output: str, test_file_processor: AtCoderTestFileProcessor) -> None:
    with pytest.raises(ValueError):
        test_file_processor.validate_output_format(decoded_output)


@pytest.mark.parametrize(
    "decoded_output, expected_score",
    [
        ("Score = 1\n", 1),
        ("Score = 100\n", 100),
        ("Score = -100\n", -100),
        ("Score = 0\n", 0),
    ],
)
def test_parse_stdout(
    decoded_output: str, expected_score: Optional[int], test_file_processor: AtCoderTestFileProcessor
) -> None:
    assert test_file_processor.parse_stdout(decoded_output) == expected_score


@pytest.mark.parametrize("decoded_output", ["", "Score=100"])
def test_parse_stdout_invalid(decoded_output: str, test_file_processor: AtCoderTestFileProcessor) -> None:
    with pytest.raises(ValueError):
        test_file_processor.parse_stdout(decoded_output)


@patch("builtins.open", new_callable=mock_open)
@patch("subprocess.run")
@pytest.mark.parametrize(
    "decoded_output, expected_score",
    [
        ("Score = 1\n", 1),
        ("Score = 100\n", 100),
        ("Score = -100\n", -100),
        ("Score = 0\n", 0),
    ],
)
def test_process_test_file(
    mock_subprocess_run: Mock,
    mock_open_func: Mock,
    decoded_output: str,
    expected_score: Optional[int],
    test_file_processor: AtCoderTestFileProcessor,
) -> None:
    mock_subprocess_run.return_value = Mock(stdout=decoded_output.encode("utf-8"))
    score = test_file_processor.process_test_file(generate_mock_test_file("sample"))
    assert score == expected_score


@patch("builtins.open", new_callable=mock_open)
@patch("subprocess.run")
@pytest.mark.parametrize(
    "decoded_output, expected_score",
    [
        ("Unexpected EOF\nScore = 0\n", None),
        ("Invalid operation: P\nScore = 100\n", None),
        ("Invalid operation length\nScore = -100\n", None),
    ],
)
def test_process_test_file_invalid(
    mock_subprocess_run: Mock,
    mock_open_func: Mock,
    decoded_output: str,
    expected_score: Optional[int],
    test_file_processor: AtCoderTestFileProcessor,
) -> None:
    mock_subprocess_run.return_value = Mock(stdout=decoded_output.encode("utf-8"))
    score = test_file_processor.process_test_file(generate_mock_test_file("sample"))
    assert score is None


@pytest.mark.parametrize(
    "file_names, expected_scores",
    [
        (
            [
                "0000.txt",
                "0001.txt",
                "0002.txt",
                "0003.txt",
                "0004.txt",
                "0005.txt",
                "0006.txt",
            ],
            [1, 100, -100, 0, None, None, None],
        ),
    ],
)
def test_process_test_files(
    file_names: list[str],
    expected_scores: list[Optional[int]],
    mock_test_file_processor: Mock,
) -> None:

    mock_test_files = generate_mock_test_files(file_names)
    mock_test_file_processor.process_test_file.side_effect = expected_scores

    processor = TestFilesProcessor(mock_test_files, mock_test_file_processor)

    test_cases = processor.process_test_files()

    assert len(test_cases.test_cases) == len(expected_scores)
    for i, test_case in enumerate(test_cases):
        assert test_case.score == expected_scores[i]
