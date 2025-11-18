from fastapi import APIRouter, HTTPException
from models.plate import Plaka, PlakaCreate, PlakaUpdate
from typing import List, Optional
from datetime import datetime, timezone

router = APIRouter(prefix="/plates", tags=["Plaka Yönetimi"])

db = None

def set_db(database):
    global db
    db = database

@router.post("", response_model=Plaka)
async def create_plate(plate_input: PlakaCreate):
    # Aynı daireye maksimum 3 plaka kontrolü
    existing_plates = await db.plates.count_documents({
        "daire_id": plate_input.daire_id
    })
    
    if existing_plates >= 3:
        raise HTTPException(status_code=400, detail="Bir daireye maksimum 3 plaka eklenebilir")
    
    # Aynı plaka var mı?
    duplicate = await db.plates.find_one({"plaka_no": plate_input.plaka_no})
    if duplicate:
        raise HTTPException(status_code=400, detail="Bu plaka zaten kayıtlı")
    
    plate_dict = plate_input.model_dump()
    plate_obj = Plaka(**plate_dict)
    doc = plate_obj.model_dump()
    
    # Tarihleri ISO formatına çevir
    doc['olusturma_tarihi'] = doc['olusturma_tarihi'].isoformat()
    if doc.get('gecerlilik_baslangic'):
        doc['gecerlilik_baslangic'] = doc['gecerlilik_baslangic'].isoformat()
    if doc.get('gecerlilik_bitis'):
        doc['gecerlilik_bitis'] = doc['gecerlilik_bitis'].isoformat()
    
    await db.plates.insert_one(doc)
    return plate_obj

@router.get("", response_model=List[Plaka])
async def get_plates(site_id: Optional[str] = None, daire_id: Optional[str] = None):
    query = {}
    if site_id:
        query['site_id'] = site_id
    if daire_id:
        query['daire_id'] = daire_id
    
    plates = await db.plates.find(query, {"_id": 0}).to_list(10000)
    
    for plate in plates:
        if isinstance(plate.get('olusturma_tarihi'), str):
            plate['olusturma_tarihi'] = datetime.fromisoformat(plate['olusturma_tarihi'])
        if plate.get('gecerlilik_baslangic') and isinstance(plate['gecerlilik_baslangic'], str):
            plate['gecerlilik_baslangic'] = datetime.fromisoformat(plate['gecerlilik_baslangic'])
        if plate.get('gecerlilik_bitis') and isinstance(plate['gecerlilik_bitis'], str):
            plate['gecerlilik_bitis'] = datetime.fromisoformat(plate['gecerlilik_bitis'])
    
    return plates

@router.get("/{plate_id}", response_model=Plaka)
async def get_plate(plate_id: str):
    plate = await db.plates.find_one({"id": plate_id}, {"_id": 0})
    if not plate:
        raise HTTPException(status_code=404, detail="Plaka bulunamadı")
    
    if isinstance(plate.get('olusturma_tarihi'), str):
        plate['olusturma_tarihi'] = datetime.fromisoformat(plate['olusturma_tarihi'])
    if plate.get('gecerlilik_baslangic') and isinstance(plate['gecerlilik_baslangic'], str):
        plate['gecerlilik_baslangic'] = datetime.fromisoformat(plate['gecerlilik_baslangic'])
    if plate.get('gecerlilik_bitis') and isinstance(plate['gecerlilik_bitis'], str):
        plate['gecerlilik_bitis'] = datetime.fromisoformat(plate['gecerlilik_bitis'])
    
    return plate

@router.get("/check/{plate_no}")
async def check_plate(plate_no: str):
    """Plaka durumunu kontrol et"""
    plate = await db.plates.find_one({"plaka_no": plate_no}, {"_id": 0})
    
    if not plate:
        return {
            "found": False,
            "durum": "Tanımsız",
            "plaka_no": plate_no
        }
    
    # Geçerlilik kontrolü (misafir için)
    if plate['durum'] == 'Misafir':
        now = datetime.now(timezone.utc)
        
        baslangic = plate.get('gecerlilik_baslangic')
        bitis = plate.get('gecerlilik_bitis')
        
        if baslangic and isinstance(baslangic, str):
            baslangic = datetime.fromisoformat(baslangic)
        if bitis and isinstance(bitis, str):
            bitis = datetime.fromisoformat(bitis)
        
        if bitis and now > bitis:
            return {
                "found": True,
                "durum": "Süresi Dolmuş",
                "plaka_no": plate_no,
                "data": plate
            }
    
    return {
        "found": True,
        "durum": plate['durum'],
        "plaka_no": plate_no,
        "data": plate
    }

@router.put("/{plate_id}", response_model=Plaka)
async def update_plate(plate_id: str, plate_input: PlakaUpdate):
    update_data = {k: v for k, v in plate_input.model_dump().items() if v is not None}
    
    # Tarihleri ISO formatına çevir
    if update_data.get('gecerlilik_baslangic'):
        update_data['gecerlilik_baslangic'] = update_data['gecerlilik_baslangic'].isoformat()
    if update_data.get('gecerlilik_bitis'):
        update_data['gecerlilik_bitis'] = update_data['gecerlilik_bitis'].isoformat()
    
    result = await db.plates.update_one(
        {"id": plate_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plaka bulunamadı")
    
    return await get_plate(plate_id)

@router.delete("/{plate_id}")
async def delete_plate(plate_id: str):
    result = await db.plates.delete_one({"id": plate_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plaka bulunamadı")
    return {"message": "Plaka silindi"}