import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import drawSvg as draw

try:
    from exporters.matrix_gen import MatrixGen
    from exporters.svg_objects import G, SVG_HeaderBlock, SVG_Technique, Text, convertToPx,_optimalFontSize
    from core.gradient import Gradient
    from core.filter import Filter
except ModuleNotFoundError:
    from ..exporters.matrix_gen import MatrixGen
    from ..exporters.svg_objects import G, SVG_HeaderBlock, SVG_Technique, Text, convertToPx, _optimalFontSize
    from ..core.gradient import Gradient
    from ..core.filter import Filter


class BadTemplateException(Exception):
    pass


class SvgTemplates:
    def __init__(self, source='taxii', domain='enterprise', local=None):
        """
            Initialization - Creates a SvgTemplate object

            :param domain: Which domain to utilize for the underlying matrix layout
            :param source: Use the taxii server or local data
            :param local: Optional path to local stix data
        """
        muse = domain
        if muse.startswith('mitre-'):
            muse = domain[6:]
        if muse in ['enterprise', 'mobile']:
            self.mode = muse
            self.h = MatrixGen(source=source, local=local)
            self.codex = self.h.get_matrix(muse)
            self.lhandle = None
        else:
            raise BadTemplateException

    def _build_headers(self, name, config, desc=None, filters=None, gradient=None):
        """
            Internal - build the header blocks for the svg

            :param name: The name of the layer being exported
            :param config: SVG Config object
            :param desc: Description of the layer being exported
            :param filters: Any filters applied to the layer being exported
            :param gradient: Gradient information included with the layer
            :return: Instantiated SVG header
        """
        max_x = convertToPx(config.width, config.unit)
        max_y = convertToPx(config.height, config.unit)
        header_height = convertToPx(config.headerHeight, config.unit)
        ff = config.font
        d = draw.Drawing(max_x, max_y, origin=(0, -max_y), displayInline=False)
        psych = 0
        overlay = None
        if config.showHeader:
            operation_x = max_x - 30

            root = G(tx=5, ty=5, style='font-family: {}'.format(ff))

            header = G()
            root.append(header)
            b1 = G()
            header.append(b1)

            header_count = 0
            if config.showAbout:
                header_count += 1
            if config.showFilters:
                header_count += 1
            if config.showLegend and config.legendDocked:
                header_count += 1

            if header_count > 0:
                header_width = max_x / header_count - (15 * (header_count-1))
                if config.showAbout:
                    if desc is not None:
                        g = SVG_HeaderBlock().build(height=header_height, width=header_width, label='about', t1text=name,
                                                    t2text=desc, config=config)
                    else:
                        g = SVG_HeaderBlock().build(height=header_height, width=header_width, label='about', t1text=name,
                                                    config=config)
                    b1.append(g)
                    psych += 1
                if config.showFilters:
                    fi = filters
                    if fi is None:
                        fi = Filter()
                        fi.platforms = ["Windows", "Linux",	"macOS"]
                        fi.stages = ["act"]
                    g2 = SVG_HeaderBlock().build(height=header_height, width=header_width, label='filters',
                                             t1text=', '.join(fi.platforms), t2text=fi.stages[0], config=config)
                    b2 = G(tx=operation_x / header_count * psych + 20 * psych)
                    header.append(b2)
                    b2.append(g2)
                    psych += 1
                if config.showLegend:
                    gr = gradient
                    if gr is None:
                        gr = Gradient(colors=["#ff6666","#ffe766","#8ec843"], minValue=1, maxValue=100)
                    colors = []
                    div = round((gr.maxValue - gr.minValue) / (len(gr.colors) * 2 - 1))
                    for i in range(0, len(gr.colors) * 2 - 1):
                        colors.append(
                            (gr.compute_color(int(gr.minValue + div * i)), gr.minValue + div * i))
                    colors.append((gr.compute_color(gr.maxValue), gr.maxValue))
                    if config.legendDocked:
                        b3 = G(tx=operation_x / header_count * psych + 20 * psych)
                        g3 = SVG_HeaderBlock().build(height=header_height, width=header_width, label='legend',
                                                     variant='graphic', colors=colors, config=config)
                        header.append(b3)
                        b3.append(g3)
                        psych +=1
                    else:
                        adjusted_height = convertToPx(config.legendHeight, config.unit)
                        adjusted_width = convertToPx(config.legendWidth, config.unit)
                        g3 = SVG_HeaderBlock().build(height=adjusted_height, width=adjusted_width, label='legend',
                                                     variant='graphic', colors=colors, config=config)
                        lx = convertToPx(config.legendX, config.unit)
                        if not lx:
                            lx = max_x - adjusted_width - convertToPx(config.border, config.unit)
                        ly = convertToPx(config.legendY, config.unit)
                        if not ly:
                            ly = max_y - adjusted_height - convertToPx(config.border, config.unit)
                        overlay = G(tx=lx, ty=ly)
                        if (ly + adjusted_height) > max_y or (lx + adjusted_width) > max_x:
                            print("[WARNING] - Floating legend will render partly out of view...")
                        overlay.append(g3)
            d.append(root)
        return d, psych, overlay

    def get_tactic(self, tactic, height, width, config, colors=[], scores=[], subtechs=[], exclude=[],
                   mode=(True, False)):
        """
            Build a 'tactic column' svg object

            :param tactic: The corresponding tactic for this column
            :param height: A technique block's allocated height
            :param width: A technique blocks' allocated width
            :param config: A SVG Config object
            :param colors: Default color data in case of no score
            :param scores: Score values for the dataset
            :param subtechs: List of visible subtechniques
            :param exclude: List of excluded techniques
            :param mode: Tuple describing text for techniques (Show Name, Show ID)
            :return: Instantiated tactic column
        """
        offset = 0
        column = G(ty=2)
        for x in tactic.techniques:
            if any(x.id == y[0] and (y[1] == self.h.convert(tactic.tactic.name) or not y[1]) for y in exclude):
                continue
            found = False
            for y in scores:
                if x.id == y[0] and (y[1] == self.h.convert(tactic.tactic.name) or not y[1]):
                    x.score = y[2]
                    found = True
                    continue
            if not found:
                x.score = None
            if any(x.id == y[0] and (y[1] == self.h.convert(tactic.tactic.name) or not y[1]) for y in subtechs):
                a, offset = self.get_tech(offset, mode, x, tactic=self.h.convert(tactic.tactic.name),
                                          subtechniques=tactic.subtechniques.get(x.id, []), colors=colors,
                                          config=config, height=height, width=width)
            else:
                a, offset = self.get_tech(offset, mode, x, tactic=self.h.convert(tactic.tactic.name),
                                          subtechniques=[], colors=colors, config=config, height=height, width=width)
            column.append(a)
        return column

    def get_tech(self, offset, mode, technique, tactic, config, height, width, subtechniques=[], colors=[]):
        """
            Retrieve a svg object for a single technique

            :param offset: The offset in the column based on previous work
            :param mode: Tuple describing display format (Show Name, Show ID)
            :param technique: The technique to build a block for
            :param tactic: The corresponding tactic
            :param config: An SVG Config object
            :param height: The allocated height of a technique block
            :param width: The allocated width of a technique block
            :param subtechniques: A list of all visible subtechniques, some of which may apply to this one
            :param colors: A list of all color overrides in the event of no score, which may apply
            :return: Tuple (SVG block, new offset)
        """
        a, b = SVG_Technique(self.lhandle.gradient).build(offset, technique, height,
                                                          width, subtechniques=subtechniques, mode=mode,
                                                          tactic=tactic, colors=colors, tBC=config.tableBorderColor)
        return a, b

    def export(self, showName, showID, lhandle, config, sort=0, scores=[], colors=[], subtechs=[], exclude=[]):
        """
            Export a layer object to an SVG object

            :param showName: Boolean of whether or not to show names
            :param showID:  Boolean of whether or not to show IDs
            :param lhandle: The layer object being exported
            :param config: A SVG Config object
            :param sort: The sort mode
            :param scores: List of tactic scores
            :param colors: List of tactic default colors
            :param subtechs: List of visible subtechniques
            :param exclude: List of excluded techniques
            :return:
        """
        d, presence, overlay = self._build_headers(lhandle.name, config, lhandle.description, lhandle.filters,
                                            lhandle.gradient)
        self.codex = self.h._adjust_ordering(self.codex, sort, scores)
        self.lhandle = lhandle
        glob = G()
        index = 5
        lengths = []
        for x in self.codex:
            sum = len(x.techniques)
            for enum in exclude:
                if enum[0] in [y.id for y in x.techniques]:
                    if self.h.convert(enum[1]) == x.tactic.name or enum[1] == False:
                        sum -= 1
            for y in x.subtechniques:
                if y in [z[0] for z in subtechs]:
                    sum += len(x.subtechniques[y])
            lengths.append(sum)
        tech_width = (convertToPx(config.width, config.unit) / len(self.codex)) - 10
        header_offset = convertToPx(config.headerHeight, config.unit)
        if presence == 0:
            header_offset = 0
        header_offset += 30
        tech_height = (convertToPx(config.height, config.unit) - header_offset -
                       convertToPx(config.border, config.unit)) / max(lengths)
        incre = tech_width + 10
        set = 0
        for x in self.codex:
            disp = ''
            if showName and showID:
                disp = x.tactic.id + ": " + x.tactic.name
            elif showName:
                disp = x.tactic.name
            elif showID:
                disp = x.tactic.id

            g = G(tx=index, ty=header_offset)
            gt = G(tx=(tech_width / 2) + 2)
            index += incre
            fs, _ = _optimalFontSize(disp, tech_width, tech_height+10, maxFontSize=28)
            if set == 0:
                set = fs
            tx = Text(ctype='TacticName', font_size=set, text=disp, position='middle')
            gt.append(tx)
            a = self.get_tactic(x, tech_height, tech_width, colors=colors, subtechs=subtechs, exclude=exclude,
                                mode=(showName, showID), scores=scores, config=config)
            g.append(gt)
            g.append(a)
            glob.append(g)
        d.append(glob)
        if overlay:
            d.append(overlay)
        return d