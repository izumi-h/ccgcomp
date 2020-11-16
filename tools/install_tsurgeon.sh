#!/bin/bash
#
# Download Tsurgeon (Version 3.9.2)
# from https://nlp.stanford.edu/software/tregex.html
#

tregex_url="https://nlp.stanford.edu/software/stanford-tregex-2018-10-16.zip"
tregex_basename=`basename $tregex_url`

if [ ! -d stanford-tregex-2018-10-16 ]; then
  curl -LO $tregex_url
  unzip $tregex_basename
fi

# Set path to stanford-tregex-2018-10-16 directory
tregex_dir=`pwd`"/"stanford-tregex-2018-10-16
echo $tregex_dir > scripts/tregex_location.txt

rm -f $tregex_basename
