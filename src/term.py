# coding=utf-8
"""
Where most of the logic happens.
"""
import onto_utils
import language

terms = dict()
heads = dict()
tagged = dict()
discarded = dict()
reasons = dict()
blacklist = set()
orphans = dict()
closest = dict()


def closest_by_head(_t, head):
    """Finds the closest term in the ontology.
    :param _t: a term which is a string
    :param head: its head word which is a string too
    """
    if head in heads:
        # Change here for disambiguation with distributional semantics
        trust = language.trust(_t, heads[head])
        if trust:
            closest[_t] = onto_utils.max_val_tie(
                (v, k) for k, v in trust.items())
        return closest[_t]


def tag(t, head=None):
    """Tries to determine the type of a term.
    :type head: None
    :param t: a term which is  a string
    :param head: an optional head word which is a string
    """
    if t in terms:
        closest[t].add({t, })
        reasons[t] = 'Term known. Exact match: %s' % t
    elif head:
        head = language.real_head(t, head, blacklist)
        res = closest_by_head(t, head)
        if res:
            reasons[t] = 'Term unknown, head known. Closest term: %s, ' \
                         '%s, %s' % (t, head, res)
    else:
        discarded[t] = head
        reasons[t] = 'Term and head unknown: %s, %s' % (t, head)


class Term(object):
    """A so-called term aka an ontology concept."""

    def __init__(self, name, **kwargs):
        self.name = language.lemmatize(name)
        kwargs = onto_utils.clean_dict(kwargs)
        if 'parents' in kwargs:
            kwargs['parents'] = set(
                language.lemmatize(p) for p in kwargs['parents'])
        self.__dict__.update(kwargs)
        if 'head' in kwargs:
            self.head = language.lemmatize(self.head)
            heads.setdefault(self.head, set()).add(self.name)
        if 'synonyms' in kwargs:
            self.synonyms = set(language.lemmatize(s) for s in self.synonyms)
            kwargs.pop('synonyms')
            for s in self.synonyms:
                kwargs['synonym_of'] = set()
                kwargs['synonym_of'].add(name)
                Term(name=s, **kwargs)
        if self.name in terms:
            self.__dict__ = onto_utils.fusion_dict(terms[self.name],
                                                   self.__dict__)
        else:
            terms[self.name] = self

    def ancestors(self):
        """Finds all the ancestors of a concept."""
        if hasattr(self, 'parents'):
            for p in self.parents:
                if p in terms:
                    yield p
                    for a in terms[p].ancestors():
                        yield a

    def __repr__(self):
        """The string representation of q term."""
        return "|".join(
            "%s:%s" % (k, v) for k, v in sorted(self.__dict__.items()))


if __name__ == '__main__':
    pass
