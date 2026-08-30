#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CKM Catering — Luxury Gourmet Banquet Briefing PDF Generator
============================================================
Generates luxury dark-gold PDF banquet briefings showcasing high-end
Catering dishes, seasonal ingredients, and executive chef insights.
"""

import os
import sys as _sys, os as _os
# 2026-08-30 自 DevOps hub 遷入;report_paths.py 現在與本檔同層。
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from report_paths import report_dir  # noqa: E402
import sys
import json
import html
from datetime import datetime

import reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    sys.stderr.reconfigure(encoding='utf-8', errors='ignore')

# Brand Color Palette (Luxury Phnom Penh Catering)
COLOR_PRIMARY_DARK = "#111827"      # Deep Royal Black
COLOR_GOLD         = "#D4AF37"      # Metallic Gold
COLOR_GOLD_DARK    = "#996515"      # Dark Gold Line
COLOR_GOLD_LIGHT   = "#FEF9C3"      # Pale Gold Background
COLOR_TEXT_MAIN    = "#1F2937"      # Dark Charcoal
COLOR_TEXT_MUTED   = "#6B7280"      # Slate 500
COLOR_LINE         = "#E5E7EB"      # Light Border

def register_fonts():
    leela = "C:/Windows/Fonts/LeelawUI.ttf"
    leela_b = "C:/Windows/Fonts/LeelaUIb.ttf"
    if os.path.exists(leela) and os.path.exists(leela_b):
        try:
            pdfmetrics.registerFont(TTFont("LeelawUI", leela))
            pdfmetrics.registerFont(TTFont("LeelawUI-Bold", leela_b))
            return "LeelawUI", "LeelawUI-Bold"
        except Exception:
            pass
    khmer = "C:/Windows/Fonts/KhmerUI.ttf"
    khmer_b = "C:/Windows/Fonts/KhmerUIb.ttf"
    if os.path.exists(khmer) and os.path.exists(khmer_b):
        try:
            pdfmetrics.registerFont(TTFont("KhmerUI", khmer))
            pdfmetrics.registerFont(TTFont("KhmerUI-Bold", khmer_b))
            return "KhmerUI", "KhmerUI-Bold"
        except Exception:
            pass
    font_path = "C:/Windows/Fonts/msjh.ttc"
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont("MSJH", font_path, subfontIndex=0))
            pdfmetrics.registerFont(TTFont("MSJH-Bold", font_path, subfontIndex=1))
            return "MSJH", "MSJH-Bold"
        except Exception:
            pass
    return "Helvetica", "Helvetica-Bold"

def generate_ckm_branded_pdf(json_file_path=None, output_dir=None):
    font_name, font_bold = register_fonts()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    # 2026-08-30:原本寫死 C:\Projects\DevOps(hub 已刪除)。這個變數已無讀取端,
    
    # 但它曾經是「圖檔目錄找不到就靜默產出無圖 PDF」的來源之一,故一併移除。
    reports_ckm = os.path.join(devops_root, "Reports", "CKM")
    output_dir = output_dir or report_dir("CKM")   # 一天一個資料夾
    os.makedirs(output_dir, exist_ok=True)
    
    # 真本在 CKM repo,唯讀讀取。
    #
    # 原本讀的是 Reports/CKM/pulseData.json,而 2026-08-23 量到那份是轉存時代的快照:
    # 4 筆(本尊 37 筆)、最新 pulse-04(本尊 pulse-38)、4 筆的 image_url 全部指向
    # .webp 第三方照片,而那些照片同日已從兩個 repo 刪除。用它產出的簡報是拿 33 筆
    # 之前的資料配 4 個不存在的圖檔。
    #
    # DevOps 管站外,專案 repo 管站內(AGENTS.md §8-2)。hub 讀 repo,不持有副本。
    CKM_PULSE = os.path.join(r"C:\Projects\CKM", "src", "data", "pulseData.json")
    json_path = json_file_path or CKM_PULSE
    if not os.path.exists(json_path):
        print(f"[WARN] No pulseData.json found at {json_path}")
        return None
        
    with open(json_path, "r", encoding="utf-8") as f:
        pulse_items = json.load(f)
        
    if not pulse_items:
        print("[WARN] pulseData.json is empty.")
        return None

    out_filename = f"CKM_{today_str}_Catering_Gourmet_Briefing.pdf"
    out_pdf_path = os.path.join(output_dir, out_filename)
    downloads_pdf_path = out_pdf_path
    
    # Document Geometry
    page_w, page_h = A4
    margin = 16 * mm
    header_h = 25 * mm
    footer_h = 16 * mm
    
    styles = getSampleStyleSheet()
    
    st_title = ParagraphStyle(
        'CKMTitle', parent=styles['Normal'],
        fontName=font_bold, fontSize=15, leading=21,
        textColor=colors.HexColor(COLOR_PRIMARY_DARK), spaceAfter=4
    )
    st_sub = ParagraphStyle(
        'CKMSub', parent=styles['Normal'],
        fontName=font_name, fontSize=9, leading=13,
        textColor=colors.HexColor(COLOR_TEXT_MUTED), spaceAfter=8
    )
    st_dish_h = ParagraphStyle(
        'CKMDishH', parent=styles['Normal'],
        fontName=font_bold, fontSize=11, leading=15,
        textColor=colors.HexColor(COLOR_PRIMARY_DARK), spaceAfter=3
    )
    st_dish_sub = ParagraphStyle(
        'CKMDishSub', parent=styles['Normal'],
        fontName=font_name, fontSize=8.5, leading=12,
        textColor=colors.HexColor(COLOR_GOLD_DARK), spaceAfter=4
    )
    st_body = ParagraphStyle(
        'CKMBody', parent=styles['Normal'],
        fontName=font_name, fontSize=8, leading=12,
        textColor=colors.HexColor(COLOR_TEXT_MAIN), spaceAfter=4
    )
    
    def draw_furniture(canvas, doc):
        canvas.saveState()
        # Top Header Bar
        canvas.setFillColor(colors.HexColor(COLOR_PRIMARY_DARK))
        canvas.rect(0, page_h - header_h, page_w, header_h, stroke=0, fill=1)
        # Gold Accent Line
        canvas.setFillColor(colors.HexColor(COLOR_GOLD))
        canvas.rect(0, page_h - header_h - 1.8, page_w, 1.8, stroke=0, fill=1)
        
        # Header Text
        y_mid = page_h - header_h / 2
        canvas.setFillColor(colors.HexColor(COLOR_GOLD))
        canvas.setFont(font_bold, 13)
        canvas.drawString(margin, y_mid + 1.2 * mm, "CKM CATERING ｜ 金邊頂級外燴與高端宴席")
        canvas.setFillColor(colors.HexColor("#D1D5DB"))
        canvas.setFont(font_name, 8)
        canvas.drawString(margin, y_mid - 4.5 * mm, "星級粵菜私廚 ｜ 名流婚宴 ｜ 跨國企業年會 ｜ 食材旬味特刊")
        
        canvas.setFillColor(colors.white)
        canvas.setFont(font_name, 9)
        canvas.drawRightString(page_w - margin, y_mid - 1 * mm, f"BRIEFING: {today_str}")
        
        # Footer
        fy = 10 * mm
        canvas.setStrokeColor(colors.HexColor(COLOR_LINE))
        canvas.setLineWidth(0.5)
        canvas.line(margin, fy + 4 * mm, page_w - margin, fy + 4 * mm)
        canvas.setFillColor(colors.HexColor(COLOR_TEXT_MUTED))
        canvas.setFont(font_name, 7.5)
        canvas.drawString(margin, fy, "ckmkh.com ｜ 柬埔寨金邊最高規格外燴服務 ｜ 貴賓專屬菜單與主廚洞察")
        canvas.drawRightString(page_w - margin, fy, f"Page {doc.page}")
        canvas.restoreState()

    frame = Frame(margin, footer_h, page_w - 2 * margin, page_h - header_h - footer_h - 4 * mm,
                  id='main_frame', leftPadding=0, rightPadding=0, topPadding=8, bottomPadding=0)
    
    doc = BaseDocTemplate(out_pdf_path, pagesize=A4,
                          title=f"CKM 頂級外燴特刊 {today_str}",
                          author="CKM Catering",
                          subject="金邊高端外燴與宴席菜單特刊")
    doc.addPageTemplates([PageTemplate(id='ckm_template', frames=[frame], onPage=draw_furniture)])
    
    story = []
    
    story.append(Paragraph("金邊名流宴席與星級主廚旬味洞察 (Gourmet Banquet Briefing)", st_title))
    story.append(Paragraph("本特刊精選金邊高端婚宴（ម្ហូបការ）、企業商務外燴與名流私宴之時令頂級食材工法與美饌故事。", st_sub))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(COLOR_GOLD), spaceAfter=8))
    
    images_dir = os.path.join(reports_ckm, "images")
    
    for idx, item in enumerate(pulse_items[:6], 1):
        source_title_en = item.get("source_title_en", "")
        dish_title_km = item.get("title_km", "星級美饌")
        summary_km = item.get("summary_km", "")
        img_url = item.get("image_url", "")
        
        # Format local image
        img_flowable = None
        if img_url:
            local_img_name = os.path.basename(img_url)
            local_img_path = os.path.join(images_dir, local_img_name)
            if os.path.exists(local_img_path):
                try:
                    img_flowable = RLImage(local_img_path, width=42 * mm, height=30 * mm)
                except Exception:
                    img_flowable = None
                    
        url = (item.get("url") or item.get("source_link") or item.get("link") or "").strip()
        header_label = f"【美饌 {idx:02d}】 {html.escape(source_title_en)}" if source_title_en else f"【美饌 {idx:02d}】"
        if url:
            desc_text = f'<b>{header_label}</b><br/><a href="{html.escape(url)}"><font color="#B45309"><u>{html.escape(dish_title_km)}</u></font></a>'
        else:
            desc_text = f"<b>{header_label}</b><br/>{html.escape(dish_title_km)}"
        desc_para = Paragraph(desc_text, st_dish_h)
        summary_para = Paragraph(f"<b>工法與主廚筆記：</b><br/>{html.escape(summary_km)}", st_body)
        
        # 2-column dish card layout
        content_cell = [desc_para, summary_para]
        
        if img_flowable:
            card_data = [[img_flowable, content_cell]]
            col_widths = [45 * mm, (page_w - 2 * margin) - 47 * mm]
        else:
            card_data = [[content_cell]]
            col_widths = [page_w - 2 * margin]
            
        card_table = Table(card_data, colWidths=col_widths)
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FAFAFA")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor(COLOR_GOLD)),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(card_table)
        story.append(Spacer(1, 6))

    os.makedirs(output_dir, exist_ok=True)
    try:
        doc.build(story)
        print(f"[SUCCESS] CKM Catering Luxury Gourmet Briefing PDF Generated: {out_pdf_path} ({os.path.getsize(out_pdf_path)/1024:.1f} KB)")
    except PermissionError:
        print(f"[WARN] 檔案目前正被 PDF 檢視器開啟鎖定中: {out_pdf_path} (請關閉檢視器即可覆寫)")
    return out_pdf_path

if __name__ == "__main__":
    raise SystemExit(0 if generate_ckm_branded_pdf() else 1)
