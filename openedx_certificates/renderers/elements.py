# -*- coding: utf-8 -*-

import logging
import os
import copy
import settings

from reportlab.lib.pagesizes import landscape
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import reportlab.lib.enums as reportlab_enums

from openedx_certificates.renderers.util import apply_style_to_font_list
from openedx_certificates.renderers.util import autoscale_text
from openedx_certificates.renderers.util import font_for_string

logging.config.dictConfig(settings.LOGGING)
log = logging.getLogger('certificates.' + __name__)

TEMPLATE_DIR = settings.TEMPLATE_DIR

def draw_rect(_certificateGen, attributes, canvas, context=None):
    canvas.setLineWidth(attributes.get('stroke_width', 1))
    r,g,b = attributes.get('stroke_color', [0,0,0])
    canvas.setStrokeColorRGB(r,g,b)
    r,g,b = attributes.get('fill_color', [1,1,1])
    canvas.setFillColorRGB(r,g,b)
    canvas.rect(
        attributes.get('x', 0),
        attributes.get('y', 0),
        attributes.get('width', 0),
        attributes.get('height', 0),
        stroke=attributes.get('stroke', 1),
        fill=attributes.get('fill', 1),
    )

def draw_line(_certificateGen, attributes, canvas, context=None):
    canvas.setLineWidth(attributes.get('stroke_width', .5))
    r,g,b = attributes.get('stroke_color', [0,0,0])
    canvas.setStrokeColorRGB(r,g,b)
    canvas.line(
        attributes.get('x_start', 0),
        attributes.get('y_start', 0),
        attributes.get('x_end', 0),
        attributes.get('y_end', 0),
    )

def draw_image(_certificateGen, attributes, canvas, context=None):
    image_file = os.path.join(TEMPLATE_DIR, attributes.get('file', '/'))
    canvas.drawImage(
        image_file,
        attributes.get('x', 0),
        attributes.get('y', 0),
        attributes.get('width', 0),
        attributes.get('height', 0),
        mask='auto',
    )

def draw_text(certificateGen, attributes, canvas, context):
    string = unicode(attributes.get("string", ""))
    return _draw_text(certificateGen, attributes, canvas, string)

def draw_formatted_text(certificateGen, attributes, canvas, context):
    string = unicode(attributes.get("string", ""))
    string = string.format(**context)
    return _draw_text(certificateGen, attributes, canvas, string)

def _draw_text(certificateGen, attributes, canvas, string):
    alignment = attributes.get("alignment", "TA_LEFT")
    style_for_text = ParagraphStyle(
        name="text",
        fontSize=attributes.get("font_size", 12),
        leading=attributes.get("leading", 12),
        textColor=attributes.get("text_color", [0,0,0]),
        alignment=getattr(reportlab_enums, alignment, reportlab_enums.TA_LEFT),
    )
    (fonttag, fontfile, text_style) = font_for_string(
        apply_style_to_font_list(certificateGen.fontlist, style_for_text),
        string
    )
    paragraph = Paragraph(string, text_style)
    width, height = paragraph.wrapOn(canvas, attributes.get("width", 0), attributes.get("height", 0))
    paragraph.drawOn(canvas, attributes.get("x", 0), attributes.get("y", 0))

options = {
        "rectangle": draw_rect,
        "line": draw_line,
        "image": draw_image,
        "text": draw_text,
        "formatted_text": draw_formatted_text,
}

def draw_template_element(certificateGen, element, attributes, canvas, context=None):
    options[element](certificateGen, attributes, canvas, context=None)

def draw_instructor_element(certificateGen, instructor_attributes, instructor_template, canvas):
    x_position = instructor_attributes.get("x_position", 0)
    y_position = instructor_attributes.get("y_position", 0)
    for ordered_element in instructor_template:
        ordered_element_copy = copy.deepcopy(ordered_element)
        for element, attributes in ordered_element_copy.iteritems():
            x_offset = attributes.get('x_offset', 0)
            if element == "text":
                attributes['string'] = instructor_attributes.get(attributes.get("string", ""), "")
                attributes['x'] = x_position + x_offset
                attributes['y'] = y_position
                if attributes['string']:
                    y_position += attributes.get('height', 0)
            elif element == "image":
                attributes['file'] = instructor_attributes.get(attributes.get("file", ""), "")
                attributes['x'] = x_position + x_offset
                attributes['y'] = y_position - 10
                if attributes['file']:
                    y_position += attributes.get('height', 0)
            draw_template_element(certificateGen, element, attributes, canvas)
