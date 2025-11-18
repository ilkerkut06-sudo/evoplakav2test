import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Activity, Camera, DoorOpen, Car, AlertTriangle, CheckCircle } from 'lucide-react';
import CameraGrid from '@/components/CameraGrid';
import LogPanel from '@/components/LogPanel';
import LiveTicker from '@/components/LiveTicker';
import SystemStatus from '@/components/SystemStatus';
import StatsCards from '@/components/StatsCards';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [cameras, setCameras] = useState([]);
  const [logs, setLogs] = useState([]);
  const [systemStatus, setSystemStatus] = useState(null);

  useEffect(() => {
    fetchStats();
    fetchCameras();
    fetchLogs();
    fetchSystemStatus();

    // Her 5 saniyede bir güncelle
    const interval = setInterval(() => {
      fetchStats();
      fetchLogs();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/logs/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('İstatistikler alınamadı:', error);
    }
  };

  const fetchCameras = async () => {
    try {
      const response = await axios.get(`${API}/cameras?aktif=true`);
      setCameras(response.data);
    } catch (error) {
      console.error('Kameralar alınamadı:', error);
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await axios.get(`${API}/logs?limit=20`);
      setLogs(response.data);
    } catch (error) {
      console.error('Loglar alınamadı:', error);
    }
  };

  const fetchSystemStatus = async () => {
    try {
      const response = await axios.get(`${API}/settings/system-status`);
      setSystemStatus(response.data);
    } catch (error) {
      console.error('Sistem durumu alınamadı:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <div className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-xl">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center">
                <Camera className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
                  Plaka Tanıma Sistemi
                </h1>
                <p className="text-sm text-slate-400">Site Yönetim ve Güvenlik</p>
              </div>
            </div>
            <SystemStatus status={systemStatus} />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-6 py-6 space-y-6">
        {/* Stats Cards */}
        <StatsCards stats={stats} />

        {/* Camera Grid ve Log Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <CameraGrid cameras={cameras} />
          </div>
          <div>
            <LogPanel logs={logs} />
          </div>
        </div>

        {/* Live Ticker */}
        <LiveTicker logs={logs} />
      </div>
    </div>
  );
};

export default Dashboard;