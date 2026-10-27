# MAVLab members (staff, postdocs, PhD students, former members): last name -> first initials
#
# Used by filter_pure_mavlab.py (MAVLab papers in Pure) and import_repository.py
# (M.Sc. theses with a MAVLab member as mentor). A person matches on the last word of
# the last name plus the first letter of the first name, so short names such as Li, Ho
# and Wu, or other people with the same last name (J. Popovic, T.M. Croon), do not
# match. Several letters allow several people or spellings; '' accepts any first name.
# Add new MAVLab members here.
import re
import unicodedata

MEMBERS = {
    # staff
    'croon': 'G', 'wagter': 'C', 'remes': 'B', 'smeur': 'E', 'hamaza': 'S', 'karasek': 'M',
    'popovic': 'M', 'scheper': 'K', 'dupeyroux': 'J', 'tijmons': 'S',
    # postdocs, PhD students and former members
    'valles': 'F', 'coppola': 'M', 'mcguire': 'K', 'olejnik': 'D', 'dijk': 'T', 'ruijsink': 'HR',
    'armanini': 'S', 'caetano': 'J', 'horst': 'E', 'tienen': 'F', 'hecke': 'K', 'oliveira': 'J',
    'lentink': 'D', 'percin': 'M', 'tay': '', 'noyon': '', 'ferede': 'R', 'bahnam': 'S',
    'mancinelli': 'A', 'stroobants': 'S', 'hagenaars': 'J', 'ho': 'H', 'li': 'S', 'wu': 'Y',
    'altena': 'A', 'bredenbeck': 'A', 'ramirez': 'J', 'farinha': 'A', 'ponti': 'T', 'blaha': 'T',
    'nowak': '',
}

# staff (assistant/associate/full professors): the M.Sc. thesis search
STAFF = ['croon', 'wagter', 'remes', 'smeur', 'hamaza', 'karasek', 'popovic', 'scheper', 'dupeyroux', 'tijmons']


def ascii_lower(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()


def staff(last_name, first_name):
    return member(last_name, first_name) in STAFF


def member(last_name, first_name):
    # the MAVLab last name of this person, or None
    last = re.sub(r'[^a-z -]', '', ascii_lower(last_name)).replace('-', ' ').split()
    first = re.sub(r'[^a-z]', '', ascii_lower(first_name))[:1].upper()
    if not last or last[-1] not in MEMBERS:
        return None
    initials = MEMBERS[last[-1]]
    return last[-1] if not initials or first in initials else None
