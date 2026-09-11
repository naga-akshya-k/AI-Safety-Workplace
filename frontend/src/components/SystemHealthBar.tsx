import React from 'react';
import { Cpu, HardDrive, ShieldCheck, Wifi } from 'lucide-react';

interface SystemHealthBarProps {
  status: string;
}

export const SystemHealthBar: React.FC<SystemHealthBarProps> = ({ status }) => {
  return (
    <footer className="bg-[#0d1117] border-t border-[#30363d] px-6 py-2 text-xs flex items-center justify-between font-mono text-gray-400">
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <Cpu className="w-3.5 h-3.5 text-emerald-400" />
          <span>INFERENCE ENGINE:</span>
          <span className="text-white font-semibold">NVIDIA RTX 3050 / FP16 CUDA</span>
        </div>
        <div className="flex items-center gap-2">
          <HardDrive className="w-3.5 h-3.5 text-sky-400" />
          <span>RELATIONAL DB:</span>
          <span className="text-white font-semibold">SQLITE (AUDITABLE)</span>
        </div>
        <div className="flex items-center gap-2">
          <Wifi className="w-3.5 h-3.5 text-indigo-400" />
          <span>STREAM PIPELINE:</span>
          <span className="text-white font-semibold">BYTETRACK MOT @ 15-20 FPS</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
        <span className="text-gray-400">FAIL-SAFE STATUS:</span>
        <span className="text-emerald-400 font-bold uppercase">{status || 'ACTIVE'}</span>
      </div>
    </footer>
  );
};
