#!/bin/bash
THIS_DIR=$(dirname $(readlink -f $0))

output_dn=$THIS_DIR/../output/reorganize

variation=phase_0

var_out_dn=$output_dn/$variation
mkdir -p $var_out_dn
fast_foto_dn="/Users/ernie/Library/CloudStorage/GoogleDrive-erniep@gmail.com/My Drive/Family Photos/"
uv run photokinthesis reorganize \
   --fast-foto-dir "$fast_foto_dn" \
   --output-dir $var_out_dn
