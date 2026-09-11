import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { LiveMonitor } from './components/LiveMonitor';
import { IncidentTriageQueue } from './components/IncidentTriageQueue';
import { ZoneEditorModal } from './components/ZoneEditorModal';
import { EvidenceViewerModal } from './components/EvidenceViewerModal';
import { AnalyticsDashboard } from './components/AnalyticsDashboard';
import { SensorFusionPanel } from './components/SensorFusionPanel';
import { SystemHealthBar } from './components/SystemHealthBar';
import { Camera, Incident } from './types/safety';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'monitor' | 'triage' | 'zones' | 'analytics'>('monitor');
  const [editingCameraForZones, setEditingCameraForZones] = useState<Camera | null>(null);
  const [selectedIncidentForEvidence, setSelectedIncidentForEvidence] = useState<Incident | null>(null);
  const [highestRiskLevel, setHighestRiskLevel] = useState<number>(0);
  const [systemStatus, setSystemStatus] = useState<string>('ONLINE');

  return (
    <div className="min-h-screen bg-[#0b0e14] text-gray-100 flex flex-col justify-between">
      <div>
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          criticalCount={0}
          highestRiskLevel={highestRiskLevel}
          systemStatus={systemStatus}
        />

        <main>
          {activeTab === 'monitor' && (
            <div className="flex flex-col gap-4">
              <LiveMonitor
                onSelectIncidentForReview={(id) => setActiveTab('triage')}
                onOpenZoneEditor={(cam) => setEditingCameraForZones(cam)}
              />
              <div className="px-6 pb-6">
                <SensorFusionPanel />
              </div>
            </div>
          )}

          {activeTab === 'triage' && (
            <IncidentTriageQueue
              onViewEvidence={(incident) => setSelectedIncidentForEvidence(incident)}
            />
          )}

          {activeTab === 'zones' && (
            <div className="p-6 max-w-5xl mx-auto text-center">
              <div className="bg-[#161b22] border border-[#30363d] p-8 rounded-xl flex flex-col items-center gap-4">
                <h3 className="text-base font-bold text-white">Geofence & Safety Zone Studio</h3>
                <p className="text-xs text-gray-400 max-w-lg">
                  Configure exclusion zones, PPE enforcement corridors, and machinery clearance areas. Select a camera feed in the Live Monitor to launch the interactive polygon editor.
                </p>
                <button
                  onClick={() => setActiveTab('monitor')}
                  className="px-4 py-2 bg-[#238636] hover:bg-[#2ea043] text-white text-xs font-semibold rounded-md transition-colors"
                >
                  Go to Live Monitor & Open Editor
                </button>
              </div>
            </div>
          )}

          {activeTab === 'analytics' && <AnalyticsDashboard />}
        </main>
      </div>

      {/* Modals */}
      {editingCameraForZones && (
        <ZoneEditorModal
          camera={editingCameraForZones}
          onClose={() => setEditingCameraForZones(null)}
          onZoneCreated={() => {}}
        />
      )}

      {selectedIncidentForEvidence && (
        <EvidenceViewerModal
          incident={selectedIncidentForEvidence}
          onClose={() => setSelectedIncidentForEvidence(null)}
        />
      )}

      <SystemHealthBar status={systemStatus} />
    </div>
  );
};

export default App;
