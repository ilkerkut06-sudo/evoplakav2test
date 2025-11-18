import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import CameraBox from './CameraBox';
import { Grid3x3, Grid2x2, Maximize2 } from 'lucide-react';

const CameraGrid = ({ cameras }) => {
  const [gridLayout, setGridLayout] = useState('2x2'); // '1x1', '2x2', '3x3'

  const getGridClass = () => {
    switch (gridLayout) {
      case '1x1':
        return 'grid-cols-1';
      case '2x2':
        return 'grid-cols-1 md:grid-cols-2';
      case '3x3':
        return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3';
      default:
        return 'grid-cols-1 md:grid-cols-2';
    }
  };

  return (
    <Card className="bg-slate-800/50 border-slate-700 backdrop-blur-sm" data-testid="camera-grid-container">
      <div className="p-4 border-b border-slate-700">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">Canlı Kameralar</h3>
          <div className="flex gap-2">
            <Button
              variant={gridLayout === '1x1' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setGridLayout('1x1')}
              className="h-8 w-8 p-0"
              data-testid="grid-layout-1x1"
            >
              <Maximize2 className="w-4 h-4" />
            </Button>
            <Button
              variant={gridLayout === '2x2' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setGridLayout('2x2')}
              className="h-8 w-8 p-0"
              data-testid="grid-layout-2x2"
            >
              <Grid2x2 className="w-4 h-4" />
            </Button>
            <Button
              variant={gridLayout === '3x3' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setGridLayout('3x3')}
              className="h-8 w-8 p-0"
              data-testid="grid-layout-3x3"
            >
              <Grid3x3 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
      
      <div className="p-4">
        {cameras.length === 0 ? (
          <div className="text-center py-12 text-slate-400" data-testid="no-cameras-message">
            <p>Henüz kamera eklenmemiş</p>
            <p className="text-sm mt-2">Kamera Yönetimi bölümünden kamera ekleyebilirsiniz</p>
          </div>
        ) : (
          <div className={`grid ${getGridClass()} gap-4`}>
            {cameras.map((camera) => (
              <CameraBox key={camera.id} camera={camera} />
            ))}
          </div>
        )}
      </div>
    </Card>
  );
};

export default CameraGrid;