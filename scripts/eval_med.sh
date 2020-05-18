#!/bin/bash

# This script evaluates semantic templates on the MED dataset.
# MED has 1189 problems from med_1.txt to med_1189.txt
#
# Usage:
#  ./scripts/eval_med.sh <tag> <nbest> <templates> <start number> <end number>
#
# <tag> ::= gq | gqlex | all
#
# Example:
# ./scripts/eval_med.sh gq 1 scripts/semantic_templates.yaml 1 100

tag=$1
nbest=$2

# Set the name of semantic templates
templates=$3

startnum=$4
endnum=$5

plain_dir="med_plain"
cache_dir="cache"
results_dir="en_results"

if [ ! -e $results_dir ]; then
  mkdir -p $results_dir
fi

function proving() {
  id=$1
  label=$2
  if [ -f ${plain_dir}/med_${id}_${label}.txt ]; then
    ./scripts/rte.sh ${plain_dir}/med_${id}_${label}.txt $templates $nbest
  fi
}

# Display the result for each problem in a html file
echo "Evaluating."
echo "<!doctype html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <title>Evaluation results of "$templates" on FraCaS </title>
  <style>
    body {
      font-size: 1.5em;
    }
  </style>
</head>
<body>
<table border='1'>
<tr>
  <td>fracas problem</td>
  <td>gold answer</td>
  <td>system answer</td>
  <td>C&C</td>
  <td>depccg</td>
</tr>" > $results_dir/main_med.html

red_color="rgb(255,0,0)"
green_color="rgb(0,255,0)"
white_color="rgb(255,255,255)"
gray_color="rgb(136,136,136)"

function display() {
  id=$1
  label=$2
  if [ -f ${plain_dir}/med_${id}_${label}.answer ]; then
    gold_filename="${plain_dir}/med_${id}_${label}.answer"
    base_filename=${gold_filename##*/}
    gold_answer=`cat $gold_filename`
    echo '<tr>
    <td>'${base_filename/.answer/}'</td>
    <td>'$gold_answer'</td>' >> $results_dir/main_med.html
    for parser in "" "candc." "depccg."; do
      res=${results_dir}/${base_filename/.answer/.txt}.${parser}answer
      if [ -e "$res" -a -s "$res" ]; then
        system_answer=`cat ${results_dir}/${base_filename/.answer/.txt}.${parser}answer`
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
      elif [ "$system_answer" == "error" ]; then
        color=$gray_color
      elif [ "$system_answer" == "unknown" ] || [ "$system_answer" == "undef" ]; then
        color=$white_color
      fi
      echo '<td><a style="background-color:'$color';" href="'${base_filename/.answer/.txt}.${parser}html'">'$system_answer'</a>' >> $results_dir/main_med.html
    done
    echo '</tr>' >> $results_dir/main_med.html
  fi
}

count=1

# Collect results and print accuracies.
function calculate_score() {
  id=$1
  label=$2
  if [ -f ${cache_dir}/med_${id}_${label}.txt.tok ]; then
    count=$((count += 1))
    f="${cache_dir}/med_${id}_${label}.txt.tok"
    filename=${f##*/}
    base_filename=${filename/.txt.tok/}
    num_lines=`cat $f | wc -l`
    premises="single"
    if [ "$num_lines" -gt 2 ]; then
      premises="multi"
    fi
    gold_answer=`cat ${plain_dir}/${base_filename}.answer`
    system_answer=`cat ${results_dir}/${base_filename}.txt.answer`
    candc_answer=`cat ${results_dir}/${base_filename}.txt.candc.answer`
    depccg_answer=`cat ${results_dir}/${base_filename}.txt.depccg.answer`
    echo $base_filename $premises $gold_answer >> gold.results
    echo $base_filename $premises $system_answer >> system.results
    echo $base_filename $premises $candc_answer >> candc.results
    echo $base_filename $premises $depccg_answer >> depccg.results
  fi
}


for id in $(seq ${startnum} ${endnum}); do
  if [ ${tag} == "all" ]; then
    proving $id gq
    display $id gq
    calculate_score $id gq
    proving $id gqlex
    display $id gqlex
    calculate_score $id gqlex
  else
    proving $id $tag
    display $id $tag
    calculate_score $id $tag
  fi
done

echo "----------------------------------------------------------------------------" \
 > ${results_dir}/score.txt
echo -e "Number of problems: "$count >> ${results_dir}/score.txt

echo "
</body>
</html>
" >> $results_dir/main_med.html

echo "----------------------------------------------------------------------------" \
 >> ${results_dir}/score.txt
echo -e "Multi-parsers:" >> ${results_dir}/score.txt
python scripts/report_results_med.py gold.results system.results >> ${results_dir}/score.txt
echo "----------------------------------------------------------------------------" \
 >> ${results_dir}/score.txt
echo -e "C&C:" >> ${results_dir}/score.txt
python scripts/report_results_med.py gold.results candc.results >> ${results_dir}/score.txt
echo "----------------------------------------------------------------------------" \
 >> ${results_dir}/score.txt
echo -e "depccg:" >> ${results_dir}/score.txt
python scripts/report_results_med.py gold.results depccg.results >> ${results_dir}/score.txt

cat ${results_dir}/score.txt

rm -f gold.results system.results candc.results depccg.results
