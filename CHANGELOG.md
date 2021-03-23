# v1.9.0 - 23 March 2021
## Fixes
- Fixed a bug in the layer library where layers could be imported improperly in specific contexts.

# v1.8.1 - 3 March 2021
## Fixes
- Layer library should no longer throw errors when it encounters the "Network" and "PRE" platforms.
- Layer library should no longer throw errors if it encounters a layer with a version number higher than it expects.
- Setting `showSubtechniques` to true on a technique should no longer cause a crash when exporting the layer to SVG.

# v1.8 - 15 December 2020
## Improvements
- Updated Layer library to support ATT&CK Navigator Layer format version 4.1. 

# v1.7 - 27 October 2020
## Improvements
- Removed pre-ATT&CK domain from scripts to support migration of that content to enterprise tactics. See issue [#36](https://github.com/mitre-attack/attack-scripts/issues/36).
- Updated scripts which produce layers to use v4.0 of the Navigator Layer Format. See issue [#47](https://github.com/mitre-attack/attack-scripts/issues/47).

# v1.6 - 5 October 2020
## Improvements
- Added [layer to SVG](https://github.com/mitre-attack/attack-scripts/tree/master/layers#to_svgpy) converter. See issue [#1](https://github.com/mitre-attack/attack-scripts/issues/1).
- Added option to filter mappings by tactic in [technique_mappings_to_csv](technique_mappings_to_csv.py). See pull request [#46](https://github.com/mitre-attack/attack-scripts/pull/46).

# v1.5.2 - 2 September 2020
## Improvements
- Clarified documentation on creation of virtual environments for Windows compatibility.
- Added section to install docs about taxii2client compatibility. See issue [#19](https://github.com/mitre-attack/attack-scripts/issues/19).
- Standardized import style to better follow the standard set in [MITRE/CTI#103](https://github.com/mitre/cti/pull/103).

# v1.5.1 - 27 July 2020
## New Scripts
- Added [layer to excel](https://github.com/mitre-attack/attack-scripts/tree/master/layers#to_excelpy) converter. See issue [#25](https://github.com/mitre-attack/attack-scripts/issues/25).
## Improvements
- Updated README to better describe repo contents.
- Removed outdated detection training. See issue [#37](https://github.com/mitre-attack/attack-scripts/issues/37).

# v1.5 - 8 July 2020
## New Scripts
Added scripts used to generate the [sample layers in the ATT&CK Navigator repository](https://github.com/mitre-attack/attack-navigator/tree/develop/layers/data/samples). See issue [#21](https://github.com/mitre-attack/attack-scripts/issues/21) and [the sample layer README](scripts/layers/samples/README.md) for more details. The following scripts were added:
- [heatmap.py](scripts/layers/samples/heatmap.py)
- [bear_APT.py](scripts/layers/samples/bear_APT.py)
- [apt3_apt29_software.py](scripts/layers/samples/apt3_apt29_software.py)
- [software_execution.py](scripts/layers/samples/software_execution.py)
## Fixes
- Fixed a bug in diff_stix where sub-techniques had the wrong URL in hyperlinks.

# v1.4.1 - 18 May 2020
## New Scripts
- New script [technique_mappings_to_csv.py](technique_mappings_to_csv.py) added to support mapping Techniques with Mitigations, Groups or Software. The output is a CSV file. Added in PR [#23](https://github.com/mitre-attack/attack-scripts/pull/23)
## Improvements
- Updated [diff_stix.py](scripts/diff_stix.py) with sub-techniques support. See issue [#12](https://github.com/mitre-attack/attack-scripts/issues/12).
## Fixes
- Fixed bug in LayerOps causing issues with cross-tactic techniques, as well as a bug where a score lambda could affect the outcome of other lambdas.

# V1.4 - 5 May 2020
## New Scripts
- Added Layers folder with utility scripts for working with [ATT&CK Navigator](https://github.com/mitre-attack/attack-navigator) Layers. See the Layers [README](layers/README.md) for more details. See issues [#2](https://github.com/mitre-attack/attack-scripts/issues/2) and [#3](https://github.com/mitre-attack/attack-scripts/issues/3).

# v1.3 - 8 January 2019
## New Scripts
- Added [diff_stix.py](scripts/diff_stix.py).

# v1.2 - 24 October 2019
- Added ATT&CKcon 2.0 Detection Training. See [the readme](/trainings/detection-training/README.md) for details.

# v1.1 - 29 March 2019
## New Scripts
- Added [techniques_from_data_source.py](scripts/techniques_from_data_source.py).

# v1.0 - 1 March 2019
## New Scripts
- Added [techniques_data_sources_vis.py](scripts/techniques_data_sources_vis.py).
