import pytest

from uc.converter import ConversionGraph, Quantity

pytestmark = pytest.mark.regression


def test_zero_scale_raises_error():
    """
    Bug #001: System crashed when scale=0 was provided.
    Fixed in v0.0.2 by adding validation.
    """
    g = ConversionGraph()
    g.add_unit("m", "length")
    g.add_unit("cm", "length")

    with pytest.raises(ValueError, match="Scale must be non-zero"):
        g.add_linear("m", "cm", scale=0)


def test_dimension_mismatch_provides_clear_error():
    """
    Bug #002: Dimension errors showed confusing KeyError messages.
    Fixed in v0.0.5 with TypeError and clear dimension information.
    """
    g = ConversionGraph()
    g.add_unit("m", "length")
    g.add_unit("kg", "mass")

    with pytest.raises(TypeError, match="Incompatible dimensions"):
        g.convert(Quantity(10, "m"), "kg")
