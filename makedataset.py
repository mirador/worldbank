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

label_var = 'NAME'
var_codes = []
key_vars = ['NAME', 'REGION', 'INCOME', 'YEAR']
var_names = {'NAME':'Country name', 'REGION':'Region', 'INCOME':'Income group','YEAR':'Year'}
var_types = {'NAME':'String', 'REGION':'category', 'INCOME':'category', 'YEAR':'int'}

var_tree = {}
var_groups = []

country_codes = []
country_names = {}
country_regions = {}
income_groups = {}

all_data = {}

print 'Create data tree...'
var_tree['Keys'] = {'Countries and years':key_vars}
var_groups.append('Keys')
reader = csv.reader(open(source_folder + 'WDI_csv/WDI_Series.csv', 'r'), dialect='excel')
reader.next()
for row in reader:
    code = row[0].upper()
    name = row[3]
    topic = row[1]
    parts = topic.split(':')
    if len(parts) < 2: 
        print '  Variable ' + code + ' does not have properly formatted topic: "' + topic + '", so it won\'t be included.'
        continue
    group = parts[0].strip().replace('&', 'and')
    table = parts[1].strip().replace('&', 'and')    
    
    if group in var_tree:
        tables = var_tree[group]
    else:
        tables = {}
        var_tree[group] = tables
        var_groups.append(group)
    
    if table in tables:
        variables = tables[table]
    else:
        variables = []
        tables[table] = variables
        
    variables.append(code)
    var_codes.append(code)    
    var_names[code] = name
    var_types[code] = 'int'
                             
print 'Done.'
                             
#print var_groups

# sys.exit(0)

print 'Reading country metadata...'
reader = csv.reader(open(source_folder + 'WDI_csv/WDI_Country.csv', 'r'), dialect='excel')
reader.next()
for row in reader:
    code = row[0]
    short_name = row[1]
    long_name = row[3]    
    notes = row[6]
    region = row[7]
    group = row[8]
    
    if 'aggregate' in notes:
        print '  Aggregate region ' + short_name +', skipping.'
        continue
    
    country_codes.append(code)
    country_names[code] = short_name
    
    country_regions[code] = region
    income_groups[code] = group

print 'Done.'

print 'Reading data...'
missing_vars = Set([])
missing_countries = Set([])
reader = csv.reader(open(source_folder + 'WDI_csv/WDI_Data.csv', 'r'), dialect='excel')
titles = reader.next()
years = titles[4: len(titles)]
for row in reader:
    code = row[3].upper()
    country = row[1].upper()
    if not code in var_codes:
        if not code in missing_vars:
            print '  Variable ' + code + ' is missing from dictionary, skipping'
            missing_vars.add(code);
        continue        

    if not country in country_codes:
        if not country in missing_countries:
            print '  Country ' + country + ' is missing from dictionary, skipping'
            missing_countries.add(country)
        continue
            
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
#     print var, var_names[var]
# 
# for country in country_codes:
#     print country, country_names[country]    
#print len(country_codes)    

#print all_data
#print years

# Remove binary file, just in case
if os.path.isfile(output_folder + 'data.bin'):
    os.remove(output_folder + 'data.bin')

# sys.exit(0)

print 'Creating data file...'
writer = csv.writer(open(output_folder + 'data.tsv', 'w'), dialect='excel-tab')    
all_titles = []
all_titles.extend(key_vars)
all_titles.extend(var_codes)
writer.writerow(all_titles)
for country in country_codes:
    for year in years:
    
#         country_short_names[code] = short_name
#     country_long_names[code] = long_name
#     
#     country_regions[code] = region
#     income_groups[code] = group
    
    
        row = [country_names[country], country_regions[country], income_groups[country], year]
        
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
               
print 'Creating dictionary file...'
dfile = open(output_folder + 'dictionary.tsv', 'w')
for var in all_titles:
    line = var_names[var] + '\t' + var_types[var]
    if var == label_var:
        line = line + '\tlabel'
    line = line + '\n'   
    dfile.write(line)  
dfile.close()
print 'Done.'




print 'Creating groups file...'

# Writing file in utf-8 because the input html files from
# NHANES website sometimes have characters output the ASCII range.
xml_file = codecs.open(output_folder + 'groups.xml', 'w', 'utf-8')
xml_strings = []
write_xml_line('<?xml version="1.0"?>')
write_xml_line('<data>')
for group in var_groups:
    write_xml_line(' <group name="' + group + '">')
    tables = var_tree[group]
    for table in tables:
        write_xml_line('  <table name="' + table + '">')        
        variables = tables[table] 
        for var in variables:
            write_xml_line('   <variable name="' + var + '"/>')        
        write_xml_line('  </table>')
    write_xml_line(' </group>')
write_xml_line('</data>')    
xml_file.close()

# XML validation.
try:
    doc = parseString(''.join(xml_strings))
    doc.toxml()
    print 'Done.' 
except:
    sys.stderr.write('XML validation error:\n')
    raise    
