#!/bin/bash
THIS_DIR=$(dirname $(readlink -f $0))

fast_foto_dn="/Users/ernie/Library/CloudStorage/GoogleDrive-erniep@gmail.com/My Drive/Family Photos"
collection_name="Ellen Pusateri's Photos"
collection_bn="ellen_pusateris_photos"
collection_version="0000"
# collections_dn="/Users/ernie/Library/CloudStorage/GoogleDrive-erniep@gmail.com/My Drive/photokinthesis/collections"
collections_dn=$THIS_DIR/../output/collections
uv run pk init-collection-from-fast-foto \
   --fast-foto-dir "$fast_foto_dn" \
   --name "$collection_name" \
   --output-dir "$collections_dn/$collection_bn/$collection_version"
