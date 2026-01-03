"""Command-line interface for photokinthesis."""

from pathlib import Path
import typer
from typing_extensions import Annotated

from photokinthesis.utils import reorganize_fast_foto, deduplicate_photos

app = typer.Typer(
    help="photokinthesis - Photo organization toolkit",
    no_args_is_help=True,
)


@app.callback()
def main():
    """photokinthesis - Photo organization toolkit."""
    pass


@app.command()
def reorganize(
    fast_foto_dir: Annotated[
        Path,
        typer.Option(
            "--fast-foto-dir",
            help="Directory containing outputs from FastFoto scanning software",
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            help="Directory where reorganized files will be written",
        ),
    ],
) -> None:
    """Reorganize FastFoto output files into a structured format."""
    typer.echo(f"Processing FastFoto directory: {fast_foto_dir}")
    typer.echo(f"Output directory: {output_dir}")

    reorganize_fast_foto(fast_foto_dir, output_dir)

    typer.echo("Reorganization complete!")


@app.command()
def dedup(
    reorganized_dir: Annotated[
        Path,
        typer.Option(
            "--reorganized-dir",
            help="Directory containing fronts/, enhanced_fronts/, and backs/ subdirectories",
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            help="Directory where deduplicated files will be written",
        ),
    ],
    duplicates_dir: Annotated[
        Path,
        typer.Option(
            "--duplicates-dir",
            help="Directory where duplicate files will be written for review",
        ),
    ],
    threshold: Annotated[
        int,
        typer.Option(
            "--threshold",
            help="Hash difference threshold for detecting duplicates (0=exact matches only, higher=more sensitive, recommend 5-10)",
        ),
    ] = 5,
) -> None:
    """Remove duplicate images using perceptual hashing."""
    typer.echo(f"Processing reorganized directory: {reorganized_dir}")
    typer.echo(f"Output directory: {output_dir}")
    typer.echo(f"Duplicates directory: {duplicates_dir}")
    typer.echo(f"Threshold: {threshold}")

    stats = deduplicate_photos(reorganized_dir, output_dir, duplicates_dir, threshold)

    typer.echo(f"\nDeduplication complete!")
    typer.echo(f"Total images processed: {stats['total']}")
    typer.echo(f"Unique images kept: {stats['kept']}")
    typer.echo(f"Duplicates removed: {stats['duplicates']}")


if __name__ == "__main__":
    app()
