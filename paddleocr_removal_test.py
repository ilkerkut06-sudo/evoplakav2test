#!/usr/bin/env python3
"""
PaddleOCR Kaldırma Sonrası Backend Test
PaddleOCR kaldırıldıktan sonra sistemin temel backend fonksiyonlarının hala çalıştığını doğrular.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Backend URL from frontend/.env
BACKEND_URL = "https://siteplates.preview.emergentagent.com/api"

class PaddleOCRRemovalTester:
    def __init__(self):
        self.session = None
        self.test_data = {
            'site_id': None,
            'blok_id': None,
            'daire_ids': [],
            'plaka_id': None
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

    async def test_1_sistem_ayarlari_kontrolu(self):
        """1. Sistem Ayarları Kontrolü"""
        print("\n=== 1. Sistem Ayarları Kontrolü ===")
        
        # GET /api/settings endpoint'ine istek at
        success, response = await self.make_request("GET", "/settings")
        
        if not success:
            self.log_result("GET /api/settings", False, f"Settings endpoint'i erişilemez: {response}")
            return
        
        # Response status 200 olmalı ve ocr_motor field'ının "easyocr" olduğunu doğrula
        if response.get('ocr_motor') == 'easyocr':
            self.log_result("OCR Motor Kontrolü", True, "OCR motor 'easyocr' olarak ayarlı")
        else:
            self.log_result("OCR Motor Kontrolü", False, f"OCR motor beklenen 'easyocr' değil, mevcut: {response.get('ocr_motor')}")

    async def test_2_site_blok_daire_crud(self):
        """2. Site & Blok & Daire CRUD"""
        print("\n=== 2. Site & Blok & Daire CRUD ===")
        
        # POST /api/site: Yeni bir site oluştur
        site_data = {
            "site_adi": "Test Sitesi PaddleOCR Fix",
            "adres": "İstanbul Test Mahallesi No:456",
            "yonetici_adi": "Test Yönetici",
            "yonetici_telefon": "0532-999-8877"
        }
        
        success, response = await self.make_request("POST", "/sites", site_data)
        if success:
            self.test_data['site_id'] = response['id']
            self.log_result("Site Oluşturma", True, f"Site oluşturuldu - ID: {response['id']}")
        else:
            self.log_result("Site Oluşturma", False, f"Site oluşturulamadı: {response}")
            return

        # POST /api/site/blok: Oluşturulan siteye 1 blok ekle
        blok_data = {
            "blok_adi": "A Blok",
            "daire_sayisi": 2,
            "aciklama": "Test bloku"
        }
        
        success, response = await self.make_request("POST", f"/sites/{self.test_data['site_id']}/bloklar", blok_data)
        if success:
            self.test_data['blok_id'] = response['id']
            self.log_result("Blok Oluşturma", True, f"A Blok oluşturuldu - ID: {response['id']}, 2 daire ile")
        else:
            self.log_result("Blok Oluşturma", False, f"Blok oluşturulamadı: {response}")
            return

        # GET /api/site: Site listesini çek, yeni oluşturulan sitenin döndüğünü doğrula
        success, response = await self.make_request("GET", "/sites")
        if success:
            site_found = any(site['id'] == self.test_data['site_id'] for site in response)
            if site_found:
                self.log_result("Site Listesi Kontrolü", True, "Yeni oluşturulan site listede bulundu")
            else:
                self.log_result("Site Listesi Kontrolü", False, "Yeni oluşturulan site listede bulunamadı")
        else:
            self.log_result("Site Listesi Kontrolü", False, f"Site listesi alınamadı: {response}")

        # Daire ID'lerini al
        success, site_detail = await self.make_request("GET", f"/sites/{self.test_data['site_id']}")
        if success:
            blok = next((b for b in site_detail['bloklar'] if b['id'] == self.test_data['blok_id']), None)
            if blok and len(blok['daireler']) == 2:
                self.test_data['daire_ids'] = [d['id'] for d in blok['daireler']]
                self.log_result("Daire Kontrolü", True, "2 daire otomatik oluşturuldu")
            else:
                self.log_result("Daire Kontrolü", False, f"Beklenen 2 daire, bulunan: {len(blok['daireler']) if blok else 0}")

    async def test_3_plaka_olusturma_senkronizasyon(self):
        """3. Plaka Oluşturma ve Daire Senkronizasyonu"""
        print("\n=== 3. Plaka Oluşturma ve Daire Senkronizasyonu ===")
        
        if not self.test_data['daire_ids']:
            self.log_result("Plaka Oluşturma", False, "Daire ID'leri bulunamadı")
            return

        # POST /api/plates: Blok içindeki 1. daireye bir plaka ekle
        plaka_data = {
            "plaka_no": "34TEST123",
            "isim_soyisim": "AHMET YILMAZ",
            "telefon": "05551234567",
            "durum": "Tanımlı",
            "site_id": self.test_data['site_id'],
            "blok_id": self.test_data['blok_id'],
            "daire_id": self.test_data['daire_ids'][0],
            "arac_tipi": "Sedan"
        }
        
        success, response = await self.make_request("POST", "/plates", plaka_data)
        if success:
            self.test_data['plaka_id'] = response['id']
            self.log_result("Plaka Oluşturma", True, f"34TEST123 plakası oluşturuldu - ID: {response['id']}")
        else:
            self.log_result("Plaka Oluşturma", False, f"Plaka oluşturulamadı: {response}")
            return

        # GET /api/site/{site_id}: Oluşturulan site detayını çek
        success, site_detail = await self.make_request("GET", f"/sites/{self.test_data['site_id']}")
        if success:
            blok = next((b for b in site_detail['bloklar'] if b['id'] == self.test_data['blok_id']), None)
            if blok:
                daire_1 = next((d for d in blok['daireler'] if d['id'] == self.test_data['daire_ids'][0]), None)
                daire_2 = next((d for d in blok['daireler'] if d['id'] == self.test_data['daire_ids'][1]), None)
                
                # 1. dairenin isim_soyisim ve telefon bilgilerinin "AHMET YILMAZ" ve "05551234567" olduğunu doğrula
                if daire_1 and daire_1.get('isim_soyisim') == 'AHMET YILMAZ' and daire_1.get('telefon') == '05551234567':
                    self.log_result("1. Daire Senkronizasyon", True, "1. dairenin bilgileri doğru güncellendi")
                else:
                    self.log_result("1. Daire Senkronizasyon", False, f"1. daire bilgileri: isim={daire_1.get('isim_soyisim') if daire_1 else 'N/A'}, telefon={daire_1.get('telefon') if daire_1 else 'N/A'}")
                
                # 2. dairenin bilgilerinin hala "Boş" ve "-" olduğunu doğrula
                if daire_2 and daire_2.get('isim_soyisim') == 'Boş' and daire_2.get('telefon') == '-':
                    self.log_result("2. Daire Boş Kontrolü", True, "2. daire bilgileri boş olarak kaldı")
                else:
                    self.log_result("2. Daire Boş Kontrolü", False, f"2. daire bilgileri: isim={daire_2.get('isim_soyisim') if daire_2 else 'N/A'}, telefon={daire_2.get('telefon') if daire_2 else 'N/A'}")
            else:
                self.log_result("Site Detay Kontrolü", False, "Blok bulunamadı")
        else:
            self.log_result("Site Detay Kontrolü", False, f"Site detayı alınamadı: {site_detail}")

    async def test_4_plaka_tasima_temizleme(self):
        """4. Plaka Taşıma ve Eski Daire Temizleme"""
        print("\n=== 4. Plaka Taşıma ve Eski Daire Temizleme ===")
        
        if not self.test_data['plaka_id'] or len(self.test_data['daire_ids']) < 2:
            self.log_result("Plaka Taşıma", False, "Plaka ID veya daire ID'leri eksik")
            return

        # PUT /api/plates/{plate_id}: 34TEST123 plakasını 2. daireye taşı
        plaka_update_data = {
            "isim_soyisim": "AHMET YILMAZ",
            "telefon": "05551234567",
            "daire_id": self.test_data['daire_ids'][1],
            "site_id": self.test_data['site_id'],
            "blok_id": self.test_data['blok_id']
        }
        
        success, response = await self.make_request("PUT", f"/plates/{self.test_data['plaka_id']}", plaka_update_data)
        if success:
            self.log_result("Plaka Taşıma", True, "34TEST123 plakası 2. daireye taşındı")
        else:
            self.log_result("Plaka Taşıma", False, f"Plaka taşınamadı: {response}")
            return

        # GET /api/site/{site_id}: Site detayını tekrar çek
        success, site_detail = await self.make_request("GET", f"/sites/{self.test_data['site_id']}")
        if success:
            blok = next((b for b in site_detail['bloklar'] if b['id'] == self.test_data['blok_id']), None)
            if blok:
                daire_1 = next((d for d in blok['daireler'] if d['id'] == self.test_data['daire_ids'][0]), None)
                daire_2 = next((d for d in blok['daireler'] if d['id'] == self.test_data['daire_ids'][1]), None)
                
                # 1. dairenin bilgilerinin temizlenip "Boş" ve "-" olduğunu doğrula
                if daire_1 and daire_1.get('isim_soyisim') == 'Boş' and daire_1.get('telefon') == '-':
                    self.log_result("1. Daire Temizleme", True, "1. dairenin bilgileri temizlendi")
                else:
                    self.log_result("1. Daire Temizleme", False, f"1. daire bilgileri temizlenmedi: isim={daire_1.get('isim_soyisim') if daire_1 else 'N/A'}, telefon={daire_1.get('telefon') if daire_1 else 'N/A'}")
                
                # 2. dairenin bilgilerinin "AHMET YILMAZ" ve "05551234567" olduğunu doğrula
                if daire_2 and daire_2.get('isim_soyisim') == 'AHMET YILMAZ' and daire_2.get('telefon') == '05551234567':
                    self.log_result("2. Daire Güncelleme", True, "2. dairenin bilgileri güncellendi")
                else:
                    self.log_result("2. Daire Güncelleme", False, f"2. daire bilgileri: isim={daire_2.get('isim_soyisim') if daire_2 else 'N/A'}, telefon={daire_2.get('telefon') if daire_2 else 'N/A'}")
            else:
                self.log_result("Site Detay Kontrolü", False, "Blok bulunamadı")
        else:
            self.log_result("Site Detay Kontrolü", False, f"Site detayı alınamadı: {site_detail}")

    async def test_5_temizlik_cleanup(self):
        """5. Temizlik (Cleanup)"""
        print("\n=== 5. Temizlik (Cleanup) ===")
        
        # DELETE /api/plates/{plate_id}: Oluşturulan plakayı sil
        if self.test_data['plaka_id']:
            success, response = await self.make_request("DELETE", f"/plates/{self.test_data['plaka_id']}")
            if success:
                self.log_result("Plaka Silme", True, "Test plakası başarıyla silindi")
            else:
                self.log_result("Plaka Silme", False, f"Plaka silinemedi: {response}")

        # DELETE /api/site/{site_id}: Oluşturulan siteyi sil
        if self.test_data['site_id']:
            success, response = await self.make_request("DELETE", f"/sites/{self.test_data['site_id']}")
            if success:
                self.log_result("Site Silme", True, "Test sitesi başarıyla silindi")
            else:
                self.log_result("Site Silme", False, f"Site silinemedi: {response}")

    async def run_paddleocr_removal_tests(self):
        """PaddleOCR kaldırma sonrası tüm testleri çalıştır"""
        print("🚀 PaddleOCR Kaldırma Sonrası Backend Testleri Başlatılıyor...")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 70)
        
        await self.test_1_sistem_ayarlari_kontrolu()
        await self.test_2_site_blok_daire_crud()
        await self.test_3_plaka_olusturma_senkronizasyon()
        await self.test_4_plaka_tasima_temizleme()
        await self.test_5_temizlik_cleanup()
        
        print("\n" + "=" * 70)
        print("📊 PADDLEOCR KALDIRMA TEST SONUÇLARI")
        print("=" * 70)
        print(f"✅ Başarılı: {self.results['passed']}")
        print(f"❌ Başarısız: {self.results['failed']}")
        
        total_tests = self.results['passed'] + self.results['failed']
        if total_tests > 0:
            success_rate = (self.results['passed'] / total_tests * 100)
            print(f"📈 Başarı Oranı: {success_rate:.1f}%")
        
        if self.results['errors']:
            print("\n🔍 BAŞARISIZ TESTLER:")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        print("\n🎯 BAŞARI KRİTERLERİ:")
        print("  • Tüm API endpoint'leri 2xx status code dönmeli ✅" if self.results['failed'] == 0 else "  • API endpoint'lerinde hatalar var ❌")
        print("  • OCR motor 'easyocr' olarak ayarlı olmalı")
        print("  • Plaka oluşturulduğunda daire bilgileri otomatik güncellenmeli")
        print("  • Plaka taşındığında eski daire temizlenmeli ve yeni daire güncellenmeli")
        
        return self.results['failed'] == 0

async def main():
    """Ana test çalıştırıcı"""
    async with PaddleOCRRemovalTester() as tester:
        success = await tester.run_paddleocr_removal_tests()
        return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))