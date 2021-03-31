# Comparatives for Natural Language Inference
This repository contains code for our paper: 
* Izumi Haruta, Koji Mineshima and Daisuke Bekki. 2020. [Combining Event Semantics and Degree Semantics for Natural Language Inference](https://www.aclweb.org/anthology/2020.coling-main.156.pdf). In *Proceedings of the 2020 Conference on COLING*.
* Izumi Haruta, Koji Mineshima and Daisuke Bekki. 2020. [Logical Inferences with Comparatives and Generalized Quantifiers](https://www.aclweb.org/anthology/2020.acl-srw.35.pdf). In *Proceedings of the 2020 ACL Student Research Workshop (ACL-SRW)*.

## Requirements
* Python 3.6.5+
* [Vampire](https://github.com/vprover/vampire) 4.4.0
* [Tsurgeon](https://nlp.stanford.edu/software/tregex.html) 3.9.2
* [spaCy](https://github.com/explosion/spaCy) 2.1.8
* [word2number](https://github.com/akshaynagpal/w2n) 1.1+

### tag: `acl-srw2020`
* [Vampire](https://github.com/vprover/vampire) 4.3.0
## Setup
The system uses scripts available from [ccg2lambda](https://github.com/mynlp/ccg2lambda). It is necessary to install **python3** (3.6.5 or later), **nltk**, **lxml**, **simplejson** and **pyyaml** python libraries. 
If python3 and pip are already installed, you can install these packages with pip:

```
$ pip install lxml simplejson pyyaml nltk
```
See also [installation](https://github.com/mynlp/ccg2lambda#installation) of ccg2lambda.

In addition, **spacy** (version 2.1.8) and **word2number** are used when performing semantic assignment in the semantic template. Then, install the English version of spacy.
```
$ pip install spacy==2.1.8 word2number
$ python3 -m spacy download en
```

To run the system, first clone our repository:
```
$ git clone https://github.com/izumi-h/ccgcomp.git
```
### Installing Vampire and Tsurgeon
1. To install Vampire and Tsurgeon, change your directory to where you cloned the repository and run the following:
    ```
    $ cd ccgcomp
    $ ./tools/install_tools.sh
    ```
2. This command downloads Vampire (version 4.4.0) to `ccgcomp/vampire-4.4` and Tsurgeon (version 3.9.2) to `ccgcomp/stanford-tregex-2018-10-16`. You can change the location of Vampire and Tsurgeon by editing `scripts/vampire_dir.txt` and `scripts/tregex_location.txt`.

    ```
    $ cat scripts/vampire_dir.txt
    /Users/izumi/ccgcomp/vampire-4.4
    $ cat scripts/tregex_location.txt
    /Users/izumi/ccgcomp/stanford-tregex-2018-10-16
    ```
### Installing CCG parsers
There are the following three as typical CCG parsers.
* [C\&C](https://sites.google.com/site/stephenclark609/resources/c-c_parser)
* [depccg](https://github.com/masashi-y/depccg)
* [EasyCCG](https://github.com/mikelewis0/easyccg)

In the paper, our system is experimented by using two parsers, C&C and depccg. If you hope the same environment, choose `mac` or `linux` and execute the following command:
* Mac
    ```
    $ ./tools/install_parsers.sh mac
    ```
* Linux
    ```
    $ ./tools/install_parsers.sh linux
    ```
This command downloads C&C to `ccgcomp/candc-1.00`, EasyCCG to `ccgcomp/easyccg`, and depccg to `ccgcomp/depccg`. You can change the location of C&C by editing  `scripts/parser_location.txt`.
```
$ cat scripts/parser_location.txt
candc:/Users/izumi/ccgcomp/candc-1.00
easyccg:/Users/izumi/ccgcomp/easyccg
depccg:
```

### Selecting [MED](https://github.com/verypluming/MED) dataset
1. To get `MED.tsv` and divide the dataset into two types, do the following in ccgcomp directory: 
    ```
    $ ./tools/extract_med.sh
    ```
2. Then, we are ready to divide it into those that do not require lexical knowledge (`gq` tag) and those that require lexical knowledge (`gqlex` tag) in `./med_plain` and `./fracas_plain`.

    ```
    $ ls ./med_plain/*
    ./med_plain/med_1000_gq.answer     ./med_plain/med_465_gqlex.txt
    ./med_plain/med_1000_gq.txt        ./med_plain/med_466_gqlex.answer
    ./med_plain/med_1001_gq.answer     ./med_plain/med_466_gqlex.txt
    ./med_plain/med_1001_gq.txt        ./med_plain/med_467_gq.answer
    ・・・
    ```
    
### Setting [HANS](https://github.com/tommccoy1/hans) test dataset
1. To get HANS dataset, do the following in ccgcomp directory:
```
./tools/setting_hans.sh
```
2. Then the test data of the hans is set to `./hans_plain`.
```
ls ./hans_plain/*
./hans_plain/hans_10000_lexical_overlap.answer  ./hans_plain/hans_10000_lexical_overlap.txt
./hans_plain/hans_10001_subsequence.answer      ./hans_plain/hans_10001_subsequence.txt
./hans_plain/hans_28001_constituent.answer      ./hans_plain/hans_28001_constituent.txt
...
```
### Setting [SICK](http://alt.qcri.org/semeval2014/) dataset and downloading VerbOcean
1. To get SICK dataset and download [VerbOcean](http://demo.patrickpantel.com/demos/verbocean/), do the following in ccgcomp directory:
```
./ccg2lambda/download_dependencies.sh
```
2. Then, if you do `./scripts/eval_sick.sh`, the problems are set in `./sick_plain`.
```
$ ls ./sick_plain/*
./sick_plain/sick_test_10.answer      ./sick_plain/sick_train_1064.txt
./sick_plain/sick_test_10.txt         ./sick_plain/sick_train_1065.answer
./sick_plain/sick_test_1001.answer    ./sick_plain/sick_train_1065.txt
./sick_plain/sick_test_1001.txt       ./sick_plain/sick_train_1068.answer
...
```
    
## Running the system on several datasets
 
### Evaluation on FraCaS, MED, CAD, and HANS
You can use the [FraCaS](https://nlp.stanford.edu/~wcmac/downloads/fracas.xml), MED, CAD, and HANS test sets.

#### Usage:
```
 ./scripts/eval_fracas.sh <nbest> <ncore> <templates> <list of section numbers>
```

#### Example:
```
./scripts/eval_fracas.sh 1 2 scripts/semantic_template_event.yaml 5 6
```
- `<nbest>`: the number of output patterns of derivation trees
- `<ncore>`: the number of core

#### FraCaS section number:

```                                               single-
------------------------------------------------------
FraCaS
------------------------------------------------------
sec   topic            start   count     %     premise
---   -----------      -----   -----   -----   -------
 1    Quantifiers         1      80     23 %      50
 2    Plurals            81      33     10 %      24
 3    Anaphora          114      28      8 %       6
 4    Ellipsis          142      55     16 %      25
 5    Adjectives        197      23      7 %      15
 6    Comparatives      220      31      9 %      16
 7    Temporal          251      75     22 %      39
 8    Verbs             326       8      2 %       8
 9    Attitudes         334      13      4 %       9
 
------------------------------------------------------
CAD
------------------------------------------------------
10    Adjective
11    Adverb
12    Comparative

------------------------------------------------------
MED
------------------------------------------------------
13    gq
14    gqlex

------------------------------------------------------
HANS
------------------------------------------------------
15   hans-lexical_overlap
16   hans-subsequence
17   hans-constituent
```
The outputs are shown as:

```
candc parsing cache/fracas_220_comparatives.txt
execute tsurgeon cache/fracas_220_comparatives.txt.candc.ptb
semantic parsing cache/fracas_220_comparatives.txt.candc.sem.xml
judging entailment cache/fracas_220_comparatives.txt.candc.sem.xml unknown
...
----------------------------------------------------------------------------
Multi-parsers:
                              all premi.         single           multi
generalized_quantifiers   |     0.9452     |     0.9318     |     0.9655     
plurals                   |      ----      |      ----      |      ----     
adjectives                |     0.9545     |     0.9333     |     1.0000     
comparatives              |     0.8387     |     0.7500     |     0.9333     
verbs                     |      ----      |      ----      |      ----     
attitudes                 |      ----      |      ----      |      ----     
adjective                 |      ----      |      ----      |      ----     
comparative               |      ----      |      ----      |      ----     
gq                        |      ----      |      ----      |      ----     
gqlex                     |      ----      |      ----      |      ----     
lexical_overlap           |      ----      |      ----      |      ----     
subsequence               |      ----      |      ----      |      ----     
constituent               |      ----      |      ----      |      ----
total                     |     0.9206     |     0.8933     |     0.9608
----------------------------------------------------------------------------
C&C:
                              all premi.          single           multi
・・・     
```

### Evaluation on SICK
In addition, you can use the following for SICK dataset:
#### Usage:
```
./scripts/eval_sick.sh <ncores> <split> <templates>
```
#### Example:
```
./scripts/eval_sick.sh 10 test scripts/semantic_template_event.yaml
```
- `<split>`:`trial` (500 questions), `train` (5000 questions) and `test` (4500 questions).


By default, created files are to be stored in the three directories (`cache`, `en_results`, `tptp`).
* `cache/*.sem.xml` -- CCG derivation tress in XML format
* `en_results/*.answer` -- system prediction (yes, no, unknown)
* `en_results/*.html` -- visualized CCG derivation tree with semantic representation: the CCG tree for each FraCaS problem is accessible from `en_results/main_section*.html`.
* `en_results/*.time` -- the time that is taken to prove the problem
* `tptp/*.tptp` -- semantic representation in [tptp format](http://www.tptp.org/)


You can also run the system on each inference in FraCaS. For example, the following tried to prove the inference with ID FraCaS-243:
```
./scripts/rte_neg.sh fracas_plain/fracas_243_comparatives.txt scripts/semantic_templates.yaml
```
Or, you can do the experiment for each component, as described in [Ablation experiment](https://github.com/izumi-h/ccgcomp#ablation-experiment):
```
./scripts/rte_neg_ablation.sh fracas_plain/fracas_243_comparatives.txt scripts/semantic_templates.yaml 4
```

### Ablation experiment
To gain insights into the impact of each component, we performed an ablation experiment on overall performance.

#### Usage:
* FraCaS, MED, CAD, and HANS
```
./scripts/eval_fracas_ablation.sh <nbest> <ncore> <templates> <option> <list of section numbers>
```
* SICK
```
./scripts/eval_sick_ablation.sh <ncores> <option> <split> <templates>
```
* `<option>`: Set the option of ablation experiment
    - `normal`: 1, `+tsurgeon`: 2, `+abduction`: 3, `+rule`: 4, `+implicature`: 5
    
#### Example:
* FraCaS, MED, CAD, and HANS
```
./scripts/eval_fracas_ablation.sh 1 3 ./scripts/eval_sick.sh scripts/semantic_template_event.yaml
```
* SICK
```
./scripts/eval_sick_ablation.sh 10 tsurgeon test scripts/semantic_template_event.yaml
```

## Code Structure
The code is divided into the following:
1. `./ccg2lambda` -- scripts from [ccg2lambda](https://github.com/mynlp/ccg2lambda)
2. `./fracas_plain` -- inference problems from FraCaS and CAD by default. In each `fracas_plain/*.txt` file, a set of premises and a hypothesis are shown line by line. For example, for ID fracas_220, the first two lines are premises and the final line "The PC_6082 is fast" is a hypothesis.
    ```
    $ cat fracas_plain/fracas_220_comparatives.txt
    The PC_6082 is faster than the ITEL_XZ.
    The ITEL_XZ is fast.
    The PC_6082 is fast.
    ```
    The gold answer label is in `fracas_plain/*.txt`.
    
    ```
    $ cat fracas_plain/fracas_220_comparatives.answer
    yes
    ```
3. `./scripts` - main scripts including semantic templates (`scripts/semantic_templates.yaml`), Tsurgeon script (`scripts/transform.tsgn`) and the COMP axioms.
4. `./tools` - tools for setup
5. `./CAD` - CAD dataset which focuses on comparatives and numerical constructions

## Citation
* Izumi Haruta, Koji Mineshima, Daisuke Bekki. Combining Event Semantics and Degree Semantics for Natural Language Inference. Proceedings of  the 28nd International Conference on Computational Linguistics (COLING), pages 1758--1764, Online, December, 2020. [pdf](https://www.aclweb.org/anthology/2020.coling-main.156.pdf)
```
@inproceedings{haruta-etal-2020-combining,
    title = "Combining Event Semantics and Degree Semantics for Natural Language Inference",
    author = "Haruta, Izumi  and
      Mineshima, Koji  and
      Bekki, Daisuke",
    booktitle = "Proceedings of the 28th International Conference on Computational Linguistics",
    month = dec,
    year = "2020",
    address = "Barcelona, Spain (Online)",
    publisher = "International Committee on Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2020.coling-main.156",
    pages = "1758--1764",
}
```
* Izumi Haruta, Koji Mineshima, Daisuke Bekki. Logical Inferences with Comparatives and Generalized Quantifiers. Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics: Student Research Workshop (ACL-SRW), pages 263--270, Online, july, 2020. [pdf](https://www.aclweb.org/anthology/2020.acl-srw.35.pdf)
```
@inproceedings{haruta-etal-2020-logical,
    title = "Logical Inferences with Comparatives and Generalized Quantifiers",
    author = "Haruta, Izumi  and
      Mineshima, Koji  and
      Bekki, Daisuke",
    booktitle = "Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics: Student Research Workshop (ACL-SRW)",
    month = jul,
    year = "2020",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2020.acl-srw.35",
    pages = "263--270",
}
```
## Results
You can see [the html files](https://drive.google.com/drive/folders/17gZYhPw2zNmOH3kEmQpjWYp5C1Tp5vgQ?usp=sharing) as the results that maps CCG derivation trees to semantic representaions.