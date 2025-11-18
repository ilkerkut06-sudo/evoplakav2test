from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone
import uuid

class Daire(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    daire_no: str
    isim_soyisim: str
    telefon: str
    not_: Optional[str] = None
    olusturma_tarihi: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DaireCreate(BaseModel):
    daire_no: str
    isim_soyisim: str
    telefon: str
    not_: Optional[str] = None

class Blok(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    blok_adi: str
    aciklama: Optional[str] = None
    daireler: List[Daire] = []
    olusturma_tarihi: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BlokCreate(BaseModel):
    blok_adi: str
    aciklama: Optional[str] = None

class Site(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    site_adi: str
    adres: str
    yonetici_adi: Optional[str] = None
    yonetici_telefon: Optional[str] = None
    logo_url: Optional[str] = None
    bloklar: List[Blok] = []
    olusturma_tarihi: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SiteCreate(BaseModel):
    site_adi: str
    adres: str
    yonetici_adi: Optional[str] = None
    yonetici_telefon: Optional[str] = None
    logo_url: Optional[str] = None