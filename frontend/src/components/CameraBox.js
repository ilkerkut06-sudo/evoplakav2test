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

  const wsRef = useRef(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (camera.kamera_tipi === 'WEBCAM') {
      startWebRTC();
    } else {
      // RTSP için backend stream kullan
      setIsOnline(true);
    }
    
    return () => {
      stopWebRTC();
    };
  }, [camera]);

  const startWebRTC = async () => {
    try {
      // WebRTC: Browser'dan webcam aç
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(device => device.kind === 'videoinput');
      
      let constraints = { video: { width: 640, height: 480 } };
      
      if (camera.webcam_index !== undefined && videoDevices[camera.webcam_index]) {
        constraints = {
          video: {
            deviceId: { exact: videoDevices[camera.webcam_index].deviceId },
            width: 640,
            height: 480
          }
        };
      }
      
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
      }
      
      // WebSocket bağlantısı (YOLO/OCR için)
      connectWebSocket();
      
      setIsOnline(true);
    } catch (error) {
      console.error('WebRTC başlatılamadı:', error);
      setIsOnline(false);
    }
  };

  const connectWebSocket = () => {
    const wsUrl = `ws://localhost:8001/api/stream/ws/${camera.id}`;
    wsRef.current = new WebSocket(wsUrl);
    
    wsRef.current.onopen = () => {
      console.log('WebSocket bağlantısı kuruldu');
      // Frame göndermeye başla
      startFrameSending();
    };
    
    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Backend'den gelen plaka tanıma sonuçlarını işle
      if (data.type === 'detection') {
        console.log('Plaka tespit edildi:', data);
      }
    };
    
    wsRef.current.onerror = (error) => {
      console.error('WebSocket hatası:', error);
    };
    
    wsRef.current.onclose = () => {
      console.log('WebSocket bağlantısı kesildi');
      stopFrameSending();
    };
  };

  const startFrameSending = () => {
    // Her 100ms'de bir frame gönder (10 FPS)
    intervalRef.current = setInterval(() => {
      sendFrameToBackend();
    }, 100);
  };

  const stopFrameSending = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const sendFrameToBackend = () => {
    if (!videoRef.current || !canvasRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      return;
    }
    
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    canvas.width = 640;
    canvas.height = 480;
    
    context.drawImage(videoRef.current, 0, 0, 640, 480);
    
    canvas.toBlob((blob) => {
      if (blob && wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        blob.arrayBuffer().then(buffer => {
          wsRef.current.send(buffer);
        });
      }
    }, 'image/jpeg', 0.8);
  };

  const stopWebRTC = () => {
    stopFrameSending();
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
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
          /* WebRTC: Client-side webcam */
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
              data-testid="camera-video-element"
            />
            <canvas ref={canvasRef} style={{ display: 'none' }} />
          </>
        ) : (
          /* RTSP: Backend MJPEG stream */
          <img
            src={`${API}/stream/${camera.id}`}
            alt={camera.kamera_adi}
            className="w-full h-full object-cover"
            data-testid="camera-video-element"
            onError={() => setIsOnline(false)}
            onLoad={() => setIsOnline(true)}
          />
        )}
        
        {!isOnline && (
          <div className="absolute inset-0 flex items-center justify-center text-slate-500">
            <div className="text-center">
              <Camera className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p className="text-sm">Kamera Offline</p>
              <p className="text-xs mt-1 text-slate-600">{camera.kamera_tipi}</p>
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