

all:
	./validate.py

bib:
	./makecite.py > main.tex && latex main @&>1 > /dev/null && bibtex main

