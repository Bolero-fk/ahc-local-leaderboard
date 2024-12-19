from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

from ahc_local_leaderboard.submit.test_file_processor import (
    AtCoderTestFileProcessor,
    PahcerTestFileProcessor,
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


@pytest.mark.parametrize(
    "decoded_output, expected_score",
    [
        ("Score = 1\n", 1),
        ("Score = 100\n", 100),
        ("Score = -100\n", None),
        ("Score = 0\n", None),
        (
            "warning: field comments is never read\n\
            warning: fields initial_comments and commented_op are never read\nScore = 1679\n",
            1679,
        ),
    ],
)
def test_parse_stdout(
    decoded_output: str, expected_score: Optional[int], test_file_processor: AtCoderTestFileProcessor
) -> None:
    assert test_file_processor.parse_stdout(decoded_output) == expected_score


@patch("builtins.open", new_callable=mock_open)
@patch("subprocess.run")
@pytest.mark.parametrize(
    "decoded_output, expected_score",
    [
        ("Score = 1\n", 1),
        ("Score = 100\n", 100),
        ("Score = -100\n", None),
        ("Score = 0\n", None),
        (
            "warning: field comments is never read\n\
            warning: fields initial_comments and commented_op are never read\nScore = 1679\n",
            1679,
        ),
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

    processor = TestFilesProcessor(mock_test_file_processor)

    test_cases = processor.process_test_files(mock_test_files)

    assert len(test_cases.test_cases) == len(expected_scores)
    for i, test_case in enumerate(test_cases):
        assert test_case.score == expected_scores[i]


def sample_pahcer_data() -> dict:  # type: ignore
    return {
        "wa_seeds": [1, 3],
        "cases": [
            {"seed": 0, "score": 100},
            {"seed": 1, "score": 0},
            {"seed": 2, "score": 50},
            {"seed": 3, "score": 0},
            {"seed": 10, "score": 8},
        ],
    }


def test_get_case_by_seed() -> None:

    with patch(
        "ahc_local_leaderboard.submit.test_file_processor.PahcerTestFileProcessor.load_pahcer_file",
        return_value=sample_pahcer_data(),
    ):
        processor = PahcerTestFileProcessor(Path("mock.json"))

        case = processor.get_case_by_seed(2)
        assert case == {"seed": 2, "score": 50}

        case = processor.get_case_by_seed(10)
        assert case == {"seed": 10, "score": 8}

        case = processor.get_case_by_seed(99)
        assert case is None


def test_pahcer_process_test_file() -> None:

    with patch(
        "ahc_local_leaderboard.submit.test_file_processor.PahcerTestFileProcessor.load_pahcer_file",
        return_value=sample_pahcer_data(),
    ):
        processor = PahcerTestFileProcessor(Path("mock.json"))

        test_file = Mock()

        test_file.get_seed_number.return_value = 0
        score = processor.process_test_file(test_file)
        assert score == 100

        test_file.get_seed_number.return_value = 1
        score = processor.process_test_file(test_file)
        assert score is None

        test_file.get_seed_number.return_value = 99
        score = processor.process_test_file(test_file)
        assert score is None

        test_file.get_seed_number.return_value = 10
        score = processor.process_test_file(test_file)
        assert score == 8
