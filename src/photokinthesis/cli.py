from pathlib import Path

import typer
import uvicorn

from photokinthesis.collection import Collection

pk = typer.Typer(no_args_is_help=True)


@pk.callback()
def main() -> None:
    pass


@pk.command()
def init_collection_from_fast_foto(
    fast_foto_dir: Path = typer.Option(..., "--fast-foto-dir"),
    output_dir: Path = typer.Option(..., "--output-dir"),
    name: str = typer.Option(..., "--name"),
) -> None:
    """Initialize a collection from a FastFoto directory."""
    collection = Collection.read_fast_foto_tree(fast_foto_dir, name)
    collection.write(output_dir)


@pk.command()
def serve(
    port: int = typer.Option(8000, "--port", "-p"),
) -> None:
    """Start the web server."""
    uvicorn.run("photokinthesis.web.app:app", host="127.0.0.1", port=port, reload=True)


if __name__ == "__main__":
    pk()
