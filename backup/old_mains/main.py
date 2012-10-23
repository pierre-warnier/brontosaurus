import test
from obo import read_terms
from onto_utils import read_heads, read_blacklist, read_types, read_lemma

# First
read_blacklist(open('/bibdev/travail/typage/typage_biotope_task3.4/data/expe_20120912/blacklist.txt'))

# LEARNING
read_terms(open('/bibdev/travail/typage/typage_biotope_task3.4/data/expe_20120912/bacteria_habitat_OntoBiotope-34'))
read_heads(open('/bibdev/travail/typage/typage_biotope_task3.4/data/expe_20120912/heads_tolearn_onto'), action='learn')
#test.cleaning_helper()
print '#' * 100
#test.cleaning_helper()

# LEARNING
print 'LEARNING'
print "Reading lemma"
read_lemma(open('/bibdev/travail/typage/typage_biotope_task3.4/data/expe_20120912/lemma'))
print "Reading types"
read_types(open('/bibdev/travail/typage/typage_biotope_task3.4/data/expe_20120912/types'))
print "Reading heads"
read_heads(open('/bibdev/travail/typage/typage_biotope_task3.4/data/expe_20120912/heads_tolearn_dico'), action='learn')
print "Saving"
test.save(prefix='/bibdev/travail/typage/typage_biotope_task3.4/dumps/expe1_20120912/expe1_20120912_after_learning')

# TAGGING
print "\nTAGGING"
print "Tagging heads"
read_heads(open('/bibdev/travail/typage/typage_biotope_task3.4/data/expe_20120912/heads_totag'), action='tag')
print "Saving"
test.save(prefix='/bibdev/travail/typage/typage_biotope_task3.4/dumps/expe1_20120912/expe1_20120912_after_tagging')

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
