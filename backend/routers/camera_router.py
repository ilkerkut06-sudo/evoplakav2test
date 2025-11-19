from fastapi import APIRouter, HTTPException
from models.camera import Kamera, KameraCreate, KameraUpdate
from typing import List
from datetime import datetime

router = APIRouter(prefix="/cameras", tags=["Kamera Yönetimi"])

db = None

def set_db(database):
    global db
    db = database

@router.post("", response_model=Kamera)
async def create_camera(camera_input: KameraCreate):
    camera_dict = camera_input.model_dump()
    camera_obj = Kamera(**camera_dict)
    doc = camera_obj.model_dump()
    doc['olusturma_tarihi'] = doc['olusturma_tarihi'].isoformat()
    
    await db.cameras.insert_one(doc)
    return camera_obj

@router.get("", response_model=List[Kamera])
async def get_cameras(aktif: bool = None):
    query = {}
    if aktif is not None:
        query['aktif'] = aktif
    
    cameras = await db.cameras.find(query, {"_id": 0}).to_list(1000)
    
    for camera in cameras:
        if isinstance(camera.get('olusturma_tarihi'), str):
            camera['olusturma_tarihi'] = datetime.fromisoformat(camera['olusturma_tarihi'])
    
    return cameras

@router.get("/{camera_id}", response_model=Kamera)
async def get_camera(camera_id: str):
    camera = await db.cameras.find_one({"id": camera_id}, {"_id": 0})
    if not camera:
        raise HTTPException(status_code=404, detail="Kamera bulunamadı")
    
    if isinstance(camera.get('olusturma_tarihi'), str):
        camera['olusturma_tarihi'] = datetime.fromisoformat(camera['olusturma_tarihi'])
    
    return camera

@router.put("/{camera_id}", response_model=Kamera)
async def update_camera(camera_id: str, camera_input: KameraUpdate):
    update_data = {k: v for k, v in camera_input.model_dump().items() if v is not None}
    
    result = await db.cameras.update_one(
        {"id": camera_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Kamera bulunamadı")
    
    return await get_camera(camera_id)

@router.delete("/{camera_id}")
async def delete_camera(camera_id: str):
    result = await db.cameras.delete_one({"id": camera_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Kamera bulunamadı")
    return {"message": "Kamera silindi"}

@router.post("/{camera_id}/ptz/{action}")
async def control_ptz(camera_id: str, action: str):
    """PTZ kontrol (up, down, left, right, zoom_in, zoom_out)"""
    camera = await db.cameras.find_one({"id": camera_id})
    if not camera:
        raise HTTPException(status_code=404, detail="Kamera bulunamadı")
    
    # ONVIF PTZ kontrolü burada implement edilecek
    # Şimdilik mock response
    
    return {
        "message": f"PTZ komutu gönderildi: {action}",
        "camera_id": camera_id,
        "action": action
    }

@router.get("/{camera_id}/stream")
async def get_camera_stream(camera_id: str):
    """Kamera stream'ini test et"""
    import cv2
    
    camera = await db.cameras.find_one({"id": camera_id}, {"_id": 0})
    if not camera:
        raise HTTPException(status_code=404, detail="Kamera bulunamadı")
    
    camera_type = camera.get('kamera_tipi', '').upper()
    
    # Webcam ise OpenCV ile test et
    if camera_type == 'WEBCAM':
        webcam_index = camera.get('webcam_index', 0)
        
        try:
            cap = cv2.VideoCapture(webcam_index)
            
            if not cap.isOpened():
                return {
                    "status": "error",
                    "message": f"Webcam {webcam_index} açılamadı. Başka uygulama kullanıyor olabilir.",
                    "webcam_index": webcam_index,
                    "camera_type": camera_type
                }
            
            # Bir frame oku
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                return {
                    "status": "success",
                    "message": f"Webcam {webcam_index} çalışıyor!",
                    "webcam_index": webcam_index,
                    "resolution": f"{frame.shape[1]}x{frame.shape[0]}",
                    "camera_type": camera_type
                }
            else:
                return {
                    "status": "error",
                    "message": f"Webcam {webcam_index} frame okunamadı",
                    "webcam_index": webcam_index,
                    "camera_type": camera_type
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Webcam hatası: {str(e)}",
                "webcam_index": webcam_index,
                "camera_type": camera_type,
                "error_detail": str(e)
            }
    
    # RTSP IP kamera ise
    elif camera_type == 'RTSP':
        rtsp_url = camera.get('main_stream_url')
        
        if not rtsp_url:
            return {
                "status": "error",
                "message": "RTSP URL tanımlanmamış",
                "camera_type": camera_type
            }
        
        try:
            cap = cv2.VideoCapture(rtsp_url)
            
            if not cap.isOpened():
                return {
                    "status": "error",
                    "message": f"RTSP stream açılamadı: {rtsp_url}",
                    "camera_type": camera_type,
                    "rtsp_url": rtsp_url
                }
            
            # Bir frame oku
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                return {
                    "status": "success",
                    "message": f"RTSP stream çalışıyor!",
                    "resolution": f"{frame.shape[1]}x{frame.shape[0]}",
                    "camera_type": camera_type,
                    "rtsp_url": rtsp_url
                }
            else:
                return {
                    "status": "error",
                    "message": f"RTSP stream frame okunamadı",
                    "camera_type": camera_type,
                    "rtsp_url": rtsp_url
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"RTSP hatası: {str(e)}",
                "camera_type": camera_type,
                "rtsp_url": rtsp_url,
                "error_detail": str(e)
            }
    
    else:
        return {
            "status": "error",
            "message": f"Bilinmeyen kamera tipi: {camera_type}",
            "camera_type": camera_type,
            "supported_types": ["WEBCAM", "RTSP"]
        }