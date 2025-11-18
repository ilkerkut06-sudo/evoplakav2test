import asyncio
import cv2
import numpy as np
from typing import Optional, Dict
import logging
from datetime import datetime, timezone
import base64
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)

class PlatePipeline:
    def __init__(self, plate_detector, ocr_service, plate_corrector, vehicle_classifier):
        self.plate_detector = plate_detector
        self.ocr_service = ocr_service
        self.plate_corrector = plate_corrector
        self.vehicle_classifier = vehicle_classifier
        self.is_running = False
        self.queue = asyncio.Queue(maxsize=100)
    
    async def start(self):
        """Pipeline'i başlat"""
        self.is_running = True
        logger.info("Plaka tanıma pipeline başlatıldı")
    
    async def stop(self):
        """Pipeline'i durdur"""
        self.is_running = False
        logger.info("Plaka tanıma pipeline durduruldu")
    
    async def process_frame(self, frame: np.ndarray, camera_id: str, camera_name: str,
                           ai_correction_enabled: bool = True) -> Optional[Dict]:
        """
        Frame'i işle ve plaka bilgilerini döndür
        """
        try:
            # 1. Plakaları tespit et
            plates = self.plate_detector.detect_plates(frame)
            
            if not plates:
                return None
            
            # İlk plakayı işle (birden fazla plaka varsa en yüksek güvenli olan)
            plates.sort(key=lambda x: x[2], reverse=True)
            plate_img, bbox, yolo_conf = plates[0]
            
            # 2. Araç tipini sınıflandır
            vehicle_type = self.vehicle_classifier.classify_vehicle(frame)
            
            # 3. OCR ile plaka oku
            plate_text, ocr_conf = self.ocr_service.read_plate(plate_img)
            
            if not plate_text:
                return None
            
            # 4. AI düzeltme (isteğe bağlı)
            original_plate = plate_text
            was_corrected = False
            
            if ai_correction_enabled:
                plate_text, was_corrected = self.plate_corrector.correct_plate(plate_text)
            
            # 5. Fotoğrafı base64'e çevir
            photo_base64 = self.frame_to_base64(frame, bbox)
            
            result = {
                "plaka_no": plate_text,
                "orijinal_plaka": original_plate if was_corrected else None,
                "duzeltildi_mi": was_corrected,
                "arac_tipi": vehicle_type,
                "yolo_guven": float(yolo_conf),
                "ocr_guven": float(ocr_conf),
                "fotograf_base64": photo_base64,
                "kamera_id": camera_id,
                "kamera_adi": camera_name,
                "tarih": datetime.now(timezone.utc).isoformat()
            }
            
            logger.info(f"Plaka tanındı: {plate_text} (Kamera: {camera_name})")
            return result
            
        except Exception as e:
            logger.error(f"Pipeline işleme hatası: {e}")
            return None
    
    def frame_to_base64(self, frame: np.ndarray, bbox: tuple) -> str:
        """Frame'i base64'e çevir (plaka bölgesi vurgulu)"""
        try:
            # Bbox çiz
            x1, y1, x2, y2 = bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # JPEG'e çevir
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            
            return f"data:image/jpeg;base64,{img_base64}"
        except Exception as e:
            logger.error(f"Base64 dönüştürme hatası: {e}")
            return ""
    
    def get_queue_size(self) -> int:
        """Kuyruk boyutunu döndür"""
        return self.queue.qsize()
    
    def get_status(self) -> Dict:
        """Pipeline durumunu döndür"""
        return {
            "running": self.is_running,
            "queue_size": self.queue.qsize(),
            "max_queue_size": self.queue.maxsize
        }