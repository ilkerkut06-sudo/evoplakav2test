import React, { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Activity } from 'lucide-react';
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';

const LiveTicker = ({ logs }) => {
  const [tickerText, setTickerText] = useState('');

  useEffect(() => {
    if (logs && logs.length > 0) {
      const latest = logs.slice(0, 5);
      const text = latest
        .map((log) => {
          const time = format(new Date(log.tarih), 'HH:mm', { locale: tr });
          const status = getDurumText(log.durum);
          return `${time} - ${log.plaka_no} - ${status} - ${log.kamera_adi}`;
        })
        .join('  •  ');
      setTickerText(text);
    }
  }, [logs]);

  const getDurumText = (durum) => {
    const map = {
      'Tanımlı': 'Tanımlı Araç',
      'Misafir': 'Misafir Araç',
      'Tanımsız': 'Tanımsız Araç',
      'Yasaklı': '⚠️ Yasaklı Araç Denemesi',
    };
    return map[durum] || durum;
  };

  return (
    <Card 
      className="bg-slate-800/50 border-slate-700 backdrop-blur-sm overflow-hidden"
      data-testid="live-ticker"
    >
      <div className="p-3 bg-slate-900/50 border-b border-slate-700 flex items-center gap-2">
        <Activity className="w-4 h-4 text-sky-500" />
        <span className="text-sm font-semibold text-white">Canlı Akış</span>
      </div>
      <div className="relative overflow-hidden h-10 flex items-center bg-slate-900/30">
        <div className="ticker-wrapper">
          <div className="ticker-content text-slate-300 text-sm whitespace-nowrap">
            {tickerText || 'Henüz geçiş kaydı yok...'}
          </div>
        </div>
      </div>
    </Card>
  );
};

export default LiveTicker;