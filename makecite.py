#!/usr/bin/env python

with open("mavlab.bib") as ft:
    bibfile = ft.read().splitlines()

count = 0

def find_cite( line ):
    global count
    if "@" in line:
        cite=line.split("{")
        if len(cite) > 1:
            print("\\cite{"+cite[1].rstrip(",").strip()+"}, ")
        count = count + 1;

if __name__ == '__main__':
    print("\\documentclass{article}\n\\title{Test}\n\\author{BibTest}\n\\begin{document}\n\n")
    for line in bibfile:
        find_cite( line )
    print("\nBib file has ",count, " entries.\n\n\\bibliographystyle{unsrt}\n\\bibliography{mavlab}\n\n\\end{document}\n")
