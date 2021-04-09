# attack-scripts

This repository contains standalone scripts and utilities for working with ATT&CK.
- the [scripts](scripts) folder contains one-off scripts for processing and visualizing ATT&CK content.
- the [scripts/layers/samples](scripts/layers/samples) folder contains one-off scripts demonstrating the generation of ATT&CK Navigator layers from ATT&CK data. The outputs of these scripts can also be found on the [ATT&CK Navigator repository](https://github.com/mitre-attack/attack-navigator/tree/master/layers/data/samples).

See also our [mitreattack-python](https://github.com/mitre-attack/mitreattack-python/) pip module for more python tools!

## Requirements
- [python3](https://www.python.org/)

## Installation
1. Create virtual environment:
    - macOS and Linux: `python3 -m venv env`
    - Windows: `py -m venv env`
2. Activate the virtual environment:
    - macOS and Linux: `source env/bin/activate`
    - Windows: `env/Scripts/activate.bat`
3. Install requirements into the virtual environment: `pip3 install -r requirements.txt`

### taxii2client compatibility
A recent update to the `taxii2client` python library changed the API for TAXII 2.0 requests. This repository has been updated to work with the latest version of taxii2client, however if your installed version is < 2.0.0 you may need to patch the scripts for them to run properly. Please see our [USAGE document on MITRE/CTI](https://github.com/mitre/cti/blob/master/USAGE.md#taxii2client) for more information.

## Related MITRE Work
#### CTI
[Cyber Threat Intelligence repository](https://github.com/mitre/cti) of the ATT&CK catalog expressed in STIX 2.0 JSON. This repository also contains [our USAGE document](https://github.com/mitre/cti/blob/master/USAGE.md) which includes additional examples of accessing and parsing our dataset in Python.

#### ATT&CK
ATT&CK® is a curated knowledge base and model for cyber adversary behavior, reflecting the various phases of an adversary’s lifecycle and the platforms they are known to target. ATT&CK is useful for understanding security risk against known adversary behavior, for planning security improvements, and verifying defenses work as expected.

https://attack.mitre.org

#### STIX
Structured Threat Information Expression (STIX<sup>™</sup>) is a language and serialization format used to exchange cyber threat intelligence (CTI).

STIX enables organizations to share CTI with one another in a consistent and machine readable manner, allowing security communities to better understand what computer-based attacks they are most likely to see and to anticipate and/or respond to those attacks faster and more effectively.

STIX is designed to improve many different capabilities, such as collaborative threat analysis, automated threat exchange, automated detection and response, and more.

https://oasis-open.github.io/cti-documentation/

## Notice

Copyright 2020 The MITRE Corporation

Approved for Public Release; Distribution Unlimited. Case Number 19-0486.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

This project makes use of ATT&CK®

[ATT&CK Terms of Use](https://attack.mitre.org/resources/terms-of-use/)
