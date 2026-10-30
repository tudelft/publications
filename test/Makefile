
# the bib file to test: make BIB=../pure.bib
BIB ?= ../website/all.bib

all: main.pdf

# LaTeX + BibTeX, then LaTeX again until all citations are resolved (at most 5 runs);
# the warnings and errors of BibTeX and LaTeX end up in report.txt (not the @online media
# entries, which BibTeX styles do not know)
main.pdf: $(BIB) makecite.py
	python ./makecite.py $(BIB) > main.tex
	-pdflatex -interaction=nonstopmode main > /dev/null
	-bibtex main > /dev/null
	for i in 1 2 3 4 5; do \
		pdflatex -interaction=nonstopmode main > /dev/null; \
		grep -q "Rerun to get" main.log || break; \
	done; true
	{ grep -E "^(Warning--|Repeated entry|I was expecting|You're missing|.*---line [0-9]+ of file)" main.blg | grep -v "isn't style-file defined"; \
	  grep -E "^(! |LaTeX Warning: Citation|Overfull)" main.log; } > report.txt; true
	@echo "BibTeX: `grep -c -E '^Warning--' report.txt` warnings, `grep -c -E '^Repeated entry|---line' main.blg` errors;" \
	      "LaTeX: `grep -c '^! ' main.log` errors, `grep -c 'Citation .* undefined' main.log` undefined citations; see test/report.txt"

# check the DOIs, URLs, PDF links, ISBNs and ISSNs (~1500 internet lookups, ~20 min)
validate:
	python ./validate.py $(BIB)

clean:
	rm -rf main.tex *.aux *.pdf report.txt *.log *.dvi *.blg *.bbl *.bak *.sav validate_report.csv
