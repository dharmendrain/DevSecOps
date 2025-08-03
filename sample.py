#region IMPORT packages TEST

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER, inch, landscape, A4, A3, portrait
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.colors import Color
from reportlab.platypus import (BaseDocTemplate, SimpleDocTemplate,Frame, PageTemplate, 
                        NextPageTemplate, Paragraph, PageBreak, Image, Spacer, Table, TableStyle)
from reportlab.lib import colors
import json
from reportlab.lib.colors import PCMYKColor
from reportlab.graphics.shapes import Line, LineShape, Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.lib.validators import Auto
from random import randint
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.widgets.markers import makeMarker
from app.services.constant import *
import os
from pathlib import Path
from datetime import datetime
from reportlab.platypus.flowables import TopPadder
from reportlab.lib.units import cm
from app.model.item  import Item
from django.conf import settings
try:
    from django.utils import importlib
except ImportError:
    import importlib
#endregion

#region EXTRA PARAMETERS DEFINED 

page_height = 841
page_width = 595
table_width = 595

text_font_bold = 'Calibri-Bold'
text_font = 'Calibri'

color_workz_blue = Color((8/255), (84/255), (156/255), 1)
color_workz_text_blue = Color((30/255), (44/255), (68/255), 1)

colors_list = [Color(red=(79/255),green=(129/255),blue=(188/255)), 
                  Color(red=(192/255),green=(80/255),blue=(78/255)),
                  Color(red=(155/255),green=(187/255),blue=(88/255)), 
                  Color(red=(128/255),green=(100/255),blue=(161/255)), 
                  Color(red=(74/255),green=(172/255),blue=(197/255)), 
                  Color(red=(247/255),green=(150/255),blue=(72/255)), 
                  Color(red=(44/255),green=(77/255),blue=(255/255))]

colorWorkzBlue = Color((8/255), (84/255), (156/255), 1)
colorWorkzTextBlue = Color((32/255), (64/255), (100/255), 1)

#endregion
company_info = None

class FooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        self.width, self.height = portrait(A4) #landscape(A3)

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            if (self._pageNumber > 0): #if (self._pageNumber > 1):
                self.draw_canvas(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_canvas(self, page_count):
        page = "Page %s of %s" % (self._pageNumber, page_count)
        x = 65
        self.saveState()
        self.setStrokeColorRGB(0, 0, 0)
        self.setLineWidth(0.5)
        
        # if (self._pageNumber == 1): #if (self._pageNumber > 1):
        #         # self.drawImage("static/workz_background.png", 0, 0, width=792, height=612)
        #         pass
        # else:
        global company_info
        if (self._pageNumber == 1):
            self.drawImage(company_info.logo.path, self.width-inch*1-130, self.height-50, width=200, height=40, preserveAspectRatio=True)
        # self.drawImage(os.path.join(settings.MEDIA_ROOT, 'images\\logo.jpg'), self.width-inch*1-50, self.height-25, width=120, height=20, preserveAspectRatio=True)
        self.setFont('Times-Roman', 10)
        self.drawString(portrait(A4)[0]-x, 10, page)
            #self.drawString(landscape(A3)[0]-x, 10, page)

        # self.drawImage("static/ohka.png", self.width - inch * 2, self.height-50, width=100, height=30, preserveAspectRatio=True, mask='auto')
        # self.line(30, 740, LETTER[0] - 50, 740)
        # self.line(66, 78, LETTER[0] - 66, 78)
        self.restoreState()

class WorkProof:
    def __init__(self, path, work_list, invoice, company):
        self.path = path
        self.work_list = work_list
        self.invoice = invoice
        self.company = company
        global company_info
        company_info = self.company
        self.styleSheet = getSampleStyleSheet()
        self.elements = []

        self.invoice_header()
        self.invoice_header_detail()
        self.invoice_item()
        # self.invoice_bank()
        # self.invoice_terms()
        self.doc = SimpleDocTemplate(path, pagesize=portrait(A4))
        self.doc.multiBuild(self.elements, canvasmaker=FooterCanvas)

    def invoice_header(self):
        '''
        This will contaion invoice header and logo information
        '''
        spacer = Spacer(0, -80)
        self.elements.append(spacer)

        header_name = 'WORK PROOF'

        logo = 'logo path'
        data = [
                [header_name], 
                ]

        ts = [
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.black),
                ('VALIGN', (0, 0), (0, 0), 'MIDDLE'),
                ('FONTSIZE', (0, 0), (0, 0), 15),
                ('FONT', (0, 0), (0, 0), 'Times-Bold')
            ]
        t = Table(
                data, style=ts, colWidths = page_width, rowHeights = 20) #

        self.elements.append(t)

        spacer = Spacer(0, 10)
        self.elements.append(spacer)

    def invoice_item(self):
        data = [[u'No', u'Item', u'Image']]
        total_amount = 0
        row = 0
        for work in self.work_list:
            row = row + 1
            data.append([
                row,
                work.item.name + '\n' + ' ({} x {})'.format(work.w, work.h) + '\n' + work.item.code,
                Image(work.image.path, width=200, height=100),
                # Image(settings.PROJECT_DIR + work.image.url.replace('/','\\'), width=200, height=100),
            ])
            total_amount = total_amount + work.total_amount

        table = Table(data, colWidths=[1 * cm, 7 * cm, 11 * cm])
        table.setStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
            ('GRID', (0, 0), (-1, -1), 1, (0.7, 0.7, 0.7)),
            # ('GRID', (-2, -1), (-1, -1), 1, (0.7, 0.7, 0.7)),
            # ('FONT', (-2, -1), (-1, -1), 'Times-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
            ('FONT', (0, 0), (-1, 0), 'Times-Bold'),
        ])

        self.elements.append(table)

        spacer = Spacer(0, 10)
        self.elements.append(spacer)

    def invoice_header_detail(self):
        # drawing = Drawing(table_width/2, 400)
        # image = canvas.Canvas.drawImage(os.path.join(settings.MEDIA_ROOT, 'images\\logo.jpg'), 120, 25, y=10,width=120, height=20, preserveAspectRatio=True)
        # drawing.add(image)
        data = [[u'Invoice No', u':', self.invoice.invoice_number, u''], 
                [u'Invoice Date', u':', self.invoice.invoice_date.strftime("%d %B, %Y"), u''], 
                [u'Due Date', u':', self.invoice.due_date.strftime("%d %B, %Y"), u''], 
                [u'Work Date', u':', self.invoice.from_date.strftime("%d %B, %Y") + ' to ' + self.invoice.to_date.strftime("%d %B, %Y"), u''], 
                [u'', u'', u'', u''], 
                ]
        
        table = Table(data, colWidths=[2 * cm, 0.5 * cm, 7 * cm, 10 * cm])
        table.setStyle([
            ('FONT', (1, 0), (-1, -1), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
            # ('GRID', (0, 0), (-1, -2), 1, (0.7, 0.7, 0.7)),
            # ('GRID', (-2, -1), (-1, -1), 1, (0.7, 0.7, 0.7)),
            ('ALIGN', (-2, 0), (-1, -1), 'LEFT'),
            # ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
        ])
        self.elements.append(table)

        # self.elements.append(Image(os.path.join(settings.MEDIA_ROOT, 'images\\logo.jpg'), width=None, height=5))

        data = [[u'Billed By:', u'Billed To:'], 
                [self.company.name, self.invoice.client.parent_company],
                [self.company.address.replace('\r',''), self.invoice.client.address.replace('\r','')], 
                [u'GSTIN: {}'.format(self.company.gst_in), u'GSTIN: {}'.format(self.invoice.client.gst_in)], 
                [u'PAN: {}'.format(self.company.pan), u'PAN: {}'.format(self.invoice.client.pan)], 
                [u'Contact: {}'.format(self.company.contact), u'Contact: {}'.format(self.invoice.client.contact)], 
                ]
        
        table = Table(data, colWidths=[10 * cm, 9 * cm])
        table.setStyle([
            ('FONT', (0, 0), (1, 1), 'Times-Bold'),
            # ('FONT', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
            # ('GRID', (0, 0), (-1, -2), 1, (0.7, 0.7, 0.7)),
            # ('GRID', (-2, -1), (-1, -1), 1, (0.7, 0.7, 0.7)),
            # ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
            ('BACKGROUND', (0, 0), (-1, -1), (0.9, 0.9, 0.9)),
        ])
        self.elements.append(table)

        spacer = Spacer(0, 10)
        self.elements.append(spacer)

    def invoice_bank(self):
        data = [[u'Bank Details:', u'', u'', u''], 
                [u'Account Holder Name', u'2BRAINS', u'', u''], 
                [u'Account Number', u'0130102000037712', u'', u''], 
                [u'IFSC', u'IBKL0000130', u'', u''], 
                [u'Account Type', u'Current', u'', u''],
                [u'Bank', u'IDBI Bank', u'', u''], 
                ]
        
        table = Table(data, colWidths=[4 * cm, 2 * cm, 10 * cm, 3 * cm])
        table.setStyle([
            # ('FONT', (0, 0), (-1, -1), 'Helvetica'),
            ('FONT', (0, 0), (0, 0), 'Times-Bold'),
            ('FONT', (1, 0), (-1, -1), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
            ('BACKGROUND', (0, 0), (-1, -1), (0.9, 0.9, 0.9)),
            # ('GRID', (0, 0), (-1, -2), 1, (0.7, 0.7, 0.7)),
            # ('GRID', (-2, -1), (-1, -1), 1, (0.7, 0.7, 0.7)),
            # ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
            # ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
        ])
        self.elements.append(table)
        spacer = Spacer(0, 10)
        self.elements.append(spacer)

    def invoice_terms(self):
        data = [[u'Terms and Conditions:'], 
                [u'1. Please pay within 15 days from the date of invoice, overdue interest @ 14% will be charged on delayed payments.'], 
                [u'2. Please quote invoice number when remitting funds.'], 
                [u''], 
                [u'For any enquiry, reach out via email at bharat.designer11@gmail.com, call on +91 96622 95966'], 
                ]
        
        table = Table(data, colWidths=[19.5 * cm])
        table.setStyle([
            ('FONT', (0, 0), (0, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
            # ('GRID', (0, 0), (-1, -2), 1, (0.7, 0.7, 0.7)),
            # ('GRID', (-2, -1), (-1, -1), 1, (0.7, 0.7, 0.7)),
            # ('ALIGN', (-2, 0), (-1, -1), 'RIGHT'),
            # ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
            ('ALIGN', (0, 3), (-1, -1), 'CENTER'),
        ])
        self.elements.append(table)

    def firstpage_background(self):
            # report_header = self.data['report_header']

            spacer = Spacer(0, -85)
            self.elements.append(spacer)

            # I = Image('app/assets/workz_background.png')
            # I.drawHeight =685
            # I.drawWidth = page_width
            # self.elements.append(I)
            
            # P0 = Paragraph('''
            #        <b><font size=15 color=black>Remote SIM Provisioning Report</font></b>''',)

            spacer = Spacer(0, -530)
            self.elements.append(spacer)

            data = [
                ['Remote SIM Provisioning Report'], 
                ]

            ts = [
                # ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
                ('ALIGN', (-1, -1), (-1, -1), 'CENTER'),
                #  ('BACKGROUND', (0, -1), (-1, -1), colorWorkzBlue),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.white),
                ('VALIGN', (-1, -1), (-1, -1), 'MIDDLE'),
                # ('VALIGN', (0, 0), (-1, -1), 'TOP')
                # ('FONT', (-1, 1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (-1, -1), (-1, -1), 48),
                ('TEXTFONT', (-1, -1), (-1, -1), text_font_bold)
            ]
            t = Table(
                data, style=ts, colWidths = page_width, rowHeights = 60) #

            self.elements.append(t)

            spacer = Spacer(0, 100)
            self.elements.append(spacer)

            # data = [
            #     [report_header['tenant_name'] + ', '+ report_header['country']], 
            #     ]
            data = [
                ['tenant_name' + ', '+ 'country'], 
                ]
            ts = [
                # ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
                ('ALIGN', (-1, -1), (-1, -1), 'CENTER'),
                #  ('BACKGROUND', (0, -1), (-1, -1), colorWorkzBlue),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.black),
                ('VALIGN', (-1, -1), (-1, -1), 'MIDDLE'),
                # ('VALIGN', (0, 0), (-1, -1), 'TOP')
                # ('FONT', (-1, 1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (-1, -1), (-1, -1), 36),
                ('TEXTFONT', (-1, -1), (-1, -1), text_font_bold)
            ]
            t = Table(
                data, style=ts, colWidths = page_width, rowHeights = 40) #

            self.elements.append(t)

            spacer = Spacer(0, 80)
            self.elements.append(spacer)

            data = [
                ['from_date'], 
                ['to'], 
                ['to_date'], 
                ]

            ts = [
                # ('GRID', (0, 0), (-1, -1), 0.5, colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                #  ('BACKGROUND', (0, -1), (-1, -1), colorWorkzBlue),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                # ('VALIGN', (0, 0), (-1, -1), 'TOP')
                # ('FONT', (-1, 1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 22),
                ('TEXTFONT', (0, 0), (-1, -1), text_font_bold)
            ]
            t = Table(
                data, style=ts, colWidths = page_width, rowHeights = 30) #

            self.elements.append(t)

            self.elements.append(PageBreak())
