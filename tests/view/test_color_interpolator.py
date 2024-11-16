import pytest
from rich.color import Color

from ahc_local_leaderboard.view.color_interpolator import ColorInterpolator


@pytest.mark.parametrize("start", [-100000, -1, 0, 1, 100000])
@pytest.mark.parametrize("end", [-100000, -1, 0, 1, 100000])
def test_exponential_interpolation(start: int, end: int) -> None:
    assert ColorInterpolator.exponential_interpolation(start, end, 0) == start
    assert ColorInterpolator.exponential_interpolation(start, end, 1) == end

    previous_value = ColorInterpolator.exponential_interpolation(start, end, 0)

    for t in [i * 0.1 for i in range(1, 11)]:  # t = 0.1, 0.2, ..., 1.0
        current_value = ColorInterpolator.exponential_interpolation(start, end, t)

        if start < end:
            assert current_value >= previous_value
        else:
            assert current_value <= previous_value

        previous_value = current_value


@pytest.mark.parametrize("t", [-0.1, 1.1])
def test_exponential_interpolation_assertions(t: float) -> None:
    with pytest.raises(AssertionError):
        ColorInterpolator.exponential_interpolation(0, 100, t)


def test_exponential_color_interpolate() -> None:

    start_color = Color.from_rgb(255, 0, 0)
    end_color = Color.from_rgb(0, 255, 0)

    color_0 = ColorInterpolator.exponential_color_interpolate(start_color, end_color, 0)
    assert color_0.get_truecolor().red == start_color.get_truecolor().red
    assert color_0.get_truecolor().green == start_color.get_truecolor().green
    assert color_0.get_truecolor().blue == start_color.get_truecolor().blue

    color_50 = ColorInterpolator.exponential_color_interpolate(start_color, end_color, 0.5)
    assert 127 <= color_50.get_truecolor().red <= 255
    assert 0 <= color_50.get_truecolor().green <= 127
    assert color_50.get_truecolor().blue == 0

    color_100 = ColorInterpolator.exponential_color_interpolate(start_color, end_color, 1)
    assert color_100.get_truecolor().red == end_color.get_truecolor().red
    assert color_100.get_truecolor().green == end_color.get_truecolor().green
    assert color_100.get_truecolor().blue == end_color.get_truecolor().blue


@pytest.mark.parametrize("t", [-0.1, 1.1])
def test_exponential_color_interpolate_assertions(t: float) -> None:
    start_color = Color.from_rgb(255, 0, 0)
    end_color = Color.from_rgb(0, 255, 0)

    with pytest.raises(AssertionError):
        ColorInterpolator.exponential_interpolation(start_color, end_color, t)
