#!/usr/bin/env python


import httplib
from urlparse import urlparse

def checkUrl(url):
    p = urlparse(url)
    conn = httplib.HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    if resp.status >= 400:
        print ("ERROR: link to " + url + " is failing.")
    return resp.status
    # < 400



def unlatex( string ):
    return string.replace("{\\%}","%")


def noaccent( txt ):
    return ''.join(x for x in unicodedata.normalize('NFKD', txt) if x in string.ascii_letters).lower()


def bib_tag_content( line, tag ):
    return unlatex(line.strip().replace(tag,"").strip().lstrip("=").rstrip(",").strip().lstrip("{").rstrip("}").strip());


with open("mavlab.bib") as ft:
    bibfile = ft.read().splitlines()


def find_url( line ):
    if "url = " in line:
        url = bib_tag_content(line, "url") 
        resp_code = checkUrl ( url )
        print( resp_code, "URL", url )
    if "file = " in line:
        url = bib_tag_content(line, "file") 
        resp_code = checkUrl ( url )
        print( resp_code, "FILE", url )
    if "doi = " in line:
        doi = bib_tag_content(line, "doi")
        resp_code = checkUrl ( "https://doi.org/" + doi )
        print( resp_code, "DOI", doi )
    if "isbn = " in line:
        isbn = bib_tag_content(line, "isbn")
        resp_code = checkUrl ( "http://isbndb.com/search/all?query=" + isbn )
        print( resp_code, "ISBN", isbn )
    if "issn = " in line:
        issn = bib_tag_content(line, "issn")
        #resp_code = checkUrl ( "https://journals4free.com/?q=" + issn )
        resp_code = checkUrl ( "https://journals4free.com/link.jsp?l=" + issn )
        print( resp_code, "ISSN", issn )

if __name__ == '__main__':
    for line in bibfile:
        find_url( line )
    #print checkUrl('http://www.stackoverflow.com') # True
    #print checkUrl('http://stackoverflow.com/notarealpage.html') # False
