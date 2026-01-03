#!/bin/bash
THIS_DIR=$(dirname $(readlink -f $0))

output_dn=$THIS_DIR/../output/dedup

variation=phase_0
reorganize_var=phase_0

var_out_dn=$output_dn/$variation
mkdir -p $var_out_dn/{duplicates,output}
uv run photokinthesis dedup \
   --threshold 1 \
   --reorganized-dir $THIS_DIR/../output/reorganize/$reorganize_var \
   --duplicates-dir $var_out_dn/duplicates \
   --output-dir $var_out_dn/output
