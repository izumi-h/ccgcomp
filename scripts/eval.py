# -*- coding: utf-8 -*-

import argparse
from lxml import etree
# from nltk.inference import Prover9, Mace
from nltk.sem.logic import Expression, NegatedExpression, ApplicationExpression
import os
import subprocess
import sys
import textwrap
import time
from multiprocessing import Queue, Process
import re

lexpr = Expression.fromstring

# from axiom_prover9 import prover9_axioms
from axiom_vampire_event import vampire_axioms
from change_tags import get_types
from abduction_event import get_axioms

from os.path import expanduser
HOME = expanduser("~")
# vampire_dir = HOME + "/vampire"
file = open("./scripts/vampire_dir.txt")
vampire_dir = file.read().strip()
sys.path.append("./ccg2lambda")

from linguistic_tools import is_antonym

sys.path.append("./scripts")


from nltk2tptp import convert_to_tptp_proof, convert_to_tptp
from nltk2normal import get_atomic_formulas, rename_degree_variable


def get_formulas_from_xml(doc):
    formulas = [s.get('sem', None) for s in doc.xpath(
        './sentences/sentence/semantics[1]/span[1]')]
    return formulas


# types of predicates
non_Sub = ['former', 'true', 'false']
clause = ['before']
datasets = ['med', 'hans']


def get_antonyms(adjdic, antonyms):
    adjs = [k for k, v in adjdic.items()]
    for i in range(len(adjs) - 1):
        Flag = is_antonym(adjs[i], adjs[i + 1])
        if Flag:
            if adjdic[adjs[i]] == 'POS' and adjdic[adjs[i + 1]] == 'NEG':
                antonyms.append([adjs[i], adjs[i + 1]])
            else:
                antonyms.append([adjs[i + 1], adjs[i]])
    return antonyms


# def prove_prover9mace(premises, conclusion, predicates, lst, axioms):
#     adjdic, adjlst, objlst, numlst \
#         = get_types(ARGS.sem.strip(".sem.xml") + '.jigg.xml')
#     antonyms = []
#     if adjlst != []:
#         antonyms = get_antonyms(adjdic, antonyms)
#     # add axioms from comp
#     axioms2 = prover9_axioms(adjdic, antonyms, objlst, predicates, lst)

#     axioms += axioms2
#     axioms = set(axioms)
#     axioms = list(axioms)

#     premises = axioms + premises
    
#     def prover_fun(queue):
#         res = Prover9(timeout=3).prove(conclusion, premises)
#         is_prover = True
#         queue.put((is_prover, res))

#     def modelbuilder_fun(queue):
#         res = Mace(end_size=50).build_model(conclusion, premises)
#         is_prover = False
#         queue.put((is_prover, res))

#     queue = Queue()
#     prover_process = Process(target=prover_fun, args=(queue,))
#     modelbuilder_process = Process(target=modelbuilder_fun, args=(queue,))
#     processes = [prover_process, modelbuilder_process]
#     for process in processes:
#         process.start()

#     while queue.empty():
#         pass

#     is_prover, result = queue.get()
#     if is_prover:
#         modelbuilder_process.terminate()
#     else:
#         prover_process.terminate()
#         result = not result
#     return result


def prove_vampire(premises, conclusion, predicates, lst, axioms, mode):
    adjdic, adjlst, objlst, numlst, tverblst, iverblst \
        = get_types(ARGS.sem.strip(".sem.xml") + '.jigg.xml')
    antonyms = []
    if adjlst != []:
        antonyms = get_antonyms(adjdic, antonyms)
    # add axioms from comp
    types, axioms2 = vampire_axioms(adjdic, antonyms, objlst, tverblst,
                                    iverblst, predicates, lst)
    axioms += axioms2
    axioms = set(axioms)
    axioms = list(axioms)

    # tptp_axioms = [convert_to_tptp(axiom) for axiom in axioms]
    premises = axioms + premises
    premises.append(conclusion)
    fols = convert_to_tptp_proof(premises)
    # print(fols)

    type_f = []
    type_f_adj = []
    type_f_adj.extend(types)
    lems = []

    for adj in adjlst:
        adj_type = 'tff(' + adj + '_type, type , ' + adj + \
                   ' : $i * $int > $o).'
        type_f_adj.append(adj_type)

    if len(numlst) >= 2:
        numlst.sort()
        for i in range(len(numlst) - 1):
            lem = '$less(' + str(numlst[i]) + ',' + str(numlst[i + 1]) + ')'
            f = lexpr(lem)
            lemma = convert_to_tptp(f)
            lems.append(lemma)
    for pred in predicates:
        if pred[0] == 'much' or pred[0] == 'many' or pred[0] == 'few':
            adj_type = 'tff(' + pred[0] + '_type, type , ' + pred[0] + \
                       ' : $i * $int > $o).'
            type_f_adj.append(adj_type)
            if pred[0] == 'many':
                adj_type = 'tff(few_type, type , few : $i * $int > $o).'
                type_f_adj.append(adj_type)
            elif pred[0] == 'few':
                adj_type = 'tff(many_type, type , many : $i * $int > $o).'
                type_f_adj.append(adj_type)
            else:
                pass
            qu_lem = lexpr('all x y.(exists d.(' + pred[0] + '(x,d) & -'
                           + pred[0] + '(y,d)) -> all d.(' + pred[0] +
                           '(y,d) -> ' + pred[0] + '(x,d)))')
            qu_lem = convert_to_tptp(qu_lem)
            if qu_lem not in lems:
                lems.append(qu_lem)

        elif pred[0] == 'year' or pred[0] == 'num':
            type_f.append('tff(' + pred[0] + '_type, type , ' + pred[0] + ' : $int * $i > $o).')

        for naf in non_Sub:
            if pred[0] == naf:
                naf_type = 'tff(' + naf + '_type, type , ' + naf + \
                           ' : $o > $o).'
                type_f.append(naf_type)

        v_type = 'tff(acci_type, type , acci : $i * $o > $o).'
        type_f.append(v_type)

        for c in clause:
            if pred[0] == c:
                c_type = 'tff(' + c + '_type, type , ' + c + \
                         ' : $o * $o > $o).'
                type_f.append(c_type)

        for obj in objlst:
            if (pred[0] == obj) or (obj in pred[1][0]):
                obj_type = 'tff(' + obj + '_type, type , ' + obj + \
                           ' : $i > $o).'
                type_f.append(obj_type)

        type_f.append('tff(th_type, type , th : $i > $int).')
        type_f.append('tff(d0_type, type , d0 : $int).')

        # if (len(pred[1]) == 2) and ('_th' in (pred[1])[1]):
        #     type_f.append('tff(th_type, type , th : $i > $int).')
        if (len(pred[1]) == 2) and ('_np' in (pred[1])[1]):
            type_f.append('tff(np_type, type , np : $i * $int > $int).')

    type_f = set(type_f)
    type_f = list(type_f)
    type_f_adj = set(type_f_adj)
    type_f_adj = list(type_f_adj)
    # fols = set(fols)
    # fols = list(fols)

    # print(type_f)
    # print(type_f_adj)

    for i in range(len(lems)):
        fols.insert(-1, 'tff(p{0},lemma,{1}).'.format(i, lems[i]))

    fols = type_f + type_f_adj + fols

    # if ('many' in fols) or ('few' in fols):
    #     f = lexpr('all d1.-exists d2.($less(d1,d2) & $less(d2,$sum(d1,1)))')
    #     lemma = convert_to_tptp(f)
    #     fols.insert(-1, 'tff(p1,lemma,{0}).'.format(lemma))

    # print(fols)

    # arg = ARGS.sem.strip("./results")
    # arg = arg.strip(".sem.xml")
    # arg = ARGS.sem.strip(".sem.xml")
    arg = ARGS.sem.replace('cache/', '')
    arg = arg.replace('.sem.xml', '')
    with open("tptp/" + arg + ".tptp", "w", encoding="utf-8") as z:
        for f in fols:
            z.write(f + "\n")
    tptp_script = ' '.join(fols)
    ps = subprocess.Popen(('echo', tptp_script), stdout=subprocess.PIPE)
    try:
        if mode == 'casc_sat':
            timeout = '1'
        else:
            timeout = '7'
        output = subprocess.check_output(
              (vampire_dir + '/vampire', '-t', timeout, '--mode', mode),
              stdin=ps.stdout,
              stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        return False
    ps.wait()
    output_lines = [
        str(line).strip() for line in output.decode('utf-8').split('\n')]
    res = is_theorem_in_vampire(output_lines)
    return res


def is_theorem_in_vampire(output_lines):
    if output_lines:
        proof_message = '% Refutation found. Thanks to Tanya!'
        if (proof_message in output_lines):
            # proof_message = output_lines[0]
            # if proof_message == '% Refutation found. Thanks to Tanya!':
            return True
        else:
            # print(output_lines)
            return False
    else:
        # print(output_lines)
        return False

    
def theorem_proving(prove_fun, premises, conclusion, predicates, lst, axioms,
                    mode, data):
    res = prove_fun(premises, conclusion, predicates, lst, axioms, mode)
    if res:
        prediction = 'yes'
    else:
        if data not in datasets:
            negated_conclusion = NegatedExpression(conclusion)
            res = prove_fun(premises, negated_conclusion, predicates, lst,
                            axioms, mode)
            if res:
                prediction = 'no'
            else:
                prediction = 'unknown'
        else:
            prediction = 'unknown'
    return prediction


def multi_theorem_proving(prove_fun, premises, conclusion, predicates, lst,
                          axioms, mode, data):
    def prove_positive(queue):
        res = prove_fun(premises, conclusion, predicates, lst, axioms, mode)
        is_prover = True
        queue.put((is_prover, res))

    def prove_negative(queue):
        negated_conclusion = NegatedExpression(conclusion)
        res = prove_fun(premises, negated_conclusion, predicates, lst, axioms,
                        mode)
        is_prover = False
        queue.put((is_prover, res))

    queue = Queue()
    prove_pos_process = Process(target=prove_positive, args=(queue,))
    prove_neg_process = Process(target=prove_negative, args=(queue,))
    processes = [prove_pos_process, prove_neg_process]
    for process in processes:
        process.start()

    while queue.empty():
        pass

    is_prover, is_theorem = queue.get()
    if is_prover and is_theorem:
        prove_neg_process.terminate()
        prediction = 'yes'
    else:
        prove_pos_process.terminate()
        if is_theorem:
            prediction = 'no'
        else:
            prediction = 'unknown'
    return prediction


def get_predicate(formula):
    predlst = []
    preds = get_atomic_formulas(lexpr(formula))
    for pred in preds:
        if isinstance(pred, ApplicationExpression):
            predicate, args = pred.uncurry()
            pred_str = str(predicate)
            args_str = [str(arg) for arg in args]
            item = [pred_str, args_str]
            if item not in predlst:
                predlst.append(item)
    return predlst


def main(args = None):
    global ARGS
    global DOCS
    DESCRIPTION = textwrap.dedent("""
            The input file sem should contain the parsed sentences. '\
            'All CCG trees correspond to the premises, '\
            'except the last one, which is the hypothesis.
      """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION)
    parser.add_argument("sem", help="XML input filename with semantics")

    parser.add_argument("--prover", nargs='?', type=str, default="vampire",
                        choices=["vampire"],
                        help="Prover (default: vampire).")

    parser.add_argument("--abduction", nargs='?', type=str, default="lex",
                        choices=["lex", "nolex"],
                        help="Abduction (default: lex).")

    ARGS = parser.parse_args()

    if not os.path.exists(ARGS.sem):
        print('File does not exist: {0}'.format(ARGS.sem), file=sys.stderr)
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.parse(ARGS.sem, parser)

    DOCS = root.findall('.//document')
    doc = DOCS[0]
    formulas = get_formulas_from_xml(doc)

    # add axioms from WordNet
    if ARGS.abduction == "lex":
        sentences = doc.xpath('//sentence')
        axioms = get_axioms(formulas, sentences)
    else:
        axioms = []

    lst = []
    predicates = []
    new_formulas = []
    for formula in formulas:
        if '--' in formula:
            formula = formula.replace('--', '')
        formula = rename_degree_variable(lexpr(formula))
        new_formulas.append(str(formula))
    for formula in new_formulas:
        if ('all' in formula) and ('->' in formula) \
           and ('_th(' in formula):
            lst.append(formula)
        preds = get_predicate(formula)
        for pred in preds:
            if pred not in predicates:
                predicates.append(pred)
    # print(predicates)

    # formulas2 = []
    # for formula in formu:
    #     if '--' in formula:
    #         formula = formula.replace('--', '')
    #     formulas2.append(formula)

    # if ARGS.prover == "prover9":
    #     formulas = [lexpr(formula) for formula in formulas2]
    #     conclusion = formulas[-1]
    #     premises = formulas[:-1]
    #     start = time.time()
    #     prediction = theorem_proving(prove_prover9mace, premises,
    #                                  conclusion, predicates, lst, [],
    #                                  mode)
    #     # if prediction == 'unknown':
    #     #     prediction = theorem_proving(prove_vampire, premises,
    #     #                                  conclusion, predicates,
    #     #                                  lst, axioms)
    #     end = time.time() - start
    #     # print('{0},{1:.4f}'.format(prediction, end))
    #     # print(prediction)

    p = re.compile(r'(\w+)/(\w+)_(\w+)_(\w+)')
    a = p.search(ARGS.sem)
    if a is not None:
        cache, data, num, other = a.groups()
    else:
        data = 'None'

    if ARGS.prover == "vampire":
        formulas = [lexpr(formula) for formula in new_formulas]
        premises = formulas[:-1]
        conclusion = formulas[-1]
        start = time.time()
        # prediction = multi_theorem_proving(prove_vampire,
        # premises, conclusion, predicates)
        prediction = theorem_proving(prove_vampire, premises, conclusion,
                                     predicates, lst, axioms, 'casc', data)
        end = time.time() - start
        if prediction == 'unknown' and end >= 8:
            prediction = theorem_proving(prove_vampire, premises,
                                         conclusion, predicates,
                                         lst, axioms, 'casc_sat', data)
        # print('{0},{1:.4f}'.format(prediction, end))
        print(prediction)


if __name__ == '__main__':
    main()


# Test formulas
f1 = lexpr('exists x. (boy(x) & tall(x))')
f2 = lexpr('exists x. (boy(x))')
f3 = lexpr('forall x. (boy(x) -> -tall(x))')
f4 = lexpr('tall(john)')
f5 = lexpr('-boy(john)')
inf1 = [f1, f2]
inf2 = [f2, f1]
inf3 = [f3, f4, f5]
