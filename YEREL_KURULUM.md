# 🚀 Plaka Tanıma Sistemi - Yerel Kurulum Rehberi

## ⚠️ ÖNEMLİ: Python 3.14 İçin Düzeltme Yapıldı

**Sorun çözüldü:** `paddleocr` ve `scikit-image` paketleri Python 3.14 ile uyumsuzluk gösteriyordu. Bu paketler kaldırıldı ve sistem artık sadece **EasyOCR** kullanıyor.

---

## 📋 Gereksinimler

1. **Python 3.10 - 3.14** (Kurulu olanı kontrol: `py --version`)
2. **Node.js 16+** (Kurulu olanı kontrol: `node --version`)
3. **MongoDB Community Edition**
   - İndir: https://www.mongodb.com/try/download/community
   - Kurulum sonrası MongoDB servisinin çalıştığından emin olun

---

## 🔧 Kurulum Adımları

### 1️⃣ Projeyi İndirin
```bash
# GitHub'dan klonlayın veya ZIP olarak indirin
```

### 2️⃣ Eski Virtual Environment'ı Silin (Önemli!)
Eğer daha önce kurulum denemişseniz:
```bash
# backend/venv klasörünü tamamen silin
# Windows Explorer'dan sağ tık > Sil
# veya:
rmdir /s backend\venv
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

### Hata: "Python not found"
- Python kurulu mu kontrol edin: `py --version`
- Değilse: https://www.python.org/downloads/

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
