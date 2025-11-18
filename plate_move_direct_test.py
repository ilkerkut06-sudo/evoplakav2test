#!/usr/bin/env python3
"""
Plaka Taşıma Mantığı Direkt Test - 06DBN786 plakasını Daire 3'ten Daire 1'e taşıma
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://plateguard-1.preview.emergentagent.com/api"

# Bilinen ID'ler (check_site_structure.py çıktısından)
SITE_ID = "d89aabf6-a7b6-454c-aad5-11bacffa80c9"
BLOK_ID = "c5a5f488-621d-4a50-99ce-da3578193dc5"
DAIRE_1_ID = "6c3472f1-24ef-40db-ad2d-9b56cbc77e20"  # Daire 1
DAIRE_3_ID = "62878c31-42b0-44d8-a529-e000318ca6c2"  # Daire 3 (mevcut)
PLATE_ID = "9515bf6d-c3c4-467d-beff-db34aa892608"     # 06DBN786 plaka ID

class DirectPlateTester:
    def __init__(self):
        self.session = None
        self.results = {'passed': 0, 'failed': 0, 'errors': []}

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def log_result(self, test_name: str, success: bool, message: str = ""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")

    async def make_request(self, method: str, endpoint: str, data: dict = None):
        try:
            url = f"{BACKEND_URL}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    return response.status < 400, await response.json()
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data) as response:
                    return response.status < 400, await response.json()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    return response.status < 400, await response.json()
                    
        except Exception as e:
            return False, {"error": str(e)}

    async def get_apartment_info(self, daire_id: str):
        """Daire bilgilerini al"""
        success, site_data = await self.make_request("GET", f"/sites/{SITE_ID}")
        if not success:
            return None
            
        for blok in site_data.get('bloklar', []):
            for daire in blok.get('daireler', []):
                if daire['id'] == daire_id:
                    return daire
        return None

    async def test_plate_moving(self):
        """06DBN786 plakasını Daire 3'ten Daire 1'e taşı"""
        print("\n=== PLAKA TAŞIMA TESTİ ===")
        
        # 1. Başlangıç durumunu kontrol et
        print("1. Başlangıç Durumu Kontrolü:")
        
        # Plaka bilgisini al
        success, plate_data = await self.make_request("GET", f"/plates/{PLATE_ID}")
        if success:
            current_daire = plate_data.get('daire_id')
            self.log_result("Plaka Mevcut Durumu", True, f"06DBN786 şu anda daire ID: {current_daire}")
        else:
            self.log_result("Plaka Mevcut Durumu", False, f"Plaka bilgisi alınamadı: {plate_data}")
            return

        # Daire 3 bilgilerini al
        daire_3_info = await self.get_apartment_info(DAIRE_3_ID)
        if daire_3_info:
            self.log_result("Daire 3 Başlangıç Bilgisi", True, 
                          f"Daire 3: {daire_3_info.get('isim_soyisim', 'Boş')} - {daire_3_info.get('telefon', '-')}")

        # Daire 1 bilgilerini al
        daire_1_info = await self.get_apartment_info(DAIRE_1_ID)
        if daire_1_info:
            self.log_result("Daire 1 Başlangıç Bilgisi", True, 
                          f"Daire 1: {daire_1_info.get('isim_soyisim', 'Boş')} - {daire_1_info.get('telefon', '-')}")

        # 2. Plakayı Daire 1'e taşı
        print("\n2. Plaka Taşıma İşlemi:")
        
        update_data = {
            "daire_id": DAIRE_1_ID,
            "site_id": SITE_ID,
            "blok_id": BLOK_ID,
            "not_": "Daire 1'e taşındı - Test işlemi"
        }
        
        success, response = await self.make_request("PUT", f"/plates/{PLATE_ID}", update_data)
        if success:
            self.log_result("Plaka Taşıma İşlemi", True, "06DBN786 başarıyla Daire 1'e taşındı")
        else:
            self.log_result("Plaka Taşıma İşlemi", False, f"Taşıma başarısız: {response}")
            return

        # 3. Taşıma sonrası doğrulama
        print("\n3. Taşıma Sonrası Doğrulama:")
        
        # Plaka bilgisini tekrar kontrol et
        success, updated_plate = await self.make_request("GET", f"/plates/{PLATE_ID}")
        if success and updated_plate.get('daire_id') == DAIRE_1_ID:
            self.log_result("Plaka Yeni Konum Doğrulama", True, "Plaka Daire 1'de doğrulandı")
        else:
            self.log_result("Plaka Yeni Konum Doğrulama", False, "Plaka konumu doğrulanamadı")

        # 4. Daire bilgilerini kontrol et
        print("\n4. Daire Bilgileri Kontrolü:")
        
        # Eski daire (Daire 3) - boş olmalı
        daire_3_after = await self.get_apartment_info(DAIRE_3_ID)
        if daire_3_after:
            name_3 = daire_3_after.get('isim_soyisim', 'Boş')
            phone_3 = daire_3_after.get('telefon', '-')
            
            if name_3 in ['Boş', ''] and phone_3 in ['-', '']:
                self.log_result("Eski Daire (Daire 3) Temizleme", True, f"Daire 3 temizlendi: '{name_3}' - '{phone_3}'")
            else:
                self.log_result("Eski Daire (Daire 3) Temizleme", False, f"Daire 3 temizlenmedi: '{name_3}' - '{phone_3}'")

        # Yeni daire (Daire 1) - YAHYA bilgisi olmalı
        daire_1_after = await self.get_apartment_info(DAIRE_1_ID)
        if daire_1_after:
            name_1 = daire_1_after.get('isim_soyisim', 'Boş')
            phone_1 = daire_1_after.get('telefon', '-')
            
            if 'YAHYA' in name_1.upper():
                self.log_result("Yeni Daire (Daire 1) Bilgi Güncelleme", True, f"Daire 1: '{name_1}' - '{phone_1}'")
            else:
                self.log_result("Yeni Daire (Daire 1) Bilgi Güncelleme", False, f"Daire 1'de YAHYA bilgisi yok: '{name_1}' - '{phone_1}'")

    async def add_test_logs(self):
        """6 adet test logu ekle"""
        print("\n=== TEST LOGLARI EKLEME ===")
        
        test_logs = [
            # 3 adet "Tanımlı"
            {"plaka_no": "34ABC123", "kamera_adi": "Ana Giriş", "kamera_id": "test-camera-1", "durum": "Tanımlı", "giris_cikis": "Giriş", "fotograf_url": None},
            {"plaka_no": "06XYZ789", "kamera_adi": "Arka Giriş", "kamera_id": "test-camera-2", "durum": "Tanımlı", "giris_cikis": "Çıkış", "fotograf_url": None},
            {"plaka_no": "35DEF456", "kamera_adi": "Yan Kapı", "kamera_id": "test-camera-3", "durum": "Tanımlı", "giris_cikis": "Giriş", "fotograf_url": None},
            # 2 adet "Misafir"
            {"plaka_no": "07GHI321", "kamera_adi": "Ana Giriş", "kamera_id": "test-camera-1", "durum": "Misafir", "giris_cikis": "Giriş", "fotograf_url": None},
            {"plaka_no": "16JKL654", "kamera_adi": "Arka Giriş", "kamera_id": "test-camera-2", "durum": "Misafir", "giris_cikis": "Çıkış", "fotograf_url": None},
            # 1 adet "Yasaklı"
            {"plaka_no": "99ZZZ999", "kamera_adi": "Ana Giriş", "kamera_id": "test-camera-1", "durum": "Yasaklı", "giris_cikis": "Giriş", "fotograf_url": None}
        ]
        
        for i, log_data in enumerate(test_logs, 1):
            success, response = await self.make_request("POST", "/logs", log_data)
            if success:
                self.log_result(f"Test Log {i} ({log_data['durum']})", True, 
                              f"Plaka: {log_data['plaka_no']}, Kamera: {log_data['kamera_adi']}")
            else:
                self.log_result(f"Test Log {i} ({log_data['durum']})", False, f"Log eklenemedi: {response}")

    async def run_tests(self):
        print("🚀 Plaka Taşıma Mantığı Direkt Test")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        await self.test_plate_moving()
        await self.add_test_logs()
        
        print("\n" + "=" * 60)
        print("📊 TEST SONUÇLARI")
        print("=" * 60)
        print(f"✅ Başarılı: {self.results['passed']}")
        print(f"❌ Başarısız: {self.results['failed']}")
        
        if self.results['passed'] + self.results['failed'] > 0:
            success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100)
            print(f"📈 Başarı Oranı: {success_rate:.1f}%")
        
        if self.results['errors']:
            print("\n🔍 HATALAR:")
            for error in self.results['errors']:
                print(f"  • {error}")

async def main():
    async with DirectPlateTester() as tester:
        await tester.run_tests()

if __name__ == "__main__":
    asyncio.run(main())