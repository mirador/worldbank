'''
Converts several datasets from World Bank into Mirador format

@copyright: Fathom Information Design 2014
'''

import sys, os, csv, codecs, shutil
from xml.dom.minidom import parseString
from sets import Set

def write_xml_line(line, xml_file, xml_strings):
    ascii_line = ''.join(char for char in line if ord(char) < 128)
    if len(ascii_line) < len(line):
        print "  Warning: non-ASCII character found in line: '" + line.encode('ascii', 'ignore') + "'"
    xml_file.write(ascii_line + '\n')
    xml_strings.append(ascii_line + '\n')

def read_variables(filename, var_tree, var_groups, var_codes, var_names, var_types):
    print '  Reading ' + filename + '...'
    reader = csv.reader(open(filename, 'r'), dialect='excel')
    reader.next()
    for row in reader:
        code = row[0].upper()
        name = row[3]
        topic = row[1]
        parts = topic.split(':')
        if len(parts) < 2: 
            print '    Variable ' + code + ' does not have properly formatted topic: "' + topic + '", so it won\'t be included.'
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
        
        if not code in variables:
            variables.append(code)
            var_codes.append(code)    
            var_names[code] = name
            var_types[code] = 'int'
            
def read_education_variables(filename, var_tree, var_groups, var_codes, var_names, var_types):            
    topics = ['Education Inequity', 'Educational Attainment', 'Equity', 'Expenditures', 'Learning Outcomes', 'Literacy', 'Pre-Primary', 'Primary', 'Secondary', 'Teachers', 'Tertiary']
    print '  Reading education variables from ' + filename + '...'
    reader = csv.reader(open(filename, 'r'), dialect='excel')
    reader.next()
    for row in reader:
        code = row[0].upper()
        name = row[3]
        topic = row[1]
        if not topic in topics:
            print '    Topic "' + topic + '" not supported for education data.'
            continue
        group = 'Education'
        table = topic
    
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
        
        if not code in variables:
            variables.append(code)
            var_codes.append(code)    
            var_names[code] = name
            var_types[code] = 'int'
            
def read_countries(filename, country_codes, country_names, country_regions, income_groups):
    print '  Reading ' + filename + '...'
    reader = csv.reader(open(filename, 'r'), dialect='excel')
    reader.next()
    for row in reader:
        code = row[0]
        name = row[1]
        notes = row[6]
        region = row[7]
        group = row[8]
    
        if 'aggregate' in notes:
            print '    Skipping aggregate region "' + name +'".'
            continue
    
        if not code in country_codes:
            country_codes.append(code)
            country_names[code] = name
    
            country_regions[code] = region
            income_groups[code] = group

def read_data(filename, all_data, all_years, var_codes, country_codes, missing_vars, missing_countries):
    print '  Reading ' + filename + '...'
    reader = csv.reader(open(filename, 'r'), dialect='excel')
    titles = reader.next()
    
    years = titles[4: len(titles)]
    if len(all_years) == 0:
        all_years.extend(years)
#     elif len(all_years) != len(years):    
#         raise Exception('Inconsistent number of years! ' + str(len(all_years)) + ' ' + str(len(years)))

    year0 = int(all_years[0])
    year1 = int(titles[4])
    ydiff = year1 - year0     

    for row in reader:
        code = row[3].upper()
        country = row[1].upper()
        if not code in var_codes:
            if not code in missing_vars:
                print '    Variable ' + code + ' is missing from dictionary, skipping.'
                missing_vars.add(code);
            continue        

        if not country in country_codes:
            if not country in missing_countries:
                print '    Country ' + country + ' is missing from dictionary, skipping.'
                missing_countries.add(country)
            continue
            
#         for i in range(4, len(titles)):
        for y in range(0, len(all_years)):
        
            year = all_years[y]
            key = country + ':' + year
            if key in all_data:
                dat = all_data[key]
            else:
                dat = {}
                all_data[key] = dat
                
            if y < ydiff:     
                dat[code] = '\\N'
                continue
              
            i = 4 + y - ydiff
            if row[i] != '':
#                 if code in dat and dat[code] != row[i]:
#                     print '    Warning: data inconsistency for variable ' + code + ': ' + dat[code] + ' ' + row[i]                
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

def write_data(dat_filename, bin_filename, country_codes, all_titles, all_years, all_data):
    # Remove binary file, just in case
    if os.path.isfile(bin_filename):
        os.remove(bin_filename)

    print '  Creating data file ' + dat_filename + '...'
    writer = csv.writer(open(dat_filename, 'w'), dialect='excel-tab')
    writer.writerow(all_titles)
    for country in country_codes:
        for year in all_years:  
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

def write_dict(filename, all_titles, var_names, var_types):
    print '  Creating dictionary file ' + filename + '...'
    dfile = open(filename, 'w')
    for var in all_titles:
        line = var_names[var] + '\t' + var_types[var]
        if var == label_var:
            line = line + '\tlabel'
        line = line + '\n'   
        dfile.write(line)  
    dfile.close()

def write_grp(filename, var_tree, var_groups):
    print '  Creating groups file ' + filename + '...'
    # Writing file in utf-8 because the input html files from
    # NHANES website sometimes have characters output the ASCII range.
    xml_file = codecs.open(filename, 'w', 'utf-8')
    xml_strings = []
    write_xml_line('<?xml version="1.0"?>', xml_file, xml_strings)
    write_xml_line('<data>', xml_file, xml_strings)
    for group in var_groups:
        write_xml_line(' <group name="' + group + '">', xml_file, xml_strings)
        tables = var_tree[group]
        for table in tables:
            write_xml_line('  <table name="' + table + '">', xml_file, xml_strings)
            variables = tables[table] 
            for var in variables:
                write_xml_line('   <variable name="' + var + '"/>', xml_file, xml_strings)
            write_xml_line('  </table>', xml_file, xml_strings)
        write_xml_line(' </group>', xml_file, xml_strings)
    write_xml_line('</data>', xml_file, xml_strings)
    xml_file.close()

    # XML validation.
    try:
        doc = parseString(''.join(xml_strings))
        doc.toxml()
    except:
        sys.stderr.write('XML validation error:\n')
        raise  

source_folder = 'source/'
output_folder = 'mirador/'
add_hnp = False
add_genstats = False
add_edstats = False

for arg in sys.argv[1: len(sys.argv)]:
    print arg
    if arg == '-hnp': add_hnp = True   
    if arg == '-gender': add_genstats = True
    if arg == '-edu': add_edstats = True
    
country_codes = []
country_names = {}
country_regions = {}
income_groups = {}

label_var = 'NAME'
var_codes = []
key_vars = ['NAME', 'REGION', 'INCOME', 'YEAR']
var_names = {'NAME':'Country name', 'REGION':'Region', 'INCOME':'Income group','YEAR':'Year'}
var_types = {'NAME':'String', 'REGION':'category', 'INCOME':'category', 'YEAR':'int'}
var_tree = {}
var_groups = []

all_data = {}
all_years = []
missing_vars = Set([])
missing_countries = Set([])

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

shutil.copyfile('config.mira', output_folder + 'config.mira')

print 'Reading country metadata...'
read_countries(source_folder + 'WDI_csv/WDI_Country.csv', country_codes, country_names, country_regions, income_groups)
print 'Done.'

print 'Create data tree...'
var_tree['Keys'] = {'Countries and years':key_vars}
var_groups.append('Keys')
read_variables(source_folder + 'WDI_csv/WDI_Series.csv', var_tree, var_groups, var_codes, var_names, var_types)
if add_hnp: 
    read_variables(source_folder + 'hnp_stats_csv/HNP_Series.csv', var_tree, var_groups, var_codes, var_names, var_types)
if add_genstats:
    read_variables(source_folder + 'Gender_Stats_csv/Gender_Series.csv', var_tree, var_groups, var_codes, var_names, var_types)
if add_edstats:
    read_education_variables(source_folder + 'Edstats_csv/EDStats_Series.csv', var_tree, var_groups, var_codes, var_names, var_types)
print 'Done.'

print 'Reading data...'
read_data(source_folder + 'WDI_csv/WDI_Data.csv', all_data, all_years, var_codes, country_codes, missing_vars, missing_countries)
if add_hnp:
    read_data(source_folder + 'hnp_stats_csv/HNP_Data.csv', all_data, all_years, var_codes, country_codes, missing_vars, missing_countries)
if add_genstats:
    read_data(source_folder + 'Gender_Stats_csv/Gender_Data.csv', all_data, all_years, var_codes, country_codes, missing_vars, missing_countries)
if add_edstats:
    read_data(source_folder + 'Edstats_csv/Edstat_Data.csv', all_data, all_years, var_codes, country_codes, missing_vars, missing_countries)
print 'Done.'

print 'Writing Mirador dataset...'
all_titles = []
all_titles.extend(key_vars)
all_titles.extend(var_codes)
write_data(output_folder + 'data.tsv', output_folder + 'data.bin', country_codes, all_titles, all_years, all_data)
write_dict(output_folder + 'dictionary.tsv', all_titles, var_names, var_types)
write_grp(output_folder + 'groups.xml', var_tree, var_groups)
print 'Done.'
