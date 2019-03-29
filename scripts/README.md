# scripts

This folder contains one-off scripts for working with ATT&CK content. These scripts are included either because they provide useful functionality or as demonstrations of how to fetch, parse or visualize ATT&CK content.

| script | description |
|:-------|:------------|
| [techniques_from_data_src.py](techniques_from_data_src.py) | Fetches the current ATT&CK STIX 2.0 objects from the ATT&CK TAXII server, prints all of the data sources listed in ATT&CK, and then lists all the techniques containing a given (hardcoded) data source. |
| [techniques_data_sources_vis.py](techniques_data_sources_vis.py) | Generate the csv data used to create the "Techniques Mapped to Data Sources" visualization in the ATT&CK roadmap. Run `python techniques_data_sources_vis.py -h` for usage instructions. | 
