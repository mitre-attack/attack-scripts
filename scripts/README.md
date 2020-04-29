# scripts

This folder contains one-off scripts for working with ATT&CK content. These scripts are included either because they provide useful functionality or as demonstrations of how to fetch, parse or visualize ATT&CK content.

| script | description |
|:-------|:------------|
| [techniques_from_data_source.py](techniques_from_data_source.py) | Fetches the current ATT&CK STIX 2.0 objects from the ATT&CK TAXII server, prints all of the data sources listed in Enterprise ATT&CK, and then lists all the Enterprise techniques containing a given data source. Run `python3 techniques_from_data_source.py -h` for usage instructions. |
| [techniques_data_sources_vis.py](techniques_data_sources_vis.py) | Generate the csv data used to create the "Techniques Mapped to Data Sources" visualization in the ATT&CK roadmap. Run `python3 techniques_data_sources_vis.py -h` for usage instructions. | 
| [diff_stix.py](diff_stix.py) | Create markdown and/or ATT&CK Navigator layers reporting on the changes between two versions of the STIX2 bundles representing the ATT&CK content. For default operation, put [enterprise-attack.json](https://github.com/mitre/cti/blob/master/enterprise-attack/enterprise-attack.json), [mobile-attack.json](https://github.com/mitre/cti/blob/master/mobile-attack/mobile-attack.json), and [pre-attack.json](https://github.com/mitre/cti/blob/master/pre-attack/pre-attack.json) bundles in 'old' and 'new' folders for the script to compare. Run `python3 diff_stix.py -h` for full usage instructions. |
| [technique_mappings_to_csv.py](technique_mappings_to_csv.py) | Fetches the current ATT&CK content expressed as STIX2 and creates spreadsheet mapping Techniques with Mitigations, Groups or Software. Run `python3 technique_mappings_to_csv.py -h` for usage instructions. |
