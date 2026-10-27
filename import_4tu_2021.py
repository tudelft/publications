# Download the 4TU.ResearchData datasets of MAVLab staff into 4tu.bib
#
# Every dataset on data.4tu.nl gets a DataCite DOI with prefix 10.4121, so the
# DataCite REST API (https://support.datacite.org/docs/api) is used to find and
# describe them: no scraping of data.4tu.nl. Two searches:
# - datasets with a MAVLab staff member among the creators (one request per person)
# - datasets that reference a MAVLab paper (a DOI in PAPERS), e.g. data uploaded
#   by a PhD student only (40 papers per request)
#
# - one entry per dataset, keyed by its concept DOI (without .v1, .v2): it always
#   points to the latest version, so a new version updates the entry in place
# - @data is the teachPress type for datasets
# - entries are sorted by year (newest first), type, first author and title, so
#   new datasets appear at the top and existing entries never move
# - when a search fails, or far fewer datasets are found than before (use --force
#   when that is intended), 4tu.bib is not changed and the exit code is 1
import argparse
import codecs
import os
import re
import sys
import time

import requests


API = 'https://api.datacite.org/dois'
PREFIX = '10.4121'
OUTPUT = '4tu.bib'
PAPERS = ['pure.bib', 'mavlab_nopure.bib', 'arxiv_nopub.bib']    # MAVLab papers, for datasets that reference them
BATCH = 40    # paper DOIs per DataCite request

# MAVLab staff: last name -> first initial (skips other people with the same last name)
STAFF = {'croon': 'G', 'wagter': 'C', 'smeur': 'E', 'remes': 'B', 'tijmons': 'S',
         'hamaza': 'S', 'popovic': 'M', 'karasek': 'M', 'dupeyroux': 'J', 'scheper': 'K'}


def search(query):
    # all DOIs that match the query, all pages
    records, url = [], API
    params = {'query': 'prefix:%s AND %s' % (PREFIX, query), 'page[size]': 1000}
    while url:
        for attempt in range(3):
            try:
                p = requests.get(url, params=params, timeout=60)
                if p.status_code == 200:
                    break
                print('  HTTP', p.status_code)
            except requests.RequestException as e:
                print('  error:', e)
            time.sleep(10 * (attempt + 1))
        else:
            return None
        d = p.json()
        records += d['data']
        url, params = d.get('links', {}).get('next'), None
    return records


def paper_dois():
    dois = []
    for filename in PAPERS:
        with open(filename, encoding='utf-8-sig') as f:
            for doi in re.findall(r'^\s*doi\s*=\s*[{"](.*?)[}"]', f.read(), re.M):
                doi = doi.replace('\\_', '_').strip().lower()
                if not doi.startswith(PREFIX + '/'):
                    dois.append(doi)
    return list(dict.fromkeys(dois))


def ascii_lower(s):
    return s.lower().replace('ć', 'c').replace('č', 'c')


def is_staff(creator):
    family = creator.get('familyName') or creator.get('name', '').split(',')[0]
    given = creator.get('givenName') or (creator.get('name', '').split(',') + [''])[1]
    last = ascii_lower(family).replace('-', ' ').split()
    return bool(last) and last[-1] in STAFF and given.strip().upper().startswith(STAFF[last[-1]])


def concept_doi(doi):
    return re.sub(r'\.v\d+$', '', doi.lower())


def version(doi):
    m = re.search(r'\.v(\d+)$', doi.lower())
    return int(m.group(1)) if m else 0


def clean(txt):
    txt = re.sub(r'<[^>]+>', ' ', txt or '')
    return ' '.join(txt.replace('{', '(').replace('}', ')').split())


def bib_name(creator):
    if creator.get('familyName'):
        return (creator['familyName'] + ', ' + creator.get('givenName', '')).strip(', ')
    return creator.get('name', '')


def to_bibtex(doi, a):
    title = clean(a['titles'][0]['title']) if a.get('titles') else ''
    abstract = [clean(d.get('description')) for d in a.get('descriptions', []) if d.get('descriptionType') == 'Abstract']
    keywords = [clean(s['subject']) for s in a.get('subjects', []) if s.get('subject')]
    rights = [r['rights'] for r in a.get('rightsList', []) if r.get('rights')]
    fields = [
        ('author', ' and '.join(bib_name(c) for c in a.get('creators', []))),
        ('title', title),
        ('year', str(a.get('publicationYear', ''))),
        ('publisher', clean(a.get('publisher') if isinstance(a.get('publisher'), str) else (a.get('publisher') or {}).get('name'))),
        ('doi', doi),
        ('url', 'https://doi.org/' + doi),
        ('keywords', ', '.join(dict.fromkeys(keywords))),
        ('abstract', abstract[0] if abstract else ''),
        ('copyright', clean(rights[0]) if rights else ''),
        ('note', clean(a.get('types', {}).get('resourceTypeGeneral', ''))),
    ]
    bib = '@data{' + doi + ',\n'
    bib += ',\n'.join('\t%-9s = {%s}' % (k, v) for k, v in fields if v)
    return bib + '\n}'


def sort_key(e):
    # newest first; within a year a fixed order on type, first author and title,
    # and the DOI so that entries with the same author and title never swap places
    first_author = e['author'].split(' and ')[0].lower()
    return (-int(e['year'] or 0), e['type'], first_author, e['title'].lower(), e['doi'])


def read_previous(filename):
    entries = {}
    if os.path.exists(filename):
        with open(filename, encoding='utf-8-sig') as f:
            for m in re.finditer(r'^@\w+\{([^,\n]+),.*?^\}', f.read(), re.S | re.M):
                entries[concept_doi(m.group(1).replace('https://doi.org/', ''))] = m.group(0)
    return entries


def import_4tu(force=False):
    previous = read_previous(OUTPUT)

    # newest record per concept DOI
    found = {}

    def add(a):
        doi = concept_doi(a['doi'])
        # the concept DOI carries the metadata of the latest version; versioned DOIs are a fallback
        rank = (version(a['doi']) == 0, version(a['doi']))
        if doi not in found or rank > found[doi][0]:
            found[doi] = (rank, a)

    # datasets with a MAVLab staff member among the creators
    for name in sorted(STAFF):
        records = search('creators.name:*%s*' % name)
        if records is None:
            print('DataCite does not answer: %s not changed, run the script again later.' % OUTPUT)
            return False
        n = 0
        for r in records:
            if any(is_staff(c) for c in r['attributes'].get('creators', [])):
                add(r['attributes'])
                n += 1
        print('- %-10s %3d DataCite records, %3d with MAVLab staff' % (name, len(records), n))

    # datasets that reference a MAVLab paper; related DOIs are stored with or without https://doi.org/
    dois = paper_dois()
    staff_only = set(found)
    for i in range(0, len(dois), BATCH):
        query = ' OR '.join('"%s" OR "https://doi.org/%s"' % (d, d) for d in dois[i:i + BATCH])
        records = search('relatedIdentifiers.relatedIdentifier:(%s)' % query)
        if records is None:
            print('DataCite does not answer: %s not changed, run the script again later.' % OUTPUT)
            return False
        for r in records:
            add(r['attributes'])
    print('- %d MAVLab papers: %d more datasets that reference them' % (len(dois), len(set(found) - staff_only)))

    entries = []
    for doi, (_, a) in found.items():
        entries.append({'doi': doi, 'bib': to_bibtex(doi, a), 'year': str(a.get('publicationYear', '')),
                        'type': 'data', 'author': bib_name((a.get('creators') or [{}])[0]),
                        'title': clean(a['titles'][0]['title']) if a.get('titles') else ''})
    entries.sort(key=sort_key)

    if len(entries) < 0.8 * len(previous) and not force:
        print('Only %d datasets found, %d before: %s not changed. Check the DataCite search, or run with --force.' % (len(entries), len(previous), OUTPUT))
        return False

    tmp = OUTPUT + '.tmp'
    bibf = codecs.open(tmp, 'w', 'utf-8')
    bibf.write(u'﻿')
    bibf.write('# AUTOGENERATED by import_4tu_2021.py: 4TU.ResearchData datasets of MAVLab staff and of MAVLab papers\n')
    bibf.write('# Import from: ' + API + '?query=prefix:' + PREFIX + ' AND (creators.name:<staff> or relatedIdentifiers.relatedIdentifier:<paper DOI>)\n')
    bibf.write('# Sorted by year (newest first), type, first author and title\n\n')
    for e in entries:
        bibf.write(e['bib'] + '\n\n')
    bibf.close()
    os.replace(tmp, OUTPUT)

    new = [e['doi'] for e in entries if e['doi'] not in previous]
    removed = [d for d in previous if d not in found]
    print('================================================================')
    print(len(entries), 'datasets,', len(new), 'new,', len(removed), 'no longer found')
    for d in new:
        print('   new:', d)
    for d in removed:
        print('   no longer found:', d)
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download the 4TU.ResearchData datasets of MAVLab staff and of MAVLab papers')
    parser.add_argument('--force', action='store_true', help='write 4tu.bib even when far fewer datasets are found than before')
    sys.exit(0 if import_4tu(parser.parse_args().force) else 1)
