
# the bib files that make up all.bib
SOURCES = ../arxiv_nopub.bib ../dataverse.bib ../mavlab_nopure.bib ../mediacoverage.bib ../pure.bib ../msc.bib ../4tu.bib

all:
	# cd  ../ && python ./filter_pure_mavlab.py
	cd  ../ && python ./filter_arxiv.py
	cat $(SOURCES) > all.bib
	cd  ../ && python ./filter_delfly.py
	python ./mavlab_bibtex_merge.py
	-python ./check_duplicates.py $(SOURCES)

# publications that occur more than once in the sources (exit code 1)
check:
	python ./check_duplicates.py $(SOURCES)

# download what is on the website into website_export.bib
download:
	python ./download_website.py

# publications that are on the website more than once (exit code 1)
check-web:
	python ./check_duplicates.py website_export.bib


# the open-source code page of the website (opensourcecode.html) from ../opensourcecode.json
code-page:
	python ./opensourcecode_page.py

clean:
	rm -f not_delfly.bib
	rm -f mavlab_merged.bib
	rm -f mavlab_pure_extra.bib
	rm -f mavlab_web_extra.bib
	rm -rf mavlab_merged_web.bib
	rm ../*.bak
	
