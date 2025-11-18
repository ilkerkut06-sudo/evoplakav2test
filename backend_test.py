#!/usr/bin/env python3
"""
Backend API Test Suite for Plaka Tanıma Sistemi
Tests high priority tasks from test_result.md
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
import uuid

# Backend URL from frontend/.env
BACKEND_URL = "https://plateguard-1.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session = None
        self.test_data = {
            'site_id': None,
            'blok_id': None,
            'daire_ids': [],
            'plaka_id': None,
            'kamera_id': None
        }
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
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    response_data = await response.json()
                    return response.status < 400, response_data
                    
        except Exception as e:
            return False, {"error": str(e)}

    async def test_health_check(self):
        """Test basic API health"""
        success, data = await self.make_request("GET", "/health")
        if success and data.get("status") == "healthy":
            self.log_result("API Health Check", True, "API is healthy and database connected")
        else:
            self.log_result("API Health Check", False, f"Health check failed: {data}")

    async def test_site_management(self):
        """Test Site Management - Block Editing functionality"""
        print("\n=== Site Yönetimi - Blok Düzenleme Testleri ===")
        
        # 1. Create a new site
        site_data = {
            "site_adi": "Test Sitesi Merkez",
            "adres": "İstanbul Kadıköy Test Mahallesi No:123",
            "yonetici_adi": "Ahmet Yılmaz",
            "yonetici_telefon": "0532-123-4567"
        }
        
        success, response = await self.make_request("POST", "/sites", site_data)
        if success:
            self.test_data['site_id'] = response['id']
            self.log_result("Site Oluşturma", True, f"Site ID: {response['id']}")
        else:
            self.log_result("Site Oluşturma", False, f"Site oluşturulamadı: {response}")
            return

        # 2. Create a block with 3 apartments
        blok_data = {
            "blok_adi": "A Blok",
            "daire_sayisi": 3,
            "aciklama": "Ana blok"
        }
        
        success, response = await self.make_request("POST", f"/sites/{self.test_data['site_id']}/bloklar", blok_data)
        if success:
            self.test_data['blok_id'] = response['id']
            self.log_result("Blok Oluşturma (3 daire)", True, f"Blok ID: {response['id']}")
            
            # Verify 3 apartments were created automatically
            success, site_data = await self.make_request("GET", f"/sites/{self.test_data['site_id']}")
            if success:
                blok = next((b for b in site_data['bloklar'] if b['id'] == self.test_data['blok_id']), None)
                if blok and len(blok['daireler']) == 3:
                    self.log_result("Otomatik Daire Oluşturma", True, "3 daire otomatik oluşturuldu")
                    # Store apartment IDs
                    self.test_data['daire_ids'] = [d['id'] for d in blok['daireler']]
                else:
                    self.log_result("Otomatik Daire Oluşturma", False, f"Beklenen 3 daire, bulunan: {len(blok['daireler']) if blok else 0}")
        else:
            self.log_result("Blok Oluşturma", False, f"Blok oluşturulamadı: {response}")
            return

        # 3. Edit block to increase apartments to 5 (should add 2 new apartments)
        blok_update_data = {
            "blok_adi": "A Blok",
            "daire_sayisi": 5,
            "aciklama": "Ana blok - genişletildi"
        }
        
        success, response = await self.make_request("PUT", f"/sites/{self.test_data['site_id']}/bloklar/{self.test_data['blok_id']}", blok_update_data)
        if success:
            self.log_result("Blok Düzenleme - Daire Artırma", True, "Daire sayısı 5'e çıkarıldı")
            
            # Verify 5 apartments exist now
            success, site_data = await self.make_request("GET", f"/sites/{self.test_data['site_id']}")
            if success:
                blok = next((b for b in site_data['bloklar'] if b['id'] == self.test_data['blok_id']), None)
                if blok and len(blok['daireler']) == 5:
                    self.log_result("Yeni Daire Ekleme Doğrulama", True, "2 yeni daire eklendi, toplam 5 daire")
                    # Update apartment IDs
                    self.test_data['daire_ids'] = [d['id'] for d in blok['daireler']]
                else:
                    self.log_result("Yeni Daire Ekleme Doğrulama", False, f"Beklenen 5 daire, bulunan: {len(blok['daireler']) if blok else 0}")
        else:
            self.log_result("Blok Düzenleme - Daire Artırma", False, f"Blok güncellenemedi: {response}")

        # 4. Edit block to decrease apartments to 3 (should remove empty apartments)
        blok_update_data = {
            "blok_adi": "A Blok",
            "daire_sayisi": 3,
            "aciklama": "Ana blok - küçültüldü"
        }
        
        success, response = await self.make_request("PUT", f"/sites/{self.test_data['site_id']}/bloklar/{self.test_data['blok_id']}", blok_update_data)
        if success:
            self.log_result("Blok Düzenleme - Daire Azaltma", True, "Daire sayısı 3'e düşürüldü")
            
            # Verify only 3 apartments remain (empty ones should be deleted)
            success, site_data = await self.make_request("GET", f"/sites/{self.test_data['site_id']}")
            if success:
                blok = next((b for b in site_data['bloklar'] if b['id'] == self.test_data['blok_id']), None)
                if blok and len(blok['daireler']) == 3:
                    self.log_result("Boş Daire Silme Doğrulama", True, "Boş daireler silindi, 3 daire kaldı")
                else:
                    self.log_result("Boş Daire Silme Doğrulama", False, f"Beklenen 3 daire, bulunan: {len(blok['daireler']) if blok else 0}")
        else:
            self.log_result("Blok Düzenleme - Daire Azaltma", False, f"Blok güncellenemedi: {response}")

        # 5. Change block name
        blok_update_data = {
            "blok_adi": "A Blok - Yenilendi",
            "daire_sayisi": 3,
            "aciklama": "Ana blok - isim değiştirildi"
        }
        
        success, response = await self.make_request("PUT", f"/sites/{self.test_data['site_id']}/bloklar/{self.test_data['blok_id']}", blok_update_data)
        if success and response.get('blok_adi') == "A Blok - Yenilendi":
            self.log_result("Blok Adı Değiştirme", True, "Blok adı başarıyla değiştirildi")
        else:
            self.log_result("Blok Adı Değiştirme", False, f"Blok adı değiştirilemedi: {response}")

    async def test_plate_management(self):
        """Test Plate Management - Plate Moving Logic"""
        print("\n=== Plaka Yönetimi - Plaka Taşıma Testleri ===")
        
        if not self.test_data['site_id'] or not self.test_data['blok_id'] or not self.test_data['daire_ids']:
            self.log_result("Plaka Testleri", False, "Site/Blok/Daire verileri eksik")
            return

        # 1. Create a plate and assign to first apartment
        plaka_data = {
            "plaka_no": "34ABC123",
            "site_id": self.test_data['site_id'],
            "blok_id": self.test_data['blok_id'],
            "daire_id": self.test_data['daire_ids'][0],
            "arac_tipi": "Sedan",
            "durum": "Tanımlı",
            "not_": "Test plakası"
        }
        
        success, response = await self.make_request("POST", "/plates", plaka_data)
        if success:
            self.test_data['plaka_id'] = response['id']
            self.log_result("Plaka Oluşturma", True, f"Plaka ID: {response['id']}, Daire: {self.test_data['daire_ids'][0]}")
        else:
            self.log_result("Plaka Oluşturma", False, f"Plaka oluşturulamadı: {response}")
            return

        # 2. Move plate to different apartment
        if len(self.test_data['daire_ids']) > 1:
            plaka_update_data = {
                "daire_id": self.test_data['daire_ids'][1],
                "not_": "Plaka taşındı"
            }
            
            success, response = await self.make_request("PUT", f"/plates/{self.test_data['plaka_id']}", plaka_update_data)
            if success and response.get('daire_id') == self.test_data['daire_ids'][1]:
                self.log_result("Plaka Taşıma", True, f"Plaka yeni daireye taşındı: {self.test_data['daire_ids'][1]}")
                
                # 3. Verify old apartment reference is cleaned (this would be checked in frontend logic)
                # For backend, we just verify the plate is correctly updated
                success, plate_data = await self.make_request("GET", f"/plates/{self.test_data['plaka_id']}")
                if success and plate_data.get('daire_id') == self.test_data['daire_ids'][1]:
                    self.log_result("Plaka Referans Güncelleme", True, "Plaka referansı doğru güncellendi")
                else:
                    self.log_result("Plaka Referans Güncelleme", False, "Plaka referansı güncellenemedi")
            else:
                self.log_result("Plaka Taşıma", False, f"Plaka taşınamadı: {response}")

        # 4. Test plate check functionality
        success, response = await self.make_request("GET", "/plates/check/34ABC123")
        if success and response.get('found') and response.get('durum') == 'Tanımlı':
            self.log_result("Plaka Kontrol", True, "Plaka durumu doğru kontrol edildi")
        else:
            self.log_result("Plaka Kontrol", False, f"Plaka kontrol hatası: {response}")

    async def test_camera_management(self):
        """Test Camera Management"""
        print("\n=== Kamera Yönetimi Testleri ===")
        
        # 1. Create camera with empty bagli_kapi_id
        kamera_data = {
            "kamera_adi": "Ana Giriş Kamerası",
            "kamera_tipi": "RTSP",
            "giris_cikis": "Giriş",
            "main_stream_url": "rtsp://192.168.1.100:554/stream1",
            "sub_stream_url": "rtsp://192.168.1.100:554/stream2",
            "onvif_ip": "192.168.1.100",
            "onvif_port": 80,
            "onvif_kullanici": "admin",
            "onvif_sifre": "123456",
            "bagli_kapi_id": None,  # Empty as specified
            "aktif": True,
            "plaka_tanima_aktif": True
        }
        
        success, response = await self.make_request("POST", "/cameras", kamera_data)
        if success:
            self.test_data['kamera_id'] = response['id']
            self.log_result("Kamera Oluşturma", True, f"Kamera ID: {response['id']}")
        else:
            self.log_result("Kamera Oluşturma", False, f"Kamera oluşturulamadı: {response}")
            return

        # 2. Get camera list
        success, response = await self.make_request("GET", "/cameras")
        if success and isinstance(response, list) and len(response) > 0:
            self.log_result("Kamera Listesi", True, f"{len(response)} kamera bulundu")
        else:
            self.log_result("Kamera Listesi", False, f"Kamera listesi alınamadı: {response}")

        # 3. Edit camera
        kamera_update_data = {
            "kamera_adi": "Ana Giriş Kamerası - Güncellendi",
            "giris_cikis": "Ortak",
            "aktif": True
        }
        
        success, response = await self make_request("PUT", f"/cameras/{self.test_data['kamera_id']}", kamera_update_data)
        if success and response.get('kamera_adi') == "Ana Giriş Kamerası - Güncellendi":
            self.log_result("Kamera Düzenleme", True, "Kamera başarıyla güncellendi")
        else:
            self.log_result("Kamera Düzenleme", False, f"Kamera güncellenemedi: {response}")

    async def test_settings_management(self):
        """Test Settings Management"""
        print("\n=== Ayarlar Yönetimi Testleri ===")
        
        # 1. Get current settings
        success, response = await self.make_request("GET", "/settings")
        if success:
            self.log_result("Ayarları Çekme", True, f"OCR Motor: {response.get('ocr_motor', 'N/A')}")
            current_ocr = response.get('ocr_motor', 'paddleocr')
        else:
            self.log_result("Ayarları Çekme", False, f"Ayarlar alınamadı: {response}")
            return

        # 2. Change OCR engine
        new_ocr = "easyocr" if current_ocr == "paddleocr" else "paddleocr"
        settings_update = {
            "ocr_motor": new_ocr,
            "ai_duzeltme_aktif": True,
            "yolo_confidence": 0.7
        }
        
        success, response = await self.make_request("PUT", "/settings", settings_update)
        if success and response.get('ocr_motor') == new_ocr:
            self.log_result("OCR Motor Değiştirme", True, f"OCR motor {new_ocr} olarak değiştirildi")
        else:
            self.log_result("OCR Motor Değiştirme", False, f"OCR motor değiştirilemedi: {response}")

        # 3. Save settings and verify
        success, response = await self.make_request("GET", "/settings")
        if success and response.get('ocr_motor') == new_ocr:
            self.log_result("Ayarları Kaydetme", True, "Ayarlar başarıyla kaydedildi")
        else:
            self.log_result("Ayarları Kaydetme", False, "Ayarlar kaydedilemedi")

    async def cleanup_test_data(self):
        """Clean up test data"""
        print("\n=== Test Verilerini Temizleme ===")
        
        # Delete plate
        if self.test_data['plaka_id']:
            success, _ = await self.make_request("DELETE", f"/plates/{self.test_data['plaka_id']}")
            self.log_result("Plaka Silme", success, "Test plakası silindi" if success else "Plaka silinemedi")

        # Delete camera
        if self.test_data['kamera_id']:
            success, _ = await self.make_request("DELETE", f"/cameras/{self.test_data['kamera_id']}")
            self.log_result("Kamera Silme", success, "Test kamerası silindi" if success else "Kamera silinemedi")

        # Delete site (this will cascade delete blocks and apartments)
        if self.test_data['site_id']:
            success, _ = await self.make_request("DELETE", f"/sites/{self.test_data['site_id']}")
            self.log_result("Site Silme", success, "Test sitesi silindi" if success else "Site silinemedi")

    async def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Backend API Testleri Başlatılıyor...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        await self.test_health_check()
        await self.test_site_management()
        await self.test_plate_management()
        await self.test_camera_management()
        await self.test_settings_management()
        await self.cleanup_test_data()
        
        print("\n" + "=" * 60)
        print("📊 TEST SONUÇLARI")
        print("=" * 60)
        print(f"✅ Başarılı: {self.results['passed']}")
        print(f"❌ Başarısız: {self.results['failed']}")
        print(f"📈 Başarı Oranı: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results['errors']:
            print("\n🔍 HATALAR:")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        return self.results['failed'] == 0

async def main():
    """Main test runner"""
    async with BackendTester() as tester:
        success = await tester.run_all_tests()
        return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))