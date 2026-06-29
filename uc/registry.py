"""YAML-based unit registry loader."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
from typing import Optional

import yaml

from uc.converter import ConversionGraph


def load_registry(data_dir: Path | None = None, graph: Optional[ConversionGraph] = None) -> ConversionGraph:
    """Load unit definitions from YAML files and build a ConversionGraph.

    Args:
        data_dir: Directory containing YAML unit definition files.
                 If None, uses the package's built-in data directory.
        graph: Optional ConversionGraph instance to populate. If None,
               a new ConversionGraph with the default search algorithm is created.

    Returns:
        ConversionGraph with all units and conversions loaded.

    Example:
        >>> unit_registry = load_registry()
        >>> from uc import Quantity
        >>> result = unit_registry.convert(Quantity(100, "cm"), "m")
        >>> result.value
        1.0
    """
    if graph is None:
        graph = ConversionGraph()

    if data_dir is None:
        data_dir = Path(__file__).parent / "data"

    # Load all YAML files in the data directory
    yaml_files = sorted(data_dir.glob("*.yaml"))

    for yaml_file in yaml_files:
        _load_yaml_file(graph, yaml_file)

    return graph


def _load_yaml_file(graph: ConversionGraph, yaml_file: Path) -> None:
    """Load a single YAML file containing unit definitions.

    Args:
        graph: ConversionGraph to populate.
        yaml_file: Path to YAML file.
    """
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    dimension = data.get("dimension")
    if not dimension:
        raise ValueError(f"Missing 'dimension' in {yaml_file}")

    # Register all units
    for unit_name in data.get("units", []):
        graph.add_unit(unit_name, dimension)

    # Add conversions
    for conv in data.get("conversions", []):
        _add_conversion(graph, conv)


def _add_conversion(graph: ConversionGraph, conv: Dict[str, Any]) -> None:
    """Add a single conversion to the graph based on YAML specification.

    Args:
        graph: ConversionGraph to add conversion to.
        conv: Dictionary with conversion specification.
    """
    u_from = conv["from"]
    u_to = conv["to"]
    conv_type = conv["type"]

    if conv_type == "linear":
        scale = conv["scale"]
        graph.add_linear(u_from, u_to, scale=scale)

    elif conv_type == "affine":
        scale = conv["scale"]
        offset = conv["offset"]
        graph.add_affine(u_from, u_to, scale=scale, offset=offset)

    else:
        raise ValueError(f"Unknown conversion type: {conv_type}")
