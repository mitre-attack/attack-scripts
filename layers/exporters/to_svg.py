import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import drawSvg as draw

try:
    from core import Layer
    from exporters.svg_templates import SvgTemplates
except ModuleNotFoundError:
    from ..core import Layer
    from ..exporters.svg_templates import SvgTemplates

class NoLayer(Exception):
    pass

class ToSvg:
    def __init__(self, domain='enterprise', source='taxii', local=None):
        """
            Sets up exporting system, builds underlying matrix

            :param server: Whether or not to use live cti-taxii data to construct the matrix
            :param local: Optional path to local stix data

        """
        self.raw_handle = SvgTemplates(domain=domain, source=source, local=local)

    def to_svg(self, layer, output='example.svg'):
        if layer is not None:
            if not isinstance(layer, Layer):
                raise TypeError

        if layer is None:
            raise NoLayer

        included_subs = []
        if layer.layer.techniques:
            for entry in layer.layer.techniques:
                if entry.showSubtechniques:
                    if entry.tactic:
                        included_subs.append((entry.techniqueID, entry.tactic))
                    else:
                        included_subs.append((entry.techniqueID, False))

        excluded = []
        if layer.layer.hideDisabled:
            for entry in layer.layer.techniques:
                if entry.enabled == False:
                    if entry.tactic:
                        excluded.append((entry.techniqueID, entry.tactic))
                    else:
                        excluded.append((entry.techniqueID, False))
        scores = []
        colors = []
        if layer.layer.techniques:
            for entry in layer.layer.techniques:
                if entry.score:
                    if entry.tactic:
                        scores.append((entry.techniqueID, entry.tactic, entry.score))
                    else:
                        scores.append((entry.techniqueID, False, entry.score))
                elif entry.color:
                    if entry.tactic:
                        colors.append((entry.techniqueID, entry.tactic, entry.color))
                    else:
                        colors.append((entry.techniqueID, False, entry.color))
        sName = True
        sID = False
        sort = 0
        if layer.layer.layout:
            sName = layer.layer.layout.showName
            sID = layer.layer.layout.showID
        if layer.layer.sorting:
            sort = layer.layer.sorting
        g = self.raw_handle.export(showName=sName, showID=sID, sort=sort, scores=scores,
                                   subtechs=included_subs, colors=colors,
                                   exclude=excluded, lhandle=layer.layer)
        d = self.raw_handle._build_headers(layer.layer.name, layer.layer.description, layer.layer.filters,
                                           layer.layer.gradient)
        d.append(g)

        d.saveSvg(output)
