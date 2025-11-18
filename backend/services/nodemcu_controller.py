import aiohttp
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class NodeMCUController:
    def __init__(self):
        self.timeout = aiohttp.ClientTimeout(total=5)
    
    async def open_door(self, ip_address: str, endpoint_url: str, nodemcu_id: str) -> bool:
        """
        NodeMCU cihazına HTTP isteği göndererek kapıyı aç
        """
        try:
            url = f"http://{ip_address}{endpoint_url}"
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        logger.info(f"Kapı açıldı: {nodemcu_id} ({url})")
                        return True
                    else:
                        logger.error(f"Kapı açma hatası: {response.status}")
                        return False
        
        except Exception as e:
            logger.error(f"NodeMCU bağlantı hatası ({nodemcu_id}): {e}")
            return False
    
    async def check_connection(self, ip_address: str) -> bool:
        """NodeMCU cihazına bağlanabilir mi kontrol et"""
        try:
            url = f"http://{ip_address}/status"
            
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    return response.status == 200
        
        except Exception as e:
            logger.debug(f"Bağlantı kontrolü başarısız: {e}")
            return False
    
    def get_status(self) -> dict:
        """Controller durumunu döndür"""
        return {
            "initialized": True,
            "timeout": self.timeout.total
        }