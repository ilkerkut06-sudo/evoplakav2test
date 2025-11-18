#!/usr/bin/env python3
"""
Site yapısını kontrol et ve mevcut daireleri listele
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://plateguard-1.preview.emergentagent.com/api"

async def check_site_structure():
    async with aiohttp.ClientSession() as session:
        # Tüm siteleri al
        async with session.get(f"{BACKEND_URL}/sites") as response:
            sites = await response.json()
            
        print("=== SİTE YAPISI ===")
        for site in sites:
            print(f"\n🏢 Site: {site['site_adi']} (ID: {site['id']})")
            
            for blok in site.get('bloklar', []):
                print(f"  📦 Blok: {blok['blok_adi']} (ID: {blok['id']})")
                print(f"     Daire Sayısı: {len(blok.get('daireler', []))}")
                
                for daire in blok.get('daireler', []):
                    print(f"     🏠 Daire {daire.get('daire_no', 'N/A')}: {daire.get('isim_soyisim', 'Boş')} - {daire.get('telefon', '-')} (ID: {daire['id']})")
        
        # 06DBN786 plakasını bul
        async with session.get(f"{BACKEND_URL}/plates") as response:
            plates = await response.json()
            
        print("\n=== 06DBN786 PLAKA BİLGİSİ ===")
        for plate in plates:
            if plate.get('plaka_no') == '06DBN786':
                print(f"Plaka: {plate['plaka_no']}")
                print(f"Site ID: {plate['site_id']}")
                print(f"Blok ID: {plate['blok_id']}")
                print(f"Daire ID: {plate['daire_id']}")
                print(f"Durum: {plate['durum']}")
                break

if __name__ == "__main__":
    asyncio.run(check_site_structure())