import json, os, shutil, sys
from stix2 import TAXIICollectionSource, Filter
from taxii2client.v20 import Collection
from pprint import pprint
import argparse
from tqdm import tqdm
from tabulate import tabulate

# if verbose is set to True, additional processing logs will be printed to stdout
verbose = False

######## MAPS FOR TECHNIQUES #########
# technique name (string) -> STIX ID (string)
tech_to_id={}
# technique name (string) -> data sources (array of strings)
tech_to_data={}
# technique name (string) -> tactics (array of strings)
tech_to_tac={}
# technique name (string) -> permissions (array of strings)
# Note: sometimes empty
tech_to_perm={}
# technique name (string) -> platforms (array of strings)
tech_to_plat={}
# technique name (string) -> defenses evaded (array of strings)
# Note: sometimes empty
tech_to_def={}
# technique name (string) -> software (array of strings)
tech_to_software={}
# technique name (string) -> group (array of strings)
tech_to_group={}

######## MAPS FOR SOFTWARE ###########
# software name (string) -> STIX ID (string)
software_to_id={}
# software name (string) -> techniques (array of strings)
software_to_tech={}
# software name (string) -> groups (array of strings)
software_to_group={}

######## MAPS FOR GROUPS ############
# group name (string) -> STIX ID (string)
group_to_id={}
# group name (string) -> techniques (array of strings)
group_to_tech={}
# group name (string) -> software (array of strings)
group_to_software={}

######## MAPS FOR IDS ###############
# STIX ID (string) -> technique name (string)
id_to_tech={}
# STIX ID (string) -> software name (string)
id_to_software={}
# STIX ID (string) -> group name (string)
id_to_group={}

######## OTHER MAPS #################
# tactics (string) -> permissions (dictionary: permission string -> count integer)
tactics_to_permission={}


def add_link(alpha, beta, alpha_dict, beta_dict):
    """helper function for parsing relationships.
    
    arguments:
        alpha: string, the first item in the relationship
        beta:  string, the second item in the relationship
        alpha_dict: dict, the data structure for storing items of the same type as alpha
        beta_dict:  dict, the data structure for storing items of the same type as beta
    """
    
    if alpha not in alpha_dict:
        alpha_dict[alpha]=[]
    if beta not in beta_dict:
        beta_dict[beta]=[]
    if alpha not in beta_dict[beta]:
        beta_dict[beta].append(alpha)
    if beta not in alpha_dict[alpha]:
        alpha_dict[alpha].append(beta)


def makelower(indict):
    """return a copy of a string->string dict such that all keys and values are lowercase."""

    return {k.lower(): v for k, v in indict.items()}


def establish_connection(collection: str):
    """establish a connection with the TAXII server.

    arguments: 
        collection: string, the url of the collection with which to connect.

    returns: 
        connection to the taxii collection
    """

    
    # Establish TAXII2 Collection instance for Enterprise ATT&CK collection
    collection = Collection(collection)
    # Supply the collection to TAXIICollection
    tc_src = TAXIICollectionSource(collection)
    return tc_src


def parse_tactics():
    """creates mappings from tactics to permissions. Requires that the technique dictionaries have been loaded already; see parse_techniques."""
    
    # Iterate over each technique
    for tech in tech_to_tac:
        # Iterate over each tactic
        for tac in tech_to_tac[tech]:
            # Initialize this one, if it hasn't already been
            if tac not in tactics_to_permission:
                tactics_to_permission[tac]={}
            # Now iterate over each permission
            for perm in tech_to_perm[tech]:
                if perm not in tactics_to_permission[tac]:
                    tactics_to_permission[tac][perm]=0
                tactics_to_permission[tac][perm]=tactics_to_permission[tac][perm] + 1


def parse_software(software_set):
    """parse stix software into appropriate data structures.

    arguments:
        software_set: list of stix-formatted software dicts
    """

    for entry in software_set:
        name=entry['name']
        cur_id=entry['id']
        if name not in software_to_id:
            software_to_id[name]=cur_id
            id_to_software[cur_id]=name


def parse_groups(group_set):
    """parse stix groups into appropriate data structures.

    arguments:
        group_set: list of stix-formatted group dicts
    """

    for entry in group_set:
        name=entry['name']
        cur_id=entry['id']
        if name not in group_to_id:
            group_to_id[name]=cur_id
            id_to_group[cur_id]=name


def parse_relationships(relationships):
    """parse stix relationships into appropriate data structures.

    arguments:
        relationships: list of stix-formatted relationship dicts
    """

    # Iterate over each relationship
    for obj in relationships:
        # Load the source and target STIX IDs
        src=obj['source_ref']
        tgt=obj['target_ref']
        # Handle each case
        if src in id_to_tech and tgt in id_to_group:
            add_link(id_to_tech[src], id_to_group[tgt], tech_to_group, group_to_tech)
        if src in id_to_tech and tgt in id_to_software:
            add_link(id_to_tech[src], id_to_software[tgt], tech_to_software, software_to_tech)
        if src in id_to_software and tgt in id_to_group:
            add_link(id_to_software[src], id_to_group[tgt], software_to_group, group_to_software)
        if src in id_to_software and tgt in id_to_tech:
            add_link(id_to_software[src], id_to_tech[tgt], software_to_tech, tech_to_software)
        if src in id_to_group and tgt in id_to_tech:
            add_link(id_to_group[src], id_to_tech[tgt], group_to_tech, tech_to_group)
        if src in id_to_group and tgt in id_to_software:
            add_link(id_to_group[src], id_to_software[tgt], group_to_software, software_to_group)


def parse_techniques(techniques):
    """parse stix techniques into appropriate data structures.

    arguments:
        techniques: list of stix-formatted technique dicts
    """

    # Iterate over each technique object
    for obj in techniques:
        # Easy-access the technique's name
        tech=obj['name']
        # Go through each technique dictionary global
        # If we haven't seen this technique before, we need to initialize the array
        if tech not in tech_to_data:
            tech_to_data[tech]=[]
        if tech not in tech_to_tac:
            tech_to_tac[tech]=[]
        if tech not in tech_to_perm:
            tech_to_perm[tech]=[]
        if tech not in tech_to_plat:
            tech_to_plat[tech]=[]
        if tech not in tech_to_def:
            tech_to_def[tech]=[]
        # Store the ID number
        if 'id' in obj:
            tech_to_id[tech]=obj['id']
            id_to_tech[obj['id']]=tech
        # Store the tactics
        if 'kill_chain_phases' in obj:
            for pair in obj['kill_chain_phases']:
                if 'phase_name' in pair:
                    tac=pair['phase_name']
                    if tac not in tech_to_tac[tech]:
                        tech_to_tac[tech].append(tac)
        # Store the platforms the technique applies to
        if 'x_mitre_platforms' in obj:
            for plat in obj['x_mitre_platforms']:
                if plat not in tech_to_plat[tech]:
                    tech_to_plat[tech].append(plat)
        # Store the data sources we can monitor to detect the technique
        if 'x_mitre_data_sources' in obj:
            for src in obj['x_mitre_data_sources']:
                if src not in tech_to_data[tech]:
                    tech_to_data[tech].append(src)
        # Store the defenses the technique bypasses
        if 'x_mitre_defense_bypassed' in obj:
            for defb in obj['x_mitre_defense_bypassed']:
                if defb not in tech_to_def[tech]:
                    tech_to_def[tech].append(defb)
        # Store the permissions required to execute the technique
        if 'x_mitre_permissions_required' in obj:
            for perm in obj['x_mitre_permissions_required']:
                if perm not in tech_to_perm[tech]:
                    tech_to_perm[tech].append(perm)

    # As a note: sometimes permissions required lists user + root permissions
    # This code below makes sure only User is listed as a permission if it's a required permission
    # (rationale: if a technique requires user permission, it stands to reason you can run it as Administrator/SYSTEM/root)
    for tech in tech_to_perm:
        if 'User' in tech_to_perm[tech]:
            tech_to_perm[tech]=['User']


def write_DPT(output_directory):
    """writes a CSV that links techniques, defenses, permissions, and tactics.
    
    specifically, the output will link:
        a specific technique, to
        a defense the technique bypassess, to
        the permissions needed to run the technique,
        repeated for each defense and tactic that is linked to the technique

    arguments:
        output_directory: string. The folder the output data will be written to. The folder will be created if it doesn't already exist.
    """


    output_file = os.path.join(output_directory, "dpt.csv")
    # Make sure the directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    with open (output_file, "w") as output_file:
        # Write the header of the CSV
        output_file.write("tech,defense,permission\n")
        # Iterate through each technique, defense, and permission
        for tech in tech_to_def:
            for defn in tech_to_def[tech]:
                for perm in tech_to_perm[tech]:
                    output_file.write(tech.lower() + "," + defn.lower() + "," + perm.lower() + "\n")


def write_tacticsToTechniques(output_directory="generated_content"):
    """write a csv linking tactics to techniques.
    
    arguments:
        output_directory: string. The folder the output data will be written to. The folder will be created if it doesn't already exist.
    """
    output_file = os.path.join(output_directory, "tacticsToTechniques.csv")
    # Make sure the directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    with open (output_file, "w") as output_file:
        # Write the header of the CSV
        output_file.write("technique,tactic\n")
        for tech in tech_to_tac:
            for tac in tech_to_tac[tech]:
                output_file.write(tech.lower() + "," + tac.lower() + "\n")


def write_TSG(specified_techniques=None, output_directory="generated_content"):
    """write a csv linking techniques, software and groups.
    
    specifically, the output will link:
        techniques, to
        software implementing those techniques, to
        groups using the software

    arguments:
        specified_techniques: string[] of techniques to link. All other techniques will be ignored. If this argument is not specified 
                              it will output all techniques.
        output_directory: string. The folder the output data will be written to. The folder will be created if it doesn't already exist.
    """

    filename = "tsg_subset.csv" if specified_techniques is not None else "tsg.csv"
    output_file = os.path.join(output_directory, filename)
    # Make sure the directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    with open (output_file, "w") as output_file:
        # Write the header of the CSV
        output_file.write("technique,software,group\n")
        # only process techniques we want to output
        # if we don't specify any desired techniques, all techniques will be processed
        desired_techniques = list(filter(lambda t: specified_techniques is None or t in specified_techniques, tech_to_software))
        for tech in desired_techniques:
            for software in tech_to_software[tech]:
                # Some software may not be used by groups
                if software not in software_to_group:
                    continue
                for group in software_to_group[software]:
                    output_file.write(tech.lower() + "," + software.lower() + "," + group.lower() + "\n")


def write_tacticPermissions(output_directory="generated_content"):
    """write a CSV showing the number of techniques in a tactic that require a minimum permission.

    arguments:
        output_directory: string. The folder the output data will be written to. The folder will be created if it doesn't already exist.
    """

    output_file = os.path.join(output_directory, "tacticPermissions.csv")
    # Make sure the directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    with open (output_file, "w") as output_file:
        # Write the header of the CSV
        output_file.write("tactic,permission,technique count\n")
        for tac in tactics_to_permission:
            for perm in tactics_to_permission[tac]:
                output_file.write(tac.lower() + "," + perm.lower() + "," + str(tactics_to_permission[tac][perm]) + "\n")


def write_techniquesToDatasources(data_sources, output_directory="generated_content"):
    """write a CSV linking techniques to the data sources that can potentially detect those techniques.

    arguments:
        data_sources: string[] of datasource names. The output will be filtered according to this list.
        output_directory: string. The folder the output data will be written to. The folder will be created if it doesn't already exist.
    """

    output_file = os.path.join(output_directory, "techniques_datasources.csv")
    # make sure the directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    with open (output_file, "w") as output_file:
        # Write the header of the CSV
        output_file.write("technique,data source\n")
        for tech in tech_to_data:
            for data in tech_to_data[tech]:
                if data.lower() in data_sources:
                    output_file.write(tech.lower() + "," + data.lower() + "\n")


def generate_content(data_sources_list, tactics_to_visualize, output_directory="generated_content"):
    """download, parse and write content to csv.

    arguments:
        data_sources_list: string[] of datasource names. techniques_datasources.csv will be filtered according to this list
        tactics_to_visualize: string[] of tactic names. tsg_subset.csv will be filtered according to this list
        output_directory: string. The folder the output data will be written to. The folder will be created if it doesn't already exist.
    """

    # establish the connection to the TAXII server
    if verbose: print("establishing connection... ", end="", flush=True)
    tc_src = establish_connection("https://cti-taxii.mitre.org/stix/collections/95ecc380-afe9-11e4-9b6c-751b66dd541e/")
    if verbose: print("done!")

    # Get all techniques in Enterprise ATT&CK
    # use tqdm progress bar if verbose mode is enabled
    if verbose: pbar = tqdm(total=5, desc="retrieving data", bar_format="{desc} |{bar}| {percentage:3.0f}%  ", ncols=35)
    techniques = tc_src.query([Filter("type", "=", "attack-pattern")])
    if verbose: pbar.update(1)
    tools_set = tc_src.query([Filter("type", "=", "tool")])
    if verbose: pbar.update(1)
    malwares = tc_src.query([Filter("type", "=", "malware")])
    if verbose: pbar.update(1)
    intrusion_sets = tc_src.query([Filter("type", "=", "intrusion-set")])
    if verbose: pbar.update(1)
    relationships = tc_src.query([Filter("type", "=", "relationship")])
    if verbose: 
        pbar.update(1)
        print("") # tqdm needs a newline after the bar finishes

    # parse technique, software, and groups into helper dictionaries
    if verbose: print("parsing data... ", end="", flush=True)
    parse_techniques(techniques)
    parse_software(tools_set)
    parse_software(malwares)
    parse_groups(intrusion_sets)
    # parse relationships between techniques, software, and groups
    parse_relationships(relationships)
    # pars the tactics -> permissions counter
    parse_tactics()

    if verbose: 
        print("done!")
        print("writing output to directory " + output_directory + "... ", end="", flush=True)

    # write output files
    write_DPT(output_directory)
    write_tacticsToTechniques(output_directory)
    write_TSG(output_directory=output_directory)
    # tsg is too big for visualization, so write a subset version
    # select by tactics specified by user
    selected_techs=[]
    for tech in tech_to_tac:
        techniqueHasTactic = not set(tactics_to_visualize).isdisjoint(set(tech_to_tac[tech]))
        if techniqueHasTactic:
            selected_techs.append(tech)

    write_TSG(selected_techs, output_directory)
    # Write tactics -> permission file
    write_tacticPermissions(output_directory)
    # Write techniques + data sources
    write_techniquesToDatasources(data_sources_list, output_directory)
    if verbose: print("done!")


if __name__ == "__main__":
    # terminal colors for help highlighting
    defaultValColor = '\033[94m' # blue
    endcolor = '\033[0m' # reset color to default

    # helper function for color formatting of default values in help output
    def defaultStr(multi=False):
        if multi: return " Default values are " + defaultValColor + "%(default)s" + endcolor+ "."
        else: return " Default value is " + defaultValColor + "%(default)s" + endcolor+ "."

    # description of output files, for help output
    outfile_descs = tabulate(
        [
            (
                "dpt.csv",
                "links techniques to bypassed defenses to permissions, for each defense\nand tactic linked to the technique"
            ),
            (
                "tacticPermissions.csv",
                "shows the number of techniques in each tactic that require a minimum permission"
            ),
            (
                "tacticsToTechniques.csv",
                "links tactics to techniques"
            ),
            (
                "techniques_datasources.csv",
                "links techniques to the data sources that can potentially detect them"
            ),
            (
                "tsg.csv",
                "links techniques to software implementing them to groups using the software"
            ),
            (
                "tsg_subset.csv",
                "the same as tsg.csv but filtering to techniques in a subset of tactics"
            )
        ], 
        headers=("filename", "description"),
        colalign=("right",),
        tablefmt="fancy_grid"
    )

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=(
            "Generate the csv data used to create the ATT&CK data sources visualization." "\n\n"
            "The following files are created:" "\n\n"
            f"{outfile_descs}"
        )
    )
    parser.add_argument("-datasources",
        type=str,
        nargs="+",
        metavar=("datasource1", "datasource2"),
        default=[
            "user account: user account creation",
            "active directory: active directory object creation",
            "container: container creation",
            "driver: driver load",
            "file: file deletion",
            "firmware: firmware modification",
            "instance: instance creation",
            "logon session: logon session metadata",
            "scheduled job: scheduled job creation",
            "service: service modification",
            "process: process metadata",
            "sensor health: host status"
        ],
        help="list data source names for datasources written in techniques_datasources.csv." + defaultStr(True)
    )
    parser.add_argument("-tactics",
        type=str,
        nargs="+",
        metavar=("tactic1", "tactic2"),
        default=["collection"],
        help="list tactic names for techniques written in tsg_subset.csv." + defaultStr()
    )
    parser.add_argument("-output",
        type=str,
        metavar="output_folder",
        dest="output_folder",
        default="generated_content",
        help="directory in which to put output csv." + defaultStr()
    )
    parser.add_argument("-v", "--verbose",
        dest="verbose",
        action='store_true',
        default=False,
        help="enable verbose logging."
    )

    args = parser.parse_args()
    verbose = args.verbose
    generate_content(args.datasources, args.tactics, args.output_folder)
   
