import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  ShieldAlert, 
  Activity, 
  Eye, 
  Sliders, 
  BarChart3, 
  AlertTriangle, 
  Clock, 
  BookOpen,
  Wifi,
  Sparkles
} from 'lucide-react';

interface NavbarProps {
  activeTab: 'monitor' | 'triage' | 'zones' | 'analytics';
  setActiveTab: (tab: 'monitor' | 'triage' | 'zones' | 'analytics') => void;
  criticalCount: number;
  highestRiskLevel: number;
  systemStatus: string;
  onOpenGuide: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  criticalCount,
  highestRiskLevel,
  systemStatus,
  onOpenGuide,
}) => {
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(now.toLocaleTimeString('en-US', { hour12: false }));
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  const getRiskBadge = () => {
    switch (highestRiskLevel) {
      case 4:
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 text-xs font-black bg-rose-950/90 text-rose-300 border border-rose-600/80 rounded-full animate-pulse shadow-lg shadow-rose-950/50">
            <AlertTriangle className="w-3.5 h-3.5" /> LEVEL 4: CRITICAL EMERGENCY
          </span>
        );
      case 3:
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 text-xs font-black bg-amber-950/90 text-amber-300 border border-amber-600/80 rounded-full shadow-lg shadow-amber-950/50">
            <AlertTriangle className="w-3.5 h-3.5" /> LEVEL 3: HIGH RISK
          </span>
        );
      case 2:
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 text-xs font-bold bg-yellow-950/90 text-yellow-300 border border-yellow-600/80 rounded-full shadow">
            LEVEL 2: MEDIUM RISK
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 text-xs font-bold bg-emerald-950/90 text-emerald-300 border border-emerald-600/80 rounded-full shadow">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping mr-0.5" />
            LEVEL 0: NORMAL OPERATIONS
          </span>
        );
    }
  };

  return (
    <header className="bg-slate-950/90 backdrop-blur-md border-b border-slate-800/80 px-6 py-3.5 sticky top-0 z-50 shadow-md">
      <div className="flex items-center justify-between gap-4">
        
        {/* Title and Industrial Branding */}
        <div className="flex items-center gap-3.5">
          <div className="p-2.5 bg-gradient-to-br from-indigo-500/20 to-blue-500/10 border border-indigo-500/30 rounded-xl shadow-inner text-indigo-400">
            <Shield className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-base font-extrabold text-white tracking-tight">
                SAFEGUARD INDUSTRIAL
              </h1>
              <span className="text-[11px] font-mono px-2 py-0.5 bg-slate-800/90 text-slate-300 border border-slate-700 rounded-md font-semibold">
                v1.0.0 ENTERPRISE
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium tracking-wide">
              Workplace Intelligence, PPE Compliance & Hazard Prevention
            </p>
          </div>
        </div>

        {/* Center Navigation Tabs */}
        <nav className="flex items-center gap-1.5 bg-slate-900/90 p-1.5 border border-slate-800 rounded-xl shadow-inner">
          <button
            onClick={() => setActiveTab('monitor')}
            className={`flex items-center gap-2 px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              activeTab === 'monitor'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-900/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Eye className="w-4 h-4" />
            Live Perimeter Monitor
          </button>
          
          <button
            onClick={() => setActiveTab('triage')}
            className={`flex items-center gap-2 px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all relative ${
              activeTab === 'triage'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-900/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <ShieldAlert className="w-4 h-4" />
            Incident Triage Queue
            {criticalCount > 0 && (
              <span className="px-1.5 py-0.2 text-[10px] font-bold bg-rose-600 text-white rounded-full animate-bounce">
                {criticalCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab('zones')}
            className={`flex items-center gap-2 px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              activeTab === 'zones'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-900/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <Sliders className="w-4 h-4" />
            Zone Geofence Studio
          </button>

          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex items-center gap-2 px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              activeTab === 'analytics'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-900/40'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
            }`}
          >
            <BarChart3 className="w-4 h-4" />
            Safety Compliance KPIs
          </button>
        </nav>

        {/* Right Status Badges & Presentation Guide Button */}
        <div className="flex items-center gap-3">
          
          {/* Live System Time */}
          <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 bg-slate-900 border border-slate-800 rounded-lg text-xs font-mono text-slate-300">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>{timeStr}</span>
          </div>

          {/* Highest Current Risk Status */}
          {getRiskBadge()}

          {/* Presentation Guide Modal Trigger */}
          <button
            onClick={onOpenGuide}
            className="flex items-center gap-2 px-3.5 py-1.5 bg-gradient-to-r from-amber-500/20 to-orange-500/20 hover:from-amber-500/30 hover:to-orange-500/30 text-amber-300 border border-amber-500/50 rounded-lg text-xs font-bold transition-all shadow-md hover:shadow-amber-500/10 cursor-pointer"
            title="Open comprehensive step-by-step presentation script and reviewer defense guide"
          >
            <BookOpen className="w-4 h-4 text-amber-400" />
            <span className="hidden sm:inline">Presentation Guide</span>
          </button>
        </div>

      </div>
    </header>
  );
};
