from unittest.mock import Mock, patch

import pytest

from ahc_local_leaderboard.utils.console_handler import ConsoleHandler


@pytest.mark.parametrize("message", ["This is an error", "", "$%'-_@{}~`!#()'."])
@patch("ahc_local_leaderboard.utils.console_handler.ConsoleHandler.console.print")
def test_print_error(mock_print: Mock, message: str) -> None:
    ConsoleHandler.print_error(message)
    mock_print.assert_called_once_with(f"[bold red]Error:[/] {message}")


@pytest.mark.parametrize("message", ["This is a success", "", "$%'-_@{}~`!#()'."])
@patch("ahc_local_leaderboard.utils.console_handler.ConsoleHandler.console.print")
def test_print_success(mock_print: Mock, message: str) -> None:
    ConsoleHandler.print_success(message)
    mock_print.assert_called_once_with(f"[bold green]{message}[/]")


@pytest.mark.parametrize("message", ["This is an info message", "", "$%'-_@{}~`!#()'."])
@patch("ahc_local_leaderboard.utils.console_handler.ConsoleHandler.console.print")
def test_print_info(mock_print: Mock, message: str) -> None:
    ConsoleHandler.print_info(message)
    mock_print.assert_called_once_with(f"[bold cyan]{message}[/]")


@pytest.mark.parametrize("command", ["echo Hello", "", "$%'-_@{}~`!#()'."])
@patch("ahc_local_leaderboard.utils.console_handler.ConsoleHandler.console.print")
def test_print_directive(mock_print: Mock, command: str) -> None:
    ConsoleHandler.print_directive(command)
    mock_print.assert_any_call("Please run the following command:", style="yellow")
    mock_print.assert_any_call(f"  $ {command}", style="bold cyan")


@pytest.mark.parametrize("command1", ["echo Hello", "", "$%'-_@{}~`!#()'."])
@pytest.mark.parametrize("command2", ["echo World", "", "$%'-_@{}~`!#()'."])
@patch("ahc_local_leaderboard.utils.console_handler.ConsoleHandler.console.print")
def test_print_directives(mock_print: Mock, command1: str, command2: str) -> None:
    commands = [command1, command2]
    ConsoleHandler.print_directives(commands)
    mock_print.assert_any_call("Please run one of the following commands:", style="yellow")
    mock_print.assert_any_call(f"  $ {command1}", style="bold cyan")
    mock_print.assert_any_call(f"  $ {command2}", style="bold cyan")
