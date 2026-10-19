# Download the publications that are online on https://mavlab.tudelft.nl into website_export.bib
#
# Replaces the manual teachPress export in WordPress: every publication on the
# public pages carries its teachPress BibTeX entry, the same as the admin export.
#   /publications/     all publications except media, 50 per page
#   /media-coverage/   media items (teachPress type 'online')
import html
import re
import time

import requests


WEBSITE = 'https://mavlab.tudelft.nl'
PAGES = ['/publications/', '/media-coverage/']
OUTPUT = 'website_export.bib'


def download_page(path):
    entries, page = [], 1
    while True:
        p = requests.get(WEBSITE + path, params={'limit': page, 'tgid': '', 'yr': '', 'type': '', 'usr': '', 'auth': '', 'tsr': ''}, timeout=60)
        p.raise_for_status()
        found = [html.unescape(b.replace('<br />', '')).strip()
                 for b in re.findall(r'<div class="tp_bibtex_entry"><pre>(.*?)</pre>', p.text, re.S)]
        total = re.findall(r'(\d+) entries', p.text)
        print('-', path, 'page', page, ':', len(found), 'entries', '(of %s)' % total[0] if total else '')
        if not found or any(b in entries for b in found):
            return entries
        entries += found
        # the page links show how many pages there are
        if page >= max([int(x) for x in re.findall(r'[?&]limit=(\d+)', p.text)] + [1]):
            return entries
        page += 1
        time.sleep(1)


def key(bib):
    return bib.split('{', 1)[1].split(',', 1)[0]


if __name__ == '__main__':
    entries = {}
    for path in PAGES:
        for bib in download_page(path):
            entries.setdefault(key(bib), bib)
    if len(entries) < 500:
        raise SystemExit('Only %d entries found: the website layout may have changed, %s not written.' % (len(entries), OUTPUT))

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        f.write('% Downloaded from ' + WEBSITE + ' (' + ', '.join(PAGES) + ') by download_website.py\n')
        f.write('% Encoding: UTF-8\n\n')
        f.write('\n\n'.join(entries.values()) + '\n')
    print(len(entries), 'entries written to', OUTPUT)
