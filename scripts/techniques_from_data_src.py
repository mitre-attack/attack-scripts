from stix2 import TAXIICollectionSource, Filter
from taxii2client import Collection

# Create variable to hold all data sources
all_data_srcs = []

# Establish TAXII2 Collection instance for Enterprise ATT&CK collection
collection = Collection("https://cti-taxii.mitre.org/stix/collections/95ecc380-afe9-11e4-9b6c-751b66dd541e/")

# Supply the collection to TAXIICollection
tc_src = TAXIICollectionSource(collection)

# Get all techniques in Enterprise ATT&CK
techniques = tc_src.query([Filter("type", "=", "attack-pattern")])

# Get all data sources in Enterprise ATT&CK
for tech in techniques:
    if 'x_mitre_data_sources' in tech:
        all_data_srcs += [
            data_src for data_src in tech.x_mitre_data_sources
            if data_src not in all_data_srcs
        ]
print("All data sources in Enterprise ATT&CK:\n")
print("\n".join(all_data_srcs) + "\n\n")

# Get all techniques that have Windows Registry as a data source
techs_with_data_src = tc_src.query([
    Filter("type", "=", "attack-pattern"),
    Filter("x_mitre_data_sources", "in", "Windows Registry")
])

# Get names of techniques
tech_names = [tech.name for tech in techs_with_data_src]
print("The following " + str(len(tech_names)) + 
    " techniques use 'Windows Registry' as a data source:\n")
print("\n".join(tech_names))
