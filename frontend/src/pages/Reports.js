import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { FileText, Download, Calendar, Car, BarChart3 } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const Reports = () => {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [vehicleStats, setVehicleStats] = useState([]);
  const [doorStats, setDoorStats] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    baslangic_tarihi: '',
    bitis_tarihi: '',
    durum: '',
    kamera_id: '',
  });

  useEffect(() => {
    fetchStats();
    fetchLogs();
    fetchVehicleStats();
    fetchDoorStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/logs/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('İstatistikler alınamadı');
    }
  };

  const fetchLogs = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.baslangic_tarihi) params.append('baslangic_tarihi', filters.baslangic_tarihi);
      if (filters.bitis_tarihi) params.append('bitis_tarihi', filters.bitis_tarihi);
      if (filters.durum) params.append('durum', filters.durum);
      if (filters.kamera_id) params.append('kamera_id', filters.kamera_id);
      params.append('limit', '100');

      const response = await axios.get(`${API}/logs?${params.toString()}`);
      setLogs(response.data);
    } catch (error) {
      toast.error('Loglar yüklenemedi');
    }
  };

  const fetchVehicleStats = async () => {
    try {
      const response = await axios.get(`${API}/reports/vehicle-type-stats`);
      setVehicleStats(response.data);
    } catch (error) {
      console.error('Araç istatistikleri alınamadı');
    }
  };

  const fetchDoorStats = async () => {
    try {
      const response = await axios.get(`${API}/logs/kapi-stats`);
      setDoorStats(response.data);
    } catch (error) {
      console.error('Kapı istatistikleri alınamadı');
    }
  };

  const handleFilterApply = () => {
    fetchLogs();
  };

  const handleDownloadPDF = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.baslangic_tarihi) params.append('baslangic_tarihi', filters.baslangic_tarihi);
      if (filters.bitis_tarihi) params.append('bitis_tarihi', filters.bitis_tarihi);
      if (filters.durum) params.append('durum', filters.durum);

      const response = await axios.get(`${API}/reports/generate-pdf?${params.toString()}`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `rapor_${Date.now()}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('PDF rapor indirildi');
    } catch (error) {
      toast.error('PDF oluşturulamadı');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (durum) => {
    const colors = {
      'Tanımlı': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      'Misafir': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      'Tanımsız': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      'Yasaklı': 'bg-red-500/20 text-red-400 border-red-500/30',
    };
    return <Badge className={colors[durum] || colors['Tanımsız']}>{durum}</Badge>;
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
            Raporlar ve İstatistikler
          </h1>
          <p className="text-slate-400 mt-1">Detaylı geçiş raporları ve analizler</p>
        </div>

        <Button
          onClick={handleDownloadPDF}
          disabled={loading}
          className="bg-emerald-600 hover:bg-emerald-700"
          data-testid="download-pdf-button"
        >
          <Download className="w-4 h-4 mr-2" />
          {loading ? 'Hazırlanıyor...' : 'PDF İndir'}
        </Button>
      </div>

      {/* İstatistik Kartları */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-slate-800/50 border-slate-700 p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-lg bg-sky-500/20 flex items-center justify-center">
                <Car className="w-6 h-6 text-sky-400" />
              </div>
              <div>
                <p className="text-sm text-slate-400">Toplam Araç</p>
                <p className="text-2xl font-bold text-white">{stats.toplam_arac}</p>
              </div>
            </div>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700 p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                <Calendar className="w-6 h-6 text-emerald-400" />
              </div>
              <div>
                <p className="text-sm text-slate-400">Bu Ay Giriş</p>
                <p className="text-2xl font-bold text-white">{stats.bu_ay_giris}</p>
              </div>
            </div>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700 p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-lg bg-amber-500/20 flex items-center justify-center">
                <FileText className="w-6 h-6 text-amber-400" />
              </div>
              <div>
                <p className="text-sm text-slate-400">Bugün Misafir</p>
                <p className="text-2xl font-bold text-white">{stats.bugun_misafir}</p>
              </div>
            </div>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700 p-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-lg bg-red-500/20 flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-red-400" />
              </div>
              <div>
                <p className="text-sm text-slate-400">Yasaklı Deneme</p>
                <p className="text-2xl font-bold text-white">{stats.yasakli_denemesi}</p>
              </div>
            </div>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Filtreler */}
        <Card className="bg-slate-800/50 border-slate-700 p-6 lg:col-span-1">
          <h3 className="text-lg font-semibold text-white mb-4">Filtreler</h3>
          <div className="space-y-4">
            <div>
              <Label className="text-slate-300">Başlangıç Tarihi</Label>
              <Input
                type="date"
                value={filters.baslangic_tarihi}
                onChange={(e) => setFilters({ ...filters, baslangic_tarihi: e.target.value })}
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-300">Bitiş Tarihi</Label>
              <Input
                type="date"
                value={filters.bitis_tarihi}
                onChange={(e) => setFilters({ ...filters, bitis_tarihi: e.target.value })}
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-300">Durum</Label>
              <Select value={filters.durum} onValueChange={(v) => setFilters({ ...filters, durum: v })}>
                <SelectTrigger className="bg-slate-900 border-slate-700 text-white">
                  <SelectValue placeholder="Tümü" />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-700">
                  <SelectItem value="">Tümü</SelectItem>
                  <SelectItem value="Tanımlı">Tanımlı</SelectItem>
                  <SelectItem value="Misafir">Misafir</SelectItem>
                  <SelectItem value="Tanımsız">Tanımsız</SelectItem>
                  <SelectItem value="Yasaklı">Yasaklı</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button onClick={handleFilterApply} className="w-full bg-sky-600 hover:bg-sky-700">
              Filtrele
            </Button>
          </div>

          {/* Araç Tipi İstatistikleri */}
          {vehicleStats.length > 0 && (
            <div className="mt-6 pt-6 border-t border-slate-700">
              <h4 className="text-sm font-semibold text-white mb-3">Araç Tipleri</h4>
              <div className="space-y-2">
                {vehicleStats.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">{item.arac_tipi}</span>
                    <span className="text-white font-semibold">{item.adet}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Kapı İstatistikleri */}
          {doorStats.length > 0 && (
            <div className="mt-6 pt-6 border-t border-slate-700">
              <h4 className="text-sm font-semibold text-white mb-3">Kapı Geçişleri</h4>
              <div className="space-y-2">
                {doorStats.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">{item.kapi_adi}</span>
                    <span className="text-white font-semibold">{item.toplam_gecis}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </Card>

        {/* Log Listesi */}
        <Card className="bg-slate-800/50 border-slate-700 p-6 lg:col-span-2">
          <h3 className="text-lg font-semibold text-white mb-4">Geçiş Kayıtları ({logs.length})</h3>
          <ScrollArea className="h-[600px]">
            <div className="space-y-3">
              {logs.map((log, idx) => (
                <Card key={log.id || idx} className="bg-slate-900/50 border-slate-700 p-4">
                  <div className="flex items-start gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-bold text-white">{log.plaka_no}</span>
                        {getStatusBadge(log.durum)}
                      </div>
                      <div className="text-sm space-y-1">
                        {log.isim_soyisim && (
                          <p className="text-slate-400">{log.isim_soyisim}</p>
                        )}
                        <p className="text-slate-500">
                          {format(new Date(log.tarih), 'dd MMM yyyy HH:mm', { locale: tr })} - {log.kamera_adi}
                        </p>
                        <p className="text-slate-500">Araç: {log.arac_tipi || 'Bilinmiyor'}</p>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </ScrollArea>
        </Card>
      </div>
    </div>
  );
};

export default Reports;