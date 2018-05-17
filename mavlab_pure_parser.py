from lxml import html
import requests
from collections import OrderedDict
import re
import json

save_paper_lists = ['2018','2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003', '2002']

chairs = {
    'MAVLAB': ['coppola', 'scheper', 'mcguire', 'olejnik', 'dijk', 'wagter', 'croon', 'remes', 'ruijsink', 'karasek', 'armanini', 'caetano', 'tijmons', 'smeur', 'host', 'tienen', 'hecke', 'li']}

pageno = 0

done = False

papers = dict()
totals = OrderedDict()

def get_chair(name):
    for chair, staff in chairs.items():
        if name in staff:
            return chair
    return None

while not done:
    print('Page',pageno)
    p = requests.get('https://pure.tudelft.nl/portal/en/organisations/control--simulation(8055ace1-b565-4d06-8366-aa18bc5e3828)/publications.html?page=%d&pageSize=100' % pageno)

    dom = html.fromstring(p.text)

    portal_list = dom.body.find_class('portal_list')

    lst = portal_list[0].find_class('portal_list_item')
    for i in lst:
        try:
            title = i.find_class('title')[0].getchildren()[0].getchildren()[0].text
            date  = i.find_class('date')[0].text
            date = re.match(r'.*([1-3][0-9]{3})', date).group(1)
            doctype  = i.find_class('type_classification')[0].text
            if date not in totals:
                papers[date] = {}
                totals[date] = {key:{} for key in chairs.keys()}
                totals[date].update({staff:{} for chair in chairs.values() for staff in chair})
                #print(list(totals[date].keys()))
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
                if doctype not in curyear_paper:
                    curyear_paper[doctype] = [paperstring]
                else:
                    curyear_paper[doctype].append(paperstring)
            #    chair[doctype] = chair.get(doctype, 0) + 1

        except:
            pass

    if len(dom.find_class('portal_navigator_next portal_navigator_next_disabled')) > 0:
        done = True
    else:
        pageno += 1

with open('cs_pure_summary.txt', 'w') as fout:
    fout.write(json.dumps(totals, sort_keys=True, indent=2, separators=(',', ': ')))

for year in save_paper_lists:
    with open('cs_pure_papers_'+year+'.txt', 'w') as fout:
        fout.write(json.dumps(papers[year], sort_keys=True, indent=2, separators=('\n', ': ')))
    # for date, lst in totals.items():
    #     fout.write(date + '\n')
    #     for doctype, count in lst.items():
    #         fout.write('    %s: %d\n' % (doctype, count))

with open('mavlab_summary.csv', 'w') as fout:
    fout.write('year,conference,journal,phd,book,chapter,special\n')
    for i in totals:
        yeartotals = totals[i]['MAVLAB']
        print(i, yeartotals)

        conf = 0
        if 'Conference contribution' in yeartotals:
            conf = yeartotals['Conference contribution']
        
        article = 0
        if 'Article' in yeartotals:
            article = yeartotals['Article']
        
        phd = 0
        if 'Dissertation (TU Delft)' in yeartotals:
            phd = yeartotals['Dissertation (TU Delft)']
        
        spec = 0
        if 'Special issue' in yeartotals:
            spec = yeartotals['Special issue']
        
        book = 0
        if 'Book' in yeartotals:
            book = yeartotals['Book']
        
        chapt = 0
        if 'Chapter' in yeartotals:
            chapt = yeartotals['Chapter']
        
        fout.write(str(i) + ", " + str(conf) + ", " + str(article) + ", " + str(phd) + ", " + str(book) + ", " + str(chapt) + ", " + str(spec) + "\n" )

print('Done')
