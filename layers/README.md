# layers

This folder contains modules and scripts for working with ATT&CK layers. The core module allows users to load, validate, process, and save ATT&CK layers. A brief overview of the components can be found below. All scripts adhere to the MITRE ATT&CK Navigator Layer file format, [version 3.0](https://github.com/mitre-attack/attack-navigator/blob/develop/layers/LAYERFORMATv3.md).

| script | description |
|:-------|:------------|
| [exceptions.py](core/exceptions.py) | Implements errors and supporting functions for the core module. |
| [filter.py](core/filter.py) | Implements a basic filter object. |
| [gradient.py](core/gradient.py) | Implements a basic gradient object. |
| [layer.py](core/layer.py) | Provides an interface for interacting with core module's layer representation. A further breakdown can be found in the corresponding section below. |
| [layerobj.py](core/layerobj.py) | Implements a basic layer object. This should not be manipulated directly, instead, use the [layer representation](core/layer.py). |
| [layout.py](core/layout.py) | Implements a basic layout object. |
| [legenditem.py](core/legenditem.py) | Implements a basic legenditem object. |
| [metadata.py](core/metadata.py) | Implements a basic metadata object. |
| [technique.py](core/technique.py) | Implements a basic technique object. |
| [layerops.py](manipulators/layerops.py) | Provides a means by which to combine multiple ATT&CK layer objects in customized ways. A further breakdown can be found in the corresponding section below. |

## layer.py
Layer.py provides a Layer class, which is the interface used to interact with the rest of the core module, and provides an abstract representation of an ATT&CK layer. The layer class has a collection of methods, the functionality of which is documented in the table below. An example of how to interface with the class to load and retrieve layer objects is documented following that.

| method | description |
|:-------|:------------|
| Layer().load_input(_input_) | Loads an ATT&CK layer from either a dictionary or a string representation of a dictionary. |
| Layer().load_file(_input_) | Loads an ATT&CK layer from a file location specified by the _input_. |
| Layer().export_file(_input_) | Saves the current state of the loaded ATT&CK layer to a json file denoted by the _input_. |
| Layer().get_dict() | Returns a representation of the current ATT&CK layer object as a dictionary. | 

#### Example Usage

```python
example_layer_dict = {
    "name": "example layer",
    "version": "3.0",
    "domain": "mitre-enterprise",
    "description": "hello, world",
    ...
    }
example_layer_location = "/path/to/layer/file.json"
example_layer_out_location = "/path/to/new/layer/file.json"

from layers.core.layer import Layer

layer1 = Layer(example_layer_dict)
layer1.export_file(example_layer_out_location)

layer2 = Layer()
layer2.load_input(example_layer_dict)
layer2.get_dict()

layer3 = Layer()
layer3.load_file(example_layer_location)
```

## layerops.py
Layerops.py provides the LayerOps class, which is a way to combine layer files in an automated way, using user defined lambda functions. Each LayerOps instance, when created, ingests the provided lambda functions, and stores them for use. An existing LayerOps class can be used to combine layer files according to the initialized lambda using the process method. The breakdown of this two step process is documented in the table below, while examples of both the list and dictionary modes of operation can be found below.

| method | description |
|:-------|:------------|
| LayerOps(score=_score_, comment=_comment_, enabled=_enabled_, colors=_colors_, metadata=_metadata_, name=_name_, desc=_desc_, default_values=_default_values_) | Each of the _inputs_ takes a lambda function that will be used to combine technique object fields matching the parameter. The one exception to this is _default_values_, which is an optional dictionary argument containing default values to provide the lambda functions if elements of the combined layers are missing them. |
| LayerOps.process(_data_, defaults=_defaults_) | Applies the lambda functions stored during initialization to the layer objects in _data_. _data_ must be either a list or a dictionary of Layer objects, and is expected to match the format of the lambda equations provided during initialization. |

#### Example Usage
```python
from layers.manipulators.layerops import LayerOps
from layers.core.layer import Layer

demo = Layer()
demo.load_file("C:\Users\attack\Downloads\layer.json")
demo2 = Layer()
demo2.load_input({"name": "example layer", ... })

lo = LayerOps(score=lambda x: x[0] * x[1], 
              name=lambda x: x[1], 
              desc=lambda x: "This is an list example")
out_layer = lo.process([demo, demo2])
out_layer.export_file("C:\demo_layer1.json")

lo2 = LayerOps(score=lambda x: x['a'], 
               color=lambda x: x['b'], 
               desc=lambda x: "This is a dict example")
out_layer2 = lo2.process({'a': demo, 'b': demo2})
dict_layer = out_layer2.get_dict()
print(dict_layer)
out_layer2.export_file("C:\demo_layer2.json")
```