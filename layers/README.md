# layers

This folder contains modules and scripts for working with ATT&CK Navigator layers. "ATT&CK Navigator Layers are a set of annotations overlayed on top of the ATT&CK Matrix. For more about ATT&CK Navigator layers, visit the ATT&CK Navigator repository. The core module allows users to load, validate, manipulate, and save ATT&CK layers. A brief overview of the components can be found below. All scripts adhere to the MITRE ATT&CK Navigator Layer file format, [version 3.0](https://github.com/mitre-attack/attack-navigator/blob/develop/layers/LAYERFORMATv3.md).

#### Core Modules
| script | description |
|:-------|:------------|
| [filter](core/filter.py) | Implements a basic [filter object](https://github.com/mitre-attack/attack-navigator/blob/develop/layers/LAYERFORMATv3.md#filter-object-properties). |
| [gradient](core/gradient.py) | Implements a basic [gradient object](https://github.com/mitre-attack/attack-navigator/blob/develop/layers/LAYERFORMATv3.md#gradient-object-properties). |
| [layer](core/layer.py) | Provides an interface for interacting with core module's layer representation. A further breakdown can be found in the corresponding section below. |
| [layout](core/layout.py) | Implements a basic [layout object](https://github.com/mitre-attack/attack-navigator/blob/develop/layers/LAYERFORMATv3.md#layout-object-properties). |
| [legenditem](core/legenditem.py) | Implements a basic [legenditem object](https://github.com/mitre-attack/attack-navigator/blob/develop/layers/LAYERFORMATv3.md#legenditem-object-properties). |
| [metadata](core/metadata.py) | Implements a basic [metadata object](https://github.com/mitre-attack/attack-navigator/blob/develop/layers/LAYERFORMATv3.md#metadata-object-properties). |
| [technique](core/technique.py) | Implements a basic [technique object](https://github.com/mitre-attack/attack-navigator/blob/develop/layers/LAYERFORMATv3.md#technique-object-properties). |

#### Manipulator Scripts
| script | description |
|:-------|:------------|
| [layerops](manipulators/layerops.py) | Provides a means by which to combine multiple ATT&CK layer objects in customized ways. A further breakdown can be found in the corresponding section below. |

## Layer
The Layer class provides format validation and read/write capabilities to aid in working with ATT&CK Navigator Layers in python. It is the primary interface through which other Layer-related classes defined in the core module should be used. The Layer class API and a usage example are below.

| method [x = Layer()]| description |
|:-------|:------------|
| x.from_str(_input_) | Loads an ATT&CK layer from either a string representation of a dictionary. |
| x.from_dict(_input_) | Loads an ATT&CK layer from either a dictionary. |
| x.from_file(_input_) | Loads an ATT&CK layer from a file location specified by the _input_. |
| x.to_file(_input_) | Saves the current state of the loaded ATT&CK layer to a json file denoted by the _input_. |
| x.to_dict() | Returns a representation of the current ATT&CK layer object as a dictionary. |
| x.to_str() | Returns a representation of the current ATT&CK layer object as a string representation of a dictionary. | 

#### Example Usage

```python
example_layer_dict = {
    "name": "example layer",
    "version": "3.0",
    "domain": "mitre-enterprise"
}

example_layer_location = "/path/to/layer/file.json"
example_layer_out_location = "/path/to/new/layer/file.json"

from layers.core import Layer

layer1 = Layer(example_layer_dict)              # Create a new layer and load existing data
layer1.to_file(example_layer_out_location)  # Write out the loaded layer to the specified file

layer2 = Layer()                                # Create a new layer object
layer2.from_dict(example_layer_dict)           # Load layer data into existing layer object
print(layer2.to_dict())                        # Retrieve the loaded layer's data as a dictionary, and print it

layer3 = Layer()                                # Create a new layer object
layer3.from_file(example_layer_location)        # Load layer data from a file into existing layer object
```

## layerops.py
Layerops.py provides the LayerOps class, which is a way to combine layer files in an automated way, using user defined lambda functions. Each LayerOps instance, when created, ingests the provided lambda functions, and stores them for use. An existing LayerOps class can be used to combine layer files according to the initialized lambda using the process method. The breakdown of this two step process is documented in the table below, while examples of both the list and dictionary modes of operation can be found below.

##### LayerOps()
```python
 x = LayerOps(score=score, comment=comment, enabled=enabled, colors=colors, metadata=metadata, name=name, desc=desc, default_values=default_values)
```
 
 Each of the _inputs_ takes a lambda function that will be used to combine technique object fields matching the parameter. The one exception to this is _default_values_, which is an optional dictionary argument containing default values to provide the lambda functions if techniques of the combined layers are missing them.

##### .process() Method
```python
x.process(data, default_values=default_values)
```
The process method applies the lambda functions stored during initialization to the layer objects in _data_. _data_ must be either a list or a dictionary of Layer objects, and is expected to match the format of the lambda equations provided during initialization. default_values is an optional dictionary argument that overrides the currently stored default
 values with new ones for this specific processing operation.

#### Example Usage
```python
from layers.manipulators.layerops import LayerOps
from layers.core.layer import Layer

demo = Layer()
demo.from_file("C:\Users\attack\Downloads\layer.json")
demo2 = Layer()
demo2.from_file("C:\Users\attack\Downloads\layer2.json")
demo3 = Layer()
demo3.from_file("C:\Users\attack\Downloads\layer3.json")

# Example 1) Build a LayerOps object that takes a list and averages scores across the layers
lo = LayerOps(score=lambda x: sum(x) / len(x), 
              name=lambda x: x[1], 
              desc=lambda x: "This is an list example")     # Build LayerOps object
out_layer = lo.process([demo, demo2])                       # Trigger processing on a list of demo and demo2 layers
out_layer.to_file("C:\demo_layer1.json")                    # Save averaged layer to file
out_layer2 = lo.process([demo, demo2, demo3])               # Trigger processing on a list of demo, demo2, demo3
visual_aid = out_layer2.to_dict()                           # Retrieve dictionary representation of processed layer

# Example 2) Build a LayerOps object that takes a dictionary and averages scores across the layers
lo2 = LayerOps(score=lambda x: sum([x[y] for y in x]) / len([x[y] for y in x]), 
               color=lambda x: x['b'], 
               desc=lambda x: "This is a dict example")      # Build LayerOps object, with lambda
out_layer3 = lo2.process({'a': demo, 'b': demo2})            # Trigger processing on a dictionary of demo and demo2
dict_layer = out_layer3.to_dict()                            # Retrieve dictionary representation of processed layer
print(dict_layer)                                            # Display retrieved dictionary
out_layer4 = lo2.process({'a': demo, 'b': demo2, 'c': demo3})# Trigger processing on a dictionary of demo, demo2, demo3
out_layer4.to_file("C:\demo_layer4.json")                    # Save averaged layer to file

# Example 3) Build a LayerOps object that takes a single element dictionary and inverts the score
lo3 = LayerOps(score=lambda x: 100 - x['a'],
               desc= lambda x: "This is a simple example")  # Build LayerOps object to invert score (0-100 scale)
out_layer5 = lo3.process({'a': demo})                       # Trigger processing on dictionary of demo
print(out_layer5.to_dict())                                 # Display processed layer in dictionary form
out_layer5.to_file("C:\demo_layer5.json")                   # Save inverted score layer to file

# Example 4) Build a LayerOps object that combines the comments from elements in the list, with custom defaults
lo4 = LayerOps(score=lambda x: '; '.join(x),
               default_values= {
                "comment": "This was an example of new default values"
                },
               desc= lambda x: "This is a defaults example")  # Build LayerOps object to combine descriptions, defaults
out_layer6 = lo4.process([demo2, demo3])                      # Trigger processing on a list of demo2 and demo0
out_layer6.to_file("C:\demo_layer6.json")                     # Save combined comment layer to file
```
