import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import drawSvg as draw

try:
    from exporters.matrix_gen import MatrixGen
except ModuleNotFoundError:
    from ..exporters.matrix_gen import MatrixGen


class Cell(draw.DrawingParentElement):
    TAG_NAME = 'a'
    def __init__(self):
        # Other init logic...
        # Keyword arguments to super().__init__() correspond to SVG node
        # arguments: stroke_width=5 -> stroke-width="5"
        super().__init__()

class HeaderRect(draw.DrawingParentElement):
    TAG_NAME = 'rect'
    def __init__(self, width, height):
        super().__init__(width=width, height=height,stroke_width='1', stroke='black', fill='white')

class G(draw.DrawingParentElement):
    TAG_NAME = 'g'
    def __init__(self):
        super().__init__()

class TitleGroup(draw.DrawingParentElement):
    TAG_NAME = 'g'
    def __init__(self, x, y):
        super().__init__(transform='translate(' + str(x) + ',' + str(y) + ')')

class HeaderText(draw.DrawingParentElement):
    TAG_NAME = 'text'
    def __init__(self, text, pad, fontsize, font_units):
        tform = 'translate(' + str(pad) + ',' + str(fontsize + pad) + ')'
        super().__init__(text=text, transform=tform, dx=0, dy=0, font_size=font_units + fontsize, font_weight="bold")

class Root(draw.DrawingParentElement):
    TAG_NAME = 'g'
    def __init__(self):
        super().__init__(transform='translate(5,5)', style='font-family: sans-serif;')

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

        width = 250
        height = 250
        master = Root()
        g = G()
        master.append(g)
        heads = TitleGroup(0,0)
        g.append(heads)
        h2 = TitleGroup(0,5)
        heads.append(h2)
        rect = HeaderRect(width, height)
        h2.append(rect)
        tex = HeaderText('this was a test', 5, 80, 80)
        h2.append(tex)
        d.append(master)


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