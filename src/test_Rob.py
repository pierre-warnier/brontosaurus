import onto_utils
import language

terms = dict()
heads = dict()
tagged = dict()
discarded = dict()
reasons = dict()
blacklist = set()
orphans = dict()

def save(prefix):
    # head terms
    fd = open(prefix + '_head_terms.csv', 'wb')
    fd.write('head;terms\n')
    for k,v in sorted(heads.items()):
        fd.write('%s;%s\n' % (k, '|'.join(v)))
    fd.close()

    # terms
    fd = open(prefix + '_terms.csv', 'wb')
    fd.write('name;term_info\n')
    for k,v in sorted(terms.items()):
        fd.write('%s;%s\n' % (k, v))
    fd.close()

    # terms
    fd = open(prefix + '_rejected_during_learning.csv', 'wb')
    fd.write('name;head\n')
    for k,v in sorted(orphans.items()):
        fd.write('%s;%s\n' % (k, v))
    fd.close()

    # terms tagged
    fd = open(prefix + '_terms_tagged.csv', 'wb')
    fd.write('name;types\n')
    for k,v in sorted(tagged.items()):
        fd.write('%s;%s\n' % (k, '|'.join((i if isinstance(i, str) else i[1]) for i in v)))
    fd.close()

    # terms not tagged
    fd = open(prefix + '_terms_not_tagged.csv', 'wb')
    fd.write('name;head\n')
    for k,v in sorted(discarded.items()):
        fd.write('%s;%s\n' % (k, v))
    fd.close()

    # tagging explained
    fd = open(prefix + '_tagging_explained.csv', 'wb')
    fd.write('name;reason\n')
    for k,v in sorted(reasons.items()):
        fd.write('%s;%s\n' % (k, v))
    fd.close()

    # ancestors explained
    fd = open(prefix + '_ancestors_explained.csv', 'wb')
    fd.write('name;ancestors\n')
    for k,v in sorted(terms.items()):
        fd.write('%s;%s\n' % (k, '|'.join(v.ancestors())))
    fd.close()

def subsets_by_head(_t, head):
    res = dict()
    if head in heads:
        trust = language.trust(_t, heads[head])
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
        res = set(i for i in terms[t].subsets())
        if not res:
            discarded[t] = head
            reasons[t] = 'Term known but no type associated: %s, %s' %(t, head)
            return
        else:
            reasons[t] = 'Term known and type associated: %s, %s, %s' %(t, head, '|'.join(res))

    elif head:
        # Comment the next 2 lines if you don't want any special treatment of terms with 'of'
        if head not in heads:
            head = language.get_new_head(t, head, blacklist)
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

def closest_term(t, head=None):
    t = language.lemmatize(t)
    if t in terms:
        return t
    if not head:
        head = language.get_head(t)
    if head in heads:
        return language.closest_in_list(t, heads[head])

class Term(object):

    def __init__(self, name, **kwargs):
        self.name = language.lemmatize(name)
        kwargs = onto_utils.clean_dict(kwargs)
        if '_subsets' in kwargs:
            kwargs['_subsets'] = set(p.lower().replace('_','') for p in kwargs['_subsets'])
        # To avoid loops... The source can be dirty
        if 'parents' in kwargs:
            if self.name in kwargs['parents']:
                kwargs['parents'].remove(self.name)
            kwargs['parents'] = set(language.lemmatize(p) for p in kwargs['parents'])
                
        self.__dict__.update(kwargs)
        if 'head' in kwargs:
            self.head = language.lemmatize(language.real_head(self.name, self.head, blacklist))
            heads.setdefault(self.head, set()).add(self.name)
        if 'synonyms' in kwargs:
            self.synonyms = set(language.lemmatize(s) for s in self.synonyms)
            kwargs.pop('synonyms')
            for s in self.synonyms:
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
