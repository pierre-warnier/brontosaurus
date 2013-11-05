import sys
import codecs

import param
import onto_utils
import language

import numpy as np


terms = dict()
heads = dict()
tagged = dict()
discarded = dict()
reasons = dict()
blacklist = set()
orphans = dict()
closest = dict()


def save(prefix):
    "Dumps the memory content"
    # head lemma
    fd = codecs.open(prefix + u'_term_lemma.csv', 'wb', 'UTF-8')
    fd.write('term\tlemma\n')
    for k,v in sorted(language.lemma.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # head terms
    fd = codecs.open(prefix + u'_head_terms.csv', 'wb', 'UTF-8')
    fd.write('head\tterms\n')
    for k,v in sorted(heads.items()):
        fd.write('%s\t%s\n' % (k, '|'.join(v)))
    fd.close()

    # terms
    fd = codecs.open(prefix + u'_terms.csv', 'wb', 'UTF-8')
    fd.write('name\tterm_info\n')
    for k,v in sorted(terms.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # terms
    fd = codecs.open(prefix + u'_rejected_during_learning.csv', 'wb', 'UTF-8')
    fd.write('name\thead\n')
    for k,v in sorted(orphans.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # terms tagged
    fd = codecs.open(prefix + u'_terms_tagged.csv', 'wb', 'UTF-8')
    fd.write('name\ttypes\n')
    for k,v in sorted(tagged.items()):
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
    for k,v in sorted(tagged.items()):
        conceptk = closest[k]
        tmp = conceptk.copy()
        for c in conceptk:
            if hasattr(terms[c], 'synonym_of'):
                tmp.remove(c)
                for s in terms[c].synonym_of:
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
    for k,v in sorted(discarded.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # tagging explained
    fd = codecs.open(prefix + u'_tagging_explained.csv', 'wb', 'UTF-8')
    fd.write('name\treason\n')
    for k,v in sorted(reasons.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # ancestors explained
    fd = codecs.open(prefix + u'_ancestors_explained.csv', 'wb', 'UTF-8')
    fd.write('name\tancestors\n')
    for k,v in sorted(terms.items()):
        fd.write('%s\t%s\n' % (k, '|'.join(v.ancestors())))
    fd.close()

def subsets_by_head(_t, head):
    res = dict()
    if head in heads:
        # Change here for disambiguation with distributional semantics
        trust = language.trust(_t, heads[head])
        if trust:
            closest[_t] = onto_utils.max_val_tie((v,k) for k,v in trust.items())
        for t in heads[head]:
            for s in terms[t].subsets():
                res[s] = res.get(s, 0) + trust[t]
    if res:
	# XXX s may be zero so v/s -> div by zero
        s = sum(res.values())
        return tuple(("%.1f%%" %i, j) for i,j in sorted(((float(v) / (s+1) * 100, k) for k,v in res.items()), reverse=True))
    return tuple()

def tag(t, head=None):
    "Tries to determine the type of a term."
    t = language.lemmatize(t)
    if head:
        head = language.lemmatize(language.real_head(t, head, blacklist))
    res = None
    if t in terms:
        closest[t] = set()
        closest[t].add(t)

        res = set(i for i in terms[t].subsets())
        if not res:
            discarded[t] = head
            reasons[t] = 'Term known but no type associated: %s, %s' %(t, head)
            return
        else:
            reasons[t] = 'Term known and type associated: %s, %s, %s' %(t, head, '|'.join(res))

    elif head:
        if head in heads:
            res = subsets_by_head(t, head)
            if not res:
                discarded[t] = head
                reasons[t] = 'Term unknown, head known but no type associated: %s, %s' %(t, head)
                return
            else:
                reasons[t] = 'Term unknown, head known and type associated: %s, %s, %s' %(t, head, '|'.join(str(i) for i in res))
    if res:
        tagged[t] = res
    else:
        discarded[t] = head
        reasons[t] = 'Term and head unknown: %s, %s' %(t, head)

def cleaning_helper():
    "A helper function that detects obvious flows in the ontology."
    for k,v in terms.iteritems():
        if hasattr(v, 'parents'):
            # self loops
            if k in v.parents:
                print >>sys.stderr, "'%s': self loop, parents: %s" %(k, v.parents) 
            # orphans
            #to_ditch = set()
            for p in v.parents:
                if p not in terms:
                    print >>sys.stderr, "'%s': orphan, parent: '%s' not in ontology" %(k, p) 
            #        to_ditch.add(p)
            #v.parents = v.parents - to_ditch
            # term is a synonym of its parent
            for p in v.parents:
                try:
                    if k in terms[p].synonyms:
                        print >>sys.stderr, "'%s' is a synonym of its parent: '%s'" %(k, p) 
                except: pass
        if not set(v.subsets()):
            print >>sys.stderr, "'%s' none of its ancestors are typed '%s'" %(k, tuple(v.ancestors())) 

class Term(object):

    def __init__(self, name, **kwargs):
        self.name = language.lemmatize(name)
        kwargs = onto_utils.clean_dict(kwargs)
        if 'parents' in kwargs:
            kwargs['parents'] = set(language.lemmatize(p) for p in kwargs['parents'])
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
            terms[self.name].fusion(self)
        else:
            terms[self.name] = self

    def fusion(self, term1):
        self.__dict__ = onto_utils.fusion_dict(self.__dict__, term1.__dict__)

    def ancestors(self):
        if hasattr(self, 'parents'):
            for p in self.parents:
                if p in terms:
                    yield p
                    for a in terms[p].ancestors():
                        yield a

    def s_subsets(self):
        if not hasattr(self, '_s_subsets'):
            self._s_subsets = tuple((a, self.sim_subsets(terms[a])) for a in [self.name] + list(onto_utils.unique(self.ancestors())))
        return self._s_subsets

    def sim_subsets(self, t):
        if not hasattr(self, '_sim_subsets'):
            self._sim_subsets = dict()
        if not hasattr(t, '_sim_subsets'):
            t._sim_subsets = dict()
        if t.name not in self._sim_subsets:
            r = language.jaccard(set(self.subsets()), set(t.subsets()))
            self._sim_subsets[t.name] = r
            t._sim_subsets[self.name] = r
        return self._sim_subsets[t.name]

    def subsets(self):
        if hasattr(self, '_subsets'):
            for subset in self._subsets:
                yield subset
        else:
            if hasattr(self, 'parents'):
                for p in self.parents:
                    if p in terms:
                        for s in terms[p].subsets():
                            yield s
    
    def __repr__(self):
        return "|".join("%s:%s" %(k,v) for k,v in sorted(self.__dict__.iteritems()))

if __name__ == '__main__':
    pass
