from lxml import html
import requests
from collections import OrderedDict
import re
import json

save_paper_lists = ['2018','2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003', '2002']

chairs = {
    'MAVLAB': ['Xu', 'Valles', 'coppola', 'scheper', 'mcguire', 'olejnik', 'dijk', 'wagter', 'croon', 'remes', 'ruijsink', 'karasek', 'armanini', 'caetano', 'tijmons', 'smeur', 'horst', 'tienen', 'hecke', 'li']}



papers = dict()
totals = OrderedDict()
biburls = []

def get_chair(name):
    for chair, staff in chairs.items():
        if name in staff:
            return chair
    return None

def get_bib(url):
    p = requests.get(url)
    dom = html.fromstring(p.text)
    lst = dom.body.find_class('publication_export')
    bib = ""
    for i in lst:
        try:
            if (i.text == 'BibTeX'):
                print('FOUND BIB')
                for j in range(0,20):
                    txt = i.getnext()[j].text
                    if  not "  abstract " in txt:
                        bib = bib + txt
                        print(txt.strip())
                    if txt == '}':
                        break;
        except:
            pass
    return bib


def download_list():
    pageno = 0
    done = False
    while not done:
        print('Page',pageno)
        p = requests.get('https://pure.tudelft.nl/portal/en/organisations/control--simulation(8055ace1-b565-4d06-8366-aa18bc5e3828)/publications.html?page=%d&pageSize=100' % pageno)

        dom = html.fromstring(p.text)

        portal_list = dom.body.find_class('portal_list')

        lst = portal_list[0].find_class('portal_list_item')
        for i in lst:
            try:
                # Parse the HTML to find the key elements
                title = i.find_class('title')[0].getchildren()[0].getchildren()[0].text
                url = i.find_class('title')[0].getchildren()[0].attrib.get('href').replace('.html','/export.html')
                date  = i.find_class('date')[0].text
                date = re.match(r'.*([1-3][0-9]{3})', date).group(1)
                doctype  = i.find_class('type_classification')[0].text


                if date not in totals:
                    papers[date] = {}
                    totals[date] = {key:{} for key in chairs.keys()}
                    totals[date].update({staff:{} for chair in chairs.values() for staff in chair})

                curyear = totals[date]
                curyear_paper = papers[date]
                paperstring = title + ': ' + i.text_content().split('Research output:')[0].lstrip(title)

                # First always increase C&S
                chair = curyear['MAVLAB']
                asgnchair = []
                mavlabpaper = 0
                for person in i.find_class('link person'):
                    name = person.getchildren()[0].text.split(',')[0].split(' ')[-1].lower()
                    chairname = get_chair(name)
                    if chairname:
                        sum_pers = curyear[name]
                        if doctype not in sum_pers:
                            sum_pers[doctype] = []
                        sum_pers[doctype].append(paperstring)
                        if chairname not in asgnchair:
                            chair = curyear[chairname]
                            chair[doctype] = chair.get(doctype, 0) + 1
                            asgnchair.append(chairname)
                            mavlabpaper = 1

                if mavlabpaper:
                    print('-', mavlabpaper,  title)
                    #print('-', mavlabpaper,  url)
                    biburls.append((date,url))
                    #get_bib(url)
                    if doctype not in curyear_paper:
                        curyear_paper[doctype] = [paperstring]
                    else:
                        curyear_paper[doctype].append(paperstring)


            except:
                pass

        if len(dom.find_class('portal_navigator_next portal_navigator_next_disabled')) > 0:
            done = True
        else:
            pageno += 1

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

download_list()
print_summary()

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
