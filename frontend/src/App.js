import React from 'react';
import '@/App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from '@/components/Layout';
import Dashboard from '@/pages/Dashboard';
import SiteManagement from '@/pages/SiteManagement';
import PlateManagement from '@/pages/PlateManagement';
import CameraManagement from '@/pages/CameraManagement';
import NodeMCUManagement from '@/pages/NodeMCUManagement';
import Reports from '@/pages/Reports';
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
            <Route path="/plates" element={<PlateManagement />} />
            <Route path="/cameras" element={<CameraManagement />} />
            <Route path="/nodemcu" element={<NodeMCUManagement />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </BrowserRouter>
      <Toaster position="top-right" />
    </div>
  );
}

export default App;