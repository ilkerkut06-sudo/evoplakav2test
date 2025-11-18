# 📦 Offline Installer Kılavuzu - Plaka Tanıma Sistemi

## 🎯 Amaç
İnternet bağlantısı olmayan ortamlarda (kapalı network, yüksek güvenlikli sistemler) kurulum yapabilmek için tüm gerekli paketleri önceden indirip taşınabilir hale getirme.

---

## 📋 Gereksinimler

### İnternet Bağlantılı Ortamda (Paketleri İndirirken):
- ✅ Python 3.12
- ✅ Node.js 16+
- ✅ İnternet bağlantısı (stabil)
- ✅ ~5 GB boş disk alanı

### Hedef Ortamda (Offline Kurulum):
- ✅ Python 3.12 (önceden kurulu olmalı)
- ✅ Node.js 16+ (önceden kurulu olmalı)
- ✅ MongoDB (önceden kurulu ve çalışır olmalı)
- ✅ ~3 GB boş disk alanı

---

## 🔨 ADIM 1: Offline Installer Oluşturma (İnternete Bağlı Ortamda)

### 1.1 Script'i Çalıştırın
```
create_offline_installer.bat
```

### 1.2 Ne Yapılıyor?
Script otomatik olarak:
1. `offline_installer` klasörü oluşturur
2. **Backend paketlerini indirir** (~1.5 GB):
   - PyTorch, EasyOCR, OpenCV, NumPy vb.
   - Tüm wheel dosyaları `backend_packages\` altına
3. **Frontend paketlerini indirir** (~500 MB):
   - node_modules tüm bağımlılıklarıyla
   - `frontend_packages\node_modules.zip` olarak arşivlenir
4. **Script dosyalarını kopyalar**:
   - setup_and_start.bat
   - start_server.bat
   - requirements.txt, package.json vb.

### 1.3 Süre
- **Backend:** 5-10 dakika (PyTorch büyük bir paket)
- **Frontend:** 2-5 dakika
- **Arşivleme:** 2-3 dakika
- **TOPLAM:** ~10-20 dakika

### 1.4 Sonuç
```
offline_installer/
├── backend_packages/          # ~1.5 GB (Python wheel dosyaları)
│   ├── torch-2.2.0-*.whl
│   ├── opencv_python-*.whl
│   ├── easyocr-*.whl
│   └── ... (tüm bağımlılıklar)
├── frontend_packages/         # ~500 MB
│   └── node_modules.zip
├── scripts/
│   ├── requirements.txt
│   ├── package.json
│   ├── backend.env
│   ├── setup_and_start.bat
│   └── start_server.bat
└── README.txt
```

---

## 📦 ADIM 2: Offline Installer'ı Taşıma

### 2.1 Offline Installer Hazırlığı
1. `offline_installer` klasörünü **ZIP** olarak sıkıştırın (isteğe bağlı)
2. `offline_install.bat` dosyasını da ekleyin
3. Hedef makineye taşıma yöntemi:
   - USB disk
   - Harici HDD
   - Network paylaşımı (eğer intranet varsa)
   - DVD/Blu-ray (çok büyük projeler için)

### 2.2 Boyut Bilgisi
- **Sıkıştırılmış:** ~1.2-1.5 GB
- **Açık hali:** ~2-3 GB

---

## 🚀 ADIM 3: Hedef Makinede Offline Kurulum

### 3.1 Önkoşullar (Hedef Makinede MUTLAKA Kurulu Olmalı)

#### Python 3.12 Kontrolü
```
py --version
```
**Çıktı:** `Python 3.12.x` olmalı

Kurulu değilse:
- USB ile Python 3.12 installer'ı taşıyın
- Link: https://www.python.org/downloads/release/python-3120/
- "Add Python to PATH" işaretleyin ✅

#### Node.js Kontrolü
```
node --version
```
**Çıktı:** `v16.x.x` veya üzeri

Kurulu değilse:
- USB ile Node.js installer'ı taşıyın
- Link: https://nodejs.org/

#### MongoDB Kontrolü
```
# Windows Hizmetler (services.msc)
MongoDB servisi -> Çalışıyor olmalı
```

Kurulu değilse:
- USB ile MongoDB installer'ı taşıyın
- Link: https://www.mongodb.com/try/download/community

---

### 3.2 Kurulum Adımları

**1. Dosyaları Yerleştirin:**
```
C:\Plaka_Tanima_Sistemi\
├── offline_installer\       # Taşıdığınız klasör
├── offline_install.bat      # Kurulum script'i
└── (backend ve frontend otomatik oluşturulacak)
```

**2. Offline Kurulum Script'ini Çalıştırın:**
```
offline_install.bat
```

**3. Script Otomatik Olarak:**
- ✅ Python ve Node.js'i kontrol eder
- ✅ `backend` ve `frontend` klasörleri oluşturur
- ✅ Backend venv oluşturur
- ✅ **OFFLINE** Python paketleri yükler (internet yok!)
- ✅ **OFFLINE** node_modules açar (internet yok!)
- ✅ `.env.local` otomatik oluşturur
- ✅ MongoDB kontrolü yapar

**4. Süre:**
- Backend paket kurulumu: 3-5 dakika
- Frontend node_modules açma: 2-3 dakika
- **TOPLAM:** ~5-10 dakika

---

## ✅ ADIM 4: Servisleri Başlatma

### Otomatik Başlatma
```
start_server.bat
```

### Manuel Başlatma

**Backend:**
```
cd backend
venv\Scripts\activate
py -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Frontend:**
```
cd frontend
set PORT=3000
yarn start
```

### Tarayıcıda Açın
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001/docs

---

## 🔍 Sorun Giderme

### Hata: "Python not found"
**Sebep:** Python 3.12 kurulu değil veya PATH'e eklenmemiş
**Çözüm:** 
1. Python 3.12 kurun
2. Kurulum sırasında "Add to PATH" işaretleyin
3. Bilgisayarı yeniden başlatın

---

### Hata: "offline_installer klasörü bulunamadı"
**Sebep:** offline_installer klasörü mevcut dizinde yok
**Çözüm:** 
1. `create_offline_installer.bat` çalıştırarak oluşturun
2. Veya başka makineden kopyalayın

---

### Hata: "node_modules.zip bulunamadı"
**Sebep:** Offline installer oluşturulurken hata olmuş
**Çözüm:** 
1. İnternet bağlantılı makinede `create_offline_installer.bat` tekrar çalıştırın
2. `frontend_packages\node_modules.zip` dosyasının oluştuğunu doğrulayın

---

### Hata: "MongoDB connection error"
**Sebep:** MongoDB servisi çalışmıyor
**Çözüm:** 
1. Windows Hizmetler açın (services.msc)
2. "MongoDB" servisini bulun
3. Sağ tık > Başlat
4. Veya komut satırı: `net start MongoDB`

---

### Hata: Backend paketleri yüklenemiyor
**Sebep:** wheel dosyaları eksik veya bozuk
**Çözüm:** 
1. `offline_installer\backend_packages\` klasöründe tüm .whl dosyalarının var olduğunu kontrol edin
2. Eksikse, internet bağlantılı makinede tekrar `create_offline_installer.bat` çalıştırın

---

## 📊 Boyut Optimizasyonu

### Frontend Paketlerini Küçültmek
Eğer `node_modules.zip` çok büyükse:
```
# Sadece production bağımlılıkları
npm install --production
```

### Backend Paketlerini Küçültmek
Sadece gerekli platformlar için:
```
# Sadece Windows için indirme
pip download -r requirements.txt -d backend_packages --platform win_amd64 --only-binary=:all:
```

---

## 🎯 Kullanım Senaryoları

### Senaryo 1: Kapalı Network (Air-Gapped)
- Askeri tesisler
- Finansal kurumlar
- Yüksek güvenlikli sistemler
→ **Offline installer ideal!**

### Senaryo 2: Zayıf İnternet Bağlantısı
- Kırsal bölgeler
- Mobil kurulumlar
- Yavaş bağlantılar
→ **Paketleri bir kez indirin, çok yerde kullanın**

### Senaryo 3: Çoklu Kurulum
- 10+ makineye kurulum
- Aynı network'te tekrar tekrar indirme yerine
→ **Offline installer ile hızlı kurulum**

---

## 💡 İpuçları

1. **Güncel Tutma:**
   - Yeni versiyon çıktığında offline installer'ı yeniden oluşturun

2. **Sıkıştırma:**
   - ZIP yerine 7-Zip kullanın (daha iyi sıkıştırma)

3. **Doğrulama:**
   - Offline installer'ı başka bir makinede test edin

4. **Dokümantasyon:**
   - README.txt dosyasını mutlaka okutun

5. **Yedekleme:**
   - Offline installer'ı birden fazla yerde saklayın

---

## 📞 Destek

Sorun yaşıyorsanız:
1. README.txt dosyasını okuyun
2. Bu kılavuzu takip edin
3. Log dosyalarını kaydedin
4. Destek ekibine ulaşın

---

**Oluşturma Tarihi:** Kasım 2025  
**Versiyon:** 1.0  
**Python:** 3.12  
**Node.js:** 16+
