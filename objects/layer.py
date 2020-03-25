import json

class Layer:
    """
        Initialization - create a new Layer object
        :param init_dict: Optionally provide base Layer json or string data on initialization
    """
    def __init__(self, init_dict={}):
        self.load_input(init_dict)

    """
        loads input from a string or dictionary format
        :param init_dit: the string or dictionary representing the layer data to be loaded
    """
    def load_input(self, init_dict):
        if isinstance(init_dict, str):
            self.data = json.loads(init_dict)
        else:
            self.data = init_dict

    """ 
        loads input from a layer file specified by filename
        :param filename: the target filename to load from
    """
    def load_file(self, filename):
        with open(filename, 'r') as fio:
            raw = fio.read()
            self.data = json.load(raw)

    """ 
        saves the current state of the layer to a layer file specified by filename
        :param filename: the target filename to save as
    """
    def export_file(self, filename):
        with open(filename, 'w') as fio:
            json.dump(self.data, fio)

    """ 
        INTERNAL - modify an element of the layer referenced by key to be value
        :param key: the element to modify
        :param value: the element's new value
    """
    def _edit(self, key, value):
        self.data[key] = value

    """
        INTERNAL - get the current value of an element in the layer data referenced by key
        :param key: the element to retrieve the value of 
    """
    def _get(self, key):
        return self.data[key]

    """
        INTERNAL - get a list of all known elements in the current layer data
    """
    def _enumerate(self):
        return [x for x in self.data.keys()]

    """
        INTERNAL - print out the entire layer data for debug purposes
    """
    def _dump(self):
        print(self.data)