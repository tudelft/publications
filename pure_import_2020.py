# Download HTML
import requests
from lxml import html
# Parse RSS-XML
import xml.etree.ElementTree as ET
# Strip HTML
from bs4 import BeautifulSoup
# Store FILE
import codecs


#root = ET.parse('https://research.tudelft.nl/en/organisations/control-operations/publications/?format=rss&page=5').getroot()

def download_list(page, filename):

    if page == 0:
        bibf = codecs.open(filename,'w', 'utf-8')
        bibf.write(u'\ufeff')
        bibf.close()

    papernr = 1
    pageno = page
    done = False
    while not done:
        print('- Page',pageno)
        
        #p = requests.get('https://research.tudelft.nl/en/organisations/control-operations/publications/?format=rss&page=%d' % pageno)
        p = requests.get('https://research.tudelft.nl/en/organisations/control-simulation/publications/?format=rss&page=%d' % pageno)

        done = True

        root = ET.fromstring(p.text)
        for pub in root.findall('channel/item'):
            title = pub.findall('title')[0].text
            link = pub.findall('link')[0].text
            
            #description = pub.findall('description')[0].text
            #dom = html.fromstring(description)
            #journal  = dom.body.find_class('journal')

            p = requests.get(link)
            dom = html.fromstring(p.text)
            
            bib = dom.body.get_element_by_id('cite-BIBTEX').getchildren()[0]
                        
            print(str(papernr) + ' ',title)

            # open and add, in case of error one can continue
            bibf = codecs.open(filename,'a', 'utf-8')
            bibf.write('# '+str(pageno)+', '+str(papernr)+'\n# '+title+'\n# '+link+'\n\n')
            
            # dump bibtex into file
            for b in bib.getchildren():
                soup = BeautifulSoup(html.tostring(b),features="lxml")
                txt = soup.get_text()
                if '}' in txt:
                    bibf.write('\turl       = "'+ link +'",\n')

                if ' url  ' in txt:
                    bibf.write(txt.replace(' url  ', ' url2 ')+'\n')    
                elif not ' abstract ' in txt:
                    #print(txt)
                    bibf.write(txt+'\n')
            #print('')

            bibf.write('\n')
            bibf.close()


            papernr += 1

            # continue is at least 1 paper was found.
            done = False


        pageno += 1

        # debug: stop after 1 page
        #if pageno >= 1:
        #    done = True

     


# To continue downloading, type a non-zero page.
# page=0 resets the output
download_list(0, 'cs.bib')
