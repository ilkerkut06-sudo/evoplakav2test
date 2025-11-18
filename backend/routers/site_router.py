from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from models.site import Site, SiteCreate, Blok, BlokCreate, Daire, DaireCreate
from typing import List
import os
from datetime import datetime

router = APIRouter(prefix="/sites", tags=["Site Yönetimi"])

# MongoDB bağlantısı
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# ===== SİTE CRUD =====
@router.post("", response_model=Site)
async def create_site(site_input: SiteCreate):
    site_dict = site_input.model_dump()
    site_obj = Site(**site_dict)
    doc = site_obj.model_dump()
    doc['olusturma_tarihi'] = doc['olusturma_tarihi'].isoformat()
    await db.sites.insert_one(doc)
    return site_obj

@router.get("", response_model=List[Site])
async def get_sites():
    sites = await db.sites.find({}, {"_id": 0}).to_list(1000)
    for site in sites:
        if isinstance(site.get('olusturma_tarihi'), str):
            site['olusturma_tarihi'] = datetime.fromisoformat(site['olusturma_tarihi'])
        # Blok ve daire tarihlerini dönüştür
        for blok in site.get('bloklar', []):
            if isinstance(blok.get('olusturma_tarihi'), str):
                blok['olusturma_tarihi'] = datetime.fromisoformat(blok['olusturma_tarihi'])
            for daire in blok.get('daireler', []):
                if isinstance(daire.get('olusturma_tarihi'), str):
                    daire['olusturma_tarihi'] = datetime.fromisoformat(daire['olusturma_tarihi'])
    return sites

@router.get("/{site_id}", response_model=Site)
async def get_site(site_id: str):
    site = await db.sites.find_one({"id": site_id}, {"_id": 0})
    if not site:
        raise HTTPException(status_code=404, detail="Site bulunamadı")
    if isinstance(site.get('olusturma_tarihi'), str):
        site['olusturma_tarihi'] = datetime.fromisoformat(site['olusturma_tarihi'])
    return site

@router.put("/{site_id}", response_model=Site)
async def update_site(site_id: str, site_input: SiteCreate):
    update_data = site_input.model_dump()
    result = await db.sites.update_one(
        {"id": site_id},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Site bulunamadı")
    return await get_site(site_id)

@router.delete("/{site_id}")
async def delete_site(site_id: str):
    result = await db.sites.delete_one({"id": site_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Site bulunamadı")
    return {"message": "Site silindi"}

# ===== BLOK CRUD =====
@router.post("/{site_id}/bloklar", response_model=Blok)
async def add_blok(site_id: str, blok_input: BlokCreate):
    site = await db.sites.find_one({"id": site_id})
    if not site:
        raise HTTPException(status_code=404, detail="Site bulunamadı")
    
    blok_dict = blok_input.model_dump()
    blok_obj = Blok(**blok_dict)
    blok_doc = blok_obj.model_dump()
    blok_doc['olusturma_tarihi'] = blok_doc['olusturma_tarihi'].isoformat()
    
    await db.sites.update_one(
        {"id": site_id},
        {"$push": {"bloklar": blok_doc}}
    )
    return blok_obj

@router.put("/{site_id}/bloklar/{blok_id}", response_model=Blok)
async def update_blok(site_id: str, blok_id: str, blok_input: BlokCreate):
    update_data = blok_input.model_dump()
    result = await db.sites.update_one(
        {"id": site_id, "bloklar.id": blok_id},
        {"$set": {
            "bloklar.$.blok_adi": update_data['blok_adi'],
            "bloklar.$.aciklama": update_data.get('aciklama')
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Blok bulunamadı")
    
    site = await db.sites.find_one({"id": site_id})
    blok = next((b for b in site['bloklar'] if b['id'] == blok_id), None)
    if isinstance(blok.get('olusturma_tarihi'), str):
        blok['olusturma_tarihi'] = datetime.fromisoformat(blok['olusturma_tarihi'])
    return blok

@router.delete("/{site_id}/bloklar/{blok_id}")
async def delete_blok(site_id: str, blok_id: str):
    result = await db.sites.update_one(
        {"id": site_id},
        {"$pull": {"bloklar": {"id": blok_id}}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Blok bulunamadı")
    return {"message": "Blok silindi"}

# ===== DAİRE CRUD =====
@router.post("/{site_id}/bloklar/{blok_id}/daireler", response_model=Daire)
async def add_daire(site_id: str, blok_id: str, daire_input: DaireCreate):
    daire_dict = daire_input.model_dump()
    daire_obj = Daire(**daire_dict)
    daire_doc = daire_obj.model_dump()
    daire_doc['olusturma_tarihi'] = daire_doc['olusturma_tarihi'].isoformat()
    
    result = await db.sites.update_one(
        {"id": site_id, "bloklar.id": blok_id},
        {"$push": {"bloklar.$.daireler": daire_doc}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Site/Blok bulunamadı")
    return daire_obj

@router.put("/{site_id}/bloklar/{blok_id}/daireler/{daire_id}")
async def update_daire(site_id: str, blok_id: str, daire_id: str, daire_input: DaireCreate):
    update_data = daire_input.model_dump()
    
    # MongoDB array update için pozisyon bulma
    site = await db.sites.find_one({"id": site_id})
    if not site:
        raise HTTPException(status_code=404, detail="Site bulunamadı")
    
    for i, blok in enumerate(site.get('bloklar', [])):
        if blok['id'] == blok_id:
            for j, daire in enumerate(blok.get('daireler', [])):
                if daire['id'] == daire_id:
                    await db.sites.update_one(
                        {"id": site_id},
                        {"$set": {
                            f"bloklar.{i}.daireler.{j}.daire_no": update_data['daire_no'],
                            f"bloklar.{i}.daireler.{j}.isim_soyisim": update_data['isim_soyisim'],
                            f"bloklar.{i}.daireler.{j}.telefon": update_data['telefon'],
                            f"bloklar.{i}.daireler.{j}.not_": update_data.get('not_')
                        }}
                    )
                    return {"message": "Daire güncellendi"}
    
    raise HTTPException(status_code=404, detail="Daire bulunamadı")

@router.delete("/{site_id}/bloklar/{blok_id}/daireler/{daire_id}")
async def delete_daire(site_id: str, blok_id: str, daire_id: str):
    site = await db.sites.find_one({"id": site_id})
    if not site:
        raise HTTPException(status_code=404, detail="Site bulunamadı")
    
    for i, blok in enumerate(site.get('bloklar', [])):
        if blok['id'] == blok_id:
            await db.sites.update_one(
                {"id": site_id},
                {"$pull": {f"bloklar.{i}.daireler": {"id": daire_id}}}
            )
            return {"message": "Daire silindi"}
    
    raise HTTPException(status_code=404, detail="Blok bulunamadı")