from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
import uuid

class Kamera(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    kamera_adi: str
    kamera_tipi: str  # "RTSP", "WEBCAM"
    giris_cikis: str  # "Giriş", "Çıkış", "Ortak"
    
    # RTSP için
    main_stream_url: Optional[str] = None
    sub_stream_url: Optional[str] = None
    
    # WEBCAM için
    webcam_index: Optional[int] = None  # 0, 1, 2, vs. - Birden fazla webcam desteği
    
    # ONVIF için
    onvif_ip: Optional[str] = None
    onvif_port: int = 80
    onvif_kullanici: Optional[str] = None
    onvif_sifre: Optional[str] = None
    
    # Kapı eşlemesi
    bagli_kapi_id: Optional[str] = None
    
    # Durum
    aktif: bool = True
    plaka_tanima_aktif: bool = True
    
    olusturma_tarihi: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KameraCreate(BaseModel):
    kamera_adi: str
    kamera_tipi: str
    giris_cikis: str
    main_stream_url: Optional[str] = None
    sub_stream_url: Optional[str] = None
    webcam_index: Optional[int] = None
    onvif_ip: Optional[str] = None
    onvif_port: int = 80
    onvif_kullanici: Optional[str] = None
    onvif_sifre: Optional[str] = None
    bagli_kapi_id: Optional[str] = None
    aktif: bool = True
    plaka_tanima_aktif: bool = True

class KameraUpdate(BaseModel):
    kamera_adi: Optional[str] = None
    giris_cikis: Optional[str] = None
    main_stream_url: Optional[str] = None
    sub_stream_url: Optional[str] = None
    onvif_ip: Optional[str] = None
    onvif_port: Optional[int] = None
    onvif_kullanici: Optional[str] = None
    onvif_sifre: Optional[str] = None
    bagli_kapi_id: Optional[str] = None
    aktif: Optional[bool] = None
    plaka_tanima_aktif: Optional[bool] = None