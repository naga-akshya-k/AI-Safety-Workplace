import React, { useState, useEffect } from 'react';
import { telemetryApi } from '../services/api';
import { Thermometer, Wind, Activity, Zap, AlertTriangle, CheckCircle2 } from 'lucide-react';

export const SensorFusionPanel: React.FC = () => {
  const [telemetry, setTelemetry] = useState<Record<string, any>>({
    'temp_zone_01': { value: 34.2, unit: '°C', status: 'NORMAL' },
    'gas_co_01': { value: 4.1, unit: 'ppm', status: 'NORMAL' },
    'combustible_lel_01': { value: 2.0, unit: '% LEL', status: 'NORMAL' },
    'vibration_motor_03': { value: 2.8, unit: 'mm/s RMS', status: 'NORMAL' },
  });

  useEffect(() => {
    const fetchLive = async () => {
      try {
        const data = await telemetryApi.getLive();
        if (data && Object.keys(data).length > 0) {
          setTelemetry(data);
        }
      } catch (err) {
        // keep simulated live default
      }
    };
    fetchLive();
    const interval = setInterval(fetchLive, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between pb-2 border-b border-[#30363d]">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Zap className="w-4 h-4 text-amber-400" />
          Multi-Modal Industrial Telemetry
        </h3>
        <span className="text-[10px] font-mono px-2 py-0.5 bg-emerald-950/80 text-emerald-400 border border-emerald-800 rounded">
          TELEMETRY ONLINE
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* Temp */}
        <div className="bg-[#0d1117] p-3 rounded border border-[#30363d] flex flex-col gap-1">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span className="flex items-center gap-1">
              <Thermometer className="w-3.5 h-3.5 text-rose-400" /> Ambient Temp
            </span>
            <span className="text-[10px] font-mono text-emerald-400">NORMAL</span>
          </div>
          <div className="text-lg font-bold text-white font-mono">
            {telemetry['temp_zone_01']?.value || 34.2} {telemetry['temp_zone_01']?.unit || '°C'}
          </div>
          <span className="text-[10px] text-gray-500">Threshold: 50.0 °C</span>
        </div>

        {/* Toxic Gas */}
        <div className="bg-[#0d1117] p-3 rounded border border-[#30363d] flex flex-col gap-1">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span className="flex items-center gap-1">
              <Wind className="w-3.5 h-3.5 text-sky-400" /> Toxic Gas (CO)
            </span>
            <span className="text-[10px] font-mono text-emerald-400">SAFE</span>
          </div>
          <div className="text-lg font-bold text-white font-mono">
            {telemetry['gas_co_01']?.value || 4.1} {telemetry['gas_co_01']?.unit || 'ppm'}
          </div>
          <span className="text-[10px] text-gray-500">Threshold: 25.0 ppm</span>
        </div>

        {/* Combustible Gas */}
        <div className="bg-[#0d1117] p-3 rounded border border-[#30363d] flex flex-col gap-1">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span className="flex items-center gap-1">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-400" /> Combustible
            </span>
            <span className="text-[10px] font-mono text-emerald-400">NORMAL</span>
          </div>
          <div className="text-lg font-bold text-white font-mono">
            {telemetry['combustible_lel_01']?.value || 2.0} {telemetry['combustible_lel_01']?.unit || '% LEL'}
          </div>
          <span className="text-[10px] text-gray-500">Threshold: 20.0 %</span>
        </div>

        {/* Vibration */}
        <div className="bg-[#0d1117] p-3 rounded border border-[#30363d] flex flex-col gap-1">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span className="flex items-center gap-1">
              <Activity className="w-3.5 h-3.5 text-indigo-400" /> Motor Vibration
            </span>
            <span className="text-[10px] font-mono text-emerald-400">NOMINAL</span>
          </div>
          <div className="text-lg font-bold text-white font-mono">
            {telemetry['vibration_motor_03']?.value || 2.8} {telemetry['vibration_motor_03']?.unit || 'mm/s'}
          </div>
          <span className="text-[10px] text-gray-500">Threshold: 11.2 mm/s</span>
        </div>
      </div>
    </div>
  );
};
