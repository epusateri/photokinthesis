#!/bin/bash
THIS_DIR=$(dirname $(readlink -f $0))


# collection_name=phase_0_tiny
# collections_image_dn=$THIS_DIR/../images
# uv run photokinthesis serve \
#     --collection-xmp-dir $THIS_DIR/../collections \
#     --collection-image-dir "$collections_image_dn" \
#     --port 8000


collection_name=phase_0
collections_image_dn="/Users/ernie/Library/CloudStorage/GoogleDrive-erniep@gmail.com/My Drive/photokinthesis/collections"
uv run photokinthesis serve \
    --collection-xmp-dir $THIS_DIR/../collections \
    --collection-image-dir "$collections_image_dn" \
    --port 8000
