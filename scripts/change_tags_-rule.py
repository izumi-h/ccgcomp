import xml.etree.ElementTree as ET
import sys
import re
from word2number import w2n
from nltk.corpus import sentiwordnet as swn
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer


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
        # print('##### \'' + word + '\' is not adjective! ####')
        return
    if pos_score > neg_score:
        token.attrib['entity'] = "POS"
    elif neg_score > pos_score:
        token.attrib['entity'] = "NEG"
    else:
        token.attrib['entity'] = "PRE"


def add_adj_handtags(token, Fpos, Fneg, Fpre, Fnsub, Fin):
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


def orgs(token):
    token.attrib['surf'] = re.sub('_', '', token.attrib['surf'])
    token.attrib['entity'] = "B-ORG"
    token.attrib['pos'] = "NNP"


def change_tags(root, Fpre, Fin, adj, surf, lemma, Fpos, Fneg, Fnsub, adv):
    for token in root.iter('token'):
        # if token.attrib['surf'] in org:
        #     token.attrib['entity'] = "B-ORG"
        #     token.attrib['pos'] = "NNP"
        if '_' in token.attrib['surf'] and token.attrib['surf'][0].isupper():
            index = token.attrib['id'].index('_')
            num = int(token.attrib['id'][index+1:])
            Search = token.attrib['id'][:index+1] + str(num-1)
            a = root.find(".//token[@id='{}']".format(Search))
            if a.attrib['base'] == 'the':
                orgs(token)

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

            elif token.attrib['surf'] == 'sci-fi' \
                or token.attrib['surf'] == 'light' \
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

        elif token.attrib['surf'] in surf:
            if token.attrib['surf'] == 'Aldo':
                token.attrib['pos'] = "NNP"
            elif token.attrib['surf'] == 'Jones':
                token.attrib['entity'] = "B-PERSON"
            elif token.attrib['surf'] == 'drunk':
                if token.attrib['cat'] == 'S[pss]\\NP':
                    token.attrib['pos'] = "VBN"
            elif token.attrib['surf'] == 'likely' \
                    and token.attrib['cat'] == '(S[adj]\\NP)/(S[to]\\NP)':
                token.attrib['pos'] = 'MD'
            elif token.attrib['surf'] == 'Japanese' \
                    and token.attrib['cat'] == 'N':
                token.attrib['entity'] = "B-LANGUAGE"

            elif token.attrib['surf'] == 'singing':
                token.attrib['base'] = "sing"
            
            else:
                pass

        elif token.attrib['base'] in lemma:
            if token.attrib['base'] == 'hundred':
                token.attrib['base'] = "100"
            elif token.attrib['base'] == 'more':
                token.attrib['base'] = "many"
            elif token.attrib['base'] == 'less':
                token.attrib['base'] = "little"
            elif token.attrib['base'] == 'people':
                token.attrib['base'] = "person"
                
            elif token.attrib['base'] == 'half':
                token.attrib['pos'] = "CD"
            elif token.attrib['base'] == 'garlic' \
                    or token.attrib['base'] == 'pasta' \
                    or token.attrib['base'] == 'okra':
                token.attrib['pos'] = "NN"
                token.attrib['surf'] = token.attrib['base']
            elif token.attrib['surf'] == 'Irishman':
                token.attrib['entity'] = "B-NORP"
            elif token.attrib['surf'] == 'Europeans':
                token.attrib['base'] = "european"
            elif token.attrib['surf'] == 'kick' \
                    or token.attrib['surf'] == 'squirt':
                token.attrib['pos'] = "NN"
            elif token.attrib['surf'] == 'alien':
                token.attrib['pos'] = "NN"
                token.attrib['entity'] = "O"

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
            add_adj_handtags(token, Fpos, Fneg, Fpre, Fnsub, Fin)
            # if token.attrib['base'] in Fpos:
            #     token.attrib['entity'] = "POS"
            # elif token.attrib['base'] in Fneg:
            #     token.attrib['entity'] = "NEG"
            # elif token.attrib['base'] in Fpre:
            #     token.attrib['entity'] = "PRE"
            # elif token.attrib['base'] in Fnsub:
            #     token.attrib['entity'] = "N-SUB"
            # elif token.attrib['entity'] != 'POS' \
            #         and token.attrib['entity'] != 'NEG' \
            #         and token.attrib['entity'] != 'PRE' \
            #         and token.attrib['entity'] != 'N-SUB':
            #     add_color_tags(token)
            #     if token.attrib['entity'] != 'PRE':
            #         add_adj_tags(token)
            # else:
            #     pass

            # if token.attrib['base'] in Fin:
            #     if token.attrib['entity'] == "POS":
            #         token.attrib['entity'] = "POS-INT"
            #     elif token.attrib['entity'] == "NEG":
            #         token.attrib['entity'] = "NEG-INT"
            #     else:
            #         pass

        elif (token.attrib['pos'])[:2] == 'RB' \
                and (token.attrib['cat'] == '(S\\NP)\\(S\\NP)'
                     or token.attrib['cat'] == '(S[adv]\\NP)\\(S[adv]\\NP)'):
            word = token.attrib['base']
            if (token.attrib['base'])[-2:] == 'ly' \
               and token.attrib['base'] not in adv:
                s = []
                winner = ""
                for ss in wn.synsets(word):
                    for lemmas in ss.lemmas():
                        s.append(lemmas)
                try:
                    for pers in s:
                        posword = pers.pertainyms()[0].name()
                        if posword[0:3] == word[0:3]:
                            winner = posword
                            break

                    token.attrib['base'] = winner
                except IndexError:
                    pass
            elif token.attrib['pos'] == 'RBR':
                wnl = WordNetLemmatizer()
                token.attrib['base'] = wnl.lemmatize(word, 'a')
            add_adj_handtags(token, Fpos, Fneg, Fpre, Fnsub, Fin)
            if (token.attrib['entity'])[:3] != 'POS' and \
               (token.attrib['entity'])[:3] != 'NEG':
                token.attrib['base'] = token.attrib['surf']
        else:
            pass


def get_types(filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    adjdic = {}
    adjlst = []
    # advdic = {}
    # advlst = []
    objlst = []
    numlst = []
    tverblst = []
    iverblst = []
    Flag = False

    for token in root.iter('token'):
        if (((token.attrib['pos'] == "JJ") or (token.attrib['pos'] == "JJR"))
           and (token.attrib['entity'] != "PRE")
           and (token.attrib['entity'] != "B-NORP")
           and (token.attrib['cat'] != "S[pss]\\NP")) \
           or (((token.attrib['pos'] == "RB")
                or (token.attrib['pos'] == "RBR"))
               and (((token.attrib['entity'])[:3] == 'POS')
                    or ((token.attrib['entity'])[:3] == 'NEG'))):
            if not token.attrib['base'] in adjlst \
               and '~' not in token.attrib['base']:
                adjlst.append(token.attrib['base'])
                if ((token.attrib['entity'])[:3] == 'POS') \
                   or ((token.attrib['entity'])[:3] == 'NEG'):
                    adjdic[token.attrib['base']] = token.attrib['entity']
        # if ((token.attrib['pos'] == "JJ") or (token.attrib['pos'] == "JJR")) \
        #    and (token.attrib['entity'] != "PRE") \
        #    and (token.attrib['entity'] != "B-NORP") \
        #    and (token.attrib['cat'] != "S[pss]\\NP"):
        #     if not token.attrib['base'] in adjlst:
        #         adjlst.append(token.attrib['base'])
        #         if ((token.attrib['entity'])[:3] == 'POS') \
        #            or ((token.attrib['entity'])[:3] == 'NEG'):
        #             adjdic[token.attrib['base']] = token.attrib['entity']

        # elif (((token.attrib['pos'] == "RB")
        #         or (token.attrib['pos'] == "RBR"))):
        #     if not token.attrib['base'] in advlst \
        #        and '~' not in token.attrib['base']:
        #         advlst.append(token.attrib['base'])
        #         if ((token.attrib['entity'])[:3] == 'POS') \
        #            or ((token.attrib['entity'])[:3] == 'NEG'):
        #             advdic[token.attrib['base']] = token.attrib['entity']

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

        elif (token.attrib['pos'])[:2] == 'VB' and \
                not token.attrib['base'] == 'be':
            if '/NP' in token.attrib['cat'] or \
               '/PP' in token.attrib['cat'] or \
               'S[pss]' in token.attrib['cat']:
                if not token.attrib['base'] in tverblst:
                    tverblst.append(token.attrib['base'])
            else:
                if not token.attrib['base'] in iverblst:
                    iverblst.append(token.attrib['base'])

        else:
            pass
    return adjdic, adjlst, objlst, numlst, tverblst, iverblst


def main():

    args = sys.argv
    filename = args[1]

    # Fpos = ['fast', 'genuine', 'great', 'ambitious', 'many', 'indispensable',
    #         'noisy', 'early']
    Fneg = ['short', 'slow', 'few', 'little', 'young']
    Fpre = ['four_legged', 'major', 'several', 'law', 'leading', 'true',
            'false', 'sci-fi', 'other', 'hooded', 'colored']
    Fnsub = ['former']
    Fin = ['clever', 'successful', 'important', 'genuine', 'competent',
           'stupid', 'great', 'modest', 'popular', 'poor', 'indispensable',
           'excellent', 'interest', 'ambitious']
    # adj = ['cleverer', 'four_legged', 'light', 'tan', 'sci-fi', 'colored',
    #        'elder']
    # surf = ['Aldo', 'singing', 'drunk', 'Japanese', 'likely', 'Jones']
    # lemma = ['hundred', 'more', 'less', 'irishman', 'half', 'garlic', 'kick',
    #          'squirt', 'pasta', 'okra', 'europeans', 'alien', 'people']
    # org = ['PC_6082', 'ITEL_XZ', 'ITEL_ZX', 'ITEL_ZY']

    Fpos = ['fast', 'genuine', 'great', 'ambitious', 'many', 'indispensable']
    adj = []
    surf = []
    lemma = ['hundred', 'more', 'less', 'half', 'people']

    adv = ['lately', 'nearly', 'highly', 'rarely']

    tree = ET.parse(filename)
    root = tree.getroot()

    change_tags(root, Fpre, Fin, adj, surf, lemma, Fpos, Fneg, Fnsub, adv)

    tree.write(filename, 'utf-8', True)


if __name__ == "__main__":
    main()
