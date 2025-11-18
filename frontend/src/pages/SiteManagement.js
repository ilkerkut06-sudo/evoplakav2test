import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Plus, Edit, Trash2, Building2, Home, Users } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const SiteManagement = () => {
  const [sites, setSites] = useState([]);
  const [openSite, setOpenSite] = useState(false);
  const [openBlok, setOpenBlok] = useState(false);
  const [selectedSite, setSelectedSite] = useState(null);
  const [selectedBlok, setSelectedBlok] = useState(null);
  const [editSiteMode, setEditSiteMode] = useState(false);
  const [editBlokMode, setEditBlokMode] = useState(false);
  
  const [siteForm, setSiteForm] = useState({
    site_adi: '',
    adres: '',
    yonetici_adi: '',
    yonetici_telefon: '',
  });

  const [blokForm, setBlokForm] = useState({
    blok_adi: '',
    daire_sayisi: 1,
    aciklama: '',
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

  const handleSiteSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editSiteMode && selectedSite) {
        await axios.put(`${API}/sites/${selectedSite.id}`, siteForm);
        toast.success('Site güncellendi');
      } else {
        await axios.post(`${API}/sites`, siteForm);
        toast.success('Site eklendi');
      }
      setOpenSite(false);
      resetSiteForm();
      fetchSites();
    } catch (error) {
      toast.error('Site işlemi başarısız');
    }
  };

  const handleBlokSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editBlokMode && selectedBlok) {
        await axios.put(`${API}/sites/${selectedSite.id}/bloklar/${selectedBlok.id}`, blokForm);
        toast.success('Blok güncellendi');
      } else {
        await axios.post(`${API}/sites/${selectedSite.id}/bloklar`, blokForm);
        toast.success(`Blok ve ${blokForm.daire_sayisi} daire eklendi`);
      }
      setOpenBlok(false);
      resetBlokForm();
      fetchSites();
    } catch (error) {
      toast.error('Blok işlemi başarısız');
    }
  };

  const handleDeleteSite = async (id) => {
    if (!window.confirm('Siteyi silmek istediğinize emin misiniz?')) return;
    try {
      await axios.delete(`${API}/sites/${id}`);
      toast.success('Site silindi');
      fetchSites();
    } catch (error) {
      toast.error('Site silinemedi');
    }
  };

  const handleDeleteBlok = async (siteId, blokId) => {
    if (!window.confirm('Bloku silmek istediğinize emin misiniz?')) return;
    try {
      await axios.delete(`${API}/sites/${siteId}/bloklar/${blokId}`);
      toast.success('Blok silindi');
      fetchSites();
    } catch (error) {
      toast.error('Blok silinemedi');
    }
  };

  const handleEditSite = (site) => {
    setSelectedSite(site);
    setSiteForm({
      site_adi: site.site_adi,
      adres: site.adres,
      yonetici_adi: site.yonetici_adi || '',
      yonetici_telefon: site.yonetici_telefon || '',
    });
    setEditSiteMode(true);
    setOpenSite(true);
  };

  const handleEditBlok = (site, blok) => {
    setSelectedSite(site);
    setSelectedBlok(blok);
    setBlokForm({
      blok_adi: blok.blok_adi,
      daire_sayisi: blok.daire_sayisi || blok.daireler?.length || 0,
      aciklama: blok.aciklama || '',
    });
    setEditBlokMode(true);
    setOpenBlok(true);
  };

  const resetSiteForm = () => {
    setSiteForm({ site_adi: '', adres: '', yonetici_adi: '', yonetici_telefon: '' });
    setEditSiteMode(false);
    setSelectedSite(null);
  };

  const resetBlokForm = () => {
    setBlokForm({ blok_adi: '', daire_sayisi: 1, aciklama: '' });
    setEditBlokMode(false);
    setSelectedBlok(null);
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
            Site Yönetimi
          </h1>
          <p className="text-slate-400 mt-1">Site yapısını oluşturun (Site → Blok → Daire)</p>
        </div>

        <Dialog open={openSite} onOpenChange={(o) => { setOpenSite(o); if (!o) resetSiteForm(); }}>
          <DialogTrigger asChild>
            <Button className="bg-sky-600 hover:bg-sky-700" data-testid="add-site-button">
              <Plus className="w-4 h-4 mr-2" />
              Yeni Site Ekle
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-slate-900 border-slate-700" data-testid="add-site-dialog">
            <DialogHeader>
              <DialogTitle className="text-white">{editSiteMode ? 'Site Düzenle' : 'Yeni Site Ekle'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSiteSubmit} className="space-y-4">
              <div>
                <Label className="text-slate-300">Site Adı *</Label>
                <Input
                  required
                  value={siteForm.site_adi}
                  onChange={(e) => setSiteForm({ ...siteForm, site_adi: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <div>
                <Label className="text-slate-300">Adres *</Label>
                <Input
                  required
                  value={siteForm.adres}
                  onChange={(e) => setSiteForm({ ...siteForm, adres: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <div>
                <Label className="text-slate-300">Yönetici Adı</Label>
                <Input
                  value={siteForm.yonetici_adi}
                  onChange={(e) => setSiteForm({ ...siteForm, yonetici_adi: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <div>
                <Label className="text-slate-300">Yönetici Telefon</Label>
                <Input
                  value={siteForm.yonetici_telefon}
                  onChange={(e) => setSiteForm({ ...siteForm, yonetici_telefon: e.target.value })}
                  className="bg-slate-800 border-slate-700 text-white"
                />
              </div>
              <Button type="submit" className="w-full bg-sky-600 hover:bg-sky-700">
                {editSiteMode ? 'Güncelle' : 'Site Ekle'}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Blok Ekleme/Düzenleme Dialog */}
      <Dialog open={openBlok} onOpenChange={(o) => { setOpenBlok(o); if (!o) resetBlokForm(); }}>
        <DialogContent className="bg-slate-900 border-slate-700">
          <DialogHeader>
            <DialogTitle className="text-white">
              {editBlokMode ? `Blok Düzenle - ${selectedSite?.site_adi}` : `Blok Ekle - ${selectedSite?.site_adi}`}
            </DialogTitle>
          </DialogHeader>
          <form onSubmit={handleBlokSubmit} className="space-y-4">
            <div>
              <Label className="text-slate-300">Blok Adı *</Label>
              <Input
                required
                placeholder="A, B, C..."
                value={blokForm.blok_adi}
                onChange={(e) => setBlokForm({ ...blokForm, blok_adi: e.target.value })}
                className="bg-slate-800 border-slate-700 text-white"
              />
            </div>
            <div>
              <Label className="text-slate-300">Daire Sayısı *</Label>
              <Input
                required
                type="number"
                min="1"
                max="200"
                placeholder="55"
                value={blokForm.daire_sayisi}
                onChange={(e) => setBlokForm({ ...blokForm, daire_sayisi: parseInt(e.target.value) || 1 })}
                className="bg-slate-800 border-slate-700 text-white"
              />
              {editBlokMode ? (
                <p className="text-xs text-amber-500 mt-1">Uyarı: Daire sayısı değiştirilirse mevcut daireler etkilenebilir</p>
              ) : (
                <p className="text-xs text-slate-500 mt-1">Bu sayıda daire otomatik oluşturulacak (1'den başlayarak)</p>
              )}
            </div>
            <div>
              <Label className="text-slate-300">Açıklama</Label>
              <Input
                value={blokForm.aciklama}
                onChange={(e) => setBlokForm({ ...blokForm, aciklama: e.target.value })}
                className="bg-slate-800 border-slate-700 text-white"
              />
            </div>
            <Button type="submit" className="w-full bg-sky-600 hover:bg-sky-700">
              {editBlokMode ? 'Güncelle' : 'Blok ve Daireleri Oluştur'}
            </Button>
          </form>
        </DialogContent>
      </Dialog>

      {/* Site Listesi */}
      <div className="space-y-4">
        {sites.map((site) => (
          <Card key={site.id} className="bg-slate-800/50 border-slate-700 p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-lg bg-sky-500/20 flex items-center justify-center">
                  <Building2 className="w-6 h-6 text-sky-400" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-lg">{site.site_adi}</h3>
                  <p className="text-sm text-slate-400">{site.adres}</p>
                  <p className="text-xs text-slate-500 mt-1">{site.bloklar?.length || 0} Blok</p>
                </div>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleEditSite(site)}
                  className="text-slate-400 hover:text-white"
                >
                  <Edit className="w-4 h-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => { setSelectedSite(site); setOpenBlok(true); }}
                  className="text-emerald-400 hover:text-emerald-300"
                >
                  <Plus className="w-4 h-4 mr-1" />
                  Blok
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDeleteSite(site.id)}
                  className="text-red-400 hover:text-red-300"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {/* Bloklar */}
            {site.bloklar && site.bloklar.length > 0 && (
              <Accordion type="single" collapsible className="mt-4">
                {site.bloklar.map((blok) => (
                  <AccordionItem key={blok.id} value={blok.id} className="border-slate-700">
                    <AccordionTrigger className="text-white hover:text-sky-400">
                      <div className="flex items-center gap-2">
                        <Home className="w-4 h-4" />
                        Blok {blok.blok_adi} ({blok.daireler?.length || 0} Daire)
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="space-y-2 pt-2">
                        <div className="flex gap-2 mb-3">
                          <Button
                            size="sm"
                            onClick={() => handleEditBlok(site, blok)}
                            className="bg-sky-600 hover:bg-sky-700"
                          >
                            <Edit className="w-3 h-3 mr-1" />
                            Blok Düzenle
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleDeleteBlok(site.id, blok.id)}
                          >
                            <Trash2 className="w-3 h-3 mr-1" />
                            Blok Sil
                          </Button>
                        </div>

                        {/* Daireler - SİL BUTONU KALDIRILDI */}
                        {blok.daireler && blok.daireler.length > 0 ? (
                          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2">
                            {blok.daireler.map((daire) => (
                              <Card key={daire.id} className="bg-slate-900/50 border-slate-700 p-2">
                                <div className="flex items-center gap-1">
                                  <Users className="w-3 h-3 text-slate-400" />
                                  <span className="text-xs font-semibold text-white">{daire.daire_no}</span>
                                </div>
                                {daire.isim_soyisim && daire.isim_soyisim !== 'Boş' && (
                                  <p className="text-xs text-slate-400 mt-1 truncate">{daire.isim_soyisim}</p>
                                )}
                              </Card>
                            ))}
                          </div>
                        ) : (
                          <p className="text-sm text-slate-500 italic">Henüz daire eklenmemiş</p>
                        )}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            )}
          </Card>
        ))}
      </div>

      {sites.length === 0 && (
        <div className="text-center py-12 text-slate-400">
          <Building2 className="w-16 h-16 mx-auto mb-4 opacity-20" />
          <p>Henüz site eklenmemiş</p>
        </div>
      )}
    </div>
  );
};

export default SiteManagement;