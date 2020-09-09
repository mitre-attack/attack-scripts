import pandas as pd
from stix2 import Filter
from itertools import chain
from tqdm import tqdm
import datetime

attackToStixTerm = {
    "technique": ["attack-pattern"],
    "tactic": ["x-mitre-tactic"],
    "software": ["tool", "malware"],
    "group": ["intrusion-set"],
    "mitigation": ["course-of-action"],
    "matrix": ["x-mitre-matrix"],
}
stixToAttackTerm = {
    "attack-pattern": "technique",
    "x-mitre-tactic": "tactic",
    "tool": "software",
    "malware": "software",
    "intrusion-set": "group",
    "course-of-action": "mitigation",
    "x-mitre-matrix": "matrix"
}

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

def get_citations(objects):
    """given a list of STIX objects, return a pandas dataframe for the citations on the objects"""
    citations = []
    for sdo in objects:
        if "external_references" in sdo:
            for ref in sdo["external_references"]:
                if "external_id" not in ref and "description" in ref and not ref["description"].startswith("(Citation: "):
                    citation = {
                        "reference": ref["source_name"],
                        "citation": ref["description"]
                    }
                    if "url" in ref:
                        citation["url"] = ref["url"]

                    citations.append(citation)
    return pd.DataFrame(citations).drop_duplicates(subset="reference", ignore_index=True)

def parseBaseStix(sdo):
    """given an SDO, return a row of fields that are common across the STIX types"""
    row = {}
    if "external_references" in sdo and sdo["external_references"][0]["source_name"] in ["mitre-attack", "mitre-mobile-attack"]:
        row["ID"] = sdo["external_references"][0]["external_id"]
        row["url"] = sdo["external_references"][0]["url"]
    if "name" in sdo:
        row["name"] = sdo["name"]
    if "description" in sdo:
        row["description"] = sdo["description"]
    if "created" in sdo:
        row["created"] = format_date(sdo["created"])
    if "modified" in sdo:
        row["last modified"] = format_date(sdo["modified"])
    if "x_mitre_version" in sdo:
        row["version"] = sdo["x_mitre_version"]
    if "x_mitre_contributors" in sdo:
        row["contributors"] = "; ".join(sorted(sdo["x_mitre_contributors"]))
    return row

def techniquesToDf(src, domain):
    """convert the stix techniques to pandas dataframes. 
    Return a lookup of labels (descriptors) to dataframes"""
    techniques = src.query([Filter("type", "=", "attack-pattern")])
    techniques = remove_revoked_deprecated(techniques)
    technique_rows = []

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

        # base STIX properties
        row = parseBaseStix(technique)
        
        # sub-technique properties

        tactics = list(map(lambda kcp: kcp["phase_name"].replace("-", " ").title(), technique["kill_chain_phases"]))
        row["tactics"] = ", ".join(sorted(tactics))

        if "x_mitre_detection" in technique:
            row["detection"] = technique["x_mitre_detection"]
        if "x_mitre_platforms" in technique:
            row["platforms"] = ", ".join(sorted(technique["x_mitre_platforms"]))

        # domain specific fields -- enterprise
        if domain == "enterprise-attack":
            row["is sub-technique"] = subtechnique
            if subtechnique: 
                row["name"] = f"{parent['name']}: {technique['name']}"
                row["sub-technique of"] = parent["external_references"][0]["external_id"]

            if "x_mitre_data_sources" in technique:
                row["data sources"] = ", ".join(sorted(technique["x_mitre_data_sources"]))
            if "privilege-escalation" in tactics and "x_mitre_permissions_required" in technique:
                row["permissions required"] = ", ".join(sorted(technique["x_mitre_permissions_required"]))
            if "defense-evasion" in tactics and "x_mitre_defense_bypassed" in technique:
                row["defenses bypassed"] = ", ".join(sorted(technique["x_mitre_defense_bypassed"]))
            if "execution" in tactics and "x_mitre_remote_support" in technique:
                row["supports remote"] = technique["x_mitre_remote_support"]
                
        # domain specific fields -- mobile
        elif domain == "mobile-attack":
            if "x_mitre_tactic_types" in technique:
                row["tactic type"] = technique["x_mitre_tactic_types"]
            mtc_refs = list(filter(lambda ref: ref["source_name"] == "NIST Mobile Threat Catalogue", technique["external_references"]))
            if mtc_refs:
                row["MTC ID"] = mtc_refs[0]["external_id"]
        
        technique_rows.append(row)

    citations = get_citations(techniques)
    dataframes =  {
        "techniques": pd.DataFrame(technique_rows).sort_values("name"),
    }
    # add relationships
    dataframes.update(relationshipsToDf(src, relatedType="technique"))
    # add/merge citations
    if not citations.empty: 
        if "citations" in dataframes: # append to existing citations from references
            dataframes["citations"].append(citations)
        else: # add citations
            dataframes["citations"] = citations
        
        dataframes["citations"].sort_values("reference")

    return dataframes

def tacticsToDf(src, domain):
    """convert the stix tactics to pandas dataframes. 
    Return a lookup of labels (descriptors) to dataframes"""
    tactics = src.query([Filter("type", "=", "x-mitre-tactic")])
    tactics = remove_revoked_deprecated(tactics)

    tactic_rows = []
    for tactic in tqdm(tactics, desc="parsing mitigations"):
        tactic_rows.append(parseBaseStix(tactic))

    citations = get_citations(tactics)
    dataframes =  {
        "tactics": pd.DataFrame(tactic_rows).sort_values("name"),
    }
    if not citations.empty: dataframes["citations"] = citations.sort_values("reference")

    return dataframes

def softwareToDf(src, domain):
    """convert the stix software to pandas dataframes. 
    Return a lookup of labels (descriptors) to dataframes"""
    software = list(chain.from_iterable( # software are the union of the tool and malware types
        src.query(f) for f in [Filter("type", "=", "tool"), Filter("type", "=", "malware")]
    ))
    software = remove_revoked_deprecated(software)
    software_rows = []
    for soft in tqdm(software, desc="parsing software"):
        # add common STIx fields
        row = parseBaseStix(soft)
        # add software-specific fields
        if "x_mitre_platforms" in soft:
            row["platforms"] = ", ".join(sorted(soft["x_mitre_platforms"]))
        if "x_mitre_aliases" in soft:
            row["aliases"] = ", ".join(sorted(soft["x_mitre_aliases"]))
        row["type"] = soft["type"] # malware or tool
        
        software_rows.append(row)

    citations = get_citations(software)
    dataframes =  {
        "software": pd.DataFrame(software_rows).sort_values("name"),
    }
    # add relationships
    dataframes.update(relationshipsToDf(src, relatedType="software"))
    # add/merge citations
    if not citations.empty: 
        if "citations" in dataframes: # append to existing citations from references
            dataframes["citations"].append(citations)
        else: # add citations
            dataframes["citations"] = citations
        
        dataframes["citations"].sort_values("reference")

    return dataframes

def groupsToDf(src, domain):
    """convert the stix groups to pandas dataframes. 
    Return a lookup of labels (descriptors) to dataframes"""
    groups = src.query([Filter("type", "=", "intrusion-set")])
    groups = remove_revoked_deprecated(groups)
    group_rows = []
    for group in tqdm(groups, desc="parsing groups"):
        group_rows.append(parseBaseStix(group))
    
    citations = get_citations(groups)
    dataframes = {
        "groups": pd.DataFrame(group_rows).sort_values("name"),
    }
    # add relationships
    dataframes.update(relationshipsToDf(src, relatedType="group"))
    # add/merge citations
    if not citations.empty: 
        if "citations" in dataframes: # append to existing citations from references
            dataframes["citations"].append(citations)
        else: # add citations
            dataframes["citations"] = citations
        
        dataframes["citations"].sort_values("reference")
        
    return dataframes

def mitigationsToDf(src, domain):
    """convert the stix mitigations to pandas dataframes. 
    Return a lookup of labels (descriptors) to dataframes"""
    mitigations = src.query([Filter("type", "=", "course-of-action")])
    mitigations = remove_revoked_deprecated(mitigations)
    mitigation_rows = []
    for mitigation in tqdm(mitigations, desc="parsing mitigations"):
        mitigation_rows.append(parseBaseStix(mitigation))
    
    citations = get_citations(mitigations)
    dataframes = {
        "mitigations": pd.DataFrame(mitigation_rows).sort_values("name"),
    }
    # add relationships
    dataframes.update(relationshipsToDf(src, relatedType="mitigation"))
    # add/merge citations
    if not citations.empty: 
        if "citations" in dataframes: # append to existing citations from references
            dataframes["citations"].append(citations)
        else: # add citations
            dataframes["citations"] = citations
        
        dataframes["citations"].sort_values("reference")
        
    return dataframes

def matricesToDf(src, domain):
    """convert the stix matrices to pandas dataframes. 
    Return a lookup of labels (descriptors) to dataframes"""
    matrices = src.query([Filter("type", "=", "x-mitre-matrix")])
    matrices = remove_revoked_deprecated(matrices)

    return {}

def relationshipsToDf(src, relatedType=None):
    """convert the stix relationships to pandas dataframes. 
    args: 
        src: the ATT&CK dataset
        relatedType: (optional) string, singular attack type to only return relationships with, e.g "mitigation"
    Return a lookup of labels (descriptors) to dataframes"""
    relationships = src.query([Filter("type", "=", "relationship")])
    relationships = remove_revoked_deprecated(relationships)
    relationship_rows = []
    used_relationships = []
    iterdesc = "parsing all relationships" if not relatedType else f"parsing relationships for type={relatedType}"
    for relationship in tqdm(relationships, desc=iterdesc):
        source = src.get(relationship["source_ref"])
        target = src.get(relationship["target_ref"])
        
        # filter if related objects don't exist or are revoked or deprecated
        if not source or source.get("x_mitre_deprecated", False) is True or source.get("revoked", False) is True: 
            continue
        if not target or target.get("x_mitre_deprecated", False) is True or target.get("revoked", False) is True: 
            continue
        if relationship["relationship_type"] == "revoked": 
            continue
        
        # don't track sub-technique relationships, those are tracked in the techniques df
        if relationship["relationship_type"] == "subtechnique-of": 
            continue

        # filter out relationships not with relatedType
        if relatedType:
            related = False
            for stixTerm in attackToStixTerm[relatedType]: # try all stix types for the ATT&CK type
               if source["type"] == stixTerm or target["type"] == stixTerm: # if any stix type is part of the relationship
                   related = True
                   break;
            if not related: continue # skip this relationship if the types don't match

        # add mapping data
        row = {}
        def add_side(label, sdo):
            """add data for one side of the mapping"""
            if "external_references" in sdo and sdo["external_references"][0]["source_name"] in ["mitre-attack", "mitre-mobile-attack"]:
                row[f"{label} ID"] = sdo["external_references"][0]["external_id"] # "source ID" or "target ID"
            if "name" in sdo:
                row[f"{label} name"] = sdo["name"] # "source name" or "target name"
            row[f"{label} type"] = stixToAttackTerm[sdo["type"]] # "source type" or "target type"
        
        add_side("source", source)
        row["mapping type"] = relationship["relationship_type"]
        add_side("target", target)
        if "description" in relationship:
            row["mapping description"] = relationship["description"]
        
        used_relationships.append(relationship) # track relationships that were not filtered
        relationship_rows.append(row)
    
    citations = get_citations(relationships)
    relationships = pd.DataFrame(relationship_rows).sort_values(["mapping type", "source type", "target type", "source name", "target name"])
    if not relatedType:
        dataframes = {
            "relationships": relationships,
        }
        if not citations.empty:
            dataframes["citations"] = citations.sort_values("reference")
        
        return dataframes
    else: # break into dataframes by mapping type
        dataframes = {}

        # group:software / "associated {other type}"
        relatedGroupSoftware = relationships.query("`mapping type` == 'uses' and (`source type` == 'group' or `source type` == 'software') and (`target type` == 'group' or `target type` == 'software')")
        if not relatedGroupSoftware.empty:
            dataframes[f"associated {'software' if relatedType == 'group' else 'groups'}"] = relatedGroupSoftware

        # technique:group + technique:software / "procedure examples"
        procedureExamples = relationships.query("`mapping type` == 'uses' and `target type` == 'technique'")
        if not procedureExamples.empty:
            dataframes["procedure examples"] = procedureExamples

        # technique:mitigation / "mitigation mappings"
        relatedMitigations = relationships.query("`mapping type` == 'mitigates'")
        if not relatedMitigations.empty:
            dataframes['associated mitigations' if relatedType == 'technique' else 'techniques addressed'] = relatedMitigations
        
        if not citations.empty:
            dataframes["citations"] = citations.sort_values("reference")

        return dataframes
