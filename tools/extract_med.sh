#!/bin/bash

# Usage:
#
# ./eval_med_gq.sh
#

if [ ! -f MED/MED.tsv ]; then
  echo "no MED.tsv file. Try:"
  echo "git clone https://github.com/verypluming/MED.git"
  # echo "cd MED"
  # echo "cp MED.tsv <parsing_comp directory>"
  exit 1
fi

# Create med_gq.tsv
cat MED/MED.tsv | grep paper \
                | grep -v GLUE \
                | grep -v FraCaS \
                | grep -v crowd \
                > med_gq.tsv

sick="med_gq.tsv"

plain_dir="med_plain"

# Extract training and test data from SICK dataset, removing the header line.
if [ ! -d ${plain_dir} ]; then
  mkdir -p ${plain_dir}
fi

echo "Extracting problems from the MED file."
cat $sick | \
tr -d '\r' | \
awk -F'\t' -v tdir=${plain_dir} \
  '{pair_id=$1;
    id=NR;
    premise=toupper(substr($9,0,1))substr($9,2,length($9));
    conclusion=toupper(substr($10,0,1))substr($10,2,length($10));
    if($4 ~ /lexical/){tag="gqlex"} else {tag="gq"}
    if($16 == "contradiction"){
      judgement="no";
    } else if ($16 == "entailment") {
      judgement="yes";
    } else if ($16 == "neutral") {
      judgement="unknown";
    }
    printf "%s\n%s\n", premise, conclusion > tdir"/med_"id"_"tag".txt";
    printf "%s\n", judgement > tdir"/med_"id"_"tag".answer";
   }'

# Copy all files to fracas_plain (for evaluation by eval_fracas.sh)
cp med_plain/* fracas_plain/
