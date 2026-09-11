import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { LiveMonitor } from './components/LiveMonitor';
import { IncidentTriageQueue } from './components/IncidentTriageQueue';
import { ZoneEditorModal } from './components/ZoneEditorModal';
import { EvidenceViewerModal } from './components/EvidenceViewerModal';
import { AnalyticsDashboard } from './components/AnalyticsDashboard';
import { SensorFusionPanel } from './components/SensorFusionPanel';
import { SystemHealthBar } from './components/SystemHealthBar';
import { PresentationGuideModal } from './components/PresentationGuideModal';
import { Camera, Incident } from './types/safety';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'monitor' | 'triage' | 'zones' | 'analytics'>('monitor');
  const [editingCameraForZones, setEditingCameraForZones] = useState<Camera | null>(null);
  const [selectedIncidentForEvidence, setSelectedIncidentForEvidence] = useState<Incident | null>(null);
  const [highestRiskLevel, setHighestRiskLevel] = useState<number>(0);
  const [systemStatus, setSystemStatus] = useState<string>('ONLINE');
  const [isGuideOpen, setIsGuideOpen] = useState<boolean>(false);
  const [focusedCameraId, setFocusedCameraId] = useState<number>(1);

  const handleSelectCameraFromGuide = (camId: number) => {
    setFocusedCameraId(camId);
    setActiveTab('monitor');
  };

  return (
    <div className="min-h-screen bg-[#0B1120] text-slate-100 flex flex-col justify-between selection:bg-indigo-500 selection:text-white">
      <div>
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          criticalCount={0}
          highestRiskLevel={highestRiskLevel}
          systemStatus={systemStatus}
          onOpenGuide={() => setIsGuideOpen(true)}
        />

        <main>
          {activeTab === 'monitor' && (
            <div className="flex flex-col gap-4">
              <LiveMonitor
                forcedCameraId={focusedCameraId}
                onSelectIncidentForReview={(id) => setActiveTab('triage')}
                onOpenZoneEditor={(cam) => setEditingCameraForZones(cam)}
                onOpenGuide={() => setIsGuideOpen(true)}
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
              <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl flex flex-col items-center gap-4 shadow-xl">
                <h3 className="text-base font-bold text-white">Geofence & Safety Zone Studio</h3>
                <p className="text-xs text-slate-400 max-w-lg leading-relaxed">
                  Configure exclusion zones, PPE enforcement corridors, and machinery clearance areas. Select a camera feed in the Live Monitor to launch the interactive polygon editor.
                </p>
                <button
                  onClick={() => setActiveTab('monitor')}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-lg transition-colors shadow-md shadow-indigo-900/40"
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

      <PresentationGuideModal
        isOpen={isGuideOpen}
        onClose={() => setIsGuideOpen(false)}
        onSelectCamera={handleSelectCameraFromGuide}
      />

      <SystemHealthBar status={systemStatus} />
    </div>
  );
};

export default App;
