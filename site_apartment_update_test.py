#!/usr/bin/env python3
"""
Site Yönetimi - Daire Listesi Güncelleme Testi
Specific test for apartment list update functionality
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional

# Backend URL from the review request
BACKEND_URL = "https://siteplates.preview.emergentagent.com/api"

class SiteApartmentUpdateTester:
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

    async def get_apartment_info(self, site_id: str, apartment_id: str) -> Dict:
        """Get specific apartment information from site details"""
        success, site_data = await self.make_request("GET", f"/sites/{site_id}")
        if not success:
            return {}
        
        for blok in site_data.get('bloklar', []):
            for daire in blok.get('daireler', []):
                if daire['id'] == apartment_id:
                    return daire
        return {}

    async def print_apartment_status(self, site_id: str, step_name: str):
        """Print current status of all apartments"""
        print(f"\n--- {step_name} - Daire Durumları ---")
        success, site_data = await self.make_request("GET", f"/sites/{site_id}")
        if success:
            for blok in site_data.get('bloklar', []):
                print(f"Blok: {blok['blok_adi']}")
                for i, daire in enumerate(blok.get('daireler', []), 1):
                    isim = daire.get('isim_soyisim', 'Boş')
                    telefon = daire.get('telefon', '-')
                    plaka_sayisi = len(daire.get('plakalar', []))
                    print(f"  Daire {i}: İsim='{isim}', Telefon='{telefon}', Plaka Sayısı={plaka_sayisi}")

    async def test_site_apartment_update_scenario(self):
        """Test the complete site apartment update scenario"""
        print("🎯 Site Yönetimi - Daire Listesi Güncelleme Testi")
        print("=" * 60)
        
        # Step 1: Check existing sites/blocks/apartments or create test data
        print("\n1️⃣ Mevcut site/blok/daireler kontrol ediliyor...")
        
        success, sites = await self.make_request("GET", "/sites")
        if success and len(sites) > 0:
            # Use existing site
            site = sites[0]
            self.test_data['site_id'] = site['id']
            print(f"   Mevcut site kullanılıyor: {site['site_adi']} (ID: {site['id']})")
            
            # Get site details to find blocks and apartments
            success, site_details = await self.make_request("GET", f"/sites/{site['id']}")
            if success and site_details.get('bloklar'):
                blok = site_details['bloklar'][0]
                self.test_data['blok_id'] = blok['id']
                
                if len(blok.get('daireler', [])) >= 3:
                    self.test_data['daire_ids'] = [d['id'] for d in blok['daireler'][:3]]
                    print(f"   Mevcut blok kullanılıyor: {blok['blok_adi']} - {len(blok['daireler'])} daire")
                else:
                    print("   Yeterli daire yok, yeni blok oluşturuluyor...")
                    await self.create_test_block()
            else:
                print("   Blok bulunamadı, yeni blok oluşturuluyor...")
                await self.create_test_block()
        else:
            print("   Site bulunamadı, yeni site oluşturuluyor...")
            await self.create_test_site()
        
        if not self.test_data['site_id'] or not self.test_data['daire_ids'] or len(self.test_data['daire_ids']) < 3:
            self.log_result("Test Verisi Hazırlama", False, "Yeterli test verisi oluşturulamadı")
            return
        
        await self.print_apartment_status(self.test_data['site_id'], "Başlangıç Durumu")
        
        # Step 2: Add new plate (TEST123) to Apartment 1
        print("\n2️⃣ Yeni plaka (TEST123) Daire 1'e ekleniyor...")
        
        plaka_data = {
            "plaka_no": "TEST123",
            "site_id": self.test_data['site_id'],
            "blok_id": self.test_data['blok_id'],
            "daire_id": self.test_data['daire_ids'][0],
            "arac_tipi": "Sedan",
            "durum": "Tanımlı",
            "isim_soyisim": "Ahmet Yılmaz",
            "telefon": "05551234567",
            "not_": "Test plakası"
        }
        
        success, response = await self.make_request("POST", "/plates", plaka_data)
        if success:
            self.test_data['plaka_id'] = response['id']
            self.log_result("Plaka Ekleme", True, f"TEST123 plakası Daire 1'e eklendi (ID: {response['id']})")
        else:
            self.log_result("Plaka Ekleme", False, f"Plaka eklenemedi: {response}")
            return
        
        await self.print_apartment_status(self.test_data['site_id'], "Plaka Ekleme Sonrası")
        
        # Step 3: Check Apartment 1's information - should be filled
        print("\n3️⃣ Daire 1'in bilgileri kontrol ediliyor...")
        
        daire1_info = await self.get_apartment_info(self.test_data['site_id'], self.test_data['daire_ids'][0])
        if daire1_info:
            isim = daire1_info.get('isim_soyisim', '')
            telefon = daire1_info.get('telefon', '')
            if isim and isim != 'Boş' and telefon and telefon != '-':
                self.log_result("Daire 1 Bilgi Doldurma", True, f"İsim: '{isim}', Telefon: '{telefon}'")
            else:
                self.log_result("Daire 1 Bilgi Doldurma", False, f"Bilgiler dolmadı - İsim: '{isim}', Telefon: '{telefon}'")
        else:
            self.log_result("Daire 1 Bilgi Doldurma", False, "Daire 1 bilgileri alınamadı")
        
        # Step 4: Check Apartments 2 and 3 - should still be "Boş"
        print("\n4️⃣ Daire 2 ve 3'ün durumu kontrol ediliyor...")
        
        for i, daire_id in enumerate(self.test_data['daire_ids'][1:3], 2):
            daire_info = await self.get_apartment_info(self.test_data['site_id'], daire_id)
            if daire_info:
                isim = daire_info.get('isim_soyisim', 'Boş')
                telefon = daire_info.get('telefon', '-')
                if isim == 'Boş' and telefon == '-':
                    self.log_result(f"Daire {i} Boş Durumu", True, f"Daire {i} boş durumda")
                else:
                    self.log_result(f"Daire {i} Boş Durumu", False, f"Daire {i} boş değil - İsim: '{isim}', Telefon: '{telefon}'")
            else:
                self.log_result(f"Daire {i} Boş Durumu", False, f"Daire {i} bilgileri alınamadı")
        
        # Step 5: Edit plate and move to Apartment 2
        print("\n5️⃣ Plaka düzenleniyor ve Daire 2'ye taşınıyor...")
        
        plaka_update_data = {
            "site_id": self.test_data['site_id'],
            "blok_id": self.test_data['blok_id'],
            "daire_id": self.test_data['daire_ids'][1],  # Move to Apartment 2
            "isim_soyisim": "Mehmet Demir",
            "telefon": "05559876543",
            "not_": "Plaka Daire 2'ye taşındı"
        }
        
        success, response = await self.make_request("PUT", f"/plates/{self.test_data['plaka_id']}", plaka_update_data)
        if success:
            self.log_result("Plaka Taşıma", True, "TEST123 plakası Daire 2'ye taşındı")
        else:
            self.log_result("Plaka Taşıma", False, f"Plaka taşınamadı: {response}")
            return
        
        await self.print_apartment_status(self.test_data['site_id'], "Plaka Taşıma Sonrası")
        
        # Step 6: Final verification
        print("\n6️⃣ Final kontrol - Site yönetiminden daire durumları...")
        
        # Check Apartment 1: Should be "Boş" and "-"
        daire1_info = await self.get_apartment_info(self.test_data['site_id'], self.test_data['daire_ids'][0])
        if daire1_info:
            isim1 = daire1_info.get('isim_soyisim', 'Boş')
            telefon1 = daire1_info.get('telefon', '-')
            plaka_count1 = len(daire1_info.get('plakalar', []))
            
            if isim1 == 'Boş' and telefon1 == '-' and plaka_count1 == 0:
                self.log_result("Daire 1 Temizleme", True, "Daire 1 başarıyla temizlendi")
            else:
                self.log_result("Daire 1 Temizleme", False, f"Daire 1 temizlenmedi - İsim: '{isim1}', Telefon: '{telefon1}', Plaka: {plaka_count1}")
        
        # Check Apartment 2: Should have name and phone
        daire2_info = await self.get_apartment_info(self.test_data['site_id'], self.test_data['daire_ids'][1])
        if daire2_info:
            isim2 = daire2_info.get('isim_soyisim', '')
            telefon2 = daire2_info.get('telefon', '')
            plaka_count2 = len(daire2_info.get('plakalar', []))
            
            if isim2 and isim2 != 'Boş' and telefon2 and telefon2 != '-' and plaka_count2 > 0:
                self.log_result("Daire 2 Bilgi Güncelleme", True, f"Daire 2 bilgileri güncellendi - İsim: '{isim2}', Telefon: '{telefon2}'")
            else:
                self.log_result("Daire 2 Bilgi Güncelleme", False, f"Daire 2 bilgileri eksik - İsim: '{isim2}', Telefon: '{telefon2}', Plaka: {plaka_count2}")
        
        # Check Apartment 3: Should still be "Boş"
        daire3_info = await self.get_apartment_info(self.test_data['site_id'], self.test_data['daire_ids'][2])
        if daire3_info:
            isim3 = daire3_info.get('isim_soyisim', 'Boş')
            telefon3 = daire3_info.get('telefon', '-')
            plaka_count3 = len(daire3_info.get('plakalar', []))
            
            if isim3 == 'Boş' and telefon3 == '-' and plaka_count3 == 0:
                self.log_result("Daire 3 Boş Durumu Korunması", True, "Daire 3 boş durumunu korudu")
            else:
                self.log_result("Daire 3 Boş Durumu Korunması", False, f"Daire 3 durumu değişti - İsim: '{isim3}', Telefon: '{telefon3}', Plaka: {plaka_count3}")

    async def create_test_site(self):
        """Create test site with block and apartments"""
        site_data = {
            "site_adi": "Test Sitesi - Daire Güncelleme",
            "adres": "İstanbul Test Mahallesi",
            "yonetici_adi": "Test Yönetici",
            "yonetici_telefon": "05551111111"
        }
        
        success, response = await self.make_request("POST", "/sites", site_data)
        if success:
            self.test_data['site_id'] = response['id']
            await self.create_test_block()

    async def create_test_block(self):
        """Create test block with 3 apartments"""
        if not self.test_data['site_id']:
            return
            
        blok_data = {
            "blok_adi": "Test Blok",
            "daire_sayisi": 3,
            "aciklama": "Test için oluşturulan blok"
        }
        
        success, response = await self.make_request("POST", f"/sites/{self.test_data['site_id']}/bloklar", blok_data)
        if success:
            self.test_data['blok_id'] = response['id']
            
            # Get apartment IDs
            success, site_data = await self.make_request("GET", f"/sites/{self.test_data['site_id']}")
            if success:
                for blok in site_data['bloklar']:
                    if blok['id'] == self.test_data['blok_id']:
                        self.test_data['daire_ids'] = [d['id'] for d in blok['daireler']]
                        break

    async def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Test verilerini temizleme...")
        
        # Delete plate
        if self.test_data['plaka_id']:
            success, _ = await self.make_request("DELETE", f"/plates/{self.test_data['plaka_id']}")
            if success:
                print("   ✅ Test plakası silindi")
            else:
                print("   ❌ Test plakası silinemedi")

    async def run_test(self):
        """Run the apartment update test"""
        try:
            await self.test_site_apartment_update_scenario()
            await self.cleanup_test_data()
            
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
            
        except Exception as e:
            print(f"❌ Test sırasında hata: {str(e)}")
            return False

async def main():
    """Main test runner"""
    async with SiteApartmentUpdateTester() as tester:
        success = await tester.run_test()
        return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))