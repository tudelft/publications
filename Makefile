

all:
	./validate.py

bib:
	./makecite.py > main.tex && latex main && bibtex main

