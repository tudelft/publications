

all: main.pdf


main.pdf: ../pure.bib
	make bib

bib:
	python ./makecite.py > main.tex
	pdflatex main
	bibtex main
	pdflatex main

clean:
	rm -rf main.tex *.aux *.pdf report.txt *.log *.dvi *.blg *.bbl *.bak *.sav
