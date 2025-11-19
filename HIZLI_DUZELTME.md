# ⚡ Hızlı Düzeltme Rehberi

## 🔴 CRACO Hatası: 'craco' is not recognized

### Sebep
`node_modules` eksik veya tam kurulmamış. `@craco/craco` devDependency olarak kurulmalı.

### ⚡ Hızlı Çözüm (1 Dakika)

```batch
cd frontend
rmdir /s /q node_modules
yarn install
```

Yarn yoksa:
```batch
npm install --legacy-peer-deps
```

### ✅ Test
```batch
dir node_modules\.bin\craco.cmd
```
Bu dosya varsa ✅ craco kurulu

---

## 🔴 Backend: KeyError 'DB_NAME' veya 'MONGO_URL'

### Sebep
`backend/.env` dosyası eksik

### ⚡ Hızlı Çözüm (30 Saniye)

```batch
cd backend
echo MONGO_URL=mongodb://localhost:27017 > .env
echo DB_NAME=test_database >> .env
echo CORS_ORIGINS=* >> .env
```

### ✅ Test
```batch
type backend\.env
```
İçeriği görmelisiniz

---

## 🔴 MongoDB Connection Error

### Sebep
MongoDB servisi çalışmıyor

### ⚡ Hızlı Çözüm

**Yöntem 1: Services (Önerilen)**
1. `Win + R` → `services.msc`
2. "MongoDB" servisi → Sağ tık → Başlat

**Yöntem 2: Komut Satırı**
```batch
net start MongoDB
```

### ✅ Test
```batch
mongo --eval "db.version()"
```
Versiyon görmeli

---

## 🔄 TAM TEMİZ KURULUM

Tüm hatalar için evrensel çözüm:

```batch
REM 1. Temizlik
rmdir /s /q backend\venv
rmdir /s /q frontend\node_modules

REM 2. MongoDB başlat
net start MongoDB

REM 3. Kurulum
setup_and_start.bat
```

**Süre:** 5-10 dakika

---

## 🚨 ACİL DURUM: Manuel Başlatma

Setup script çalışmazsa manuel:

### Backend
```batch
cd backend
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
py -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### Frontend (Yeni Terminal)
```batch
cd frontend
yarn install
yarn start
```

---

## 📋 Kontrol Listesi

Başlatmadan önce:
- [ ] Python 3.12 kurulu (`py --version`)
- [ ] Node.js 16+ kurulu (`node --version`)
- [ ] MongoDB servisi çalışıyor (`services.msc`)
- [ ] backend/.env var (`type backend\.env`)
- [ ] frontend/node_modules/craco var

---

## 🎯 Başarı Kriterleri

### Backend
```
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8001
```

### Frontend
```
Compiled successfully!
```

### Tarayıcı
- http://localhost:3000 ✅
- http://localhost:8001/docs ✅

---

## 🔴 Offline Installer: craco eksik

### Sebep
Offline installer oluşturulurken node_modules eksik kalmış

### ⚡ Hızlı Çözüm

**İnternet bağlantılı makinede:**
```batch
cd frontend
rmdir /s /q node_modules
yarn install
cd ..
create_offline_installer.bat
```

Script otomatik craco kontrolü yapacak.

### ✅ Test
```batch
# Offline installer içinde kontrol:
dir offline_installer\frontend_packages\node_modules.zip
```

---

**Hala sorun mu var?** GitHub'dan en son versiyonu indirip temiz kurulum yapın.
