from uc.cli import app


def test_cli_basic_conversion(runner):
    """Test complete system: CLI input -> registry -> converter -> output."""
    result = runner.invoke(app, ["100000", "cm", "km"])
    assert result.exit_code == 0
    assert "1.0" in result.stdout


def test_cli_unknown_unit_error(runner):
    """Test system error handling for unknown units."""
    result = runner.invoke(app, ["100", "xyz", "m"])
    assert result.exit_code == 1
    assert "Error" in result.stderr
