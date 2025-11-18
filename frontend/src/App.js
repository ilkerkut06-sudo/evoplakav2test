import React from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from '@/components/Layout';
import Dashboard from '@/pages/Dashboard';
import SiteManagement from '@/pages/SiteManagement';
import Settings from '@/pages/Settings';
import { Toaster } from '@/components/ui/sonner';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/sites" element={<SiteManagement />} />
            <Route path="/plates" element={<div className="p-6 text-white">Plaka Yönetimi - Yakında</div>} />
            <Route path="/cameras" element={<div className="p-6 text-white">Kamera Yönetimi - Yakında</div>} />
            <Route path="/nodemcu" element={<div className="p-6 text-white">Kapı Kontrolü - Yakında</div>} />
            <Route path="/reports" element={<div className="p-6 text-white">Raporlar - Yakında</div>} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </BrowserRouter>
      <Toaster position="top-right" />
    </div>
  );
}

export default App;