#!/bin/bash
THIS_DIR=$(dirname $(readlink -f $0))

cd "$THIS_DIR/.."
uv run pk serve --port 8000
