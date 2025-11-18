from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid

class Plaka(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plaka_no: str
    site_id: str
    blok_id: str
    daire_id: str
    arac_tipi: Optional[str] = "Bilinmiyor"  # Sedan, SUV, Kamyon vb.
    durum: str = "Tanımlı"  # Tanımlı, Misafir, Yasaklı
    gecerlilik_baslangic: Optional[datetime] = None  # Misafir için
    gecerlilik_bitis: Optional[datetime] = None  # Misafir için
    not_: Optional[str] = None
    olusturma_tarihi: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PlakaCreate(BaseModel):
    plaka_no: str
    site_id: str
    blok_id: str
    daire_id: str
    arac_tipi: Optional[str] = "Bilinmiyor"
    durum: str = "Tanımlı"
    gecerlilik_baslangic: Optional[datetime] = None
    gecerlilik_bitis: Optional[datetime] = None
    not_: Optional[str] = None
    # Daire bilgileri - Frontend'ten gönderilecek
    isim_soyisim: Optional[str] = None
    telefon: Optional[str] = None

class PlakaUpdate(BaseModel):
    plaka_no: Optional[str] = None
    site_id: Optional[str] = None
    blok_id: Optional[str] = None
    daire_id: Optional[str] = None
    arac_tipi: Optional[str] = None
    durum: Optional[str] = None
    gecerlilik_baslangic: Optional[datetime] = None
    gecerlilik_bitis: Optional[datetime] = None
    not_: Optional[str] = None
    # Daire bilgileri - Frontend'ten gönderilecek
    isim_soyisim: Optional[str] = None
    telefon: Optional[str] = None