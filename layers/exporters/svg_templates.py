import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import drawSvg as draw

try:
    from exporters.matrix_gen import MatrixGen
    from exporters.svg_objects import G, SVG_HeaderBlock, SVG_Technique, Text
except ModuleNotFoundError:
    from ..exporters.matrix_gen import MatrixGen
    from ..exporters.svg_objects import G, SVG_HeaderBlock, SVG_Technique, Text


class BadTemplateException(Exception):
    pass


class SvgTemplates:
    def __init__(self, source='taxii', domain='enterprise', local=None):
        """
            Initialization - Creates a ExcelTemplate object

            :param server: Whether or not to use the taxii server to build the matrix
            :param local: Optional path to local taxii data
            :param domain: The domain to utilize
        """
        muse = domain
        if muse.startswith('mitre-'):
            muse = domain[6:]
        if muse in ['enterprise', 'mobile']:
            self.mode = muse
            self.h = MatrixGen(source=source, local=local)
            self.codex = self.h.get_matrix(muse)
        else:
            raise BadTemplateException

    # Configurable Constants
    incre_x = 80
    incre_y = 20
    tactic_spacing = 10
    header_height = 86
    tactic_font = 8
    header_text_size = 28

    def _build_headers(self, name, desc=None, filters=None, gradient=None):
        max_y = self.incre_y * max(len(x.techniques) for x in self.codex) + self.header_height
        max_x = self.incre_x * (len(self.codex)) + (self.tactic_spacing * len(self.codex)) + 50
        d = draw.Drawing(max_x, max_y, origin=(0, -max_y), displayInline=False)

        operation_x = max_x - 30

        root = G(tx=5, ty=5, style='font-family: sans-serif')
        header = G()
        root.append(header)
        b1 = G()
        header.append(b1)

        header_count = 1
        psych = 1
        if filters is not None:
            header_count += 1
        if gradient is not None:
            header_count += 1

        header_width = operation_x / header_count - 30
        if desc is not None:
            g = SVG_HeaderBlock().build(height=self.header_height, width=header_width, label='about', t1text=name,
                                    t1size=self.header_text_size, t2text=desc, t2size=self.header_text_size)
        else:
            g = SVG_HeaderBlock().build(height=self.header_height, width=header_width, label='about', t1text=name,
                                        t1size=self.header_text_size)
        b1.append(g)
        if filters is not None:
            g2 = SVG_HeaderBlock().build(height=self.header_height, width=header_width, label='filters',
                                     t1text=', '.join(filters.platforms), t1size=self.header_text_size,
                                     t2text=filters.stages[0], t2size=self.header_text_size)
            b2 = G(tx=operation_x / header_count)
            header.append(b2)
            b2.append(g2)
            psych += 1
        if gradient is not None:
            b3 = G(tx=operation_x / header_count * psych)
            colors = [gradient.compute_color(gradient.minValue)]
            for i in range(1, len(gradient.colors) * 2):
                colors.append(gradient.compute_color(int(gradient.maxValue/(len(gradient.colors)*2)) * i))
            g3 = SVG_HeaderBlock().build(height=self.header_height, width=header_width, label='legend', type='graphic',
                                         colors=colors, values=(gradient.minValue, gradient.maxValue))
            header.append(b3)
            b3.append(g3)
        d.append(root)
        return d

    def get_tactic(self, tactic, colors=[], subtechs=[], exclude=[], mode=(True, False)):
        offset = 0
        column = G(ty=2)
        for x in tactic.techniques:
            if any(x.id == y[0] and (y[1] == self.h.convert(tactic.tactic.name) or not y[1]) for y in exclude):
                continue
            if any(x.id == y[0] and (y[1] == self.h.convert(tactic.tactic.name) or not y[1]) for y in subtechs):
                a, offset = self.get_tech(offset, mode, x, tactic=self.h.convert(tactic.tactic.name),
                                          subtechniques=tactic.subtechniques.get(x.id, []), colors=colors)
            else:
                a, offset = self.get_tech(offset, mode, x, tactic=self.h.convert(tactic.tactic.name),
                                          subtechniques=[], colors=colors)
            column.append(a)
        return column

    def get_tech(self, offset, mode, technique, tactic, subtechniques=[], colors=[]):
        a, b = SVG_Technique(self.lhandle.gradient).build(offset, technique, subtechniques=subtechniques, mode=mode,
                                                          tactic=tactic, colors=colors)
        return a, b

    def export(self, showName, showID, lhandle, sort=0, scores=[], colors=[], subtechs=[], exclude=[]):
        """
            Export a raw svg template

            :param showName: Whether or not to display names for each entry
            :param showID: Whether or not to display Technique IDs for each entry
            :param sort: The sort mode to utilize
            :param subtechs: List of all visible subtechniques
            :param exclude: List of of techniques to exclude from the matrix
            return: a base template for the svg diagram
        """
        self.codex = self.h._adjust_ordering(self.codex, sort, scores)
        self.lhandle = lhandle
        glob = G()
        incre = self.incre_x + self.tactic_spacing
        index = 5
        for x in self.codex:
            g = G(tx=index, ty=self.header_height + 30)
            gt = G(tx=(self.incre_x / 2) + 2)
            index += incre
            tx = Text(ctype='TacticName', font_size=self.tactic_font, text=x.tactic.name, position='middle')
            gt.append(tx)
            a = self.get_tactic(x, colors=colors, subtechs=subtechs, exclude=exclude, mode=(showName,showID))
            g.append(gt)
            g.append(a)
            glob.append(g)
        return glob