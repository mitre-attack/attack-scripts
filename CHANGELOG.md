# Changes staged on develop
## Fixes
- Fixed a bug in diff_stix where sub-techniques had the wrong URL in hyperlinks.

# V1.4.1 - 18 May 2020
## New Scripts
- New script [technique_mappings_to_csv.py](technique_mappings_to_csv.py) added to support mapping Techniques with Mitigations, Groups or Software. The output is a CSV file. Added in PR [#23](https://github.com/mitre-attack/attack-scripts/pull/23)
## Improvements
- Updated [diff_stix.py](scripts/diff_stix.py) with sub-techniques support. See issue [#12](https://github.com/mitre-attack/attack-scripts/issues/12).
## Fixes
- Fixed bug in LayerOps causing issues with cross-tactic techniques, as well as a bug where a score lambda could affect the outcome of other lambdas.

# V1.4 - 5 May 2020
## New Scripts
- Added Layers folder with utility scripts for working with [ATT&CK Navigator](https://github.com/mitre-attack/attack-navigator) Layers. See the Layers [README](layers/README.md) for more details. See issues [#2](https://github.com/mitre-attack/attack-scripts/issues/2) and [#3](https://github.com/mitre-attack/attack-scripts/issues/3).

# V1.3 - 8 January 2019
## New Scripts
- Added [diff_stix.py](scripts/diff_stix.py).

# V1.2 - 24 October 2019
- Added ATT&CKcon 2.0 Detection Training. See [the readme](/trainings/detection-training/README.md) for details.

# V1.1 - 29 March 2019
## New Scripts
- Added [techniques_from_data_source.py](scripts/techniques_from_data_source.py).

# V1.0 - 1 March 2019
## New Scripts
- Added [techniques_data_sources_vis.py](scripts/techniques_data_sources_vis.py).
