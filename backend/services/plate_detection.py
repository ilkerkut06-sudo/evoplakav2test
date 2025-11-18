import cv2
import numpy as np
from typing import List, Tuple, Optional
import logging
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class PlateDetector:
    def __init__(self, model_path="yolov8n.pt", confidence=0.5):
        self.confidence = confidence
        self.model = None
        self.load_model(model_path)
    
    def load_model(self, model_path: str):
        """YOLO modelini yükle"""
        try:
            self.model = YOLO(model_path)
            logger.info(f"YOLO modeli yüklendi: {model_path}")
        except Exception as e:
            logger.error(f"YOLO model yüklenemedi: {e}")
    
    def detect_plates(self, frame: np.ndarray) -> List[Tuple[np.ndarray, Tuple[int, int, int, int], float]]:
        """
        Frame'de plakaları tespit et
        Returns: [(plate_img, bbox, confidence), ...]
        """
        if self.model is None:
            return []
        
        try:
            # YOLO tahmin
            results = self.model(frame, conf=self.confidence, verbose=False)
            
            plates = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Bounding box koordinatları
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    conf = float(box.conf[0])
                    
                    # Plaka bölgesini kırp
                    plate_img = frame[y1:y2, x1:x2]
                    
                    if plate_img.size > 0:
                        plates.append((plate_img, (x1, y1, x2, y2), conf))
            
            return plates
            
        except Exception as e:
            logger.error(f"Plaka tespit hatası: {e}")
            return []
    
    def update_confidence(self, new_confidence: float):
        """Güven eşiğini güncelle"""
        self.confidence = new_confidence
    
    def get_status(self) -> dict:
        """Detektor durumunu döndür"""
        return {
            "initialized": self.model is not None,
            "confidence": self.confidence,
            "model_loaded": self.model is not None
        }