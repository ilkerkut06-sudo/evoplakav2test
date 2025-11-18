import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Plus, Edit, Trash2, Building2 } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SiteManagement = () => {
  const [sites, setSites] = useState([]);
  const [open, setOpen] = useState(false);
  const [formData, setFormData] = useState({
    site_adi: '',
    adres: '',
    yonetici_adi: '',
    yonetici_telefon: '',
  });

  useEffect(() => {
    fetchSites();
  }, []);

  const fetchSites = async () => {
    try {
      const response = await axios.get(`${API}/sites`);
      setSites(response.data);
    } catch (error) {
      toast.error('Siteler yüklenemedi');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/sites`, formData);
      toast.success('Site eklendi');
      setOpen(false);
      setFormData({ site_adi: '', adres: '', yonetici_adi: '', yonetici_telefon: '' });
      fetchSites();
    } catch (error) {
      toast.error('Site eklenemedi');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Siteyi silmek istediğinize emin misiniz?')) return;
    try {
      await axios.delete(`${API}/sites/${id}`);
      toast.success('Site silindi');
      fetchSites();
    } catch (error) {
      toast.error('Site silinemedi');
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
            Site Yönetimi
          </h1>
          <p className="text-slate-400 mt-1">Site, blok ve daire yönetimi</p>
        </div>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button className="bg-sky-600 hover:bg-sky-700" data-testid="add-site-button">
              <Plus className="w-4 h-4 mr-2" />
              Yeni Site Ekle
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-slate-900 border-slate-700" data-testid="add-site-dialog">
            <DialogHeader>
              <DialogTitle className="text-white">Yeni Site Ekle</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label className="text-slate-300">Site Adı *</Label>
                <Input
                  required
                  value={formData.site_adi}
                  onChange={(e) => setFormData({ ...formData, site_adi: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                  data-testid="site-name-input"
                />
              </div>
              <div>
                <Label className="text-slate-300">Adres *</Label>
                <Input
                  required
                  value={formData.adres}
                  onChange={(e) => setFormData({ ...formData, adres: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                  data-testid="site-address-input"
                />
              </div>
              <div>
                <Label className="text-slate-300">Yönetici Adı</Label>
                <Input
                  value={formData.yonetici_adi}
                  onChange={(e) => setFormData({ ...formData, yonetici_adi: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <div>
                <Label className="text-slate-300">Yönetici Telefon</Label>
                <Input
                  value={formData.yonetici_telefon}
                  onChange={(e) => setFormData({ ...formData, yonetici_telefon: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <Button type="submit" className="w-full bg-sky-600 hover:bg-sky-700" data-testid="submit-site-button">
                Site Ekle
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sites.map((site) => (
          <Card key={site.id} className="bg-slate-800/50 border-slate-700 p-6" data-testid={`site-card-${site.id}`}>
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-lg bg-sky-500/20 flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-sky-400" />
                </div>
                <div>
                  <h3 className="font-bold text-white" data-testid="site-name">{site.site_adi}</h3>
                  <p className="text-sm text-slate-400">{site.bloklar?.length || 0} Blok</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" className="text-slate-400 hover:text-white">
                  <Edit className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDelete(site.id)}
                  className="text-red-400 hover:text-red-300"
                  data-testid="delete-site-button"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div className="space-y-2 text-sm">
              <p className="text-slate-400"><span className="text-slate-500">Adres:</span> {site.adres}</p>
              {site.yonetici_adi && (
                <p className="text-slate-400"><span className="text-slate-500">Yönetici:</span> {site.yonetici_adi}</p>
              )}
            </div>
          </Card>
        ))}
      </div>

      {sites.length === 0 && (
        <div className="text-center py-12 text-slate-400" data-testid="no-sites-message">
          <Building2 className="w-16 h-16 mx-auto mb-4 opacity-20" />
          <p>Henüz site eklenmemiş</p>
        </div>
      )}
    </div>
  );
};

export default SiteManagement;