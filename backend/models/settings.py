from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

class SistemAyarlari(BaseModel):
    id: str = "sistem_ayarlari"  # Tek kayıt
    
    # OCR Motor
    ocr_motor: str = "paddleocr"  # "paddleocr" veya "easyocr"
    
    # AI Plaka Düzeltme
    ai_duzeltme_aktif: bool = True
    
    # Gece Modu
    gece_modu_aktif: bool = False
    gece_modu_baslangic: str = "20:00"
    gece_modu_bitis: str = "06:00"
    
    # Görüntü İşleme
    yolo_confidence: float = 0.5
    ocr_confidence: float = 0.6
    
    # Gece profili ayarları
    gece_brightness: float = 1.2
    gece_contrast: float = 1.3
    
    # Site logosu
    site_logo_url: Optional[str] = None
    
    guncelleme_tarihi: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SistemAyarlariUpdate(BaseModel):
    ocr_motor: Optional[str] = None
    ai_duzeltme_aktif: Optional[bool] = None
    gece_modu_aktif: Optional[bool] = None
    gece_modu_baslangic: Optional[str] = None
    gece_modu_bitis: Optional[str] = None
    yolo_confidence: Optional[float] = None
    ocr_confidence: Optional[float] = None
    gece_brightness: Optional[float] = None
    gece_contrast: Optional[float] = None
    site_logo_url: Optional[str] = None