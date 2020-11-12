import bibtexparser
import json

from collections import OrderedDict

chairs = {
    'MAVLAB': ['Xu', 'Valles', 'coppola', 'scheper', 'mcguire', 'olejnik', 'dijk', 'wagter', 'croon', 'remes',
               'ruijsink', 'karasek', 'armanini', 'caetano', 'tijmons', 'smeur', 'horst', 'tienen', 'hecke', 'li',
               'percin', 'tay', 'noyon']}


def get_chair(name):
    for chair, staff in chairs.items():
        if name in staff:
            return chair
    return None


papers = dict()
totals = OrderedDict()

mavlabpapers = {}


parser = bibtexparser.bparser.BibTexParser(common_strings=True)
with open('cs.bib', encoding="utf8") as bibtex_file:
    bibtex_str = bibtex_file.read()

bib_database = bibtexparser.loads(bibtex_str, parser=parser)

mavlab_database = bibtexparser.bibdatabase.BibDatabase()
rest = bibtexparser.bibdatabase.BibDatabase()

print('================================================================')

for b in bib_database.entries:
    #print(b)
    if not ('year' in b) or not ('author' in b) or not ('ENTRYTYPE' in b) or not ('title' in b):
        print('ERROR!', b)
        print('------------------------------------------------------------------------')
        continue


    # Paper
    year = b['year']
    title = b['title']
    doctype = b['ENTRYTYPE']
    authors = b['author']

    
    if year not in totals:
        papers[year] = []
        totals[year] = {key:{} for key in chairs.keys()}
        totals[year].update({staff:{} for chair in chairs.values() for staff in chair})

    curyear = totals[year]
    curyear_papers = papers[year]
    paperstring = b['ID'] + ': ' + doctype
    curyear_papers.append(paperstring)
    papers[year] = curyear_papers

    mavlabpaper = 0
    for person in authors.split(' and '):
        if ',' in person:
            # last name left of comma: right part
            name = person.split(',')[0].split(' ')[-1].strip().strip('{').strip('}').strip().lower()
        else:
            # last name
            name = person.split(' ')[-1].strip().strip('{').strip('}').strip().lower()
        chairname = get_chair(name)
        if chairname == 'MAVLAB':
            mavlabpaper = 1

        #print(person, name, chairname)
        if chairname:
            sum_pers = curyear[name]
            if doctype not in sum_pers:
                sum_pers[doctype] = []
            sum_pers[doctype].append(paperstring)

    #print('-----',b['year'],b['ENTRYTYPE'],mavlabpaper)
        

    if mavlabpaper == 1:
        key = (year, doctype)
        if not key in mavlabpapers:
            mavlabpapers[key] = 0
        mavlabpapers[key] += 1
        mavlab_database.entries.append(b)
    else:
        rest.entries.append(b)
    

print(mavlabpapers)
    

# dump back
writer = bibtexparser.bwriter.BibTexWriter()
writer.indent = '\t'     # indent entries with 4 spaces instead of one
writer.order_entries_by = 'year'
writer.align_values = True
with open('cs_mav.bib', 'w', encoding='utf8') as bibfile:
    bibfile.write(writer.write(mavlab_database))
    


with open('cs_nomav.bib', 'w', encoding='utf8') as bibfile:
    bibfile.write(writer.write(rest))


def print_summary():

    # Excel file with papers per year
    with open('mavlab_summary.csv', 'w') as fout:
        paper_types = ['article','inproceedings', 'phdthesis', 'conference', 'book', 'misc']
        fout.write('year')
        for t in paper_types:
            fout.write(';' + t)
        fout.write('\n')

        for y in range(2003,2021):
            fout.write(str(y) + ';')
            for t in paper_types:
                key = (str(y),t)
                #print(key)

                if key in mavlabpapers:
                    fout.write(str(mavlabpapers[key]) + ';')
                else:
                    fout.write('0;')
                    
            fout.write('\n' )

print_summary()

print('Done')
