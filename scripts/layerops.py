# Example Use:
# from objects.layer import Layer

# demo = Layer()
# demo.load_file("C:\Users\attack\Downloads\layer.json")
# demo2 = Layer()
# demo2.load_input(Existing_Layer_String_Previously_Loaded)

# lo = layerops([demo, demo2])
# lo.process(score=lambda x: x[0] * x[1], out_Name="example 1", out_Desc="This is an list example")
# out_layer = lo.get_processed()
# out_layer.export_file("C:\demo_layer1.json")

# lo2 = layerops({'a': demo, 'b': demo2})
# lo2.process(score=lambda x: x['a'], color=lambda x: x['b'], out_Desc="This is a dict example")
# lo2.edit_meta(name="example 2")
# out_layer2 = lo2.get_processed()
# out_layer2.export_file("C:\demo_layer2.json")

import copy
from objects.layer import Layer

class InvalidFormat(Exception):
    pass

class BadLambda(Exception):
    pass

class MismatchedDomain(Exception):
    pass

class layerops:
    """
        Initialization - takes a list or dict of Layer objects, and prepares to process them

        :param data: A dict or list of Layer objects.
        :raises InvalidFormat: An error indicating that a the layer data wasn't provided in a list or dict
    """
    def __init__(self, data):
        self.data = data
        if isinstance(data, dict):
            temp = {}
            for entry in data.keys():
                temp[entry] = data[entry]._get('techniques')
            self.mode = 'dict'
            self._merge_to_template(key=list(data.keys())[0])
        elif isinstance(data, list):
            temp = []
            for entry in data:
                temp.append(entry._get('techniques'))
            self.mode = 'list'
            self._merge_to_template()
        else:
            raise InvalidFormat
        self.da = temp
        self.corpus = self._build_template(temp)

        # Default values for fields if they aren't supplied
        self.default_values = {
            "comment": "",
            "enabled": True,
            "color": "#ffffff",
            "score": 1,
            "metadata": []
        }
        self.processed = None

    """
        Processes the ingested data using User provided Lambdas
        :param score: lambda to calculate score
        :param comment: lambda to generate comments
        :param enabled: lambda to determine enabled status
        :param metadata: lambda to generate metadata
        :param defaults: dictionary containing desired default values for missing data element values
        :param out_Name: new name to apply to the resulting layer
        :param out_Desc: new description to apply to the resulting layer
    """
    def process(self, score=None, comment=None, enabled=None, colors=None, metadata=None, defaults=None,
                out_Name=None, out_Desc=None):
        composite = copy.deepcopy(self.corpus)
        if score != None:
            for entry in composite:
                entry['score'] = self._applyOperation(self.da, entry, 'score', score, defaults)

        if comment != None:
            for entry in composite:
                entry['comment'] = self._applyOperation(self.da, entry, 'comment', comment, defaults)

        if enabled != None:
            for entry in composite:
                entry['enabled'] = self._applyOperation(self.da, entry, 'enabled', enabled, defaults)

        if colors != None:
            for entry in composite:
                entry['color'] = self._applyOperation(self.da, entry, 'color', colors, defaults)

        if metadata != None:
            for entry in composite:
                entry['metadata'] = self._applyOperation(self.da, entry, 'metadata', metadata, defaults)

        processed = copy.deepcopy(self.out)
        processed['techniques'] = composite
        if out_Name != None:
            processed['name'] = out_Name
        if out_Desc != None:
            processed['description'] = out_Desc
        self.processed = Layer(processed)

    """
        Retrieve processed results
        :returns: A Layer object representing the processing changes
    """
    def get_processed(self):
        if self.processed is not None:
            return self.processed
        else:
            print('Please call the Process method to combine loaded layers.')

    """
        Edits name and description metadata on a processed layer
        :param name: the new name to use
        :param desc: the new description to use
    """
    def edit_meta(self, name=None, desc=None):
        if name is not None:
            if self.processed is not None:
                self.processed._edit('name', name)
        if desc is not None:
            if self.processed is not None:
                self.processed._edit('description', desc)

    """
        INTERNAL: merges initial layer files in either dict or list form into a single template. Defaults to the first
            entry in the case of difference in metadata.
        :param key: the key referencing the first entry to default to
        :raises MismatchedDomain: An error indicating that the layers came from different domains
    """
    def _merge_to_template(self, key=0):
        self.out = {}
        dict_map = []
        collide = []
        if self.mode == 'dict':
            for x in self.data.keys():
                dict_map.append(x)
                collide.append(self.data[x])
        else:
            for x in self.data:
                collide.append(x)
        key_space = self.data[key]._enumerate()
        for entry in key_space:
            if entry != 'techniques':
                standard = collide[0]._get(entry)
                if any(y != standard for y in [x._get(entry) for x in collide]):
                    if entry == 'domain':
                        print('FATAL ERROR! Layer mis-match on domain. Exiting.')
                        raise MismatchedDomain
                    print('Warning! Layer mis-match detected for {}. Defaulting to {}\'s value'.format(entry, key))
                self.out[entry] = standard

    """
        INTERNAL: builds a base template by combining available technique listings from each layer
        :param data: the raw ingested technique data (list or dict)
    """
    def _build_template(self, data):
        if self.mode == 'list':
            return self._template(data)
        elif self.mode == 'dict':
            temp = {}
            t2 = []
            for key in data:
                temp[key] = self._template([data[key]])
            for key in temp:
                for elm in temp[key]:
                    if not any (elm['techniqueID'] == x['techniqueID'] for x in t2):
                        t2.append(elm)
                    else:
                         [x.update(elm) if x['techniqueID'] == elm['techniqueID'] else x for x in t2]
            return t2

    """
        INTERNAL: creates a template technique entry for a given listing of techniques
        :param data: a single layer's technique data
        :returns: a list of technique templates
    """
    def _template(self, data):
        temp = []
        for entry in data:
            temp.append([{"techniqueID": x['techniqueID'], "tactic": x['tactic']} if 'tactic' in x else {
                          "techniqueID": x['techniqueID']} for x in entry])
        return list({v['techniqueID']:v for v in [elm for list in temp for elm in list]}.values())

    """
        INTERNAL: generates a list containing all values for a given key across the collection
        :param search: the key to search for 
        :param collection: the data collection to search
        :returns: a list of values for that key across the collection
    """
    def _grabList(self, search, collection):
        temp = []
        for x in collection:
            temp.append(self._grabElement(search, x))
        return temp

    """
        INTERNAL: generates a dictionary containing all values for a given key across the collection
        :param search: the key to search for
        :param collection: the data collection to search
        :returns: a dict of values for that key across the collection
    """
    def _grabDict(self, search, collection):
        temp = {}
        for key in collection:
            temp[key] = self._grabElement(search, collection[key])
        return temp

    """ 
        INTERNAL: returns a matching element in the listing for the search key
        :param search: the key to search for
        :param listing: the data element to search
        :returns: the found value, or an empty dict
    """
    def _grabElement(self, search, listing):
        val = [x for x in listing if self._inDict(search, x)]
        if len(val) > 0:
            return val[0]
        return {}

    """
        INTERNAL: returns bool of whether or not the key searched for can be found across the dataset corpus
        :param search: the key to search for 
        :param complete: the data set to search for
        :returns: true/false
    """
    def _inDict(self, search, complete):
        comp_list = complete.items()
        search_terms = search.items()
        return all(elm in comp_list for elm in search_terms)

    """
        INTERNAL: applies a lambda expression to the dataset
        :param corpus: the dataset
        :param element: the template file to fill out
        :param name: the name of the field being processed
        :param lda: the lambda expression to apply
        :param defaults: any default values should the field not be found in a dataset entry
        :raises BadLambda: error denoting that an error has occurred when running the lambda function 
        :returns: lambda output
    """
    def _applyOperation(self, corpus, element, name, lda, defaults):
        if self.mode == 'list':
            listing = self._grabList(element, corpus)
            values = []
            for x in listing:
                if name in x:
                    values.append(x[name])
                else:
                    if defaults is not None:
                        if name in defaults:
                            values.append(defaults[name])
                            continue
                    values.append(self.default_values[name])
        else:
            listing = self._grabDict(element, corpus)
            values = {}
            for elm in listing:
                if name in listing[elm]:
                    values[elm] = listing[elm][name]
                else:
                    if defaults is not None:
                        if name in defaults:
                            values[elm] = defaults[name]
                            continue
                    values[elm] = self.default_values[name]
        try:
            return lda(values)
        except IndexError and KeyError:
            print('Unable to continue, lambda targeting "{}" could not operate correctly on {}. Maybe the field is missing?'.format(name, element))
            print('[RAW] Extracted matching elements: {}'.format(listing))
            raise BadLambda

test = Layer()
test2 = Layer()
test3 = Layer()
temp = """
{
	"name": "test layer name",
	"version": "3.0",
	"domain": "mitre-enterprise",
	"description": "test layer description which has some additional words and is quite long",
	"filters": {
		"stages": [
			"act"
		],
		"platforms": [
			"Windows",
			"Linux",
			"macOS"
		]
	},
	"sorting": 0,
	"layout": {
		"layout": "side",
		"showID": false,
		"showName": true
	},
	"hideDisabled": false,
	"techniques": [
		{
			"techniqueID": "T1015",
			"tactic": "persistence",
			"color": "#756bb1",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1015",
			"tactic": "privilege-escalation",
			"color": "#756bb1",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1138",
			"tactic": "persistence",
			"color": "",
			"comment": "comment",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1138",
			"tactic": "privilege-escalation",
			"color": "#778833",
			"comment": "comment",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1197",
			"tactic": "defense-evasion",
			"score": 3,
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1197",
			"tactic": "persistence",
			"score": 3,
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1088",
			"tactic": "defense-evasion",
			"score": 25,
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1088",
			"tactic": "privilege-escalation",
			"score": 25,
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1191",
			"tactic": "defense-evasion",
			"score": 44,
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1191",
			"tactic": "execution",
			"score": 44,
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1116",
			"tactic": "defense-evasion",
			"score": 123,
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1059",
			"tactic": "execution",
			"score": 2,
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1109",
			"tactic": "defense-evasion",
			"score": 16,
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1109",
			"tactic": "persistence",
			"score": 16,
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1122",
			"tactic": "defense-evasion",
			"color": "#ffaabb",
			"comment": "test comment 3",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1122",
			"tactic": "persistence",
			"color": "",
			"comment": "test comment 3",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1503",
			"tactic": "credential-access",
			"score": 18,
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1140",
			"tactic": "defense-evasion",
			"score": 8,
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1482",
			"tactic": "discovery",
			"color": "#bcbddc",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1157",
			"tactic": "persistence",
			"score": 61,
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1157",
			"tactic": "privilege-escalation",
			"score": 61,
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1212",
			"tactic": "credential-access",
			"color": "",
			"comment": "comment another one",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1083",
			"tactic": "discovery",
			"color": "",
			"comment": "",
			"enabled": false,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1046",
			"tactic": "discovery",
			"color": "",
			"comment": "",
			"enabled": false,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1201",
			"tactic": "discovery",
			"color": "#636363",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1552",
			"tactic": "credential-access",
			"color": "",
			"comment": "",
			"enabled": true,
			"metadata": [],
			"showSubtechniques": true
		},
		{
			"techniqueID": "T1552.001",
			"tactic": "credential-access",
			"color": "",
			"comment": "",
			"enabled": false,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1552.002",
			"tactic": "credential-access",
			"color": "",
			"comment": "",
			"enabled": false,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1552.004",
			"tactic": "credential-access",
			"color": "",
			"comment": "",
			"enabled": false,
			"metadata": [],
			"showSubtechniques": false
		},
		{
			"techniqueID": "T1552.006",
			"tactic": "credential-access",
			"color": "",
			"comment": "",
			"enabled": false,
			"metadata": [],
			"showSubtechniques": false
		}
	],
	"gradient": {
		"colors": [
			"#ff6666",
			"#ffe766",
			"#8ec843"
		],
		"minValue": 0,
		"maxValue": 100
	},
	"legendItems": [
        {
            "label": "legend1",
            "color": "#d396f7"
        },
        {
            "label": "longer legend",
            "color": "#9ccce2"
        },
        {
            "label": "legend3",
            "color": "#62c487"
        }
    ],
	"metadata": [],
	"showTacticRowBackground": false,
	"tacticRowBackground": "#4400ff",
	"selectTechniquesAcrossTactics": false,
	"selectSubtechniquesWithParent": false
}
"""

temp2 = """
{
    "name": "example layer",
    "version": "3.0",
    "domain": "mitre-enterprise",
    "description": "hello, world",
    "filters": {
        "stages": [
            "act"
        ],
        "platforms": [
            "Windows",
            "macOS"
        ]
    },
    "sorting": 2,
    "layout": {
        "layout": "side",
        "showName": true,
        "showID": false
    },
    "hideDisabled": false,
    "techniques": [
        {
            "techniqueID": "T1110",
            "color": "#fd8d3c",
            "comment": "This is a comment for technique T1110",
            "showSubtechniques": true
        },
        {
            "techniqueID": "T1110.001",
            "comment": "This is a comment for T1110.001 - the first subtechnique of technique T1110.001"
        },
        {
            "techniqueID": "T1134",
            "tactic": "defense-evasion",
            "score": 75,
            "comment": "this is a comment for T1134 which is only applied on the defense-evasion tactic"
        },
        {
            "techniqueID": "T1078",
            "tactic": "discovery",
            "enabled": false
        },
        {
            "techniqueID": "T1053",
            "tactic": "privilege-escalation",
            "metadata": [
                { 
                    "name": "T1053 metadata1", 
                    "value": "T1053 metadata1 value" 
                },
                { 
                    "name": "T1053 metadata2", 
                    "value": "T1053 metadata2 value" 
                }
            ]
        }
    ],
    "gradient": {
        "colors": [
            "#ff6666",
            "#ffe766",
            "#8ec843"
        ],
        "minValue": 0,
        "maxValue": 100
    },
    "legendItems": [
        {
            "label": "Legend Item Label",
            "color": "#FF00FF"
        }
    ],
    "showTacticRowBackground": true,
    "tacticRowBackground": "#dddddd",
    "selectTechniquesAcrossTactics": false,
    "selectSubtechniquesWithParent": false,
    "metadata": [
        { 
            "name": "layer metadata 1", 
            "value": "layer metadata 1 value" 
        },
        { 
            "name": "layer metadata 2", 
            "value": "layer metadata 2 value" 
        }
    ]
}
"""


test.load_input(temp)
test2.load_input(temp2)

t1 = layerops([test, test2])
t1.process(score=lambda x: x[0] * x[1])
t1.get_processed()._dump()