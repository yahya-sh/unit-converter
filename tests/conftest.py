import pytest

from uc.converter import ConversionGraph


@pytest.fixture(scope="class", params=["bfs", "dfs"])
def unit_registry(request) -> ConversionGraph:
    """Fixture for unit tests - minimal registry."""
    g = ConversionGraph(search_algo=request.param)
    g.add_unit("m", "length")
    g.add_unit("cm", "length")
    g.add_unit("mm", "length")
    g.add_unit("mi", "length")
    g.add_unit("km", "length")
    g.add_linear("m", "cm", scale=100.0)
    g.add_linear("cm", "mm", scale=10.0)
    g.add_linear("mi", "km", scale=1.60934)
    return g


@pytest.fixture
def temp_registry_dir(tmp_path):
    """Create a temporary registry directory for testing."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Create a simple test registry
    length_yaml = data_dir / "length.yaml"
    length_yaml.write_text("""
dimension: length
units:
  - m
  - cm
conversions:
  - from: m
    to: cm
    type: linear
    scale: 100.0
""")

    return data_dir
