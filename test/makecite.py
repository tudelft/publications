#!/usr/bin/env python

bibname = '../pure'

with open(bibname+'.bib', encoding="utf8") as ft:
    bibfile = ft.read().splitlines()

count = 0
year = 2016
bibitem = ''

def find_cite( line ):
    global count
    global bibitem
    global year
    if "## " + str(year) in line:
        #print("\\section{"+str(year)+"}")
        year = year - 1
    if len(line) > 0 and line[0] == '@' :
        cite=line.split("{")
        if len(cite) > 1:
            if cite[0].lstrip("@").strip() != bibitem:
                bibitem = cite[0].lstrip("@").strip()
                #print("\\subsection{"+bibitem+"}")
            print("\\cite{"+cite[1].rstrip(",").strip().rstrip(",").strip()+"}, ")
        count = count + 1;

if __name__ == '__main__':
    print("\\documentclass{article}\n\\title{Test}\n\\author{BibTest}\n\\begin{document}\n\n")
    for line in bibfile:
        #update_year( line )
        find_cite( line )
    print("\nBib file has ",count, " entries.\n\n\\bibliographystyle{unsrt}\n\\bibliography{"+(bibname)+"}\n\n\\end{document}\n")
