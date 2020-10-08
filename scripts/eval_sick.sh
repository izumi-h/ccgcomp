#!/bin/bash

# Usage:
#
# ./eval_sick.sh <ncores> <split> <templates.yaml>
#
# Example:
#
# ./eval_sick.sh 10 train scripts/semantic_template_event.yaml
#

# ccg2lambda=$(cat ccg2lambda_dir.txt)
ccg2lambda="ccg2lambda"
sick=${ccg2lambda}/SICK.semeval.txt

# How many processes in parallel you want to run.
# The maximum number should be inferior to the number of cores in your machine.
# Default: 3
cores=${1:-3}
# Split of the data (default train):
#   train (4439 problems),
#   test (4906 problems),
#   trial (495 problems).
dataset=${2:-"train"}
templates=$3

if [ ! -f $sick ]; then
  echo "Error: File for SICK dataset does not exist!"
  exit 1
fi

plain_dir="sick_plain"
results_dir="en_results"

# Extract training and test data from SICK dataset, removing the header line.
if [ ! -d ${plain_dir} ]; then
  mkdir -p ${plain_dir}

  echo "Extracting problems from the SICK file."
  tail -n +2 $sick | \
  tr -d '\r' | \
  awk -F'\t' -v tdir=${plain_dir} \
    '{pair_id=$1;
      sub(/\.$/,"",$2);
      sub(/\.$/,"",$3);
      premise=$2;
      conclusion=$3;
      if($5 == "CONTRADICTION"){
        judgement="no";
      } else if ($5 == "ENTAILMENT") {
        judgement="yes";
      } else if ($5 == "NEUTRAL") {
        judgement="unknown";
      }
      set=$NF;
      printf "%s.\n%s.\n", premise, conclusion > tdir"/sick_"tolower(set)"_"pair_id".txt";
      printf "%s\n", judgement > tdir"/sick_"tolower(set)"_"pair_id".answer";
     }'
fi

# Create files that list all filenames of training, testing and trial.
for dset in {train,test,trial}; do
  ls -v ${plain_dir}/sick_${dset}_*.txt > ${plain_dir}/sick_${dset}.files
done
# Split filename entries into several files, for parallel processing:
ntrain=`cat ${plain_dir}/sick_train.files | wc -l`
ntest=`cat ${plain_dir}/sick_test.files | wc -l`
ntrial=`cat ${plain_dir}/sick_trial.files | wc -l`
train_lines_per_split=`python -c "from math import ceil; print(int(ceil(float(${ntrain})/${cores})))"`
test_lines_per_split=`python -c "from math import ceil; print(int(ceil(float(${ntest})/${cores})))"`
trial_lines_per_split=`python -c "from math import ceil; print(int(ceil(float(${ntrial})/${cores})))"`

rm -f ${plain_dir}/sick_{train,test,trial}.files_??
split -l $train_lines_per_split ${plain_dir}/sick_train.files ${plain_dir}/sick_train.files_
split -l $test_lines_per_split ${plain_dir}/sick_test.files ${plain_dir}/sick_test.files_
split -l $trial_lines_per_split ${plain_dir}/sick_trial.files ${plain_dir}/sick_trial.files_

# Run pipeline for each entailment problem.
for ff in ${plain_dir}/sick_${dataset}.files_??; do
  for f in `cat ${ff}`; do
    # ./scripts/rte.sh $f $templates;
    ./scripts/rte_neg.sh $f $templates;
  done &
done

# Wait for the parallel processes to finish.
wait

total=0
correct=0
for f in ${plain_dir}/sick_${dataset}_*.answer; do
  let total++
  base_filename=${f##*/}
  sys_filename=${results_dir}/${base_filename/.answer/.txt.answer}
  gold_answer=`head -1 $f`
  if [ ! -e ${sys_filename} ]; then
    sys_answer="unknown"
  else
    sys_answer=`head -1 ${sys_filename}`
    if [ ! "${sys_answer}" == "unknown" ] && [ ! "${sys_answer}" == "yes" ] && [ ! "${sys_answer}" == "no" ]; then
      sys_answer="unknown"
    fi
  fi
  if [ "${gold_answer}" == "${sys_answer}" ]; then
    let correct++
  fi
  echo -e $f"\t"$gold_answer"\t"$sys_answer
done

accuracy=`echo "scale=3; $correct / $total" | bc -l`
echo "Accuracy: "$correct" / "$total" = "$accuracy

# Print a summary (precision, recall, f-score) of the errors at individual problems,
# per problem category and a global score.
echo "Evaluating."
echo "<!doctype html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <title>Evaluation results of "$category_templates"</title>
  <style>
    body {
      font-size: 1.5em;
    }
  </style>
</head>
<body>
<table border='1'>
<tr>
  <td>sick problem</td>
  <td>gold answer</td>
  <td>system answer</td>
  <td>C&C</td>
  <td>EasyCCG</td>
  <td>depccg</td>
</tr>" > $results_dir/main_sick.html

red_color="rgb(255,0,0)"
green_color="rgb(0,255,0)"
white_color="rgb(255,255,255)"
gray_color="rgb(136,136,136)"

for gold_filename in `ls -v ${plain_dir}/sick_${dataset}_*.answer`; do
  base_filename=${gold_filename##*/} # this line obtains the filename, without the directory path.
  system_filename=${results_dir}/${base_filename/.answer/.txt.answer}
  gold_answer=`cat $gold_filename`
  echo '<tr>
  <td>'${base_filename/.answer/}'</td>
  <td>'$gold_answer'</td>' >> $results_dir/main_sick.html
  for parser in "" "candc." "easyccg." "depccg."; do 
    if [ -e ${results_dir}/${base_filename/.answer/.txt}.${parser}answer ]; then
      system_answer=`cat ${results_dir}/${base_filename/.answer/.txt}.${parser}answer`
      time_filename=${results_dir}/${base_filename/.answer/.txt.time}
    else
      system_answer="error"
    fi
    color=$white_color
    if [ "$gold_answer" == "yes" ] || [ "$gold_answer" == "no" ]; then
      if [ "$gold_answer" == "$system_answer" ]; then
        color=$green_color
      else
        color=$red_color
      fi
    elif [ "$system_answer" == "yes" ] || [ "$system_answer" == "no" ]; then
      color=$red_color
    else
      color=$white_color
    fi
    echo '<td><a style="background-color:'$color';" href="'${base_filename/.answer/.txt}.${parser}html'">'$system_answer'</a>' >> $results_dir/main_sick.html
  done
  echo '</tr>' >> $results_dir/main_sick.html
done

# Collect results and print accuracies.
for f in ${plain_dir}/sick_${dataset}*.txt; do
  filename=${f##*/}
  base_filename=${filename/.txt/}
  num_lines=`cat $f | wc -l`
  premises="single"
  if [ "$num_lines" -gt 2 ]; then
    premises="multi"
  fi
  gold_answer=`cat ${plain_dir}/${base_filename}.answer`
  system_answer=`cat ${results_dir}/${base_filename}.txt.answer`
  candc_answer=`cat ${results_dir}/${base_filename}.txt.candc.answer`
  easyccg_answer=`cat ${results_dir}/${base_filename}.txt.easyccg.answer`
  depccg_answer=`cat ${results_dir}/${base_filename}.txt.depccg.answer`
  echo $base_filename $premises $gold_answer >> gold.results
  echo $base_filename $premises $system_answer >> system.results
  echo $base_filename $premises $candc_answer >> candc.results
  echo $base_filename $premises $easyccg_answer >> easyccg.results
  echo $base_filename $premises $depccg_answer >> depccg.results
done

echo -e "Multi-parsers:" > ${results_dir}/score.txt
python ${ccg2lambda}/report_results_sick.py gold.results system.results >> ${results_dir}/score.txt
echo -e "C&C:" >> ${results_dir}/score.txt
python ${ccg2lambda}/report_results_sick.py gold.results candc.results >> ${results_dir}/score.txt
echo -e "EasyCCG:" >> ${results_dir}/score.txt
python ${ccg2lambda}/report_results_sick.py gold.results easyccg.results >> ${results_dir}/score.txt
echo -e "depccg:" >> ${results_dir}/score.txt
python ${ccg2lambda}/report_results_sick.py gold.results depccg.results >> ${results_dir}/score.txt

cat ${results_dir}/score.txt

rm -f gold.results system.results candc.results easyccg.results depccg.results
