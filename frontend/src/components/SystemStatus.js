import React from 'react';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from '@/components/ui/hover-card';

const SystemStatus = ({ status }) => {
  if (!status) {
    return (
      <Badge variant="outline" className="border-slate-600 text-slate-400">
        Yükleniyor...
      </Badge>
    );
  }

  const getStatusIcon = (initialized) => {
    if (initialized) return <CheckCircle className="w-4 h-4 text-emerald-500" />;
    return <XCircle className="w-4 h-4 text-red-500" />;
  };

  const systemHealth = status.system?.status === 'healthy';

  return (
    <HoverCard>
      <HoverCardTrigger>
        <div className="flex items-center gap-2 cursor-pointer" data-testid="system-status-trigger">
          {systemHealth ? (
            <CheckCircle className="w-5 h-5 text-emerald-500" />
          ) : (
            <AlertCircle className="w-5 h-5 text-amber-500" />
          )}
          <span className="text-sm text-slate-300">
            {systemHealth ? 'Sistem Normal' : 'Sistem Uyarısı'}
          </span>
        </div>
      </HoverCardTrigger>
      <HoverCardContent className="w-80 bg-slate-800 border-slate-700" data-testid="system-status-details">
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-white mb-3">Sistem Durumu</h4>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">OpenCV</span>
              {getStatusIcon(true)}
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">YOLOv8</span>
              {getStatusIcon(status.yolo?.initialized)}
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">
                OCR ({status.ocr?.engine === 'paddleocr' ? 'PaddleOCR' : 'EasyOCR'})
              </span>
              {getStatusIcon(status.ocr?.initialized)}
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">Araç Sınıflandırma</span>
              {getStatusIcon(status.vehicle_classifier?.initialized)}
            </div>
          </div>

          <div className="pt-3 border-t border-slate-700 space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">CPU Kullanımı</span>
              <span className="text-white font-medium">{status.system?.cpu_usage?.toFixed(1)}%</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">RAM Kullanımı</span>
              <span className="text-white font-medium">{status.system?.memory_usage?.toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </HoverCardContent>
    </HoverCard>
  );
};

export default SystemStatus;