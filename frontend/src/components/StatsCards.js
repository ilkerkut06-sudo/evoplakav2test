import React from 'react';
import { Card } from '@/components/ui/card';
import { Car, Users, AlertTriangle, Activity, Camera } from 'lucide-react';

const StatsCards = ({ stats }) => {
  if (!stats) return null;

  const cards = [
    {
      title: 'Bugünkü Giriş',
      value: stats.bugun_giris,
      icon: Car,
      color: 'from-emerald-500 to-teal-600',
      bgColor: 'bg-emerald-500/10',
    },
    {
      title: 'Bu Ay Toplam',
      value: stats.bu_ay_giris,
      icon: Activity,
      color: 'from-sky-500 to-blue-600',
      bgColor: 'bg-sky-500/10',
    },
    {
      title: 'Bugünkü Misafir',
      value: stats.bugun_misafir,
      icon: Users,
      color: 'from-amber-500 to-orange-600',
      bgColor: 'bg-amber-500/10',
    },
    {
      title: 'Online Kamera',
      value: stats.online_kamera,
      icon: Camera,
      color: 'from-purple-500 to-pink-600',
      bgColor: 'bg-purple-500/10',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <Card
            key={idx}
            className="bg-slate-800/50 border-slate-700 backdrop-blur-sm hover:bg-slate-800/70 transition-all duration-300"
            data-testid={`stat-card-${card.title.toLowerCase().replace(/\s+/g, '-')}`}
          >
            <div className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm text-slate-400 mb-1">{card.title}</p>
                  <p className="text-3xl font-bold text-white">{card.value}</p>
                </div>
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${card.color} flex items-center justify-center`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
};

export default StatsCards;