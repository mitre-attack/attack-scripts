import json
from layers.objects.exceptions import UninitializedLayer, BadType, BadInput, \
    handler
from layers.objects.layerobj import LayerObj


class Layer:
    def __init__(self, init_dict={}, strict=True):
        """
             Initialization - create a new Layer object
             :param init_dict: Optionally provide base Layer json or string
                data on initialization
         """
        self.__layer = None
        self.strict = strict
        self.load_input(init_dict)

    @property
    def layer(self):
        if self.__layer is not None:
            return self.__layer
        return "No Layer Loaded Yet!"

    def load_input(self, init_dict):
        """
            loads input from a string or dictionary format
            :param init_dit: the string or dictionary representing the layer
                data to be loaded
        """
        if isinstance(init_dict, str):
            self.data = json.loads(init_dict)
        else:
            self.data = init_dict
        if self.data != {}:
            self.build()

    def load_file(self, filename):
        """
             loads input from a layer file specified by filename
             :param filename: the target filename to load from
        """
        with open(filename, 'r') as fio:
            raw = fio.read()
            self.data = json.load(raw)
            self.build()

    def export_file(self, filename):
        """
            saves the current state of the layer to a layer file specified by
                filename
            :param filename: the target filename to save as
        """
        if self.__layer is not None:
            with open(filename, 'w') as fio:
                json.dump(self.__layer.get_dict(), fio)
        else:
            raise UninitializedLayer

    def build(self):
        """
            Loads the data stored in self.data into a LayerObj (self.layer)
        """
        try:
            self.__layer = LayerObj(self.data['version'], self.data['name'],
                                    self.data['domain'])
        except BadType or BadInput as e:
            handler(type(self).__name__, 'Layer is malformed: {}. '
                                         'Unable to load.'.format(e))
            self.__layer = None
            return
        except KeyError as e:
            handler(type(self).__name__, 'Layer is missing parameters: {}. '
                                         'Unable to load.'.format(e))
            self.__layer = None
            return

        for key in self.data:
            if key not in ['version', 'name', 'domain']:
                try:
                    self.__layer._linker(key, self.data[key])
                except Exception as e:
                    if self.strict:
                        handler(type(self).__name__, "{} error. "
                                                     "Unable to load."
                                .format(str(e.__class__.__name__)))
                        self.__layer = None
                        return

    def get_dict(self):
        """
            Converts the currently loaded layer file into a dict
            :returns: A dict representation of the current layer object
        """
        if self.__layer is not None:
            return self.__layer.get_dict()
