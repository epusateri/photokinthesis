#!/bin/bash
THIS_DIR=$(dirname $(readlink -f $0))


dedup_var=phase_0
collection_name=phase_0
collections_image_dn="/Users/ernie/Library/CloudStorage/GoogleDrive-erniep@gmail.com/My Drive/photokinthesis/collections"
uv run photokinthesis init-collection \
   --reorganized-dir $THIS_DIR/../output/dedup/$dedup_var/output \
   --collection-name phase_0 \
   --tag "dc:source=Ellen (Deichler) Pusateri" \
   --collection-xmp-dir $THIS_DIR/../collections \
   --collection-image-dir "$collections_image_dn"

