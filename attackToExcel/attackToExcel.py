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


def build_dataframes(src, domain):
    """build pandas dataframes for each attack type, and return a dictionary lookup for each type to the relevant dataframe"""
    # get each ATT&CK type
    return {
        "techniques": stixToDf.techniquesToDf(src, domain),
        "tactics": stixToDf.tacticsToDf(src, domain),
        "software": stixToDf.softwareToDf(src, domain),
        "groups": stixToDf.groupsToDf(src, domain),
        "mitigations": stixToDf.mitigationsToDf(src, domain),
        "matrices": stixToDf.matricesToDf(src, domain),
        "relationships": stixToDf.relationshipsToDf(src)
    }

def main(domain, version):
    """create excel files for the ATT&CK dataset of the specified domain and version"""
    # build dataframes
    dataframes = build_dataframes(get_data_from_version(domain, version), domain)
    print("writing and formatting files... ", end="", flush=True)
    # set up output directory
    domainVersionString = f"{domain}-{version}"
    if not os.path.exists(domainVersionString):
        os.mkdir(domainVersionString)
    # master dataset file
    master_writer = pd.ExcelWriter(os.path.join(domainVersionString, f"{domainVersionString}.xlsx"), engine='xlsxwriter')
    citations = pd.DataFrame() # master list of citations
    # write individual dataframes and add to master writer
    for objType in dataframes:
        if objType != "matrices":
            # write the dataframes for the object type into named sheets
            obj_writer = pd.ExcelWriter(os.path.join(domainVersionString, f"{domainVersionString}-{objType}.xlsx"))
            for dfname in dataframes[objType]: 
                dataframes[objType][dfname].to_excel(obj_writer, sheet_name=dfname, index=False) 
            obj_writer.save()

            # add citations to master citations list
            if "citations" in dataframes[objType]:
                citations = citations.append(dataframes[objType]["citations"])

            # add main df to master dataset
            dataframes[objType][objType].to_excel(master_writer, sheet_name=objType, index=False)
        else: # handle matrix special formatting
            # TODO add name and description
            matrix_writer = pd.ExcelWriter(os.path.join(domainVersionString, f"{domainVersionString}-{objType}.xlsx"), engine='xlsxwriter')

            for matrix in dataframes[objType]:
                sheetname = "matrix" if len(dataframes[objType]) == 1 else matrix["name"] + " matrix"
                matrix["matrix"].to_excel(master_writer, sheet_name=sheetname, index=False)
                matrix["matrix"].to_excel(matrix_writer, sheet_name=sheetname, index=False)
                # track added formats
                for writer in [master_writer, matrix_writer]:
                    # define column border styles
                    borderleft = writer.book.add_format({"left": 1})
                    borderright = writer.book.add_format({"right": 1})

                    formats = {} # formats already defined on the writer
                    sheet = writer.sheets[sheetname]
                    # merge ranges
                    for mergeRange in matrix["merge"]:
                        if mergeRange.format:
                            if mergeRange.format["name"] not in formats: # add format to book if not defined
                                formats[mergeRange.format["name"]] = writer.book.add_format(mergeRange.format["format"])
                            theformat = formats[mergeRange.format["name"]] # get saved format if already added
                            if mergeRange.format["name"] == "tacticHeader": 
                                # also set border for entire column for grouping
                                sheet.set_column(
                                    mergeRange.leftCol - 1,
                                    mergeRange.leftCol - 1,
                                    width=20, # set column widths to make matrix more readable
                                    cell_format=borderleft
                                )
                                sheet.set_column(
                                    mergeRange.rightCol - 1,
                                    mergeRange.rightCol - 1,
                                    width=20, # set column widths to make matrix more readable
                                    cell_format=borderright
                                )
                        else: theformat = None # no format
                        sheet.merge_range(mergeRange.to_excel(), mergeRange.data, theformat)
                        
            matrix_writer.save()

    # remove duplicate citations and add to master file
    citations.drop_duplicates(subset="reference", ignore_index=True).sort_values("reference").to_excel(master_writer, sheet_name="citations", index=False)
    # write the master file
    master_writer.save()
    print("done")

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
    args = parser.parse_args()
    
    main(args.domain, args.version)
