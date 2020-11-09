from lxml import html
import requests
from collections import OrderedDict
import re
import json
import xml.etree.ElementTree as ET

save_paper_lists = ['2020','2019','2018','2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006', '2005', '2004', '2003', '2002']

chairs = {
    'MAVLAB': ['Xu', 'Valles', 'coppola', 'scheper', 'mcguire', 'olejnik', 'dijk', 'wagter', 'croon', 'remes', 'ruijsink', 'karasek', 'armanini', 'caetano', 'tijmons', 'smeur', 'horst', 'tienen', 'hecke', 'li']}




#root = ET.parse('https://research.tudelft.nl/en/organisations/control-operations/publications/?format=rss&page=5').getroot()

def download_list():
    pageno = 0
    done = False
    while not done:
        print('Page',pageno)
        
        p = requests.get('https://research.tudelft.nl/en/organisations/control-operations/publications/?format=rss&page=%d' % pageno)

        done = True

        root = ET.fromstring(p.text)
        for pub in root.findall('channel/item'):
            title = pub.findall('title')[0].text
            link = pub.findall('link')[0].text
            date = pub.findall('pubDate')[0].text
            description = pub.findall('description')[0].text
            dom = html.fromstring(description)
            journal  = dom.body.find_class('journal')
            print('-',title)
            if len(journal) > 0:
                print(' --> ', html.tostring(journal[0]))
                vol = dom.body.find_class('volume')
                if len(vol) > 0:
                    print('      ', html.tostring(vol[0]))
                nr = dom.body.find_class('journalnumber')
                if len(nr) > 0:
                    print('      ', html.tostring(nr[0]))
                

            # Found something, continue
            done = False


        pageno += 1

        if pageno >= 1:
            done = True




download_list()
