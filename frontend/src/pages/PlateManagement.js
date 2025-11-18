import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Plus, Edit, Trash2, CreditCard, Search } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const PlateManagement = () => {
  const [plates, setPlates] = useState([]);
  const [sites, setSites] = useState([]);
  const [open, setOpen] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [currentPlate, setCurrentPlate] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    site_id: '',
    blok_id: '',
    daire_id: '',
    plaka_no: '',
    isim_soyisim: '',
    telefon: '',
    arac_tipi: 'Sedan',
    durum: 'Tanımlı',
    not_: '',
  });

  useEffect(() => {
    fetchPlates();
    fetchSites();
  }, []);

  const fetchPlates = async () => {
    try {
      const response = await axios.get(`${API}/plates`);
      setPlates(response.data);
    } catch (error) {
      toast.error('Plakalar yüklenemedi');
    }
  };

  const fetchSites = async () => {
    try {
      const response = await axios.get(`${API}/sites`);
      setSites(response.data);
    } catch (error) {
      console.error('Siteler yüklenemedi');
    }
  };

  // Seçili site, blok ve daireyi hesapla
  const selectedSite = sites.find(s => s.id === formData.site_id) || null;
  const selectedBlok = selectedSite?.bloklar?.find(b => b.id === formData.blok_id) || null;
  const selectedDaire = selectedBlok?.daireler?.find(d => d.id === formData.daire_id) || null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const plakaData = {
        plaka_no: formData.plaka_no,
        site_id: formData.site_id,
        blok_id: formData.blok_id,
        daire_id: formData.daire_id,
        arac_tipi: formData.arac_tipi,
        durum: formData.durum,
        not_: formData.not_,
        // Daire bilgileri - Backend senkronizasyonu için
        isim_soyisim: formData.isim_soyisim,
        telefon: formData.telefon
      };

      if (editMode && currentPlate) {
        // DÜZENLEME MODU - Backend otomatik daire senkronizasyonu yapacak
        await axios.put(`${API}/plates/${currentPlate.id}`, plakaData);
        toast.success('Plaka güncellendi');
      } else {
        // YENİ PLAKA EKLEME - Backend otomatik daire senkronizasyonu yapacak
        await axios.post(`${API}/plates`, plakaData);
        toast.success('Plaka eklendi');
      }
      
      setOpen(false);
      resetForm();
      fetchPlates();
      fetchSites(); // Site bilgilerini yenile
    } catch (error) {
      console.error('Plaka işlemi hatası:', error);
      toast.error(error.response?.data?.detail || 'Plaka işlemi başarısız');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Plakayı silmek istediğinize emin misiniz?')) return;
    try {
      await axios.delete(`${API}/plates/${id}`);
      toast.success('Plaka silindi');
      fetchPlates();
      fetchSites();
    } catch (error) {
      toast.error('Plaka silinemedi');
    }
  };

  const handleEdit = (plate) => {
    const site = sites.find(s => s.id === plate.site_id);
    const blok = site?.bloklar?.find(b => b.id === plate.blok_id);
    const daire = blok?.daireler?.find(d => d.id === plate.daire_id);

    setCurrentPlate(plate);
    setFormData({
      site_id: plate.site_id || '',
      blok_id: plate.blok_id || '',
      daire_id: plate.daire_id || '',
      plaka_no: plate.plaka_no || '',
      isim_soyisim: daire?.isim_soyisim || '',
      telefon: daire?.telefon || '',
      arac_tipi: plate.arac_tipi || 'Sedan',
      durum: plate.durum || 'Tanımlı',
      not_: plate.not_ || '',
    });
    setEditMode(true);
    setOpen(true);
  };

  const resetForm = () => {
    setFormData({
      site_id: '',
      blok_id: '',
      daire_id: '',
      plaka_no: '',
      isim_soyisim: '',
      telefon: '',
      arac_tipi: 'Sedan',
      durum: 'Tanımlı',
      not_: '',
    });
    setEditMode(false);
    setCurrentPlate(null);
  };

  const getStatusBadge = (durum) => {
    const colors = {
      'Tanımlı': 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
      'Misafir': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      'Yasaklı': 'bg-red-500/20 text-red-400 border-red-500/30',
    };
    return <Badge className={colors[durum] || colors['Tanımlı']}>{durum}</Badge>;
  };

  // Daire seçildiğinde bilgileri doldur (sadece yeni ekleme modunda)
  useEffect(() => {
    if (selectedDaire && !editMode) {
      setFormData(prev => ({
        ...prev,
        isim_soyisim: selectedDaire.isim_soyisim === 'Boş' ? '' : selectedDaire.isim_soyisim,
        telefon: selectedDaire.telefon === '-' ? '' : selectedDaire.telefon,
      }));
    }
  }, [formData.daire_id, editMode, selectedDaire]);

  const filteredPlates = plates.filter(plate => 
    plate.plaka_no.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
            Plaka Yönetimi
          </h1>
          <p className="text-slate-400 mt-1">Araç plakalarını yönetin</p>
        </div>

        <Dialog open={open} onOpenChange={(o) => { setOpen(o); if (!o) resetForm(); }}>
          <DialogTrigger asChild>
            <Button className="bg-sky-600 hover:bg-sky-700" data-testid="add-plate-button">
              <Plus className="w-4 h-4 mr-2" />
              Yeni Plaka Ekle
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-slate-900 border-slate-700 max-w-2xl" data-testid="add-plate-dialog">
            <DialogHeader>
              <DialogTitle className="text-white">{editMode ? 'Plaka Düzenle' : 'Yeni Plaka Ekle'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label className="text-slate-300">Site *</Label>
                <Select 
                  value={formData.site_id || undefined} 
                  onValueChange={(v) => setFormData({ ...formData, site_id: v, blok_id: '', daire_id: '' })}
                >
                  <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                    <SelectValue placeholder="Site seçin" />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-700">
                    {sites.length > 0 ? (
                      sites.map(site => (
                        <SelectItem key={site.id} value={site.id}>{site.site_adi}</SelectItem>
                      ))
                    ) : (
                      <div className="p-2 text-slate-400 text-sm">Site bulunamadı</div>
                    )}
                  </SelectContent>
                </Select>
              </div>

              {formData.site_id && selectedSite && (
                <div>
                  <Label className="text-slate-300">Blok *</Label>
                  <Select 
                    value={formData.blok_id || undefined} 
                    onValueChange={(v) => setFormData({ ...formData, blok_id: v, daire_id: '' })}
                  >
                    <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                      <SelectValue placeholder="Blok seçin" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      {selectedSite.bloklar && selectedSite.bloklar.length > 0 ? (
                        selectedSite.bloklar.map(blok => (
                          <SelectItem key={blok.id} value={blok.id}>Blok {blok.blok_adi}</SelectItem>
                        ))
                      ) : (
                        <div className="p-2 text-slate-400 text-sm">Bu sitede blok yok</div>
                      )}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {formData.blok_id && selectedBlok && (
                <div>
                  <Label className="text-slate-300">Daire No *</Label>
                  <Select 
                    value={formData.daire_id || undefined} 
                    onValueChange={(v) => setFormData({ ...formData, daire_id: v })}
                  >
                    <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                      <SelectValue placeholder="Daire seçin" />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      {selectedBlok.daireler && selectedBlok.daireler.length > 0 ? (
                        selectedBlok.daireler.map(daire => (
                          <SelectItem key={daire.id} value={daire.id}>
                            Daire {daire.daire_no}
                          </SelectItem>
                        ))
                      ) : (
                        <div className="p-2 text-slate-400 text-sm">Bu blokta daire yok</div>
                      )}
                    </SelectContent>
                  </Select>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-slate-300">İsim Soyisim *</Label>
                  <Input
                    required
                    value={formData.isim_soyisim}
                    onChange={(e) => setFormData({ ...formData, isim_soyisim: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
                <div>
                  <Label className="text-slate-300">Telefon *</Label>
                  <Input
                    required
                    value={formData.telefon}
                    onChange={(e) => setFormData({ ...formData, telefon: e.target.value })}
                    className="bg-slate-800 border-slate-700 text-white"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-slate-300">Plaka Numarası *</Label>
                  <Input
                    required
                    placeholder="34ABC123"
                    value={formData.plaka_no}
                    onChange={(e) => setFormData({ ...formData, plaka_no: e.target.value.toUpperCase() })}
                    className="bg-slate-800 border-slate-700 text-white"
                    data-testid="plate-number-input"
                  />
                </div>
                <div>
                  <Label className="text-slate-300">Araç Tipi</Label>
                  <Select value={formData.arac_tipi} onValueChange={(v) => setFormData({ ...formData, arac_tipi: v })}>
                    <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-slate-900 border-slate-700">
                      <SelectItem value="Sedan">Sedan</SelectItem>
                      <SelectItem value="SUV">SUV</SelectItem>
                      <SelectItem value="Hatchback">Hatchback</SelectItem>
                      <SelectItem value="Kamyon">Kamyon</SelectItem>
                      <SelectItem value="Minibüs">Minibüs</SelectItem>
                      <SelectItem value="Motosiklet">Motosiklet</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label className="text-slate-300">Durum</Label>
                <Select value={formData.durum} onValueChange={(v) => setFormData({ ...formData, durum: v })}>
                  <SelectTrigger className="bg-slate-800 border-slate-700 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-slate-900 border-slate-700">
                    <SelectItem value="Tanımlı">Tanımlı</SelectItem>
                    <SelectItem value="Yasaklı">Yasaklı</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label className="text-slate-300">Not</Label>
                <Input
                  value={formData.not_}
                  onChange={(e) => setFormData({ ...formData, not_: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                  placeholder="Opsiyonel"
                />
              </div>

              <Button type="submit" className="w-full bg-sky-600 hover:bg-sky-700" data-testid="submit-plate-button">
                {editMode ? 'Güncelle' : 'Plaka Ekle'}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            placeholder="Plaka ara..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 bg-slate-800 border-slate-700 text-white"
            data-testid="search-plate-input"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredPlates.map((plate) => {
          const site = sites.find(s => s.id === plate.site_id);
          const blok = site?.bloklar?.find(b => b.id === plate.blok_id);
          const daire = blok?.daireler?.find(d => d.id === plate.daire_id);

          return (
            <Card key={plate.id} className="bg-slate-800/50 border-slate-700 p-6" data-testid={`plate-card-${plate.id}`}>
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-lg bg-sky-500/20 flex items-center justify-center">
                    <CreditCard className="w-6 h-6 text-sky-400" />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-lg" data-testid="plate-number">{plate.plaka_no}</h3>
                    <p className="text-sm text-slate-400">{plate.arac_tipi}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="ghost" size="sm" onClick={() => handleEdit(plate)} className="text-slate-400 hover:text-white">
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(plate.id)}
                    className="text-red-400 hover:text-red-300"
                    data-testid="delete-plate-button"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <div className="space-y-2">
                {getStatusBadge(plate.durum)}
                {daire && (
                  <div className="text-sm text-slate-400 mt-2">
                    <p>{daire.isim_soyisim}</p>
                    <p className="text-xs text-slate-500">{site?.site_adi} - Blok {blok?.blok_adi} - Daire {daire.daire_no}</p>
                  </div>
                )}
                {plate.not_ && <p className="text-sm text-slate-400 mt-2">{plate.not_}</p>}
              </div>
            </Card>
          );
        })}
      </div>

      {filteredPlates.length === 0 && (
        <div className="text-center py-12 text-slate-400" data-testid="no-plates-message">
          <CreditCard className="w-16 h-16 mx-auto mb-4 opacity-20" />
          <p>Henüz plaka eklenmemiş</p>
        </div>
      )}
    </div>
  );
};

export default PlateManagement;