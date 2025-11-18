#!/usr/bin/env python3
"""
Comprehensive Backend Test - Site Apartment Update Logic
Tests the critical functionality gaps in apartment-plate synchronization
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional

# Backend URL from the review request
BACKEND_URL = "https://siteplates.preview.emergentagent.com/api"

class ComprehensiveBackendTester:
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
            'errors': [],
            'critical_issues': []
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def log_result(self, test_name: str, success: bool, message: str = "", critical: bool = False):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        
        if success:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
            if critical:
                self.results['critical_issues'].append(f"{test_name}: {message}")

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

    async def setup_clean_test_environment(self):
        """Create a clean test environment with fresh site and apartments"""
        print("🏗️ Setting up clean test environment...")
        
        # Create test site
        site_data = {
            "site_adi": "Backend Test Sitesi",
            "adres": "Test Mahallesi Backend Sokak No:1",
            "yonetici_adi": "Test Yönetici",
            "yonetici_telefon": "05551111111"
        }
        
        success, response = await self.make_request("POST", "/sites", site_data)
        if success:
            self.test_data['site_id'] = response['id']
            print(f"   ✅ Test sitesi oluşturuldu: {response['id']}")
        else:
            self.log_result("Test Site Oluşturma", False, f"Site oluşturulamadı: {response}", critical=True)
            return False

        # Create test block with 3 apartments
        blok_data = {
            "blok_adi": "Test Blok",
            "daire_sayisi": 3,
            "aciklama": "Backend test için oluşturulan blok"
        }
        
        success, response = await self.make_request("POST", f"/sites/{self.test_data['site_id']}/bloklar", blok_data)
        if success:
            self.test_data['blok_id'] = response['id']
            print(f"   ✅ Test bloku oluşturuldu: {response['id']}")
            
            # Get apartment IDs
            success, site_data = await self.make_request("GET", f"/sites/{self.test_data['site_id']}")
            if success:
                for blok in site_data['bloklar']:
                    if blok['id'] == self.test_data['blok_id']:
                        self.test_data['daire_ids'] = [d['id'] for d in blok['daireler']]
                        print(f"   ✅ {len(self.test_data['daire_ids'])} daire hazır")
                        break
        else:
            self.log_result("Test Blok Oluşturma", False, f"Blok oluşturulamadı: {response}", critical=True)
            return False

        return len(self.test_data['daire_ids']) >= 3

    async def test_apartment_plate_synchronization_gap(self):
        """Test the critical gap in apartment-plate synchronization"""
        print("\n🔍 CRITICAL FUNCTIONALITY GAP TESTING")
        print("=" * 60)
        
        # Test 1: Plate creation with apartment information
        print("\n1️⃣ Testing plate creation with apartment information...")
        
        plaka_data = {
            "plaka_no": "TEST001",
            "site_id": self.test_data['site_id'],
            "blok_id": self.test_data['blok_id'],
            "daire_id": self.test_data['daire_ids'][0],
            "arac_tipi": "Sedan",
            "durum": "Tanımlı",
            "isim_soyisim": "Test Kullanıcı",  # This field is NOT in PlakaCreate model
            "telefon": "05551234567",          # This field is NOT in PlakaCreate model
            "not_": "Test plakası"
        }
        
        success, response = await self.make_request("POST", "/plates", plaka_data)
        if success:
            self.test_data['plaka_id'] = response['id']
            print(f"   ✅ Plaka oluşturuldu: {response['id']}")
            
            # Check if apartment information was updated
            success, site_data = await self.make_request("GET", f"/sites/{self.test_data['site_id']}")
            if success:
                apartment = None
                for blok in site_data['bloklar']:
                    for daire in blok['daireler']:
                        if daire['id'] == self.test_data['daire_ids'][0]:
                            apartment = daire
                            break
                
                if apartment:
                    isim = apartment.get('isim_soyisim', 'Boş')
                    telefon = apartment.get('telefon', '-')
                    
                    if isim == 'Test Kullanıcı' and telefon == '05551234567':
                        self.log_result("Apartment Info Sync on Plate Creation", True, "Apartment information correctly updated")
                    else:
                        self.log_result("Apartment Info Sync on Plate Creation", False, 
                                      f"CRITICAL GAP: Apartment info not synced - Expected: 'Test Kullanıcı'/'05551234567', Got: '{isim}'/'{telefon}'", 
                                      critical=True)
                else:
                    self.log_result("Apartment Info Sync on Plate Creation", False, "Apartment not found", critical=True)
        else:
            self.log_result("Plate Creation with Apartment Info", False, f"Plaka oluşturulamadı: {response}", critical=True)
            return

        # Test 2: Check if apartment includes plate information
        print("\n2️⃣ Testing if apartment data includes plate information...")
        
        success, site_data = await self.make_request("GET", f"/sites/{self.test_data['site_id']}")
        if success:
            apartment = None
            for blok in site_data['bloklar']:
                for daire in blok['daireler']:
                    if daire['id'] == self.test_data['daire_ids'][0]:
                        apartment = daire
                        break
            
            if apartment:
                plakalar = apartment.get('plakalar', [])
                if len(plakalar) > 0:
                    self.log_result("Apartment Includes Plate Data", True, f"Apartment has {len(plakalar)} plates")
                else:
                    self.log_result("Apartment Includes Plate Data", False, 
                                  "CRITICAL GAP: Apartment data doesn't include associated plates", 
                                  critical=True)

        # Test 3: Plate moving and apartment cleanup
        print("\n3️⃣ Testing plate moving and apartment cleanup...")
        
        if len(self.test_data['daire_ids']) >= 2:
            plaka_update_data = {
                "site_id": self.test_data['site_id'],
                "blok_id": self.test_data['blok_id'],
                "daire_id": self.test_data['daire_ids'][1],  # Move to apartment 2
                "isim_soyisim": "Yeni Kullanıcı",
                "telefon": "05559876543",
                "not_": "Plaka taşındı"
            }
            
            success, response = await self.make_request("PUT", f"/plates/{self.test_data['plaka_id']}", plaka_update_data)
            if success:
                print(f"   ✅ Plaka taşındı")
                
                # Check if old apartment was cleaned
                success, site_data = await self.make_request("GET", f"/sites/{self.test_data['site_id']}")
                if success:
                    old_apartment = None
                    new_apartment = None
                    
                    for blok in site_data['bloklar']:
                        for daire in blok['daireler']:
                            if daire['id'] == self.test_data['daire_ids'][0]:
                                old_apartment = daire
                            elif daire['id'] == self.test_data['daire_ids'][1]:
                                new_apartment = daire
                    
                    # Check old apartment cleanup
                    if old_apartment:
                        old_isim = old_apartment.get('isim_soyisim', 'Boş')
                        old_telefon = old_apartment.get('telefon', '-')
                        
                        if old_isim == 'Boş' and old_telefon == '-':
                            self.log_result("Old Apartment Cleanup", True, "Old apartment correctly cleaned")
                        else:
                            self.log_result("Old Apartment Cleanup", False, 
                                          f"CRITICAL GAP: Old apartment not cleaned - Still has: '{old_isim}'/'{old_telefon}'", 
                                          critical=True)
                    
                    # Check new apartment update
                    if new_apartment:
                        new_isim = new_apartment.get('isim_soyisim', 'Boş')
                        new_telefon = new_apartment.get('telefon', '-')
                        
                        if new_isim == 'Yeni Kullanıcı' and new_telefon == '05559876543':
                            self.log_result("New Apartment Update", True, "New apartment correctly updated")
                        else:
                            self.log_result("New Apartment Update", False, 
                                          f"CRITICAL GAP: New apartment not updated - Expected: 'Yeni Kullanıcı'/'05559876543', Got: '{new_isim}'/'{new_telefon}'", 
                                          critical=True)
            else:
                self.log_result("Plate Moving", False, f"Plaka taşınamadı: {response}", critical=True)

    async def test_model_structure_gaps(self):
        """Test model structure gaps"""
        print("\n4️⃣ Testing model structure gaps...")
        
        # Check if PlakaCreate model accepts isim_soyisim and telefon
        plaka_data_with_apartment_info = {
            "plaka_no": "TEST002",
            "site_id": self.test_data['site_id'],
            "blok_id": self.test_data['blok_id'],
            "daire_id": self.test_data['daire_ids'][2],
            "arac_tipi": "SUV",
            "durum": "Tanımlı",
            "isim_soyisim": "Model Test",
            "telefon": "05551111111",
            "not_": "Model test plakası"
        }
        
        success, response = await self.make_request("POST", "/plates", plaka_data_with_apartment_info)
        if success:
            # Check if the extra fields were ignored or processed
            created_plate = response
            if 'isim_soyisim' in created_plate or 'telefon' in created_plate:
                self.log_result("PlakaCreate Model Accepts Apartment Info", True, "Model accepts apartment information")
            else:
                self.log_result("PlakaCreate Model Accepts Apartment Info", False, 
                              "MODEL GAP: PlakaCreate model doesn't include isim_soyisim and telefon fields", 
                              critical=True)
            
            # Clean up
            await self.make_request("DELETE", f"/plates/{created_plate['id']}")
        else:
            # Check if it failed due to unknown fields
            error_msg = response.get('detail', str(response))
            if 'isim_soyisim' in error_msg or 'telefon' in error_msg:
                self.log_result("PlakaCreate Model Accepts Apartment Info", False, 
                              f"MODEL GAP: PlakaCreate model rejects apartment info - {error_msg}", 
                              critical=True)
            else:
                self.log_result("PlakaCreate Model Test", False, f"Unexpected error: {error_msg}")

    async def cleanup_test_data(self):
        """Clean up test data"""
        print("\n🧹 Cleaning up test data...")
        
        # Delete plate
        if self.test_data['plaka_id']:
            success, _ = await self.make_request("DELETE", f"/plates/{self.test_data['plaka_id']}")
            if success:
                print("   ✅ Test plakası silindi")

        # Delete site (cascades to blocks and apartments)
        if self.test_data['site_id']:
            success, _ = await self.make_request("DELETE", f"/sites/{self.test_data['site_id']}")
            if success:
                print("   ✅ Test sitesi silindi")

    async def run_comprehensive_test(self):
        """Run comprehensive backend functionality test"""
        print("🎯 COMPREHENSIVE BACKEND FUNCTIONALITY TEST")
        print("Testing critical apartment-plate synchronization gaps")
        print("=" * 60)
        
        # Setup clean environment
        if not await self.setup_clean_test_environment():
            return False
        
        # Run tests
        await self.test_apartment_plate_synchronization_gap()
        await self.test_model_structure_gaps()
        
        # Cleanup
        await self.cleanup_test_data()
        
        # Results
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['passed'] + self.results['failed'] > 0:
            success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100)
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.results['critical_issues']:
            print(f"\n🚨 CRITICAL ISSUES FOUND ({len(self.results['critical_issues'])}):")
            for issue in self.results['critical_issues']:
                print(f"  • {issue}")
        
        if self.results['errors']:
            print(f"\n🔍 ALL ERRORS ({len(self.results['errors'])}):")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        return len(self.results['critical_issues']) == 0

async def main():
    """Main test runner"""
    async with ComprehensiveBackendTester() as tester:
        success = await tester.run_comprehensive_test()
        return 0 if success else 1

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))