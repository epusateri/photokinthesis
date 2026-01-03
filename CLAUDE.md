# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**photokinthesis** is a Python package built with modern Python tooling using `uv` for dependency management and `hatchling` as the build backend.

## Development Setup

This project uses `uv` for package and dependency management:

```bash
# Set up development environment
uv sync

# Install package in editable mode
uv pip install -e .
```

## CLI Usage

The package provides a command-line interface via the `photokinthesis` command:

```bash
# Reorganize FastFoto output files
photokinthesis reorganize --fast-foto-dir <input_dir> --output-dir <output_dir>
```

### `reorganize` Command

Reorganizes files from FastFoto scanning software output into a structured format:
- `basename.jpg` → `<output_dir>/fronts/`
- `basename_a.jpg` → `<output_dir>/enhanced_fronts/`
- `basename_b.jpg` → `<output_dir>/backs/`

**Collision Handling**: If multiple files have the same basename (from different subdirectories), they are renamed consistently across all output directories using numeric suffixes (e.g., `photo_0.jpg`, `photo_1.jpg`).

**Requirements**: Output directories must be empty or non-existent.

## Package Structure

- `src/photokinthesis/__init__.py` - Package initialization
- `src/photokinthesis/cli.py` - CLI implementation using Typer
- `src/photokinthesis/utils.py` - Core utility functions
- Package version is defined in both `pyproject.toml` and `src/photokinthesis/__init__.py`

## Build System

- **Build backend**: hatchling
- **Python requirement**: >=3.8
- **Dependencies**: typer[all] for CLI functionality

## Key Notes

- Uses `uv.lock` for dependency locking (excluded from git via `.gitignore`)
- No test suite currently exists
