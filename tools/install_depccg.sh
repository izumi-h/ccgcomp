#!/bin/bash
#
# Download depccg parsers
#
# Usage
# ./tools/install_depccg.sh

depccg_url="https://github.com/masashi-y/depccg.git"

if [ ! -d ../depccg ] && [ ! -d depccg ]; then
  git clone $depccg_url
  pip install cython numpy depccg
  depccg_en download
  echo "Setting scripts/parser_location.txt pointing to depccg"
  echo "depccg:" >> scripts/parser_location.txt
  rm -f $parser_basename $models_basename
fi
