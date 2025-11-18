import psutil
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        pass
    
    def get_system_status(self) -> Dict:
        """Sistem durumunu al"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "status": "healthy" if cpu_percent < 80 and memory.percent < 85 else "warning"
            }
        except Exception as e:
            logger.error(f"Sistem durumu alınamadı: {e}")
            return {
                "cpu_usage": 0,
                "memory_usage": 0,
                "status": "error",
                "error": str(e)
            }