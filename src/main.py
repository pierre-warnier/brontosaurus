import test
from obo import read_terms
from onto_utils import read_heads 

read_terms(open('../data/mbto.obo'))
read_heads(open('../data/mbto.heads'), action='learn')
test.cleaning_helper()
print '#' * 100
test.cleaning_helper()
print len(test.terms)
test.save('./dumps/v34')
test.save_sim('./dumps/v34')
