from nltk.stem import WordNetLemmatizer
from nltk import pos_tag, word_tokenize

lemmatizer = WordNetLemmatizer()
def lemmatize2(s):
    if s:
        # One way
        # return " ".join(lemmatizer.lemmatize(w) for w in word_tokenize(s)).lower()
        # An other
        return " ".join(lemmatizer.lemmatize(w.lower()) for w in word_tokenize(s))
    return ''

lemma = dict()
def lemmatize(s):
    return lemma.get(s,s)

def jaccard(s1, s2):
    try:
        return float(len(s1.intersection(s2))) / len(s1.union(s2))
    #except ZeroDivisionError: return None
    except ZeroDivisionError: return 0.

def bow_jac_dist(s1, s2):
    set1, set2 = set(word_tokenize(s1)), set(word_tokenize(s2))
    return jaccard(set1, set2)

def real_head(s, head, blacklist=None):
    if not blacklist:
        blacklist = set()
    if head in blacklist:
        l = list(i for i in word_tokenize(s) if i not in blacklist)
        if l:
            return l[-1]
    return head

def get_new_head(s, head, blacklist=None):
    if not blacklist:
        blacklist = set()
    if 'of' in s:
        l = list(i for i in word_tokenize(s.partition(' of ')[-1]) if i not in blacklist and i != head)
        if l:
            return l[-1]
    return head

def closest_in_list(t, l):
    score, candidate = max((bow_jac_dist(t, c), c) for c in l) 
    if score > 0:
        return candidate

def trust(t, l):
    return dict((c, bow_jac_dist(t, c)) for c in l) 


if __name__ == "__main__":
    #print word_tokenize('fly flies married marrying woman women man men corpus corpora scenario scenarii')
    #print lemmatize('fly flies married marrying woman women man men corpus corpora scenario scenarii porcine species')
    #print pos_tagging('The big blue eyes of the girl are nice') 
    s1 = 'black water marsh'
    s2 = 'water black marsh'
    s4 = 'marsh'
    s3 = 'black marsh'
    s5 = 'mud of the black marsh'
    print bow_jac_dist(s1,s2)
    print bow_jac_dist(s1,s3)
    l = (s1,s2,s3)
    print closest_in_list(s4, l)
    print '########################'
    blacklist = set(('marsh',))
    print get_new_head(s1, 'marsh', blacklist)
    print get_new_head(s5, 'mud', blacklist)
