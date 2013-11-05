from nltk import word_tokenize

lemma = dict()
def lemmatize(s):
    "Lemma else surface form."
    return lemma.get(s,s)

def jaccard(s1, s2):
    "Jaccard distance between 2 sets."
    try:
        return float(len(s1.intersection(s2))) / len(s1.union(s2))
    except ZeroDivisionError: return 0.

def bow_jac_dist(s1, s2):
    "Bag of word jaccard distance between two muli-word concepts."
    set1, set2 = set(word_tokenize(s1)), set(word_tokenize(s2))
    return jaccard(set1, set2)

def real_head(s, head, blacklist=None):
    "Whenever the head is uninformative, find another one."
    if not blacklist:
        blacklist = set()
    if head in blacklist:
        l = list(i for i in word_tokenize(s) if i not in blacklist)
        if l:
            return l[-1]
    return head

def trust(t, l):
    "How close a term t is from the terms in l?"
    return dict((c, bow_jac_dist(t, c)) for c in l) 


if __name__ == "__main__":
    pass
