# 🚀 Plaka Tanıma Sistemi - Yerel Kurulum Rehberi

## ⚠️ ÖNEMLİ: Python 3.14 İçin Düzeltme Yapıldı

**Sorun çözüldü:** `paddleocr` ve `scikit-image` paketleri Python 3.14 ile uyumsuzluk gösteriyordu. Bu paketler kaldırıldı ve sistem artık sadece **EasyOCR** kullanıyor.

---

## 📋 Gereksinimler

1. **Python 3.12 veya 3.13** ⚠️ ZORUNLU
   - Python 3.14 AI/ML paketleriyle uyumlu değil
   - Python 3.11 ve altı bazı paketler için eski
   - **Önerilen:** Python 3.12.x (En stabil)
   - İndir: https://www.python.org/downloads/
   - Kurulu olanı kontrol: `py --version`
   
2. **Node.js 16+** (Kurulu olanı kontrol: `node --version`)
   - İsteğe bağlı: Yarn package manager (önerilir)
   - Yarn kurulumu: `npm install -g yarn`
   - Yarn yoksa otomatik olarak npm kullanılır

3. **MongoDB Community Edition**
   - İndir: https://www.mongodb.com/try/download/community
   - Kurulum sonrası MongoDB servisinin çalıştığından emin olun

---

## 🔧 Kurulum Adımları

### 1️⃣ Python 3.12 veya 3.13 Kurun
1. Mevcut Python sürümünüzü kontrol edin:
   ```
   py --version
   ```

2. Eğer Python 3.14 veya başka sürüm varsa:
   - Python 3.12 indirin: https://www.python.org/downloads/release/python-3120/
   - **Windows installer (64-bit)** seçin
   - Kurulum sırasında "Add Python to PATH" işaretleyin ✅
   
3. Kurulum sonrası kontrol:
   ```
   py --version
   ```
   Çıktı: `Python 3.12.x` veya `Python 3.13.x` olmalı

### 2️⃣ Eski Virtual Environment'ı Silin (Kritik!)
Eğer daha önce kurulum denemişseniz:
```bash
# backend/venv klasörünü TAMAMEN silin
# Windows Explorer'dan sağ tık > Sil
# veya komut satırından:
rmdir /s /q backend\venv
```

### 3️⃣ Frontend .env Dosyasını Oluşturun
**Önemli:** Frontend klasöründe `.env.local` dosyası oluşturun:

```
frontend/.env.local
```

İçeriği:
```
REACT_APP_BACKEND_URL=http://localhost:8001
```

### 4️⃣ Setup Script'ini Çalıştırın
Proje ana klasöründe:
```bash
setup_and_start.bat
```

Bu script otomatik olarak:
- Python ve Node.js varlığını kontrol eder
- Backend için virtual environment oluşturur
- Tüm bağımlılıkları kurar
- Her iki servisi başlatır

---

## 🎯 Manuel Başlatma (İsteğe Bağlı)

Kurulumdan sonra servisleri manuel başlatmak için:
```bash
start_server.bat
```

---

## ✅ Kurulum Doğrulama

Tarayıcınızda otomatik açılacak:
- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8001/docs

---

## 🐛 Sorun Giderme

### Hata: Pillow/PyTorch/NumPy derleme hatası
**Sebep:** Python 3.14 veya uyumsuz sürüm kullanıyorsunuz
**Çözüm:**
1. Python 3.12 veya 3.13 kurun
2. `backend\venv` klasörünü tamamen silin
3. `setup_and_start.bat` dosyasını yeniden çalıştırın

### Hata: "Python not found"
- Python kurulu mu kontrol edin: `py --version`
- Python 3.12 veya 3.13 kurulu olmalı
- İndir: https://www.python.org/downloads/release/python-3120/

### Hata: "Node.js not found"
- Node.js kurulu mu kontrol edin: `node --version`
- Değilse: https://nodejs.org/

### Hata: MongoDB bağlantı hatası
- MongoDB servisinin çalıştığından emin olun
- Windows Hizmetler'de "MongoDB" servisini kontrol edin
- Varsayılan port: 27017

### Hata: "Port already in use"
- 8001 ve 3000 portlarının boş olduğundan emin olun
- Eski server pencerelerini kapatın

### Hata: Backend paket kurulumu başarısız
1. `backend/venv` klasörünü silin
2. `setup_and_start.bat` dosyasını yeniden çalıştırın

### Hata: Frontend dependency conflict (date-fns)
**Sebep:** npm peer dependency uyarısı
**Çözüm:**
1. Script otomatik olarak `--legacy-peer-deps` kullanır
2. Veya Yarn kurun: `npm install -g yarn`
3. `frontend/node_modules` klasörünü silin ve tekrar deneyin

---

## 📦 Değişiklikler (v1.1)

✅ **Kaldırılanlar:**
- `paddleocr` (Python 3.14 uyumsuzluğu)
- `scikit-image` (derleme hatası)
- `shapely` (gereksiz bağımlılık)

✅ **Mevcut OCR Motoru:**
- `easyocr` - Türkçe ve tüm dillerde plaka tanıma destekli

---

## 💡 İpuçları

- **Webcam kullanımı:** Kamera Yönetimi sayfasında webcam index'i seçebilirsiniz (0, 1, 2...)
- **Performans:** İlk OCR işlemi yavaş olabilir (model yükleniyor)
- **Test:** Sistemin çalıştığını doğrulamak için Dashboard'a gidin ve test plakası girin

---

## 📞 Destek

Sorun yaşıyorsanız:
1. `backend\venv` klasörünü silip yeniden deneyin
2. Hata loglarını kaydedin
3. GitHub'da issue açın veya destek ekibine ulaşın

---

**Güncelleme Tarihi:** 18 Kasım 2025
**Versiyon:** 1.1 (Python 3.14 Uyumlu)
