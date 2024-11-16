from rich.console import Console


class ConsoleHandler:
    """コンソールへのメッセージ表示を管理するクラス。"""

    console = Console()

    @staticmethod
    def print_error(message: str) -> None:
        """赤字のエラーメッセージを表示します。"""
        ConsoleHandler.console.print(f"[bold red]Error:[/] {message}")

    @staticmethod
    def print_success(message: str) -> None:
        """緑字の成功メッセージを表示します。"""
        ConsoleHandler.console.print(f"[bold green]{message}[/]")

    @staticmethod
    def print_info(message: str) -> None:
        """青字の情報メッセージを表示します。"""
        ConsoleHandler.console.print(f"[bold cyan]{message}[/]")

    @staticmethod
    def print_directive(command: str) -> None:
        """ユーザーが実行すべきコマンドの指示を表示します。"""
        ConsoleHandler.console.print("Please run the following command:", style="yellow")
        ConsoleHandler.console.print(f"  $ {command}", style="bold cyan")

    @staticmethod
    def print_directives(commands: list[str]) -> None:
        """ユーザーが実行すべき複数のコマンドの指示を表示します。"""
        ConsoleHandler.console.print("Please run one of the following commands:", style="yellow")
        for command in commands:
            ConsoleHandler.console.print(f"  $ {command}", style="bold cyan")
