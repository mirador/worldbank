'''

Converts the World Bank indicators for Development into Mirador format

@copyright: Fathom Information Design 2014
'''

# World Development Indicators
# http://data.worldbank.org/data-catalog/world-development-indicators
# http://databank.worldbank.org/data/download/WDI_csv.zip

# Gender Statistics
# http://data.worldbank.org/data-catalog/gender-statistics
# http://databank.worldbank.org/data/download/Gender_Stats_csv.zip

# Education Statistics
# http://data.worldbank.org/data-catalog/ed-stats
# http://databank.worldbank.org/data/download/Edstats_csv.zip

# Health Nutrition and Population Statistics
# http://data.worldbank.org/data-catalog/health-nutrition-and-population-statistics
# http://databank.worldbank.org/data/download/hnp_stats_csv.zip

import sys, os, csv, codecs
from xml.dom.minidom import parseString
from sets import Set

def write_xml_line(line):
    ascii_line = ''.join(char for char in line if ord(char) < 128)
    if len(ascii_line) < len(line):
        print "  Warning: non-ASCII character found in line: '" + line.encode('ascii', 'ignore') + "'"
    xml_file.write(ascii_line + '\n')
    xml_strings.append(ascii_line + '\n')

source_folder = 'source/'
output_folder = 'mirador/'

var_codes = []
var_titles = {'COUNTRY':'Country', 'YEAR':'Year'}
var_types = {'COUNTRY':'String', 'YEAR':'int'}
country_codes = []
country_names = {}
all_data = {}

print 'Reading data...'
reader = csv.reader(open(source_folder + 'WDI_csv/WDI_Data.csv', 'r'), dialect='excel')
titles = reader.next()
years = titles[4: len(titles)]
for row in reader:
    code = row[3].upper()
    country = row[1].upper()
    if not code in var_codes:
        var_codes.append(code)
        var_titles[code] = row[2]
        var_types[code] = 'int'
    if not country in country_codes:
        country_codes.append(country)        
        country_names[country] = row[0]
    
    for i in range(4, len(titles)):
        year = titles[i]
        key = country + ':' + year
        if key in all_data:
            dat = all_data[key]
        else:
            dat = {}
            all_data[key] = dat
        if row[i] != '':    
            dat[code] = row[i]
            if var_types[code] == 'int':
                try:
                    value = float(row[i])
                    if not value.is_integer():
                        var_types[code] = 'float'
                except ValueError:
                    pass
        else:    
            dat[code] = '\\N'
print 'Done.'
        
# for var in var_codes:
#     print var, var_titles[var]
# 
# for country in country_codes:
#     print country, country_names[country]    
#print len(country_codes)    

#print all_data
#print years

# Remove binary file, just in case
if os.path.isfile(output_folder + 'data.bin'):
    os.remove(output_folder + 'data.bin')

print 'Creating data file...'
writer = csv.writer(open(output_folder + 'data.tsv', 'w'), dialect='excel-tab')    
all_titles = ['COUNTRY', 'YEAR']
all_titles.extend(var_codes)
writer.writerow(all_titles)
for country in country_codes:
    for year in years:
        row = [country_names[country], year]
        key = country + ':' + year
        if key in all_data:
            row_data = all_data[key]
            for code in var_codes:
                if code in row_data:
                    row.append(row_data[code]);
                else:
                    row.append('\\N');
        else:
            row.extend(['\\N'] * len(var_codes))
        writer.writerow(row)
print 'Done.'
               
print "Creating dictionary file..."               
dfile = open(output_folder + 'dictionary.tsv', 'w')
for var in all_titles:
    line = var_titles[var] + '\t' + var_types[var]
    if var == 'COUNTRY':
        line = line + '\tlabel'
    line = line + '\n'   
    dfile.write(line)  
dfile.close()
print 'Done.'    
    
