import xml.etree.ElementTree as ET
import sys
from word2number import w2n
from nltk.corpus import sentiwordnet as swn


def add_color_tags(token):

    # HTML Color Names
    # http://www.w3schools.com/colors/colors_names.asp

    colors = ['aqua', 'aquamarine', 'azure', 'beige', 'bisque', 'black',
              'blue', 'brown', 'chartreuse', 'chocolate', 'coral', 'cornsilk',
              'crimson', 'cyan', 'fuchsia', 'gainsboro', 'gold', 'gray',
              'grey', 'green', 'indigo', 'ivory', 'khaki', 'lavender', 'lime',
              'linen', 'magenta', 'maroon', 'moccasin', 'navy', 'olive',
              'orange', 'orchid', 'peru', 'pink', 'plum', 'purple', 'red',
              'salmon', 'sienna', 'silver', 'snow', 'tan', 'teal', 'thistle',
              'tomato', 'turquoise', 'violet', 'wheat', 'white', 'yellow']
    if token.attrib['pos'] == 'JJ':
        if token.attrib['surf'] in colors:
            token.attrib['entity'] = 'PRE'


def add_adj_tags(token):
    word = token.attrib['base']
    try:
        pos_score = list(swn.senti_synsets(word, 'a'))[0].pos_score()
        neg_score = list(swn.senti_synsets(word, 'a'))[0].neg_score()
    except IndexError:
        print('##### \'' + word + '\' is not adjective! ####')
        return
    if pos_score > neg_score:
        token.attrib['entity'] = "POS"
    elif neg_score > pos_score:
        token.attrib['entity'] = "NEG"
    else:
        token.attrib['entity'] = "PRE"


def change_tags(root, Fpre, Fin, adj, word, lemma, org, Fpos, Fneg, Fnsub):
    for token in root.iter('token'):
        if token.attrib['surf'] in org:
            token.attrib['entity'] = "B-ORG"
            token.attrib['pos'] = "NNP"

        elif token.attrib['surf'] in adj:
            if token.attrib['surf'] == 'cleverer':
                token.attrib['pos'] = "JJR"
                token.attrib['base'] = "clever"

            elif token.attrib['surf'] == 'four_legged':
                token.attrib['pos'] = "JJ"
                token.attrib['base'] = token.attrib['surf']
            elif token.attrib['surf'] == 'elder':
                if token.attrib['cat'] == 'N/N' \
                   or token.attrib['cat'] == 'N[adj]/N':
                    token.attrib['base'] = "old"

            elif token.attrib['surf'] == 'light' \
                    or token.attrib['surf'] == 'tan':
                if token.attrib['cat'] == 'N/N' \
                   or token.attrib['cat'] == 'N[adj]/N':
                    token.attrib['pos'] = "JJ"
                    token.attrib['base'] = token.attrib['surf']
                    token.attrib['cat'] = 'N[adj]/N'
                elif token.attrib['cat'] == 'S[adj]\\NP':
                    token.attrib['pos'] = "JJ"

            else:
                pass

        elif token.attrib['surf'] in word:
            if token.attrib['surf'] == 'drunk':
                if token.attrib['cat'] == 'S[pss]\\NP':
                    token.attrib['pos'] = "VBN"

            elif token.attrib['surf'] == 'singing':
                token.attrib['base'] = "sing"
            else:
                pass

        elif token.attrib['base'] in lemma:
            if token.attrib['base'] == 'hundred':
                token.attrib['base'] = "100"
            elif token.attrib['base'] == 'more':
                token.attrib['base'] = "many"
            elif token.attrib['surf'] == 'less':
                token.attrib['base'] = "little"
                
            elif token.attrib['base'] == 'half':
                token.attrib['pos'] = "CD"
            elif token.attrib['surf'] == 'Irishman':
                token.attrib['entity'] = "B-NORP"
            elif token.attrib['surf'] == 'Europeans':
                token.attrib['base'] = "european"
            elif token.attrib['surf'] == 'kick' \
                    or token.attrib['surf'] == 'squirt':
                token.attrib['pos'] = "NN"

            else:
                pass
        else:
            pass

        if token.attrib['pos'] == 'CD' \
           and not token.attrib['surf'] == 'half':
            if '_' not in token.attrib['surf']:
                try:
                    token.attrib['base'] \
                        = str(w2n.word_to_num(token.attrib['base']))
                except ValueError:
                    print('##### \'' + token.attrib['surf'] +
                          '\' is not numeral! ####')

        elif (token.attrib['pos'])[:2] == 'JJ':
            if token.attrib['base'] in Fpos:
                token.attrib['entity'] = "POS"
            elif token.attrib['base'] in Fneg:
                token.attrib['entity'] = "NEG"
            elif token.attrib['base'] in Fpre:
                token.attrib['entity'] = "PRE"
            elif token.attrib['base'] in Fnsub:
                token.attrib['entity'] = "N-SUB"
            elif token.attrib['entity'] != 'POS' \
                    and token.attrib['entity'] != 'NEG' \
                    and token.attrib['entity'] != 'PRE' \
                    and token.attrib['entity'] != 'N-SUB':
                add_color_tags(token)
                if token.attrib['entity'] != 'PRE':
                    add_adj_tags(token)
            else:
                pass

            if token.attrib['base'] in Fin:
                if token.attrib['entity'] == "POS":
                    token.attrib['entity'] = "POS-INT"
                elif token.attrib['entity'] == "NEG":
                    token.attrib['entity'] = "NEG-INT"
                else:
                    pass
        else:
            pass


def get_types(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    adjdic = {}
    adjlst = []
    objlst = []
    numlst = []
    Flag = False

    for token in root.iter('token'):
        if ((token.attrib['pos'] == "JJ") or (token.attrib['pos'] == "JJR")) \
           and (token.attrib['entity'] != "PRE") \
           and (token.attrib['entity'] != "B-NORP") \
           and (token.attrib['cat'] != "S[pss]\\NP"):
            if not token.attrib['base'] in adjlst:
                adjlst.append(token.attrib['base'])
                if ((token.attrib['entity'])[:3] == 'POS') \
                   or ((token.attrib['entity'])[:3] == 'NEG'):
                    adjdic[token.attrib['base']] = token.attrib['entity']

        elif (token.attrib['pos'] == "NN") or (token.attrib['pos'] == "NNS"):
            if not token.attrib['base'] in objlst:
                objlst.append(token.attrib['base'])

        elif token.attrib['surf'] == "at~most":
            Flag = True

        elif token.attrib['pos'] == "CD" \
                and not token.attrib['surf'] == "half":
            if Flag:
                num = int(token.attrib['base']) + 1
                Flag = False
                if num not in numlst:
                    numlst.append(num)
            else:
                if '_' not in token.attrib['surf']:
                    num = int(token.attrib['base'])
                    if num not in numlst:
                        numlst.append(num)

        else:
            pass
    return adjdic, adjlst, objlst, numlst


def main():

    args = sys.argv
    filename = args[1]

    Fpos = ['fast', 'genuine', 'great', 'ambitious', 'many', 'indispensable']
    Fneg = ['short', 'slow', 'few', 'little']
    Fpre = ['four_legged', 'major', 'several', 'law', 'leading', 'true',
            'false']
    Fnsub = ['former']
    Fin = ['clever', 'successful', 'important', 'genuine', 'competent',
           'stupid', 'great', 'modest', 'popular', 'poor', 'indispensable',
           'excellent', 'interest', 'ambitious']
    adj = ['cleverer', 'four_legged', 'light', 'tan', 'elder']
    # surf = ['hundreds', 'more', 'less', 'half', 'kick', 'singing',
    #         'squirt', 'drunk', 'Europeans']
    word = ['singing', 'drunk']
    lemma = ['hundred', 'more', 'less', 'half', 'kick', 'squirt',
             'europeans', 'irishman']
    org = ['PC_6082', 'ITEL_XZ', 'ITEL_ZX', 'ITEL_ZY']

    tree = ET.parse(filename)
    root = tree.getroot()

    change_tags(root, Fpre, Fin, adj, word, lemma, org, Fpos, Fneg, Fnsub)

    tree.write(filename, 'utf-8', True)


if __name__ == "__main__":
    main()
