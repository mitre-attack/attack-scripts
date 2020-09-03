import argparse
from stix2 import MemoryStore
import stixToDf
import os
import requests
import pandas as pd

def get_data_from_version(domain, version):
    """get the ATT&CK STIX data for the given version from MITRE/CTI. Domain should be 'enterprise-attack', 'mobile-attack' or 'pre-attack'."""
    url = f"https://raw.githubusercontent.com/mitre/cti/ATT%26CK-{version}/{domain}/{domain}.json"
    stix_json = requests.get(url, verify=False).json()
    return MemoryStore(stix_data=stix_json["objects"])


def build_dataframes(src, include_deprecated=False):
    """build pandas dataframes for each attack type, and return a dictionary lookup for each type to the relevant dataframe"""
    # get each ATT&CK type
    return {
        "techniques": stixToDf.techniquesToDf(src, include_deprecated=False),
        "tactics": stixToDf.tacticsToDf(src, include_deprecated=False),
        "solationships": stixToDf.relationshipsToDf(src, include_deprecated=False)
    }

def main(domain, version, include_deprecated=False):
    """create excel files for the ATT&CK dataset of the specified domain and version"""
    # build dataframes
    dataframes = build_dataframes(get_data_from_version(domain, version), include_deprecated)
    # set up output directory
    domainVersionString = f"{domain}-{version}"
    if not os.path.exists(domainVersionString):
        os.mkdir(domainVersionString)
    # master dataset file
    master_writer = pd.ExcelWriter(os.path.join(domainVersionString, f"{domainVersionString}.xlsx"))
    # write individual dataframes
    for objType in dataframes:
        # write the dataframes for the object type into named sheets
        obj_writer = pd.ExcelWriter(os.path.join(domainVersionString, f"{domainVersionString}-{objType}.xlsx"))
        for dfname in dataframes[objType]: 
            dataframes[objType][dfname].to_excel(obj_writer, sheet_name=dfname) 
        obj_writer.save()
         # add main df to master dataset
        dataframes[objType][objType].to_excel(master_writer, sheet_name=objType)
    master_writer.save()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
         description="Convert ATT&CK STIX data to excel spreadsheets"
    )
    parser.add_argument("-domain",
        type=str,
        choices=["enterprise-attack", "mobile-attack"],
        default="enterprise-attack",
        help="which domain of ATT&CK to convert"
    )
    parser.add_argument("-version",
        type=str,
        default="v7.2",
        help=f"which version of ATT&CK to convert"
    )
    parser.add_argument("--include-deprecated",
        action="store_true",
        dest="include_deprecated",
        help=f"show deprecated and revoked objects"
    )
    args = parser.parse_args()
    
    main(args.domain, args.version, args.include_deprecated)
