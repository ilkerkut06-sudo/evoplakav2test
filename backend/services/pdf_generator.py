from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from typing import List, Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)

class PDFReportGenerator:
    def __init__(self):
        # Türkçe karakter desteği için font kaydı (sistem fontlarını kullan)
        try:
            # Windows için Arial kullan (Türkçe karakter desteği var)
            if os.name == 'nt':
                pdfmetrics.registerFont(TTFont('Turkish', 'C:/Windows/Fonts/arial.ttf'))
            else:
                # Linux için alternatif
                pdfmetrics.registerFont(TTFont('Turkish', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
        except:
            logger.warning("Türkçe font yüklenemedi, varsayılan font kullanılacak")
    
    def generate_log_report(
        self,
        filename: str,
        logs: List[Dict],
        filters: Dict,
        logo_url: Optional[str] = None
    ) -> str:
        """
        Geçiş logları için PDF raporu oluştur
        Returns: PDF dosya yolu
        """
        try:
            doc = SimpleDocTemplate(filename, pagesize=A4)
            elements = []
            
            # Stil tanımları
            styles = getSampleStyleSheet()
            
            try:
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontName='Turkish',
                    fontSize=18,
                    textColor=colors.HexColor('#0ea5e9'),
                    alignment=TA_CENTER
                )
                
                normal_style = ParagraphStyle(
                    'CustomNormal',
                    parent=styles['Normal'],
                    fontName='Turkish',
                    fontSize=10
                )
            except:
                title_style = styles['Heading1']
                normal_style = styles['Normal']
            
            # Logo (varsa)
            if logo_url and os.path.exists(logo_url):
                try:
                    logo = Image(logo_url, width=3*cm, height=3*cm)
                    elements.append(logo)
                    elements.append(Spacer(1, 0.5*cm))
                except:
                    pass
            
            # Başlık
            title = Paragraph("Araç Geçiş Raporu", title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.5*cm))
            
            # Rapor bilgileri
            report_info = f"""Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}<br/>
            Tarih Aralığı: {filters.get('baslangic', 'Tümü')} - {filters.get('bitis', 'Tümü')}<br/>
            Toplam Kayıt: {len(logs)}"""
            
            info_para = Paragraph(report_info, normal_style)
            elements.append(info_para)
            elements.append(Spacer(1, 1*cm))
            
            # Tablo
            if logs:
                table_data = [['Plaka', 'Tarih', 'Saat', 'Durum', 'Araç Tipi', 'Kamera']]
                
                for log in logs:
                    tarih_obj = log.get('tarih')
                    if isinstance(tarih_obj, str):
                        tarih_obj = datetime.fromisoformat(tarih_obj)
                    
                    table_data.append([
                        log.get('plaka_no', '-'),
                        tarih_obj.strftime('%d.%m.%Y'),
                        tarih_obj.strftime('%H:%M'),
                        log.get('durum', '-'),
                        log.get('arac_tipi', '-'),
                        log.get('kamera_adi', '-')
                    ])
                
                table = Table(table_data, colWidths=[3*cm, 2.5*cm, 2*cm, 2.5*cm, 2.5*cm, 4*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0ea5e9')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
            else:
                no_data = Paragraph("Kayıt bulunamadı.", normal_style)
                elements.append(no_data)
            
            # PDF oluştur
            doc.build(elements)
            logger.info(f"PDF raporu oluşturuldu: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"PDF oluşturma hatası: {e}")
            raise
    
    def get_status(self) -> dict:
        """PDF generator durumunu döndür"""
        return {
            "initialized": True,
            "supported_formats": ["PDF"]
        }