import re

import test

re_term = re.compile('^\[Term\]$')
re_name = re.compile('^name:\s(.+)')
re_subset = re.compile('^subset:\s(.+)')
re_synonym = re.compile('^synonym: "(.+)"')
re_is_obsolete = re.compile('^is_obsolete: true')
re_is_a = re.compile('^is_a: .* ! (.+)')
    
def read_terms(fd):
    for line in fd:
        if not line.startswith('#'):
            line = line.strip()
            if re_term.match(line):
                try:
                    if not is_obsolete:
                        test.Term(name=name, parents=is_a, _subsets=subsets, synonyms=synonyms)
                except UnboundLocalError:
                    pass
                name, subsets, is_a, synonyms = None, set(), set(), set()
                is_obsolete = False
                continue
            m = re_name.match(line)
            if m:
                name = m.group(1).strip().lower()
                continue
            m = re_subset.match(line)
            if m:
                subset = m.group(1).lower()
                if subset.lower() != 'envo-lite-gsc'.lower():
                    subsets.add(m.group(1).lower())
                continue
            m = re_is_a.match(line)
            if m:
                is_a.add(m.group(1).lower())
                continue
            m = re_synonym.match(line)
            if m:
                synonyms.add(m.group(1).lower())
                continue
            m = re_is_obsolete.match(line)
            if m:
                is_obsolete = True
                continue

if __name__ == "__main__":
    read_terms(open('../data/mbto.obo'))
    test.cleaning_helper()
    print len(test.terms)
    test.save('./dumps/v34')
    #for k,v in sorted(test.terms.items()):
        #print '%s;%s;%s' % (k, v.sv_wang(), '|'.join(str(t) for t in v.s_wang()))
      #  print '%f sim(intestine, %s), subsets(intestine) = %s, subsets(%s) = %s' % (test.terms['intestine'].sim_subsets(v), k, list(test.terms['intestine'].subsets()),k, list(v.subsets()))
    #print test.terms['water']
    #print test.terms['intestine']
    #print test.terms['wetland']

   # print tuple(test.terms['intestine']._s_wang())
   # print tuple(test.terms['intestine'].s_wang())
   # print test.terms['intestine'].sv_wang()
   # print tuple(test.terms['quicksand']._s_wang())
   # print tuple(test.terms['quicksand'].s_wang())
   # print test.terms['quicksand'].sv_wang()
