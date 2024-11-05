import re

from rich.text import Text


class ScoreFormatter:
    """スコアの見た目を整形する専用クラス"""

    @staticmethod
    def format_total_absolute_score(total_absolute_score, invalid_score_count=0):
        """Total Absolute Scoreの表示を調整"""
        abs_score_text = Text(str(total_absolute_score), style="white")
        if invalid_score_count > 0:
            abs_score_text.append(f" ({invalid_score_count})", style="bold red")
        return abs_score_text

    @staticmethod
    def format_absolute_score(absolute_score):
        """絶対スコアの表示を生成します"""
        return Text(str(absolute_score), style="white" if str(absolute_score).isdigit() else "red")

    @staticmethod
    def exponential_interpolation(start, end, t):
        """指数関数的な補間を実行する関数"""
        return int(start + (end - start) * (t ** 2))

    @staticmethod
    def get_gradient_color(relative_score, max_score):
        """relative_score の値に応じて赤→黄色→緑のグラデーションを生成する関数"""
        color_thr = max_score * 0.9

        if relative_score <= color_thr:
            # 0 ~ color_thr は赤→黄色
            t = relative_score / color_thr
            red = 255
            green = ScoreFormatter.exponential_interpolation(0, 255, t)
            blue = 0
        else:
            # color_thr ~ max_score は黄色→緑
            t = (relative_score - color_thr) / (max_score - color_thr)
            red = ScoreFormatter.exponential_interpolation(255, 0, t)
            green = 255
            blue = 0

        return f"rgb({int(red)},{int(green)},{int(blue)})"
    
    @staticmethod
    def format_relative_score(relative_score, max_score):
        """相対スコアの表示をグラデーションカラーで整形"""
        relative_score_color = ScoreFormatter.get_gradient_color(relative_score, max_score)
        return Text(str(relative_score), style=relative_score_color)

    @staticmethod
    def format_score_diff(absolute_score, top_score):
        """トップスコアとの差分の表示を生成します"""
        score_difference = abs(absolute_score - top_score) if absolute_score is not None and top_score is not None else "None"
        return Text(str(score_difference), style="white" if str(score_difference).isdigit() else "red")

    @staticmethod
    def format_test_case_input(test_case_input):
        """Test Case Inputの数値部分を青色でフォーマットする"""
        input_text = Text()
        for part in re.split(r'(\d+|\.)', test_case_input):
            if part.isdigit() or part == '.':
                input_text.append(part, style="bold cyan")
            else:
                input_text.append(part, style="white")
        return input_text
