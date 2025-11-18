import cv2
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self, engine="easyocr"):
        self.engine = engine
        self.paddle_ocr = None
        self.easy_ocr = None
        self.initialize_engine()
    
    def initialize_engine(self):
        """OCR motorunu başlat"""
        try:
            if self.engine == "paddleocr":
                try:
                    from paddleocr import PaddleOCR
                    self.paddle_ocr = PaddleOCR(
                        use_angle_cls=True,
                        lang='en',
                        show_log=False
                    )
                    logger.info("PaddleOCR başlatıldı")
                except ImportError:
                    logger.warning("PaddleOCR yüklü değil, EasyOCR'ye geçiliyor")
                    self.engine = "easyocr"
                    import easyocr
                    self.easy_ocr = easyocr.Reader(['en'], gpu=False)
                    logger.info("EasyOCR başlatıldı")
            elif self.engine == "easyocr":
                import easyocr
                self.easy_ocr = easyocr.Reader(['en'], gpu=False)
                logger.info("EasyOCR başlatıldı")
        except Exception as e:
            logger.error(f"OCR motor başlatılamadı: {e}")
    
    def switch_engine(self, new_engine: str):
        """OCR motorunu değiştir"""
        if new_engine != self.engine:
            self.engine = new_engine
            self.initialize_engine()
    
    def preprocess_plate_image(self, plate_img: np.ndarray) -> np.ndarray:
        """Plaka görüntüsünü ön işle"""
        try:
            # Gri tonlamaya çevir
            if len(plate_img.shape) == 3:
                gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
            else:
                gray = plate_img
            
            # Kontrast artır
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Gaussian blur ile gürültü azalt
            blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
            
            # Threshold uygula
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return thresh
        except Exception as e:
            logger.error(f"Görüntü ön işleme hatası: {e}")
            return plate_img
    
    def read_plate(self, plate_img: np.ndarray, confidence_threshold: float = 0.6) -> Tuple[Optional[str], float]:
        """Plaka görüntüsünden metin oku"""
        try:
            # Ön işleme
            processed = self.preprocess_plate_image(plate_img)
            
            if self.engine == "paddleocr" and self.paddle_ocr:
                result = self.paddle_ocr.ocr(processed, cls=True)
                
                if result and result[0]:
                    # En yüksek güvenli sonuç al
                    best_text = ""
                    best_conf = 0.0
                    
                    for line in result[0]:
                        text = line[1][0]
                        conf = line[1][1]
                        if conf > best_conf:
                            best_text = text
                            best_conf = conf
                    
                    if best_conf >= confidence_threshold:
                        # Temizle
                        plate_text = self.clean_plate_text(best_text)
                        return plate_text, best_conf
            
            elif self.engine == "easyocr" and self.easy_ocr:
                result = self.easy_ocr.readtext(processed)
                
                if result:
                    # En yüksek güvenli sonuç al
                    best_text = ""
                    best_conf = 0.0
                    
                    for detection in result:
                        text = detection[1]
                        conf = detection[2]
                        if conf > best_conf:
                            best_text = text
                            best_conf = conf
                    
                    if best_conf >= confidence_threshold:
                        plate_text = self.clean_plate_text(best_text)
                        return plate_text, best_conf
            
            return None, 0.0
            
        except Exception as e:
            logger.error(f"OCR okuma hatası: {e}")
            return None, 0.0
    
    def clean_plate_text(self, text: str) -> str:
        """Plaka metnini temizle"""
        # Boşlukları kaldır ve büyük harfe çevir
        cleaned = text.replace(" ", "").replace("-", "").upper()
        # Sadece harf ve rakam bırak
        cleaned = ''.join(c for c in cleaned if c.isalnum())
        return cleaned
    
    def get_status(self) -> dict:
        """Motor durumunu döndür"""
        status = {
            "engine": self.engine,
            "initialized": False,
            "error": None
        }
        
        try:
            if self.engine == "paddleocr" and self.paddle_ocr:
                status["initialized"] = True
            elif self.engine == "easyocr" and self.easy_ocr:
                status["initialized"] = True
        except Exception as e:
            status["error"] = str(e)
        
        return status