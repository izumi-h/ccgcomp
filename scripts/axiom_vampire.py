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


def vampire_axioms(adjdic, antonyms, Objs, predicates, lst):
    axiom = []
    # objlst = []

    # Flag = False

    incountable = ['time']

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
            if 'person' in Objs:
                if '_np' in pred[1][1]:
                    defcom = lexpr('all x. (' + pred[0] + '(x,_np(_u,_th(_u))) <-> ' + pred[0] + '(x,_np(_person,_th(_person))))')
                else:
                    defcom = lexpr('all x. (' + pred[0] + '(x,_th(_u)) <-> ' + pred[0] + '(x,_th(_person)))')
                axiom.extend([defcom])

            # Positive adjectives
            #if pred[0] in Fpos:
            if adjdic[pred[0]] == 'POS':
                cp1 = lexpr('all x. all y. (exists d1. (' + pred[0] + '(x,d1) & -' + pred[0] + '(y,d1)) -> all d2. (' + pred[0] + '(y,d2) -> ' + pred[0] + '(x,d2)))')
                ax2 = lexpr('all d1. all x. (' + pred[0] + '(x,d1) <-> all d2. ($lesseq(d2,d1) -> ' + pred[0] + '(x,d2)))')
                axiom.extend([cp1, ax2])

                if '_th(_u)' in ((pred[1])[1]):
                    thp = lexpr('all x. (' + pred[0] + '(x,_th(_u)) <-> exists d. (' + pred[0] + '(x,d) & ($less(_th(_u),d))))')
                    axiom.extend([thp])

            # Negative adjectives
            # elif pred[0] in Fneg:
            if adjdic[pred[0]] == 'NEG':
                cp2 = lexpr('all x. all y. (exists d1. (' + pred[0] + '(x,d1) & -' + pred[0] + '(y,d1)) -> all d2. (' + pred[0] + '(y,d2) -> ' + pred[0] + '(x,d2)))')
                ax1 = lexpr('all d1. all x. (' + pred[0] + '(x,d1) <-> all d2. ($lesseq(d1,d2) -> ' + pred[0] + '(x,d2)))')
                axiom.extend([cp2, ax1])

                if '_th(_u)' in ((pred[1])[1]):
                    thm = lexpr('all x. (' + pred[0] + '(x,_th(_u)) <-> exists d. (' + pred[0] + '(x,d) & ($less(d,_th(_u)))))')
                    axiom.extend([thm])

        elif pred[0] == 'know' or pred[0] == 'manage':
            att1 = lexpr('all x.(' + pred[0] + '(x,' + pred[1][1] + ') -> ' + pred[1][1] + ')')
            axiom.extend([att1])
            
        elif pred[0] == 'fail':
            att2 = lexpr('all x.(' + pred[0] + '(x,' + pred[1][1] + ') -> -' + pred[1][1] + ')')
            axiom.extend([att2])

        # former
        elif (('former' in pred[0]) and (type(pred[1][0]) is str)):
            aff = lexpr('all x. (_former(' + pred[1][0] + ') -> -' + pred[1][0] + ')')
            axiom.extend([aff])

        elif pred[0] == 'true':
            tr = lexpr('_true(' + pred[1][0] + ') -> ' + pred[1][0])
            axiom.extend([tr])

        elif pred[0] == 'false':
            fl = lexpr('_false(' + pred[1][0] + ') -> -' + pred[1][0])
            axiom.extend([fl])

        # elif ('of' in pred[0]):
        #     ofax = lexpr('all x y.(_of(x,y) <-> (x = y))')
        #     axiom.extend([ofax])

        elif '_e' == pred[1][0]:
            if Objs != []:
                for obj in Objs:
                    comv = lexpr('$less(_th(' + obj + '),_e)')
            else:
                comv = lexpr('$less(_th(_u),_e)')
            axiom.extend([comv])
        elif pred[0] == '$less' and '_e' == pred[1][1]:
            if Objs != []:
                for obj in Objs:
                    comv = lexpr('$less(_e,_th(' + obj + '))')
            else:
                comv = lexpr('$less(_e,_th(_u))')
            axiom.extend([comv])

        else:
            pass
                
    # if ((Fp != '') and (Fm != '')):
    if antonyms != []:
        for antonym in antonyms:
            Fp = antonym[0]
            Fm = antonym[1]
            ax3 = lexpr('all d1 x. (' + Fm + '(x,d1) <-> all d2. ($less(d1,d2) -> -' + Fp + '(x,d2)))')
            ax4 = lexpr('all d1 x. (' + Fp + '(x,d1) <-> all d2. ($less(d2,d1) -> -' + Fm + '(x,d2)))')
            ax5 = lexpr('all d1 x. (-' + Fm + '(x,d1) <-> all d2. ($lesseq(d2,d1) -> ' + Fp + '(x,d2)))')
            ax6  = lexpr('all d1 x. (-' + Fp + '(x,d1) <-> all d2. ($lesseq(d1,d2) -> ' + Fm + '(x,d2)))')
            axiom.extend([ax3, ax4, ax5, ax6])

    # objlst = set(objlst)
    # objlst = list(objlst)

    if lst != []:
        for i in range(len(Objs)):
            for j in range(len(Objs)):
                if not Objs[i] == Objs[j]:
                    ax = lexpr('(all x. (' + Objs[i] + '(x) <-> ' + Objs[j] + '(x))) -> (_th(' + Objs[i] + ') = _th(' + Objs[j] + '))')
                    axiom.extend([ax])

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
    axioms = vampire_axioms(adjdic, antonyms, Objs, predicates, lst)
    print(axioms)


if __name__ == "__main__":
    main()
