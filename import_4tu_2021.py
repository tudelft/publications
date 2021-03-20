# Download HTML
import requests
from lxml import html
import codecs



def download_list(page, filename):

    url = 'https://data.4tu.nl/search?q=mavlab'

    if page == 0:
        bibf = codecs.open(filename,'w', 'utf-8')
        bibf.write(u'\ufeff')
        bibf.write('# AUTOGENERATED\n# Import from: '+url+'\n\n\n')
        bibf.close()

    papernr = 1
    pageno = page
    done = False
    while not done:
        print('- Page',pageno)
        
        p = requests.get(url) # + '&page=%d' % pageno)
        print('Downloaded...\n')
        done = True

        f = p.text.split('https://data.4tu.nl/articles/dataset/')
        for ff in f:
            print(ff.split('">')[0])

        # Download dataverse page
        dom = html.fromstring(p.text.encode('utf-8'))

        # Get lines with dataset links
        # https://data.4tu.nl/articles/dataset/Monocular_obstacle_avoidance_with_persistent_Self-Supervised_Learning/12709508
        interest = [s for s in p.text.splitlines(True) if 'https://data.4tu.nl/articles/dataset/' in s]

        #parser = etree.HTMLParser(recover=True)
        #tree = etree.fromstring(url, parser=parser)
        for p in interest:
            pp = p #.strip('/dataset.xhtml?persistentId=doi:')
            print(pp)

        if False:
            pa = requests.get('https://scipython.com/apps/doi2bib/?doi='+pp) #.replace('/','%2F'))

            start = False
            bib = []
            for s in pa.text.splitlines(True):
                if '</textarea>' in s:
                    start = False
                if start:
                    bib.append(s.replace('@misc','@data').strip('\r\n'))
                if '<textarea' in s:
                    start = True


            
            bib = '\n'.join(bib)
            bib = bib.replace('&quot;', '\"')
            bib = bib.replace('https://doi.org/','')
                        
            # open and add, in case of error one can continue
            bibf = codecs.open(filename,'a', 'utf-8')
            bibf.write('# '+str(pageno)+', '+str(papernr)+'\n# '+'https://dataverse.nl'+p+'\n\n')
            bibf.write(bib)
            bibf.write('\n')
            bibf.close()

            papernr += 1

            # continue is at least 1 paper was found.
            #done = False


        pageno += 1

        # debug: stop after 1 page
        #if pageno >= 1:
        #    done = True

     


download_list(0, 'fourtu.bib')
