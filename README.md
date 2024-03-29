# MAVLab Publication List
This repo is meant to keep a history of all publications to do with the Micro Air Vehicle Laboratory at the Delft University of Technology.

## Import

 - step 1A: download from pure: ```import_pure_2021.py```    -> ```cs.bib```
 - step 1B: download from dataverse: ```import_dataverse_2021.py```    -> ```dataverse.bib```
 - step 1C: download from arXiv: ```import_arxiv_2021.py```    -> ```arxiv.bib```
 - step 1D: download from M.Sc. thesis repo: ```import_repository.py``` -> ```msc.bib```
 - step 1E: fill ```mediacoverage.bib``` and ```mavlab_nopure.bib``` by hand
 - step 1F: search on https://data.4tu.nl/search?q=mavlab and import by hand in ```4tu.bib```
 - setp 2A: filter MAVLAB publications from pure/cs.bib: ```filter_pure_mavlab.py```  -> ```pure.bib```
 - setp 2B: filter published arxiv papers with DOI arxiv.bib: ```filter_arxiv.py```  -> ```arxiv_nopub.bib```
 - step 3: check pure/cs_nomav.bib if there are any mavlab papers left: fix the script

## Website:

 - step 4A: in wordpress: add all publications 'to own list' 
 - step 4B: export publications form website plugin as ```website_export.bib```.
 - step 5: merge pure and website with ```mavlab_bibtex_merge.py```
 - add the ```mavlab_web_extra.bib``` to pure, the ```mavlab_pure_extra.bib``` to the website until all is in merged.

## Contributing
To add a new publication, you can simply add the bibitem to the mavlab.bib, either by editing the page directly using the github editor (if you have write access to the repo) or by making a pull request with your changes. The Continuous Integration tool will test your changes to ensure that the bib file still works.

Also check the default self-archiving style of the MavLab at: https://github.com/tudelft/latex_style
