import sys

import onto_utils
import language

onto_utils.read_lemma(open(sys.argv[1]))
for k,v in sorted(language.lemma.iteritems()):
    print '%s\t%s' % (k,v)
