import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const Settings = () => {
  const [settings, setSettings] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await axios.get(`${API}/settings`);
      setSettings(response.data);
    } catch (error) {
      toast.error('Ayarlar yüklenemedi');
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/settings`, settings);
      toast.success('Ayarlar kaydedildi');
    } catch (error) {
      toast.error('Ayarlar kaydedilemedi');
    } finally {
      setLoading(false);
    }
  };

  if (!settings) return <div className="p-6 text-slate-400">Yükleniyor...</div>;

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
          Sistem Ayarları
        </h1>
        <p className="text-slate-400 mt-1">Plaka tanıma ve sistem parametreleri</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* OCR Ayarları */}
        <Card className="bg-slate-800/50 border-slate-700 p-6" data-testid="ocr-settings-card">
          <h3 className="text-lg font-semibold text-white mb-4">OCR Motor</h3>
          <div className="space-y-4">
            <div>
              <Label className="text-slate-300">Motor Seçimi</Label>
              <Select
                value={settings?.ocr_motor || 'paddleocr'}
                onValueChange={(value) => setSettings({ ...settings, ocr_motor: value })}
              >
                <SelectTrigger className="bg-slate-900 border-slate-700 text-white" data-testid="ocr-engine-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-700">
                  <SelectItem value="paddleocr">PaddleOCR (Hızlı)</SelectItem>
                  <SelectItem value="easyocr">EasyOCR (Daha Doğru)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label className="text-slate-300">AI Plaka Düzeltme</Label>
                <p className="text-xs text-slate-500">Hatalı karakterleri düzelt</p>
              </div>
              <Switch
                checked={settings.ai_duzeltme_aktif}
                onCheckedChange={(checked) => setSettings({ ...settings, ai_duzeltme_aktif: checked })}
                data-testid="ai-correction-switch"
              />
            </div>

            <div>
              <Label className="text-slate-300">OCR Güven Eşiği</Label>
              <Input
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={settings.ocr_confidence}
                onChange={(e) => setSettings({ ...settings, ocr_confidence: parseFloat(e.target.value) })}
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
          </div>
        </Card>

        {/* YOLO Ayarları */}
        <Card className="bg-slate-800/50 border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">YOLO Plaka Tespiti</h3>
          <div className="space-y-4">
            <div>
              <Label className="text-slate-300">Güven Eşiği</Label>
              <Input
                type="number"
                step="0.1"
                min="0"
                max="1"
                value={settings.yolo_confidence}
                onChange={(e) => setSettings({ ...settings, yolo_confidence: parseFloat(e.target.value) })}
                className="bg-slate-900 border-slate-700 text-white"
                data-testid="yolo-confidence-input"
              />
              <p className="text-xs text-slate-500 mt-1">Önerilen: 0.3 - 0.5</p>
            </div>
          </div>
        </Card>

        {/* Gece Modu */}
        <Card className="bg-slate-800/50 border-slate-700 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Gece Modu</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label className="text-slate-300">Gece Modu Aktif</Label>
              <Switch
                checked={settings.gece_modu_aktif}
                onCheckedChange={(checked) => setSettings({ ...settings, gece_modu_aktif: checked })}
                data-testid="night-mode-switch"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-slate-300">Başlangıç Saati</Label>
                <Input
                  type="time"
                  value={settings.gece_modu_baslangic}
                  onChange={(e) => setSettings({ ...settings, gece_modu_baslangic: e.target.value })}
                  className="bg-slate-900 border-slate-700 text-white"
                />
              </div>
              <div>
                <Label className="text-slate-300">Bitiş Saati</Label>
                <Input
                  type="time"
                  value={settings.gece_modu_bitis}
                  onChange={(e) => setSettings({ ...settings, gece_modu_bitis: e.target.value })}
                  className="bg-slate-900 border-slate-700 text-white"
                />
              </div>
            </div>

            <div>
              <Label className="text-slate-300">Parlaklık Çarpanı</Label>
              <Input
                type="number"
                step="0.1"
                min="0.5"
                max="2"
                value={settings.gece_brightness}
                onChange={(e) => setSettings({ ...settings, gece_brightness: parseFloat(e.target.value) })}
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>

            <div>
              <Label className="text-slate-300">Kontrast Çarpanı</Label>
              <Input
                type="number"
                step="0.1"
                min="0.5"
                max="2"
                value={settings.gece_contrast}
                onChange={(e) => setSettings({ ...settings, gece_contrast: parseFloat(e.target.value) })}
                className="bg-slate-900 border-slate-700 text-white"
              />
            </div>
          </div>
        </Card>
      </div>

      <div className="flex justify-end">
        <Button
          onClick={handleSave}
          disabled={loading}
          className="bg-sky-600 hover:bg-sky-700"
          data-testid="save-settings-button"
        >
          {loading ? 'Kaydediliyor...' : 'Ayarları Kaydet'}
        </Button>
      </div>
    </div>
  );
};

export default Settings;