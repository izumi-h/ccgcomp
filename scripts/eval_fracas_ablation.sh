#!/bin/bash

# This script evaluates semantic templates on the FraCaS test suite.
#
# Usage:
#  ./scripts/eval_fracas_ablation.sh <nbest> <ncore> <option> <templates> <list of section numbers>
#
# Example:
# ./scripts/eval_fracas_ablation.sh 1 3 semantic_templates_en_comparatives.yaml tsurgeon 5 6
#
# FraCaS section number:
#                                                single-
# sec   topic            start   count     %     premise
# ---   -----------      -----   -----   -----   -------
#  1    Quantifiers         1      80     23 %      50
#  2    Plurals            81      33     10 %      24
#  3    Anaphora          114      28      8 %       6
#  4    Ellipsis          142      55     16 %      25
#  5    Adjectives        197      23      7 %      15
#  6    Comparatives      220      31      9 %      16
#  7    Temporal          251      75     22 %      39
#  8    Verbs             326       8      2 %       8
#  9    Attitudes         334      13      4 %       9
#
#  10   cad-Adjectives
#  11   cad-Adverbs
#  12   cad-Comparatives
#
#  13   med-gq
#  14   med-gqlex
#
#  15   hans-lexical_overlap
#  16   hans-subsequence
#  17   hans-constituent


# Set nbest
nbest=$1
# Set the number of processing cores
ncore=$2
# Set the name of semantic templates
templates=$3
# Set the option of ablation experiment:
# {normal:1, tsurgeon:2, abduction:3, rule:4, implicature:5}
option=$4
if [ $option = "original" ]; then
    echo "Experimental setting: original"
    op=1
elif [ $option = "tsurgeon" ]; then
    echo "Experimental setting: original + tsurgeon"
    op=2
elif [ $option = "abduction" ]; then
    echo "Experimental setting: original + tsurgeon + abduction"
    op=3
elif [ $option = "rule" ]; then
    echo "Experimental setting: original + tsurgeon + abduction + rule"
    op=4
elif [ $option = "implicature" ]; then
    echo "Experimental setting: original + tsurgeon + abduction + rule + implicature"
    op=5
else
  echo "Error: Select the option for the ablation experiment."
fi

sec=$(echo ${@:5} | sed 's/ /-/g')


plain_dir="fracas_plain"
cache_dir="cache"
results_dir="en_results"

if [ ! -e $results_dir ]; then
  mkdir -p $results_dir
fi

# Generate a list of fracas inference problems
ls -v ${plain_dir}/fracas_*.txt > ${plain_dir}/fracas.files
ls -v ${plain_dir}/cad_*.txt >> ${plain_dir}/fracas.files
ls -v ${plain_dir}/med_*.txt >> ${plain_dir}/fracas.files
ls -v ${plain_dir}/hans_*.txt >> ${plain_dir}/fracas.files

rm -f ${plain_dir}/fracas.sec.files

for section_number in ${@:5}; do
  if [ ${section_number} -eq 1 ]; then
    cat ${plain_dir}/fracas.files | grep generalized_quantifiers >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 2 ]; then
    cat ${plain_dir}/fracas.files | grep plurals >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 3 ]; then
    cat ${plain_dir}/fracas.files | grep anaphora >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 4 ]; then
    cat ${plain_dir}/fracas.files | grep ellipsis >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 5 ]; then
    cat ${plain_dir}/fracas.files | grep adjectives >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 6 ]; then
    cat ${plain_dir}/fracas.files | grep comparatives >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 7 ]; then
    cat ${plain_dir}/fracas.files | grep temporal >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 8 ]; then
    cat ${plain_dir}/fracas.files | grep verbs >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 9 ]; then
    cat ${plain_dir}/fracas.files | grep attitudes >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 10 ]; then
    cat ${plain_dir}/fracas.files | grep cad | grep adjective >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 11 ]; then
    cat ${plain_dir}/fracas.files | grep cad | grep adverb >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 12 ]; then
    cat ${plain_dir}/fracas.files | grep cad | grep comparative >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 13 ]; then
    cat ${plain_dir}/fracas.files | grep med | grep gq | grep -v gqlex >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 14 ]; then
    cat ${plain_dir}/fracas.files | grep med | grep gqlex >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 15 ]; then
    cat ${plain_dir}/fracas.files | grep hans | grep lexical_overlap >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 16 ]; then
    cat ${plain_dir}/fracas.files | grep hans | grep subsequence >> ${plain_dir}/fracas.sec.files
  fi
  if [ ${section_number} -eq 17 ]; then
    cat ${plain_dir}/fracas.files | grep hans | grep constituent >> ${plain_dir}/fracas.sec.files
  fi
done

nfracas=`cat ${plain_dir}/fracas.sec.files | wc -l`
fracas_lines_per_split=`python -c "from math import ceil; print(int(ceil(float(${nfracas})/${ncore})))"`

rm -f ${plain_dir}/fracas.files_??
split -l $fracas_lines_per_split ${plain_dir}/fracas.sec.files ${plain_dir}/fracas.files_

for ff in ${plain_dir}/fracas.files_??; do
  for f in `cat ${ff}`; do
    # ./scripts/rte.sh $f $templates $nbest;
    # ./scripts/rte_neg.sh $f $templates $nbest;
    ./scripts/rte_neg_ablation.sh $f $templates $op $nbest;
  done &
done

wait

date=$(date +%Y-%m-%d_%H:%M:%S)
accuracy=$(cat ${results_dir}/score_section${sec}.${option}.txt | head -n 15 | awk -F'|' '$0 ~ "total"{print $2}' | sed 's/[ ]*//g')

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
<ul>
<li>"$date"
<li>Accuracy : "$accuracy"</li>
</ul>
<tr>
  <td>id</td>
  <td>problem</td>
  <td>gold answer</td>
  <td>system answer</td>
  <td>C&C</td>
  <td>EasyCCG</td>
  <td>depccg</td>
</tr>" > ${results_dir}/main_section${sec}.${option}.html

red_color="rgb(255,0,0)"
green_color="rgb(0,255,0)"
white_color="rgb(255,255,255)"
gray_color="rgb(136,136,136)"

function display() {
  section=$1
  for gold_filename in ${plain_dir}/${section}.answer; do
    base_filename=${gold_filename##*/}
    sentences=$(cat ${plain_dir}/${base_filename/.answer/.txt} | sed 's/$/<br>/g')
    gold_answer=`cat $gold_filename`
    echo '<tr>
    <td>'${base_filename/.answer/}'</td>
    <td>'${sentences}'</td>
    <td>'$gold_answer'</td>' >> ${results_dir}/main_section${sec}.${option}.html
    for parser in "" "candc." "easyccg." "depccg."; do
      res=${results_dir}/${base_filename/.answer/.txt}.${option}.${parser}answer
      if [ -e "$res" -a -s "$res" ]; then
        system_answer=`cat ${results_dir}/${base_filename/.answer/.txt}.${option}.${parser}answer`
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
      echo '<td><a style="background-color:'$color';" href="'${base_filename/.answer/.txt}.${option}.${parser}html'">'$system_answer'</a>' >> ${results_dir}/main_section${sec}.${option}.html
    done
    echo '</tr>' >> ${results_dir}/main_section${sec}.${option}.html
  done
}

# Collect results and print accuracies.
function calculate_score() {
  section=$1
  for f in ${cache_dir}/${section}.txt.tok; do
    filename=${f##*/}
    base_filename=${filename/.txt.tok/}
    num_lines=`cat $f | wc -l`
    premises="single"
    if [ "$num_lines" -gt 2 ]; then
      premises="multi"
    fi
    gold_answer=`cat ${plain_dir}/${base_filename}.answer`
    system_answer=`cat ${results_dir}/${base_filename}.txt.${option}.answer`
    candc_answer=`cat ${results_dir}/${base_filename}.txt.${option}.candc.answer`
    easyccg_answer=`cat ${results_dir}/${base_filename}.txt.${option}.easyccg.answer`
    depccg_answer=`cat ${results_dir}/${base_filename}.txt.${option}.depccg.answer`
    echo $base_filename $premises $gold_answer >> gold.results
    echo $base_filename $premises $system_answer >> system.results
    echo $base_filename $premises $candc_answer >> candc.results
    echo $base_filename $premises $easyccg_answer >> easyccg.results
    echo $base_filename $premises $depccg_answer >> depccg.results
  done
}

function evaluate() {
  section=$1
  display $section
  calculate_score $section
}

for section_number in ${@:5}; do
  if [ ${section_number} -eq 1 ]; then
    evaluate "fracas_*_generalized_quantifiers"
  fi
  if [ ${section_number} -eq 2 ]; then
    evaluate "fracas_*_plurals"
  fi
  if [ ${section_number} -eq 3 ]; then
    evaluate "fracas_*_nominal_anaphora"
  fi
  if [ ${section_number} -eq 4 ]; then
    evaluate "fracas_*_ellipsis"
  fi
  if [ ${section_number} -eq 5 ]; then
    evaluate "fracas_*_adjectives"
  fi
  if [ ${section_number} -eq 6 ]; then
    evaluate "fracas_*_comparatives"
  fi
  if [ ${section_number} -eq 7 ]; then
    evaluate "fracas_*_temporal_reference"
  fi
  if [ ${section_number} -eq 8 ]; then
    evaluate "fracas_*_verbs"
  fi
  if [ ${section_number} -eq 9 ]; then
    evaluate "fracas_*_attitudes"
  fi
  if [ ${section_number} -eq 10 ]; then
    evaluate "cad_*_adjective"
  fi
  if [ ${section_number} -eq 11 ]; then
    evaluate "cad_*_adverb"
  fi
  if [ ${section_number} -eq 12 ]; then
    evaluate "cad_*_comparative"
  fi
  if [ ${section_number} -eq 13 ]; then
    evaluate "med_*_gq"
  fi
  if [ ${section_number} -eq 14 ]; then
    evaluate "med_*_gqlex"
  fi
  if [ ${section_number} -eq 15 ]; then
    evaluate "hans_*_lexical_overlap"
  fi
  if [ ${section_number} -eq 16 ]; then
    evaluate "hans_*_subsequence"
  fi
  if [ ${section_number} -eq 17 ]; then
    evaluate "hans_*_constituent"
  fi
done

echo "
</body>
</html>
" >> ${results_dir}/main_section"${sec}.${option}".html

score="${results_dir}/score_section${sec}.${option}.txt"

echo ${date} > $score
echo "----------------------------------------------------------------------------" \
 >> $score
echo -e "Multi-parsers:" >> $score
python scripts/report_results.py gold.results system.results >> $score
echo "----------------------------------------------------------------------------" \
 >> $score
echo -e "C&C:" >> $score
python scripts/report_results.py gold.results candc.results >> $score
echo "----------------------------------------------------------------------------" \
 >> $score
echo -e "EasyCCG:" >> $score
python scripts/report_results.py gold.results easyccg.results >> $score
echo "----------------------------------------------------------------------------" \
 >> $score
echo -e "depccg:" >> $score
python scripts/report_results.py gold.results depccg.results >> $score

cat $score

rm -f gold.results system.results candc.results easyccg.results depccg.results
