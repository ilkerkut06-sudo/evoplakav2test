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
    <div className="p-6 space-y-6">
      {/* Header with System Status */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white" style={{ fontFamily: 'Space Grotesk, sans-serif' }}>
            Canlı İzleme
          </h1>
          <p className="text-slate-400 mt-1">Gerçek zamanlı kamera görüntüleri ve geçiş logları</p>
        </div>
        <SystemStatus status={systemStatus} />
      </div>

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
  );
};

export default Dashboard;