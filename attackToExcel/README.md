# ATT&CK To Excel

This folder contains a module for converting [ATT&CK STIX data](https://github.com/mitre/cti) to Excel spreadsheets. It also provides a means to access ATT&CK data as [Pandas](https://pandas.pydata.org/) DataFrames for data analysis.

## Usage
Print full usage instructions:
```
python3 attackToExcel.py -h
```

Example execution:
```
python3 attackToExcel.py
```

Build a excel files corresponding to a specific domain and version of ATT&CK:
```
python3 attackToExcel -domain mobile-attack -version v5.0
```

## Spreadsheet format

The Excel representation of the ATT&CK dataset includes both master spreadsheets, containing all object types, and individual spreadsheets for each object type. The individual type spreadsheets break out relationships (e.g procedure examples connecting groups to techniques) into separate sheets by relationship type, while the master spreadsheet includes all relationship types in a single sheet. Otherwise the representation is identical.

A citations sheet can be used to look up the in-text citations which appear in some fields. For domains that include multiple matrices, such as Mobile ATT&CK, each matrix gets its own named sheet. Unlike the STIX dataset, objects that have been revoked or deprecated are not included in the spreadsheets.

## Accessing the Pandas DataFrames

Internally, attackToExcel stores the parsed STIX data as Pandas DataFrames. These can be retrieved for use in data analysis. 

Example of accessing [Pandas](https://pandas.pydata.org/) DataFrames:
```python
import attackToExcel
import stixToDf
attackdata = attackToExcel.get_data_from_version("enterprise-attack")
techniques_dfs = stixToDf.techniquesToDf(attackdata, "enterprise-attack")
techniques_df = techniques_dfs["techniques"]
print(techniques_df[techniques_df["ID"].str.contains("T1102")]["name"])
# 512                                 Web Service
# 38     Web Service: Bidirectional Communication
# 121             Web Service: Dead Drop Resolver
# 323          Web Service: One-Way Communication
# Name: name, dtype: object
citations_df = techniques_dfs["citations"]
print(citations_df[citations_df["reference"].str.contains("LOLBAS Wmic")])
#         reference                                           citation                                                url
# 1010  LOLBAS Wmic  LOLBAS. (n.d.). Wmic.exe. Retrieved July 31, 2...  https://lolbas-project.github.io/lolbas/Binari...
```
