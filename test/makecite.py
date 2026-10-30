#!/usr/bin/env python
# Write a LaTeX document (to stdout) that cites every entry of a bib file, so that
# LaTeX/BibTeX show the entries that do not compile or render badly.
#
# usage: python makecite.py [file.bib]   (default: ../website/all.bib)
import re
import sys

bibname = sys.argv[1] if len(sys.argv) > 1 else '../website/all.bib'

with open(bibname, encoding="utf8") as ft:
    keys = re.findall(r'^\s*@\s*(?!comment|string|preamble)\w+\s*\{\s*([^,\s]+)\s*,', ft.read(), re.M | re.I)

if __name__ == '__main__':
    print("\\documentclass{article}\n\\usepackage[T1]{fontenc}\n\\usepackage{url}\n"
          "\\title{Test}\n\\author{BibTest}\n\\begin{document}\n")
    for key in keys:
        print("\\cite{" + key + "}, ")
    print("\nBib file has ", len(keys), " entries.\n\n\\bibliographystyle{unsrt}\n"
          "\\bibliography{" + re.sub(r'\.bib$', '', bibname) + "}\n\n\\end{document}")
