import argparse
from pathlib import Path
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


def test_view_validator_valid(mock_record_read_service: Mock) -> None:

    validator = ViewValidator(mock_record_read_service)
    args = argparse.Namespace(command="view", detail="1")  # ID 1は存在すると仮定

    assert validator.validate(args) is True
    assert validator.errors == []


def test_view_validator_invalid_id(mock_record_read_service: Mock) -> None:

    validator = ViewValidator(mock_record_read_service)
    args = argparse.Namespace(command="view", detail="2")  # ID 2は存在しないと仮定

    assert validator.validate(args) is False
    assert len(validator.errors) > 0
    assert "Record not found in the database: id = 2" in validator.errors[0]


def test_view_validator_invalid_option(mock_record_read_service: Mock) -> None:

    validator = ViewValidator(mock_record_read_service)
    args = argparse.Namespace(command="view", detail="invalid_option")

    assert validator.validate(args) is False
    assert len(validator.errors) > 0
    assert "Invalid argument for 'view --detail' option: invalid_option" in validator.errors[0]
