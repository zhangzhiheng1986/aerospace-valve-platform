# -*- coding: utf-8 -*-
"""PDF export for process routes (work instructions)."""
import io
import hashlib

# Monkey-patch hashlib.md5 for reportlab compatibility (Python 3.8 + OpenSSL)
_orig_md5 = hashlib.md5
def _md5_compat(*args, **kwargs):
    kwargs.pop('usedforsecurity', None)
    return _orig_md5(*args, **kwargs)
hashlib.md5 = _md5_compat

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

# Register CJK font (built-in to reportlab)
try:
    pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
    CJK_FONT = 'STSong-Light'
except Exception:
    CJK_FONT = 'Helvetica'


def _format_value(v):
    if v is None or v == '':
        return '-'
    if isinstance(v, list) and len(v) == 2 and isinstance(v[0], (int, float)):
        return f'{v[0]} ~ {v[1]}'
    if isinstance(v, bool):
        return 'Yes' if v else 'No'
    return str(v)


def export_process_pdf(process_id):
    """Export a single process card to PDF."""
    from valve_process import get_process_detail
    data = get_process_detail(process_id)
    if data is None:
        return None, None

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title', parent=styles['Title'],
        fontName=CJK_FONT, fontSize=18, textColor=colors.HexColor('#0b3d91'),
        spaceAfter=10,
    )
    h2 = ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontName=CJK_FONT, fontSize=13, textColor=colors.HexColor('#1a5490'),
        spaceAfter=6, spaceBefore=10,
    )
    body = ParagraphStyle(
        'Body', parent=styles['BodyText'],
        fontName=CJK_FONT, fontSize=10, leading=14,
    )
    story = []
    story.append(Paragraph(f"Process Card / 工艺卡片: {data['name']}", title_style))
    story.append(Paragraph(f"ID: <font name='Courier'>{process_id}</font> | "
                          f"Category: {data['category']}", body))
    story.append(Paragraph(f"Standard: {data.get('std', '-')}", body))
    story.append(Paragraph(f"Applicability: {data.get('applicability', '-')}", body))
    story.append(Spacer(1, 6))
    # Param table
    story.append(Paragraph("Parameters / 工艺参数", h2))
    skip = {'id', 'name', 'category', 'std', 'applicability'}
    rows = [['Parameter', 'Value']]
    for k, v in data.items():
        if k in skip:
            continue
        lbl = k.replace('_', ' ').title()
        val = _format_value(v)
        rows.append([lbl, val])
    t = Table(rows, colWidths=[55 * mm, 110 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b3d91')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), CJK_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))
    story.append(Paragraph("Avis Aerospace Valve R&D Platform / 航天阀门研发平台", body))
    doc.build(story)
    buf.seek(0)
    filename = f"process_{process_id}.pdf"
    return buf, filename


def export_route_pdf(route_id):
    """Export a process route to PDF (work instruction)."""
    from valve_process import get_process_route
    data = get_process_route(route_id)
    if data is None:
        return None, None

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=15 * mm, rightMargin=15 * mm,
                            topMargin=15 * mm, bottomMargin=15 * mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title', parent=styles['Title'],
        fontName=CJK_FONT, fontSize=18, textColor=colors.HexColor('#0b3d91'),
        spaceAfter=8,
    )
    h2 = ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontName=CJK_FONT, fontSize=12, textColor=colors.HexColor('#1a5490'),
        spaceAfter=4, spaceBefore=8,
    )
    body = ParagraphStyle(
        'Body', parent=styles['BodyText'],
        fontName=CJK_FONT, fontSize=9, leading=12,
    )
    story = []
    story.append(Paragraph(f"Work Instruction / 作业指导书: {data['name']}", title_style))
    info = (f"Route ID: <font name='Courier'>{route_id}</font> | "
            f"Material: {data['material']} | "
            f"Steps: {data['steps']} | Total Time: {data['total_time_h']} h ({data['total_time_min']} min)")
    story.append(Paragraph(info, body))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Operation Sequence / 工序列表", h2))
    rows = [['#', 'Process', 'Method', 'Equipment', 'Time (min)']]
    for op in data['operations']:
        rows.append([
            str(op['step']),
            op['process'],
            op['method'],
            op['equipment'],
            str(op['time_min']),
        ])
    t = Table(rows, colWidths=[10 * mm, 35 * mm, 60 * mm, 35 * mm, 20 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0b3d91')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), CJK_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))
    # Quality / NDT notes
    story.append(Paragraph("Quality Requirements / 质量要求", h2))
    story.append(Paragraph(
        "1. 100% visual + dimensional check per QJ 20156", body))
    story.append(Paragraph(
        "2. NDT (UT/PT) for critical surfaces per material/standard", body))
    story.append(Paragraph(
        "3. Cleanliness per GJB 420B for sealed systems", body))
    story.append(Paragraph(
        "4. 100% leak test at 1.5x working pressure, leak rate < 1E-9 Pa.m3/s", body))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Avis Aerospace Valve R&D Platform / 航天阀门研发平台 | "
        "Generated " + _now_str(), body))
    doc.build(story)
    buf.seek(0)
    filename = f"route_{route_id}.pdf"
    return buf, filename


def _now_str():
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M')
