'''
Downloads the zip files with the csv tables for the World Development Indicators, 
Health Nutrition and Population Statistics, Gender Statistics, and Education Statistics 
from the World Bank data catalog page:

http://datacatalog.worldbank.org/

@copyright: Fathom Information Design 2014
'''

import os, sys, zipfile, requests

def download_file(url, local_folder):
    local_filename = local_folder + '/' + url.split('/')[-1]
    print 'Attempting to open ' + url
    r = None
    for i in range(0, 5):
        try:
            r = requests.get(url)
            break; 
        except:
            r = None
            if i < 5 - 1: print "  Warning: Could not open " + url + ", will try again"
    if r == None:
        sys.stderr.write("Error: Failed opening " + url + " after 5 attempts\n")
        sys.exit(1)
    print 'Downloading ' + url + '...'
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    print 'Done.'      
    return 
    
def extract_zip(zip_file):
    print 'Unzipping ' + zip_file + '...'
    extract_folder = os.path.splitext(zip_file)[0]
    with zipfile.ZipFile(zip_file, 'r') as z:
        z.extractall(extract_folder)   
    print 'Done.'
    
base_url = 'http://databank.worldbank.org/data/download'
data_files = ['WDI_csv.zip', 'hnp_stats_csv.zip', 'Gender_Stats_csv.zip', 'Edstats_csv.zip']

source_folder = 'source'
if not os.path.exists(source_folder):
    os.makedirs(source_folder)

for file in data_files:
    url = base_url + '/' + file
    download_file(url, source_folder)
    extract_zip(source_folder + '/' + file)
