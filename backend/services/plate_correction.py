import re
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class PlateCorrector:
    def __init__(self):
        # Karışan karakterler
        self.char_corrections = {
            '0': 'O',
            'O': '0',
            '8': 'B',
            'B': '8',
            '5': 'S',
            'S': '5',
            '1': 'I',
            'I': '1',
            '6': 'G',
            'G': '6',
            '2': 'Z',
            'Z': '2',
        }
        
        # Türkiye plaka formatları
        # Örnek: 34ABC123, 06XY1234, 01A12345
        self.tr_plate_patterns = [
            r'^[0-9]{2}[A-Z]{1,3}[0-9]{2,4}$',  # 34ABC123, 06XY1234
            r'^[0-9]{2}[A-Z]{2}[0-9]{3,4}$',    # 34AB1234
            r'^[0-9]{2}[A-Z]{3}[0-9]{2}$',      # 34ABC12
        ]
    
    def correct_plate(self, plate_text: str) -> Tuple[str, bool]:
        """
        Plaka metnini düzelt
        Returns: (düzeltilmiş_plaka, düzeltildi_mi)
        """
        if not plate_text:
            return plate_text, False
        
        original = plate_text
        corrected = plate_text
        
        # Format kontrolü
        if self.matches_tr_format(corrected):
            return corrected, False  # Zaten doğru format
        
        # Heuristic düzeltmeler
        corrected = self.apply_heuristic_corrections(corrected)
        
        # Düzeltme yapıldı mı?
        was_corrected = (original != corrected)
        
        if was_corrected:
            logger.info(f"Plaka düzeltildi: {original} -> {corrected}")
        
        return corrected, was_corrected
    
    def matches_tr_format(self, plate: str) -> bool:
        """Türkiye plaka formatına uyuyor mu?"""
        for pattern in self.tr_plate_patterns:
            if re.match(pattern, plate):
                return True
        return False
    
    def apply_heuristic_corrections(self, plate: str) -> str:
        """
        Heuristic düzeltmeler uygula
        Türk plaka formatı: [2 rakam][1-3 harf][2-4 rakam]
        """
        if len(plate) < 5:
            return plate
        
        corrected = list(plate)
        
        # İlk 2 karakter rakam olmalı
        for i in range(min(2, len(corrected))):
            if corrected[i].isalpha():
                # Harfi rakama dönüştür
                if corrected[i] in self.char_corrections:
                    corrected[i] = self.char_corrections[corrected[i]]
        
        # Orta kısım harf olmalı (2-5 arası)
        for i in range(2, min(5, len(corrected))):
            if corrected[i].isdigit():
                # Rakamı harfe dönüştür
                if corrected[i] in self.char_corrections:
                    corrected[i] = self.char_corrections[corrected[i]]
        
        # Son kısım rakam olmalı
        for i in range(5, len(corrected)):
            if corrected[i].isalpha():
                # Harfi rakama dönüştür
                if corrected[i] in self.char_corrections:
                    corrected[i] = self.char_corrections[corrected[i]]
        
        return ''.join(corrected)
    
    def get_status(self) -> dict:
        """Düzeltici durumunu döndür"""
        return {
            "initialized": True,
            "supported_formats": ["TR"]
        }