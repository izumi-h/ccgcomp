from nltk import *
# from nltk.sem.drt import DrtParser
# from nltk.sem import logic
# logic._counter._value = 0

from nltk.sem import Expression
from nltk.sem.logic import *
lexpr = Expression.fromstring

# import time

## Logical formulas ##

# Negation: -A
# Conjunction: A & B
# Disjunction: A | B
# Conditional mood: A -> B
# Universal quantifier: all x. A
# Existential quantifier: exists x. A
# Equal: x = y
# Lambda formula: \x. A

# class Inference:
#     def __init__(self, number, gold, premises, conclusion):
#         self.number = number
#         self.gold = gold
#         self.premises = premises
#         self.conclusion = conclusion
#     def show(self, system_answer, time):
#         print('{0}: {1}/{2}  time:{3:.2f}'.format(self.number, self.gold, system_answer, time))

# def prove_neg(premises, conclusion):
#     negconclusion = NegatedExpression(conclusion)
#     try:
#         if Prover9(timeout=3).prove(negconclusion, axioms + premises):
#             answer = 'no'
#         else:
#             if Mace(end_size=50).build_model(conclusion, axioms + premises):
#                 answer = 'unknown'
#             else:
#                 answer = 'timeout'
#     except:
#         answer = 'unknown1'
#     return answer

# def prove(premises, conclusion):
#     try:
#         if Prover9(timeout=3).prove(conclusion, axioms + premises):
#            answer = 'yes'
#         else:
#            answer = prove_neg(premises, conclusion)
#         return answer
#     except:
#         answer = prove_neg(premises, conclusion)
#         return answer


def vampire_axioms(adjdic, antonyms, Objs, tVerbs, iVerbs, predicates, lst):
    axiom = []
    # objlst = []

    Flag1 = False
    Flag2 = False

    # incountable = ['time']

    for pred in predicates:
        # print(pred)
        if pred[0][0] == '_':
            pred[0] = pred[0][1:]

        if (pred[0] == 'many') and not (pred[0] in adjdic):
            adjdic[pred[0]] = 'POS'
        if (pred[0] == 'few') and not (pred[0] in adjdic):
            adjdic[pred[0]] = 'NEG'

        # Adjectives
        # if (pred[0] in Fpos) or (pred[0] in Fneg):
        if pred[0] in adjdic:
            if '_d0' in pred[1][1]:
                deg = lexpr('$less(0,_d0)')
                axiom.append(deg)
            if 'person' in Objs:
                if '_np' in pred[1][1]:
                    defcom = lexpr('all x. (' + pred[0] + '(x,_np(_u,_th(_u))) <-> ' + pred[0] + '(x,_np(_person,_th(_person))))')
                else:
                    defcom = lexpr('all x. (' + pred[0] + '(x,_th(_u)) <-> ' + pred[0] + '(x,_th(_person)))')
                axiom.append(defcom)

            if '_np' in pred[1][1]:
                np = lexpr('all x d1 d2.($lesseq(d1,d2) <-> $lesseq(_np(x,d1),_np(x,d2)))')
                axiom.append(np)

            # Positive adjectives
            # if pred[0] in Fpos:
            if antonyms != [] or '_th(' not in ((pred[1])[1]):
                if adjdic[pred[0]][:3] == 'POS':
                    if '$' in pred[1][1]:
                        upper = lexpr('all x. exists d1.(' + pred[0] + '(x,d1) & -exists d2.($less(d1,d2) & ' + pred[0] + '(x,d2)))')
                        axiom.append(upper)
                    # cp1 = lexpr('all x. all y. (exists d1. (' + pred[0] + '(x,d1) & -' + pred[0] + '(y,d1)) -> all d2. (' + pred[0] + '(y,d2) -> ' + pred[0] + '(x,d2)))')
                    if pred[0] != 'many' or (pred[1][1])[0] != 'd' or Flag1:
                        ax1 = lexpr('all x d1. (' + pred[0] + '(x,d1) -> all d2. ($lesseq(d2,d1) -> ' + pred[0] + '(x,d2)))')
                        axiom.append(ax1)

                    # if '_th(_u)' in ((pred[1])[1]):
                    #     thp = lexpr('all x. (' + pred[0] + '(x,_th(_u)) <-> exists d. (' + pred[0] + '(x,d) & ($less(_th(_u),d))))')
                    #     axiom.extend([thp])

            # Negative adjectives
            # elif pred[0] in Fneg:
                elif adjdic[pred[0]][:3] == 'NEG':
                    if '$' in pred[1][1]:
                        lower = lexpr('all x. exists d1.(' + pred[0] + '(x,d1) & -exists d2.($less(d2,d1) & ' + pred[0] + '(x,d2)))')
                        axiom.append(lower)
                    # cp2 = lexpr('all x. all y. (exists d1. (' + pred[0] + '(x,d1) & -' + pred[0] + '(y,d1)) -> all d2. (' + pred[0] + '(y,d2) -> ' + pred[0] + '(x,d2)))')

                    if not Flag2 and ((pred[1])[1] == '_d0' or \
                         ('_np' in (pred[1])[1] and '_d0' in (pred[1])[1])):
                        Flag2 = True
                        if Objs != []:
                            for obj in Objs:
                                comv = lexpr('$less(_d0,_th(' + obj + '))')
                        else:
                            comv = lexpr('$less(_d0,_th(_u))')
                        axiom.append(comv)

                    if pred[0] != 'few' or (pred[1][1])[0] != 'd' or Flag1:
                        ax2 = lexpr('all x d1. (' + pred[0] + '(x,d1) -> all d2. ($lesseq(d1,d2) -> ' + pred[0] + '(x,d2)))')
                        axiom.append(ax2)
                else:
                    pass

                # if not Flag:
                #     if Objs != []:
                #         for obj in Objs:
                #             comv = lexpr('$less(_d0,_th(' + obj + '))')
                #     else:
                #         comv = lexpr('$less(_d0,_th(_u))')
                #     Flag = True
                #     axiom.extend([comv])

                # if '_th(_u)' in ((pred[1])[1]):
                #     thm = lexpr('all x. (' + pred[0] + '(x,_th(_u)) <-> exists d. (' + pred[0] + '(x,d) & ($less(d,_th(_u)))))')
                #     axiom.extend([thm])

        # elif pred[0] == 'know' or pred[0] == 'manage':
        #     att1 = lexpr('all x.(' + pred[0] + '(x,' + pred[1][1] + ') -> ' + pred[1][1] + ')')
        #     axiom.extend([att1])
            
        # elif pred[0] == 'fail':
        #     att2 = lexpr('all x.(' + pred[0] + '(x,' + pred[1][1] + ') -> -' + pred[1][1] + ')')
        #     axiom.extend([att2])

        elif pred[0] == 'AccI':
            att1 = lexpr('all e. (AccI(e,' + pred[1][1] + ') -> (_know(e) ->' + pred[1][1] + '))')
            att2 = lexpr('all e. (AccI(e,' + pred[1][1] + ') -> (_forget(e) ->' + pred[1][1] + '))')
            att3 = lexpr('all e. (AccI(e,' + pred[1][1] + ') -> (_learn(e) ->' + pred[1][1] + '))')
            att4 = lexpr('all e. (AccI(e,' + pred[1][1] + ') -> (_remember(e) ->' + pred[1][1] + '))')
            att5 = lexpr('all e. (AccI(e,' + pred[1][1] + ') -> (_manage(e) ->' + pred[1][1] + '))')
            att6 = lexpr('all e. (AccI(e,' + pred[1][1] + ') -> (_fail(e) -> -' + pred[1][1] + '))')
            axiom.extend([att1, att2, att3, att4, att5, att6])

        # former
        elif (('former' in pred[0]) and (type(pred[1][0]) is str)):
            aff = lexpr('all x. (_former(' + pred[1][0] + ') -> -' + pred[1][0] + ')')
            axiom.append(aff)

        elif pred[0] == 'true':
            tr = lexpr('_true(' + pred[1][0] + ') -> ' + pred[1][0])
            axiom.append(tr)

        elif pred[0] == 'false':
            fl = lexpr('_false(' + pred[1][0] + ') -> -' + pred[1][0])
            axiom.append(fl)

        # elif ('of' in pred[0]):
        #     ofax = lexpr('all x y.(_of(x,y) <-> (x = y))')
        #     axiom.extend([ofax])

        elif '$less' in pred[0]:
            Flag1 = True
            if not Flag2 and (pred[1][0] == '_d0' or pred[1][1] == '_d0'):
                Flag2 = True
                deg = lexpr('$less(0,_d0)')
                axiom.append(deg)
                if '_d0' == pred[1][0]:
                    if Objs != []:
                        for obj in Objs:
                            comv = lexpr('$less(_th(' + obj + '),_d0)')
                            axiom.append(comv)
                    else:
                        comv = lexpr('$less(_th(_u),_d0)')
                        axiom.append(comv)
        # elif pred[0] == '$less' and '_d0' == pred[1][1]:
            # if Objs != []:
            #     for obj in Objs:
            #         comv = lexpr('$less(_d0,_th(' + obj + '))')
            # else:
            #     comv = lexpr('$less(_d0,_th(_u))')
            # axiom.extend([comv])

        else:
            pass

    # if ((Fp != '') and (Fm != '')):
    if antonyms != []:
        for antonym in antonyms:
            Fp = antonym[0]
            Fm = antonym[1]
            # ax3 = lexpr('all x d1. (' + Fm + '(x,d1) <-> all d2. ($less(d1,d2) -> -' + Fp + '(x,d2)))')
            # ax4 = lexpr('all x d1. (' + Fp + '(x,d1) <-> all d2. ($less(d2,d1) -> -' + Fm + '(x,d2)))')
            # ax5 = lexpr('all x d1. (-' + Fm + '(x,d1) <-> all d2. ($lesseq(d2,d1) -> ' + Fp + '(x,d2)))')
            # ax6  = lexpr('all x d1. (-' + Fp + '(x,d1) <-> all d2. ($lesseq(d1,d2) -> ' + Fm + '(x,d2)))')
            # axiom.extend([ax3, ax4, ax5, ax6])
            ax3 = lexpr('all x d.(' + Fp + '(x,d) <-> -' + Fm + '(x,d))')
            axiom.append(ax3)

    # objlst = set(objlst)
    # objlst = list(objlst)

    if lst != []:
        for i in range(len(Objs)):
            for j in range(len(Objs)):
                if not Objs[i] == Objs[j]:
                    ax = lexpr('(all x. (' + Objs[i] + '(x) <-> ' + Objs[j] + '(x))) -> (_th(' + Objs[i] + ') = _th(' + Objs[j] + '))')
                    axiom.append(ax)

    if tVerbs != []:
        for verb in tVerbs:
            verbax = lexpr('all e1 e2.(' + verb + '(e1) & ' + verb + '(e2) & (subj(e1) = subj(e2)) & (acc(e1) = acc(e2)) -> (e1 = e2))')
            if not verbax in axiom:
                axiom.append(verbax)
    if iVerbs != []:
        for verb in iVerbs:
            verbax = lexpr('all e1 e2.(' + verb + '(e1) & ' + verb + '(e2) & (subj(e1) = subj(e2)) -> (e1 = e2))')
            if not verbax in axiom:
                axiom.append(verbax)

    axiom = set(axiom)
    axiom = list(axiom)
    # print(axiom)
    return axiom


def main():
    # print('Gold answer/System answer')
    # total_problem = 0
    # correct_answer = 0

    # for ex in examples:
    #     start = time.time()
    #     answer = prove(ex.premises, ex.conclusion)
    #     end = time.time() - start
    #     if answer == ex.gold:
    #         correct_answer += 1
    #         total_problem += 1
    #     else:
    #         total_problem += 1
    #     ex.show(answer, end)

    # accuracy = correct_answer / total_problem
    # print('Accuracy: {0:.4f}'.format(accuracy))
    adjdic = {}
    antonyms = []
    Objs = []
    lst = []
    predicates = []
    axioms, lemma = vampire_axioms(adjdic, antonyms, Objs, predicates, lst)
    print(axioms)


if __name__ == "__main__":
    main()
