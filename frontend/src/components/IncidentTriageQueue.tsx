import React, { useState, useEffect } from 'react';
import { Incident } from '../types/safety';
import { incidentApi } from '../services/api';
import { ShieldAlert, CheckCircle, XCircle, AlertTriangle, Clock, History, FileText } from 'lucide-react';

interface IncidentTriageQueueProps {
  onViewEvidence: (incident: Incident) => void;
}

export const IncidentTriageQueue: React.FC<IncidentTriageQueueProps> = ({ onViewEvidence }) => {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [minRiskFilter, setMinRiskFilter] = useState<number>(2);
  const [overrideModalIncident, setOverrideModalIncident] = useState<Incident | null>(null);
  const [overrideReason, setOverrideReason] = useState('');

  const loadIncidents = async () => {
    setLoading(true);
    try {
      const data = await incidentApi.list({
        risk_level: minRiskFilter,
        status_filter: statusFilter || undefined,
      });
      setIncidents(data);
    } catch (err) {
      console.error('Failed to load incidents:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadIncidents();
    const interval = setInterval(loadIncidents, 4000); // Polling triage queue
    return () => clearInterval(interval);
  }, [statusFilter, minRiskFilter]);

  const handleAction = async (incidentId: number, action: string, notes?: string, reason?: string) => {
    try {
      await incidentApi.review(incidentId, action, notes, reason);
      loadIncidents();
      setOverrideModalIncident(null);
      setOverrideReason('');
    } catch (err) {
      console.error('Failed to execute review action:', err);
    }
  };

  const getSeverityBadge = (level: number) => {
    switch (level) {
      case 4:
        return <span className="px-2 py-0.5 text-xs font-bold bg-red-950 text-red-400 border border-red-800 rounded">LVL 4 CRITICAL</span>;
      case 3:
        return <span className="px-2 py-0.5 text-xs font-bold bg-orange-950 text-orange-400 border border-orange-800 rounded">LVL 3 HIGH</span>;
      case 2:
        return <span className="px-2 py-0.5 text-xs font-bold bg-amber-950 text-amber-400 border border-amber-800 rounded">LVL 2 MEDIUM</span>;
      default:
        return <span className="px-2 py-0.5 text-xs font-bold bg-gray-800 text-gray-300 rounded">LVL {level}</span>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING_REVIEW':
        return <span className="px-2 py-0.5 text-[11px] font-semibold bg-amber-500/20 text-amber-300 rounded border border-amber-500/30">Pending Review</span>;
      case 'ACKNOWLEDGED':
        return <span className="px-2 py-0.5 text-[11px] font-semibold bg-sky-500/20 text-sky-300 rounded border border-sky-500/30">Acknowledged</span>;
      case 'CONFIRMED_HAZARD':
        return <span className="px-2 py-0.5 text-[11px] font-semibold bg-red-500/20 text-red-300 rounded border border-red-500/30">Confirmed Hazard</span>;
      case 'FALSE_POSITIVE_OVERRIDE':
        return <span className="px-2 py-0.5 text-[11px] font-semibold bg-purple-500/20 text-purple-300 rounded border border-purple-500/30">Operator Override (FP)</span>;
      case 'RESOLVED':
        return <span className="px-2 py-0.5 text-[11px] font-semibold bg-emerald-500/20 text-emerald-300 rounded border border-emerald-500/30">Resolved</span>;
      default:
        return <span className="px-2 py-0.5 text-[11px] font-semibold bg-gray-700 text-gray-300 rounded">{status}</span>;
    }
  };

  return (
    <div className="p-6 flex flex-col gap-6 max-w-7xl mx-auto">
      {/* Triage Header & Filters */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-[#161b22] p-4 rounded-lg border border-[#30363d]">
        <div>
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-red-400" />
            Human-in-the-Loop Incident Triage Queue
          </h2>
          <p className="text-xs text-gray-400 mt-0.5">
            Every safety-critical alert requires human verification, sign-off, or auditable false-positive rejection.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex items-center gap-3">
          <select
            value={minRiskFilter}
            onChange={(e) => setMinRiskFilter(Number(e.target.value))}
            className="bg-[#0d1117] border border-[#30363d] text-white text-xs font-medium py-1.5 px-3 rounded focus:outline-none"
          >
            <option value={2}>Minimum Severity: Level 2 (Medium+)</option>
            <option value={3}>Minimum Severity: Level 3 (High+)</option>
            <option value={4}>Minimum Severity: Level 4 (Critical Only)</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-[#0d1117] border border-[#30363d] text-white text-xs font-medium py-1.5 px-3 rounded focus:outline-none"
          >
            <option value="">All Review Statuses</option>
            <option value="PENDING_REVIEW">Pending Review</option>
            <option value="ACKNOWLEDGED">Acknowledged</option>
            <option value="CONFIRMED_HAZARD">Confirmed Hazard</option>
            <option value="FALSE_POSITIVE_OVERRIDE">False Positive Override</option>
            <option value="RESOLVED">Resolved</option>
          </select>
        </div>
      </div>

      {/* Incidents Table / Cards */}
      <div className="space-y-3">
        {incidents.length === 0 ? (
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-12 text-center text-gray-400">
            <CheckCircle className="w-10 h-10 text-emerald-500/60 mx-auto mb-3" />
            <h3 className="text-sm font-semibold text-white">Incident Queue Clean</h3>
            <p className="text-xs text-gray-500 mt-1">No unresolved incidents matching the active criteria.</p>
          </div>
        ) : (
          incidents.map((incident) => (
            <div
              key={incident.id}
              className="bg-[#161b22] border border-[#30363d] rounded-lg p-4 flex flex-col md:flex-row gap-4 justify-between items-start md:items-center hover:border-gray-500 transition-colors"
            >
              {/* Left Details */}
              <div className="flex items-start gap-4 flex-1">
                {incident.evidence_snapshot_path && (
                  <button
                    onClick={() => onViewEvidence(incident)}
                    className="w-24 h-16 bg-black rounded border border-[#30363d] overflow-hidden flex-shrink-0 group relative"
                  >
                    <img
                      src={incident.evidence_snapshot_path}
                      alt="Evidence"
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                    />
                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center text-[10px] text-white font-bold transition-opacity">
                      Inspect
                    </div>
                  </button>
                )}

                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    {getSeverityBadge(incident.risk_level)}
                    <span className="font-bold text-white text-xs tracking-wide">
                      {incident.event_type.replace('_', ' ')}
                    </span>
                    {getStatusBadge(incident.status)}
                    <span className="text-[11px] text-gray-400 font-mono">
                      #{incident.id} • Cam {incident.camera_id}
                    </span>
                  </div>

                  {/* Reasoning */}
                  <p className="text-xs text-gray-300 max-w-2xl mt-0.5">
                    {incident.explainability?.reasoning || 'Incident automatically flagged by multi-stage vision pipeline.'}
                  </p>

                  {/* Audit Logs Summary */}
                  {incident.audit_logs && incident.audit_logs.length > 0 && (
                    <div className="flex items-center gap-1.5 text-[11px] text-indigo-400 mt-1">
                      <History className="w-3.5 h-3.5" />
                      <span>
                        Last action: {incident.audit_logs[incident.audit_logs.length - 1].action} by Safety Operator (
                        {new Date(incident.audit_logs[incident.audit_logs.length - 1].timestamp).toLocaleTimeString()})
                      </span>
                    </div>
                  )}
                </div>
              </div>

              {/* Right Action Buttons */}
              <div className="flex items-center gap-2 flex-wrap self-end md:self-center">
                <button
                  onClick={() => onViewEvidence(incident)}
                  className="px-2.5 py-1.5 text-xs bg-[#21262d] hover:bg-[#30363d] text-gray-200 border border-[#30363d] rounded flex items-center gap-1.5 transition-colors"
                >
                  <FileText className="w-3.5 h-3.5" /> Evidence
                </button>

                {incident.status === 'PENDING_REVIEW' && (
                  <>
                    <button
                      onClick={() => handleAction(incident.id, 'ACKNOWLEDGE', 'Operator acknowledged alert')}
                      className="px-2.5 py-1.5 text-xs bg-sky-900/60 hover:bg-sky-800 text-sky-200 border border-sky-700 rounded transition-colors"
                    >
                      Acknowledge
                    </button>
                    <button
                      onClick={() => handleAction(incident.id, 'CONFIRM', 'Confirmed genuine safety breach')}
                      className="px-2.5 py-1.5 text-xs bg-red-900/70 hover:bg-red-800 text-red-200 border border-red-700 rounded transition-colors"
                    >
                      Confirm Hazard
                    </button>
                    <button
                      onClick={() => setOverrideModalIncident(incident)}
                      className="px-2.5 py-1.5 text-xs bg-purple-900/60 hover:bg-purple-800 text-purple-200 border border-purple-700 rounded transition-colors"
                    >
                      Reject (Override FP)
                    </button>
                  </>
                )}

                {['ACKNOWLEDGED', 'CONFIRMED_HAZARD'].includes(incident.status) && (
                  <button
                    onClick={() => handleAction(incident.id, 'RESOLVE', 'Hazard cleared and verified safe')}
                    className="px-2.5 py-1.5 text-xs bg-emerald-900/70 hover:bg-emerald-800 text-emerald-200 border border-emerald-700 rounded flex items-center gap-1 transition-colors"
                  >
                    <CheckCircle className="w-3.5 h-3.5" /> Resolve Incident
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Override False Positive Modal */}
      {overrideModalIncident && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-6 max-w-md w-full flex flex-col gap-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <XCircle className="w-5 h-5 text-purple-400" />
              Reject Incident #{overrideModalIncident.id} (False Positive)
            </h3>
            <p className="text-xs text-gray-400">
              Enterprise safety standard: False positive overrides are auditable and require documented operational justification.
            </p>
            <textarea
              rows={3}
              placeholder="E.g. Authorized maintenance worker with special hot-work permit; reflection caused false trigger..."
              value={overrideReason}
              onChange={(e) => setOverrideReason(e.target.value)}
              className="w-full bg-[#0d1117] border border-[#30363d] text-white p-2.5 text-xs rounded focus:outline-none focus:border-purple-500"
            />
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setOverrideModalIncident(null)}
                className="px-3 py-1.5 text-xs text-gray-400 hover:text-white"
              >
                Cancel
              </button>
              <button
                disabled={!overrideReason.trim()}
                onClick={() =>
                  handleAction(
                    overrideModalIncident.id,
                    'OVERRIDE',
                    'Rejected as False Positive',
                    overrideReason
                  )
                }
                className="px-4 py-1.5 text-xs bg-purple-700 hover:bg-purple-600 disabled:opacity-40 text-white font-medium rounded transition-colors"
              >
                Commit Override to Audit Log
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
