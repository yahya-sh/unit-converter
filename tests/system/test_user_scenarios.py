import pytest

from uc.cli import app

pytestmark = pytest.mark.acceptance


def test_user_can_check_weather_in_preferred_units(runner):
    """
    User Story: As a user, I want to convert the temperature between Celsius
    and Fahrenheit, so I can understand weather forecasts.
    """
    result = runner.invoke(app, ["25", "C", "F"])
    assert result.exit_code == 0
    assert "77.0" in result.stdout


def test_user_gets_clear_error_for_incompatible_units(runner):
    """
    User Story: As a user, I should get clear error messages when trying
    to convert between incompatible unit types.
    """
    result = runner.invoke(app, ["100", "m", "kg"])
    assert result.exit_code == 1
    assert "Error: " in result.stderr
