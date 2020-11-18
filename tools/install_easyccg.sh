#!/bin/bash
#
# Download EasyCCG parser
#
# Usage
# ./tools/install_easyccg.sh

easyccg_url="https://github.com/mikelewis0/easyccg.git"

models_id=0B7AY6PGZ8lc-dUN4SDcxWkczM2M
parser_basename=`basename $easyccg_url`
models_basename=model.tar.gz

if [ ! -d easyccg ]; then
  git clone $easyccg_url
  curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=${models_id}" > /dev/null
  CODE="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"  
  curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${CODE}&id=${models_id}" -o $models_basename

  tar -zxvf $models_basename --directory easyccg
  parser_dir=`pwd`"/"easyccg
  echo "Setting scripts/parser_location.txt pointing to ${parser_dir}"
  echo "easyccg:"$parser_dir >> scripts/parser_location.txt
  rm -f $parser_basename $models_basename
fi
