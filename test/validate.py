#!/usr/bin/env python


import httplib
from urlparse import urlparse

count_url = 0
count_good = 0

def checkUrl(url):
    global count_url, count_good
    count_url += 1
    try:
        p = urlparse(url)
        conn = httplib.HTTPConnection(p.netloc)
        conn.request('HEAD', p.path)
        resp = conn.getresponse()
        if resp.status >= 400:
            print ("ERROR: link to " + url + " is failing.")
        else:
            count_good += 1
        if (resp.status >= 301) & (resp.status <= 303):
            # MOVED:
            new_url = resp.getheader('location')
            #if new_url != url:
            #    print("WARNING: MOVED from", url, " to ", new_url )
        return resp.status
    except ValueError:
        print("ERROR: Failed to load")
        return 404
    # < 400



def unlatex( string ):
    return string.replace("{\\%}","%")


def noaccent( txt ):
    return ''.join(x for x in unicodedata.normalize('NFKD', txt) if x in string.ascii_letters).lower()


def bib_tag( line):
    return line.split("=", 1)[0].strip();

def bib_tag_content( line):
    return unlatex(line.split("=", 1)[-1].strip().lstrip("=").rstrip(",").strip().lstrip("\"").rstrip("\"").lstrip("{").rstrip("}").strip());


with open("../mediacoverage.bib") as ft:
    bibfile = ft.read().splitlines()


def find_url( line ):
    if "=" in line:
        tag = bib_tag(line).lower()
        #print("TAG:", tag)
        if tag == "url":
            url = bib_tag_content(line) 
            resp_code = checkUrl ( url )
            print( resp_code, "URL", url )
        if tag == "pdf":
            url = bib_tag_content(line) 
            resp_code = checkUrl ( url )
            print( resp_code, "PDF", url )
        if tag == "file":
            url = bib_tag_content(line) 
            resp_code = checkUrl ( url )
            print( resp_code, "FILE", url )
        if tag == "doi":
            doi = bib_tag_content(line)
            resp_code = checkUrl ( "https://doi.org/" + doi )
            print( resp_code, "DOI", doi )
        if tag == "isbn":
            isbn = bib_tag_content(line)
            resp_code = checkUrl ( "http://isbndb.com/search/all?query=" + isbn )
            print( resp_code, "ISBN", isbn )
        if tag == "issn":
            issn = bib_tag_content(line)
            #resp_code = checkUrl ( "https://journals4free.com/?q=" + issn )
            resp_code = checkUrl ( "https://journals4free.com/link.jsp?l=" + issn )
            print( resp_code, "ISSN", issn )

if __name__ == '__main__':
    for line in bibfile:
        find_url( line )
    print("Report: ", count_good, " good out of ", count_url)
    #print checkUrl('http://www.stackoverflow.com') # True
    #print checkUrl('http://stackoverflow.com/notarealpage.html') # False
