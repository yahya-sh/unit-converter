from __future__ import annotations

import warnings
from collections import deque
from dataclasses import dataclass
from typing import Dict, Tuple, Callable, Deque, Set, Iterable, Optional


@dataclass(frozen=True)
class Unit:
    """A named unit together with its physical dimension.

    Attributes:
        name: Canonical unit identifier (e.g., "m", "kg", "°C").
        dimension: Dimension group (e.g., "length", "mass", "temperature").
    """
    name: str
    dimension: str  # e.g., "length", "mass", "temperature"


@dataclass(frozen=True)
class Quantity:
    """A numeric value tagged with a unit name.

    Attributes:
        value: The numeric magnitude in the given unit.
        unit: The unit name (must be registered in the graph to convert).
    """
    value: float
    unit: str  # refer by unit name


class ConversionGraph:
    """Directed graph of unit conversions with automatic inverse edges.

    Each edge stores a callable `f(value: float) -> float` that maps a value
    from the source unit to the destination unit. Inverse edges are created
    automatically when adding a conversion.

    Dimension compatibility is enforced: you can only add conversions and
    convert between units of the same `dimension`.

    The `convert` method uses a graph search to find a valid conversion path.
    Edges that are not applicable for the current value (e.g., logarithmic
    conversions for non-positive inputs) are safely skipped during the search.

    Example:
        >>> g = ConversionGraph(search_algo="bfs")
        >>> g.add_unit("m", "length")
        >>> g.add_unit("cm", "length")
        >>> g.add_unit("mm", "length")
        >>> g.add_linear("m", "cm", scale=100.0)
        >>> g.add_linear("cm", "mm", scale=10.0)
        >>> g.convert(Quantity(2.5, "m"), "mm")
        Quantity(value=2500.0, unit='mm')
    """

    def __init__(self, search_algo: str = "bfs") -> None:
        # edges[(u_from, u_to)] = callable(value)->value
        self._edges: Dict[Tuple[str, str], Callable[[float], float]] = {}
        self._units: Dict[str, Unit] = {}

        if search_algo == "bfs":
            self._convert_value = self._bfs_convert_value
        elif search_algo == "dfs":
            self._convert_value = self._dfs_convert_value
        else:
            raise ValueError(f"Unknown search algorithm: {search_algo}")

    # ----- unit/edge registration -------------------------------------------------

    def add_unit(self, name: str, dimension: str) -> None:
        """Register a unit with a given dimension.

        If a unit with the same name already exists, its dimension must match.

        Args:
            name: Unit name to register.
            dimension: Dimension group name.

        Raises:
            ValueError: If the unit already exists with a different dimension.
        """
        if name in self._units:
            if self._units[name].dimension != dimension:
                raise ValueError(f"Unit '{name}' already exists with a different dimension.")
            return
        self._units[name] = Unit(name=name, dimension=dimension)

    def add_linear(self, u_from: str, u_to: str, scale: float) -> None:
        """Add a linear conversion with no offset: `to = scale * from`.

        Args:
            u_from: Source unit name.
            u_to: Destination unit name.
            scale: Multiplicative scale (non-zero).

        Raises:
            KeyError: If either unit is unknown.
            TypeError: If units have different dimensions.
            ValueError: If `scale == 0`.
        """
        self._assert_known_units(u_from, u_to)
        self._assert_same_dimension(u_from, u_to)
        if scale == 0:
            raise ValueError("Scale must be non-zero.")
        fwd = lambda x, s=scale: s * x
        inv = lambda y, s=scale: y / s
        self._add_pair(u_from, u_to, fwd, inv)

    def add_affine(self, u_from: str, u_to: str, scale: float, offset: float) -> None:
        """Add an affine conversion: `to = scale * from + offset`.

        Common for temperatures (e.g., °C ↔ K, °F ↔ °C).

        Args:
            u_from: Source unit name.
            u_to: Destination unit name.
            scale: Multiplicative scale (non-zero).
            offset: Additive offset in the destination unit.

        Raises:
            KeyError: If either unit is unknown.
            TypeError: If units have different dimensions.
            ValueError: If `scale == 0`.
        """
        self._assert_known_units(u_from, u_to)
        self._assert_same_dimension(u_from, u_to)
        if scale == 0:
            raise ValueError("Scale must be non-zero.")
        fwd = lambda x, a=scale, b=offset: a * x + b
        inv = lambda y, a=scale, b=offset: (y - b) / a
        self._add_pair(u_from, u_to, fwd, inv)

    # ----- core conversion --------------------------------------------------------

    def convert(self, q: Quantity, to_unit: str) -> Quantity:
        """Convert a quantity to a target unit using the configured search algorithm.

        The search explores all reachable conversions while skipping edges
        whose domain constraints are violated for the current value (e.g.,
        taking a logarithm of a non-positive number). If a path is found,
        the resulting value is returned in `to_unit`.

        Args:
            q: Input quantity (value and source unit).
            to_unit: Target unit name.

        Returns:
            A new `Quantity` with the converted value and `unit == to_unit`.

        Raises:
            KeyError: If either unit is unknown.
            TypeError: If units have different dimensions.
            ValueError: If no valid conversion path exists.
        """
        from_unit = q.unit
        if from_unit == to_unit:
            return q

        self._assert_convertible(from_unit, to_unit)

        result_value = self._convert_value(q.value, from_unit, to_unit)
        if result_value is None:
            raise ValueError(f"No conversion path found from '{from_unit}' to '{to_unit}'.")
        return Quantity(value=result_value, unit=to_unit)

    # ----- helpers ----------------------------------------------------------------

    def _add_pair(
            self,
            u_from: str,
            u_to: str,
            forward: Callable[[float], float],
            inverse: Callable[[float], float],
    ) -> None:
        """Install forward and inverse edges for a conversion pair.

        Overwrites any existing edges between the same pair.

        Args:
            u_from: Source unit name.
            u_to: Destination unit name.
            forward: Mapping u_from -> u_to.
            inverse: Mapping u_to -> u_from.
        """
        self._edges[(u_from, u_to)] = forward
        self._edges[(u_to, u_from)] = inverse

    def _assert_known_units(self, *names: str) -> None:
        """Ensure all given unit names are registered."""
        unknown = [n for n in names if n not in self._units]
        if unknown:
            raise KeyError(f"Unknown unit(s): {', '.join(unknown)}")

    def _assert_same_dimension(self, u1: str, u2: str) -> None:
        """Ensure two units belong to the same dimension group."""
        d1 = self._units[u1].dimension
        d2 = self._units[u2].dimension
        if d1 != d2:
            raise TypeError(f"Incompatible dimensions: '{u1}'({d1}) vs '{u2}'({d2})")

    def _assert_convertible(self, u_from: str, u_to: str) -> None:
        """Composite validation for a conversion request."""
        self._assert_known_units(u_from, u_to)
        self._assert_same_dimension(u_from, u_to)

    def _bfs_convert_value(self, value: float, u_from: str, u_to: str) -> Optional[float]:
        """Breadth-first search (BFS) over conversions to compute the target value.

        Args:
            value: Starting numeric value.
            u_from: Source unit name.
            u_to: Target unit name.

        Returns:
            Converted numeric value if a path is found; otherwise None.
        """
        queue: Deque[Tuple[str, float]] = deque([(u_from, value)])
        visited: Set[str] = {u_from}

        while queue:
            current_unit, current_value = queue.popleft()
            for neighbor, func in self._neighbors(current_unit):
                if neighbor in visited:
                    continue
                next_value = self._try_apply(func, current_value)
                if next_value is None:
                    continue
                if neighbor == u_to:
                    return next_value
                visited.add(neighbor)
                queue.append((neighbor, next_value))
        return None

    def _dfs_convert_value(self, value: float, u_from: str, u_to: str) -> Optional[float]:
        """Depth-first search (DFS) over conversions to compute the target value.

        Args:
            value: Starting numeric value.
            u_from: Source unit name.
            u_to: Target unit name.

        Returns:
            Converted numeric value if a path is found; otherwise None.
        """
        stack: list[Tuple[str, float]] = [(u_from, value)]
        visited: Set[str] = {u_from}

        while stack:
            current_unit, current_value = stack.pop()
            for neighbor, func in self._neighbors(current_unit):
                if neighbor in visited:
                    continue
                next_value = self._try_apply(func, current_value)
                if next_value is None:
                    continue
                if neighbor == u_to:
                    return next_value
                visited.add(neighbor)
                stack.append((neighbor, next_value))
        return None

    def _neighbors(self, unit: str) -> Iterable[Tuple[str, Callable[[float], float]]]:
        """Yield (neighbor_unit, edge_function) for all outgoing edges of `unit`."""
        for (src, dst), func in self._edges.items():
            if src == unit:
                yield dst, func

    @staticmethod
    def _try_apply(
            func: Callable[[float], float],
            value: float,
    ) -> Optional[float]:
        """Apply an edge function, returning None if it raises.

        This isolates domain-specific failures (e.g., log on non-positive)
        so the search algorithm can continue exploring other paths.

        Args:
            func: Edge callable to apply.
            value: Current value at the edge source.

        Returns:
            The transformed value, or None if the function raised.
        """
        try:
            return func(value)
        except Exception as e:  # noqa: BLE001
            warnings.warn(
                f"Conversion function {func.__name__ if hasattr(func, '__name__') else func} "
                f"failed for value {value!r}: {e}",
                RuntimeWarning,
                stacklevel=2,
            )
            return None
