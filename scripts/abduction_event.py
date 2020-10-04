
import argparse
import sys
import os
from lxml import etree
from collections import defaultdict
import re

from nltk.sem import Expression, ApplicationExpression
from nltk.sem.logic import Type
lexpr = Expression.fromstring
from nltk.sem.logic import *

from os.path import expanduser
HOME = expanduser("~")
# c2l = HOME + "/ccg2lambda/scripts"
# sys.path.append(c2l)
sys.path.append("./ccg2lambda")

# from knowledge import get_tokens_from_xml_node
from normalization import denormalize_token, normalize_token
from linguistic_tools import linguistic_relationship
from linguistic_tools import get_wordnet_cascade
from nltk2normal import get_atomic_formulas


def get_formulas_from_xml(doc):
    formulas = [s.get('sem', None) for s in doc.xpath(
        './sentences/sentence/semantics[1]/span[1]')]
    return formulas


def create_antonym_axioms(relations_to_pairs, adjs, pred_args):
    relation = 'antonym'
    antonyms = relations_to_pairs[relation]
    # print(antonyms)
    axioms = []
    if not antonyms:
        antonyms = []
        return axioms
    for t1, t2 in antonyms:
        if not (t1 in adjs or t2 in adjs):
            if pred_args == 1:
                # axiom = 'Axiom ax_{0}_{1}_{2} : forall F x y,
                # _{1} x -> _{2} y -> F (Subj x) -> F (Subj y) -> False.'\
                #     .format(relation, t1, t2)
                axiom1 = lexpr('all x. ({0}(x) -> -{1}(x))'.format(t1, t2))
                axiom2 = lexpr('all x. ({1}(x) -> -{0}(x))'.format(t1, t2))
            else:
                axiom1 = lexpr('all x y. ({0}(x,y) -> -{1}(x,y))'
                               .format(t1, t2))
                axiom2 = lexpr('all x y. ({1}(x,y) -> -{0}(x,y))'
                               .format(t1, t2))
            axioms.extend([axiom1, axiom2])
    return axioms


def create_entail_axioms(relations_to_pairs, adjs, pred_args,
                         relation='synonym'):
    rel_pairs = relations_to_pairs[relation]
    axioms = []
    if not rel_pairs:
        return axioms
    for t1, t2 in rel_pairs:
        if pred_args == 1:
            # axiom = 'Axiom ax_{0}_{1}_{2} : forall x, _{1} x -> _{2} x.'\
            #         .format(relation, t1, t2)
            axiom = lexpr('all x. ({0}(x) -> {1}(x))'.format(t1, t2))
        else:
            if t1 in adjs or t2 in adjs:
                v = 'd'
            else:
                v = 'y'
            axiom = lexpr('all x {0}. ({1}(x,{0}) -> {2}(x,{0}))'
                          .format(v, t1, t2))
        axioms.append(axiom)
    return axioms


def create_reverse_entail_axioms(relations_to_pairs, adjs, pred_args,
                                 relation='hyponym'):
    rel_pairs = relations_to_pairs[relation]
    axioms = []
    if not rel_pairs:
        return axioms
    for t1, t2 in rel_pairs:
        if pred_args == 1:
            # axiom = 'Axiom ax_{0}_{1}_{2} : forall x, _{2} x -> _{1} x.'\
            #         .format(relation, t1, t2)
            axiom = lexpr('all x. ({1}(x) -> {0}(x))'.format(t1, t2))
        else:
            if t1 in adjs or t2 in adjs:
                v = 'd'
            else:
                v = 'y'
            axiom = lexpr('all x {0}. ({2}(x,{0}) -> {1}(x,{0}))'
                          .format(v, t1, t2))
        axioms.append(axiom)
    return axioms


def get_lexical_relations(premise_preds, conclusion_pred, adjs, pred_args):
    src_preds = [denormalize_token(p) for p in premise_preds]

    trg_pred = denormalize_token(conclusion_pred)

    relations_to_pairs = defaultdict(list)
    if '_dash_' in trg_pred:
        trg_pred = trg_pred.replace('_dash_', '-')

    for src_pred in src_preds:
        if src_pred == trg_pred or \
           src_pred in 'False' or \
           src_pred in 'True':
            continue
        elif '_dash_' in src_pred:
            src_pred = src_pred.replace('_dash_', '-')
        relations = linguistic_relationship(src_pred, trg_pred)
        # Choose only the highest-priority wordnet relation.
        relation = get_wordnet_cascade(relations)
        relations = [relation] if relation is not None else []
        if '-' in trg_pred or '-' in src_pred:
            trg_pred = trg_pred.replace('-', '_dash_')
            src_pred = src_pred.replace('-', '_dash_')
        for relation in relations:
            relations_to_pairs[relation].append((src_pred, trg_pred))
    # WordNet: antonym
    antonym_axioms = create_antonym_axioms(relations_to_pairs, adjs, pred_args)
    # WordNet: synonym
    synonym_axioms = create_entail_axioms(relations_to_pairs, adjs, pred_args,
                                          'synonym')
    # WordNet: hypernym
    hypernym_axioms = create_entail_axioms(relations_to_pairs, adjs, pred_args,
                                           'hypernym')
    # WordNet: similar
    similar_axioms = create_entail_axioms(relations_to_pairs, adjs, pred_args,
                                          'similar')
    # WordNet: inflection
    inflection_axioms = create_entail_axioms(relations_to_pairs, adjs,
                                             pred_args, 'inflection')
    # WordNet: derivation
    derivation_axioms = create_entail_axioms(relations_to_pairs, adjs,
                                             pred_args, 'derivation')
    # WordNet: hyponym
    hyponym_axioms = create_reverse_entail_axioms(relations_to_pairs,
                                                  adjs, pred_args)

    axioms = antonym_axioms + synonym_axioms + hypernym_axioms \
        + hyponym_axioms + similar_axioms + inflection_axioms \
        + derivation_axioms
    return list(set(axioms))


def get_tokens_from_xml_node(node):
    # tokens = node.xpath(
    #     ".//token[not(@base='*')]/@base | //token[@base='*']/@surf")
    adjs = node.xpath(
        ".//token[(@entity='POS') \
        or (@entity='NEG') or (@entity='POS-INT') \
        or (@entity='POS-INT')]/@base")
    return adjs


def check_types(p, counter):
    try:
        counter += 1
        f = lexpr(p)
        types = f.typecheck()
    except Exception as e:
        obj = re.findall('\'.*\'', str(e))
        comp = ' & (' + obj[0][1:-1] + ' = c)'
        if comp in p:
            new_p = p.replace(comp, '')
            types = check_types(new_p, counter)
        elif '_th(' in p:
            string = '_th(' + obj[0][1:-1] + ')'
            new = 'd' + str(counter)
            new_p = p.replace(string, new)
            new_p = 'exists ' + new + '.(' + new_p + ')'
            types = check_types(new_p, counter)
        else:
            types = {}
    return types


def get_axioms(formulas, sentences):

    # premises
    p = formulas[0]
    for formula in formulas[1:-1]:
        p += ' & ' + formula
    t = check_types(p, counter=10)
    p_one_preds = [k for k, v in t.items() if (str(v) == '<e,t>') or
                   (str(v) == '<v,t>')]
    p_two_preds = [k for k, v in t.items()
                   if v == Type.fromstring('<e,<e,t>>')]

    # print('{}, {}'.format(p_one_preds, p_two_preds))
    # hypothesis
    h = formulas[-1]
    t = check_types(h, counter=10)
    c_one_preds = [k for k, v in t.items() if (str(v) == '<e,t>') or
                   (str(v) == '<v,t>')]
    c_two_preds = [k for k, v in t.items()
                   if v == Type.fromstring('<e,<e,t>>')]

    for s in sentences:
        adjs = get_tokens_from_xml_node(s)
    p_axioms = []
    for c_token in c_one_preds:
        p_axiom = get_lexical_relations(p_one_preds, c_token, adjs, 1)
        # print(p_axiom)
        if p_axiom != []:
            p_axioms.extend(p_axiom)
    
    for c_token in c_two_preds:
        p_axiom2 = get_lexical_relations(p_two_preds, c_token, adjs, 2)
        # print(p_axiom)
        if p_axiom2 != []:
            p_axioms.extend(p_axiom2)
    return p_axioms


def main():
    global ARGS
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("sem", help="XML input filename with semantics")

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
    sentences = doc.xpath('//sentence')
    p_axioms = get_axioms(formulas, sentences)

    print(p_axioms)


if __name__ == '__main__':
    main()
