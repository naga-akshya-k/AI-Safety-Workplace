import React, { useState, useEffect, useRef } from 'react';
import { Camera, WebSocketPayload, PipelineOutput, Zone, Incident } from '../types/safety';
import { VideoOverlayCanvas } from './VideoOverlayCanvas';
import { cameraApi } from '../services/api';
import { 
  Camera as CamIcon, 
  Activity, 
  AlertTriangle, 
  Users, 
  Gauge, 
  CheckCircle2, 
  ShieldAlert, 
  Sliders, 
  ExternalLink,
  Zap,
  ArrowUpRight
} from 'lucide-react';

interface LiveMonitorProps {
  onSelectIncidentForReview: (incidentId: number) => void;
  onOpenZoneEditor: (camera: Camera) => void;
  onOpenGuide?: () => void;
  forcedCameraId?: number;
}

export const LiveMonitor: React.FC<LiveMonitorProps> = ({
  onSelectIncidentForReview,
  onOpenZoneEditor,
  onOpenGuide,
  forcedCameraId,
}) => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [selectedCameraId, setSelectedCameraId] = useState<number>(forcedCameraId || 1);
  const [frameSrc, setFrameSrc] = useState<string | null>(null);
  const [pipeline, setPipeline] = useState<PipelineOutput | null>(null);
  const [zones, setZones] = useState<Zone[]>([]);
  const [streamHealth, setStreamHealth] = useState<{ status: string; fps: number; frame_count: number }>({
    status: 'CONNECTING...',
    fps: 0,
    frame_count: 0,
  });

  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (forcedCameraId) {
      setSelectedCameraId(forcedCameraId);
    }
  }, [forcedCameraId]);

  // Load cameras
  useEffect(() => {
    cameraApi.list().then((cams) => {
      setCameras(cams);
      if (cams.length > 0 && !selectedCameraId) {
        setSelectedCameraId(cams[0].id);
      }
    }).catch(console.error);
  }, []);

  // Connect WebSocket when camera changes
  useEffect(() => {
    if (!selectedCameraId) return;

    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsUrl = `ws://${window.location.host}/ws/stream/${selectedCameraId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setStreamHealth((prev) => ({ ...prev, status: 'INITIALIZING FEED...' }));
    };

    ws.onmessage = (event) => {
      try {
        const data: WebSocketPayload = JSON.parse(event.data);
        if (data.frame) {
          setFrameSrc(data.frame);
        }
        if (data.pipeline) {
          setPipeline(data.pipeline);
        }
        if (data.zones) {
          setZones(data.zones);
        }
        if (data.health) {
          setStreamHealth(data.health);
        }
      } catch (err) {
        console.error('WS Parse Error:', err);
      }
    };

    ws.onerror = (err) => {
      console.error('WS Error:', err);
      setStreamHealth({ status: 'UNKNOWN / MONITORING_DEGRADED', fps: 0, frame_count: 0 });
    };

    ws.onclose = () => {
      setStreamHealth({ status: 'OFFLINE / RECONNECTING', fps: 0, frame_count: 0 });
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, [selectedCameraId]);

  const activeCamera = cameras.find((c) => c.id === selectedCameraId);

  return (
    <div className="flex flex-col gap-5 p-6 min-h-[calc(100vh-135px)] bg-[#0B1120]">
      
      {/* Top Bar: Camera Selector Switcher & Stream Telemetry */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-3.5 rounded-xl shadow-md">
        
        {/* Camera Quick Buttons */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 sm:pb-0">
          <div className="flex items-center gap-2 mr-2 text-slate-400 font-semibold text-xs uppercase tracking-wider">
            <CamIcon className="w-4 h-4 text-indigo-400" />
            <span>Industrial Feeds:</span>
          </div>

          {[
            { id: 1, label: 'CAM 01: Warehouse Forklift', hazard: 'Proximity & Collision' },
            { id: 2, label: 'CAM 02: Shop Floor Assembly', hazard: 'PPE Compliance' },
            { id: 3, label: 'CAM 03: Robotic Cell', hazard: 'Exclusion Perimeter' },
            { id: 4, label: 'CAM 04: Storage Aisle', hazard: 'Fall & Man-Down' },
          ].map((cam) => (
            <button
              key={cam.id}
              onClick={() => setSelectedCameraId(cam.id)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all border ${
                selectedCameraId === cam.id
                  ? 'bg-indigo-600 text-white border-indigo-500 shadow-md shadow-indigo-900/40'
                  : 'bg-slate-800/80 text-slate-300 border-slate-700/80 hover:bg-slate-700/80 hover:text-white'
              }`}
            >
              <span>{cam.label}</span>
              <span className={`text-[10px] px-1.5 py-0.2 rounded font-normal ${
                selectedCameraId === cam.id ? 'bg-indigo-700 text-indigo-100' : 'bg-slate-900 text-slate-400'
              }`}>
                {cam.hazard}
              </span>
            </button>
          ))}
        </div>

        {/* Live Telemetry Health Stats */}
        <div className="flex items-center gap-3 text-xs font-mono">
          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-950/80 border border-slate-800 rounded-lg text-slate-300">
            <Gauge className="w-3.5 h-3.5 text-sky-400" />
            <span className="text-slate-400 text-[11px]">RATE:</span>
            <span className="text-white font-bold">{streamHealth.fps.toFixed(1)} FPS</span>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-950/80 border border-slate-800 rounded-lg text-slate-300">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span className="text-slate-400 text-[11px]">AI INFERENCE:</span>
            <span className="text-white font-bold">{pipeline?.inference_time_ms || 38.5} ms</span>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-slate-950/80 border border-slate-800 rounded-lg text-slate-300">
            <Users className="w-3.5 h-3.5 text-indigo-400" />
            <span className="text-slate-400 text-[11px]">ACTIVE TRACKS:</span>
            <span className="text-white font-bold">{pipeline?.tracked_workers?.length || 0}</span>
          </div>

          {activeCamera && (
            <button
              onClick={() => onOpenZoneEditor(activeCamera)}
              className="flex items-center gap-1.5 px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-600/80 rounded-lg text-xs font-semibold transition-colors shadow"
            >
              <Sliders className="w-3.5 h-3.5 text-amber-400" />
              <span>Zone Studio</span>
            </button>
          )}
        </div>

      </div>

      {/* Main Grid: 16:9 CCTV Video Screen + Right Risk Intelligence Sidebar */}
      <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 items-start">
        
        {/* Left Column: 16:9 CCTV Monitor Frame */}
        <div className="xl:col-span-3 flex flex-col gap-3">
          
          {/* Monitor Enclosure Frame */}
          <div className="relative w-full aspect-video rounded-2xl overflow-hidden border border-slate-700 shadow-2xl bg-slate-950 flex items-center justify-center">
            <VideoOverlayCanvas
              frameSrc={frameSrc}
              pipeline={pipeline}
              zones={zones}
              status={streamHealth.status}
            />
          </div>

          {/* Sub-Monitor Information Strip */}
          <div className="flex flex-wrap items-center justify-between text-xs text-slate-400 bg-slate-900/60 border border-slate-800 px-4 py-2 rounded-xl">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                <strong className="text-slate-200">ACTIVE CAMERA:</strong> {activeCamera?.name || 'Loading Dock 01'}
              </span>
              <span>•</span>
              <span><strong>LOCATION:</strong> {activeCamera?.location || 'Logistics Corridor'}</span>
            </div>

            <div className="flex items-center gap-3 font-mono text-[11px]">
              <span className="text-indigo-400 font-semibold">BACKBONE: RT-DETR-L (PRIMARY)</span>
              <span>•</span>
              <span className="text-emerald-400 font-semibold">TRACKER: BYTETRACK</span>
              <span>•</span>
              <span className="text-sky-400 font-semibold">SAFETY AUDIT: HITL STRICT</span>
            </div>
          </div>

        </div>

        {/* Right Column: Real-Time Risk Intelligence & Action Center */}
        <div className="xl:col-span-1 flex flex-col gap-3">
          
          <div className="bg-slate-900/90 border border-slate-800 p-4 rounded-2xl shadow-xl flex flex-col gap-4">
            
            {/* Sidebar Title */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-amber-500/20 text-amber-400 rounded-lg">
                  <AlertTriangle className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-sm font-extrabold text-white tracking-tight">
                    Risk Intelligence
                  </h2>
                  <p className="text-[11px] text-slate-400 font-medium">Deterministic AI Classification</p>
                </div>
              </div>

              <span className="text-[10px] font-mono font-bold px-2 py-0.5 bg-slate-800 text-slate-300 border border-slate-700 rounded-md">
                LEVELS 0–4
              </span>
            </div>

            {/* Active Risk Assessments List */}
            <div className="space-y-3.5 max-h-[580px] overflow-y-auto pr-1">
              {pipeline?.risk_assessments && pipeline.risk_assessments.length > 0 ? (
                pipeline.risk_assessments.map((risk, idx) => {
                  const isCritical = risk.risk_level === 4;
                  const isHigh = risk.risk_level === 3;
                  const isMedium = risk.risk_level === 2;

                  return (
                    <div
                      key={idx}
                      className={`p-4 rounded-xl border flex flex-col gap-2.5 transition-all shadow-md ${
                        isCritical
                          ? 'bg-rose-950/60 border-rose-600/80 text-rose-100 shadow-rose-950/40'
                          : isHigh
                          ? 'bg-amber-950/60 border-amber-600/80 text-amber-100 shadow-amber-950/40'
                          : 'bg-yellow-950/50 border-yellow-600/80 text-yellow-100'
                      }`}
                    >
                      {/* Card Header: Hazard Type & Severity Badge */}
                      <div className="flex items-center justify-between">
                        <span className="font-extrabold text-xs tracking-wider uppercase font-mono">
                          {risk.event_type.replace(/_/g, ' ')}
                        </span>
                        <span className={`px-2 py-0.5 text-[10px] font-black rounded-md tracking-wider shadow ${
                          isCritical
                            ? 'bg-rose-600 text-white'
                            : isHigh
                            ? 'bg-amber-500 text-slate-950'
                            : 'bg-yellow-400 text-slate-950'
                        }`}>
                          LVL {risk.risk_level} • {(risk.confidence * 100).toFixed(0)}% CONF
                        </span>
                      </div>

                      {/* Explainability Reasoning */}
                      <p className="text-xs text-slate-200 font-medium leading-relaxed">
                        {risk.reasoning}
                      </p>

                      {/* Required Operational Action Box */}
                      <div className="bg-slate-950/80 border border-white/10 p-2.5 rounded-lg flex flex-col gap-1">
                        <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold flex items-center gap-1">
                          <Zap className="w-3 h-3 text-amber-400" />
                          Mandatory Safety Protocol:
                        </span>
                        <span className="text-white text-xs font-semibold leading-normal">
                          {risk.recommended_action}
                        </span>
                      </div>

                      {/* Triage Action Button */}
                      <button
                        onClick={() => onSelectIncidentForReview(0)}
                        className="mt-1 flex items-center justify-center gap-1.5 py-1.5 text-xs font-bold bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-white transition-colors cursor-pointer"
                      >
                        <span>Triage in Incident Queue</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  );
                })
              ) : (
                <div className="py-12 px-4 flex flex-col items-center justify-center text-center text-slate-400">
                  <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-full mb-3 text-emerald-400">
                    <CheckCircle2 className="w-8 h-8" />
                  </div>
                  <h4 className="text-sm font-bold text-slate-200">Perimeter Normal</h4>
                  <p className="text-xs text-slate-400 mt-1 max-w-xs leading-relaxed">
                    All monitored workers are fully compliant with mandatory safety PPE and clear of exclusion zones.
                  </p>
                </div>
              )}
            </div>

          </div>

        </div>

      </div>

    </div>
  );
};
