# Download all publications on https://mavlab.tudelft.nl into website_export.bib
#
# teachPress publishes its whole publication list (all types, with tags as keywords)
# as one BibTeX feed, the same entries as the export in wp-admin. The file is only
# replaced when the download looks complete.
import re
import sys

import requests

FEED = 'https://mavlab.tudelft.nl/?feed=tp_pub_bibtex'
OUTPUT = 'website_export.bib'
MIN_ENTRIES = 500    # fewer: the feed failed or changed, keep the previous file

r = requests.get(FEED, timeout=120)
r.encoding = 'utf-8'
n = len(re.findall(r'^@\w+\{', r.text, re.M))
if r.status_code != 200 or n < MIN_ENTRIES:
    print('Download failed (HTTP %d, %d entries): %s not changed' % (r.status_code, n, OUTPUT))
    sys.exit(1)

with open(OUTPUT, 'w', encoding='utf-8', newline='') as f:
    f.write('% Downloaded from ' + FEED + '\r\n% Encoding: UTF-8\r\n\r\n' + r.text)
print('%s: %d publications' % (OUTPUT, n))
