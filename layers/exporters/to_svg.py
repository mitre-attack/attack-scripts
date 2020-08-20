import json

try:
    from core import Layer
    from exporters.svg_templates import SvgTemplates
except ModuleNotFoundError:
    from ..core import Layer
    from ..exporters.svg_templates import SvgTemplates

class NoLayer(Exception):
    pass


class SVGConfig:
    def __init__(self, width=8.5, height=11, headerHeight=1, unit="in", showSubtechniques="expanded",
                 font="sans-serif", tableBorderColor="#6B7279", showHeader=True, legendDocked=True,
                 legendX=0, legendY=0, legendWidth=2, legendHeight=1, showLegend=True, showFilters=True,
                 showAbout=True, border=0.104):
        """
            Define parameters to configure SVG export

            :param width: Desired SVG width
            :param height: Desired SVG height
            :param headerHeight: Desired Header Block height
            :param unit: SVG measurement units (qualifies width, height, etc.)
            :param showSubtechniques: Display form for subtechniques - "all", "expanded" (decided by layer), or "none"
            :param font: What font style to use - "sans", "sans-serif", or "monospace"
            :param tableBorderColor: Hex color to use for the technique borders
            :param showHeader: Whether or not to show Header Blocks
            :param legendDocked: Whether or not the legend should be docked
            :param legendX: Where to place the legend on the x axis if not docked
            :param legendY: Where to place the legend on the y axis if not docked
            :param legendWidth: Width of the legend if not docked
            :param legendHeight: Height of the legend if not docked
            :param showLegend: Whether or not to show the legend
            :param showFilters: Whether or not to show the Filter Header Block
            :param showAbout: Whether or not to show the About Header Block
            :param border: What default border width to use
        """
        self.width = width
        self.height = height
        self.headerHeight = headerHeight
        self.unit = unit
        self.showSubtechniques = showSubtechniques
        self.font = font
        self.tableBorderColor = tableBorderColor
        self.showHeader = showHeader
        self.legendDocked = legendDocked
        self.legendX = legendX
        self.legendY = legendY
        self.legendWidth = legendWidth
        self.legendHeight = legendHeight
        self.showLegend = showLegend
        self.showFilters = showFilters
        self.showAbout = showAbout
        self.border = border

    def load_from_file(self, filename=""):
        """
            Load config from a json file

            :param filename: The file to read from
        """
        with open(filename, 'r') as fio:
            raw = fio.read()
            self._data = json.loads(raw)
        for entry in self._data:
            if entry in vars(self).keys():
                setattr(self, entry, self._data[entry])
            else:
                print('WARNING - Unidentified Config Field in {}: {}'.format(filename, entry))

        self._display()

    def save_to_file(self, filename=""):
        """
            Store config to json file

            :param filename: The file to write to
        """
        out = dict(width=self.width, height=self.height, headerHeight=self.headerHeight, unit=self.unit,
                   showSubtechniques=self.showSubtechniques, font=self.font, tableBorderColor=self.tableBorderColor,
                   showHeader=self.showHeader, legendDocked=self.legendDocked, legendX=self.legendX,
                   legendY=self.legendY, legendWidth=self.legendWidth, legendHeight=self.legendHeight,
                   showLegend=self.showLegend, showFilters=self.showFilters, showAbout=self.showAbout,
                   border=self.border)
        with open(filename, 'w') as file:
            json.dump(out, file)

    def _display(self):
        """
            INTERNAL - display current configuration
        """
        print("SVGConfig current settings: ")
        print("width - {}".format(self.width))
        print("height - {}".format(self.height))
        print("headerHeight - {}".format(self.headerHeight))
        print("unit - {}".format(self.unit))
        print("showSubtechniques - {}".format(self.showSubtechniques))
        print("font - {}".format(self.font))
        print("tableBorderColor - {}".format(self.tableBorderColor))
        print("showHeader - {}".format(self.showHeader))
        print("legendDocked - {}".format(self.legendDocked))
        print("legendX - {}".format(self.legendX))
        print("legendY - {}".format(self.legendY))
        print("legendWidth - {}".format(self.legendWidth))
        print("legendHeight - {}".format(self.legendHeight))
        print("showLegend - {}".format(self.showLegend))
        print("showFilters - {}".format(self.showFilters))
        print("showAbout - {}".format(self.showAbout))
        print("border - {}".format(self.border))

    @property
    def width(self):
        if self.__width is not None:
            return self.__width

    @width.setter
    def width(self, width):
        if isinstance(width, int) or isinstance(width, float):
            self.__width = width

    @property
    def height(self):
        if self.__height is not None:
            return self.__height

    @height.setter
    def height(self, height):
        if isinstance(height, int) or isinstance(height, float):
            self.__height = height

    @property
    def headerHeight(self):
        if self.__headerHeight is not None:
            return self.__headerHeight

    @headerHeight.setter
    def headerHeight(self, headerHeight):
        if isinstance(headerHeight, int) or isinstance(headerHeight, float):
            self.__headerHeight = headerHeight

    @property
    def unit(self):
        if self.__unit is not None:
            return self.__unit

    @unit.setter
    def unit(self, unit):
        if unit in ['in', 'cm', 'px', 'em', 'pt']:
            self.__unit = unit

    @property
    def showSubtechniques(self):
        if self.__showSubtechniques is not None:
            return self.__showSubtechniques

    @showSubtechniques.setter
    def showSubtechniques(self, showSubtechniques):
        if showSubtechniques in ["expanded", "all", "none"]:
            self.__showSubtechniques = showSubtechniques

    @property
    def font(self):
        if self.__font is not None:
            return self.__font

    @font.setter
    def font(self, font):
        if font in ["serif", "sans-serif", "monospace"]:
            self.__font = font

    @property
    def tableBorderColor(self):
        if self.__tableBorderColor is not None:
            return self.__tableBorderColor

    @tableBorderColor.setter
    def tableBorderColor(self, tableBorderColor):
        if isinstance(tableBorderColor, str) and tableBorderColor.startswith('#') and len(tableBorderColor) == 7:
            self.__tableBorderColor = tableBorderColor

    @property
    def showHeader(self):
        if self.__showHeader is not None:
            return self.__showHeader

    @showHeader.setter
    def showHeader(self, showHeader):
        if isinstance(showHeader, bool):
            self.__showHeader = showHeader

    @property
    def legendDocked(self):
        if self.__legendDocked is not None:
            return self.__legendDocked

    @legendDocked.setter
    def legendDocked(self, legendDocked):
        if isinstance(legendDocked, bool):
            self.__legendDocked = legendDocked

    @property
    def legendX(self):
        if self.__legendX is not None:
            return self.__legendX

    @legendX.setter
    def legendX(self, legendX):
        if isinstance(legendX, int) or isinstance(legendX, float):
            self.__legendX = legendX

    @property
    def legendY(self):
        if self.__legendY is not None:
            return self.__legendY

    @legendY.setter
    def legendY(self, legendY):
        if isinstance(legendY, int) or isinstance(legendY, float):
            self.__legendY = legendY

    @property
    def legendWidth(self):
        if self.__legendWidth is not None:
            return self.__legendWidth

    @legendWidth.setter
    def legendWidth(self, legendWidth):
        if isinstance(legendWidth, int) or isinstance(legendWidth, float):
            self.__legendWidth = legendWidth

    @property
    def legendHeight(self):
        if self.__legendHeight is not None:
            return self.__legendHeight

    @legendHeight.setter
    def legendHeight(self, legendHeight):
        if isinstance(legendHeight, int) or isinstance(legendHeight, float):
            self.__legendHeight = legendHeight

    @property
    def showLegend(self):
        if self.__showLegend is not None:
            return self.__showLegend

    @showLegend.setter
    def showLegend(self, showLegend):
        if isinstance(showLegend, bool):
            self.__showLegend = showLegend

    @property
    def showFilters(self):
        if self.__showFilters is not None:
            return self.__showFilters

    @showFilters.setter
    def showFilters(self, showFilters):
        if isinstance(showFilters, bool):
            self.__showFilters = showFilters

    @property
    def showAbout(self):
        if self.__showAbout is not None:
            return self.__showAbout

    @showAbout.setter
    def showAbout(self, showAbout):
        if isinstance(showAbout, bool):
            self.__showAbout = showAbout

    @property
    def border(self):
        if self.__border is not None:
            return self.__border

    @border.setter
    def border(self, border):
        if isinstance(border, float):
            self.__border = border

class ToSvg:
    def __init__(self, domain='enterprise', source='taxii', local=None, config=None):
        """
            Sets up exporting system, builds underlying matrix

            :param domain: Which domain to utilize for the underlying matrix layout
            :param source: Use the taxii server or local data
            :param local: Optional path to local stix data
        """
        self.raw_handle = SvgTemplates(domain=domain, source=source, local=local)
        if config != None and isinstance(config, SVGConfig):
            self.config = config
        else:
            self.config = SVGConfig()

    def to_svg(self, layer, filepath='example.svg'):
        """
            Generate a svg file based on the input layer

            :param layer: Input attack layer object to transform
            :param filepath: Desired output svg location
            :return: (meta) svg file at the targeted output location
        """
        if layer is not None:
            if not isinstance(layer, Layer):
                raise TypeError

        if layer is None:
            raise NoLayer

        included_subs = []
        if layer.layer.techniques:
            for entry in layer.layer.techniques:
                if self.config.showSubtechniques == "expanded":
                    if entry.showSubtechniques:
                        if entry.tactic:
                            included_subs.append((entry.techniqueID, entry.tactic))
                        else:
                            included_subs.append((entry.techniqueID, False))
                elif self.config.showSubtechniques == "all":
                    if entry.tactic:
                        included_subs.append((entry.techniqueID, entry.tactic))
                    else:
                        included_subs.append((entry.techniqueID, False))
                else: # none displayed
                    pass

        excluded = []
        if layer.layer.hideDisabled:
            for entry in layer.layer.techniques:
                if not entry.enabled:
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
        d = self.raw_handle.export(showName=sName, showID=sID, sort=sort, scores=scores,
                                   subtechs=included_subs, colors=colors,
                                   exclude=excluded, lhandle=layer.layer, config=self.config)
        d.saveSvg(filepath)
