from typing import Optional

from rich.color import Color
from rich.highlighter import ReprHighlighter
from rich.style import Style
from rich.text import Text

from ahc_local_leaderboard.view.color_interpolator import ColorInterpolator


class ScoreFormatter:
    """スコアの見た目を整形する専用クラス"""

    DEFAULT_STYLE = Style(color="white")
    ERROR_STYLE = Style(color="red", bold=True)

    LOW_SCORE_COLOR = Style(color="red1").color
    MEDIUM_SCORE_COLOR = Style(color="yellow1").color
    HIGH_SCORE_COLOR = Style(color="green1").color

    @staticmethod
    def format_optional_int(value: Optional[int]) -> Text:
        return Text(
            str(value), style=ScoreFormatter.DEFAULT_STYLE if isinstance(value, int) else ScoreFormatter.ERROR_STYLE
        )

    @staticmethod
    def format_total_absolute_score(total_absolute_score: int, invalid_score_count: int = 0) -> Text:
        """Total Absolute Scoreの表示を調整"""

        assert 0 <= total_absolute_score
        assert 0 <= invalid_score_count

        abs_score_text = Text(str(total_absolute_score), style=ScoreFormatter.DEFAULT_STYLE)

        if invalid_score_count > 0:
            abs_score_text.append(f" ({invalid_score_count})", style=ScoreFormatter.ERROR_STYLE)
        return abs_score_text

    @staticmethod
    def format_absolute_score(absolute_score: Optional[int]) -> Text:
        """絶対スコアの表示を生成します"""
        return ScoreFormatter.format_optional_int(absolute_score)

    @staticmethod
    def get_relative_score_color(relative_score: int, max_score: int, threshold_ratio: float = 0.9) -> Color:
        """relative_score の値に応じて赤→黄色→緑のグラデーションを生成する関数。

        AHC では可能な限り top_score に近いスコアを目指すため、スコアが大きいほど
        色の変化が強調されるように、指数補間を用いてグラデーションを生成しています。
        """

        assert 0 <= relative_score <= max_score
        assert 0 <= threshold_ratio <= 1

        color_thr = max_score * threshold_ratio

        if color_thr == 0:
            return ScoreFormatter.HIGH_SCORE_COLOR

        # スコアがしきい値以下の場合は赤→黄色、しきい値以上の場合は黄色→緑のグラデーション
        if relative_score <= color_thr:
            t = relative_score / color_thr
            return ColorInterpolator.exponential_color_interpolate(
                ScoreFormatter.LOW_SCORE_COLOR, ScoreFormatter.MEDIUM_SCORE_COLOR, t
            )
        else:
            t = (relative_score - color_thr) / (max_score - color_thr)
            return ColorInterpolator.exponential_color_interpolate(
                ScoreFormatter.MEDIUM_SCORE_COLOR, ScoreFormatter.HIGH_SCORE_COLOR, t
            )

    @staticmethod
    def format_relative_score(relative_score: int, max_score: int) -> Text:
        """相対スコアの表示をグラデーションカラーで整形"""
        assert 0 <= relative_score <= max_score
        relative_score_color = ScoreFormatter.get_relative_score_color(relative_score, max_score)
        return Text(str(relative_score), style=Style(color=relative_score_color))

    @staticmethod
    def format_score_diff(absolute_score: Optional[int], top_score: Optional[int]) -> Text:
        """トップスコアとの差分の表示を生成します"""

        if absolute_score is not None and top_score is not None:
            # スコアの最小化問題か最大化問題化で正負が変わるので絶対値をとっておく
            score_difference = abs(absolute_score - top_score)
        else:
            score_difference = None

        return ScoreFormatter.format_optional_int(score_difference)

    @staticmethod
    def format_test_case_input(test_case_input: str) -> Text:
        """Test Case Inputをフォーマットする"""

        input_text = Text(test_case_input)
        # ReprHighlighter がいい感じにHighliteしてくれている気がする
        highlighter = ReprHighlighter()
        highlighter.highlight(input_text)
        return input_text
