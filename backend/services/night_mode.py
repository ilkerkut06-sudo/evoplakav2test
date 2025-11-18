import cv2
import numpy as np
from datetime import datetime
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

class NightModeProcessor:
    def __init__(self):
        self.is_active = False
        self.brightness_factor = 1.2
        self.contrast_factor = 1.3
    
    def set_active(self, active: bool):
        """Gece modunu aktif/pasif yap"""
        self.is_active = active
    
    def update_settings(self, brightness: float, contrast: float):
        """Gece modu ayarlarını güncelle"""
        self.brightness_factor = brightness
        self.contrast_factor = contrast
    
    def should_activate(self, start_time: str, end_time: str) -> bool:
        """
        Mevcut saate göre gece modu aktif olmalı mı?
        start_time, end_time format: "HH:MM"
        """
        try:
            now = datetime.now()
            current_time = now.time()
            
            start_h, start_m = map(int, start_time.split(':'))
            end_h, end_m = map(int, end_time.split(':'))
            
            start = datetime.strptime(f"{start_h}:{start_m}", "%H:%M").time()
            end = datetime.strptime(f"{end_h}:{end_m}", "%H:%M").time()
            
            # Gece modu saat aralığı kontrolü
            if start <= end:
                return start <= current_time <= end
            else:
                # Gece yarısını geçen aralık (ör: 20:00 - 06:00)
                return current_time >= start or current_time <= end
        
        except Exception as e:
            logger.error(f"Gece modu zaman kontrolü hatası: {e}")
            return False
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Gece modu aktifse frame'i işle
        """
        if not self.is_active:
            return frame
        
        try:
            # Parlaklk ve kontrast ayarlaması
            adjusted = cv2.convertScaleAbs(
                frame,
                alpha=self.contrast_factor,  # Kontrast
                beta=int((self.brightness_factor - 1.0) * 50)  # Parlaklık
            )
            
            # Gamma düzeltmesi (gece çekimlerinde iyileştirme)
            gamma = 1.2
            inv_gamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
            adjusted = cv2.LUT(adjusted, table)
            
            # Noise azaltma
            adjusted = cv2.fastNlMeansDenoisingColored(adjusted, None, 10, 10, 7, 21)
            
            return adjusted
        
        except Exception as e:
            logger.error(f"Gece modu işleme hatası: {e}")
            return frame
    
    def get_status(self) -> dict:
        """Gece modu durumunu döndür"""
        return {
            "active": self.is_active,
            "brightness": self.brightness_factor,
            "contrast": self.contrast_factor
        }