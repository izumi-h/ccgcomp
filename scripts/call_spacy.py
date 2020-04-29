import spacy
import sys
# import re


def get_entity(x):
    if x.ent_iob_ == 'O':
        return x.ent_iob_
    else:
        return x.ent_iob_ + '-' + x.ent_type_

# filename = input()
nlp = spacy.load("en")
args = sys.argv
filename = args[1]
ans = ''


with open(filename, 'r', encoding='utf8') as input:
    sentences = input.readlines()
    for sentence in sentences:
        sentence = sentence.rstrip('\n')

        preds = nlp(sentence)
        tags = [x.tag_ for x in preds]
        if "''" in tags:
            tags.remove("''")
        entities = [get_entity(x) for x in preds]

        words = sentence.split(' ')

        for i in range(len(words)):
            ans += words[i] + '|' + tags[i] + '|' + entities[i] + ' '
        ans = ans[:-1] + '\n'

print(ans[:-1])
