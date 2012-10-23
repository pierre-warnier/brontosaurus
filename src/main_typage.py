import sys

import test
import language
from obo import read_terms
from onto_utils import read_heads, read_blacklist, read_types, read_lemma

#############################################################################
# PARAMS
#############################################################################

TASK = sys.argv[1]
EXPE = sys.argv[2]
BLACKLIST_OK = sys.argv[3] == 'True'
ONTO_OK = sys.argv[4] == 'True'
FLAT_OK = sys.argv[5] == 'True'

BASE_DATA  = '/bibdev/travail/typage/%s/data/%s/'  % (TASK, EXPE)
BASE_DUMPS = '/bibdev/travail/typage/%s/dumps/%s/' % (TASK, EXPE)

print '-' * 80
print 'Reading folder: %s' % BASE_DATA
print 'Writing folder: %s' % BASE_DUMPS
print 'Expects a blacklist: %s' % BLACKLIST_OK
print 'Expects an ontology: %s' % ONTO_OK
print 'Expects a flat resource: %s' % FLAT_OK
print '-' * 80

#############################################################################
# FIRST
print 'FIRST'
print '-' * 80
#############################################################################

print "Reading lemma"
read_lemma(open(BASE_DATA + 'lemma'))
print '%d lemma read.\n' % len(language.lemma)

if BLACKLIST_OK:
    print 'Reading blacklist'
    read_blacklist(open(BASE_DATA + 'blacklist'))
    print 'Blacklist content: %s\n' % ', '.join(test.blacklist)

print '-' * 80

if ONTO_OK:
    #############################################################################
    # LEARNING ONTO
    print 'LEARNING ONTO'
    print '-' * 80
    #############################################################################

    print "Reading onto"
    read_terms(open(BASE_DATA + 'onto'))
    print '%d terms currently in memory.\n' % len(test.terms)
    print 'The following inconsistencies were found in the ontology:'
    test.cleaning_helper()
    print

    print "Reading onto heads"
    read_heads(open(BASE_DATA + 'heads_tolearn_onto'), action='learn')
    print '%d terms currently in memory.\n' % len(test.terms)
    print 'The following inconsistencies were found in the ontology:'
    test.cleaning_helper()
    print

    print "Saving after learning onto"
    test.save(prefix=BASE_DUMPS + EXPE + '_after_learning_onto')
    print '-' * 80

if FLAT_OK:
    #############################################################################
    # LEARNING FLAT RESOURCES
    print 'LEARNING FLAT RESOURCES'
    print '-' * 80
    #############################################################################

    print "Reading flat resources types"
    read_types(open(BASE_DATA + 'types'))
    print '%d terms currently in memory.\n' % len(test.terms)

    print "Reading flat resources heads"
    read_heads(open(BASE_DATA + 'heads_tolearn_dico'), action='learn')
    print '%d terms currently in memory.\n' % len(test.terms)

    print "Saving after learning flat resources"
    test.save(prefix=BASE_DUMPS + EXPE + '_after_learning_flat_resources')
    print '-' * 80

#############################################################################
# TAGGING
print "TAGGING"
print '-' * 80
#############################################################################

print "Tagging heads"
read_heads(open(BASE_DATA + 'heads_totag'), action='tag')
print '%d terms tagged.\n' % len(test.tagged)

print "Saving after tagging"
test.save(prefix=BASE_DUMPS + EXPE + '_after_tagging')
print '-' * 80

#############################################################################
print 'Done!'
print '-' * 80
#############################################################################
