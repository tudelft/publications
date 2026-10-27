# Report publications that occur more than once in the bib files that make up all.bib
#
#   python check_duplicates.py <file.bib> ...
#
# Two entries are the same publication when they have the same key (e.g. a Pure id
# in both pure.bib and mavlab_nopure.bib), the same DOI (ignoring dataset versions
# .v1, .v2), or the same type, title and year. A preprint and its published paper
# or a dataset, a thesis and a paper with the same title, and the same news story on
# two websites are different publications.
# Exit code 1 when duplicates are found.
import re
import sys
from collections import defaultdict

import bibtexparser


def doi_id(txt):
    txt = txt.strip().lower().replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
    return re.sub(r'\.v\d+$', '', txt)


def title_id(txt):
    return re.sub(r'[^a-z0-9]', '', re.sub(r'\\[a-z]+', '', txt.lower()))


def kind(e):
    # arXiv preprints are @misc like datasets; news items on different sites differ
    if 'arxiv' in e.get('eprint', '').lower():
        return 'preprint'
    if e['ENTRYTYPE'] == 'online':
        return 'online ' + re.sub(r'^https?://(www\.)?', '', e.get('url', '')).split('/')[0]
    return e['ENTRYTYPE']


def check(filenames):
    seen = defaultdict(list)
    for f in filenames:
        parser = bibtexparser.bparser.BibTexParser(common_strings=True)
        parser.ignore_nonstandard_types = False
        with open(f, encoding='utf-8-sig') as bibfile:
            for e in bibtexparser.load(bibfile, parser=parser).entries:
                where = '%s: %s (%s %s)' % (f, e['ID'], e['ENTRYTYPE'], e.get('year', ''))
                seen['same key ' + e['ID']].append(where)
                if e.get('doi'):
                    seen['same DOI ' + doi_id(e['doi'])].append(where)
                if e.get('title'):
                    seen['same type, title and year: ' + e.get('title', '')[:70]
                         + '|' + kind(e) + title_id(e['title']) + e.get('year', '')].append(where)

    # one line per group of entries, whatever matched first
    reported = set()
    for why, entries in seen.items():
        group = tuple(sorted(set(entries)))
        if len(entries) > 1 and group not in reported:
            reported.add(group)
            print('Duplicate (%s):' % why.split('|')[0])
            for w in entries:
                print('   ', w)
    print('%d duplicates' % len(reported))
    return not reported


if __name__ == '__main__':
    sys.exit(0 if check(sys.argv[1:]) else 1)
