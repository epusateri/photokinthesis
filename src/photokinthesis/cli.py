"""Command-line interface for photokinthesis."""

from pathlib import Path
import typer
from typing_extensions import Annotated

from photokinthesis.utils import reorganize_fast_foto, deduplicate_photos
from photokinthesis.collections import init_collection
from photokinthesis.facial_recognition import recognize_faces

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


@app.command(name="init-collection")
def init_collection_cmd(
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
    collection_name: Annotated[
        str,
        typer.Option(
            "--collection-name",
            help="Name of the collection",
        ),
    ],
    collection_xmp_dir: Annotated[
        Path,
        typer.Option(
            "--collection-xmp-dir",
            help="Root directory for collection XMP files",
        ),
    ],
    collection_image_dir: Annotated[
        Path,
        typer.Option(
            "--collection-image-dir",
            help="Root directory for collection image files",
        ),
    ],
    tag: Annotated[
        list[str],
        typer.Option(
            "--tag",
            help="XMP tag in format 'namespace:name=value' (e.g., 'dc:creator=John Doe'). Can be specified multiple times.",
        ),
    ] = None,
) -> None:
    """Initialize a new photo collection with XMP metadata."""
    typer.echo(f"Initializing collection: {collection_name}")
    typer.echo(f"Source directory: {reorganized_dir}")
    typer.echo(f"Image directory: {collection_image_dir}")
    typer.echo(f"XMP directory: {collection_xmp_dir}")

    # Parse tags from key=value format
    tags_dict = {}
    if tag:
        for tag_str in tag:
            if "=" not in tag_str:
                typer.echo(f"Error: Tag must be in format 'key=value', got: {tag_str}")
                raise typer.Exit(1)
            key, value = tag_str.split("=", 1)
            tags_dict[key] = value
            typer.echo(f"  Tag: {key} = {value}")

    init_collection(
        reorganized_dir, collection_name, collection_xmp_dir, collection_image_dir, tags_dict
    )

    typer.echo("\nCollection initialized successfully!")


@app.command(name="recognize-faces")
def recognize_faces_cmd(
    collection_xmp_dir: Annotated[
        Path,
        typer.Option(
            "--collection-xmp-dir",
            help="Root directory for collection XMP files",
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
        ),
    ],
    collection_name: Annotated[
        str,
        typer.Option(
            "--collection-name",
            help="Name of the collection",
        ),
    ],
    collection_image_dir: Annotated[
        Path,
        typer.Option(
            "--collection-image-dir",
            help="Root directory for collection image files",
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
        ),
    ],
) -> None:
    """Detect faces in collection images and add face regions to XMP metadata."""
    typer.echo(f"Recognizing faces in collection: {collection_name}")
    typer.echo(f"XMP directory: {collection_xmp_dir}")
    typer.echo(f"Image directory: {collection_image_dir}")

    recognize_faces(collection_xmp_dir, collection_name, collection_image_dir)

    typer.echo("\nFace recognition complete!")


@app.command()
def serve(
    collection_xmp_dir: Annotated[
        Path,
        typer.Option(
            "--collection-xmp-dir",
            help="Root directory for collection XMP files",
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
        ),
    ],
    collection_image_dir: Annotated[
        Path,
        typer.Option(
            "--collection-image-dir",
            help="Root directory for collection image files",
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
        ),
    ],
    host: Annotated[
        str,
        typer.Option(
            "--host",
            help="Host to bind the web server to",
        ),
    ] = "0.0.0.0",
    port: Annotated[
        int,
        typer.Option(
            "--port",
            help="Port to run the web server on",
        ),
    ] = 5000,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug/--no-debug",
            help="Enable debug mode",
        ),
    ] = False,
) -> None:
    """Start the web GUI server for browsing photo collections."""
    from photokinthesis.web.app import create_app

    typer.echo(f"Starting Photokinthesis web server...")
    typer.echo(f"XMP directory: {collection_xmp_dir}")
    typer.echo(f"Image directory: {collection_image_dir}")
    typer.echo(f"Server: http://{host}:{port}")
    typer.echo(f"\nPress Ctrl+C to stop the server\n")

    app = create_app(collection_xmp_dir, collection_image_dir)
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    app()
