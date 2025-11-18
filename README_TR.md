# Plaka Tanıma ve Site Yönetim Sistemi

## Genel Bakış

Web tabanlı, tam otomatik plaka tanıma, site yönetimi ve kapı kontrol sistemi.

### Özellikler

✅ **Plaka Tanıma Pipeline**
- YOLOv8 tabanlı plaka tespiti
- PaddleOCR & EasyOCR desteği (ayarlardan seçilebilir)
- AI tabanlı hatalı plaka düzeltme
- Araç tipi sınıflandırma (Sedan, SUV, Kamyon, vb.)
- Gece modu için özel görüntü işleme profilleri

✅ **Kamera Sistemi**
- RTSP IP kamera desteği (Main + Sub Stream)
- Webcam desteği (tarayıcı üzerinden)
- WebRTC ile düşük gecikmeli canlı görüntü
- ONVIF PTZ kontrol
- Çoklu kamera grid görünümü (1x1, 2x2, 3x3)

✅ **Site Yönetimi**
- Site → Blok → Daire hiyerarşisi
- Her daireye maksimum 3 plaka
- Ziyaretçi plakaları (geçerlilik süreli)
- Yasaklı plaka listesi

✅ **Kapı Kontrol**
- NodeMCU tabanlı kapı kontrolü
- Otomatik kapı açma (tanımlı plakalar için)
- Manuel kapı açma (dashboard üzerinden)
- Kapı bazlı istatistikler

✅ **Raporlama**
- Gerçek zamanlı istatistikler
- Filtrelenebilir loglar (tarih, plaka, durum, kamera)
- PDF rapor çıktısı (Türkçe karakter desteği)
- Araç tipi bazlı analizler
- Kapı geçiş analizleri

✅ **Modern Dashboard**
- Dark tema tasarım
- Canlı kamera grid
- Son 20 geçiş logu (fotoğraflı)
- Canlı akış ticker (alt bant)
- Sistem motor durumu (CPU, RAM, OCR, YOLO)

## Teknoloji Stack

**Backend:**
- Python 3.11
- FastAPI
- MongoDB (Motor)
- OpenCV
- YOLOv8 (Ultralytics)
- PaddleOCR / EasyOCR
- ReportLab (PDF)

**Frontend:**
- React 19
- Tailwind CSS
- Shadcn UI
- Axios
- React Router
- date-fns

## Kurulum (Windows)

### Gereksinimler

1. **Python 3.8+** - [İndir](https://www.python.org/downloads/)
2. **Node.js 16+** - [İndir](https://nodejs.org/)
3. **MongoDB** - Localhost'ta çalışıyor olmalı (port: 27017)

### Otomatik Kurulum

1. Proje klasörüne gidin:
```bash
cd /yol/plaka-tanima-sistemi
```

2. Kurulum scriptini çalıştırın:
```bash
setup_and_start.bat
```

Bu script:
- Python sanal ortamı oluşturur
- Backend paketlerini yükler (OpenCV, YOLO, OCR, vb.)
- YOLO modelini indirir
- Frontend paketlerini yükler
- Veritabanını hazırlar
- Servisleri başlatır

### Manuel Başlatma

Kurulum tamamlandıktan sonra, servisleri başlatmak için:

```bash
start_server.bat
```

Bu script:
- Backend'i başlatır (Port: 8001)
- Frontend'i başlatır (Port: 3000)
- Tarayıcıda dashboard'u açar

## Kullanım

### 1. Kamera Ekleme

**RTSP IP Kamera:**
```
Dashboard → Kamera Yönetimi → Yeni Kamera Ekle
- Kamera Adı: "Ana Kapı Kamera"
- Kamera Tipi: RTSP
- Giriş/Çıkış: Giriş
- Main Stream URL: rtsp://192.168.1.100:554/stream1
- Sub Stream URL: rtsp://192.168.1.100:554/stream2
- ONVIF: IP, Port, Kullanıcı, Şifre
- Bağlı Kapı: Kapı seçin
```

**Webcam:**
```
Dashboard → Webcam Ekle
- Tarayıcı kamera izni verir
- Webcam otomatik olarak sisteme eklenir
```

### 2. Site ve Daire Yönetimi

```
Site Yönetimi → Yeni Site Ekle
└─ Site Adı: "Örnek Sitesi"
   └─ Blok Ekle: "A Blok"
      └─ Daire Ekle: "A-101"
         ├─ İsim: "Ahmet Yılmaz"
         ├─ Telefon: "05XX XXX XX XX"
         └─ Plaka Ekle: "34ABC123"
            ├─ Araç Tipi: Sedan
            └─ Durum: Tanımlı
```

### 3. NodeMCU Kapı Kontrolü

**NodeMCU Ayarları:**
```
NodeMCU Yönetimi → Yeni Cihaz Ekle
- NodeMCU ID: "KAPI-001"
- IP Adresi: "192.168.1.50"
- Kapı Adı: "Ana Giriş"
```

**Kapı - Kamera Eşleme:**
```
Kamera Ayarları → Bağlı Kapı Seç
```

### 4. Sistem Ayarları

```
Ayarlar → Sistem Ayarları
├─ OCR Motor: PaddleOCR / EasyOCR
├─ AI Plaka Düzeltme: Açık / Kapalı
├─ Gece Modu: 
│  ├─ Aktif: Evet
│  ├─ Başlangıç: 20:00
│  ├─ Bitiş: 06:00
│  ├─ Parlaklık: 1.2
│  └─ Kontrast: 1.3
└─ YOLO Güven Eşiği: 0.5
```

### 5. Raporlama

**Loglar:**
```
Raporlar → Logları Görüntüle
├─ Filtreler:
│  ├─ Tarih Aralığı
│  ├─ Plaka
│  ├─ Durum (Tanımlı, Misafir, Yasaklı)
│  └─ Kamera
└─ PDF İndir
```

**İstatistikler:**
- Bugünkü giriş sayısı
- Bu ay toplam giriş
- Misafir araç sayısı
- Araç tipi dağılımı
- Kapı bazlı geçişler

## API Dokümantasyonu

Backend çalıştıktan sonra:

**Swagger UI:** http://localhost:8001/docs
**ReDoc:** http://localhost:8001/redoc

### Önemli Endpointler

```
# Site Yönetimi
GET    /api/sites
POST   /api/sites
PUT    /api/sites/{id}
DELETE /api/sites/{id}
POST   /api/sites/{site_id}/bloklar
POST   /api/sites/{site_id}/bloklar/{blok_id}/daireler

# Plaka Yönetimi
GET    /api/plates
POST   /api/plates
GET    /api/plates/check/{plaka_no}

# Kamera Yönetimi
GET    /api/cameras
POST   /api/cameras
POST   /api/cameras/{id}/ptz/{action}

# NodeMCU / Kapı Kontrol
GET    /api/nodemcu
POST   /api/nodemcu/{id}/open
GET    /api/nodemcu/{id}/status

# Loglar
GET    /api/logs
GET    /api/logs/stats
GET    /api/logs/kapi-stats

# Raporlar
GET    /api/reports/generate-pdf
GET    /api/reports/vehicle-type-stats

# Sistem
GET    /api/settings
PUT    /api/settings
GET    /api/settings/system-status

# Stream
WS     /api/stream/ws/{camera_id}
POST   /api/stream/process-frame/{camera_id}
```

## Klasör Yapısı

```
/app/
├── backend/
│   ├── models/           # Pydantic modeller
│   │   ├── site.py
│   │   ├── plate.py
│   │   ├── camera.py
│   │   ├── nodemcu.py
│   │   ├── log.py
│   │   └── settings.py
│   ├── routers/          # API endpointleri
│   │   ├── site_router.py
│   │   ├── plate_router.py
│   │   ├── camera_router.py
│   │   ├── nodemcu_router.py
│   │   ├── log_router.py
│   │   ├── settings_router.py
│   │   ├── report_router.py
│   │   └── stream_router.py
│   ├── services/         # İş mantığı
│   │   ├── ocr_service.py
│   │   ├── plate_detection.py
│   │   ├── vehicle_classifier.py
│   │   ├── plate_correction.py
│   │   ├── nodemcu_controller.py
│   │   ├── night_mode.py
│   │   ├── pdf_generator.py
│   │   ├── system_monitor.py
│   │   └── pipeline_manager.py
│   ├── server.py         # Ana FastAPI app
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   └── Dashboard.js
│   │   ├── components/
│   │   │   ├── CameraGrid.js
│   │   │   ├── CameraBox.js
│   │   │   ├── LogPanel.js
│   │   │   ├── LiveTicker.js
│   │   │   ├── SystemStatus.js
│   │   │   ├── StatsCards.js
│   │   │   └── ui/         # Shadcn components
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.js
│   ├── package.json
│   └── .env
│
├── setup_and_start.bat   # Kurulum scripti
├── start_server.bat      # Başlatma scripti
└── README_TR.md         # Bu dosya
```

## Sorun Giderme

### Backend Başlamıyor

```bash
# Log kontrolü
tail -f /app/backend/logs/error.log

# Python paketleri eksik ise
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Başlamıyor

```bash
# Node paketleri eksik ise
cd frontend
npm install
# veya
yarn install
```

### MongoDB Bağlantı Hatası

```bash
# MongoDB çalışıyor mu?
mongo --eval "db.adminCommand('ping')"

# .env dosyasını kontrol et
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
```

### Kamera Bağlanamıyor

1. RTSP URL'ini kontrol edin
2. Kamera ağda erişilebilir mi?
3. Firewall/güvenlik duvarı ayarları
4. ONVIF kullanıcı adı/şifre doğru mu?

### Plaka Tanımıyor

1. Kamera kalitesi yeterli mi?
2. Aydınlatma uygun mu?
3. YOLO güven eşiğini düşürün (0.3-0.4)
4. Gece modu aktif mi?
5. OCR motoru değiştir (PaddleOCR ↔ EasyOCR)

## Geliştirme

### Backend

```bash
cd backend
venv\Scripts\activate

# Geliştirme modu
uvicorn server:app --reload --host 0.0.0.0 --port 8001

# Test
pytest tests/
```

### Frontend

```bash
cd frontend

# Geliştirme modu
npm start
# veya
yarn start

# Build
npm run build
```

## Lisans

Bu proje ticari kullanım için geliştirilmiştir.

## Destek

Sorunlar için: [GitHub Issues](https://github.com/your-repo/issues)
