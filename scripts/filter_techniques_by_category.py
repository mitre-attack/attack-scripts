import argparse
import csv
import io

import stix2
import taxii2client


def build_taxii_source(collection_name):
    """Downloads latest Enterprise ATT&CK content from GitHub."""
    # Establish TAXII2 Collection instance for Enterprise ATT&CK collection
    collection_map = {
        "enterprise_attack": "95ecc380-afe9-11e4-9b6c-751b66dd541e",
        "mobile_attack": "2f669986-b40b-4423-b720-4396ca6a462b"
    }
    collection_url = "https://cti-taxii.mitre.org/stix/collections/" + collection_map[collection_name] + "/"
    collection = taxii2client.Collection(collection_url)
    taxii_ds = stix2.TAXIICollectionSource(collection)

    # Create an in-memory source (to prevent multiple web requests)
    return stix2.MemorySource(stix_data=taxii_ds.query())


def get_all_techniques(src):
    """Filters data source by attack-pattern which extracts all ATT&CK Techniques"""
    filters = [
        stix2.Filter('type', '=', 'attack-pattern'),
        stix2.Filter('external_references.source_name', '=', 'mitre-attack'),
    ]
    results = src.query(filters)
    return remove_deprecated(results)


def filter_for_term_relationships(src, relationship_type, object_id, source=True):
    """Filters data source by relationship that matches type and source or target"""
    filters = [
        stix2.Filter("type", "=", "relationship"),
        stix2.Filter("relationship_type", "=", relationship_type),
    ]
    if source:
        filters.append(stix2.Filter("source_ref", "=", object_id))
    else:
        filters.append(stix2.Filter("target_ref", "=", object_id))

    results = src.query(filters)
    return remove_deprecated(results)


def filter_by_type_and_id(src, object_type, object_id):
    """Filters data source by id and type"""
    filters = [
        stix2.Filter("type", "=", object_type),
        stix2.Filter("id", "=", object_id),
    ]
    results = src.query(filters)
    return remove_deprecated(results)


def grab_external_id(stix_object):
    """Grab external id from STIX2 object"""
    for external_reference in stix_object.get("external_references", []):
        if external_reference.get("source_name") == "mitre-attack":
            return external_reference["external_id"]


def remove_deprecated(stix_objects):
    """Will remove any revoked or deprecated objects from queries made to the data source"""
    # Note we use .get() because the property may not be present in the JSON data. The default is False
    # if the property is not set.
    return list(
        filter(
            lambda x: x.get("x_mitre_deprecated", False) is False and x.get("revoked", False) is False,
            stix_objects
        )
    )


def escape_chars(a_string):
    """Some characters create problems when written to file"""
    return a_string.translate(str.maketrans({
        "\n": r"\\n",
    }))


def arg_parse():
    """Function to handle script arguments."""
    parser = argparse.ArgumentParser(description="Fetches the current ATT&CK content expressed as STIX2 and creates spreadsheet matching Techniques with Mitigations or Groups.")
    parser.add_argument("-c", "--collection", type=str, required=True, choices=["enterprise_attack", "mobile_attack"], help="Which collection to use (Enterprise, Mobile).")
    parser.add_argument("-o", "--operation", type=str, required=True, choices=["groups", "mitigations"], help="Operation to perform on ATT&CK content.")
    parser.add_argument("-s", "--save", type=str, required=False, help="Save the CSV file with a different filename.")
    return parser


def do_groups(ds):
    """Main logic to match techniques to groups"""
    all_attack_patterns = get_all_techniques(ds)
    writable_results = []

    for attack_pattern in all_attack_patterns:
        tid = grab_external_id(attack_pattern)

        # Grabs uses relationships for identified techniques
        relationships = filter_for_term_relationships(ds, "uses", attack_pattern.id, source=False)

        for relationship in relationships:
            # Groups are defined in STIX as intrusion-set objects
            groups = filter_by_type_and_id(ds, "intrusion-set", relationship.source_ref)

            if groups:
                group = groups[0]
                gid = grab_external_id(group)
                writable_results.append(
                    {
                        "TID": tid,
                        "Technique Name": attack_pattern.name,
                        "GID": gid,
                        "Group Name": group.name,
                        "Group Description": group.description,
                        "Usage": relationship.description
                    }
                )
    return sorted(writable_results, key=lambda x: (x["TID"], x["GID"]))


def do_mitigations(ds):
    """Main logic to match techniques to mitigations"""
    all_attack_patterns = get_all_techniques(ds)
    writable_results = []

    for attack_pattern in all_attack_patterns:
        tid = grab_external_id(attack_pattern)

        # Grabs mitigation relationships for identified techniques
        relationships = filter_for_term_relationships(ds, "mitigates", attack_pattern.id, source=False)

        for relationship in relationships:
            # Mitigations are defined in STIX as course-of-action objects
            mitigation = filter_by_type_and_id(ds, "course-of-action", relationship.source_ref)

            if mitigation:
                mitigation = mitigation[0]
                mid = grab_external_id(mitigation)
                writable_results.append(
                    {
                        "TID": tid,
                        "Technique Name": attack_pattern.name,
                        "MID": mid,
                        "Mitigation Name": mitigation.name,
                        "Mitigation Description": escape_chars(mitigation.description),
                        "Application": escape_chars(relationship.description),
                    }
                )
    return sorted(writable_results, key=lambda x: (x["TID"], x["MID"]))


def main(args):
    data_source = build_taxii_source(args.collection)
    op = args.operation

    if op == "groups":
        filename = args.save or "groups.csv"
        fieldnames = ["TID", "Technique Name", "GID", "Group Name", "Group Description", "Usage"]
        rowdicts = do_groups(data_source)
    elif op == "mitigations":
        filename = args.save or "mitigations.csv"
        fieldnames = ["TID", "Technique Name", "MID", "Mitigation Name", "Mitigation Description", "Application"]
        rowdicts = do_mitigations(data_source)
    else:
        raise RuntimeError("Unknown option: %s" % op)

    with io.open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rowdicts)


if __name__ == "__main__":
    parser = arg_parse()
    args = parser.parse_args()
    main(args)
