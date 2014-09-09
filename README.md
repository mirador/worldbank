## WORLD BANK DATA SCRIPTS 

This set of Python scripts downloads, parses, and aggregates datasets from the [World Bank's Open 
Data initiative](http://datacatalog.worldbank.org/), and outputs the data as a Mirador dataset.
It aggregates the following World Bank datasets:

1. World Development Indicators (WDI): http://data.worldbank.org/data-catalog/world-development-indicators
2. Health Nutrition and Population (HNP) Statistics: http://data.worldbank.org/data-catalog/health-nutrition-and-population-statistics
3. Gender Statistics: http://data.worldbank.org/data-catalog/gender-statistics
4. Education Statistics: http://data.worldbank.org/data-catalog/ed-stats

which contain yearly data from 1960 until the present and are updated quarterly, except the 
HNP statistics which are updated biannually.

### DEPENDENCIES

The scripts have the following dependencies:

1. Python 2.7.3+ (not tested with 3+) and the following package:
  * Requests: http://docs.python-requests.org/en/latest/index.html 
  
### USAGE

**1)** Download and extract the zip files:

```bash
python download.py
```

**2)** Creates Mirador dataset. By default, it only uses the WDI data:

```bash
python makedataset.py
```

and the HNP, Gender and Education statistics can be added by using the -hnp, -gender, and -edu
parameters. For example, to add HNP and Gender statistics to the base WDI data, the command would be

```bash
python makedataset.py -hnp -gender
```

The resulting Mirador dataset will be saved in the mirador folder.