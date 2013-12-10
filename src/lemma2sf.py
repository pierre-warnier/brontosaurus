# coding=utf-8
"""
A small script to retrieve the surface form of terms from their lemma.
"""
import sys
import codecs

import io
import language

io.read_lemma(codecs.open(sys.argv[1], encoding='UTF-8'))
for k, v in sorted(language.lemma.items()):
    print(('%s\t%s' % (k, v)).encode('utf8'))
