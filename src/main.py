import test
from obo import read_terms
from onto_utils import read_heads, read_blacklist, read_types

# First
#read_blacklist(open('../data/blacklist.txt'))

# LEARNING
read_terms(open('../data/mbto.obo'))
read_heads(open('../data/mbto.heads'), action='learn')
test.cleaning_helper()
print '#' * 100
test.cleaning_helper()
print len(test.terms)
test.save('./dumps/v34')
test.save_sim('./dumps/v34')
#for k,v in sorted(test.terms.items()):
    #print '%s;%s;%s' % (k, v.sv_wang(), '|'.join(str(t) for t in v.s_wang()))
  #  print '%f sim(intestine, %s), subsets(intestine) = %s, subsets(%s) = %s' % (test.terms['intestine'].sim_subsets(v), k, list(test.terms['intestine'].subsets()),k, list(v.subsets()))
#print test.terms['water']
#print test.terms['intestine']
#print test.terms['wetland']

# print tuple(test.terms['intestine']._s_wang())
# print tuple(test.terms['intestine'].s_wang())
# print test.terms['intestine'].sv_wang()
# print tuple(test.terms['quicksand']._s_wang())
# print tuple(test.terms['quicksand'].s_wang())
# print test.terms['quicksand'].sv_wang()
#test.save(prefix='./dumps/onto_v30_v3')
#read_types(open('../data/train_dev_v1.csv'))
#read_heads(open('../data/tetes_train_dev3.csv'), action='learn')
#test.save(prefix='./dumps/td_a2_v3')

# TAGGING
#read_heads(open('../data/test_v4.csv'), action='tag')
#test.save(prefix='./dumps/test_v6')

#trouves = 0
#non_trouves = 0
#for k,v in test.terms.items():
#    print k, ':', v
#    if hasattr(v, 'head') and hasattr(v, '_subsets'):
#        trouves += 1
#    else:
#        non_trouves += 1

#for k,v in test.orphans.items():
#    print k,v
print 'Done!'
#print trouves
#print non_trouves
#print len(test.terms)
#
#print len(test.tagged)
#print len(test.discarded)
