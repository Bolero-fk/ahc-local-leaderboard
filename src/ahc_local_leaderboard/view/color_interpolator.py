from rich.color import Color


class ColorInterpolator:
    """色の補間処理を提供するクラス。"""

    @staticmethod
    def exponential_interpolation(start: float, end: float, t: float) -> int:
        """二次関数的な補間を実行します。"""
        assert 0.0 <= t <= 1.0

        return int(start + (end - start) * (t**2))

    @staticmethod
    def exponential_color_interpolate(start_color: Color, end_color: Color, t: float) -> Color:
        """二つの色の間で、t の二乗に基づいた色補間を行います。"""
        assert 0.0 <= t <= 1.0

        r = ColorInterpolator.exponential_interpolation(
            start_color.get_truecolor().red, end_color.get_truecolor().red, t
        )
        g = ColorInterpolator.exponential_interpolation(
            start_color.get_truecolor().green, end_color.get_truecolor().green, t
        )
        b = ColorInterpolator.exponential_interpolation(
            start_color.get_truecolor().blue, end_color.get_truecolor().blue, t
        )

        return Color.from_rgb(r, g, b)
