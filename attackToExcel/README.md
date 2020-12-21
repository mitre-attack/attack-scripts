# ATT&CK To Excel

This folder contains a module for converting [ATT&CK STIX data](https://github.com/mitre/cti) to Excel spreadsheets. 

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

## Output format

The Excel representation of the ATT&CK dataset includes both master spreadsheets, containing all object types, and individual spreadsheets for each object type. The individual type spreadsheets break out relationships (e.g procedure examples connecting groups to techniques) into separate sheets by relationship type, while the master spreadsheet includes all relationship types in a single sheet. Otherwise the representation is identical.

A citations sheet can be used to look up the in-text citations which appear in some fields. For domains that include multiple matrices, such as Mobile ATT&CK, each matrix gets its own named sheet. Unlike the STIX dataset, objects that have been revoked or deprecated are not included in the spreadsheets.