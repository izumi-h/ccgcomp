
import argparse
from depccg.tools.reader import read_jigg_xml


def bracket(tree, tokens):
    def rec(node):
        if node.is_leaf:
            cat = str(node.cat).replace('(', '<') \
                               .replace(')', '>') \
                               .replace('[', '') \
                               .replace(']', '')
            cat = cat.replace('=true', '')
            word = node.word
            for token in tokens:
                if token['surf'] == word:
                    pos = token['pos']
                    pos = pos.replace('=true', '')
                    entity = token['entity']
            return f'({cat};{pos};{entity} {word})'
        else:
            cat = str(node.cat).replace('(', '<') \
                               .replace(')', '>') \
                               .replace('[', '') \
                               .replace(']', '')
            cat = cat.replace('=true', '')
            children = ' '.join(rec(child) for child in node.children)
            return f'({cat} {children})'
    return f'(ROOT {rec(tree)})'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('fname')

    args = parser.parse_args()

    for name, tokens, tree in read_jigg_xml(args.fname):
        print(bracket(tree, tokens))
