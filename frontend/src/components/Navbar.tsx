import React from 'react';
import { Shield, ShieldAlert, Activity, Eye, Sliders, BarChart3, AlertTriangle } from 'lucide-react';

interface NavbarProps {
  activeTab: 'monitor' | 'triage' | 'zones' | 'analytics';
  setActiveTab: (tab: 'monitor' | 'triage' | 'zones' | 'analytics') => void;
  criticalCount: number;
  highestRiskLevel: number;
  systemStatus: string;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  criticalCount,
  highestRiskLevel,
  systemStatus,
}) => {
  const getRiskBadge = () => {
    switch (highestRiskLevel) {
      case 4:
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 text-xs font-bold bg-red-950/80 text-red-400 border border-red-800 rounded animate-pulse">
            <AlertTriangle className="w-3.5 h-3.5" /> LEVEL 4: CRITICAL EMERGENCY
          </span>
        );
      case 3:
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 text-xs font-bold bg-orange-950/80 text-orange-400 border border-orange-800 rounded">
            <AlertTriangle className="w-3.5 h-3.5" /> LEVEL 3: HIGH RISK
          </span>
        );
      case 2:
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 text-xs font-bold bg-amber-950/80 text-amber-400 border border-amber-800 rounded">
            LEVEL 2: MEDIUM RISK
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold bg-emerald-950/80 text-emerald-400 border border-emerald-800 rounded">
            LEVEL 0: NORMAL OPERATIONS
          </span>
        );
    }
  };

  return (
    <header className="bg-[#161b22] border-b border-[#30363d] px-6 py-3 sticky top-0 z-50">
      <div className="flex items-center justify-between">
        {/* Title and Logo */}
        <div className="flex items-center gap-3">
          <div className="p-2 bg-red-500/10 border border-red-500/30 rounded-lg">
            <Shield className="w-6 h-6 text-red-400" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              SAFEGUARD INDUSTRIAL
              <span className="text-xs font-mono px-2 py-0.5 bg-[#21262d] text-gray-400 border border-[#30363d] rounded">
                v1.0.0 ENTERPRISE
              </span>
            </h1>
            <p className="text-xs text-gray-400 font-medium">Workplace Intelligence & Hazard Prevention</p>
          </div>
        </div>

        {/* Center Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-[#0d1117] p-1 border border-[#30363d] rounded-lg">
          <button
            onClick={() => setActiveTab('monitor')}
            className={`flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              activeTab === 'monitor'
                ? 'bg-[#238636] text-white shadow-sm'
                : 'text-gray-400 hover:text-white hover:bg-[#21262d]'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            Live Perimeter Monitor
          </button>
          <button
            onClick={() => setActiveTab('triage')}
            className={`flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-md transition-colors relative ${
              activeTab === 'triage'
                ? 'bg-[#238636] text-white shadow-sm'
                : 'text-gray-400 hover:text-white hover:bg-[#21262d]'
            }`}
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            Incident Triage Queue
            {criticalCount > 0 && (
              <span className="px-1.5 py-0.2 text-[10px] font-bold bg-red-600 text-white rounded-full">
                {criticalCount}
              </span>
            )}
          </button>
          <button
            onClick={() => setActiveTab('zones')}
            className={`flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              activeTab === 'zones'
                ? 'bg-[#238636] text-white shadow-sm'
                : 'text-gray-400 hover:text-white hover:bg-[#21262d]'
            }`}
          >
            <Sliders className="w-3.5 h-3.5" />
            Zone Geofence Studio
          </button>
          <button
            onClick={() => setActiveTab('analytics')}
            className={`flex items-center gap-2 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              activeTab === 'analytics'
                ? 'bg-[#238636] text-white shadow-sm'
                : 'text-gray-400 hover:text-white hover:bg-[#21262d]'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            Safety Compliance KPIs
          </button>
        </nav>

        {/* Right Status & Badges */}
        <div className="flex items-center gap-3">
          {getRiskBadge()}
          <div className="flex items-center gap-2 pl-3 border-l border-[#30363d] text-xs">
            <span
              className={`w-2 h-2 rounded-full ${
                systemStatus.includes('UNKNOWN') || systemStatus.includes('DEGRADED')
                  ? 'bg-amber-400 animate-ping'
                  : 'bg-emerald-400'
              }`}
            />
            <span className="text-gray-300 font-mono text-[11px]">{systemStatus}</span>
          </div>
        </div>
      </div>
    </header>
  );
};
