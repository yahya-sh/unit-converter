"""Command-line interface for unit conversion."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from uc.converter import Quantity
from uc.registry import load_registry

app = typer.Typer(help="Unit Conversion CLI - Convert between different units")


@app.command()
def convert(
        value: float = typer.Argument(..., help="Value to convert"),
        from_unit: str = typer.Argument(..., help="Source unit"),
        to_unit: str = typer.Argument(..., help="Target unit"),
        data_dir: Optional[Path] = typer.Option(None, "--data-dir", help="Custom unit registry directory"),
) -> None:
    """Convert a value from one unit to another.

    Example:
        units-convert 100 cm m
        units-convert 32 F C
    """
    try:
        # Load registry
        graph = load_registry(data_dir=data_dir)

        # Perform conversion
        quantity = Quantity(value, from_unit)
        result = graph.convert(quantity, to_unit)

        typer.echo(f"{result.value}")

    except KeyError as e:
        typer.echo(f"Error: Unknown unit - {e}", err=True)
        raise typer.Exit(code=1)

    except TypeError as e:
        typer.echo(f"Error: Incompatible units - {e}", err=True)
        raise typer.Exit(code=1)

    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
