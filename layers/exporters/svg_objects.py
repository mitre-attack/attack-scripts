import drawSvg as draw

class Cell(draw.DrawingParentElement):
    TAG_NAME = 'a'
    def __init__(self):
        # Other init logic...
        # Keyword arguments to super().__init__() correspond to SVG node
        # arguments: stroke_width=5 -> stroke-width="5"
        super().__init__()

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
        if tx == None:
            tx = 0
        if ty == None:
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
    def __init__(self, text, font_size, ctype, x=None, y=None):
        if x == None:
            x = 0
        if y == None:
            y = 0
        super().__init__(text=text, fontSize=font_size, x=x, y=-y)
        self.args['class'] = ctype

class Root(draw.DrawingParentElement):
    TAG_NAME = 'g'
    def __init__(self):
        super().__init__(transform='translate(5,5)', style='font-family: sans-serif;')

# These calculations are eyeballed, and not quite right - we need to track down the specific math involved https://github.com/mitre-attack/attack-navigator/blob/58b4b4b3881f5e774c7e2dfa19fa5062675d555f/nav-app/src/app/exporter/exporter.component.ts#L52
class SVG_HeaderBlock():
    def build(self, height, width, label, type='text', t1text=None, t1size=None, t2text=None, t2size=None):
        g = G(ty=5)
        rect = HeaderRect(width, height, 'header-box')
        g.append(rect)
        rect2 = HeaderRect(width/10, height/5, 'label-cover', x=8, y=-9.67, outline=False)
        g.append(rect2)
        text = Text(label, 12, 'header-box-label', x=10, y=3)
        g.append(text)
        if type == 'text':
            internal = G(tx=5, ctype='header-box-content')
            g.append(internal)
            upper = G(tx=0, ty=2.1)
            internal.append(upper)
            if t1text is not None:
                t1 = Text(t1text, t1size, '', x=4, y= height/3)
                upper.append(t1)
                upper.append(Line(0, width-10, (height-5)/2, (height-5)/2, stroke='#dddddd'))
                if t2text is not None:
                    lower = G(tx=0, ty=(height - 8)/2)
                    t2 = Text(t2text, t2size, '', x=4, y = (height+5)/4)
                    lower.append(t2)
                    internal.append(lower)
        else:
            pass
        return g