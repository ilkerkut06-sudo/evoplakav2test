#!/usr/bin/env python3
"""
Daire 3'te başka plaka var mı kontrol et
"""

import asyncio
import aiohttp

BACKEND_URL = "https://plateguard-1.preview.emergentagent.com/api"
DAIRE_3_ID = "62878c31-42b0-44d8-a529-e000318ca6c2"

async def check_daire_plates():
    async with aiohttp.ClientSession() as session:
        # Daire 3'teki tüm plakaları al
        async with session.get(f"{BACKEND_URL}/plates?daire_id={DAIRE_3_ID}") as response:
            plates = await response.json()
            
        print(f"=== DAİRE 3'TEKİ PLAKALAR ===")
        print(f"Daire ID: {DAIRE_3_ID}")
        print(f"Plaka Sayısı: {len(plates)}")
        
        for plate in plates:
            print(f"  - {plate['plaka_no']} (ID: {plate['id']}) - Durum: {plate['durum']}")

if __name__ == "__main__":
    asyncio.run(check_daire_plates())