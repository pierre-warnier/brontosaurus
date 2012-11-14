import sys

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
    # head lemma
    fd = open(prefix + '_term_lemma.csv', 'wb')
    fd.write('term\tlemma\n')
    for k,v in sorted(language.lemma.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # head terms
    fd = open(prefix + '_head_terms.csv', 'wb')
    fd.write('head\tterms\n')
    for k,v in sorted(heads.items()):
        fd.write('%s\t%s\n' % (k, '|'.join(v)))
    fd.close()

    # terms
    fd = open(prefix + '_terms.csv', 'wb')
    fd.write('name\tterm_info\n')
    for k,v in sorted(terms.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # terms
    fd = open(prefix + '_rejected_during_learning.csv', 'wb')
    fd.write('name\thead\n')
    for k,v in sorted(orphans.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # terms tagged
    fd = open(prefix + '_terms_tagged.csv', 'wb')
    fd.write('name\ttypes\n')
    for k,v in sorted(tagged.items()):
        fd.write('%s\t%s\n' % (k, '|'.join((i if isinstance(i, str) else i[1]) for i in v)))
    fd.close()

    # terms tagged + other info
    fd = open(prefix + '_terms_tagged_full.csv', 'wb')
    fd.write('name\ttypes\tclosest\tancestors\n')
    for k,v in sorted(tagged.items()):
        conceptk = closest[k]
        for c in conceptk:
            if hasattr(terms[closest[k]], 'synonym_of'):
                conceptk.pop(c)
                conceptk.add(terms[closest[k]].synonym_of)
        fd.write('%s\t%s\t%s\t%s\n' % (k, '|'.join((i if isinstance(i, str) else i[1]) for i in v), '|'.join(conceptk), ))
    fd.close()

    # terms not tagged
    fd = open(prefix + '_terms_not_tagged.csv', 'wb')
    fd.write('name\thead\n')
    for k,v in sorted(discarded.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # tagging explained
    fd = open(prefix + '_tagging_explained.csv', 'wb')
    fd.write('name\treason\n')
    for k,v in sorted(reasons.items()):
        fd.write('%s\t%s\n' % (k, v))
    fd.close()

    # ancestors explained
    fd = open(prefix + '_ancestors_explained.csv', 'wb')
    fd.write('name\tancestors\n')
    for k,v in sorted(terms.items()):
        fd.write('%s\t%s\n' % (k, '|'.join(v.ancestors())))
    fd.close()

def save_sim(prefix):
    # similarity matrix (WANG 2007)
    t = sorted(terms.items())
    l = list()
    for i in xrange(len(t)):
        l.append('%s\t' % t[i][0] + '\t'.join('%2.3f' % s for s in (t[i][1].sim_wang(t[j][1]) for j in xrange(len(t)))) + '\n')
    fd = open(prefix + '_sim_wang.csv', 'wb')
    fd.writelines(l)
    fd.close()

    # similarity matrix jaccard subsets
    t = sorted(terms.items())
    l = list()
    for i in xrange(len(t)):
        l.append('%s\t' % t[i][0] + '\t'.join('%2.3f' % s for s in (t[i][1].sim_subsets(t[j][1]) for j in xrange(len(t)))) + '\n')
    fd = open(prefix + '_sim_subsets.csv', 'wb')
    fd.writelines(l)
    fd.close()

    # similarity matrix WANG * jaccard subsets
    t = sorted(terms.items())
    l = list()
    for i in xrange(len(t)):
        l.append('%s\t' % t[i][0] + '\t'.join('%2.3f' % s for s in (t[i][1].sim_subsets(t[j][1]) * t[i][1].sim_wang(t[j][1]) for j in xrange(len(t)))) + '\n')
    fd = open(prefix + '_sim_wang_times_subsets.csv', 'wb')
    fd.writelines(l)
    fd.close()

    # similarity matrix WANG fusion jaccard subsets
    t = sorted(terms.items())
    l = list()
    for i in xrange(len(t)):
        l.append('%s\t' % t[i][0] + '\t'.join('%2.3f' % s for s in (t[i][1].sim_wang_subsets(t[j][1]) for j in xrange(len(t)))) + '\n')
    fd = open(prefix + '_sim_wang_fusion_subsets.csv', 'wb')
    fd.writelines(l)
    fd.close()

    # sim mat reduced to heads (set sim WANG 2007)
    t = sorted(heads.items())
    l = list()
    for i in xrange(len(t)):
        l.append('%s\t' % t[i][0] + '\t'.join('%2.3f' % s for s in (
            sim_sets_wang_subsets(set(terms[ti] for ti in t[i][1]), set(terms[tj] for tj in t[j][1]))
            for j in xrange(len(t)))) + '\n')
    fd = open(prefix + '_sim_heads_wang_fusion_subsets.csv', 'wb')
    fd.writelines(l)
    fd.close()

    # sim mat reduced to heads (set sim WANG 2007)
    t = sorted(heads.items())
    l = list()
    for i in xrange(len(t)):
        l.append('%s\t' % t[i][0] + '\t'.join('%2.3f' % s for s in (
            sim_sets_wang(set(terms[ti] for ti in t[i][1]), set(terms[tj] for tj in t[j][1]))
            for j in xrange(len(t)))) + '\n')
    fd = open(prefix + '_sim_heads_wang.csv', 'wb')
    fd.writelines(l)
    fd.close()

def sim_sets_wang_subsets(s1, s2):
    return (sum(t1.sim_set_wang_subsets(s2) for t1 in s1) + sum(t2.sim_set_wang_subsets(s1) for t2 in s2)) / (len(s1) + len(s2))

def sim_sets_wang(s1, s2):
    return (sum(t1.sim_set_wang(s2) for t1 in s1) + sum(t2.sim_set_wang(s1) for t2 in s2)) / (len(s1) + len(s2))

def subsets_by_head(_t, head):
    res = dict()
    if head in heads:
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
    t = language.lemmatize(t)
    if head:
        head = language.lemmatize(language.real_head(t, head, blacklist))
    res = None
    if t in terms:
        closest[t] = set(t, )
        res = set(i for i in terms[t].subsets())
        if not res:
            discarded[t] = head
            reasons[t] = 'Term known but no type associated: %s, %s' %(t, head)
            return
        else:
            reasons[t] = 'Term known and type associated: %s, %s, %s' %(t, head, '|'.join(res))

    elif head:
        # Comment the next 2 lines if you don't want any special treatment of terms with 'of'
        #if head not in heads:
        #    head = language.get_new_head(t, head, blacklist)
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
            #self.head = language.lemmatize(language.real_head(self.name, self.head, blacklist))
            self.head = language.lemmatize(self.head)
            heads.setdefault(self.head, set()).add(self.name)
        if 'synonyms' in kwargs:
            self.synonyms = set(language.lemmatize(s) for s in self.synonyms)
            kwargs.pop('synonyms')
            for s in self.synonyms:
                kwargs['synonym_of'] = name
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

    def s_wang(self):
        if not hasattr(self, '_s_wang'):
            self._s_wang = [(self.name, 1.),] + list(onto_utils.max_val(self.__s_wang()))
        return self._s_wang

    def __s_wang(self, score=1.):
        '''Scores of ancestors'''
        if hasattr(self, 'parents'):
            for p in self.parents:
                if p in terms:
                    pscore = is_a_coeff=param.is_a_coeff * score
                    yield p, pscore
                    for a,s in terms[p].__s_wang(pscore):
                        yield a,s

    def s_subsets(self):
        if not hasattr(self, '_s_subsets'):
            self._s_subsets = tuple((a, self.sim_subsets(terms[a])) for a in [self.name] + list(onto_utils.unique(self.ancestors())))
        return self._s_subsets

    def s_wang_subsets(self):
        if not hasattr(self, '_s_wang_subsets'):
            d_wang = dict(self.s_wang())
            d_subsets = dict(self.s_subsets())
            self._s_wang_subsets = list()
            for k in d_wang:
                self._s_wang_subsets.append((k, d_wang[k] * d_subsets[k]))
        return self._s_wang_subsets

    def sv_wang(self):
        '''Score of the term itself'''
        return sum(s for a,s in self.s_wang())

    def sv_wang_subsets(self):
        '''Score of the term itself'''
        return sum(s for a,s in self.s_wang_subsets())

    def sim_wang(self, t):
        if not hasattr(self, '_sim_wang'):
            self._sim_wang = dict()
        if not hasattr(t, '_sim_wang'):
            t._sim_wang = dict()
        if t.name not in self._sim_wang:
            a_self, a_t = set(self.ancestors()), set(t.ancestors())
            a_self.add(self.name)
            a_t.add(t.name)
            inter = a_self.intersection(a_t)
            s_self, s_t = dict(self.s_wang()), dict(t.s_wang())
            r = sum(s_self[i] + s_t[i] for i in inter) / (self.sv_wang() + t.sv_wang())
            self._sim_wang[t.name] = r
            t._sim_wang[self.name] = r
        return self._sim_wang[t.name]

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

    def sim_wang_subsets(self, t):
        if not hasattr(self, '_sim_wang_subsets'):
            self._sim_wang_subsets = dict()
        if not hasattr(t, '_sim_wang_subsets'):
            t._sim_wang_subsets = dict()
        if t.name not in self._sim_wang_subsets:
            a_self, a_t = set(self.ancestors()), set(t.ancestors())
            a_self.add(self.name)
            a_t.add(t.name)
            inter = a_self.intersection(a_t)
            s_self, s_t = dict(self.s_wang_subsets()), dict(t.s_wang_subsets())
            try:
                r = sum(s_self[i] + s_t[i] for i in inter) / (self.sv_wang_subsets() + t.sv_wang_subsets())
            except ZeroDivisionError:
                r = 0
            self._sim_wang_subsets[t.name] = r
            t._sim_wang_subsets[self.name] = r
        return self._sim_wang_subsets[t.name]

    def sim_set_wang_subsets(self, s, fusion_func=np.mean):
        '''sim with a whole set'''
        return fusion_func(self.sim_wang_subsets(t) for t in s)

    def sim_set_wang(self, s, fusion_func=np.mean):
        '''sim with a whole set'''
        return fusion_func(self.sim_wang(t) for t in s)

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
    Term('black water marsh', parents=set(('water marsh','bog')), head='marsh')
    Term('water marsh', parents=set(('marsh',)), _subsets=set(('water',)), head='marsh')
    Term('bog', parents=set(('marsh',)), _subsets=set(('garbage',)), head='bog')
    Term('marsh', parents=set(('root',)), head='marsh')
    for k,v in  terms.items():
        print k, ':', v
    print heads
    tag('red water marsh', 'marsh')
    print tagged
    print discarded
    print '#' * 50
    print list(terms['black water marsh'].ancestors())
    #terms['black water marsh'].ancestors()


   # Term('b', parents=set(('c','e')))
   # print terms
   # Term('a', parents=set(('d',)), moo='poo')
   # Term('c', parents=set(('e',)), subset='poo')
   # Term('e', parents=set(('root',)), subset='poo2')
   # Term('root')
   # print terms
   # print list(Term.terms['a'].ancestors())
   # print list(onto_utils.unique(terms['a'].ancestors()))
   # print list(onto_utils.unique(terms['root'].ancestors()))
   # print list(onto_utils.unique(terms['a'].subsets()))
   # print list(onto_utils.unique(terms['b'].subsets()))
   # print list(onto_utils.unique(terms['root'].subsets()))
