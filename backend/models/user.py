from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    kullanici_adi: str
    sifre_hash: str
    rol: str  # "admin", "guvenlik", "sakin"
    
    # Sakin için
    site_id: Optional[str] = None
    blok_id: Optional[str] = None
    daire_id: Optional[str] = None
    
    aktif: bool = True
    olusturma_tarihi: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    kullanici_adi: str
    sifre: str
    rol: str
    site_id: Optional[str] = None
    blok_id: Optional[str] = None
    daire_id: Optional[str] = None

class UserLogin(BaseModel):
    kullanici_adi: str
    sifre: str