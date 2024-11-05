from rich.console import Console

class ConsoleHandler:
    console = Console()

    @staticmethod
    def print_error(message):
        """赤字のエラーメッセージを表示"""
        ConsoleHandler.console.print(f"[bold red]Error:[/] {message}")

    @staticmethod
    def print_success(message):
        """緑字の成功メッセージを表示"""
        ConsoleHandler.console.print(f"[bold green]{message}[/]")

    @staticmethod
    def print_info(message):
        """青字の情報メッセージを表示"""
        ConsoleHandler.console.print(f"[bold cyan]{message}[/]")

    @staticmethod
    def print_directive(command):
        """ユーザーが実行すべきコマンドの指示を表示"""
        ConsoleHandler.console.print("Please run the following command:", style="yellow")
        ConsoleHandler.console.print(f"  $ {command}", style="bold cyan")

    @staticmethod
    def print_directives(commands):
        """ユーザーが実行すべき複数のコマンドの指示を表示"""
        ConsoleHandler.console.print("Please run one of the following commands:", style="yellow")
        for command in commands:
            ConsoleHandler.console.print(f"  $ {command}", style="bold cyan")