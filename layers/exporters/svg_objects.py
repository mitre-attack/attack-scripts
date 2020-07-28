import drawSvg as draw
import string
import colorsys

def _getapproximatestringwidth(st):
    """
        Internal - estimate the width of a string... somewhat poorly

        :param st: The string to evaluate
        :return: A number that roughly describes the length of the string
    """
    size = 0
    for s in st:
        if s in 'lij|\' ':
            size += 37
        elif s in '![]fI.,:;/\\t':
            size += 50
        elif s in '`-(){}r"':
            size += 60
        elif s in '*^zcsJkvxy':
            size += 85
        elif s in 'aebdhnopqug#$L+<>=?_~FZT' + string.digits:
            size += 95
        elif s in 'BSPEAKVXY&UwNRCHD':
            size += 112
        elif s in 'QGOMm%W@':
            size += 135
        else:
            size += 50
    return size * 6 / 75

def _calculateviablestringsize(st, target, width):
    """
        Internal - Calculate the font size needed to make a string fit, roughly

        :param st: The string to evaluate
        :param target: The initial font size
        :param width: The width to fit into
        :return: An adjusted font size
    """
    current_font_size = target
    while (_getapproximatestringwidth(st) * current_font_size) > (width * 10):
        current_font_size -= 1
    return current_font_size

def _wrap(st, font_size, width):
    """
        Internal - Wrap a string in the event it can't fit on one line

        :param st: String to wrap
        :param font_size: Target font size for the string
        :param width: The width of the block the line fits in
        :return: A string with line breaks to make it fit in the space provided
    """
    p1 = 0
    p2 = 1
    block = (width - 30) * 10
    construct = st.split(' ')
    if len(construct) == 1:
        return st
    build = ''
    while p2 < len(construct):
        loop = True
        strwidth = _getapproximatestringwidth(' '.join(construct[p1:p2])) * font_size

        if strwidth < block:
            p2 += 1
            loop = False
        else:
            if p1 == p2 - 1:
                pass
            else:
                build += ' '.join(construct[p1:p2-1]) + '\n'
                loop = False
                p1 = p2 - 1
        if loop:
            # force an oversized chunk
            build += ' '.join(construct[p1:p2]) + '\n'
            p1 += 1
            p2 += 1
    if _getapproximatestringwidth(' '.join(construct[p1:])) * font_size > block:
        build += ' '.join(construct[p1:-1]) + '\n' + construct[-1]
    else:
        build += ' '.join(construct[p1:])
    return build

class Cell(draw.DrawingParentElement):
    TAG_NAME = 'rect'
    def __init__(self, height, width, fill, ctype=None):
        super().__init__(height=height, width=width, style='fill: rgb({}, {}, {})'.format(fill[0], fill[1], fill[2]),
                         stroke='#6B7279')
        if ctype:
            self.args['class'] = ctype

class HeaderRect(draw.DrawingParentElement):
    TAG_NAME = 'rect'
    def __init__(self, width, height, ctype, x=None, y=None, outline=True):
        super().__init__(width=width, height=height, fill='white', rx='5')
        self.args['class'] = ctype
        if x:
            self.args['x'] = x
        if y:
            self.args['y'] = y
        if outline:
            self.args['stroke'] = 'black'

class G(draw.DrawingParentElement):
    TAG_NAME = 'g'
    def __init__(self, tx=None, ty=None, style=None, ctype=None):
        super().__init__()
        if tx is None:
            tx = 0
        if ty is None:
            ty = 0
        self.args['transform']='translate(' + str(tx) +',' + str(ty) +')'
        if style:
            self.args['style'] = style
        if ctype:
            self.args['class'] = ctype

class Line(draw.DrawingParentElement):
    TAG_NAME = 'line'
    def __init__(self, x1, x2, y1, y2, stroke):
        super().__init__(x1=x1, x2=x2, y1=y1, y2=y2, stroke=stroke)

class Text(draw.Text):
    def __init__(self, text, font_size, ctype, position=None, tx=None, ty=None, x=None, y=None, fill=None):
        if x is None:
            x = 0
        if y is None:
            y = 0
        super().__init__(text=text, fontSize=font_size, x=x, y=-y)
        self.args['class'] = ctype
        if tx is None:
            tx = 0
        if ty is None:
            ty = 0
        if tx != 0 or ty != 0:
            self.args['transform']='translate(' + str(tx) +',' + str(ty) +')'
        if position:
            self.args['style'] = 'text-anchor: {}'.format(position)
        if fill:
            self.args['fill'] = fill

class Root(draw.DrawingParentElement):
    TAG_NAME = 'g'
    def __init__(self):
        super().__init__(transform='translate(5,5)', style='font-family: sans-serif;')

class Swatch(draw.DrawingParentElement):
    TAG_NAME = 'rect'
    def __init__(self, height, width, fill):
        super().__init__(height=height, width=width, style='fill: rgb({}, {}, {})'.format(fill[0], fill[1], fill[2]))


class SVG_HeaderBlock:
    @staticmethod
    def build(height, width, label, variant='text', t1text=None, t1size=None, t2text=None, t2size=None, colors=[],
              values=(0,100)):
        """
            Build a single SVG Header Block object

            :param height: Height of the block
            :param width: Width of the block
            :param label: Label for the block
            :param variant: text or graphic - the type of header block to build
            :param t1text: upper text
            :param t1size: upper text size
            :param t2text: lower text
            :param t2size: lower text size
            :param colors: colors for the graphic variant
            :param values: values for the graphic variant's gradient
            :return:
        """
        g = G(ty=5)
        rect = HeaderRect(width, height, 'header-box')
        g.append(rect)
        rect2 = HeaderRect(_getapproximatestringwidth(label), height/5, 'label-cover', x=8, y=-9.67, outline=False)
        g.append(rect2)
        text = Text(label, 12, 'header-box-label', x=10, y=3)
        g.append(text)
        internal = G(tx=5, ctype='header-box-content')
        g.append(internal)
        if variant == 'text':
            upper = G(tx=0, ty=2.1)
            internal.append(upper)
            if t1text is not None:
                t1 = Text(t1text, _calculateviablestringsize(t1text, t1size, width), '', x=4, y= height/3)
                upper.append(t1)
                upper.append(Line(0, width-10, (height-5)/2, (height-5)/2, stroke='#dddddd'))
                if t2text is not None:
                    lower = G(tx=0, ty= (height/3 + t1size))
                    y = 10
                    lines = 4
                    fs = t2size
                    while lines > 2:
                        adjusted = _wrap(t2text, fs, width + 15)
                        lines = adjusted.count('\n')
                        if lines > 2:
                            fs = fs / 2
                    lines += 1
                    if lines > 1:
                        y = y / (4 ** lines)
                    t2 = Text(adjusted, fs, '', x=4, y=y)
                    lower.append(t2)
                    internal.append(lower)
        else:
            if len(colors):
                usable = width - 10
                block_width = usable/len(colors)
                sub1 = G(ty=5)
                sub2 = G(ty=5)
                internal.append(sub1)
                sub1.append(sub2)
                cells = G(ctype="legendCells")
                sub2.append(cells)
                offset = 0
                span = [values[0]]
                for blah in colors[:-1]:
                    span.append(int(values[1]/(len(colors)-1) * (colors.index(blah) + 1)))
                for entry in colors:
                    cell = G(ctype="cell", tx=offset)
                    conv = entry
                    if conv.startswith('#'):
                        conv = conv[1:]
                    block = Swatch(15, block_width, tuple(int(conv[i:i+2], 16) for i in (0, 2, 4)))
                    offset += block_width
                    cell.append(block)
                    cells.append(cell)
                    tblob = str(span[colors.index(entry)])
                    off = (block_width-(5 * (1+ len(tblob))))/2
                    label = Text(tblob, 12, ctype='label', ty=25, tx=off)
                    cell.append(label)
        return g

class SVG_Technique:
    def __init__(self, gradient):
        self.grade = gradient

    def build(self, offset, technique, subtechniques=[], mode=(True, False), tactic=None, colors=[]):
        """
            Build a SVG Technique block

            :param offset: Current offset to build the block at (so it fits in the column)
            :param technique: The technique to build a block for
            :param subtechniques: List of any visible subtechniques for this technique
            :param mode: Display mode (Show Name, Show ID)
            :param tactic: The corresponding tactic
            :param colors: List of all default color values if no score can be found
            :return: The newly created SVG technique block
        """
        height = 5.6
        width = 80
        indent = 11.2
        g = G(ty=offset)
        c = self._com_color(technique, tactic, colors)
        t = dict(name=self._disp(technique.name, technique.id, mode), id=technique.id,
                 color=tuple(int(c[i:i+2], 16) for i in (0, 2, 4)))
        tech, text = self._block(t, height, width)
        g.append(tech)
        g.append(text)
        new_offset = height
        for entry in subtechniques:
            gp = G(tx=indent, ty=new_offset)
            g.append(gp)
            c = self._com_color(entry, tactic, colors)
            st = dict(name=self._disp(entry.name, entry.id, mode), id=entry.id,
                     color=tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)))
            subtech, subtext = self._block(st, height, width - indent)
            gp.append(subtech)
            gp.append(subtext)
            new_offset = new_offset + height
        if len(subtechniques):
            g.append(draw.Lines(2, -height,
                                9, -height * 2,
                                9, -height * (len(subtechniques) + 1),
                                indent, -height * (len(subtechniques) + 1),
                                indent, -height,
                       close=True,
                       fill='#6B7279',
                       stroke='#6B7279'))
        return g, offset + new_offset

    @staticmethod
    def _block(technique, height, width):
        tech = Cell(height, width, technique['color'], ctype=technique['id'])
        fs = 4.5
        adjusted = _wrap(technique['name'], fs/3, width - 13)
        lines = adjusted.count('\n')
        y = 4.31
        if lines > 0:
            fs = fs / (2**lines)
            y = y / (2**lines) + .15 * (2**lines)
        hls = colorsys.rgb_to_hls(technique['color'][0], technique['color'][1], technique['color'][2])
        fill = None
        if hls[1] < 127.5:
            fill = 'white'
        text = Text(adjusted.encode('utf-8').decode('ascii', 'backslashreplace'), fs, '', x=4, y=y, fill=fill)
        return tech, text

    def _com_color(self, technique, tactic, colors=[]):
        c = 'FFFFFF'
        if technique.score:
            c = self.grade.compute_color(technique.score)[1:]
        else:
            for x in colors:
                if x[0] == technique.id and (x[1] == tactic or not x[1]):
                    c = x[2][1:]
        if c == 'FFFFFF':
            if 0 >= self.grade.minValue:
                c = self.grade.compute_color(0)[1:]
        return c

    @staticmethod
    def _disp(name, id, mode):
        p1 = name
        p2 = id
        if not mode[0]:
            p1 = ''
        if not mode[1]:
            p2 = ''
        out = ': '.join([p2, p1])
        if out.startswith(': '):
            return p1
        return out