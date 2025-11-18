import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, CheckCircle, AlertTriangle, Ban, User } from 'lucide-react';
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';

const LiveTicker = ({ logs }) => {
  // Son 3 kaydı al ve yeni tarihten eskiye sırala
  const recentLogs = logs ? logs.slice(0, 3) : [];

  const getDurumBadge = (durum) => {
    switch (durum) {
      case 'Tanımlı':
        return (
          <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 flex items-center gap-1">
            <CheckCircle className="w-3 h-3" />
            KAYITLI ARAÇ
          </Badge>
        );
      case 'Misafir':
        return (
          <Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30 flex items-center gap-1">
            <User className="w-3 h-3" />
            MİSAFİR ARAÇ
          </Badge>
        );
      case 'Yasaklı':
        return (
          <Badge className="bg-red-500/20 text-red-400 border-red-500/30 flex items-center gap-1">
            <Ban className="w-3 h-3" />
            YASAKLI ARAÇ
          </Badge>
        );
      default:
        return (
          <Badge className="bg-slate-500/20 text-slate-400 border-slate-500/30 flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" />
            TANıMSız ARAÇ
          </Badge>
        );
    }
  };

  return (
    <Card 
      className="bg-slate-800/50 border-slate-700 backdrop-blur-sm"
      data-testid="live-ticker"
    >
      <div className="p-3 bg-slate-900/50 border-b border-slate-700 flex items-center gap-2">
        <Activity className="w-4 h-4 text-sky-500 animate-pulse" />
        <span className="text-sm font-semibold text-white">Canlı Akış (Son 3 Kayıt)</span>
      </div>
      
      <div className="divide-y divide-slate-700">
        {recentLogs.length === 0 ? (
          <div className="p-4 text-center text-slate-400 text-sm">
            Henüz geçiş kaydı yok...
          </div>
        ) : (
          recentLogs.map((log, index) => {
            const tarih = new Date(log.tarih);
            const saat = format(tarih, 'HH:mm:ss', { locale: tr });
            const gun = format(tarih, 'dd.MM.yyyy', { locale: tr });
            
            return (
              <div 
                key={log.id || index} 
                className="p-2 hover:bg-slate-900/30 transition-colors"
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <span className="font-bold text-white text-base tracking-wider">
                      {log.plaka_no}
                    </span>
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <span className="font-mono">{saat}</span>
                      <span className="font-mono">{gun}</span>
                    </div>
                  </div>
                  <div>
                    {getDurumBadge(log.durum)}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
};

export default LiveTicker;