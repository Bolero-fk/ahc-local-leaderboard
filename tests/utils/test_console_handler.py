from unittest.mock import Mock, patch

from ahc_local_leaderboard.utils.console_handler import ConsoleHandler


@patch("ahc_local_leaderboard.utils.console_handler.ConsoleHandler.console.print")
def test_print_error(mock_print: Mock) -> None:
    message = "This is an error"
    ConsoleHandler.print_error(message)
    mock_print.assert_called_once_with("[bold red]Error:[/] This is an error")


@patch("ahc_local_leaderboard.utils.console_handler.ConsoleHandler.console.print")
def test_print_success(mock_print: Mock) -> None:
    message = "This is a success"
    ConsoleHandler.print_success(message)
    mock_print.assert_called_once_with("[bold green]This is a success[/]")


@patch("ahc_local_leaderboard.utils.console_handler.ConsoleHandler.console.print")
def test_print_info(mock_print: Mock) -> None:
    message = "This is an info message"
    ConsoleHandler.print_info(message)
    mock_print.assert_called_once_with("[bold cyan]This is an info message[/]")


@patch("ahc_local_leaderboard.utils.console_handler.ConsoleHandler.console.print")
def test_print_directive(mock_print: Mock) -> None:
    command = "echo Hello"
    ConsoleHandler.print_directive(command)
    mock_print.assert_any_call("Please run the following command:", style="yellow")
    mock_print.assert_any_call("  $ echo Hello", style="bold cyan")


@patch("ahc_local_leaderboard.utils.console_handler.ConsoleHandler.console.print")
def test_print_directives(mock_print: Mock) -> None:
    commands = ["echo Hello", "echo World"]
    ConsoleHandler.print_directives(commands)
    mock_print.assert_any_call("Please run one of the following commands:", style="yellow")
    mock_print.assert_any_call("  $ echo Hello", style="bold cyan")
    mock_print.assert_any_call("  $ echo World", style="bold cyan")
