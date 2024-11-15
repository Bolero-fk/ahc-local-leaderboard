import tempfile
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from ahc_local_leaderboard.database.record_write_service import RecordWriteService
from ahc_local_leaderboard.init.initializer import Initializer
from ahc_local_leaderboard.utils.file_utility import FileUtility


@pytest.fixture
def mock_record_write_service() -> Mock:
    return Mock(spec=RecordWriteService)


@pytest.fixture
def mock_file_utility() -> Mock:
    return Mock(spec=FileUtility)


def test_create_directories(
    mock_record_write_service: Mock, mock_file_utility: Mock, monkeypatch: pytest.MonkeyPatch
) -> None:

    with tempfile.TemporaryDirectory() as temp_dir:
        monkeypatch.setattr("ahc_local_leaderboard.consts.ROOT_DIR", Path(temp_dir))

        initializer = Initializer(mock_record_write_service, mock_file_utility)
        initializer.create_directories()

        for directory in initializer.leader_board_directoris:
            mock_file_utility.try_create_directory.assert_any_call(str(directory))


@pytest.mark.parametrize("path_exists", [False, True])
def test_initialize_database(mock_record_write_service: Mock, mock_file_utility: Mock, path_exists: bool) -> None:

    initializer = Initializer(mock_record_write_service, mock_file_utility)

    mock_file_utility.path_exists.return_value = path_exists
    initializer.initialize_database()

    if path_exists:
        mock_record_write_service.setup_database.assert_not_called()
    else:
        mock_record_write_service.setup_database.assert_called_once()


@patch("builtins.input", side_effect=["1"])
def test_prompt_scoring_type_maximization(
    mock_input: Mock, mock_record_write_service: Mock, mock_file_utility: Mock
) -> None:

    initializer = Initializer(mock_record_write_service, mock_file_utility)
    result = initializer.prompt_scoring_type()
    assert result == "Maximization"


@patch("builtins.input", side_effect=["2"])
def test_prompt_scoring_type_minimization(
    mock_input: Mock, mock_record_write_service: Mock, mock_file_utility: Mock
) -> None:

    initializer = Initializer(mock_record_write_service, mock_file_utility)
    result = initializer.prompt_scoring_type()
    assert result == "Minimization"


@patch("builtins.input", side_effect=["3", "0", "abc", "a", "123", "2"])
def test_prompt_scoring_type_invalid_input(
    mock_input: Mock, mock_record_write_service: Mock, mock_file_utility: Mock
) -> None:

    initializer = Initializer(mock_record_write_service, mock_file_utility)
    result = initializer.prompt_scoring_type()
    assert result == "Minimization"


@patch("builtins.open", new_callable=mock_open)
def test_write_config_file(mock_open: Mock, mock_record_write_service: Mock, mock_file_utility: Mock) -> None:

    initializer = Initializer(mock_record_write_service, mock_file_utility)
    config_data = {"scoring_type": "Maximization"}
    with patch("yaml.dump") as mock_yaml_dump:
        initializer.write_config_file(config_data)

        mock_open.assert_called_once_with(initializer.config_path, "w")
        mock_yaml_dump.assert_called_once_with(config_data, mock_open())


@pytest.mark.parametrize("path_exists", [False, True])
def test_create_config_file(mock_record_write_service: Mock, mock_file_utility: Mock, path_exists: bool) -> None:
    initializer = Initializer(mock_record_write_service, mock_file_utility)

    mock_file_utility.path_exists.return_value = path_exists

    with patch.object(
        initializer,
        "prompt_scoring_type",
        return_value="Maximization",
    ) as mock_prompt, patch.object(initializer, "write_config_file", return_value=Mock()) as mock_write:

        initializer.create_config_file()

        if path_exists:
            mock_prompt.assert_not_called()
            mock_write.assert_not_called()
        else:
            mock_prompt.assert_called_once()
            mock_write.assert_called_once_with({"scoring_type": "Maximization"})


def test_execute(mock_record_write_service: Mock, mock_file_utility: Mock) -> None:
    initializer = Initializer(mock_record_write_service, mock_file_utility)

    with patch.object(
        initializer,
        "create_directories",
        return_value=Mock(),
    ) as mock_create_dir, patch.object(
        initializer, "initialize_database", return_value=Mock()
    ) as mock_init, patch.object(initializer, "create_config_file") as mock_create_config:

        initializer.execute()

        mock_create_dir.assert_called_once()
        mock_init.assert_called_once()
        mock_create_config.assert_called_once()
