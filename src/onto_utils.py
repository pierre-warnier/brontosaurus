import codecs

import language
import test
import collections

def read_blacklist(fd):
    test.blacklist.update(set(language.lemmatize(line.strip()) for line in fd if not line.startswith('#')))

# Action is 'learn' or 'tag'
def read_heads(fd, action):
    s = set((term.strip(), head.strip()) for term,head in (line.split('\t') for line in fd if not line.startswith('#')))
    # We want to add the terms to the knowledge base
    if action == 'learn':
        for term, head in s:
            if language.lemmatize(term) in test.terms:
                test.Term(name=term, head=head)
            # It's a new term and needs to be inserted somewhere (to be improved)
            else:
                test.orphans[term] = head
                #test.Term(name=term, head=head, parents=set((candidate,)))
    # We just want to tag
    elif action == 'tag':
        for term, head in s:
            test.tag(term, head)
    else:
        print "read_heads: Action unknown!"


def read_types(fd):
    s = set((term.strip(), _type.strip()) for term, _type in (line.split('\t') for line in fd if not line.startswith('#')))
    for term, _type in s:
        test.Term(name=term, _subsets=set((_type,)))

def read_lemma(fd):
    #language.lemma.update(dict((term.strip(), language.lemmatize2(lemma.strip())) for term, lemma in (line.split('\t') for line in fd if not line.startswith('#'))))
    language.lemma.update(dict((term.strip(), lemma.strip().lower()) for term, lemma in (line.split('\t') for line in fd if not line.startswith('#'))))

def fusion_dict(d1, d2):
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
                res[k] = set((d1[k], d2[k]))
        else:
            print "WARNING", type(d1[k]), type(d2[k])
    return res

def clean_dict(d):
    todo = set()
    for k,v in d.iteritems():
        if isinstance(v, collections.Iterable) and not v:
            todo.add(k)
    for k in todo:
        d.pop(k)
    return d

def unique(it):
    '''Any iterator'''
    seen = set()
    return (i for i in it if i not in seen and not seen.add(i))

def mv_dict(it):
    '''it: ((k,v),(k,v),...)'''
    res = dict()
    for k,v in it:
        res.setdefault(k, list()).append(v)
    return res

def max_val(it):
    '''it: ((k,v),(k,v),...)'''
    t = tuple(it)
    cache = mv_dict(t)
    for k in unique(k for k,v in t):
        yield k, max(cache[k]) 

def max_val_tie(it):
    '''it: ((k,v),(k,v),...)'''
    cache = mv_dict(set(it))
    return set(cache[max(cache)])

if __name__ == '__main__':
    #d1 = {'name':'vegetable', 'parents':set(['plant-derived food']), 'synonyms':set(['legume'])}
    #d2 = {'name':'vegetable', 'head':'vegetable'}
    #print d1
    #print d2
    #d1 = clean_dict(d1)
    #d2 = clean_dict(d2)
    #print d1
    #print d2
    #print fusion_dict(d1,d2)
    read_blacklist(open('../data/blacklist.txt', encoding='UTF-8'))
    print test.blacklist


