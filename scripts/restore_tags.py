import xml.etree.ElementTree as ET
from depccg.printer import logger
from depccg.tokens import Token


def annotate_using_spacy(sentences, tokenize=False, n_threads=2, batch_size=10000):
    try:
        import spacy
        from spacy.tokens import Doc
    except ImportError:
        logger.error('failed to import spacy. please install it by "pip install spacy".')
        exit(1)

    nlp = spacy.load('en', disable=['parser'])
    logger.info('use spacy to annotate POS and NER infos.')

    if tokenize:
        docs = [nlp.tokenizer(' '.join(sentence)) for sentence in sentences]
        raw_sentences = [[str(token) for token in doc] for doc in docs]
    else:
        docs = [Doc(nlp.vocab, sentence) for sentence in sentences]
    for name, proc in nlp.pipeline:
        docs = proc.pipe(docs,
                         n_threads=n_threads,
                         batch_size=batch_size)
    
    res = []
    for sentence in docs:
        tokens = []
        for token in sentence:
            if token.ent_iob_ == 'O':
                ner = token.ent_iob_
            else:
                ner = token.ent_iob_ + '-' + token.ent_type_

            # takes care of pronoun
            if token.lemma_ == '-PRON-':
                lemma = str(token).lower()
            else:
                lemma = token.lemma_.lower()
            tokens.append(
                Token(word=str(token),
                      pos=token.tag_,
                      entity=ner,
                      lemma=lemma,
                      chunk='XX'))
        res.append(tokens)
    if tokenize:
        return res, raw_sentences
    else:
        return res


def get_init_tags(filename):

    tree = ET.parse(filename)
    root = tree.getroot()

    lst = []
    for token in root.iter('token'):
        dic = {'word': token.attrib['surf'], 'pos': token.attrib['pos'],
               'entity': token.attrib['entity'],
               'lemma': token.attrib['base']}
        lst.append(dic)
    return lst


def add_tags(filename, doc):
    # lst = [{}, {}, ..., {.}, {}, {}, ..., {.}]
    lst = get_init_tags(filename)
    empty = ['pos', 'dgr', 'dgr2']
    compound = [['a~few', 'the~few', 'a~lot~of', 'at~most', 'at~least'],
                ['more~than', 'less~than', 'fewer~than', 'as~many',
                 'more~and~more', 'more~or~less'],
                ['law_lecturer', 'legal_authority', 'stock_market',
                 'Ancient_Greek'],
                ['in-front-of', 'whether~or~not', 'in~case']]
    res = []
    for i in range(len(doc)):
        tokens = []
        # ex. d = {'word': 'The', 'pos': 'DT',
        #          'entity': 'O', 'lemma': 'the'}
        for token in doc[i]:
            token = str(token)
            Flag = True
            for d in lst:
                if token == d['word']:
                    tokens.append(
                        Token(word=token,
                              pos=d['pos'],
                              entity=d['entity'],
                              lemma=d['lemma'],
                              chunk='XX'))
                    lst.remove(d)
                    Flag = False
                    break
            if Flag:
                # empty category
                if token in empty:
                    tokens.append(
                        Token(word=token,
                              pos='EMP',
                              entity='O',
                              lemma=token,
                              chunk='XX'))
                # compound nouns
                else:
                    if token in compound[0]:
                        pos = 'DT'
                    elif token in compound[1]:
                        pos = 'RB'
                    elif token in compound[2]:
                        pos = 'NN'
                    elif token in compound[3]:
                        pos = 'IN'
                    else:
                        print('the token \'' + token + '\' is not defined')
                        continue
                    if token == 'Ancient_Greek':
                        tokens.append(
                            Token(word=token,
                                  pos=pos,
                                  entity='B-NORP',
                                  lemma=token,
                                  chunk='XX'))
                    else:
                        tokens.append(
                            Token(word=token,
                                  pos=pos,
                                  entity='O',
                                  lemma=token,
                                  chunk='XX'))
        res.append(tokens)
    # print(res)
    return res


# def main():

#     args = sys.argv
#     filename = args[1]

#     tree.write(filename, 'utf-8', True)


# if __name__ == "__main__":
#     main()
