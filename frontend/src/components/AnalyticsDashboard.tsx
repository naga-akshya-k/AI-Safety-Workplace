import React, { useState, useEffect } from 'react';
import { analyticsApi } from '../services/api';
import { BarChart3, ShieldCheck, AlertTriangle, CheckCircle, TrendingUp, AlertCircle } from 'lucide-react';

export const AnalyticsDashboard: React.FC = () => {
  const [summary, setSummary] = useState<any>({
    total_incidents: 0,
    compliance_rate_percent: 94.2,
    severity_breakdown: {
      normal_level_0: 0,
      low_level_1: 0,
      medium_level_2: 0,
      high_level_3: 0,
      critical_level_4: 0,
    },
    event_breakdown: {},
    status_breakdown: {},
  });

  useEffect(() => {
    analyticsApi.getSummary().then(setSummary).catch(console.error);
    const interval = setInterval(() => {
      analyticsApi.getSummary().then(setSummary).catch(console.error);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto flex flex-col gap-6">
      {/* Top Title */}
      <div>
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-emerald-400" />
          Enterprise Safety Intelligence & Compliance Analytics
        </h2>
        <p className="text-xs text-gray-400 mt-0.5">
          Auditable safety performance metrics aggregated from multi-camera inference and human review actions.
        </p>
      </div>

      {/* Top 4 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Compliance Rate */}
        <div className="bg-[#161b22] border border-[#30363d] p-4 rounded-lg flex flex-col justify-between">
          <span className="text-xs text-gray-400 font-medium">PPE & Safety Compliance</span>
          <div className="text-2xl font-bold text-emerald-400 mt-2 font-mono">
            {summary.compliance_rate_percent}%
          </div>
          <span className="text-[11px] text-gray-500 mt-1 flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" /> +1.4% vs last shift
          </span>
        </div>

        {/* Total Incidents */}
        <div className="bg-[#161b22] border border-[#30363d] p-4 rounded-lg flex flex-col justify-between">
          <span className="text-xs text-gray-400 font-medium">Total Logged Incidents</span>
          <div className="text-2xl font-bold text-white mt-2 font-mono">
            {summary.total_incidents}
          </div>
          <span className="text-[11px] text-gray-500 mt-1">Multi-stage verified alerts</span>
        </div>

        {/* Critical Alerts */}
        <div className="bg-[#161b22] border border-[#30363d] p-4 rounded-lg flex flex-col justify-between">
          <span className="text-xs text-gray-400 font-medium">Critical Emergencies (Lvl 4)</span>
          <div className="text-2xl font-bold text-red-400 mt-2 font-mono">
            {summary.severity_breakdown.critical_level_4 || 0}
          </div>
          <span className="text-[11px] text-red-400/80 mt-1">Immediate intervention required</span>
        </div>

        {/* HITL Overrides */}
        <div className="bg-[#161b22] border border-[#30363d] p-4 rounded-lg flex flex-col justify-between">
          <span className="text-xs text-gray-400 font-medium">Operator FP Overrides</span>
          <div className="text-2xl font-bold text-purple-400 mt-2 font-mono">
            {summary.status_breakdown['FALSE_POSITIVE_OVERRIDE'] || 0}
          </div>
          <span className="text-[11px] text-gray-500 mt-1">Model feedback training loop</span>
        </div>
      </div>

      {/* Breakdowns Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Severity Distribution */}
        <div className="bg-[#161b22] border border-[#30363d] p-5 rounded-lg flex flex-col gap-4">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            Incidents by Operational Risk Level
          </h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-red-400 font-medium">Level 4 — Critical Emergency</span>
                <span className="font-mono text-white">{summary.severity_breakdown.critical_level_4 || 0}</span>
              </div>
              <div className="h-2 bg-[#0d1117] rounded-full overflow-hidden">
                <div
                  className="h-full bg-red-600 rounded-full"
                  style={{ width: `${Math.min(100, (summary.severity_breakdown.critical_level_4 || 0) * 10)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-orange-400 font-medium">Level 3 — High Risk (Restricted Entry)</span>
                <span className="font-mono text-white">{summary.severity_breakdown.high_level_3 || 0}</span>
              </div>
              <div className="h-2 bg-[#0d1117] rounded-full overflow-hidden">
                <div
                  className="h-full bg-orange-500 rounded-full"
                  style={{ width: `${Math.min(100, (summary.severity_breakdown.high_level_3 || 0) * 10)}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-amber-400 font-medium">Level 2 — Medium Risk (PPE Advisory)</span>
                <span className="font-mono text-white">{summary.severity_breakdown.medium_level_2 || 0}</span>
              </div>
              <div className="h-2 bg-[#0d1117] rounded-full overflow-hidden">
                <div
                  className="h-full bg-amber-500 rounded-full"
                  style={{ width: `${Math.min(100, (summary.severity_breakdown.medium_level_2 || 0) * 10)}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Hazard Event Breakdown */}
        <div className="bg-[#161b22] border border-[#30363d] p-5 rounded-lg flex flex-col gap-4">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            Hazard Event Classification Breakdown
          </h3>
          <div className="space-y-3">
            {Object.keys(summary.event_breakdown).length > 0 ? (
              Object.entries(summary.event_breakdown).map(([evt, count]: [string, any]) => (
                <div key={evt}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-300 font-medium">{evt.replace('_', ' ')}</span>
                    <span className="font-mono text-white">{count}</span>
                  </div>
                  <div className="h-2 bg-[#0d1117] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-indigo-500 rounded-full"
                      style={{ width: `${Math.min(100, count * 10)}%` }}
                    />
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-gray-500 italic py-6 text-center">
                Telemetry baseline active. Hazard occurrences will register here in real-time.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
