#!/usr/bin/env python3
"""
Eklenen test loglarını kontrol et
"""

import asyncio
import aiohttp

BACKEND_URL = "https://plateguard-1.preview.emergentagent.com/api"

async def check_logs():
    async with aiohttp.ClientSession() as session:
        # Son 20 logu al
        async with session.get(f"{BACKEND_URL}/logs?limit=20") as response:
            logs = await response.json()
            
        print("=== SON EKLENEN TEST LOGLARI ===")
        
        test_plates = ["34ABC123", "06XYZ789", "35DEF456", "07GHI321", "16JKL654", "99ZZZ999"]
        
        found_logs = []
        for log in logs:
            if log['plaka_no'] in test_plates:
                found_logs.append(log)
        
        print(f"Bulunan test logları: {len(found_logs)}/6")
        
        # Durum bazında grupla
        durum_counts = {}
        for log in found_logs:
            durum = log['durum']
            durum_counts[durum] = durum_counts.get(durum, 0) + 1
        
        print("\nDurum Dağılımı:")
        for durum, count in durum_counts.items():
            print(f"  {durum}: {count} adet")
        
        print("\nDetaylar:")
        for log in found_logs:
            print(f"  - {log['plaka_no']} | {log['durum']} | {log['giris_cikis']} | {log['kamera_adi']}")

if __name__ == "__main__":
    asyncio.run(check_logs())