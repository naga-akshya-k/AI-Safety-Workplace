import React from 'react';
import { Incident } from '../types/safety';
import { X, ShieldCheck, AlertCircle, FileText, History } from 'lucide-react';

interface EvidenceViewerModalProps {
  incident: Incident | null;
  onClose: () => void;
}

export const EvidenceViewerModal: React.FC<EvidenceViewerModalProps> = ({ incident, onClose }) => {
  if (!incident) return null;

  return (
    <div className="fixed inset-0 bg-black/85 flex items-center justify-center p-6 z-50 overflow-y-auto">
      <div className="bg-[#161b22] border border-[#30363d] rounded-xl max-w-4xl w-full flex flex-col max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#30363d] bg-[#0d1117]">
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-indigo-400" />
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                Incident #{incident.id}: {incident.event_type.replace('_', ' ')}
                <span className="text-xs px-2 py-0.5 rounded font-mono font-bold bg-red-950 text-red-400 border border-red-800">
                  Risk Level {incident.risk_level}
                </span>
              </h2>
              <p className="text-xs text-gray-400">
                Logged at: {new Date(incident.created_at).toLocaleString()} • Camera #{incident.camera_id}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-gray-400 hover:text-white rounded-lg hover:bg-[#21262d] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Left: Snapshot Image */}
          <div className="flex flex-col gap-3">
            <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
              Visual Evidence Snapshot
            </span>
            <div className="bg-black rounded-lg border border-[#30363d] overflow-hidden aspect-video flex items-center justify-center">
              {incident.evidence_snapshot_path ? (
                <img
                  src={incident.evidence_snapshot_path}
                  alt="Incident snapshot"
                  className="w-full h-full object-contain"
                />
              ) : (
                <span className="text-xs text-gray-500">No snapshot recorded</span>
              )}
            </div>
            {incident.recommended_action && (
              <div className="p-3 bg-[#0d1117] border border-[#30363d] rounded-lg">
                <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider block">
                  Recommended Industrial Safety Action:
                </span>
                <p className="text-xs text-emerald-400 mt-1 font-medium">
                  {incident.recommended_action}
                </p>
              </div>
            )}
          </div>

          {/* Right: Explainability & Audit Trail */}
          <div className="flex flex-col gap-4">
            {/* Explainability Block */}
            <div className="flex flex-col gap-2">
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                Multi-Stage Explainability Audit
              </span>
              <div className="bg-[#0d1117] p-3.5 rounded-lg border border-[#30363d] text-xs space-y-2">
                <div>
                  <span className="text-gray-400 font-medium">Reasoning: </span>
                  <span className="text-white">
                    {incident.explainability?.reasoning || 'No details provided'}
                  </span>
                </div>
                <div>
                  <span className="text-gray-400 font-medium">Model Confidence: </span>
                  <span className="text-sky-400 font-mono font-bold">
                    {(incident.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div>
                  <span className="text-gray-400 font-medium">Dwell / Persistence: </span>
                  <span className="text-gray-300 font-mono">
                    {incident.duration_seconds.toFixed(1)} seconds
                  </span>
                </div>
              </div>
            </div>

            {/* Audit History Log */}
            <div className="flex flex-col gap-2">
              <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-1.5">
                <History className="w-3.5 h-3.5 text-indigo-400" />
                Immutable Human Audit Trail
              </span>
              <div className="bg-[#0d1117] p-3 rounded-lg border border-[#30363d] space-y-2 max-h-48 overflow-y-auto">
                {incident.audit_logs && incident.audit_logs.length > 0 ? (
                  incident.audit_logs.map((log) => (
                    <div key={log.id} className="text-xs border-b border-[#21262d] pb-2 last:border-0 last:pb-0">
                      <div className="flex items-center justify-between text-gray-400 font-mono text-[11px]">
                        <span className="text-white font-semibold">{log.action}</span>
                        <span>{new Date(log.timestamp).toLocaleTimeString()}</span>
                      </div>
                      <div className="text-gray-300 text-[11px] mt-0.5">
                        Transition: {log.previous_status} → {log.new_status}
                      </div>
                      {log.reason && (
                        <div className="text-indigo-300 text-[11px] mt-0.5 italic">
                          "{log.reason}"
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <span className="text-xs text-gray-500">No human reviews committed yet.</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
