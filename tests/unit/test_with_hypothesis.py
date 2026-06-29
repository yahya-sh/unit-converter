from hypothesis import given, strategies as st

from uc.converter import ConversionGraph, Quantity


@given(
    from_value=st.floats(),
    from_unit=st.sampled_from(["m", "cm", "mm", "km"]),
    to_unit=st.sampled_from(["m", "cm", "mm", "km"]),
)
def test_linear_conversion(from_value, from_unit, to_unit):
    print(f"{from_value=} {from_unit=} {to_unit=}")
    unit_registry = ConversionGraph()

    unit_registry.add_unit("km", "length")
    unit_registry.add_unit("m", "length")
    unit_registry.add_unit("cm", "length")
    unit_registry.add_unit("mm", "length")

    unit_registry.add_linear("m", "cm", scale=100.0)
    unit_registry.add_linear("cm", "mm", scale=10.0)
    unit_registry.add_linear("km", "mm", scale=1000000)

    from_quantity = Quantity(from_value, unit=from_unit)
    unit_registry.convert(from_quantity, to_unit=to_unit)
