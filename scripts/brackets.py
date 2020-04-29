
import argparse
from depccg.tools.reader import read_trees_guess_extension

def bracket(tree):
    def rec(node):
        if node.is_leaf:
            cat = str(node.cat).replace('(','<') \
                               .replace(')','>') \
                               .replace('[','') \
                               .replace(']','')
            word = node.word
            return f'({cat} {word})'
        else:
            cat = str(node.cat).replace('(','<') \
                               .replace(')','>') \
                               .replace('[','') \
                               .replace(']','')
            children = ' '.join(rec(child) for child in node.children)
            return f'({cat} {children})'
    return f'(ROOT {rec(tree)})'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fname',
                        help='file name: *.auto, *.xml, *.ptb')

    parser.add_argument('--format',
                        default='auto',
                        choices=['auto','ptb','xml'],
                        help='output format')

    args = parser.parse_args()

    for name, tokens, tree in read_trees_guess_extension(args.fname):
        print(bracket(tree))

