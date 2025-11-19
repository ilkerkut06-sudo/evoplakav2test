from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse
import logging
import json
import asyncio
import cv2
import numpy as np
import base64
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stream", tags=["Video Stream"])

db = None

def set_db(database):
    global db
    db = database

# Aktif WebSocket bağlantıları
active_connections = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
    
    async def connect(self, websocket: WebSocket, camera_id: str):
        await websocket.accept()
        if camera_id not in self.active_connections:
            self.active_connections[camera_id] = []
        self.active_connections[camera_id].append(websocket)
        logger.info(f"WebSocket bağlantısı kuruldu: {camera_id}")
    
    def disconnect(self, websocket: WebSocket, camera_id: str):
        if camera_id in self.active_connections:
            self.active_connections[camera_id].remove(websocket)
            if not self.active_connections[camera_id]:
                del self.active_connections[camera_id]
        logger.info(f"WebSocket bağlantısı kesildi: {camera_id}")
    
    async def broadcast(self, camera_id: str, message: dict):
        if camera_id in self.active_connections:
            for connection in self.active_connections[camera_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass

manager = ConnectionManager()

@router.get("/{camera_id}")
async def video_stream(camera_id: str):
    """
    MJPEG video stream endpoint
    Returns real-time video from webcam or RTSP camera
    """
    async def generate_frames():
        cap = None
        try:
            # Kamera bilgisini al
            camera = await db.cameras.find_one({"id": camera_id})
            if not camera:
                logger.error(f"Kamera bulunamadı: {camera_id}")
                return
            
            camera_type = camera.get('kamera_tipi', '').upper()
            
            # Kamerayı aç
            if camera_type == 'WEBCAM':
                webcam_index = camera.get('webcam_index', 0)
                # Windows için CAP_DSHOW backend kullan (daha stabil)
                cap = cv2.VideoCapture(webcam_index, cv2.CAP_DSHOW)
                logger.info(f"MJPEG Stream: Webcam {webcam_index} açıldı (CAP_DSHOW)")
            elif camera_type == 'RTSP':
                rtsp_url = camera.get('main_stream_url')
                if not rtsp_url:
                    logger.error("RTSP URL tanımlanmamış")
                    return
                cap = cv2.VideoCapture(rtsp_url)
                logger.info(f"MJPEG Stream: RTSP açıldı - {rtsp_url}")
            else:
                logger.error(f"Desteklenmeyen kamera tipi: {camera_type}")
                return
            
            if not cap or not cap.isOpened():
                logger.error(f"Kamera açılamadı: {camera_id}")
                return
            
            # MJPEG stream döngüsü
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning(f"Frame okunamadı: {camera_id}")
                    await asyncio.sleep(0.1)
                    continue
                
                # Frame'i küçült (performans)
                frame = cv2.resize(frame, (640, 480))
                
                # JPEG encode
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if not ret:
                    continue
                
                # MJPEG format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                
                # FPS kontrolü (~30 FPS)
                await asyncio.sleep(0.033)
        
        except Exception as e:
            logger.error(f"MJPEG stream hatası: {e}")
        finally:
            if cap:
                cap.release()
                logger.info(f"MJPEG Stream kapatıldı: {camera_id}")
    
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.websocket("/ws/{camera_id}")
async def websocket_endpoint(websocket: WebSocket, camera_id: str):
    """
    WebRTC WebSocket endpoint
    Client sends frames, backend processes with YOLO/OCR
    """
    from services.plate_detection import PlateDetector
    from services.ocr_service import OCRService
    
    await manager.connect(websocket, camera_id)
    
    try:
        # Kamera bilgisini al
        camera = await db.cameras.find_one({"id": camera_id})
        if not camera:
            await websocket.send_json({"error": "Kamera bulunamadı"})
            return
        
        # Sistem ayarları
        settings = await db.settings.find_one({"id": "sistem_ayarlari"})
        if not settings:
            settings = {"ocr_motor": "easyocr", "yolo_confidence": 0.5}
        
        # YOLO ve OCR başlat
        detector = PlateDetector(confidence=settings.get('yolo_confidence', 0.5))
        ocr_service = OCRService(engine=settings.get('ocr_motor', 'easyocr'))
        
        logger.info(f"WebRTC WebSocket başlatıldı: {camera_id}")
        
        # Frame alma döngüsü
        while True:
            # Client'tan frame al (binary data)
            frame_data = await websocket.receive_bytes()
            
            # Numpy array'e çevir
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                continue
            
            # YOLO ile plaka tespit et
            detections = detector.detect_plates(frame)
            
            results = []
            for detection in detections:
                x1, y1, x2, y2, conf = detection
                
                # Plaka bölgesini kes
                plate_img = frame[int(y1):int(y2), int(x1):int(x2)]
                
                # OCR ile plaka oku
                plate_text, ocr_conf = ocr_service.read_plate(plate_img)
                
                if plate_text:
                    results.append({
                        "plate": plate_text,
                        "confidence": float(conf),
                        "ocr_confidence": float(ocr_conf),
                        "bbox": [int(x1), int(y1), int(x2), int(y2)]
                    })
                    
                    # Database'e log kaydet
                    await db.logs.insert_one({
                        "id": str(uuid4()),
                        "plaka_no": plate_text,
                        "camera_id": camera_id,
                        "timestamp": datetime.now(timezone.utc),
                        "confidence": float(conf),
                        "durum": "Tanımlı"  # Plaka kontrolü yapılabilir
                    })
            
            # Sonuçları gönder
            if results:
                await websocket.send_json({
                    "type": "detection",
                    "detections": results,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket bağlantısı kesildi: {camera_id}")
        manager.disconnect(websocket, camera_id)
    except Exception as e:
        logger.error(f"WebSocket hatası: {e}", exc_info=True)
        manager.disconnect(websocket, camera_id)

@router.post("/rtsp/start/{camera_id}")
async def start_rtsp_stream(camera_id: str):
    """RTSP stream'i başlat"""
    camera = await db.cameras.find_one({"id": camera_id})
    if not camera:
        raise HTTPException(status_code=404, detail="Kamera bulunamadı")
    
    if camera['kamera_tipi'] != 'RTSP':
        raise HTTPException(status_code=400, detail="Bu kamera RTSP tipinde değil")
    
    # RTSP stream başlatma işlemi burada
    # Şimdilik mock response
    
    return {
        "message": "RTSP stream başlatıldı",
        "camera_id": camera_id,
        "main_stream": camera.get('main_stream_url')
    }

@router.post("/rtsp/stop/{camera_id}")
async def stop_rtsp_stream(camera_id: str):
    """RTSP stream'i durdur"""
    return {
        "message": "RTSP stream durduruldu",
        "camera_id": camera_id
    }

@router.post("/process-frame/{camera_id}")
async def process_frame(camera_id: str, frame_data: dict):
    """
    Tek bir frame'i işle (plaka tanıma pipeline)
    """
    from services.ocr_service import OCRService
    from services.plate_detection import PlateDetector
    from services.vehicle_classifier import VehicleClassifier
    from services.plate_correction import PlateCorrector
    from services.pipeline_manager import PlatePipeline
    
    # Kamera bilgisi
    camera = await db.cameras.find_one({"id": camera_id})
    if not camera:
        raise HTTPException(status_code=404, detail="Kamera bulunamadı")
    
    # Sistem ayarları
    settings = await db.settings.find_one({"id": "sistem_ayarlari"})
    if not settings:
        settings = {"ocr_motor": "easyocr", "ai_duzeltme_aktif": True, "yolo_confidence": 0.5}
    
    # Servisler
    ocr_service = OCRService(engine=settings['ocr_motor'])
    plate_detector = PlateDetector(confidence=settings['yolo_confidence'])
    vehicle_classifier = VehicleClassifier()
    plate_corrector = PlateCorrector()
    
    pipeline = PlatePipeline(plate_detector, ocr_service, plate_corrector, vehicle_classifier)
    
    try:
        # Base64 frame'i decode et
        frame_base64 = frame_data.get('frame', '').split(',')[1]
        frame_bytes = base64.b64decode(frame_base64)
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Pipeline'dan geçir
        result = await pipeline.process_frame(
            frame,
            camera_id,
            camera['kamera_adi'],
            ai_correction_enabled=settings['ai_duzeltme_aktif']
        )
        
        if result:
            # Plaka durumunu kontrol et
            plate_check = await db.plates.find_one({"plaka_no": result['plaka_no']})
            
            durum = "Tanımsız"
            isim_soyisim = None
            site_id = None
            blok_id = None
            daire_id = None
            kapi_acildi_mi = False
            
            if plate_check:
                durum = plate_check['durum']
                site_id = plate_check.get('site_id')
                blok_id = plate_check.get('blok_id')
                daire_id = plate_check.get('daire_id')
                
                # Daire sahibi bilgisi
                if site_id and blok_id and daire_id:
                    site = await db.sites.find_one({"id": site_id})
                    if site:
                        for blok in site.get('bloklar', []):
                            if blok['id'] == blok_id:
                                for daire in blok.get('daireler', []):
                                    if daire['id'] == daire_id:
                                        isim_soyisim = daire.get('isim_soyisim')
                
                # Tanımlı ise kapıyı aç
                if durum == "Tanımlı" and camera.get('bagli_kapi_id'):
                    kapi = await db.nodemcu.find_one({"id": camera['bagli_kapi_id']})
                    if kapi:
                        from services.nodemcu_controller import NodeMCUController
                        controller = NodeMCUController()
                        kapi_acildi_mi = await controller.open_door(kapi['ip_adres'], kapi.get('endpoint_url', '/open'), kapi['nodemcu_id'])
            
            # Log kaydet
            from models.log import GecisLogCreate
            log_data = GecisLogCreate(
                plaka_no=result['plaka_no'],
                orijinal_plaka=result.get('orijinal_plaka'),
                duzeltildi_mi=result.get('duzeltildi_mi', False),
                arac_tipi=result.get('arac_tipi'),
                kamera_id=camera_id,
                kamera_adi=camera['kamera_adi'],
                kapi_id=camera.get('bagli_kapi_id'),
                kapi_adi=None,  # TODO: kapı adını al
                durum=durum,
                giris_cikis=camera['giris_cikis'],
                site_id=site_id,
                blok_id=blok_id,
                daire_id=daire_id,
                isim_soyisim=isim_soyisim,
                fotograf_url=result.get('fotograf_base64'),
                kapi_acildi_mi=kapi_acildi_mi
            )
            
            log_dict = log_data.model_dump()
            from models.log import GecisLog
            log_obj = GecisLog(**log_dict)
            log_doc = log_obj.model_dump()
            log_doc['tarih'] = log_doc['tarih'].isoformat()
            await db.logs.insert_one(log_doc)
            
            return {
                "success": True,
                "plaka_no": result['plaka_no'],
                "durum": durum,
                "arac_tipi": result.get('arac_tipi'),
                "kapi_acildi_mi": kapi_acildi_mi,
                "log_id": log_obj.id
            }
        
        return {"success": False, "message": "Plaka tanınamadı"}
    
    except Exception as e:
        logger.error(f"Frame işleme hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))