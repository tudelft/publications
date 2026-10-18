# Download the arXiv preprints of MAVLab staff into arxiv.bib
#
# arxiv2bibtex.org returns empty pages when it is asked too often. Entries that
# cannot be downloaded keep their previous version, and every entry is marked
# with the date of its last successful download. A new run only downloads the
# entries that are not up to date, so run the script again (e.g. half an hour
# later) until the summary reports that all entries are up to date.
#
#   python import_arxiv_2021.py          download new, failed and outdated entries
#   python import_arxiv_2021.py --all    download all entries again
import argparse
import codecs
import datetime
import os
import re
import time

import requests


SEARCH = ['guido de croon', 'christophe de wagter', 'ewoud smeur', 'sjoerd tijmons', 'salua hamaza', 'marija popovic']
SEARCH_URL = 'https://arxiv.org/search/?searchtype=author&size=200&query='
BIBTEX_URL = 'https://arxiv2bibtex.org/?format=bibtex&q='

PAUSE = 30          # seconds between two downloads from arxiv2bibtex
RETRIES = 3         # attempts per download, pausing RETRY_PAUSE * attempt seconds in between
RETRY_PAUSE = 60
MAX_FAILURES = 5    # stop downloading after this many failed entries in a row: the server is blocking us
MAX_AGE_DAYS = 20   # entries downloaded more recently are not downloaded again (unless --all)

# '# <code>: <url> [updated|failed <date>]' starts the block of every entry
BLOCK = re.compile(r'^# (\S+): ' + re.escape(BIBTEX_URL) + r'\S+(?: \[(updated|failed) (\d{4}-\d{2}-\d{2})\])?$')


def read_previous(filename):
    entries = {}
    if not os.path.exists(filename):
        return entries
    code = None
    with open(filename, encoding='utf-8-sig') as f:
        for line in f.read().splitlines():
            m = BLOCK.match(line)
            if m:
                code = m.group(1)
                date = datetime.date.fromisoformat(m.group(3)) if m.group(3) else None
                entries[code] = {'bib': [], 'status': m.group(2), 'date': date}
            elif code is not None:
                entries[code]['bib'].append(line)
    for e in entries.values():
        e['bib'] = '\n'.join(e['bib']).strip()
    return entries


def failed_entry(code, today):
    return {'bib': '# Error: could not find bibtex for ' + code, 'status': 'failed', 'date': today}


def write(filename, header, codes, entries, today):
    # write to a temporary file first, so an interrupted run never leaves a broken arxiv.bib
    tmp = filename + '.tmp'
    bibf = codecs.open(tmp, 'w', 'utf-8')
    bibf.write(u'﻿')
    bibf.write('\n'.join(header) + '\n')
    for code in codes:
        e = entries.get(code) or failed_entry(code, today)
        mark = ' [%s %s]' % (e['status'], e['date']) if e['status'] else ''
        bibf.write('# ' + code + ': ' + BIBTEX_URL + code + mark + '\n\n')
        bibf.write(e['bib'] + '\n\n\n')
    bibf.close()
    os.replace(tmp, filename)


def download(url, parse):
    # returns the parsed answer, or None when the server keeps sending empty answers
    for attempt in range(1, RETRIES + 1):
        try:
            p = requests.get(url, timeout=60)
            result = parse(p.text) if p.status_code == 200 else None
            if result:
                return result
            print('  empty answer (HTTP', p.status_code, ')')
        except requests.RequestException as e:
            print('  error:', e)
        if attempt < RETRIES:
            print('  attempt', attempt, 'failed, pausing', RETRY_PAUSE * attempt, 's')
            time.sleep(RETRY_PAUSE * attempt)
    return None


def parse_search(text):
    codes = []
    for s in text.splitlines(True):
        if 'arXiv:' in s:
            code = s.strip("\r\n").strip().split('arXiv:')[1].strip('</a>').strip('</span')
            if code not in codes:
                codes.append(code)
    return codes


def parse_bibtex(text, code):
    start = False
    bib = []
    for s in text.splitlines(True):
        if '</textarea>' in s:
            break # only 1
        if start:
            bib.append(s.strip('\r\n'))
        if '<textarea' in s:
            start = True
    bib = '\n'.join(bib)
    if not '@' in bib or not 'Title = {' in bib:
        return None
    bib += '\n\turl = {https://arxiv.org/abs/' + code + '},'
    bib += '\n\tpdf = {https://arxiv.org/pdf/' + code + '.pdf},'
    bib += '\n}'

    bib = bib.replace('Title = {','\ttitle = {')
    bib = bib.replace('Year = {','\tyear = {')
    bib = bib.replace('Author = {','\tauthor = {')
    bib = bib.replace('Eprint = {','\teprint = {')
    bib = bib.replace('Howpublished = {','\thowpublished = {')
    bib = bib.replace('Doi = {','\tdoi = {')
    return bib


def needs_download(e, today):
    return e is None or e['status'] != 'updated' or (today - e['date']).days >= MAX_AGE_DAYS


def import_arxiv(filename, download_all):
    today = datetime.date.today()
    previous = read_previous(filename)
    print('Previous', filename, 'has', len(previous), 'entries')

    # Find the papers of every person
    header = ['# AUTOGENERATED']
    codes = []
    for person in SEARCH:
        u = SEARCH_URL + person.replace(' ', '+')
        print('- Search', u)
        header.append('# Import from: ' + u)
        found = download(u, parse_search)
        if found is None:
            print('  no answer, keeping the previously found papers')
            header.append('# Search failed on ' + str(today))
            found = []
        for code in found:
            header.append('# - ' + code)
            if not code in codes:
                codes.append(code)
        time.sleep(3)

    # Never drop a paper because a search failed
    for code in previous:
        if not code in codes:
            codes.append(code)

    entries = dict(previous)
    todo = [c for c in codes if download_all or needs_download(entries.get(c), today)]
    print(len(todo), 'of', len(codes), 'entries to download')

    report = {'new': [], 'updated': [], 'unchanged': [], 'kept previous version': [], 'failed': [], 'not tried': []}
    failures = 0
    for counter, code in enumerate(todo, 1):
        if failures >= MAX_FAILURES:
            print('Too many failures in a row: the server is blocking, stop downloading')
            report['not tried'] = todo[counter - 1:]
            break

        print(counter, '/', len(todo), ': ', code)
        bib = download(BIBTEX_URL + code, lambda text: parse_bibtex(text, code))
        old = entries.get(code)
        if bib is None:
            failures += 1
            if old and old['status'] != 'failed':
                report['kept previous version'].append(code)
            else:
                entries[code] = failed_entry(code, today)
                report['failed'].append(code)
        else:
            failures = 0
            if old is None or old['status'] == 'failed':
                report['new'].append(code)
            elif old['bib'] != bib:
                report['updated'].append(code)
            else:
                report['unchanged'].append(code)
            entries[code] = {'bib': bib, 'status': 'updated', 'date': today}

        # save after every download, so an interrupted run keeps its progress
        write(filename, header, codes, entries, today)
        if counter < len(todo):
            time.sleep(PAUSE)

    write(filename, header, codes, entries, today)

    print('================================================================')
    print('Summary:', ', '.join('%d %s' % (len(v), k) for k, v in report.items()))
    for k in ['new', 'updated', 'kept previous version', 'failed', 'not tried']:
        if report[k]:
            print(' -', k + ':', ' '.join(report[k]))
    remaining = [c for c in codes if needs_download(entries.get(c), today)]
    if remaining:
        print(len(remaining), 'entries are not up to date: run the script again later to retry them.')
    else:
        print('All', len(codes), 'entries are up to date.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download the arXiv preprints of MAVLab staff')
    parser.add_argument('--all', action='store_true', help='download all entries again')
    parser.add_argument('--file', default='arxiv.bib', help='output bib file (default: arxiv.bib)')
    args = parser.parse_args()
    import_arxiv(args.file, args.all)
