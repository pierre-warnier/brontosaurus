# coding=utf-8
"""
This is the ONLY file to run. Read the param section for more information.
"""
import sys
import codecs

import term

from onto_utils import cleaning_helper
from language import lemma
from io import save, read_terms, read_heads, read_blacklist, read_lemma

################################################################################
# PARAMS
################################################################################

TASK = sys.argv[1]  # This is a path
EXPE = sys.argv[2]  # This is a name
BLACKLIST_OK = sys.argv[3] == 'True'
ONTO_OK = sys.argv[4] == 'True'
FLAT_OK = sys.argv[5] == 'True'

BASE_DATA = '%s/data/%s/' % (TASK, EXPE)
BASE_DUMPS = '%s/dumps/%s/' % (TASK, EXPE)

print('-' * 80)
print('Reading folder: %s' % BASE_DATA)
print('Writing folder: %s' % BASE_DUMPS)
print('Expects a blacklist: %s' % BLACKLIST_OK)
print('Expects an ontology: %s' % ONTO_OK)
print('Expects a flat resource: %s' % FLAT_OK)
print('-' * 80)

################################################################################
# FIRST
print('FIRST')
print('-' * 80)
################################################################################

print('Reading lemma')
read_lemma(codecs.open(u'{0}lemma'.format(BASE_DATA), encoding='UTF-8'))
print('%d lemma read.' % len(lemma))
print()

if BLACKLIST_OK:
    print('Reading blacklist')
    read_blacklist(
        codecs.open(u'{0}blacklist'.format(BASE_DATA), encoding='UTF-8'))

    print('Blacklist content: {0:s}'.format(', '.join(term.blacklist)))
    print()

print('-' * 80)

if ONTO_OK:
    ############################################################################
    # LEARNING ONTO
    print('LEARNING ONTO')
    print('-' * 80)
    ############################################################################
    print("Reading onto")
    read_terms(codecs.open(u'{0}onto'.format(BASE_DATA)))
    print('%d terms currently in memory.' % len(term.terms))
    print()
    print('The following inconsistencies were found in the ontology:')
    cleaning_helper()
    print()

    print("Reading onto heads")
    read_heads(codecs.open(u'{0}heads_tolearn_onto'.format(BASE_DATA),
                           encoding='UTF-8'), action='learn')

    print('%d terms currently in memory.' % len(term.terms))
    print()
    print('The following inconsistencies were found in the ontology:')
    cleaning_helper()
    print()

    print("Saving after learning onto")
    save(prefix=u'{0:s}{1:s}_after_learning_onto'.format(BASE_DUMPS, EXPE))
    print('-' * 80)

if FLAT_OK:
    ############################################################################
    # LEARNING FLAT RESOURCES
    print('LEARNING FLAT RESOURCES')
    print('-' * 80)
    ############################################################################

    print("Reading flat resources heads")
    read_heads(codecs.open(u'{0}heads_tolearn_dico'.format(BASE_DATA),
                           encoding='UTF-8'), action='learn')

    print('%d terms currently in memory.' % len(term.terms))
    print()

    print("Saving after learning flat resources")
    save(prefix=u'{0:s}{1:s}_after_learning_flat_resources'.format(BASE_DUMPS,
                                                                   EXPE))

    print('-' * 80)

################################################################################
# TAGGING
print("TAGGING")
print('-' * 80)
################################################################################

print("Tagging heads")
read_heads(codecs.open(u'{0}heads_totag'.format(BASE_DATA), encoding='UTF-8'),
           action='tag')

print('%d terms tagged.' % len(term.tagged))
print()

print("Saving after tagging")
save(prefix=BASE_DUMPS + EXPE + u'_after_tagging')
print('-' * 80)

#############################################################################
print('Done!')
print('-' * 80)
#############################################################################