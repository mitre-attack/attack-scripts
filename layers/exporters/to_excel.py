from openpyxl.comments import Comment
from openpyxl.styles import PatternFill, Font

try:
    from core import Layer
    from exporters import ExcelTemplates
except ModuleNotFoundError:
    from ..core import Layer
    from ..exporters import ExcelTemplates


class NotALayerError(Exception):
    pass

class NoLayer(Exception):
    pass

class ToExcel:
    def __init__(self, layer=None):
        """
            Initialization - Creates a ToExcel object

            :param layer: A layer to initialize the instance with
        """
        if layer is not None:
            if not isinstance(layer, Layer):
                raise NotALayerError
        self.__layer = layer

    @property
    def layer(self):
        if self.__layer is not None:
            return self.__layer

    @layer.setter
    def layer(self, layer):
        if not isinstance(layer, Layer):
            raise NotALayerError
        self.__layer = layer

    def to_file(self, filepath="layer.xlsx", fresh=False):
        """
            Exports a layer file to the excel format as the file specified

            :param filepath: The location to write the excel file to
            :param fresh: Whether or not to use live cti-taxii data to construct the matrix
        """
        if self.__layer is None:
            raise NoLayer

        raw_handle = ExcelTemplates(mode=self.layer.layer.domain, fresh=fresh)

        included_subs = []
        if self.layer.layer.techniques:
            for entry in self.layer.layer.techniques:
                if entry.showSubtechniques:
                    if entry.tactic:
                        included_subs.append((entry.techniqueID, entry.tactic))
                    else:
                        included_subs.append((entry.techniqueID, False))

        excluded = []
        if self.layer.layer.hideDisabled:
            for entry in self.layer.layer.techniques:
                if entry.enabled == False:
                    if entry.tactic:
                        excluded.append((entry.techniqueID, entry.tactic))
                    else:
                        excluded.append((entry.techniqueID, False))

        sName = True
        sID = False
        if self.layer.layer.layout:
            sName = self.layer.layer.layout.showName
            sID = self.layer.layer.layout.showID
        raw_template = raw_handle.export(showName=sName, showID=sID, subtechs=included_subs, exclude=excluded)
        sheet_obj = raw_template.active
        sheet_obj.title = self.layer.layer.name
        for tech in self.layer.layer.techniques:
            p_tactic = None
            if tech.tactic:
                p_tactic = tech.tactic
            coords = raw_handle.retrieve_coords(tech.techniqueID, p_tactic)
            if coords == []:
                tac = p_tactic
                if tac == None:
                    tac = "(none)"
                print('WARNING! Technique/Tactic ' + tech.techniqueID + '/' + tac +
                      ' does not appear to exist in the loaded matrix. Skipping...')
            for location in coords:
                cell = sheet_obj.cell(row=location[0],column=location[1])

                if tech.comment:
                    cell.comment = Comment(tech.comment, 'ATT&CK Scripts Exporter')

                if tech.enabled == False:
                    if self.layer.layer.hideDisabled:
                        pass
                    else:
                        grayed_out = Font(color='909090')
                        cell.font = grayed_out
                        continue
                if tech.color:
                    c_color = PatternFill(fill_type='solid', start_color=tech.color.upper()[1:])
                    cell.fill = c_color
                    continue
                if tech.score:
                    if self.layer.layer.gradient:
                        comp_color = self.layer.layer.gradient.compute_color(tech.score)
                        c_color = PatternFill(fill_type='solid', start_color=comp_color.upper()[1:])
                        cell.fill = c_color

        raw_template.save(filepath)
