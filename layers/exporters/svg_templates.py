import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import drawSvg as draw

try:
    from exporters.matrix_gen import MatrixGen
    from exporters.svg_objects import G, SVG_HeaderBlock
except ModuleNotFoundError:
    from ..exporters.matrix_gen import MatrixGen
    from ..exporters.svg_objects import G, SVG_HeaderBlock


class BadTemplateException(Exception):
    pass


class SvgTemplates:

    def __init__(self, server=False, local=None, domain='enterprise'):
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
            self.h = MatrixGen(server=server, local=local)
            self.codex = self.h.get_matrix(muse)
        else:
            raise BadTemplateException

    def _build_raw(self, showName=True, showID=False, sort=0, scores=[], subtechs=[], exclude=[]):
        """
            INTERNAL - builds a raw, not-yet-marked-up excel document based on the specifications

            :param showName: Whether or not to display names for each entry
            :param showID: Whether or not to display Technique IDs for each entry
            :param sort: The sort mode to use
            :param subtechs: List of all visible subtechniques
            :param exclude: List of of techniques to exclude from the matrix
            :return: a openpyxl workbook object containing the raw matrix
        """
        self.codex = self.h._adjust_ordering(self.codex, sort, scores)
        template, joins = self.h._construct_panop(self.codex, subtechs, exclude)
        self.template = template
        increment_x = 50
        increment_y = 80
        max_x = increment_x * max([x[0] for x in self.template.keys()])
        max_y = increment_y * max([x[1] for x in self.template.keys()])
        d = draw.Drawing(max_x, max_y, origin=(0,-max_y), displayInline=False)

        root = G(tx=5, ty=5, style='font-family: sans-serif')
        header = G()
        root.append(header)
        b1 = G()
        g = SVG_HeaderBlock().build(height=86, width=336.8, label='about', t1text='heatmap example', t1size=28, t2text='An example layer where all\ntechniques have a randomized score', t2size='13.6')
        b2 = G(tx=354.6)
        g2 = SVG_HeaderBlock().build(height=86, width=336.6, label='filters', t1text='Windows, Linux, macOS', t1size=28, t2text='act', t2size=28)
        b3 = G(tx=709)
        g3 = SVG_HeaderBlock().build(height=86, width=336.6, label='legend', type='graphic')
        header.append(b1)
        header.append(b2)
        header.append(b3)
        b1.append(g)
        b2.append(g2)
        b3.append(g3)
        d.append(root)


        #header_coords = sorted([x for x in self.template.keys() if x[0] == 1])
        #current_index_x = max_x
        #current_index_y = 0
        #for entry in header_coords:
            # write_val = ''
            # if showName and showID:
            #     write_val = self.h._get_ID(self.codex, template[entry]) + ': ' + template[entry]
            # elif showName:
            #     write_val = template[entry]
            # elif showID:
            #     write_val = self.h._get_ID(self.codex, template[entry])
            # if any(entry[0] == y[0] and entry[1] == y[1] for y in joins):
            #     width = current_index_y + (increment_y * 2)
            # rect = Cell()
            # rect.append(draw.Rectangle(current_index_x, current_index_y, increment_y, increment_x, fill='gray'))
            # rect.append(draw.Text(write_val, 0.2, 0, 0, center=0, fill='black'))
            # d.append(rect)
            # d.setRenderSize()
            # current_index_x = current_index_x - increment_x
            # current_index_y = current_index_y + increment_y
        return d

    def export(self, showName, showID, sort=0, scores=[], subtechs=[], exclude=[]):
        """
            Export a raw svg template


            :param showName: Whether or not to display names for each entry
            :param showID: Whether or not to display Technique IDs for each entry
            :param sort: The sort mode to utilize
            :param subtechs: List of all visible subtechniques
            :param exclude: List of of techniques to exclude from the matrix
            return: a base template for the svg diagram
        """
        return self._build_raw(showName, showID, sort, scores, subtechs, exclude)