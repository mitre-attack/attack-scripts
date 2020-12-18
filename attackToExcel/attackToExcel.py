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

def write_excel(dataframes, domain, version, outputDir="."):
    """given a set of dataframes from build_dataframes, write the ATT&CK dataset to output directory"""

    print("writing formatted files... ", end="", flush=True)
    # master list of files that have been written
    written_files = []
    # set up output directory
    domainVersionString = f"{domain}-{version}"
    outputDirectory = os.path.join(outputDir, domainVersionString)
    if not os.path.exists(outputDirectory):
        os.makedirs(outputDirectory)
    # master dataset file
    master_fp = os.path.join(outputDirectory, f"{domainVersionString}.xlsx")
    master_writer = pd.ExcelWriter(master_fp, engine='xlsxwriter')
    citations = pd.DataFrame() # master list of citations
    # write individual dataframes and add to master writer
    for objType in dataframes:
        if objType != "matrices":
            # write the dataframes for the object type into named sheets
            fp = os.path.join(outputDirectory, f"{domainVersionString}-{objType}.xlsx")
            obj_writer = pd.ExcelWriter(fp)
            for dfname in dataframes[objType]: 
                dataframes[objType][dfname].to_excel(obj_writer, sheet_name=dfname, index=False) 
            obj_writer.save()
            written_files.append(fp)

            # add citations to master citations list
            if "citations" in dataframes[objType]:
                citations = citations.append(dataframes[objType]["citations"])

            # add main df to master dataset
            dataframes[objType][objType].to_excel(master_writer, sheet_name=objType, index=False)
        else: # handle matrix special formatting
            fp = os.path.join(outputDirectory, f"{domainVersionString}-{objType}.xlsx")
            matrix_writer = pd.ExcelWriter(fp, engine='xlsxwriter')
            for matrix in dataframes[objType]: # some domains have multiple matrices
                sheetname = "matrix" if len(dataframes[objType]) == 1 else matrix["name"] + " matrix" # name them accordingly if there are multiple
                matrix["matrix"].to_excel(master_writer, sheet_name=sheetname, index=False) # write unformatted matrix data to master file
                matrix["matrix"].to_excel(matrix_writer, sheet_name=sheetname, index=False) # write unformatted matrix to matrix file
                
                # for each writer, format the matrix for readability
                for writer in [master_writer, matrix_writer]:
                    # define column border styles
                    borderleft = writer.book.add_format({"left": 1, "shrink": 1})
                    borderright = writer.book.add_format({"right": 1, "shrink": 1})
                    formats = {} # formats only need to be defined once: pointers stored here for subsequent uses
                    sheet = writer.sheets[sheetname]

                    sheet.set_column(0, matrix["columns"], width=20) # set all columns to 20 width, and add text shrinking to fit

                    # merge supertechniques and tactic headers if sub-techniques are present on a tactic
                    for mergeRange in matrix["merge"]:
                        if mergeRange.format: # sometimes merge ranges have formats to add to the merged range
                            if mergeRange.format["name"] not in formats: # add format to book if not defined
                                formats[mergeRange.format["name"]] = writer.book.add_format(mergeRange.format["format"])
                            theformat = formats[mergeRange.format["name"]] # get saved format if already added
                            if mergeRange.format["name"] == "tacticHeader": # tactic header merge has additional behavior
                                # also set border for entire column for grouping
                                sheet.set_column(
                                    mergeRange.leftCol - 1,
                                    mergeRange.leftCol - 1,
                                    width=20, # set column widths to make matrix more readable
                                    cell_format=borderleft # left border around tactic
                                )
                                sheet.set_column(
                                    mergeRange.rightCol - 1,
                                    mergeRange.rightCol - 1,
                                    width=20, # set column widths to make matrix more readable
                                    cell_format=borderright # right border around tactic
                                )
                        else: theformat = None # no format
                        sheet.merge_range(mergeRange.to_excel_format(), mergeRange.data, theformat) # apply the merge
            
            matrix_writer.save() # save the matrix data
            written_files.append(fp)
            # end of matrix sheet writing

    # remove duplicate citations and add sheet to master file
    citations.drop_duplicates(subset="reference", ignore_index=True).sort_values("reference").to_excel(master_writer, sheet_name="citations", index=False)
    # write the master file
    master_writer.save()
    written_files.append(master_fp)
    print("done")
    print("files created:")
    for thefile in written_files:
        print("\t", thefile)
    return written_files


def main(domain, version, outputDir):
    """create excel files for the ATT&CK dataset of the specified domain and version"""
    # build dataframes
    dataframes = build_dataframes(get_data_from_version(domain, version), domain)
    write_excel(dataframes, domain, version, outputDir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
         description="Convert ATT&CK STIX data to excel spreadsheets"
    )
    parser.add_argument("-domain",
        type=str,
        choices=["enterprise-attack", "mobile-attack", "ics-attack"],
        default="enterprise-attack",
        help="which domain of ATT&CK to convert"
    )
    parser.add_argument("-version",
        type=str,
        default="v8.1",
        help="which version of ATT&CK to convert"
    )
    parser.add_argument("-output",
        type=str,
        default=".",
        help="output directory"
    )
    args = parser.parse_args()
    
    main(args.domain, args.version, args.output)
