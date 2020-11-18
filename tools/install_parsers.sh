#!/bin/bash
#
# Download C&C, EasyCCG, and depccg parsers
#
# Usage
# ./tools/install_parsers.sh <option>
#
candc_url_linux="https://drive.google.com/uc?id=1MAqE0RmAC1sOW6A9ErpQcFmFbzD66i7x"
candc_url_mac="https://drive.google.com/uc?id=1vl9rwQDqhy5dmt8D8EnEPTGw9zqK0KSz"

if [ "$1" = "mac" ]; then
  candc_url=$candc_url_mac
elif [ "$1" = "linux" ]; then
  candc_url=$candc_url_linux
else
  echo 'Please choose `mac` or `linux` in $1.'
  exit
fi

# models_url="https://drive.google.com/uc?id=1LR6h3rX7a4Dq7fV_bc2mEmeYxteSyenH"
models_id=1LR6h3rX7a4Dq7fV_bc2mEmeYxteSyenH
parser_basename=`basename $candc_url`
# models_basename=`basename $models_url`
models_basename=models-1.02.tgz

test -d candc-1.00 || {
  test -f $parser_basename || {
    wget $candc_url
  }

  # test -f $models_url || {
  #     wget $models_url
  # }

  curl -sc /tmp/cookie "https://drive.google.com/uc?export=download&id=${models_id}" > /dev/null
  CODE="$(awk '/_warning_/ {print $NF}' /tmp/cookie)"  
  curl -Lb /tmp/cookie "https://drive.google.com/uc?export=download&confirm=${CODE}&id=${models_id}" -o $models_basename

  tar xvzf $parser_basename
  tar xvzf $models_basename --directory candc-1.00
  parser_dir=`pwd`"/"candc-1.00
  echo "Setting scripts/parser_location.txt pointing to ${parser_dir}"
  echo "candc:"$parser_dir > scripts/parser_location.txt
  rm -f $parser_basename $models_basename
}


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

depccg_url="https://github.com/masashi-y/depccg.git"

if [ ! -d ../depccg ] && [ ! -d depccg ]; then
  git clone $depccg_url
  pip install cython numpy depccg
  depccg_en download
  echo "Setting scripts/parser_location.txt pointing to depccg"
  echo "depccg:" >> scripts/parser_location.txt
  rm -f $parser_basename $models_basename
fi
