#!/bin/bash

# Usage:
#
# ./tools/setting_hans.sh
#

hans="hans/heuristics_evaluation_set.txt"
plain_dir="hans_plain"

if [ ! -d hans ]; then
  git clone https://github.com/tommccoy1/hans.git
fi

# Set test data from HANS dataset, removing the header line.
if [ ! -d ${plain_dir} ]; then
    mkdir -p ${plain_dir}
    echo "Extracting problems from the HANS test file."
    cat $hans | \
	awk 'NR > 1' | \
	tr -d '\r' | \
	awk -F'\t' -v tdir=${plain_dir} \
	    '{id=NR;
	      premise=toupper(substr($6,0,1))substr($6,2,length($6));
	      conclusion=toupper(substr($7,0,1))substr($7,2,length($7));
	      tag=$9;
	      if($1 == "non-entailment") {
	      	    judgement="unknown";
	      } else if ($1 == "entailment") {
	      	    judgement="yes";
	      }
	      printf "%s\n%s\n", premise, conclusion > tdir"/hans_"id"_"tag".txt";
	      printf "%s\n", judgement > tdir"/hans_"id"_"tag".answer";
	      }'
fi

# Copy all files to fracas_plain (for evaluation by eval_fracas.sh)
# cp hans_plain/* fracas_plain/
cp hans_plain/*lexical_overlap* fracas_plain/
cp hans_plain/*subsequence* fracas_plain/
cp hans_plain/*constituent* fracas_plain/
