import os
from stix2 import TAXIICollectionSource, Filter, FileSystemSource
from taxii2client import Server, Collection

class MatrixEntry:
    def __init__(self, id=None, name=None):
        if id is not None:
            self.id = id
        if name is not None:
            self.name = name

    @property
    def id(self):
        if self.__id is not None:
            return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def name(self):
        if self.__name is not None:
            return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

class MatrixGen:
    convert = {
             'initial-access': 'Initial Access',
             'execution': 'Execution',
             'persistence': 'Persistence',
             'privilege-escalation': 'Privilege Escalation',
             'defense-evasion': 'Defense Evasion',
             'credential-access': 'Credential Access',
             'discovery': 'Discovery',
             'lateral-movement': 'Lateral Movement',
             'collection': 'Collection',
             'command-and-control': 'Command and Control',
             'exfiltration': 'Exfiltration',
             'impact': 'Impact'
        }
    t_lookup = {'Initial Access': 'TA0001',
                'Execution': 'TA0002',
                'Persistence': 'TA0003',
                'Privilege Escalation': 'TA0004',
                'Defense Evasion': 'TA0005',
                'Credential Access': 'TA0006',
                'Discovery': 'TA0007',
                'Lateral Movement': 'TA0008',
                'Collection': 'TA0009',
                'Command and Control': 'TA0011',
                'Exfiltration': 'TA0010',
                'Impact': 'TA0040'}
    def __init__(self, fresh=True):
        """
            Initialization - Creates a matrix generator object

            :param fresh: Bool for whether or not to read from the cti-taxii server (server currently has no
                            subtechniques)
        """
        if fresh:
            self.server = Server('https://cti-taxii.mitre.org/taxii')
            self.api_root = self.server.api_roots[0]
            self.collections = dict()

            for collection in self.api_root.collections:
                if collection.title != "PRE-ATT&CK":
                    tc = Collection('https://cti-taxii.mitre.org/stix/collections/' + collection.id)
                    self.collections[collection.title.split(' ')[0].lower()] = TAXIICollectionSource(tc)
        else:
            self.collections = dict()
            path = os.path.sep.join(__file__.split(os.path.sep)[:-1])
            self.collections['enterprise'] = FileSystemSource(os.path.sep.join([path, 'raw_stix', 'enterprise-attack']))
            self.collections['mobile'] = FileSystemSource(os.path.sep.join([path, 'raw_stix', 'mobile-attack']))

    def _get_tactic_listing(self, mode='enterprise'):
        """
            INTERNAL - retrieves tactics for the associated mode

            :param mode: The domain to draw from
        """
        tactics = {}
        t_filt = []
        matrix = self.collections[mode].query([Filter('type', '=', 'x-mitre-matrix')])
        for i in range(len(matrix)):
            tactics[matrix[i]['name']] = []
            for tactic_id in matrix[i]['tactic_refs']:
                tactics[matrix[i]['name']].append(self.collections[mode].query([Filter('id', '=', tactic_id)])[0])
        for entry in tactics[matrix[0]['name']]:
            t_filt.append(entry['name'])
        return t_filt

    def _get_technique_listing(self, tactic, mode='enterprise'):
        """
            INTERNAL - retrieves techniques for a given tactic and domain

            :param tactic: The tactic to grab techniques from
            :param mode: The domain to draw from
        """
        techniques = []
        subtechs = {}
        techs = self.collections[mode].query([Filter('type', '=', 'attack-pattern'), Filter('kill_chain_phases.phase_name', '=', tactic)])
        for entry in techs:
            if entry['kill_chain_phases'][0]['kill_chain_name'] == 'mitre-attack':
                tid = [t['external_id'] for t in entry['external_references'] if t['source_name'] == 'mitre-attack']
                if '.' not in tid[0]:
                    techniques.append(MatrixEntry(id=tid[0], name=entry['name']))
                else:
                    parent = tid[0].split('.')[0]
                    if parent not in subtechs:
                        subtechs[parent] = []
                    subtechs[parent].append(MatrixEntry(id=tid[0], name=entry['name']))
        return techniques, subtechs

    @staticmethod
    def _construct_panop(codex, subtechs, excludes):
        """
            INTERNAL - Creates a list of lists template for the matrix layout

            :param codex: A list of lists matrix (output of .build_matrix())
            :param subtechs: A list of subtechniques that will be visible
            :param excludes: A list of techniques that will be excluded
        """
        st = [x[0] for x in subtechs]
        s_tacs = [x[1] for x in subtechs]
        et = [x[0] for x in excludes]
        e_tacs = [x[1] for x in excludes]

        matrix_obj = {}
        column = 0
        cycle = False
        to_add = []
        stechs = []
        joins = []
        for col in codex:
            # each column of the matrix
            column += 1
            if cycle:
                for entry in to_add:
                    sr = entry[0]
                    joins.append([entry[0], column-1, len(stechs[entry[1]])])
                    for element in stechs[entry[1]]:
                        matrix_obj[(sr, column)] = element.name
                        sr += 1
                cycle = False
                column += 1
            row = 2
            matrix_obj[(1, column)] = col[0].name
            c_name = col[0].name
            stechs = col[1]['subtechs']
            to_add = []
            for element in col[2:]:
                elname = element.name
                tid = element.id
                skip = False
                for entry in range(0, len(et)):
                    if et[entry] == tid and (e_tacs[entry] == False or MatrixGen.convert[e_tacs[entry]] == c_name):
                        skip = True
                        break
                if not skip:
                    matrix_obj[(row, column)] = elname
                    sat = False
                    for entry in range(0, len(st)):
                        if st[entry] == tid and (s_tacs[entry] == False or MatrixGen.convert[s_tacs[entry]] == c_name):
                            # this tech has enabled subtechs
                            to_add.append((row, tid))
                            row += len(stechs[tid])
                            cycle = True
                            sat = True
                            break
                    if not sat:
                        row += 1
        return matrix_obj, joins

    @staticmethod
    def _get_ID(codex, name):
        """
            INTERNAL - Do lookups to retrieve the ID of a technique given it's name

            :param codex: The list of lists matrix object (output of build_matrix)
            :param name: The name of the technique to retrieve the ID of
            :return: The ID of the technique referenced by name
        """
        for col in codex:
            for elm in col:
                if col.index(elm) == 1:
                    for sp in elm['subtechs']:
                        for t in elm['subtechs'][sp]:
                            if t.name == name:
                                return t.id
                else:
                    if elm.name == name:
                        return elm.id
        return ''

    @staticmethod
    def _get_name(codex, id):
        """
            INTERNAL - Do lookups to retrieve the name of a technique given it's ID

            :param codex: The list of lists matrix object (output of build_matrix)
            :param id: The ID of the technique to retrieve the name of
            :return: The name of the technique referenced by id
        """
        for col in codex:
            for elm in col:
                if col.index(elm) == 1:
                    for sp in elm['subtechs']:
                        for t in elm['subtechs'][sp]:
                            if t.id == id:
                                return t.name
                else:
                    if elm.id == id:
                        return elm.name
        return ''

    def build_matrix(self, mode='enterprise'):
        """
            Build a ATT&CK matrix object, as a list of lists containing technique dictionaries

            :param mode: The domain to build a matrix for
        """
        matrix = []
        tacs = self._get_tactic_listing(mode)
        for tac in tacs:
            techs, subtechs = self._get_technique_listing(tac.lower().replace(' ', '-'), mode)
            colm = [MatrixEntry(id=self.t_lookup[tac], name=tac)]
            stemp = {}
            # sort subtechniques via id, append to column
            for par in subtechs:
                subtechs[par].sort(key=lambda x: x.name)
                stemp[par] = subtechs[par]
            colm.append({'subtechs':stemp})
            # sort techniques alphabetically, append to column
            techs.sort(key=lambda x: x.name)
            colm.extend(techs)
            matrix.append(colm)
        return matrix
