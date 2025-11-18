import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Camera, Building2, CreditCard, DoorOpen, FileText, Settings, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();

  const menuItems = [
    { path: '/', icon: Camera, label: 'Dashboard', testId: 'menu-dashboard' },
    { path: '/sites', icon: Building2, label: 'Site Yönetimi', testId: 'menu-sites' },
    { path: '/plates', icon: CreditCard, label: 'Plaka Yönetimi', testId: 'menu-plates' },
    { path: '/cameras', icon: Camera, label: 'Kamera Yönetimi', testId: 'menu-cameras' },
    { path: '/nodemcu', icon: DoorOpen, label: 'Kapı Kontrolü', testId: 'menu-nodemcu' },
    { path: '/reports', icon: FileText, label: 'Raporlar', testId: 'menu-reports' },
    { path: '/settings', icon: Settings, label: 'Ayarlar', testId: 'menu-settings' },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-0'
        } transition-all duration-300 bg-slate-900/50 border-r border-slate-800 backdrop-blur-xl overflow-hidden`}
        data-testid="sidebar"
      >
        <div className="p-6 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center">
              <Camera className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
                Plaka Tanıma
              </h2>
              <p className="text-xs text-slate-400">Yönetim Paneli</p>
            </div>
          </div>
        </div>

        <nav className="p-4 space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                data-testid={item.testId}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  active
                    ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30'
                    : 'text-slate-400 hover:bg-slate-800/50 hover:text-white'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl">
          <div className="px-6 py-4 flex items-center justify-between">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="text-slate-400 hover:text-white"
              data-testid="sidebar-toggle"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>

            <div className="text-sm text-slate-400">
              Hoş geldiniz, Admin
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;