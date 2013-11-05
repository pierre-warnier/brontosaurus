import sys
import codecs

import onto_utils
import language

onto_utils.read_lemma(codecs.open(sys.argv[1], encoding='UTF-8'))
for k,v in sorted(language.lemma.iteritems()):
    print ('%s\t%s' % (k,v)).encode('utf8')
