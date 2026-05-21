import csv
import requests
# Store FILE
import codecs
from unidecode import unidecode


#############################################################
# V1
# For all pages
# Collect all  'href="/record/uuid:'
# The line below is the Title

MAVLAB = ['wagter' , 'croon', 'remes',
            'karasek', 'smeur',  'dupeyroux',
            'hamaza', '"Scheper, K.Y.W."', '"popovic, marija"']

search = '%20OR%20'.join(MAVLAB)
url = 'https://repository.tudelft.nl/islandora/search/' + search + '?collection=education&display=tud_csv'

print(' - V1:', url)

#############################################################
# V2

MAVLAB = ['wagter' , 'croon', 'remes',
            'karasek', 'smeur',  'dupeyroux',
            'hamaza', '"Scheper, K.Y.W."', 'popovic']


search = "+OR+".join(MAVLAB)
url2_msc = "https://repository.tudelft.nl/search?search_term=" + search + "&page=1&sort=relevance&record_type=master_thesis"
url2_phd = "https://repository.tudelft.nl/search?search_term=" + search + "&page=1&sort=relevance&record_type=doctoral_thesis"


print(' - V2 MSC:', url2_msc)

#############################################################
# V3

Authors = {
    'croon': 'https://repository.tudelft.nl/person/supervised/Person_c7471550-0ab7-415d-b600-6aab41b170ce', # ?page=1
    'wagter': 'https://repository.tudelft.nl/person/supervised/Person_283a4bdd-9d21-4e56-9f7c-d83c582f6032',
    'smeur': 'https://repository.tudelft.nl/person/supervised/Person_5b52f579-173a-4ba6-9692-5a13e80e29db',
    'remes': 'https://repository.tudelft.nl/person/supervised/Person_82e35d90-9b89-4e86-8a61-74f4fdd86b64',
    'karasek': 'https://repository.tudelft.nl/person/supervised/Person_2f0b1c3d-4a5e-4f6b-8d7c-9e0a1f3c5b2b',
    'hamaza': 'https://repository.tudelft.nl/person/supervised/Person_c2be371b-2204-410d-8d16-af98b68972ff',
    'popovic': 'https://repository.tudelft.nl/person/supervised/Person_8588464f-4d22-4ba2-a530-50d9a50b2554'
}

msc_thesis = "?object_type=master_thesis"

for author in Authors:
    url = Authors[author] + msc_thesis
    print(' -', author, url)

###

# Old V1 downloader
def msc_download_to_csv():

    p=0
    p = requests.get(url) # + '&page=%d' % pageno)

    with open('./pure/msc.csv', 'wb') as f:
        f.write(p.text.encode())
    txt = p.text

    print('Downloaded...\n')
    #print(txt.encode('UTF-8'))


import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# print(selenium.__version__)

opts = Options()
# opts.add_argument("--headless")
opts.add_argument("--disable-gpu")
opts.add_argument("--no-sandbox")
opts.add_argument("start-maximized")
opts.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...")

# get script folder
script_dir = os.path.dirname(os.path.abspath(__file__))

download_dir = script_dir

print('Download directory:', download_dir)

prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
opts.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=opts)


sys.stdout.reconfigure(encoding='utf-8')


def wait_for_csv(download_dir, timeout=30, export_filename='pure/msc.csv'):
    end_time = time.time() + timeout
    print('Waiting for CSV download to complete...')
    # First wait for the .crdownload file to appear (indicating download has started)
    while time.time() < end_time:
        files = os.listdir(download_dir)
        if any(f.endswith(".crdownload") for f in files):
            print('CSV download started. (.crdownload file detected)')
            break
        time.sleep(1)
        print('.')
    else:
        raise TimeoutError("CSV download did not start")
    # Then wait for the .crdownload file to disappear (indicating download has finished)
    while time.time() < end_time:
        files = os.listdir(download_dir)
        if any(f.endswith("output.csv") for f in files) and not any(f.endswith(".crdownload") for f in files):
            print('CSV download complete. (.crdownload file gone)')
            # Remove previous export file if it exists
            if os.path.exists(os.path.join(download_dir, export_filename)):
                os.remove(os.path.join(download_dir, export_filename))
            # Move the 'output.csv' file to the specified export filename
            os.rename(os.path.join(download_dir, 'output.csv'), os.path.join(download_dir, export_filename))
            return True
        time.sleep(1)
        print('.')
    raise TimeoutError("CSV download did not complete")

def repo_download_to_csv_selenium(url, export_filename='pure/msc.csv'):
    driver.get(url)

    wait = WebDriverWait(driver, 40)

    export_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//button[contains(., "excel")]')
        )
    )

    # click on the "Export" button
    export_button.click()

    wait_for_csv(download_dir,180, export_filename)
    
    # Wait for the page to load
    # htmltxt = driver.page_source   
    # print(htmltxt) 
    


# Remove any output*.csv or *.crdownload files from previous runs
for f in os.listdir(download_dir):
    if f.startswith('output') and f.endswith('.csv'):
        os.remove(os.path.join(download_dir, f))
    if f.endswith('.crdownload'):
        os.remove(os.path.join(download_dir, f))

# msc_download_to_csv()
repo_download_to_csv_selenium(url2_msc, export_filename='pure/msc.csv')
# repo_download_to_csv_selenium(url2_phd, export_filename='pure/phd.csv')



with open('./pure/msc.csv', 'rb') as f:
    txt = f.read().decode('utf-8')


# Create bib
bibf = codecs.open('msc.bib','w', 'utf-8')
bibf.write(u'\ufeff')
bibf.write('# AUTOGENERATED\n# Import from: '+url+'\n\n\n')

reader = csv.reader(txt.split('\n'), delimiter=';')

# Parse the header: store the column names and their index
header = next(reader)
# print('Header:', header)
header_indices = {name: idx for idx, name in enumerate(header)}
print(header_indices)

# print("title", header_indices['title'])
count = 0
for row in reader:
    if len(row) > 0:
        count += 1
        
        d = row[header_indices['publication_date']]
        year = d.split('-')[-1] if '-' in d else d
        name = row[header_indices['contributor_names']]
        role = row[header_indices['contributor_roles']]
        school = "Delft University of Technology"
        
        bibf.write('@mastersthesis{'+row[header_indices['uuid']] + ',\n')
        bibf.write('\tabstract  = {'+row[header_indices['description']]+'},\n')
        bibf.write('\tauthor    = {'+name+'},\n')
        # bibf.write('\trole       = {'+role+'},\n')
        bibf.write('\tkeywords  = {'+row[header_indices['filtered_keywords']]+'},\n')
        bibf.write('\tnote      = {'+'},\n')
        bibf.write('\tschool    = {'+school+'},\n')
        bibf.write('\ttitle     = {'+row[header_indices['title']]+'},\n')
        bibf.write('\ttype      = {mathesis},\n')
        bibf.write('\turl       = {'+row[header_indices['repository_link']]+'},\n')
        bibf.write('\tyear      = {'+year+'}\n')
        bibf.write('}\n\n')


bibf.close()

print('Done. Total records:', count)