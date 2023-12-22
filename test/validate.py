#!/usr/bin/env python

import pandas as pd
import requests

df = pd.DataFrame()

#import httplib
#from urlparse import urlparse

count_url = 0
count_good = 0

def checkUrl(url_type, url):
    global count_url #, count_good
    global df
    count_url += 1

    if True: # not ('resolver.tudelft.nl/uuid' in url) and not ('arxiv.org/' in url):
        status = 'FAIL'
        redir = ''

        try:
            r = requests.head(url)
            status = r.status_code
            redir = r.headers['Location']
        except:
            print(url, 'FAILED')
        
        dfr = {'url': url, 'type':url_type, 'status': status, 'redirect': redir}
        df = df.append(dfr, ignore_index = True)
        print(dfr)
    else:
        print(url_type, url)
        
#    try:
#        p = urlparse(url)
#        conn = httplib.HTTPConnection(p.netloc)
#        conn.request('HEAD', p.path)
#        resp = conn.getresponse()
#        if resp.status >= 400:
#            print ("ERROR: link to " + url + " is failing.")
#        else:
#            count_good += 1
#        if (resp.status >= 301) & (resp.status <= 303):
#            # MOVED:
#            new_url = resp.getheader('location')
#            #if new_url != url:
#            #    print("WARNING: MOVED from", url, " to ", new_url )
#        return resp.status
#    except ValueError:
#        print("ERROR: Failed to load")
#        return 404
#    # < 400



def unlatex( string ):
    return string.replace("{\\%}","%")


def noaccent( txt ):
    return ''.join(x for x in unicodedata.normalize('NFKD', txt) if x in string.ascii_letters).lower()


def bib_tag( line):
    return line.split("=", 1)[0].strip();

def bib_tag_content( line):
    return unlatex(line.split("=", 1)[-1].strip().lstrip("=").rstrip(",").strip().lstrip("\"").rstrip("\"").lstrip("{").rstrip("}").strip());


with open("../website/all.bib", encoding="utf8") as ft:
    bibfile = ft.read().splitlines()


def find_url( line ):
    if "=" in line:
        tag = bib_tag(line).lower()
        #print("TAG:", tag)
        if tag == "url":
            url = bib_tag_content(line) 
            resp_code = checkUrl ( "URL", url )
            #print( resp_code, "URL", url )
        if tag == "pdf":
            url = bib_tag_content(line) 
            resp_code = checkUrl ( "PDF", url )
            #print( resp_code, "PDF", url )
        if tag == "file":
            url = bib_tag_content(line) 
            resp_code = checkUrl ( "FILE", url )
            #print( resp_code, "FILE", url )
        if tag == "doi":
            doi = bib_tag_content(line)
            resp_code = checkUrl ( "DOI", "https://doi.org/" + doi )
            #print( resp_code, "DOI", doi )
        if tag == "isbn":
            isbn = bib_tag_content(line)
            resp_code = checkUrl ( "ISBN", "http://isbndb.com/search/all?query=" + isbn )
            #print( resp_code, "ISBN", isbn )
        if tag == "issn":
            issn = bib_tag_content(line)
            #resp_code = checkUrl ( "https://journals4free.com/?q=" + issn )
            resp_code = checkUrl ( "ISSN", "https://portal.issn.org/resource/ISSN/" + issn )
            #print( resp_code, "ISSN", issn )

if __name__ == '__main__':
    for line in bibfile:
        find_url( line )
    print("Report: ", count_good, " good out of ", count_url)
    df.to_csv('all_urls_from_bib.csv')
    
    #print checkUrl('http://www.stackoverflow.com') # True
    #print checkUrl('http://stackoverflow.com/notarealpage.html') # False

    
