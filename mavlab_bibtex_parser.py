import bibtexparser

from collections import OrderedDict
import re
import json

save_paper_lists = ['2020','2019','2018','2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003', '2002']

chairs = {
    'MAVLAB': ['Xu', 'Valles', 'coppola', 'scheper', 'mcguire', 'olejnik', 'dijk', 'wagter', 'croon', 'remes', 'ruijsink', 'karasek', 'armanini', 'caetano', 'tijmons', 'smeur', 'horst', 'tienen', 'hecke', 'li']}


def get_chair(name):
    for chair, staff in chairs.items():
        if name in staff:
            return chair
    return None




papers = dict()
totals = OrderedDict()


with open('mavlab.bib', encoding="utf8") as bibtex_file:
    bibtex_str = bibtex_file.read()

bib_database = bibtexparser.loads(bibtex_str)

for b in bib_database.entries:
    #print(b)
    if not ('year' in b) or not ('author' in b) or not ('ENTRYTYPE' in b) or not ('title' in b):
        print('ERROR!', b)
        print('------------------------------------------------------------------------')
        continue

    #print('-----',b['year'],b['ENTRYTYPE'])

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

    for person in authors.split(' and '):
        name = person.split(',')[0].split(' ')[-1].lower()
        chairname = get_chair(name)

        #print(person, name, chairname)
        if chairname:
            sum_pers = curyear[name]
            if doctype not in sum_pers:
                sum_pers[doctype] = []
            sum_pers[doctype].append(paperstring)
        


print(papers['2019'])
    

# dump back
# bibtex_str = bibtexparser.dumps(bib_database)



def print_summary():
    with open('mavlab_pure_summary.txt', 'w') as fout:
        fout.write(json.dumps(totals, sort_keys=True, indent=2, separators=(',', ': ')))

    for year in save_paper_lists:
        with open('mavlab_pure_papers_'+year+'.txt', 'w') as fout:
            fout.write(json.dumps(papers[year], sort_keys=True, indent=2, separators=('\n', ': ')))

    # Excel file with papers per year
    with open('mavlab_summary.csv', 'w') as fout:
        paper_types = ['Conference contribution','Article', 'Dissertation (TU Delft)', 'Special issue', 'Book', 'Chapter']
        fout.write('year')
        for t in paper_types:
            fout.write(',' + t)
        fout.write('\n')

        for i in totals:
            yeartotals = totals[i]['MAVLAB']
            print(i, yeartotals)

            fout.write(str(i))

            for t in paper_types:
                v = 0;
                if t in yeartotals:
                    v = yeartotals[t]

                fout.write(', ' + str(v))

            fout.write('\n' )

#print_summary()

with open('mavlab_url.txt', encoding='utf-8', mode='w') as fout:
    year = 9999
    for u in biburls:
        if (u[0] != year):
            year = u[0]
            fout.write("\n\n%% YEAR " + str(u[0]) + "\n\n")

        fout.write("\n\n% URL " + u[1] + "\n\n")
        bib = get_bib(u[1])
        fout.write(bib)
        #print(u[0], u[1])

print('Done')
