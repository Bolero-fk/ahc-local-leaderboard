import argparse
from pathlib import Path
from typing import Optional
from unittest.mock import Mock

import pytest

from ahc_local_leaderboard.utils.validator import (
    CommandValidatorBase,
    InitValidator,
    SubmitValidator,
    ViewValidator,
)


@pytest.fixture
def mock_test_files() -> Mock:
    mock = Mock()
    mock.input_dir_path = Path("/fake/input_dir")
    mock.submit_dir_path = Path("/fake/submit_dir")
    mock.fetch_file_names_from_directory.return_value = ["test1.txt", "test2.txt"]
    return mock


@pytest.fixture
def mock_record_read_service() -> Mock:
    mock = Mock()
    mock.exists_id.side_effect = lambda x: x == 1  # IDが1の場合のみ存在すると仮定
    return mock


def mock_return_true_func() -> bool:
    return Mock(return_value=True)


def mock_return_false_func() -> bool:
    return Mock(return_value=False)


def test_init_validator(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ahc_local_leaderboard.consts.ROOT_DIR", Path("/fake"))

    monkeypatch.setattr(Path, "exists", mock_return_true_func())

    validator = InitValidator()
    args = argparse.Namespace()

    assert validator.validate(args) is True
    assert validator.errors == []


def test_init_validator_missing_directories_and_files(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ahc_local_leaderboard.consts.ROOT_DIR", Path("/fake"))

    monkeypatch.setattr(Path, "exists", mock_return_false_func())

    validator = InitValidator()
    args = argparse.Namespace()

    assert validator.validate(args) is False
    assert 0 < len(validator.errors)
    assert "Missing directories" in validator.errors[0]
    assert "Missing files" in validator.errors[1]


def test_submit_validator_missing_directories(mock_test_files: Mock, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ahc_local_leaderboard.consts.ROOT_DIR", Path("/fake"))

    monkeypatch.setattr(Path, "exists", mock_return_false_func())

    validator = SubmitValidator(mock_test_files)
    args = argparse.Namespace(command="submit")

    assert validator.validate(args) is False
    assert len(validator.errors) > 0
    assert "Missing directories" in validator.errors[0]


def test_submit_validator_missing_files(mock_test_files: Mock, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("ahc_local_leaderboard.consts.ROOT_DIR", Path("/fake"))

    monkeypatch.setattr(CommandValidatorBase, "check_directories", mock_return_true_func())

    monkeypatch.setattr(Path, "exists", mock_return_false_func())

    validator = SubmitValidator(mock_test_files)
    args = argparse.Namespace(command="submit")

    assert validator.validate(args) is False
    assert len(validator.errors) > 0
    assert "Missing files" in validator.errors[0]


@pytest.mark.parametrize("detail", [None])
@pytest.mark.parametrize("column", ["id", "rank", "time", "abs", "rel"])
def test_summary_view_validator(mock_record_read_service: Mock, detail: Optional[str], column: str) -> None:

    validator = ViewValidator(mock_record_read_service)
    args = argparse.Namespace(command="view", detail=detail, sort_column=column)  # ID 1は存在すると仮定

    assert validator.validate(args) is True
    assert validator.errors == []


@pytest.mark.parametrize("detail", ["1", "latest", "top"])
@pytest.mark.parametrize("column", ["id", "abs", "rel"])
def test_detail_view_validator(mock_record_read_service: Mock, detail: Optional[str], column: str) -> None:

    validator = ViewValidator(mock_record_read_service)
    args = argparse.Namespace(command="view", detail=detail, sort_column=column)  # ID 1は存在すると仮定

    assert validator.validate(args) is True
    assert validator.errors == []


def test_view_validator_invalid_id(mock_record_read_service: Mock) -> None:

    validator = ViewValidator(mock_record_read_service)
    args = argparse.Namespace(command="view", detail="2", sort_column="id")  # ID 2は存在しないと仮定

    assert validator.validate(args) is False
    assert len(validator.errors) > 0
    assert "Record not found in the database: id = 2" in validator.errors[0]


def test_view_validator_invalid_option(mock_record_read_service: Mock) -> None:

    validator = ViewValidator(mock_record_read_service)
    args = argparse.Namespace(command="view", detail="invalid_option", sort_column="id")

    assert validator.validate(args) is False
    assert len(validator.errors) > 0
    assert "Invalid argument for 'view --detail' option: invalid_option" in validator.errors[0]


def test_view_validator_invalid_latest_option(mock_record_read_service: Mock) -> None:

    validator = ViewValidator(mock_record_read_service)
    args = argparse.Namespace(command="view", detail="latest", sort_column="id")

    mock_record_read_service.fetch_total_record_count.return_value = 0

    assert validator.validate(args) is False
    assert len(validator.errors) > 0
    assert "No records found in the database" in validator.errors[0]


def test_view_validator_invalid_summary_sort_column_option(mock_record_read_service: Mock) -> None:

    validator = ViewValidator(mock_record_read_service)
    args = argparse.Namespace(command="view", detail=None, sort_column="invalid_option")

    assert validator.validate(args) is False
    assert len(validator.errors) > 0
    assert "Invalid argument for 'view --sort-column' option:" in validator.errors[0]


def test_view_validator_invalid_detail_sort_column_option(mock_record_read_service: Mock) -> None:

    validator = ViewValidator(mock_record_read_service)
    args = argparse.Namespace(command="view", detail="latest", sort_column="invalid_option")

    assert validator.validate(args) is False
    assert len(validator.errors) > 0
    assert "Invalid argument for 'view --sort-column' option:" in validator.errors[0]
