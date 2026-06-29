import pytest

from uc.converter import Quantity, ConversionGraph
from uc.registry import load_registry


@pytest.fixture(scope="session")
def full_registry() -> ConversionGraph:
    """Fixture for integration/system tests - full registry from YAML files."""
    return load_registry()


@pytest.mark.parametrize(
    "from_value,from_unit,to_unit,expected_value",
    [
        # Length
        (1000, "mm", "m", 1.0),
        (1, "km", "cm", 100000.0),

        # Temperature
        (0, "C", "F", 32.0),
        (100, "C", "F", 212.0),

        # Mass
        (1, "kg", "g", 1000.0),
        (1, "kg", "mg", 1000000.0),
    ],
    ids=[
        "length_mm_to_m",
        "length_km_to_cm_path",
        "temp_C_to_F_freezing",
        "temp_C_to_F_boiling",
        "mass_kg_to_g",
        "mass_kg_to_mg_path",
    ]
)
def test_registry_integration_conversions(
        full_registry,
        from_value,
        from_unit,
        to_unit,
        expected_value,
):
    """Test that registry loader properly integrates with converter for all unit types."""
    result = full_registry.convert(Quantity(from_value, from_unit), to_unit)
    assert result.value == pytest.approx(expected_value)
    assert result.unit == to_unit
