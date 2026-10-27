# Download the M.Sc. theses supervised in MAVLab from repository.tudelft.nl
#
#   msc.bib      theses with a MAVLab member (staff, postdoc or PhD student, see
#                mavlab_members.py) as supervisor (mentor, supervisor, coach)
#   msc_all.bib  theses with MAVLab staff in any role, also graduation committee only
#
# Only theses with MAVLab staff in the record are searched and kept: the repository
# covers all of TU Delft, where a postdoc's or PhD student's last name and initial
# (Wu, Y.; Li, S.) often belong to someone else.
#
# The repository has no documented export (the old CSV export is gone, #83). This
# uses the JSON endpoints of its own website:
#   /search/data?search_term=...&record_type=master_thesis&page=N   list of theses
#   /api/record/uuid:<id>                                          roles, date, faculty
#
# Entries that cannot be downloaded keep their previous version, and theses that
# the search no longer returns are kept, so a failed run never empties the files.
import codecs
import os
import re
import sys
import time

import requests

from mavlab_members import STAFF, member, staff

REPOSITORY = 'https://repository.tudelft.nl'

SUPERVISOR_ROLES = ['mentor', 'supervisor', 'coach']

SEARCH = ' OR '.join(STAFF)
PAUSE = 0.5         # seconds between requests
RETRIES = 3

FILES = {'msc.bib': 'supervisor', 'msc_all.bib': 'any role'}


def get_json(path, params=None):
    for attempt in range(1, RETRIES + 1):
        time.sleep(PAUSE)
        try:
            p = requests.get(REPOSITORY + path, params=params, timeout=60)
            if p.status_code == 200:
                return p.json()
            print('  HTTP', p.status_code, path)
        except (requests.RequestException, ValueError) as e:
            print('  error:', e)
        time.sleep(10 * attempt)
    return None


def is_staff(person):
    return staff(person['last_name'], person['first_name'])


def is_member(person):
    return member(person['last_name'], person['first_name']) is not None


def search_theses():
    theses, page = [], 1
    while True:
        d = get_json('/search/data', {'search_term': SEARCH, 'record_type': 'master_thesis',
                                      'page': page, 'sort': 'relevance'})
        if d is None:
            return None
        theses += d['records']
        print('- Search page', page, ':', len(theses), 'of', d['total'])
        if not d['records'] or len(theses) >= d['total']:
            return theses
        page += 1


def field(record, name):
    for section in record.get('metadata', {}).values():
        for item in section:
            if item.get('field') == name:
                return item.get('value')
    return None


def value(record, name):
    v = record.get(name)
    return v.get('value') if isinstance(v, dict) else v


def clean(txt):
    txt = re.sub(r'<[^>]+>', ' ', txt or '')
    return ' '.join(txt.replace('{', '(').replace('}', ')').split())


def bib_name(person):
    # name_part often has the full first name ('Jari Blom'), first_name only initials ('J.')
    last, full = person['last_name'].strip(), person.get('name_part', '').strip()
    first = full[:-len(last)].strip() if last and full.endswith(last) and len(full) > len(last) else person['first_name'].strip()
    return (last + ', ' + first).strip(', ')


def to_bibtex(uuid, record):
    authors = field(record, 'authors') or []
    contributors = field(record, 'contributors') or []
    faculty = [o['name'] for o in field(record, 'managing_organisation') or [] if o.get('type') == 'Faculty']
    note = ['%s (%s)' % (bib_name(c['person']), c.get('role', '')) for c in contributors]
    note.append('Delft University of Technology (degree granting institution)')
    if field(record, 'award_date'):
        note.append('graduation ' + field(record, 'award_date'))

    bib = '@mastersthesis{uuid:' + uuid + ',\n'
    bib += '\tabstract  = {' + clean(value(record, 'abstract')) + '},\n'
    bib += '\tauthor    = {' + ' and '.join(bib_name(a['person']) for a in authors) + '},\n'
    bib += '\tkeywords  = {' + clean('; '.join(value(record, 'keywords') or [])) + '},\n'
    bib += '\tnote      = {' + clean('; '.join(note)) + '},\n'
    bib += '\tschool    = {' + ('TU Delft ' + faculty[0] if faculty else 'Delft University of Technology') + '},\n'
    # the repository stores the subtitle separately; the website and Pure show 'title: subtitle'
    title = clean(value(record, 'title'))
    if clean(value(record, 'sub_title')):
        title += ': ' + clean(value(record, 'sub_title'))
    bib += '\ttitle     = {' + title + '},\n'
    bib += '\ttype      = {mathesis},\n'
    bib += '\turl       = {https://resolver.tudelft.nl/uuid:' + uuid + '},\n'
    bib += '\tyear      = {' + str(value(record, 'publication_year')) + '}\n'
    bib += '}'
    return bib


def read_previous(filename):
    entries = {}
    if os.path.exists(filename):
        with open(filename, encoding='utf-8-sig') as f:
            for bib in re.findall(r'^@mastersthesis\{uuid:.*?^\}', f.read(), re.S | re.M):
                entries[bib.split('uuid:', 1)[1].split(',', 1)[0]] = bib
    return entries


def year_of(bib):
    m = re.search(r'year\s*=\s*\{(\d+)', bib)
    return m.group(1) if m else '0'


def write(filename, entries):
    tmp = filename + '.tmp'
    bibf = codecs.open(tmp, 'w', 'utf-8')
    bibf.write(u'﻿')
    bibf.write('# AUTOGENERATED by import_repository.py: M.Sc. theses with a MAVLab member as ' + FILES[filename] + '\n')
    bibf.write('# Import from: ' + REPOSITORY + '/search?search_term=' + SEARCH.replace(' ', '+') + '&record_type=master_thesis\n\n\n')
    for uuid in sorted(entries, key=lambda u: (year_of(entries[u]), u), reverse=True):
        bibf.write(entries[uuid] + '\n\n')
    bibf.close()
    os.replace(tmp, filename)


def import_theses():
    previous = {f: read_previous(f) for f in FILES}
    theses = search_theses()
    if not theses:
        print('The repository search does not answer: nothing changed, run the script again later.')
        return False

    new = {f: {} for f in FILES}
    report = {'committee only': [], 'not MAVLab': 0, 'kept previous version': [], 'failed': []}
    found = set()
    for n, t in enumerate(theses, 1):
        uuid = t['id'].replace('Thing_', '')
        found.add(uuid)
        # the search result has no roles: skip theses without MAVLab contributor before downloading details
        if not any(is_staff(p) for p in t.get('contributors', [])):
            report['not MAVLab'] += 1
            continue
        record = get_json('/api/record/uuid:' + uuid)
        if record is None or not field(record, 'contributors'):
            for f in FILES:
                if uuid in previous[f]:
                    new[f][uuid] = previous[f][uuid]
            (report['kept previous version'] if any(uuid in previous[f] for f in FILES) else report['failed']).append(uuid)
            continue

        staff_roles = [c.get('role', '') for c in field(record, 'contributors') if is_staff(c['person'])]
        if not staff_roles:
            report['not MAVLab'] += 1
            continue
        bib = to_bibtex(uuid, record)
        new['msc_all.bib'][uuid] = bib
        member_roles = [c.get('role', '') for c in field(record, 'contributors') if is_member(c['person'])]
        if any(r in role for role in member_roles for r in SUPERVISOR_ROLES):
            new['msc.bib'][uuid] = bib
        else:
            report['committee only'].append(uuid)
        print(n, '/', len(theses), uuid, '|', ', '.join(member_roles))

    # theses the search no longer returns (deleted, renamed people, broken records) are kept
    kept_unfound = {f: [u for u in previous[f] if u not in found] for f in FILES}
    for f in FILES:
        for u in kept_unfound[f]:
            new[f][u] = previous[f][u]
    # every supervised thesis is also in msc_all.bib
    for u in new['msc.bib']:
        new['msc_all.bib'].setdefault(u, new['msc.bib'][u])
    for f in FILES:
        write(f, new[f])

    print('================================================================')
    for f in FILES:
        added = [u for u in new[f] if u not in previous[f]]
        removed = [u for u in previous[f] if u not in new[f]]
        print(f, ':', len(new[f]), 'theses,', len(added), 'new,', len(removed), 'removed,',
              len(kept_unfound[f]), 'kept although the search no longer finds them')
        if removed:
            print('   removed:', ' '.join(removed))
        if kept_unfound[f]:
            print('   kept:', ' '.join(kept_unfound[f]))
    print(len(report['committee only']), 'theses with MAVLab members only in the graduation committee (msc_all.bib only)')
    print(report['not MAVLab'], 'search results without MAVLab staff (other people with the same name)')
    if report['kept previous version'] or report['failed']:
        print(len(report['kept previous version']) + len(report['failed']), 'theses could not be downloaded:',
              ' '.join(report['kept previous version'] + report['failed']), '-> run the script again later.')
        return False
    return True


if __name__ == '__main__':
    sys.exit(0 if import_theses() else 1)
