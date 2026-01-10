from pathlib import Path

import typer

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


if __name__ == "__main__":
    pk()
