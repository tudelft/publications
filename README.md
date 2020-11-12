# MAVLab Publication List
This repo is meant to keep a history of all publications to do with the Micro Air Vehicle Laboratory at the Delft University of Technology.

## Import

 - step 1: download from pure: ```pure_import_2020.py```    -> ```cs.bib```
 - setp 2: filter MAVLAB publications: ```mavlab_bibtex_parser.py```  -> ```cs_mav.bib```
 - step 3: check cs_nomav.bib if there are any mavlab papers left: fix the script

## Website:

 - step 4: export publications form website plugin as ```website.bib```
 - step 5: merge pure and website with ```mavlab_bibtex_merge.py```
 - add the web_extra to pure, the pure_extra to the website until all is in merged.

## Contributing
To add a new publication, you can simply add the bibitem to the mavlab.bib, either by editing the page directly using the github editor (if you have write access to the repo) or by making a pull request with your changes. The Continuous Integration tool will test your changes to ensure that the bib file still works.

Also check the default self-archiving style of the MavLab at: https://github.com/tudelft/latex_style
