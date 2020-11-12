

all: main.pdf
	./validate.py


main.pdf: mavlab.bib
	make bib

bib:
	python3 ./makecite.py > main.tex && latex main 2>&1 > /dev/null && bibtex main

clean:
	rm -rf *.tex *.aux *.pdf report.txt *.log *.dvi *.blg *.bbl *.bak *.sav
