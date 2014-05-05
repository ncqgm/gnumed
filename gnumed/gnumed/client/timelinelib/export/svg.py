# Copyright (C) 2009, 2010, 2011  Rickard Lindberg, Roger Lindberg
#
# This file is part of Timeline.
#
# Timeline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Timeline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Timeline.  If not, see <http://www.gnu.org/licenses/>.


from types import UnicodeType
from xml.sax.saxutils import escape as xmlescape

from pysvg.structure import *
from pysvg.core import *
from pysvg.text import *
from pysvg.shape import *
from pysvg.builders import *
from pysvg.filter import *

from timelinelib.db.objects.category import sort_categories
from timelinelib.drawing.utils import darken_color


OUTER_PADDING = 5      # Space between event boxes (pixels)
INNER_PADDING = 3      # Space inside event box to text (pixels)
DATA_INDICATOR_SIZE = 10
SMALL_FONT_SIZE = 9
MAJOR_STRIP_FONT_SIZE = 6
ENCODING = "utf-8"


def export(path, scene, view_properties):
    svgDrawer = SVGDrawingAlgorithm(path, scene, view_properties, shadow=True)
    svgDrawer.draw()
    svgDrawer.write(path)


class SVGDrawingAlgorithm(object):

    # options:  shadow=True|False
    def __init__(self, path, scene, view_properties, **kwargs):
        # store important data references
        self.path = path
        self.scene = scene
        self.view_properties = view_properties
        # SVG document size, maybe TODO
        self.metrics = dict({'widthpx':1052, 'heightpx':744});
        # SVG document handle
        self.svg = svg(width="%dpx" % self.metrics['widthpx'], height="%dpx" % self.metrics['heightpx'])
        # Fonts and pens we use when drawing
        # SVG Text style
        filterShadow = filter(x="-.3",y="-.5", width=1.9, height=1.9)
        filtBlur = feGaussianBlur(stdDeviation="4")
        filtBlur.set_in("SourceAlpha")
        filtBlur.set_result("out1")
        filtOffset = feOffset()
        filtOffset.set_in("out1")
        filtOffset.set_dx(4)
        filtOffset.set_dy(-4)
        filtOffset.set_result("out2")
        filtMergeNode1 = feMergeNode()
        filtMergeNode1.set_in("out2")
        filtMergeNode2 = feMergeNode()
        filtMergeNode2.set_in("SourceGraphic")
        filtMerge = feMerge()
        filtMerge.addElement(filtMergeNode1)
        filtMerge.addElement(filtMergeNode2)
        filterShadow.addElement(filtBlur) # here i get an error from python. It is not allowed to add a primitive filter
        filterShadow.addElement(filtOffset)
        filterShadow.addElement(filtMerge)
        filterShadow.set_id("filterShadow")
        d=defs()
        d.addElement(filterShadow)
        self.svg.addElement(d)
        # local flags
        self.shadowFlag = False
        # flag handling
        for key in kwargs:
            if key == 'shadow':
                self.shadowFlag = kwargs[key]

    def write(self, path):
        """
        write the SVG code into the file with filename path. No
        checking is done if file/path exists
        """
        self.svg.save(path, encoding=ENCODING)

    def draw(self):
        self._draw_bg()
        self._draw_events(self.view_properties)
        self._draw_legend(self.view_properties, self._extract_categories())

    def _draw_bg(self):
        """
        Draw major and minor strips, lines to all event boxes and baseline.
        Both major and minor strips have divider lines and labels.
        """
        myStyle = StyleBuilder()
        myStyle.setStrokeDashArray((2,2))
        myStyle.setFontFamily(fontfamily="Verdana")
        myStyle.setFontSize("2em")
        myStyle.setTextAnchor('left')
        svgGroup = g()
        self._draw_minor_strips(svgGroup, myStyle)
        self._draw_major_strips(svgGroup, myStyle)
        self._draw_divider_line(svgGroup)
        self._draw_lines_to_non_period_events(svgGroup, self.view_properties)
        self._draw_now_line(svgGroup)
        self.svg.addElement(svgGroup)

    def _draw_minor_strips(self, group, style):
        for strip_period in self.scene.minor_strip_data:
            self._draw_minor_strip_divider_line_at(group,strip_period.end_time)
            self._draw_minor_strip_label(group, style, strip_period)

    def _draw_minor_strip_divider_line_at(self, group, time):
        x = self.scene.x_pos_for_time(time)
        oh = ShapeBuilder()
        line = oh.createLine(x,0,x,self.scene.height, strokewidth=0.5, stroke="lightgrey")
        group.addElement(line)

    def _draw_minor_strip_label(self, group, style, strip_period):
        label = self.scene.minor_strip.label(strip_period.start_time)
        middle = self.scene.x_pos_for_time(strip_period.start_time) + INNER_PADDING
        # check for negative values
        if middle < INNER_PADDING:
            return
        middley = self.scene.divider_y
        # Label
        myText = self._text(label, middle, middley)
        myText.set_style(style)
        group.addElement(myText)

    def _draw_major_strips(self, group, style):
        oh = ShapeBuilder()
        style.setStrokeDashArray("")
        fontSize = MAJOR_STRIP_FONT_SIZE
        style.setFontSize("%dem" % fontSize)
        for tp in self.scene.major_strip_data:
            # Divider line
            x = self.scene.x_pos_for_time(tp.end_time)
            line = oh.createLine(x,0,x,self.scene.height,strokewidth=0.5, stroke="grey")
            # Label
            label = self.scene.major_strip.label(tp.start_time, True)
            x = self.scene.x_pos_for_time(tp.start_time) + INNER_PADDING
            #            x = self.scene.x_pos_for_time(tp.mean_time()) - tw / 2
            # If the label is not visible when it is positioned in the middle
            # of the period, we move it so that as much of it as possible is
            # visible without crossing strip borders.
            extra_vertical_padding = 0
            if x - INNER_PADDING < 0:
                x = INNER_PADDING
                extra_vertical_padding = fontSize * 4
                # since there is no function like textwidth() for SVG, just take into account that text can be overwritten
                # do not perform a special handling for right border, SVG is unlimited
            myText = self._text(label, x, fontSize*4+INNER_PADDING+extra_vertical_padding)
            myText.set_style(style)
            group.addElement(myText)

    def _draw_divider_line(self, group):
        oh = ShapeBuilder()
        line = oh.createLine(0, self.scene.divider_y, self.scene.width,
                             self.scene.divider_y, strokewidth=0.5, stroke="grey")
        group.addElement(line)

    def _draw_lines_to_non_period_events(self, group, view_properties):
        for (event, rect) in self.scene.event_data:
            if rect.Y < self.scene.divider_y:
                x = self.scene.x_pos_for_time(event.mean_time())
                y = rect.Y + rect.Height / 2
                if view_properties.is_selected(event):
                    myStroke="red"
                else:
                    myStroke="black"
                oh = ShapeBuilder()
                line = oh.createLine(x, y, x, self.scene.divider_y, stroke=myStroke)
                group.addElement(line)
                circle = oh.createCircle(x, self.scene.divider_y, 2)
                group.addElement(circle)

    def _draw_now_line(self, group):
        x = self.scene.x_pos_for_now()
        if x > 0 and x < self.scene.width:
            oh = ShapeBuilder()
            line = oh.createLine(x, 0, x, self.scene.height, stroke="darkred")
            group.addElement(line)

    def _get_base_color(self, event):
        if event.category:
            base_color = event.category.color
        else:
            base_color = (200, 200, 200)
        return base_color

    def _get_border_color(self, event):
        base_color = self._get_base_color(event)
        border_color = darken_color(base_color)
        return border_color

    def _map_svg_color(self, color):
        """
        map (r,g,b) color to svg string
        """
        sColor = "#%02X%02X%02X" % color
        return sColor

    def _get_box_border_color(self, event):
        border_color = self._get_border_color(event)
        sColor = self._map_svg_color(border_color)
        return sColor

    def _get_box_color(self, event):
        """ get the color of the event box """
        base_color = self._get_base_color(event)
        sColor = self._map_svg_color(base_color)
        return sColor

    def _get_box_indicator_color(self, event):
        base_color = self._get_base_color(event)
        darker_color = darken_color(base_color, 0.6)
        sColor = self._map_svg_color(darker_color)
        return sColor

    def _legend_should_be_drawn(self, view_properties, categories):
        return view_properties.show_legend and len(categories) > 0

    def _extract_categories(self):
        categories = []
        for (event, rect) in self.scene.event_data:
            cat = event.category
            if cat and not cat in categories:
                categories.append(cat)
        return sort_categories(categories)

    def _draw_legend(self, view_properties, categories):
        """
        Draw legend for the given categories.

        Box in lower right corner
            Motivation for positioning in right corner:
            SVG text cannot be centered since the text width cannot be calculated
            and the first part of each event text is important.
            ergo: text needs to be left aligned.
                  But then the probability is high that a lot of text is at the left
                  bottom
                  ergo: put the legend to the right.

          +----------+
          | Name   O |
          | Name   O |
          +----------+
        """
        if self._legend_should_be_drawn(view_properties, categories):
            num_categories = len(categories)
            if num_categories == 0:
                return
            font_size = SMALL_FONT_SIZE
            myStyle = StyleBuilder()
            myStyle.setFontFamily(fontfamily="Verdana")
            myStyle.setFontSize(font_size)
            myStyle.setTextAnchor('left')
            # reserve 15% for the legend
            width = int(self.metrics['widthpx'] * 0.15)
            item_height = font_size + OUTER_PADDING
            height = num_categories *(item_height+INNER_PADDING)+2*OUTER_PADDING
            # Draw big box
            builder = ShapeBuilder()
            x = self.metrics['widthpx'] - width - OUTER_PADDING
            svgGroup = g()
            box_rect = builder.createRect(x,
                                               self.metrics['heightpx'] - height - OUTER_PADDING,
                                               width, height,fill='white')
            svgGroup.addElement(box_rect)
            # Draw text and color boxes
            cur_y = self.metrics['heightpx'] - height - OUTER_PADDING + INNER_PADDING
            for cat in categories:
                base_color = self._map_svg_color(cat.color)
                border_color = self._map_svg_color(darken_color(cat.color))
                color_box_rect = builder.createRect(x + OUTER_PADDING,
                                  cur_y, item_height, item_height, fill=base_color,
                                  stroke=border_color)
                svgGroup.addElement(color_box_rect)
                myText = self._svg_clipped_text(cat.name,
                                       (x + OUTER_PADDING + INNER_PADDING+item_height,
                                        cur_y, width-OUTER_PADDING-INNER_PADDING-item_height,
                                        item_height ),
                                        myStyle)
                svgGroup.addElement(myText)
                cur_y = cur_y + item_height + INNER_PADDING
            self.svg.addElement(svgGroup)

    def _draw_events(self, view_properties):
        """Draw all event boxes and the text inside them."""
        myStyle = StyleBuilder()
        myStyle.setFontFamily(fontfamily="Verdana")
        myStyle.setFontSize("%d" % SMALL_FONT_SIZE)
        myStyle.setTextAnchor('left')
        oh = ShapeBuilder()
        for (event, rect) in self.scene.event_data:
            # Ensure that we can't draw outside rectangle
            # have one group per event
            svgGroup = g()
            # Ensure that we can't draw content outside inner rectangle
            boxColor = self._get_box_color(event)
            boxBorderColor = self._get_box_border_color(event)
            svgRect = oh.createRect(rect.X, rect.Y,
                                         rect.GetWidth(), rect.GetHeight(),
                                         stroke=boxBorderColor,
                                         fill=boxColor )
            if self.shadowFlag:
                svgRect.set_filter("url(#filterShadow)")
            svgGroup.addElement(svgRect)
            if rect.Width > 0:
                # Draw the text (if there is room for it)
                svgGroup.addElement(self._svg_clipped_text(event.text, rect.Get(), myStyle))
            # Draw data contents indicator
            if event.has_data():
                svgGroup.addElement(self._draw_contents_indicator(event, rect))
            self.svg.addElement(svgGroup)

    def _draw_contents_indicator(self, event, rect):
        """
        The data contents indicator is a small triangle drawn in the upper
        right corner of the event rectangle.
        """
        corner_x = rect.X + rect.Width
        polyPoints = "%d,%d %d,%d %d,%d" % \
            (corner_x - DATA_INDICATOR_SIZE, rect.Y,
             corner_x, rect.Y,
             corner_x, rect.Y + DATA_INDICATOR_SIZE)
        polyColor = self._get_box_indicator_color(event)
        oh = ShapeBuilder()
        indicator = oh.createPolygon(polyPoints,fill=polyColor,stroke=polyColor)
        # TODO (low): Transparency ?
        return indicator

    def _svg_clipped_text(self, myString, rectTuple, myStyle):
        myString = self._encode_text(myString)
        # Put text,clipping into a SVG group
        group=g()
        rx, ry, width, height = rectTuple
        text_x = rx + INNER_PADDING
        text_y = ry + height - INNER_PADDING
        # TODO: in SVG, negative value should be OK, but they
        # are not drawn in Firefox. So add a special handling here
        # however the root cause is the layout function for the recs
        # which should be fixed not to have values < 0
        if text_x < INNER_PADDING:
            width = width - (INNER_PADDING-text_x)
            text_x = INNER_PADDING
        pathId = "path%d_%d" % (text_x, text_y)
        p = path(pathData= "M %d %d H %d V %d H %d" % \
                               (rx, ry + height,
                                text_x+width-INNER_PADDING,
                                ry, rx))
        clip = clipPath()
        clip.addElement(p)
        clip.set_id(pathId)
        d=defs()
        d.addElement(clip)
        self.svg.addElement(d)
        myText = text( myString, text_x, text_y )
        myText.set_style(myStyle.getStyle())
        myText.set_textLength(width-2*INNER_PADDING)
        myText.set_lengthAdjust("spacingAndGlyphs")
        group.set_clip_path("url(#%s)" % pathId)

        group.addElement(myText)
        return group

    def _text(self, the_text, x, y):
        encoded_text = self._encode_text(the_text)
        return text(encoded_text, x, y)

    def _encode_text(self, text):
        return self._encode_unicode_text(xmlescape(text))

    def _encode_unicode_text(self, text):
        if type(text) is UnicodeType:
            return text.encode(ENCODING)
        else:
            return text
