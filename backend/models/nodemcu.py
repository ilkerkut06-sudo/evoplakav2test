from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid

class NodeMCU(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nodemcu_id: str  # Cihaz ID
    ip_adres: str
    kapi_adi: str
    endpoint_url: str = "/kapiac"  # Kapı açma endpoint'i
    aciklama: Optional[str] = None
    aktif: bool = True
    son_baglanti: Optional[datetime] = None
    olusturma_tarihi: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NodeMCUCreate(BaseModel):
    nodemcu_id: str
    ip_adres: str
    kapi_adi: str
    endpoint_url: str = "/kapiac"
    aciklama: Optional[str] = None
    aktif: bool = True

class NodeMCUUpdate(BaseModel):
    nodemcu_id: Optional[str] = None
    ip_adres: Optional[str] = None
    kapi_adi: Optional[str] = None
    endpoint_url: Optional[str] = None
    aciklama: Optional[str] = None
    aktif: Optional[bool] = None