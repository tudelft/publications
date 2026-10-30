#!/usr/bin/env python
# Check the DOIs, URLs, PDF links, ISBNs and ISSNs of a bib file.
#
# usage: python validate.py [file.bib] [--offline]   (default: ../website/all.bib)
#
# - ISBN and ISSN: check digit only (no lookup: isbndb.com is a paid service now and
#   portal.issn.org answers 200 for any ISSN, so neither can tell a wrong number)
# - DOI: registered at doi.org (its handle API, so the publishers' bot checks do not matter)
# - URL, PDF, FILE: the link answers (HEAD, or GET when HEAD is not allowed)
# --offline only does the check digits. Online, every unique DOI and link is one request
# (~1500 for all.bib, ~20 min; a host that keeps timing out is skipped), so do not run it too often.
# The result is validate_report.csv (all checks); the problems are printed. A link that
# answers 403/429 or a bot check is 'blocked': the page may be fine, check it by hand.
import csv
import re
import sys
import time
from urllib.parse import urlparse

import requests
import bibtexparser
from bibtexparser.bparser import BibTexParser

HEADERS = {'User-Agent': 'MAVLab-publications-validate/1.0 (https://github.com/tudelft/publications)'}
TIMEOUT = 30
HOST_PAUSE = 1.0   # seconds between two requests to the same host
REPORT = 'validate_report.csv'

HOST_FAILS = 3     # a host that times out this many times in a row is skipped
last_request = {}
host_fails = {}


def polite_get(url, method):
    host = urlparse(url).netloc
    wait = last_request.get(host, 0) + HOST_PAUSE - time.time()
    if wait > 0:
        time.sleep(wait)
    try:
        return requests.request(method, url, headers=HEADERS, timeout=TIMEOUT,
                                allow_redirects=True, stream=True)
    finally:
        last_request[host] = time.time()


def check_isbn(isbn):
    d = re.sub(r'[^0-9Xx]', '', isbn).upper()
    if len(d) == 10:
        ok = sum((10 - i) * (10 if c == 'X' else int(c)) for i, c in enumerate(d)) % 11 == 0
    elif len(d) == 13 and d.isdigit():
        ok = sum((3 if i % 2 else 1) * int(c) for i, c in enumerate(d)) % 10 == 0
    else:
        return 'bad', 'not 10 or 13 digits'
    return ('ok', '') if ok else ('bad', 'wrong check digit')


def check_issn(issn):
    d = re.sub(r'[^0-9Xx]', '', issn).upper()
    if len(d) != 8 or not d[:7].isdigit():
        return 'bad', 'not 8 digits'
    check = (11 - sum((8 - i) * int(c) for i, c in enumerate(d[:7])) % 11) % 11
    return ('ok', '') if d[7] == ('X' if check == 10 else str(check)) else ('bad', 'wrong check digit')


def check_doi(doi):
    try:
        r = polite_get('https://doi.org/api/handles/' + doi, 'GET')
    except requests.RequestException as e:
        return 'error', type(e).__name__
    if r.status_code == 200:
        return 'ok', ''
    if r.status_code == 404:
        return 'bad', 'not registered at doi.org'
    return 'error', 'doi.org answered %d' % r.status_code


def check_url(url):
    if not re.match(r'https?://', url):
        return 'bad', 'not a web link'
    host = urlparse(url).netloc
    if host_fails.get(host, 0) >= HOST_FAILS:
        return 'error', 'host does not answer'
    try:
        r = polite_get(url, 'HEAD')
        if r.status_code in (400, 403, 404, 405, 501):   # many servers do not answer HEAD
            r = polite_get(url, 'GET')
            r.close()
    except requests.exceptions.SSLError:
        return 'bad', 'certificate error'
    except requests.exceptions.ConnectionError:
        return 'bad', 'no connection (domain gone?)'
    except requests.RequestException as e:
        host_fails[host] = host_fails.get(host, 0) + 1
        return 'error', type(e).__name__
    host_fails[host] = 0
    moved = r.url if r.url.rstrip('/') != url.rstrip('/') else ''
    if r.status_code in (403, 429) or r.headers.get('cf-mitigated'):
        return 'blocked', '%d %s' % (r.status_code, moved)
    if r.status_code >= 400:
        return 'bad', '%d %s' % (r.status_code, moved)
    return 'ok', moved


def split(value):
    return [v for v in re.split(r'[,;\s]+', value) if v]


def unlatex(value):
    return value.replace('\\%', '%').replace('\\_', '_').replace('\\&', '&').replace('{', '').replace('}', '')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    offline = '--offline' in sys.argv
    bibname = args[0] if args else '../website/all.bib'
    parser = BibTexParser(common_strings=True, ignore_nonstandard_types=False)
    with open(bibname, encoding='utf8') as f:
        entries = bibtexparser.load(f, parser).entries

    checks = []   # (key, field, value)
    for e in entries:
        for field in ('isbn', 'issn', 'doi', 'url', 'pdf', 'file'):
            if field not in e:
                continue
            values = split(e[field]) if field in ('isbn', 'issn') else [unlatex(e[field]).strip()]
            checks += [(e['ID'], field, v) for v in values]
    print(len(entries), 'entries,', len(checks), 'values to check', '(check digits only)' if offline else '')

    done = {}
    rows = []
    for key, field, value in checks:
        if field == 'isbn':
            result = check_isbn(value)
        elif field == 'issn':
            result = check_issn(value)
        elif offline:
            continue
        elif (field, value) in done:
            result = done[(field, value)]
        elif field == 'doi':
            doi = re.sub(r'^(https?://(dx\.)?doi\.org/|doi:?\s*)', '', value, flags=re.I)
            result = check_doi(doi)
            if result[0] == 'ok' and doi != value:
                result = ('bad', 'registered, but write only the DOI: ' + doi)
        else:
            result = check_url(value)
        done[(field, value)] = result
        rows.append([key, field, value, *result])
        if result[0] != 'ok':
            print('%-8s %-5s %-45s %s %s' % (result[0], field, key, value, result[1]))

    with open(REPORT, 'w', newline='', encoding='utf8') as f:
        w = csv.writer(f)
        w.writerow(['key', 'field', 'value', 'status', 'detail'])
        w.writerows(rows)
    counts = {s: sum(1 for r in rows if r[3] == s) for s in ('ok', 'bad', 'blocked', 'error')}
    print('Report:', ', '.join('%d %s' % (n, s) for s, n in counts.items()), '- all checks in', REPORT)
    return counts['bad'] == 0


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
