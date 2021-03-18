#!/bin/bash

# Usage
USAGE="Usage: ./rte_neg_ablation.sh <sentences.txt> <semantic_templates.yaml> <option> <nbest>"

# Set the option of ablation experiment:
# {normal:1, tsurgeon:2, abduction:3, rule:4, implicature:5}
op=$3
if [ -z $op ]; then
  echo "Error: The number of the option of ablation experimen is specified."
  echo "normal:1, tsurgeon:2, abduction:3, rule:4, implicature:5"
  exit 1
fi
if [ $op -eq 1 ]; then
    # echo "Experimental setting: original"
    option="original"
elif [ $op -eq 2 ]; then
    # echo "Experimental setting: original + tsurgeon"
    option="tsurgeon"
elif [ $op -eq 3 ]; then
    # echo "Experimental setting: original + tsurgeon + abduction"
    option="abduction"
elif [ $op -eq 4 ]; then
    # echo "Experimental setting: original + tsurgeon + abduction + rule"
    option="rule"
elif [ $op -eq 5 ]; then
    # echo "Experimental setting: original + tsurgeon + abduction + rule + implicature"
    option="implicature"
else
    # echo "Error: Select an option number between 1 and 5 for the ablation experiment."
    option=""
fi
# Set the number of nbest parses (Default: 1)
nbest=${4:-1}

c2l_dir="ccg2lambda"
# c2l_dir=`cat ccg2lambda_dir.txt`

# Create a file named "parser_location.txt" at the "en" directory and
# write a list of CCG parsers installed, as in:
# $ cat en/parser_location.txt
# candc:/path/to/candc-1.00
# easyccg:/path/to/easyccg
# easysrl:/path/to/EasySRL
# depccg:

# Set tregex path:
# Create a file named "tregex_location.txt" at the "scripts" directory
# $ cat tregex_location.txt
# /Users/kojimineshima/stanford-tregex-2018-10-16
tregex_dir=`cat scripts/tregex_location.txt`
export CLASSPATH=$tregex_dir/stanford-tregex.jar:$CLASSPATH

# This variable contains the filename where the semantic templates are.
semantic_templates=$2
if [ ! -f $semantic_templates ]; then
  echo "Error: File with semantic templates does not exist."
  echo $USAGE
  exit 1
fi

# This variable contains the name of the dataset (fracas or jsem).
sentences_fname=$1
sentences_basename=${sentences_fname##*/}
if [ ! -f $sentences_fname ]; then
  echo "Error: File with plain sentences does not exist."
  echo $USAGE
  exit 1
fi

function timeout() { perl -e 'alarm shift; exec @ARGV' "$@"; }

# These variables contain the names of the directories where intermediate
# results will be written.

plain_dir="cache" # tokenized sentences.
parsed_dir="cache" # parsed sentences into XML or other formats.
results_dir="en_results" # HTML semantic outputs, proving results, etc.

mkdir -p $plain_dir $parsed_dir $results_dir

mkdir -p "tptp"

# Tokenize text with Penn Treebank tokenizer.
cat $sentences_fname | \
  sed -f ${c2l_dir}/tokenizer.sed | \
  sed 's/ _ /_/g' | \
  sed 's/[[:space:]]*$//' | \
  sed 's/ (//g' | \
  sed 's/) //g' \
  > ${plain_dir}/${sentences_basename}.tok

# Set parser locations
if [ ! -f "scripts/parser_location.txt" ]; then
  echo "Error: File for the locations of parsers does not exist."
  exit 1
fi
for parser in `cat scripts/parser_location.txt`; do
  parser_name=`echo $parser | awk -F':' '{print $1}'`
  parser_dir=`echo $parser | awk -F':' '{print $2}'`
  if [ "${parser_name}" == "candc" ]; then
    candc_dir=${parser_dir}
    if [ ! -d "${candc_dir}" ] || [ ! -e "${candc_dir}"/bin/candc ]; then
      echo "C&C parser directory incorrect. Exit."
      exit 1
    fi
  fi
  if [ "${parser_name}" == "easyccg" ]; then
    easyccg_dir=${parser_dir}
    if [ ! -d "${easyccg_dir}" ] || [ ! -e "${easyccg_dir}"/easyccg.jar ]; then
      echo "EasyCCG parser directory incorrect. Exit."
      exit 1
    fi
  fi
  if [ "${parser_name}" == "depccg" ]; then
    depccg_exists=`pip freeze | grep depccg`
    if [ "${depccg_exists}" == "" ]; then
      echo "depccg parser directory incorrect. Exit."
      exit 1
    fi
  fi
done

function parse_candc() {
  # Parse using C&C.
  base_fname=$1
  ${candc_dir}/bin/candc \
      --models ${candc_dir}/models \
      --candc-printer xml \
      --input ${plain_dir}/${base_fname}.tok \
    2> ${parsed_dir}/${base_fname}.${option}.log \
     > ${parsed_dir}/${base_fname}.${option}.candc.xml
  python -m depccg.tools.tagger --format jigg_xml ${parsed_dir}/${base_fname}.${option}.candc.xml \
    > ${parsed_dir}/${base_fname}.${option}.candc.init.jigg.xml \
    2> ${parsed_dir}/${base_fname}.${option}.log
}

function parse_easyccg() {
  # Parse using EasyCCG.
  base_fname=$1
  python scripts/call_spacy.py ${plain_dir}/${base_fname}.tok | \
  java -jar ${easyccg_dir}/easyccg.jar \
    --model ${easyccg_dir}/model \
    -i POSandNERtagged \
    -o extended \
    --maxLength 100 \
    --nbest "${nbest}" \
    > ${parsed_dir}/${base_fname}.${option}.easyccg.auto \
    2> ${parsed_dir}/${base_fname}.${option}.easyccg.log
  python ${c2l_dir}/easyccg2jigg.py \
    ${parsed_dir}/${base_fname}.${option}.easyccg.auto \
    ${parsed_dir}/${base_fname}.${option}.easyccg.init.jigg.xml \
    2> ${parsed_dir}/${base_fname}.${option}.easyccg.xml.log
}

function parse_depccg() {
    # Parse using depccg.
    base_fname=$1
    cat ${plain_dir}/${base_fname}.tok | \
    env CANDC=${candc_dir} depccg_en \
        --input-format raw \
        --annotator spacy \
        --nbest $nbest \
        --format jigg_xml \
    > ${parsed_dir}/${base_fname}.${option}.depccg.init.jigg.xml \
    2> ${parsed_dir}/${base_fname}.${option}.log
}

function tsurgeon() {
  parser=$1
  sentences_basename=$2
  tsurgeon=$3
  if [ -f ${parsed_dir}/${sentences_basename}.${option}.${parser}.init.jigg.xml ]; then
    python scripts/brackets_with_pos.py ${parsed_dir}/${sentences_basename}.${option}.${parser}.init.jigg.xml \
     > ${parsed_dir}/${sentences_basename}.${option}.${parser}.ptb
  fi
  java -mx100m edu.stanford.nlp.trees.tregex.tsurgeon.Tsurgeon -s \
       -treeFile ${parsed_dir}/${sentences_basename}.${option}.${parser}.ptb $tsurgeon
}

function semantic_parsing() {
  parser=$1
  sentences_basename=$2
  sentence=$(cat ${plain_dir}/${sentences_basename}.tok)
  if [ "`cat ${plain_dir}/${sentences_basename}.tok | grep -e " not " -e "n't " `" ]; then
    python ${c2l_dir}/semparse.py \
      $parsed_dir/${sentences_basename}.${option}.${parser}.jigg.xml \
      ./scripts/semantic_template_event_not.yaml \
      $parsed_dir/${sentences_basename}.${option}.neg.${parser}.sem.xml \
      --arbi-types \
      2> $parsed_dir/${sentences_basename}.${option}.neg.${parser}.sem.err
    cp $parsed_dir/${sentences_basename}.${option}.neg.${parser}.sem.xml $parsed_dir/${sentences_basename}.${option}.neg.${parser}.jigg.xml
  fi
  python ${c2l_dir}/semparse.py \
    $parsed_dir/${sentences_basename}.${option}.${parser}.jigg.xml \
    $semantic_templates \
    $parsed_dir/${sentences_basename}.${option}.${parser}.sem.xml \
    --arbi-types \
    2> $parsed_dir/${sentences_basename}.${option}.${parser}.sem.err
}

function proving() {
  parser=$1
  sentences_basename=$2
  if [ $op -ge 3 ]; then
      lex=lex
  else
      lex=nolex
  fi
  start_time=`python -c 'import time; print(time.time())'`
  timeout 100 python scripts/eval.py \
	  ${parsed_dir}/${sentences_basename}.${option}.${parser}.sem.xml \
	  --prover vampire --abduction $lex\
	  > ${results_dir}/${sentences_basename}.${option}.${parser}.answer \
	  2> ${results_dir}/${sentences_basename}.${option}.${parser}.err
  rte_answer=`cat ${results_dir}/${sentences_basename}.${option}.${parser}.answer`
  echo "judging entailment ${parsed_dir}/${sentences_basename}.${option}.${parser}.sem.xml $rte_answer"
  proof_end_time=`python -c 'import time; print(time.time())'`
  proving_time=`echo "${proof_end_time} - ${start_time}" | bc -l | \
       awk '{printf("%.2f\n",$1)}'`
  echo $proving_time > ${results_dir}/${sentences_basename}.${option}.time
}

function select_fname() {
  ans=$1
  for fname in ${results_dir}/${sentences_basename}.${option}.*{candc,easyccg,depccg}.answer; do
    fname_answer=`cat ${fname}`
    if [ "${fname_answer}" = "${ans}" ]; then
      prediction_fname=`echo ${fname##*/} | sed 's/.answer//g'`
    fi
  done
  echo $prediction_fname
}

function predict_answer() {
  yes=$1
  no=$2
  unk=$3
  if [ ${yes} -gt ${no} ]; then
    prediction_fname=$(select_fname "yes")
  elif [ ${no} -gt ${yes} ]; then
    prediction_fname=$(select_fname "no")
  else
    prediction_fname=$(select_fname "unknown")
  fi
  if [ ! -z "${prediction_fname}" ]; then
    cp ${parsed_dir}/${prediction_fname}.jigg.xml ${parsed_dir}/${sentences_basename}.${option}.xml
    cp ${parsed_dir}/${prediction_fname}.sem.xml ${parsed_dir}/${sentences_basename}.${option}.sem.xml
    cp ${results_dir}/${prediction_fname}.answer ${results_dir}/${sentences_basename}.${option}.answer
    cp ${results_dir}/${prediction_fname}.html ${results_dir}/${sentences_basename}.${option}.html
  fi
}

function add_feature_brackets(){
    sed 's/Sadv=true,pos=true/S[adv=true,pos=true]/g' \
  | sed 's/Sdcl/S[dcl]/g' \
  | sed 's/Sadj/S[adj]/g' \
  | sed 's/Sadv/S[adv]/g' \
  | sed 's/Sng/S[ng]/g' \
  | sed 's/Sto/S[to]/g' \
  | sed 's/Sem/S[em]/g' \
  | sed 's/Sqem/S[qem]/g' \
  | sed 's/Sb/S[b]/g' \
  | sed 's/Spss/S[pss]/g' \
  | sed 's/Sasup/S[asup]/g' \
  | sed 's/SX/S[X]/g' \
  | sed 's/Spt/S[pt]/g' \
  | sed 's/NPexpl/NP[expl]/g' \
  | sed 's/NPthr/NP[thr]/g' \
  | sed 's/NPnpi/NP[npi]/g' \
  | sed 's/NPdeg/NP[deg]/g' \
  | sed 's/NPadj/NP[adj]/g' \
  | sed 's/NPnb/NP[nb]/g' \
  | sed 's/Nadj=true,pos=true/N[adj=true,pos=true]/g' \
  | sed 's/Nadj/N[adj]/g' \
  | sed 's/Nnum/N[num]/g' \
  | sed 's/Ndown/N[down]/g' \
  | sed 's/Nnm/N[nm]/g'
}

# Set the current answer
current_answer="unknown"
prediction_fname="${sentences_basename}.${option}.candc"

yes=0
no=0
unk=0

# CCG parsing, semantic parsing and theorem proving
for parser in `cat scripts/parser_location.txt`; do
    parser_name=`echo $parser | awk -F':' '{print $1}'`
    parser_dir=`echo $parser | awk -F':' '{print $2}'`
    if [ ! -e ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.init.jigg.xml ]; then
	echo "${parser_name} parsing ${plain_dir}/${sentences_basename}"
	parse_$parser_name $sentences_basename
    fi
    
    # Apply tsurgeon script
    if [ $op -ge 2 ]; then
	if [ ! -e ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.jigg.xml ]; then
	    echo "execute tsurgeon ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.ptb"

	    if [ $op -ge 4 ]; then
		python scripts/change_tags.py ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.init.jigg.xml
		tsurgeon $parser_name $sentences_basename scripts/transform.tsgn \
			 > ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.tsgn.ptb
		if [ $op -eq 5 ]; then
		    java -mx100m edu.stanford.nlp.trees.tregex.tsurgeon.Tsurgeon -s \
		    	 -treeFile ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.tsgn.ptb scripts/transform_imp.tsgn \
			 > ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.tsgn.imp.ptb
		    mv ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.tsgn.imp.ptb ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.tsgn.ptb
		fi
	    else
		python scripts/change_tags_-rule.py ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.init.jigg.xml
		tsurgeon $parser_name $sentences_basename scripts/transform_-rule.tsgn \
			 > ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.tsgn.ptb
	    fi
	
	    # cat ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.tsgn.ptb \
		#   | sed 's/</(/g' | sed 's/>/)/g' \
		#   | add_feature_brackets \
		#   | sed -e 's/;[,_A-Z-]*\$*//g' \
		#   | sed 's/\.\./\./g' \
		#   > ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.tsgn.mod.ptb
	    cat ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.tsgn.ptb \
		| sed -e 's/\((\|\\\|\/\|<\|>\)\(S\|N\|NP\|PP\)\([a-zX,=]\+\)/\1\2[\3]/g' \
    		| sed -e 's/\(\/\)\(S\|N\|NP\|PP\)\(\[\)\([a-zX,=]\+\)\(\]\)\()\)/\1\2\4\6/g' \
		| sed 's/</(/g' | sed 's/>/)/g' \
    		| sed 's/[:\|;];/\.;/g' \
    		| sed -e 's/;[.,\$_A-Z-]\+\$*//g' \
    		       > ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.tsgn.mod.ptb
	    python -m scripts.tagger --format jigg_xml ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.tsgn.mod.ptb \
		   > ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.jigg.xml
	fi
    fi
    
    if [ $op -ge 4 ]; then
	python scripts/change_tags.py ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.jigg.xml
    else
	python scripts/change_tags_-rule.py ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.jigg.xml
    fi
    
    # if [ ! -e ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.sem.xml ]; then
    echo "semantic parsing $parsed_dir/${sentences_basename}.${option}.${parser_name}.sem.xml"
    semantic_parsing $parser_name $sentences_basename
    python ${c2l_dir}/visualize.py ${parsed_dir}/${sentences_basename}.${option}.${parser_name}.sem.xml \
	   > ${results_dir}/${sentences_basename}.${option}.${parser_name}.html
    if [ -f ${parsed_dir}/${sentences_basename}.${option}.neg.${parser_name}.sem.xml ]; then
	python ${c2l_dir}/visualize.py ${parsed_dir}/${sentences_basename}.${option}.neg.${parser_name}.sem.xml \
	       > ${results_dir}/${sentences_basename}.${option}.neg.${parser_name}.html
    fi
    # fi
    # if [ ! -e ${results_dir}/${sentences_basename}.${option}.${parser_name}.answer ]; then;
    proving $parser_name $sentences_basename
    # Count yes/no/unk with each parser
    fname=${results_dir}/${sentences_basename}.${option}.${parser_name}.answer
    fname_answer=`cat ${fname}`
    if [ "$fname_answer" = "yes" ]; then
      yes=$((yes += 1))
    elif [ "$fname_answer" = "no" ]; then
      no=$((no += 1))
    else
      unk=$((unk += 1))
    fi
    if [ -f ${parsed_dir}/${sentences_basename}.${option}.neg.${parser_name}.sem.xml ]; then
      # name="${option}.neg.${parser_name}"
      name="neg.${parser_name}"
      proving $name $sentences_basename
      # Count yes/no/unk with each parser
      fname_neg=${results_dir}/${sentences_basename}.${option}.neg.${parser_name}.answer
      fname_neg_answer=`cat ${fname_neg}`
      if [ "$fname_neg_answer" = "yes" ]; then
        yes=$((yes += 1))
      elif [ "$fname_neg_answer" = "no" ]; then
        no=$((no += 1))
      else
        unk=$((unk += 1))
      fi
    fi
    # fi
done

predict_answer $yes $no $unk
