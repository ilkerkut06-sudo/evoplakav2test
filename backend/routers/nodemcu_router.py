from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from models.nodemcu import NodeMCU, NodeMCUCreate, NodeMCUUpdate
from services.nodemcu_controller import NodeMCUController
from typing import List
import os
from datetime import datetime

router = APIRouter(prefix="/nodemcu", tags=["NodeMCU/Kapı Yönetimi"])

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

controller = NodeMCUController()

@router.post("", response_model=NodeMCU)
async def create_nodemcu(nodemcu_input: NodeMCUCreate):
    # Aynı ID var mı?
    existing = await db.nodemcu.find_one({"nodemcu_id": nodemcu_input.nodemcu_id})
    if existing:
        raise HTTPException(status_code=400, detail="Bu NodeMCU ID zaten kayıtlı")
    
    nodemcu_dict = nodemcu_input.model_dump()
    nodemcu_obj = NodeMCU(**nodemcu_dict)
    doc = nodemcu_obj.model_dump()
    doc['olusturma_tarihi'] = doc['olusturma_tarihi'].isoformat()
    if doc.get('son_baglanti'):
        doc['son_baglanti'] = doc['son_baglanti'].isoformat()
    
    await db.nodemcu.insert_one(doc)
    return nodemcu_obj

@router.get("", response_model=List[NodeMCU])
async def get_nodemcu_devices():
    devices = await db.nodemcu.find({}, {"_id": 0}).to_list(1000)
    
    for device in devices:
        if isinstance(device.get('olusturma_tarihi'), str):
            device['olusturma_tarihi'] = datetime.fromisoformat(device['olusturma_tarihi'])
        if device.get('son_baglanti') and isinstance(device['son_baglanti'], str):
            device['son_baglanti'] = datetime.fromisoformat(device['son_baglanti'])
    
    return devices

@router.get("/{nodemcu_id}", response_model=NodeMCU)
async def get_nodemcu(nodemcu_id: str):
    device = await db.nodemcu.find_one({"id": nodemcu_id}, {"_id": 0})
    if not device:
        raise HTTPException(status_code=404, detail="NodeMCU bulunamadı")
    
    if isinstance(device.get('olusturma_tarihi'), str):
        device['olusturma_tarihi'] = datetime.fromisoformat(device['olusturma_tarihi'])
    if device.get('son_baglanti') and isinstance(device['son_baglanti'], str):
        device['son_baglanti'] = datetime.fromisoformat(device['son_baglanti'])
    
    return device

@router.put("/{nodemcu_id}", response_model=NodeMCU)
async def update_nodemcu(nodemcu_id: str, nodemcu_input: NodeMCUUpdate):
    update_data = {k: v for k, v in nodemcu_input.model_dump().items() if v is not None}
    
    result = await db.nodemcu.update_one(
        {"id": nodemcu_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="NodeMCU bulunamadı")
    
    return await get_nodemcu(nodemcu_id)

@router.delete("/{nodemcu_id}")
async def delete_nodemcu(nodemcu_id: str):
    result = await db.nodemcu.delete_one({"id": nodemcu_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="NodeMCU bulunamadı")
    return {"message": "NodeMCU silindi"}

@router.post("/{nodemcu_id}/open")
async def open_door(nodemcu_id: str):
    """Kapıyı manuel aç"""
    device = await db.nodemcu.find_one({"id": nodemcu_id})
    if not device:
        raise HTTPException(status_code=404, detail="NodeMCU bulunamadı")
    
    success = await controller.open_door(device['ip_adres'], device['nodemcu_id'])
    
    if success:
        # Son bağlantı zamanını güncelle
        await db.nodemcu.update_one(
            {"id": nodemcu_id},
            {"$set": {"son_baglanti": datetime.now().isoformat()}}
        )
        return {"message": "Kapı açıldı", "success": True}
    else:
        raise HTTPException(status_code=500, detail="Kapı açılamadı")

@router.get("/{nodemcu_id}/status")
async def check_nodemcu_status(nodemcu_id: str):
    """NodeMCU bağlantı durumunu kontrol et"""
    device = await db.nodemcu.find_one({"id": nodemcu_id})
    if not device:
        raise HTTPException(status_code=404, detail="NodeMCU bulunamadı")
    
    is_online = await controller.check_connection(device['ip_adres'])
    
    if is_online:
        await db.nodemcu.update_one(
            {"id": nodemcu_id},
            {"$set": {"son_baglanti": datetime.now().isoformat()}}
        )
    
    return {
        "online": is_online,
        "nodemcu_id": device['nodemcu_id'],
        "ip_adres": device['ip_adres']
    }