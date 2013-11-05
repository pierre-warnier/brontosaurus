# coding=utf-8
"""
This file deals with all inputs and outputs.
"""

import codecs
import re

import term
import language


def read_blacklist(fd):
    """Reads a list of uninformative head terms.
    :rtype : None
    :param fd: a file descriptor opened in read mode
    """
    term.blacklist.update(set(language.lemmatize(line.strip()) for line in fd if
                              not line.startswith('#')))


# Action is 'learn' or 'tag'
def read_heads(fd, action):
    """Read a list of term/heads for learning or tagging purposes.
    :rtype : None
    :param fd: a file descriptor opened in read mode
    :param action: 'learn' or 'tag'
    """
    s = set((t.strip(), head.strip()) for t, head in
            (line.split('\t') for line in fd if not line.startswith('#')))
    # We want to add the terms to the knowledge base
    if action == 'learn':
        for t, head in s:
            if language.lemmatize(t) in term.terms:
                term.Term(name=t, head=head)
            # It's a new term and needs to be inserted somewhere (to be
            # improved)
            else:
                term.orphans[t] = head
                #term.Term(name=term, head=head, parents=set((candidate,)))
    # We just want to tag
    elif action == 'tag':
        # No lemmatization at this point
        for t, head in s:
            term.tag(t, head)
    else:
        print("read_heads: Action unknown!")


def read_types(fd):
    """Reads a list of term/type.
    :rtype : None
    :param fd: a file descriptor opened in read mode
    """
    s = set((t.strip(), _type.strip()) for t, _type in
            (line.split('\t') for line in fd if not line.startswith('#')))
    for t, _type in s:
        term.Term(name=t, _subsets=set)


def read_lemma(fd):
    """Reads a list of term/lemma.
    :rtype : None
    :param fd: a file descriptor opened in read mode
    """
    language.lemma.update(
        dict((t.strip(), lemma.strip().lower()) for t, lemma in
             (line.split('\t') for line in fd if not line.startswith('#'))))


re_term = re.compile('^\[Term\]$')
re_name = re.compile('^name:\s(.+)')
re_subset = re.compile('^subset:\s(.+)')
#re_synonym = re.compile('^(?:exact|related)_synonym: "(.+)"')
re_synonym = re.compile('^synonym: " ?(.+) ?"')
re_is_obsolete = re.compile('^is_obsolete: true')
re_is_a = re.compile('^is_a: .* ! (.+)')


def read_terms(fd):
    """Reads an obo file.
    :rtype : None
    :param fd: a file descriptor opened in read mode
    """
    is_obsolete = False
    name, subsets, is_a, synonyms = None, set(), set(), set()
    for line in fd:
        if not line.startswith('#'):
            line = line.strip()
            if re_term.match(line):
                try:
                    if not is_obsolete:
                        # Here we create or update a term
                        term.Term(name=name, parents=is_a, _subsets=subsets,
                                  synonyms=synonyms)
                except UnboundLocalError:
                    pass
                name, subsets, is_a, synonyms = None, set(), set(), set()
                is_obsolete = False
                continue
            m = re_name.match(line)
            if m:
                name = m.group(1).strip().lower()
                continue
            m = re_subset.match(line)
            if m:
                subset = m.group(1).lower()
                if subset.lower() != 'envo-lite-gsc'.lower():  # unneeded
                # legacy type
                    subsets.add(m.group(1).lower())
                continue
            m = re_is_a.match(line)
            if m:
                is_a.add(m.group(1).lower())
                continue
            m = re_synonym.match(line)
            if m:
                synonyms.add(m.group(1).lower())
                continue
            m = re_is_obsolete.match(line)
            if m:
                is_obsolete = True
                continue


def save(prefix):
    """Dumps the memory content
    :rtype : None
    :param prefix: a prefixing string to all save filenames
    """
    # head lemma
    fd = codecs.open(prefix + u'_term_lemma.csv', 'wb', 'UTF-8')
    fd.write('term\tlemma\n')
    for k, v in sorted(language.lemma.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # head terms
    fd = codecs.open(prefix + u'_head_terms.csv', 'wb', 'UTF-8')
    fd.write('head\tterms\n')
    for k, v in sorted(term.heads.items()):
        fd.write('%s\t%s\n' % (k, '|'.join(v)))
    fd.close()

    # terms
    fd = codecs.open(prefix + u'_terms.csv', 'wb', 'UTF-8')
    fd.write('name\tterm_info\n')
    for k, v in sorted(term.terms.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # terms
    fd = codecs.open(prefix + u'_rejected_during_learning.csv', 'wb', 'UTF-8')
    fd.write('name\thead\n')
    for k, v in sorted(term.orphans.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # terms tagged
    fd = codecs.open(prefix + u'_terms_tagged.csv', 'wb', 'UTF-8')
    fd.write('name\ttypes\n')
    for k, v in sorted(term.tagged.items()):
        l = list()
        for i in v:
            if isinstance(i, str):
                l.append(i)
            else:
                l.append(i[1])
        fd.write('%s\t%s\n' % (k, '|'.join(l)))
    fd.close()

    # terms tagged + other info
    fd = codecs.open(prefix + u'_terms_tagged_full.csv', 'wb', 'UTF-8')
    fd.write('name\ttypes\tclosest\tancestors\n')
    for k, v in sorted(term.tagged.items()):
        conceptk = term.closest[k]
        tmp = conceptk.copy()
        for c in conceptk:
            if hasattr(term.terms[c], 'synonym_of'):
                tmp.remove(c)
                for s in term.terms[c].synonym_of:
                    tmp.add(s)
        l = list()
        for i in v:
            if isinstance(i, str):
                l.append(i)
            else:
                l.append(i[1])
        fd.write('%s\t%s\t%s\n' % (k, '|'.join(l), '|'.join(tmp), ))
    fd.close()

    # terms not tagged
    fd = codecs.open(prefix + u'_terms_not_tagged.csv', 'wb', 'UTF-8')
    fd.write('name\thead\n')
    for k, v in sorted(term.discarded.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # tagging explained
    fd = codecs.open(prefix + u'_tagging_explained.csv', 'wb', 'UTF-8')
    fd.write('name\treason\n')
    for k, v in sorted(term.reasons.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # ancestors explained
    fd = codecs.open(prefix + u'_ancestors_explained.csv', 'wb', 'UTF-8')
    fd.write('name\tancestors\n')
    for k, v in sorted(term.terms.items()):
        fd.write('%s\t%s\n' % (k, '|'.join(v.ancestors())))
    fd.close()