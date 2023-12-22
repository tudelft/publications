
all:
	# cd  ../ && python ./filter_pure_mavlab.py
	cd  ../ && python ./filter_arxiv.py
	cat ../arxiv_nopub.bib > all.bib
	cat ../dataverse.bib >> all.bib
	cat ../mavlab_nopure.bib >> all.bib
	cat ../mediacoverage.bib >> all.bib
	cat ../pure.bib >> all.bib
	cat ../msc.bib >> all.bib
	cat ../4tu.bib >> all.bib
	cd  ../ && python ./filter_delfly.py
	python ./mavlab_bibtex_merge.py


clean:
	rm -f not_delfly.bib
	rm -f mavlab_merged.bib
	rm -f mavlab_pure_extra.bib
	rm -f mavlab_web_extra.bib
	rm -rf mavlab_merged_web.bib
	rm ../*.bak
	