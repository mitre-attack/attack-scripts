import os
from stix2 import TAXIICollectionSource, Filter, FileSystemSource
from taxii2client import Server, Collection


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
        techniques = {}
        subtechs = {}
        techs = self.collections[mode].query([Filter('type', '=', 'attack-pattern'), Filter('kill_chain_phases.phase_name', '=', tactic)])
        for entry in techs:
            if entry['kill_chain_phases'][0]['kill_chain_name'] == 'mitre-attack':
                tid = [t['external_id'] for t in entry['external_references'] if t['source_name'] == 'mitre-attack']
                if '.' not in tid[0]:
                    techniques[entry['name']] = tid[0]
                else:
                    parent = tid[0].split('.')[0]
                    if parent not in subtechs:
                        subtechs[parent] = []
                    subtechs[parent].append({entry['name']: tid[0]})
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
                        matrix_obj[(sr, column)] = [x for x in element.keys()][0]
                        sr += 1
                cycle = False
                column += 1
            row = 2
            matrix_obj[(1, column)] = col[0]['tactic']
            c_name = col[0]['tactic']
            stechs = col[1]['subtechs']
            to_add = []
            for element in col[2:]:
                elname = [x for x in element.keys()][0]
                tid = element[[x for x in element.keys()][0]]
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

    def build_matrix(self, mode='enterprise'):
        """
            Build a ATT&CK matrix object, as a list of lists containing technique dictionaries

            :param mode: The domain to build a matrix for
        """
        matrix = []
        tacs = self._get_tactic_listing(mode)
        for tac in tacs:
            techs, subtechs = self._get_technique_listing(tac.lower().replace(' ', '-'), mode)
            colm = [dict(tactic=tac)]
            temp = []
            stemp = {}
            # sort subtechniques via id, append to column
            for par in subtechs:
                stemp[par] = []
                temp = []
                for entry in subtechs[par]:
                    for obj in entry:
                        temp.append(entry[obj])
                for entry in sorted(temp):
                    obj = {}
                    for k in subtechs[par]:
                        for j in k:
                            if k[j] == entry:
                                obj[j] = entry
                    stemp[par].append(obj)
            colm.append({'subtechs':stemp})
            temp = []
            # sort techniques alphabetically, append to column
            for entry in techs:
                temp.append(entry)
            for entry in sorted(temp):
                colm.append({entry:techs[entry]})
            matrix.append(colm)
        return matrix
