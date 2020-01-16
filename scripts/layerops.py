import copy

class InvalidFormat(Exception):
    pass

class BadLambda(Exception):
    pass

class layerops:
    def __init__(self, data):
        if isinstance(data, dict):
            temp = {}
            for entry in data.keys():
                temp[entry] = data[entry]['techniques']
            self.mode = 'dict'
        elif isinstance(data, list):
            temp = []
            for entry in data:
                temp.append(entry['techniques'])
            self.mode = 'list'
        else:
            raise InvalidFormat
        self.data = data
        self.da = temp
        self.corpus = self._build_template(temp)
        self.out ={
	        "name": "layer",
	        "version": "2.2",
	        "domain": "mitre-enterprise",
	        "description": "",
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
	        "viewMode": 0,
	        "hideDisabled": False,
            "gradient": {
                "colors": [
                    "#ff6666",
                    "#ffe766",
                    "#8ec843"
                ],
                "minValue": 0,
                "maxValue": 100
            },
            "legendItems": [],
            "metadata": [],
            "showTacticRowBackground": False,
            "tacticRowBackground": "#dddddd",
            "selectTechniquesAcrossTactics": True
        }
        self.default_values = {
            "comment": "",
            "enabled": True,
            "color": "#ffffff",
            "score": 1,
            "metadata": []
        }

    def process(self, score=None, comment=None, enabled=None, colors=None, metadata=None, defaults=None):
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
        print(processed)
        return processed

    def _build_template(self, data):
        if self.mode == 'list':
            return self._template(data)
        elif self.mode == 'dict':
            return self._template(data.values())

    def _template(self, data):
        temp = []
        for entry in data:
            temp.append([{"techniqueID": x['techniqueID'], "tactic": x['tactic']} for x in entry])
        return list({v['techniqueID']:v for v in [elm for list in temp for elm in list]}.values())

    def _grabList(self, search, collection):
        temp = []
        for x in collection:
            temp.append(self._grabElement(search, x))
        return temp

    def _grabDict(self, search, collection):
        temp = {}
        for key in collection:
            temp[key] = self._grabElement(search, collection[key])
        return temp

    def _grabElement(self, search, listing):
        val = [x for x in listing if self._inDict(search, x)]
        if len(val) > 0:
            return val[0]
        return {}

    def _inDict(self, search, complete):
        comp_list = complete.items()
        search_terms = search.items()
        return all(elm in comp_list for elm in search_terms)

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