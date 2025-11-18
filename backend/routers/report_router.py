from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from services.pdf_generator import PDFReportGenerator
from typing import Optional
from datetime import datetime
import tempfile

router = APIRouter(prefix="/reports", tags=["Raporlama"])

db = None

def set_db(database):
    global db
    db = database

pdf_generator = PDFReportGenerator()

@router.get("/generate-pdf")
async def generate_pdf_report(
    baslangic_tarihi: Optional[str] = None,
    bitis_tarihi: Optional[str] = None,
    site_id: Optional[str] = None,
    durum: Optional[str] = None,
    kamera_id: Optional[str] = None
):
    """
    Filtrelenmiş logların PDF raporunu oluştur
    """
    query = {}
    
    if baslangic_tarihi or bitis_tarihi:
        query['tarih'] = {}
        if baslangic_tarihi:
            query['tarih']['$gte'] = baslangic_tarihi
        if bitis_tarihi:
            query['tarih']['$lte'] = bitis_tarihi
    
    if site_id:
        query['site_id'] = site_id
    if durum:
        query['durum'] = durum
    if kamera_id:
        query['kamera_id'] = kamera_id
    
    # Logları getir
    logs = await db.logs.find(query, {"_id": 0}).sort("tarih", -1).to_list(10000)
    
    for log in logs:
        if isinstance(log.get('tarih'), str):
            log['tarih'] = datetime.fromisoformat(log['tarih'])
    
    # Site logosu (varsa)
    settings = await db.settings.find_one({"id": "sistem_ayarlari"})
    logo_url = settings.get('site_logo_url') if settings else None
    
    # Geçici PDF dosyası oluştur
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.close()
    
    filters = {
        "baslangic": baslangic_tarihi or "Tümü",
        "bitis": bitis_tarihi or "Tümü"
    }
    
    try:
        pdf_path = pdf_generator.generate_log_report(
            filename=temp_file.name,
            logs=logs,
            filters=filters,
            logo_url=logo_url
        )
        
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=f"arac_gecis_raporu_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF oluşturulamadı: {str(e)}")

@router.get("/vehicle-type-stats")
async def get_vehicle_type_stats(
    baslangic_tarihi: Optional[str] = None,
    bitis_tarihi: Optional[str] = None
):
    """Araç tipi istatistikleri"""
    query = {}
    
    if baslangic_tarihi or bitis_tarihi:
        query['tarih'] = {}
        if baslangic_tarihi:
            query['tarih']['$gte'] = baslangic_tarihi
        if bitis_tarihi:
            query['tarih']['$lte'] = bitis_tarihi
    
    pipeline = [
        {"$match": query},
        {"$group": {
            "_id": "$arac_tipi",
            "adet": {"$sum": 1}
        }},
        {"$sort": {"adet": -1}}
    ]
    
    result = await db.logs.aggregate(pipeline).to_list(100)
    
    return [
        {
            "arac_tipi": item['_id'] or "Bilinmiyor",
            "adet": item['adet']
        }
        for item in result
    ]