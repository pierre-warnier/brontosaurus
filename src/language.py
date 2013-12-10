# coding=utf-8
"""
This file deals with all language manipulations.
"""
#from nltk import word_tokenize

lemma = dict()


def lemmatize(s):
    """Lemma else surface form.
    :param s: a string of characters
    """
    return lemma.get(s, s)


def jaccard(s1, s2):
    """Jaccard distance between 2 sets.
    :param s1: a set of objects
    :param s2: another set of objects
    """
    try:
        return float(len(s1.intersection(s2))) / len(s1.union(s2))
    except ZeroDivisionError:
        return 0.


def bow_jac_dist(s1, s2):
    """Bag of word jaccard distance between two multi-word concepts.
    :param s1: a string of one or many words
    :param s2: another string of one or many words
    """
    #set1, set2 = set(word_tokenize(s1)), set(word_tokenize(s2))
    set1, set2 = set(s1.split()), set(s2.split())
    return jaccard(set1, set2)


def real_head(t, head, blacklist=None):
    """Whenever the head is uninformative, find another one.
    :param t: a term which is a string
    :param head: the current head word of that term
    :param blacklist: a list of uninformative heads
    """
    if not blacklist:
        blacklist = set()
    if head in blacklist:
        l = list(i for i in t.split() if i not in blacklist)
        if l:
            return l[-1]
    return head


def trust(t, collection):
    """How close a term t is from the terms in l?
    :param t: a term which is string
    :param collection: a set, list etc... of terms
    """
    return dict((c, bow_jac_dist(t, c)) for c in collection)


if __name__ == "__main__":
    pass
