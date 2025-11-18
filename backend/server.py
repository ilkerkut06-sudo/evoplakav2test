from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path

# Router'ları import et
from routers import (
    site_router,
    plate_router,
    camera_router,
    nodemcu_router,
    log_router,
    settings_router,
    report_router,
    stream_router
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB bağlantısı
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

# FastAPI app
app = FastAPI(
    title="Plaka Tanıma Sistemi API",
    description="Web tabanlı plaka tanıma ve site yönetim sistemi",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'lara database instance'ını geçir
site_router.set_db(db)
plate_router.set_db(db)
camera_router.set_db(db)
nodemcu_router.set_db(db)
log_router.set_db(db)
settings_router.set_db(db)
report_router.set_db(db)
stream_router.set_db(db)

# Router'ları ekle
app.include_router(site_router.router, prefix="/api")
app.include_router(plate_router.router, prefix="/api")
app.include_router(camera_router.router, prefix="/api")
app.include_router(nodemcu_router.router, prefix="/api")
app.include_router(log_router.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")
app.include_router(report_router.router, prefix="/api")
app.include_router(stream_router.router, prefix="/api")

# Ana endpoint
@app.get("/api")
async def root():
    return {
        "message": "Plaka Tanıma Sistemi API",
        "version": "1.0.0",
        "status": "running"
    }

# Health check
@app.get("/api/health")
async def health_check():
    try:
        # MongoDB bağlantısını test et
        await db.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    logger.info("Plaka Tanıma Sistemi başlatıldı")
    logger.info(f"MongoDB: {mongo_url}")
    logger.info(f"Veritabanı: {os.environ.get('DB_NAME', 'test_database')}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    logger.info("MongoDB bağlantısı kapatıldı")