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


def subsets_by_head(_t, head):
    """Finds all the subsets corresponding to a head.
    :param _t: a term which is a string
    :param head: its head word which is a string too
    """
    res = dict()
    if head in heads:
        # Change here for disambiguation with distributional semantics
        trust = language.trust(_t, heads[head])
        if trust:
            closest[_t] = onto_utils.max_val_tie(
                (v, k) for k, v in trust.items())
        for t in heads[head]:
            for s in terms[t].subsets:
                res[s] = res.get(s, 0) + trust[t]
    if res:
        # XXX s may be zero so v/s -> div by zero
        s = sum(res.values())
        return tuple(
            ("%.1f%%" % i, j) for i, j in
            sorted(((float(v) / (s + 1) * 100, k) for k, v in res.items()),
                   reverse=True))
    return tuple()


def tag(t, head=None):
    """Tries to determine the type of a term.
    :param t: a term which is  a string
    :param head: an optional head word which is a string
    """
    t = language.lemmatize(t)
    if head:
        head = language.lemmatize(language.real_head(t, head, blacklist))
    res = None
    if t in terms:
        closest[t] = set()
        closest[t].add(t)

        res = set(i for i in terms[t].subsets)
        if not res:
            discarded[t] = head
            reasons[t] = 'Term known but no type associated: %s, %s' % (t, head)
            return
        else:
            reasons[t] = 'Term known and type associated: {0:s}, {1:s}, ' \
                         '{2:s}'.format(t, head, '|'.join(res))

    elif head:
        if head in heads:
            res = subsets_by_head(t, head)
            if not res:
                discarded[t] = head
                reasons[
                    t] = 'Term unknown, head known but no type associated: ' \
                         '%s, %s' % (t, head)
                return
            else:
                reasons[
                    t] = 'Term unknown, head known and type associated: %s, ' \
                         '%s, %s' % (t, head, '|'.join(str(i) for i in res))
    if res:
        tagged[t] = res
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

    @property
    def subsets(self):
        """Finds, sometimes recursively, the types (subsets) of a concept."""
        if hasattr(self, '_subsets'):
            for subset in self._subsets:
                yield subset
        else:
            if hasattr(self, 'parents'):
                for p in self.parents:
                    if p in terms:
                        for s in terms[p].subsets:
                            yield s

    def __repr__(self):
        """The string representation of q term."""
        return "|".join(
            "%s:%s" % (k, v) for k, v in sorted(self.__dict__.items()))


if __name__ == '__main__':
    pass
