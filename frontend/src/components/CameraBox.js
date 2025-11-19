import React, { useState, useRef, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { DoorOpen, Camera, Wifi, WifiOff, Video } from 'lucide-react';
import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const CameraBox = ({ camera }) => {
  const [isOnline, setIsOnline] = useState(true);
  const [doorOpening, setDoorOpening] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    // Backend MJPEG stream kullan
    checkCameraStatus();
    return () => {
      // Cleanup
    };
  }, [camera]);

  const checkCameraStatus = async () => {
    try {
      const response = await axios.get(`${API}/cameras/${camera.id}/stream`, { timeout: 3000 });
      setIsOnline(true);
    } catch (error) {
      console.error('Kamera durumu kontrol edilemedi:', error);
      setIsOnline(false);
    }
  };

  const handleOpenDoor = async () => {
    if (!camera.bagli_kapi_id) {
      alert('Bu kameraya bağlı kapı yok');
      return;
    }

    setDoorOpening(true);
    try {
      const response = await axios.post(`${API}/nodemcu/${camera.bagli_kapi_id}/open`);
      if (response.data.success) {
        alert('Kapı açıldı!');
      }
    } catch (error) {
      console.error('Kapı açma hatası:', error);
      alert('Kapı açılamadı');
    } finally {
      setDoorOpening(false);
    }
  };

  const getStatusBadge = () => {
    if (isOnline) {
      return (
        <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
          <Wifi className="w-3 h-3 mr-1" />
          Online
        </Badge>
      );
    }
    return (
      <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
        <WifiOff className="w-3 h-3 mr-1" />
        Offline
      </Badge>
    );
  };

  const getEntryTypeBadge = () => {
    const colors = {
      'Giriş': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      'Çıkış': 'bg-amber-500/20 text-amber-400 border-amber-500/30',
      'Ortak': 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    };

    return (
      <Badge className={colors[camera.giris_cikis] || colors['Ortak']}>
        {camera.giris_cikis}
      </Badge>
    );
  };

  return (
    <Card 
      className="bg-slate-900/70 border-slate-700 overflow-hidden hover:border-slate-600 transition-all"
      data-testid={`camera-box-${camera.id}`}
    >
      {/* Video Area */}
      <div className="relative aspect-video bg-slate-950">
        {camera.kamera_tipi === 'WEBCAM' ? (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
            data-testid="camera-video-element"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-slate-500">
            <div className="text-center">
              <Camera className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">RTSP Stream</p>
              <p className="text-xs mt-1 text-slate-600">WebRTC entegrasyonu gerekiyor</p>
            </div>
          </div>
        )}
        
        {/* Overlay Badges */}
        <div className="absolute top-2 left-2 flex gap-2">
          {getStatusBadge()}
          {getEntryTypeBadge()}
        </div>
      </div>

      {/* Info Footer */}
      <div className="p-3 border-t border-slate-800">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h4 className="font-semibold text-white text-sm" data-testid="camera-name">{camera.kamera_adi}</h4>
            {camera.bagli_kapi_id && (
              <p className="text-xs text-slate-400 mt-0.5">Kapı bağlı</p>
            )}
          </div>
          
          {camera.bagli_kapi_id && (
            <Button
              size="sm"
              onClick={handleOpenDoor}
              disabled={doorOpening || !isOnline}
              className="bg-emerald-600 hover:bg-emerald-700"
              data-testid="open-door-button"
            >
              <DoorOpen className="w-4 h-4 mr-1" />
              Kapıyı Aç
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
};

export default CameraBox;