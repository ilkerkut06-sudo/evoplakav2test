import cv2
import numpy as np
from typing import Optional
import logging
from ultralytics import YOLO

logger = logging.getLogger(__name__)

class VehicleClassifier:
    def __init__(self):
        self.model = None
        self.load_model()
        
        # Araç tipi haritalama (COCO sınıflarından)
        self.vehicle_map = {
            2: "Sedan",  # car
            3: "Motosiklet",  # motorcycle
            5: "Minibüs",  # bus
            7: "Kamyon",  # truck
        }
    
    def load_model(self):
        """YOLO modelini yükle (araç tespiti için)"""
        try:
            self.model = YOLO("yolov8n.pt")  # Genel COCO modeli
            logger.info("Araç sınıflandırma modeli yüklendi")
        except Exception as e:
            logger.error(f"Araç sınıflandırma modeli yüklenemedi: {e}")
    
    def classify_vehicle(self, frame: np.ndarray) -> str:
        """Frame'den araç tipini belirle"""
        if self.model is None:
            return "Bilinmiyor"
        
        try:
            results = self.model(frame, conf=0.3, verbose=False)
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    class_id = int(box.cls[0])
                    
                    # Araç sınıfı mı?
                    if class_id in self.vehicle_map:
                        return self.vehicle_map[class_id]
                    elif class_id == 2:  # car - default sedan
                        return "Sedan"
            
            # Hiçbir araç bulunamadıysa, plaka boyutundan tahmin
            height, width = frame.shape[:2]
            if height > 300:  # Büyük araç
                return "SUV"
            else:
                return "Sedan"
            
        except Exception as e:
            logger.error(f"Araç sınıflandırma hatası: {e}")
            return "Bilinmiyor"
    
    def get_status(self) -> dict:
        """Sınıflandırıcı durumunu döndür"""
        return {
            "initialized": self.model is not None,
            "supported_types": list(self.vehicle_map.values())
        }