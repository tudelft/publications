# MAVLab Publication List
This repo keeps a history of all publications of the Micro Air Vehicle Laboratory (MAVLab) at the Delft University of Technology, part of the Control & Simulation (C&S) section. It collects them from several sources, filters the MAVLab entries and exports them for the website https://mavlab.tudelft.nl.

## Overview

| File | Content | Source |
|------|---------|--------|
| `pure/cs.bib` | all C&S publications | `import_pure_2021.py` (research.tudelft.nl) |
| `pure.bib` | MAVLab publications filtered from `pure/cs.bib` | `filter_pure_mavlab.py` |
| `mavlab_summary.csv` | MAVLab publications per year and type | `filter_pure_mavlab.py` |
| `arxiv.bib` | arXiv preprints of MAVLab staff | `import_arxiv_2021.py` |
| `arxiv_nopub.bib` | arXiv preprints whose DOI is not in `pure.bib` (not committed) | `filter_arxiv.py` |
| `4tu.bib` | datasets on data.4tu.nl | `import_4tu_2021.py` |
| `dataverse.bib` | datasets on dataverse.nl/dataverse/mavlab | `import_dataverse_2021.py` |
| `msc.bib` | M.Sc. theses supervised (mentor) by a MAVLab member (staff, postdoc or PhD student), from repository.tudelft.nl | `import_repository.py` |
| `msc_all.bib` | M.Sc. theses with MAVLab staff in any role, also graduation committee only | `import_repository.py` |
| `mediacoverage.bib` | media coverage | by hand |
| `website/logos/` | logos of the media outlets, used by `mediacoverage.bib` | by hand |
| `mavlab_nopure.bib` | publications missing in Pure / the repository | by hand |
| `opensourcecode.json` | open-source code of the MAVLab, with its papers and website posts | by hand |
| `website/opensourcecode.html` | the open-source code page of the website | `make -C website code-page` |
| `website/all.bib` | all of the above combined | `make -C website` |
| `website/delfly.bib` | DelFly / flapping-wing subset of `all.bib` | `filter_delfly.py` |
| `userbibs/user_*.bib` | per-staff subsets of `all.bib` | `filter_by_user.py` |
| `website/website_export.bib` | all publications on the website (teachPress BibTeX feed) | `make -C website download` |

Install the dependencies with `pip install -r requirements.txt`. The Pure and 4TU imports use Selenium and need Chrome.

## Monthly import (automated)
The GitHub Action `.github/workflows/monthly_import.yml` runs on the 1st of every month (or manually via *workflow_dispatch*). It imports arXiv, M.Sc. theses, 4TU and Pure, runs all filters and the website build, and opens a pull request `Monthly Paper Update import-YYYY-MM-DD-HH-MM` when anything changed. An import that is incomplete keeps its previous data and shows up as a warning on the run (exit code 1 of the script); run the action again later. Review the diff before merging.

## Manual steps

### Import
 - step 1A: download from Pure: `import_pure_2021.py` -> `pure/cs.bib`
 - step 1B: download from Dataverse: `import_dataverse_2021.py` -> `dataverse.bib` (not in the monthly import)
 - step 1C: download from arXiv: `import_arxiv_2021.py` -> `arxiv.bib` (arXiv API). If the API does not answer, the previous entries are kept and the summary asks to run the script again later.
 - step 1D: download from 4TU: `import_4tu_2021.py` -> `4tu.bib`, or search https://data.4tu.nl/search?q=mavlab and add by hand
 - step 1E: download M.Sc. theses: `import_repository.py` -> `msc.bib` (a MAVLab member as mentor/supervisor, or MAVLab staff in any role for theses of other faculties) and `msc_all.bib` (also graduation committee only). Theses that cannot be downloaded or are no longer found keep their previous entry; the summary lists what changed.
 - step 1F: fill `mediacoverage.bib` and `mavlab_nopure.bib` by hand

### Filter
 - step 2A: filter MAVLab publications from `pure/cs.bib`: `filter_pure_mavlab.py` -> `pure.bib`, `mavlab_summary.csv` and `pure/cs_nomav.bib` (the rest)
 - step 2B: remove arXiv preprints that have been published: `filter_arxiv.py` -> `arxiv_nopub.bib`
 - step 3: check `pure/cs_nomav.bib` for MAVLab papers that were missed, and `pure.bib` for papers that are not MAVLab. Fix the member list in `mavlab_members.py` (also used for the M.Sc. theses) or the `remove` list in `filter_pure_mavlab.py`.

`make` in the root runs steps 2A, 4 and the per-user export.

### Website
 - step 4: `make -C website` combines all bib files into `website/all.bib`, writes `website/delfly.bib` and runs `website/mavlab_bibtex_merge.py`
 - step 5: `filter_by_user.py` -> `userbibs/user_*.bib`
 - step 6A: in WordPress: add all publications 'to own list'
 - step 6B: `make -C website download` downloads the publications on the website into `website/website_export.bib`; `make -C website check-web` lists publications that are on the website twice
 - step 7: run `make -C website` again. The merge (matching on DOI, URL, then title + type + year) writes:
   - `mavlab_pure_extra.bib`: in this repo but not on the website -> import into WordPress
   - `mavlab_web_extra.bib`: on the website but not in this repo -> add to Pure or `mavlab_nopure.bib`
   - `mavlab_merged.bib` / `mavlab_merged_web.bib`: matched pairs

   Repeat until both extra files are empty.

## Open-source code
`opensourcecode.json` lists the code that the MAVLab releases: one entry per repository (or download), with
- `name`: the project name, usually the repository name
- `repo`: where the code is
- `year`: the year the code was first released (the year the repository was made); it does not change later
- `papers`: BibTeX keys of the publications that the code belongs to (the keys of the bib files in this repository)
- `posts`: the pages and posts on https://mavlab.tudelft.nl that link to the code

The entries are sorted newest year first, then by name. Inside `papers` and `posts`, add new items at the top of the list. Keep the layout of `json.dumps(..., indent=2, ensure_ascii=False)` (one item per line), so a git diff shows a new repository or a new link as added lines only.

A page on https://mavlab.tudelft.nl shows this list from `website/opensourcecode.html`, made by `make -C website code-page` (`website/opensourcecode_page.py`; `make -C website` and so the monthly import also run it). WordPress loads that file from the master branch of this repository with the shortcode `[mavlab_github file="website/opensourcecode.html"]` of `website/wordpress/mavlab_github_include.php`, a PHP snippet in WPCode (the page itself: `website/wordpress/opensourcecode_page_content.html`); the papers are teachPress `[tpsingle key=...]` shortcodes, so they look like on the rest of the website. Changes are online within an hour after the merge.

## Media coverage logos
Each entry of `mediacoverage.bib` has an `image_url` field: the logo of the outlet, shown next to the item on https://mavlab.tudelft.nl/media-coverage/. The logos are in `website/logos/<outlet>.png` (PNG, at most 400 px), and the same files are in the WordPress media library as `media-logo-<outlet>.png`, so the URL is `https://mavlab.tudelft.nl/wp-content/uploads/<year>/<month>/media-logo-<outlet>.png`. All items of one outlet use the same logo. For a new outlet: add the logo to `website/logos/`, upload it to the media library with that file name, and use its URL.

teachPress does not export `image_url`, but its BibTeX import stores any field with the name of a teachPress column, so `image_url` sets the logo. Importing `mediacoverage.bib` in teachPress with "overwrite" switched on updates the logos (and the other fields) of the items that are already on the website, matched by BibTeX key.

## Test
`make validate` checks the quality of `website/all.bib` (run `make` first). It runs two steps in `test/`, which can also be used on their own, for any bib file with `BIB=`:
 - `make -C test` (`makecite.py`): a LaTeX document that cites every entry, built with LaTeX and BibTeX until all citations are resolved. The BibTeX warnings (empty fields, author and editor both set) and the LaTeX errors (unescaped `&`, characters LaTeX cannot print) go to `test/report.txt`; `test/main.pdf` shows how the entries render. Takes seconds.
 - `make -C test validate` (`validate.py`): checks the ISBN and ISSN check digits, whether each DOI is registered at doi.org, and whether each URL and PDF link still answers. One request per DOI or link (~1500, ~20 min), so do not run it too often; `python test/validate.py --offline` only does the check digits. All results go to `test/validate_report.csv`; the problems are printed. `blocked` (403, 429, bot check) is not necessarily wrong: check those by hand.

## Contributing
To add a publication that is not in Pure, add the bibitem to `mavlab_nopure.bib` (or `mediacoverage.bib` for media, `opensourcecode.json` for code), either by editing directly on GitHub (with write access) or with a pull request. Do not edit files marked `# AUTOGENERATED`; they are overwritten by the import.

Also check the default self-archiving style of the MAVLab at: https://github.com/tudelft/latex_style
