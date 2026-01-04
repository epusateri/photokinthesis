#!/bin/bash
THIS_DIR=$(dirname $(readlink -f $0))


# collection_name=phase_0_tiny
# collections_image_dn=$THIS_DIR/../images
# uv run photokinthesis recognize-faces \
#    --collection-xmp-dir $THIS_DIR/../collections \
#    --collection-image-dir "$collections_image_dn" \
#    --collection-name $collection_name \


collection_name=phase_0
collections_image_dn="/Users/ernie/Library/CloudStorage/GoogleDrive-erniep@gmail.com/My Drive/photokinthesis/collections"
uv run photokinthesis recognize-faces \
   --collection-xmp-dir $THIS_DIR/../collections \
   --collection-image-dir "$collections_image_dn" \
   --collection-name $collection_name \

   
