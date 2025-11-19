from fastapi import APIRouter, HTTPException
from models.settings import SistemAyarlari, SistemAyarlariUpdate
from datetime import datetime

router = APIRouter(prefix="/settings", tags=["Sistem Ayarları"])

db = None

def set_db(database):
    global db
    db = database

@router.get("", response_model=SistemAyarlari)
async def get_settings():
    settings = await db.settings.find_one({"id": "sistem_ayarlari"}, {"_id": 0})
    
    if not settings:
        # Varsayılan ayarlar oluştur
        default_settings = SistemAyarlari()
        doc = default_settings.model_dump()
        doc['guncelleme_tarihi'] = doc['guncelleme_tarihi'].isoformat()
        await db.settings.insert_one(doc)
        return default_settings
    
    if isinstance(settings.get('guncelleme_tarihi'), str):
        settings['guncelleme_tarihi'] = datetime.fromisoformat(settings['guncelleme_tarihi'])
    
    return settings

@router.put("", response_model=SistemAyarlari)
async def update_settings(settings_input: SistemAyarlariUpdate):
    update_data = {k: v for k, v in settings_input.model_dump().items() if v is not None}
    update_data['guncelleme_tarihi'] = datetime.now().isoformat()
    
    result = await db.settings.update_one(
        {"id": "sistem_ayarlari"},
        {"$set": update_data},
        upsert=True
    )
    
    return await get_settings()

@router.get("/system-status")
async def get_system_status():
    """Sistem motorlarının durumunu kontrol et (lightweight - modelleri yüklemeden)"""
    from services.system_monitor import SystemMonitor
    
    # Ayarları al
    settings_data = await db.settings.find_one({"id": "sistem_ayarlari"}, {"_id": 0})
    if not settings_data:
        settings_data = {"ocr_motor": "easyocr", "yolo_confidence": 0.5}
    
    # Sadece sistem kaynak kullanımı (ağır modelleri yüklemeyin!)
    monitor = SystemMonitor()
    system_status = monitor.get_system_status()
    
    return {
        "ocr": ocr_status,
        "yolo": yolo_status,
        "vehicle_classifier": classifier_status,
        "system": system_status,
        "ai_correction": {
            "enabled": settings_data.get('ai_duzeltme_aktif', True)
        },
        "night_mode": {
            "enabled": settings_data.get('gece_modu_aktif', False),
            "schedule": f"{settings_data.get('gece_modu_baslangic', '20:00')} - {settings_data.get('gece_modu_bitis', '06:00')}"
        }
    }