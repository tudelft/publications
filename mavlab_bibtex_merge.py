import bibtexparser


# Import PURE
parser = bibtexparser.bparser.BibTexParser(common_strings=True)
with open('cs_mav.bib', encoding="utf8") as bibtex_file:
    bibtex_str = bibtex_file.read()

bib_pure = bibtexparser.loads(bibtex_str, parser=parser)
print(len(bib_pure.entries))

# Import WEBSITE
parser2 = bibtexparser.bparser.BibTexParser(common_strings=True)
with open('website.bib', encoding="utf8") as bibtex_file2:
    bibtex_str2 = bibtex_file2.read()

bib_website = bibtexparser.loads(bibtex_str2, parser=parser2)

# Results
mavlab_missing = bibtexparser.bibdatabase.BibDatabase()
mavlab_merged  = bibtexparser.bibdatabase.BibDatabase()

print(len(bib_pure.entries),len(bib_website.entries))

def cleanup_title(txt):
    txt = txt.replace('{', '').replace('}', '').strip().lower()
    txt = txt.replace(',', ' ').replace('.', ' ').replace('`', ' ').replace('?', ' ')
    txt = txt.replace('\\textquoteright','').replace('\\textquoteleft','')
    txt = txt.replace('/', ' ').replace('-', ' ').replace('\'', ' ').replace('"', ' ').replace(':', ' ')
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
            
        if 'doi' in b2 and 'doi' in b:
            if b['doi'] == b2['doi']:
                print('-merged',b['ID'],b2['ID'])
                mavlab_merged.entries.append(b)
                bib_website.entries.remove(b2)
                merged = 1
                break

        if 'title' in b2 and 'ENTRYTYPE' in b2:
            t1 = cleanup_title(b['title'])
            t2 = cleanup_title(b2['title'])
            if t1 == t2 and b['ENTRYTYPE'] == b2['ENTRYTYPE']:
                print('-merged',b['ID'],b2['ID'])
                mavlab_merged.entries.append(b)
                bib_website.entries.remove(b2)
                merged = 1
                break

    if merged == 0:
        mavlab_missing.entries.append(b)


print(len(mavlab_missing.entries),len(mavlab_merged.entries))

# dump back
writer = bibtexparser.bwriter.BibTexWriter()
writer.indent = '\t'
writer.order_entries_by = 'year'
writer.align_values = True
with open('mavlab_pure_extra.bib', 'w', encoding='utf8') as bibfile:
    bibfile.write(writer.write(mavlab_missing))
    


with open('mavlab_merged.bib', 'w', encoding='utf8') as bibfile:
    bibfile.write(writer.write(mavlab_merged))
 
with open('mavlab_web_extra.bib', 'w', encoding='utf8') as bibfile:
    bibfile.write(writer.write(bib_website))
 




print('Done')
