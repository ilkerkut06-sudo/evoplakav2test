import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Plus, Edit, Trash2, DoorOpen, Wifi, WifiOff, Lock, Unlock } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const NodeMCUManagement = () => {
  const [devices, setDevices] = useState([]);
  const [open, setOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentDevice, setCurrentDevice] = useState(null);
  const [formData, setFormData] = useState({
    nodemcu_id: '',
    ip_adres: '',
    kapi_adi: '',
    aciklama: '',
    aktif: true,
  });

  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchDevices = async () => {
    try {
      const response = await axios.get(`${API}/nodemcu`);
      setDevices(response.data);
    } catch (error) {
      toast.error('Cihazlar yüklenemedi');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editMode) {
        await axios.put(`${API}/nodemcu/${currentDevice.id}`, formData);
        toast.success('Cihaz güncellendi');
      } else {
        await axios.post(`${API}/nodemcu`, formData);
        toast.success('Cihaz eklendi');
      }
      setOpen(false);
      resetForm();
      fetchDevices();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Cihaz işlemi başarısız');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Cihazı silmek istediğinize emin misiniz?')) return;
    try {
      await axios.delete(`${API}/nodemcu/${id}`);
      toast.success('Cihaz silindi');
      fetchDevices();
    } catch (error) {
      toast.error('Cihaz silinemedi');
    }
  };

  const handleEdit = (device) => {
    setCurrentDevice(device);
    setFormData({
      nodemcu_id: device.nodemcu_id,
      ip_adres: device.ip_adres,
      kapi_adi: device.kapi_adi,
      aciklama: device.aciklama || '',
      aktif: device.aktif,
    });
    setEditMode(true);
    setOpen(true);
  };

  const resetForm = () => {
    setFormData({
      nodemcu_id: '',
      ip_adres: '',
      kapi_adi: '',
      aciklama: '',
      aktif: true,
    });
    setEditMode(false);
    setCurrentDevice(null);
  };

  const handleOpenDoor = async (id) => {
    try {
      await axios.post(`${API}/nodemcu/${id}/open`);
      toast.success('Kapı açma komutu gönderildi');
    } catch (error) {
      toast.error('Kapı açılamadı');
    }
  };

  const checkStatus = async (id) => {
    try {
      const response = await axios.get(`${API}/nodemcu/${id}/status`);
      if (response.data.online) {
        toast.success('Çevre birimi online');
      } else {
        toast.error('Çevre birimi offline');
      }
    } catch (error) {
      toast.error('Durum kontrol edilemedi');
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
            Kapı Kontrolü (NodeMCU)
          </h1>
          <p className="text-slate-400 mt-1">NodeMCU cihazlarını ve kapıları yönetin</p>
        </div>

        <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) resetForm(); }}>
          <DialogTrigger asChild>
            <Button className="bg-sky-600 hover:bg-sky-700" data-testid="add-nodemcu-button">
              <Plus className="w-4 h-4 mr-2" />
              Yeni Cihaz Ekle
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-slate-900 border-slate-700 max-w-2xl" data-testid="add-nodemcu-dialog">
            <DialogHeader>
              <DialogTitle className="text-white">{editMode ? 'Cihaz Düzenle' : 'Yeni Cihaz Ekle'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-slate-300">NodeMCU ID *</Label>
                  <Input
                    required
                    placeholder="KAPI-001"
                    value={formData.nodemcu_id}
                    onChange={(e) => setFormData({ ...formData, nodemcu_id: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                    data-testid="nodemcu-id-input"
                  />
                </div>
                <div>
                  <Label className="text-slate-300">IP Adresi *</Label>
                  <Input
                    required
                    placeholder="192.168.1.50"
                    value={formData.ip_adres}
                    onChange={(e) => setFormData({ ...formData, ip_adres: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                    data-testid="ip-address-input"
                  />
                </div>
              </div>

              <div>
                <Label className="text-slate-300">Kapı Adı *</Label>
                <Input
                  required
                  placeholder="Ana Giriş Kapısı"
                  value={formData.kapi_adi}
                  onChange={(e) => setFormData({ ...formData, kapi_adi: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>

              <div>
                <Label className="text-slate-300">Açıklama</Label>
                <Input
                  value={formData.aciklama}
                  onChange={(e) => setFormData({ ...formData, aciklama: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                  placeholder="Opsiyonel"
                />
              </div>

              <Button type="submit" className="w-full bg-sky-600 hover:bg-sky-700" data-testid="submit-nodemcu-button">
                {editMode ? 'Güncelle' : 'Cihaz Ekle'}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {devices.map((device) => (
          <Card key={device.id} className="bg-slate-800/50 border-slate-700 p-6" data-testid={`nodemcu-card-${device.id}`}>
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                  <DoorOpen className="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                  <h3 className="font-bold text-white" data-testid="door-name">{device.kapi_adi}</h3>
                  <p className="text-sm text-slate-400">{device.nodemcu_id}</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={() => handleEdit(device)} className="text-slate-400 hover:text-white">
                  <Edit className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(device.id)}
                  className="text-red-400 hover:text-red-300"
                  data-testid="delete-nodemcu-button"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Badge className={device.aktif ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-slate-500/20 text-slate-400 border-slate-500/30'}>
                  {device.aktif ? <Wifi className="w-3 h-3 mr-1" /> : <WifiOff className="w-3 h-3 mr-1" />}
                  {device.aktif ? 'Aktif' : 'Pasif'}
                </Badge>
              </div>

              <div className="text-sm space-y-1">
                <p className="text-slate-400"><span className="text-slate-500">IP:</span> {device.ip_adres}</p>
                {device.aciklama && <p className="text-slate-400">{device.aciklama}</p>}
              </div>

              <div className="flex gap-2 pt-2">
                <Button
                  onClick={() => handleOpenDoor(device.id)}
                  size="sm"
                  className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                  data-testid="open-door-button"
                >
                  <Unlock className="w-4 h-4 mr-1" />
                  Kapıyı Aç
                </Button>
                <Button
                  onClick={() => checkStatus(device.id)}
                  size="sm"
                  variant="outline"
                  className="border-slate-600 text-slate-300"
                >
                  Durum
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {devices.length === 0 && (
        <div className="text-center py-12 text-slate-400" data-testid="no-devices-message">
          <DoorOpen className="w-16 h-16 mx-auto mb-4 opacity-20" />
          <p>Henüz cihaz eklenmemiş</p>
        </div>
      )}
    </div>
  );
};

export default NodeMCUManagement;