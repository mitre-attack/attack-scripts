import argparse
import csv
import io

from stix2 import TAXIICollectionSource, MemorySource, Filter
from taxii2client.v20 import Collection

import tqdm


def build_taxii_source(collection_name):
    """Downloads latest Enterprise or Mobile ATT&CK content from MITRE TAXII Server."""
    # Establish TAXII2 Collection instance for Enterprise ATT&CK collection
    collection_map = {
        "enterprise_attack": "95ecc380-afe9-11e4-9b6c-751b66dd541e",
        "mobile_attack": "2f669986-b40b-4423-b720-4396ca6a462b"
    }
    collection_url = "https://cti-taxii.mitre.org/stix/collections/" + collection_map[collection_name] + "/"
    collection = Collection(collection_url)
    taxii_ds = TAXIICollectionSource(collection)

    # Create an in-memory source (to prevent multiple web requests)
    return MemorySource(stix_data=taxii_ds.query())


def get_all_techniques(src, source_name):
    """Filters data source by attack-pattern which extracts all ATT&CK Techniques"""
    filters = [
        Filter("type", "=", "attack-pattern"),
        Filter("external_references.source_name", "=", source_name),
    ]
    results = src.query(filters)
    return remove_deprecated(results)


def filter_for_term_relationships(src, relationship_type, object_id, target=True):
    """Filters data source by type, relationship_type and source or target"""
    filters = [
        Filter("type", "=", "relationship"),
        Filter("relationship_type", "=", relationship_type),
    ]
    if target:
        filters.append(Filter("target_ref", "=", object_id))
    else:
        filters.append(Filter("source_ref", "=", object_id))

    results = src.query(filters)
    return remove_deprecated(results)


def filter_by_type_and_id(src, object_type, object_id, source_name):
    """Filters data source by id and type"""
    filters = [
        Filter("type", "=", object_type),
        Filter("id", "=", object_id),
        Filter("external_references.source_name", "=", source_name),
    ]
    results = src.query(filters)
    return remove_deprecated(results)


def grab_external_id(stix_object, source_name):
    """Grab external id from STIX2 object"""
    for external_reference in stix_object.get("external_references", []):
        if external_reference.get("source_name") == source_name:
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
    parser = argparse.ArgumentParser(description="Fetches the current ATT&CK content expressed as STIX2 and creates spreadsheet mapping Techniques with Mitigations, Groups or Software.")
    parser.add_argument("-d", "--domain", type=str, required=True, choices=["enterprise_attack", "mobile_attack"], help="Which ATT&CK domain to use (Enterprise, Mobile).")
    parser.add_argument("-m", "--mapping-type", type=str, required=True, choices=["groups", "mitigations", "software"], help="Which type of object to output mappings for using ATT&CK content.")
    parser.add_argument("-s", "--save", type=str, required=False, help="Save the CSV file with a different filename.")
    return parser


def do_mapping(ds, fieldnames, relationship_type, type_filter, source_name, sorting_keys):
    """Main logic to map techniques to mitigations, groups or software"""
    all_attack_patterns = get_all_techniques(ds, source_name)
    writable_results = []

    for attack_pattern in tqdm.tqdm(all_attack_patterns, desc="parsing data for techniques"):
        # Grabs relationships for identified techniques
        relationships = filter_for_term_relationships(ds, relationship_type, attack_pattern.id)

        for relationship in relationships:
            # Groups are defined in STIX as intrusion-set objects
            # Mitigations are defined in STIX as course-of-action objects
            # Software are defined in STIX as malware objects
            stix_results = filter_by_type_and_id(ds, type_filter, relationship.source_ref, source_name)

            if stix_results:
                row_data = (
                    grab_external_id(attack_pattern, source_name),
                    attack_pattern.name,
                    grab_external_id(stix_results[0], source_name),
                    stix_results[0].name,
                    escape_chars(stix_results[0].description),
                    escape_chars(relationship.description),
                )

                writable_results.append(dict(zip(fieldnames, row_data)))

    return sorted(writable_results, key=lambda x: (x[sorting_keys[0]], x[sorting_keys[1]]))


def main(args):
    data_source = build_taxii_source(args.domain)
    op = args.mapping_type

    source_map = {
        "enterprise_attack": "mitre-attack",
        "mobile_attack": "mitre-mobile-attack",
    }
    source_name = source_map[args.domain]

    if op == "groups":
        filename = args.save or "groups.csv"
        fieldnames = ("TID", "Technique Name", "GID", "Group Name", "Group Description", "Usage")
        relationship_type = "uses"
        type_filter = "intrusion-set"
        sorting_keys = ("TID", "GID")
        rowdicts = do_mapping(data_source, fieldnames, relationship_type, type_filter, source_name, sorting_keys)
    elif op == "mitigations":
        filename = args.save or "mitigations.csv"
        fieldnames = ("TID", "Technique Name", "MID", "Mitigation Name", "Mitigation Description", "Application")
        relationship_type = "mitigates"
        type_filter = "course-of-action"
        sorting_keys = ("TID", "MID")
        rowdicts = do_mapping(data_source, fieldnames, relationship_type, type_filter, source_name, sorting_keys)
    elif op == "software":
        filename = args.save or "software.csv"
        fieldnames = ("TID", "Technique Name", "SID", "Software Name", "Software Description", "Use")
        relationship_type = "uses"
        type_filter = "malware"
        sorting_keys = ("TID", "SID")
        rowdicts = do_mapping(data_source, fieldnames, relationship_type, type_filter, source_name, sorting_keys)
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
