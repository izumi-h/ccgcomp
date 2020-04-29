
import argparse
from depccg.tools.reader import read_trees_guess_extension
from depccg.printer import print_
from depccg.tokens import english_annotator
from depccg.download import SEMANTIC_TEMPLATES
from scripts.restore_tags import annotate_using_spacy
from scripts.restore_tags import add_tags

LANG = 'en'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('PATH',
                        help='path to either of *.auto, *.xml, *.jigg.xml, *.ptb')
    parser.add_argument('--annotator',
                        default='spacy',
                        choices=english_annotator.keys(),
                        help='annotate POS, named entity, and lemmas using this library')
    parser.add_argument('-f',
                        '--format',
                        default='xml',
                        choices=['auto', 'xml', 'prolog', 'jigg_xml', 'jigg_xml_ccg2lambda', 'json'],
                        help='input parser type')
    parser.add_argument('--semantic-templates',
                        help='semantic templates used in "ccg2lambda" format output')
    args = parser.parse_args()
    
    doc, trees = [], []
    for _, tokens, tree in read_trees_guess_extension(args.PATH):
        doc.append([token.word for token in tokens])
        trees.append([(tree, 0)])
    if args.PATH.endswith('.ptb'):
        filename = args.PATH.replace('tsgn.mod.ptb', 'init.jigg.xml')
        tagged_doc = add_tags(filename, doc)
    else:
        annotate_fun = english_annotator[args.annotator]
        tagged_doc = annotate_using_spacy(doc, tokenize=False)

    semantic_templates = args.semantic_templates or SEMANTIC_TEMPLATES[LANG]
    print_(trees,
           tagged_doc,
           format=args.format,
           lang=LANG,
           semantic_templates=semantic_templates)
