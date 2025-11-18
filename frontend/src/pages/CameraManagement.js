import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Plus, Edit, Trash2, Camera, Wifi, WifiOff } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CameraManagement = () => {
  const [cameras, setCameras] = useState([]);
  const [nodemcus, setNodemcus] = useState([]);
  const [open, setOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentCamera, setCurrentCamera] = useState(null);
  const [formData, setFormData] = useState({
    kamera_adi: '',
    kamera_tipi: 'RTSP',
    giris_cikis: 'Giriş',
    main_stream_url: '',
    sub_stream_url: '',
    onvif_ip: '',
    onvif_port: 80,
    onvif_kullanici: '',
    onvif_sifre: '',
    bagli_kapi_id: '',
    aktif: true,
    plaka_tanima_aktif: true,
  });

  useEffect(() => {
    fetchCameras();
    fetchNodemcus();
  }, []);

  const fetchCameras = async () => {
    try {
      const response = await axios.get(`${API}/cameras`);
      setCameras(response.data);
    } catch (error) {
      toast.error('Kameralar yüklenemedi');
    }
  };

  const fetchNodemcus = async () => {
    try {
      const response = await axios.get(`${API}/nodemcu`);
      setNodemcus(response.data);
    } catch (error) {
      console.error('NodeMCU listesi yüklenemedi');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editMode) {
        await axios.put(`${API}/cameras/${currentCamera.id}`, formData);
        toast.success('Kamera güncellendi');
      } else {
        await axios.post(`${API}/cameras`, formData);
        toast.success('Kamera eklendi');
      }
      setOpen(false);
      resetForm();
      fetchCameras();
    } catch (error) {
      toast.error('Kamera işlemi başarısız');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Kamerayı silmek istediğinize emin misiniz?')) return;
    try {
      await axios.delete(`${API}/cameras/${id}`);
      toast.success('Kamera silindi');
      fetchCameras();
    } catch (error) {
      toast.error('Kamera silinemedi');
    }
  };

  const handleEdit = (camera) => {
    setCurrentCamera(camera);
    setFormData({ ...camera });
    setEditMode(true);
    setOpen(true);
  };

  const resetForm = () => {
    setFormData({
      kamera_adi: '',
      kamera_tipi: 'RTSP',
      giris_cikis: 'Giriş',
      main_stream_url: '',
      sub_stream_url: '',
      onvif_ip: '',
      onvif_port: 80,
      onvif_kullanici: '',
      onvif_sifre: '',
      bagli_kapi_id: '',
      aktif: true,
      plaka_tanima_aktif: true,
    });
    setEditMode(false);
    setCurrentCamera(null);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
            Kamera Yönetimi
          </h1>
          <p className="text-slate-400 mt-1">IP kameraları ve webcam'leri yönetin</p>
        </div>

        <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) resetForm(); }}>
          <DialogTrigger asChild>
            <Button className="bg-sky-600 hover:bg-sky-700" data-testid="add-camera-button">
              <Plus className="w-4 h-4 mr-2" />
              Yeni Kamera Ekle
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-slate-900 border-slate-700 max-w-3xl max-h-[90vh] overflow-y-auto" data-testid="add-camera-dialog">
            <DialogHeader>
              <DialogTitle className="text-white">{editMode ? 'Kamera Düzenle' : 'Yeni Kamera Ekle'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-slate-300">Kamera Adı *</Label>
                  <Input
                    required
                    value={formData.kamera_adi}
                    onChange={(e) => setFormData({ ...formData, kamera_adi: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                    data-testid="camera-name-input"
                  />
                </div>
                <div>
                  <Label className="text-slate-300">Kamera Tipi</Label>
                  <Select value={formData.kamera_tipi} onValueChange={(v) => setFormData({ ...formData, kamera_tipi: v })}>
                    <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      <SelectItem value="RTSP">RTSP IP Kamera</SelectItem>
                      <SelectItem value="WEBCAM">Webcam</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label className="text-slate-300">Giriş/Çıkış</Label>
                <Select value={formData.giris_cikis} onValueChange={(v) => setFormData({ ...formData, giris_cikis: v })}>
                  <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-700">
                    <SelectItem value="Giriş">Giriş</SelectItem>
                    <SelectItem value="Çıkış">Çıkış</SelectItem>
                    <SelectItem value="Ortak">Ortak</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {formData.kamera_tipi === 'RTSP' && (
                <>
                  <div>
                    <Label className="text-slate-300">Main Stream URL</Label>
                    <Input
                      placeholder="rtsp://192.168.1.100:554/stream1"
                      value={formData.main_stream_url}
                      onChange={(e) => setFormData({ ...formData, main_stream_url: e.target.value })}
                      className="bg-slate-800 border-slate-700 text-white"
                    />
                  </div>
                  <div>
                    <Label className="text-slate-300">Sub Stream URL (Plaka Tanıma)</Label>
                    <Input
                      placeholder="rtsp://192.168.1.100:554/stream2"
                      value={formData.sub_stream_url}
                      onChange={(e) => setFormData({ ...formData, sub_stream_url: e.target.value })}
                      className="bg-slate-800 border-slate-700 text-white"
                    />
                  </div>

                  <div className="border-t border-slate-700 pt-4">
                    <h4 className="text-white font-semibold mb-3">ONVIF Ayarları (PTZ için)</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-slate-300">IP Adresi</Label>
                        <Input
                          value={formData.onvif_ip}
                          onChange={(e) => setFormData({ ...formData, onvif_ip: e.target.value })}
                          className="bg-slate-800 border-slate-700 text-white"
                          placeholder="192.168.1.100"
                        />
                      </div>
                      <div>
                        <Label className="text-slate-300">Port</Label>
                        <Input
                          type="number"
                          value={formData.onvif_port}
                          onChange={(e) => setFormData({ ...formData, onvif_port: parseInt(e.target.value) })}
                          className="bg-slate-800 border-slate-700 text-white"
                        />
                      </div>
                      <div>
                        <Label className="text-slate-300">Kullanıcı Adı</Label>
                        <Input
                          value={formData.onvif_kullanici}
                          onChange={(e) => setFormData({ ...formData, onvif_kullanici: e.target.value })}
                          className="bg-slate-800 border-slate-700 text-white"
                        />
                      </div>
                      <div>
                        <Label className="text-slate-300">Şifre</Label>
                        <Input
                          type="password"
                          value={formData.onvif_sifre}
                          onChange={(e) => setFormData({ ...formData, onvif_sifre: e.target.value })}
                          className="bg-slate-800 border-slate-700 text-white"
                        />
                      </div>
                    </div>
                  </div>
                </>
              )}

              <div>
                <Label className="text-slate-300">Bağlı Kapı (Opsiyonel)</Label>
                <Select value={formData.bagli_kapi_id || 'none'} onValueChange={(v) => setFormData({ ...formData, bagli_kapi_id: v === 'none' ? '' : v })}>
                  <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                    <SelectValue placeholder="Kapı seçin" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-700">
                    <SelectItem value="none">Kapı yok</SelectItem>
                    {nodemcus.map(node => (
                      <SelectItem key={node.id} value={node.id}>{node.kapi_adi}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <Label className="text-slate-300">Kamera Aktif</Label>
                <Switch
                  checked={formData.aktif}
                  onCheckedChange={(checked) => setFormData({ ...formData, aktif: checked })}
                />
              </div>

              <div className="flex items-center justify-between">
                <Label className="text-slate-300">Plaka Tanıma Aktif</Label>
                <Switch
                  checked={formData.plaka_tanima_aktif}
                  onCheckedChange={(checked) => setFormData({ ...formData, plaka_tanima_aktif: checked })}
                />
              </div>

              <Button type="submit" className="w-full bg-sky-600 hover:bg-sky-700" data-testid="submit-camera-button">
                {editMode ? 'Güncelle' : 'Kamera Ekle'}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {cameras.map((camera) => (
          <Card key={camera.id} className="bg-slate-800/50 border-slate-700 p-6" data-testid={`camera-card-${camera.id}`}>
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-lg bg-sky-500/20 flex items-center justify-center">
                  <Camera className="w-6 h-6 text-sky-400" />
                </div>
                <div>
                  <h3 className="font-bold text-white" data-testid="camera-name">{camera.kamera_adi}</h3>
                  <p className="text-sm text-slate-400">{camera.kamera_tipi}</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={() => handleEdit(camera)} className="text-slate-400 hover:text-white">
                  <Edit className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(camera.id)}
                  className="text-red-400 hover:text-red-300"
                  data-testid="delete-camera-button"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                {camera.aktif ? (
                  <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
                    <Wifi className="w-3 h-3 mr-1" />
                    Aktif
                  </Badge>
                ) : (
                  <Badge className="bg-slate-500/20 text-slate-400 border-slate-500/30">
                    <WifiOff className="w-3 h-3 mr-1" />
                    Pasif
                  </Badge>
                )}
                <Badge variant="outline" className="border-slate-600 text-slate-400">
                  {camera.giris_cikis}
                </Badge>
              </div>
              {camera.plaka_tanima_aktif && (
                <p className="text-xs text-emerald-400">✓ Plaka tanıma aktif</p>
              )}
            </div>
          </Card>
        ))}
      </div>

      {cameras.length === 0 && (
        <div className="text-center py-12 text-slate-400" data-testid="no-cameras-message">
          <Camera className="w-16 h-16 mx-auto mb-4 opacity-20" />
          <p>Henüz kamera eklenmemiş</p>
        </div>
      )}
    </div>
  );
};

export default CameraManagement;