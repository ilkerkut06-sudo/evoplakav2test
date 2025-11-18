from fastapi import APIRouter, HTTPException, Query
from models.log import GecisLog, GecisLogCreate
from typing import List, Optional
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/logs", tags=["Geçiş Logları"])

db = None

def set_db(database):
    global db
    db = database

@router.post("", response_model=GecisLog)
async def create_log(log_input: GecisLogCreate):
    log_dict = log_input.model_dump()
    log_obj = GecisLog(**log_dict)
    doc = log_obj.model_dump()
    doc['tarih'] = doc['tarih'].isoformat()
    
    await db.logs.insert_one(doc)
    return log_obj

@router.get("", response_model=List[GecisLog])
async def get_logs(
    limit: int = Query(default=20, le=1000),
    skip: int = 0,
    plaka_no: Optional[str] = None,
    durum: Optional[str] = None,
    kamera_id: Optional[str] = None,
    baslangic_tarihi: Optional[str] = None,
    bitis_tarihi: Optional[str] = None
):
    query = {}
    
    if plaka_no:
        query['plaka_no'] = plaka_no
    if durum:
        query['durum'] = durum
    if kamera_id:
        query['kamera_id'] = kamera_id
    
    # Tarih aralığı filtresi
    if baslangic_tarihi or bitis_tarihi:
        query['tarih'] = {}
        if baslangic_tarihi:
            query['tarih']['$gte'] = baslangic_tarihi
        if bitis_tarihi:
            query['tarih']['$lte'] = bitis_tarihi
    
    logs = await db.logs.find(query, {"_id": 0}).sort("tarih", -1).skip(skip).limit(limit).to_list(limit)
    
    for log in logs:
        if isinstance(log.get('tarih'), str):
            log['tarih'] = datetime.fromisoformat(log['tarih'])
    
    return logs

@router.get("/stats")
async def get_stats():
    """Genel istatistikler"""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Bugünkü girişler
    today_count = await db.logs.count_documents({
        "tarih": {"$gte": today_start.isoformat()}
    })
    
    # Bu ayki girişler
    month_count = await db.logs.count_documents({
        "tarih": {"$gte": month_start.isoformat()}
    })
    
    # Bugünkü misafirler
    today_guests = await db.logs.count_documents({
        "tarih": {"$gte": today_start.isoformat()},
        "durum": "Misafir"
    })
    
    # Yasaklı araç denemeleri
    blocked_attempts = await db.logs.count_documents({
        "durum": "Yasaklı"
    })
    
    # Toplam kayıtlı araç
    total_vehicles = await db.plates.count_documents({})
    
    # Online kamera sayısı
    online_cameras = await db.cameras.count_documents({"aktif": True})
    
    return {
        "bugun_giris": today_count,
        "bu_ay_giris": month_count,
        "bugun_misafir": today_guests,
        "yasakli_denemesi": blocked_attempts,
        "toplam_arac": total_vehicles,
        "online_kamera": online_cameras
    }

@router.get("/kapi-stats")
async def get_door_stats():
    """Kapı bazlı istatistikler"""
    pipeline = [
        {"$group": {
            "_id": "$kapi_adi",
            "toplam_gecis": {"$sum": 1}
        }},
        {"$sort": {"toplam_gecis": -1}}
    ]
    
    result = await db.logs.aggregate(pipeline).to_list(100)
    
    return [
        {
            "kapi_adi": item['_id'] or "Bilinmeyen",
            "toplam_gecis": item['toplam_gecis']
        }
        for item in result
    ]

@router.get("/recent-ticker")
async def get_recent_ticker(limit: int = 10):
    """Canlı akış için son olaylar"""
    logs = await db.logs.find({}, {"_id": 0}).sort("tarih", -1).limit(limit).to_list(limit)
    
    for log in logs:
        if isinstance(log.get('tarih'), str):
            log['tarih'] = datetime.fromisoformat(log['tarih'])
    
    return logs