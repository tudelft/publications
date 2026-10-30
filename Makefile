


all:
	python ./filter_pure_mavlab.py
	make -C ./website
	python filter_by_user.py

# quality control of website/all.bib: LaTeX/BibTeX (test/report.txt), then the DOIs, URLs,
# PDF links, ISBNs and ISSNs (test/validate_report.csv; ~1500 internet lookups, ~20 min)
validate:
	-make -C ./test
	make -C ./test validate
