import pandas as pd
from stix2 import Filter
from itertools import chain
from tqdm import tqdm

def remove_revoked_deprecated(stix_objects):
    """Remove any revoked or deprecated objects from queries made to the data source"""
    # Note we use .get() because the property may not be present in the JSON data. The default is False
    # if the property is not set.
    return list(
        filter(
            lambda x: x.get("x_mitre_deprecated", False) is False and x.get("revoked", False) is False,
            stix_objects
        )
    )

def format_date(date):
    """ Given a date string, format to %d %B %Y """
    if isinstance(date, str):
        date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    return ("{} {} {}").format(date.strftime("%d"), date.strftime("%B"), date.strftime("%Y"))

def techniquesToDf(src, domain):
    """convert the stix techniques to pandas dataframes. 
    Return a lookup of labels (descriptors) to dataframes"""
    techniques = src.query([Filter("type", "=", "attack-pattern")])
    techniques = remove_revoked_deprecated(techniques)
    rows = []
    for technique in tqdm(techniques, desc="parsing techniques"):
        # get parent technique if sub-technique
        subtechnique = "x_mitre_is_subtechnique" in technique and technique["x_mitre_is_subtechnique"]
        if subtechnique:
            subtechnique_of = src.query([
                Filter("type", "=", "relationship"),
                Filter("relationship_type", "=", "subtechnique-of"),
                Filter("source_ref", "=", technique["id"])
            ])[0]
            parent = src.get(subtechnique_of["target_ref"])
        
        tactics = list(map(lambda kcp: kcp["phase_name"], technique["kill_chain_phases"]))
        # general fields
        row = {
            "ATT&CK ID": technique["external_references"][0]["external_id"],
            "name": technique["name"] if not subtechnique else f"{parent['name']}: {technique['name']}",
            "description": technique["description"],
            "tactics": ", ".join(tactics),
            "version": technique["x_mitre_version"],
            "created": format_date(technique["created"]),
            "last modified": format_date(technique["modified"])
        }
        if "x_mitre_detection" in technique:
            row["detection"] = technique["x_mitre_detection"]
        if "x_mitre_platforms" in technique:
            row["platforms"] = ", ".join(technique["x_mitre_platforms"])


        # domain specific fields -- enterprise
        if domain == "enterprise-attack":
            row["is sub-technique"] = subtechnique
            if "x_mitre_data_sources" in technique:
                row["data sources"] = ", ".join(technique["x_mitre_data_sources"])
            if "privilege-escalation" in tactics and "x_mitre_permissions_required" in technique:
                row["permissions required"] = ", ".join(technique["x_mitre_permissions_required"])
            if "defense-evasion" in tactics and "x_mitre_defense_bypassed" in technique:
                row["defenses bypassed"] = ", ".join(technique["x_mitre_defense_bypassed"])
            if "execution" in tactics and "x_mitre_remote_support" in technique:
                row["supports remote"] = technique["x_mitre_remote_support"]
                
        # domain specific fields -- mobile
        elif domain == "mobile-attack":
            if "x_mitre_tactic_types" in technique:
                row["tactic type"] = technique["x_mitre_tactic_types"]
            mtc_refs = list(filter(lambda ref: ref["source_name"] == "NIST Mobile Threat Catalogue", technique["external_references"]))
            if mtc_refs:
                row["MTC ID"] = mtc_refs[0]["external_id"]
        
        rows.append(row)
    return {
        "techniques": pd.DataFrame(rows).sort_values("name")
    }

def tacticsToDf(src, domain):
    """convert the stix tactics to pandas dataframes. 
    Return a lookup of labels (descriptors) to dataframes"""
    tactics = src.query([Filter("type", "=", "x-mitre-tactic")])
    if not include_deprecated: tactics = remove_revoked_deprecated(tactics)

    return {}

def softwareToDf(src, domain):
    """convert the stix software to pandas dataframes. 
    Return a lookup of labels (descriptors) to dataframes"""
    software = list(chain.from_iterable( # software are the union of the tool and malware types
        src.query(f) for f in [Filter("type", "=", "tool"), Filter("type", "=", "malware")]
    ))
    if not include_deprecated: software = remove_revoked_deprecated(software)

    return {}

def groupsToDf(src, domain):
    """convert the stix groups to pandas dataframes. 
    Return a lookup of labels (descriptors) to dataframes"""
    groups = src.query([Filter("type", "=", "intrusion-set")])
    if not include_deprecated: groups = remove_revoked_deprecated(groups)

    return {}

def mitigationsToDf(src, domain):
    """convert the stix mitigations to pandas dataframes. 
    Return a lookup of labels (descriptors) to dataframes"""
    mitigations = src.query([Filter("type", "=", "course-of-action")])
    if not include_deprecated: mitigations = remove_revoked_deprecated(mitigations)

    return {}

def matricesToDf(src, domain):
    """convert the stix matrices to pandas dataframes. 
    Return a lookup of labels (descriptors) to dataframes"""
    matrices = src.query([Filter("type", "=", "x-mitre-matrix")])
    if not include_deprecated: matrices = remove_revoked_deprecated(matrices)

    return {}

def relationshipsToDf(src, domain):
    """convert the stix relationships to pandas dataframes. 
    Return a lookup of labels (descriptors) to dataframes"""
    relationships = src.query([Filter("type", "=", "relationship")])
    if not include_deprecated: relationships = remove_revoked_deprecated(relationships)

    return {}

