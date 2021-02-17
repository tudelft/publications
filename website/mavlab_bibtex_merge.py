import bibtexparser


# Import PURE
fname = 'all.bib'
parser = bibtexparser.bparser.BibTexParser(common_strings=True)
with open(fname, encoding="utf8") as bibtex_file:
    bibtex_str = bibtex_file.read()

bib_pure = bibtexparser.loads(bibtex_str, parser=parser)
print(fname + ' contains ',len(bib_pure.entries), ' entries')

# Import WEBSITE
fname = 'website_export.bib'
parser2 = bibtexparser.bparser.BibTexParser(common_strings=True)
with open(fname , encoding="utf8") as bibtex_file2:
    bibtex_str2 = bibtex_file2.read()

bib_website = bibtexparser.loads(bibtex_str2, parser=parser2)
print(fname + ' contains ',len(bib_website.entries), ' entries')

# Results
mavlab_missing = bibtexparser.bibdatabase.BibDatabase()
mavlab_merged  = bibtexparser.bibdatabase.BibDatabase()

verbose = False

def cleanup_title(txt):
    txt = txt.replace('{', '').replace('}', '').replace('¿','').strip().lower().strip('.')
    txt = txt.replace(',', ' ').replace('.', ' ').replace('`', ' ').replace('?', ' ')
    txt = txt.replace('\\textquoteright','').replace('\\textquoteleft','').replace('{}','')
    txt = txt.replace('textquoteright',' ').replace('textquoteleft',' ')
    txt = txt.replace('/', ' ').replace('-', '').replace('\'', ' ').replace('"', ' ').replace(':', ' ')
    txt = txt.replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').strip()
    return txt

for b in bib_pure.entries:
    #print(b)
    if not ('year' in b) or not ('author' in b) or not ('ENTRYTYPE' in b) or not ('title' in b):
        print('ERROR!', b)
        print('------------------------------------------------------------------------')
        continue


    # Paper
    year = b['year']
    title = b['title']
    doctype = b['ENTRYTYPE']
    authors = b['author']

    merged = 0
    for b2 in bib_website.entries:
        
        # Prefer matching DOI
        if 'doi' in b2 and 'doi' in b:
            if b['doi'] == b2['doi']:
                if verbose:
                    print('-DOI merged',b['ID'],b2['ID'])
                mavlab_merged.entries.append(b)
                bib_website.entries.remove(b2)
                merged = 1
                break

        # Or match title and entrytype and year
        if 'title' in b2 and 'ENTRYTYPE' in b2 and 'year' in b2:
            t1 = cleanup_title(b['title'])
            t2 = cleanup_title(b2['title'])
            if t1 == t2 and b['ENTRYTYPE'] == b2['ENTRYTYPE'] and b['year'] == b2['year']:
                if verbose:
                    print('-merged',b['ID'],b2['ID'])
                mavlab_merged.entries.append(b)
                bib_website.entries.remove(b2)
                merged = 1
                break

    if merged == 0:
        mavlab_missing.entries.append(b)


print('pure',len(bib_pure.entries), ' split in merged ', len(mavlab_merged.entries), ' missing ',len(mavlab_missing.entries))
print('website entries remaining', len(bib_website.entries))

# dump back
writer = bibtexparser.bwriter.BibTexWriter()
writer.indent = '\t'
writer.order_entries_by = 'year'
writer.align_values = True
with open('mavlab_pure_extra.bib', 'w', encoding='utf8') as bibfile:
    if len(mavlab_missing.entries) > 0:
        bibfile.write(writer.write(mavlab_missing))
    else:
        bibfile.write('Empty')
    

with open('mavlab_merged.bib', 'w', encoding='utf8') as bibfile:
    if len(mavlab_merged.entries) > 0:
        bibfile.write(writer.write(mavlab_merged))
    else:
        bibfile.write('Empty')
 
with open('mavlab_web_extra.bib', 'w', encoding='utf8') as bibfile:
    if len(bib_website.entries) > 0:
        bibfile.write(writer.write(bib_website))
    else:
        bibfile.write('Empty')





print('Done')
