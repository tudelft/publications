
all:
	cat ../arxiv.bib > all.bib
	cat ../dataverse.bib >> all.bib
	cat ../mavlab_nopure.bib >> all.bib
	cat ../mediacoverage.bib >> all.bib
	cat ../pure.bib >> all.bib
	cat ../msc.bib >> all.bib
	cd  ../ && python ./filter_delfly.py
