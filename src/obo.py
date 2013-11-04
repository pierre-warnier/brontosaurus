import re
import codecs

import test

re_term = re.compile('^\[Term\]$')
re_name = re.compile('^name:\s(.+)')
re_subset = re.compile('^subset:\s(.+)')
#re_synonym = re.compile('^(?:exact|related)_synonym: "(.+)"')
re_synonym = re.compile('^synonym: " ?(.+) ?"')
re_is_obsolete = re.compile('^is_obsolete: true')
re_is_a = re.compile('^is_a: .* ! (.+)')
    
def read_terms(fd):
    "Reads an obo file"
    for line in fd:
        if not line.startswith('#'):
            line = line.strip()
            if re_term.match(line):
                try:
                    if not is_obsolete:
                        # Here we create or update a term
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
                if subset.lower() != 'envo-lite-gsc'.lower(): # unneeded legacy type
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
    pass
