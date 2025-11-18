import React from 'react';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Car, Clock, User } from 'lucide-react';
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';

const LogPanel = ({ logs }) => {
  const getStatusBadge = (durum) => {
    const colors = {
      'Tanımlı': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      'Misafir': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      'Tanımsız': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      'Yasaklı': 'bg-red-500/20 text-red-400 border-red-500/30',
    };

    return (
      <Badge className={colors[durum] || colors['Tanımsız']}>
        {durum}
      </Badge>
    );
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return format(date, 'HH:mm:ss', { locale: tr });
    } catch {
      return '-';
    }
  };

  return (
    <Card 
      className="bg-slate-800/50 border-slate-700 backdrop-blur-sm h-full"
      data-testid="log-panel"
    >
      <div className="p-4 border-b border-slate-700">
        <h3 className="text-lg font-semibold text-white">Son Geçişler</h3>
        <p className="text-sm text-slate-400">Son 20 kayıt</p>
      </div>

      <ScrollArea className="h-[600px]">
        <div className="p-4 space-y-3">
          {logs.length === 0 ? (
            <div className="text-center py-8 text-slate-400" data-testid="no-logs-message">
              <p>Henüz geçiş kaydı yok</p>
            </div>
          ) : (
            logs.map((log, idx) => (
              <Card
                key={log.id || idx}
                className="bg-slate-900/50 border-slate-700 p-3 hover:bg-slate-900/70 transition-all"
                data-testid={`log-item-${idx}`}
              >
                <div className="flex gap-3">
                  {/* Fotoğraf */}
                  <div className="w-16 h-16 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0 overflow-hidden">
                    {log.fotograf_url ? (
                      <img 
                        src={log.fotograf_url} 
                        alt="Araç" 
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <Car className="w-6 h-6 text-slate-600" />
                    )}
                  </div>

                  {/* Bilgiler */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <p className="font-bold text-white text-sm truncate" data-testid="log-plate-number">
                        {log.plaka_no}
                      </p>
                      {getStatusBadge(log.durum)}
                    </div>

                    {log.isim_soyisim && (
                      <div className="flex items-center gap-1 text-xs text-slate-400 mb-1">
                        <User className="w-3 h-3" />
                        <span className="truncate">{log.isim_soyisim}</span>
                      </div>
                    )}

                    <div className="flex items-center gap-1 text-xs text-slate-500">
                      <Clock className="w-3 h-3" />
                      <span>{formatDate(log.tarih)}</span>
                    </div>

                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className="text-xs border-slate-600 text-slate-400">
                        {log.arac_tipi || 'Bilinmiyor'}
                      </Badge>
                      <Badge variant="outline" className="text-xs border-slate-600 text-slate-400">
                        {log.kamera_adi}
                      </Badge>
                    </div>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      </ScrollArea>
    </Card>
  );
};

export default LogPanel;