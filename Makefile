

all: main.pdf
	./validate.py


main.pdf: cs_mav.bib
	make bib

bib:
	python ./makecite.py > main.tex && pdflatex main 2>&1 > /dev/null && bibtex main && pdflatex main

clean:
	rm -rf main.tex *.aux *.pdf report.txt *.log *.dvi *.blg *.bbl *.bak *.sav
