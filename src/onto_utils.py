# coding=utf-8
"""
A collection of helper functions.
"""
import collections

import term


def fusion_dict(d1, d2):
    """Attempts to fusion two dictionaries into one.
    :param d1: a dict
    :param d2: another dict
    """
    if not d1:
        return d2
    if not d2:
        return d1
    res = dict()
    inter = set(d1.keys()).intersection(set(d2.keys()))
    only_d1 = set(d1.keys()).difference(set(d2.keys()))
    only_d2 = set(d2.keys()).difference(set(d1.keys()))
    for k in only_d1:
        res[k] = d1[k]
    for k in only_d2:
        res[k] = d2[k]
    for k in inter:
        if type(d1[k]) == type(d2[k]) == type(set()):
            res[k] = d1[k].union(d2[k])
        elif type(d1[k]) == type(d2[k]) == type(u''):
            if d1[k] == d2[k]:
                res[k] = d1[k]
            else:
                res[k] = {d1[k], d2[k]}
        else:
            print("WARNING", type(d1[k]), type(d2[k]))
    return res


def clean_dict(d):
    """Removes empty collections from a dictionary.
    :param d: a dict
    """
    todo = set()
    for k, v in d.items():
        if isinstance(v, collections.Iterable) and not v:
            todo.add(k)
    for k in todo:
        d.pop(k)
    return d


def unique(it):
    """Returns the unique elements of an iterator.
    :param it: an iterator
    """
    seen = set()
    return (i for i in it if i not in seen and not seen.add(i))


def mv_dict(it):
    """Creates a multiple value dictionary from an iterator.
    :param it: ((k,v),(k,v),...)
    """
    res = dict()
    for k, v in it:
        res.setdefault(k, list()).append(v)
    return res


def max_val_tie(it):
    """Returns the value of the biggest key in a dict created from an
    iterator.
    :param it: ((k,v),(k,v),...)
    """
    cache = mv_dict(set(it))
    return set(cache[max(cache)])


def cleaning_helper():
    """A helper function that detects obvious flows in the ontology.
    :rtype : None. This function prints its outputs.
    """
    for k, v in term.terms.items():
        if hasattr(v, 'parents'):
            # self loops
            if k in v.parents:
                print("'%s': self loop, parents: %s" % (
                    k, v.parents))
                # orphans
            #to_ditch = set()
            for p in v.parents:
                if p not in term.terms:
                    print("'{0:s}': orphan, parent: '{1:s}' "
                          "not in ontology".format(k, p))
                    #        to_ditch.add(p)
                    #v.parents = v.parents - to_ditch
                    # term is a synonym of its parent
            for p in v.parents:
                if p in term.terms and hasattr(term.terms[p], 'synonyms') and k in term.terms[p].synonyms:
                    print("'{0:s}' is a synonym of its parent: "
                          "'{1:s}'".format(k, p))
        if not set(v.subsets):
            print("'%s' none of its ancestors are typed '%s'" % (
                k, tuple(v.ancestors())))


if __name__ == '__main__':
    pass
