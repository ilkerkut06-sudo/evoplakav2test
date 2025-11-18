from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid

class GecisLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plaka_no: str
    orijinal_plaka: Optional[str] = None  # AI düzeltme öncesi
    duzeltildi_mi: bool = False
    
    # Araç bilgileri
    arac_tipi: Optional[str] = "Bilinmiyor"
    
    # Konum bilgileri
    kamera_id: str
    kamera_adi: str
    kapi_id: Optional[str] = None
    kapi_adi: Optional[str] = None
    
    # Durum
    durum: str  # "Tanımlı", "Misafir", "Tanımsız", "Yasaklı"
    giris_cikis: str  # "Giriş", "Çıkış"
    
    # Sakin bilgileri (varsa)
    site_id: Optional[str] = None
    blok_id: Optional[str] = None
    daire_id: Optional[str] = None
    isim_soyisim: Optional[str] = None
    
    # Görsel
    fotograf_url: Optional[str] = None
    
    # Kapı kontrolü
    kapi_acildi_mi: bool = False
    
    tarih: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GecisLogCreate(BaseModel):
    plaka_no: str
    orijinal_plaka: Optional[str] = None
    duzeltildi_mi: bool = False
    arac_tipi: Optional[str] = "Bilinmiyor"
    kamera_id: str
    kamera_adi: str
    kapi_id: Optional[str] = None
    kapi_adi: Optional[str] = None
    durum: str
    giris_cikis: str
    site_id: Optional[str] = None
    blok_id: Optional[str] = None
    daire_id: Optional[str] = None
    isim_soyisim: Optional[str] = None
    fotograf_url: Optional[str] = None
    kapi_acildi_mi: bool = False