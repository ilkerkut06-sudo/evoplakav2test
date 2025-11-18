#!/usr/bin/env python3
"""
Plaka Taşıma Mantığı ve Test Logları Ekleme Testi
Özel test senaryosu: 06DBN786 plakasını Daire 3'ten Daire 1'e taşıma
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
import uuid

# Backend URL from frontend/.env
BACKEND_URL = "https://siteplates.preview.emergentagent.com/api"

class PlateMoveTester:
    def __init__(self):
        self.session = None
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }

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

    async def make_request(self, method: str, endpoint: str, data: Dict = None) -> tuple[bool, Dict]:
        """Make HTTP request and return (success, response_data)"""
        try:
            url = f"{BACKEND_URL}{endpoint}"
            
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data
                    
        except Exception as e:
            return False, {"error": str(e)}

    async def find_plate_06DBN786(self):
        """06DBN786 plakasını bul"""
        print("\n=== 06DBN786 Plakasını Arama ===")
        
        # Tüm plakaları çek
        success, plates = await self.make_request("GET", "/plates")
        if not success:
            self.log_result("Plaka Listesi Çekme", False, f"Plakalar alınamadı: {plates}")
            return None
            
        # 06DBN786 plakasını bul
        target_plate = None
        for plate in plates:
            if plate.get('plaka_no') == '06DBN786':
                target_plate = plate
                break
                
        if target_plate:
            self.log_result("06DBN786 Plakası Bulma", True, f"Plaka bulundu - ID: {target_plate['id']}, Daire: {target_plate['daire_id']}")
            return target_plate
        else:
            self.log_result("06DBN786 Plakası Bulma", False, "06DBN786 plakası bulunamadı")
            return None

    async def get_apartment_info(self, site_id: str, daire_id: str):
        """Daire bilgilerini al"""
        success, site_data = await self.make_request("GET", f"/sites/{site_id}")
        if not success:
            return None
            
        # Daire bilgisini bul
        for blok in site_data.get('bloklar', []):
            for daire in blok.get('daireler', []):
                if daire['id'] == daire_id:
                    return daire
        return None

    async def find_daire_1(self, site_id: str):
        """Daire 1'i bul"""
        success, site_data = await self.make_request("GET", f"/sites/{site_id}")
        if not success:
            return None
            
        # Daire 1'i bul (daire_no = 1)
        for blok in site_data.get('bloklar', []):
            for daire in blok.get('daireler', []):
                if daire.get('daire_no') == 1:
                    return daire
        return None

    async def test_plate_moving_logic(self):
        """Plaka taşıma mantığını test et"""
        print("\n=== PLAKA TAŞIMA MANTIĞI TESTİ ===")
        
        # 1. 06DBN786 plakasını bul
        plate = await self.find_plate_06DBN786()
        if not plate:
            return
            
        original_daire_id = plate['daire_id']
        site_id = plate['site_id']
        blok_id = plate['blok_id']
        plate_id = plate['id']
        
        # 2. Orijinal daire bilgilerini al (Daire 3 - YAHYA)
        original_daire = await self.get_apartment_info(site_id, original_daire_id)
        if original_daire:
            self.log_result("Orijinal Daire Bilgisi", True, 
                          f"Daire {original_daire.get('daire_no')}: {original_daire.get('isim_soyisim', 'Boş')} - {original_daire.get('telefon', '-')}")
        
        # 3. Daire 1'i bul
        target_daire = await self.find_daire_1(site_id)
        if not target_daire:
            self.log_result("Daire 1 Bulma", False, "Daire 1 bulunamadı")
            return
            
        target_daire_id = target_daire['id']
        self.log_result("Daire 1 Bulma", True, f"Daire 1 ID: {target_daire_id}")
        
        # 4. Plakayı Daire 1'e taşı
        update_data = {
            "daire_id": target_daire_id,
            "site_id": site_id,
            "blok_id": blok_id,
            "not_": "Daire 1'e taşındı - Test"
        }
        
        success, response = await self.make_request("PUT", f"/plates/{plate_id}", update_data)
        if success:
            self.log_result("Plaka Taşıma", True, f"06DBN786 plakası Daire 1'e taşındı")
            
            # 5. Taşıma sonrası doğrulama
            success, updated_plate = await self.make_request("GET", f"/plates/{plate_id}")
            if success and updated_plate.get('daire_id') == target_daire_id:
                self.log_result("Plaka Taşıma Doğrulama", True, "Plaka başarıyla Daire 1'e taşındı")
                
                # 6. Eski daire bilgilerini kontrol et (Daire 3 - boş olmalı)
                old_daire = await self.get_apartment_info(site_id, original_daire_id)
                if old_daire:
                    old_name = old_daire.get('isim_soyisim', 'Boş')
                    old_phone = old_daire.get('telefon', '-')
                    
                    if old_name in ['Boş', ''] and old_phone in ['-', '']:
                        self.log_result("Eski Daire Temizleme", True, f"Daire {old_daire.get('daire_no')} temizlendi: {old_name} - {old_phone}")
                    else:
                        self.log_result("Eski Daire Temizleme", False, f"Daire {old_daire.get('daire_no')} temizlenmedi: {old_name} - {old_phone}")
                
                # 7. Yeni daire bilgilerini kontrol et (Daire 1 - YAHYA olmalı)
                new_daire = await self.get_apartment_info(site_id, target_daire_id)
                if new_daire:
                    new_name = new_daire.get('isim_soyisim', 'Boş')
                    new_phone = new_daire.get('telefon', '-')
                    
                    if 'YAHYA' in new_name.upper():
                        self.log_result("Yeni Daire Bilgi Güncelleme", True, f"Daire 1: {new_name} - {new_phone}")
                    else:
                        self.log_result("Yeni Daire Bilgi Güncelleme", False, f"Daire 1'de YAHYA bilgisi bulunamadı: {new_name} - {new_phone}")
                        
            else:
                self.log_result("Plaka Taşıma Doğrulama", False, "Plaka taşıma doğrulanamadı")
        else:
            self.log_result("Plaka Taşıma", False, f"Plaka taşınamadı: {response}")

    async def add_test_logs(self):
        """6 adet test logu ekle"""
        print("\n=== TEST LOGLARI EKLEME ===")
        
        # Test logları
        test_logs = [
            # 3 adet "Tanımlı" durum
            {
                "plaka_no": "34ABC123",
                "kamera_adi": "Ana Giriş",
                "kamera_id": "test-camera-1",
                "durum": "Tanımlı",
                "giris_cikis": "Giriş",
                "fotograf_url": None
            },
            {
                "plaka_no": "06XYZ789",
                "kamera_adi": "Arka Giriş",
                "kamera_id": "test-camera-2",
                "durum": "Tanımlı",
                "giris_cikis": "Çıkış",
                "fotograf_url": None
            },
            {
                "plaka_no": "35DEF456",
                "kamera_adi": "Yan Kapı",
                "kamera_id": "test-camera-3",
                "durum": "Tanımlı",
                "giris_cikis": "Giriş",
                "fotograf_url": None
            },
            # 2 adet "Misafir" durum
            {
                "plaka_no": "07GHI321",
                "kamera_adi": "Ana Giriş",
                "kamera_id": "test-camera-1",
                "durum": "Misafir",
                "giris_cikis": "Giriş",
                "fotograf_url": None
            },
            {
                "plaka_no": "16JKL654",
                "kamera_adi": "Arka Giriş",
                "kamera_id": "test-camera-2",
                "durum": "Misafir",
                "giris_cikis": "Çıkış",
                "fotograf_url": None
            },
            # 1 adet "Yasaklı" durum
            {
                "plaka_no": "99ZZZ999",
                "kamera_adi": "Ana Giriş",
                "kamera_id": "test-camera-1",
                "durum": "Yasaklı",
                "giris_cikis": "Giriş",
                "fotograf_url": None
            }
        ]
        
        # Her logu ekle
        for i, log_data in enumerate(test_logs, 1):
            success, response = await self.make_request("POST", "/logs", log_data)
            if success:
                self.log_result(f"Test Log {i} ({log_data['durum']})", True, 
                              f"Plaka: {log_data['plaka_no']}, Kamera: {log_data['kamera_adi']}")
            else:
                self.log_result(f"Test Log {i} ({log_data['durum']})", False, 
                              f"Log eklenemedi: {response}")

    async def run_tests(self):
        """Tüm testleri çalıştır"""
        print("🚀 Plaka Taşıma ve Test Logları Testi Başlatılıyor...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        await self.test_plate_moving_logic()
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
        
        return self.results['failed'] == 0

async def main():
    """Main test runner"""
    async with PlateMoveTester() as tester:
        success = await tester.run_tests()
        return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))