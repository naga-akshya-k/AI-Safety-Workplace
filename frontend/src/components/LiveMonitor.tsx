import React, { useState, useEffect, useRef } from 'react';
import { Camera, WebSocketPayload, PipelineOutput, Zone, Incident } from '../types/safety';
import { VideoOverlayCanvas } from './VideoOverlayCanvas';
import { cameraApi } from '../services/api';
import { Camera as CamIcon, Activity, AlertTriangle, Users, Gauge, CheckCircle2 } from 'lucide-react';

interface LiveMonitorProps {
  onSelectIncidentForReview: (incidentId: number) => void;
  onOpenZoneEditor: (camera: Camera) => void;
}

export const LiveMonitor: React.FC<LiveMonitorProps> = ({
  onSelectIncidentForReview,
  onOpenZoneEditor,
}) => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [selectedCameraId, setSelectedCameraId] = useState<number>(1);
  const [frameSrc, setFrameSrc] = useState<string | null>(null);
  const [pipeline, setPipeline] = useState<PipelineOutput | null>(null);
  const [zones, setZones] = useState<Zone[]>([]);
  const [streamHealth, setStreamHealth] = useState<{ status: string; fps: number; frame_count: number }>({
    status: 'CONNECTING...',
    fps: 0,
    frame_count: 0,
  });

  const wsRef = useRef<WebSocket | null>(null);

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
    <div className="grid grid-cols-1 xl:grid-cols-4 gap-6 p-6 h-[calc(100vh-135px)]">
      {/* Main Video Monitor */}
      <div className="xl:col-span-3 flex flex-col gap-4 h-full">
        {/* Stream Top Toolbar */}
        <div className="flex items-center justify-between bg-[#161b22] border border-[#30363d] px-4 py-2.5 rounded-lg">
          <div className="flex items-center gap-3">
            <CamIcon className="w-5 h-5 text-gray-400" />
            <select
              value={selectedCameraId}
              onChange={(e) => setSelectedCameraId(Number(e.target.value))}
              className="bg-[#0d1117] border border-[#30363d] text-white text-xs font-semibold py-1 px-3 rounded focus:outline-none focus:border-green-500"
            >
              {cameras.map((c) => (
                <option key={c.id} value={c.id}>
                  CAM {c.id}: {c.name} ({c.location})
                </option>
              ))}
            </select>
          </div>

          {/* Telemetry Metrics Bar */}
          <div className="flex items-center gap-4 text-xs font-mono">
            <div className="flex items-center gap-1 text-gray-300">
              <Gauge className="w-4 h-4 text-sky-400" />
              <span>FPS:</span>
              <span className="text-white font-bold">{streamHealth.fps}</span>
            </div>
            <div className="flex items-center gap-1 text-gray-300">
              <Activity className="w-4 h-4 text-emerald-400" />
              <span>LATENCY:</span>
              <span className="text-white font-bold">{pipeline?.inference_time_ms || 0} ms</span>
            </div>
            <div className="flex items-center gap-1 text-gray-300">
              <Users className="w-4 h-4 text-indigo-400" />
              <span>TRACKS:</span>
              <span className="text-white font-bold">{pipeline?.tracked_workers?.length || 0}</span>
            </div>

            {activeCamera && (
              <button
                onClick={() => onOpenZoneEditor(activeCamera)}
                className="px-2.5 py-1 text-xs bg-[#21262d] text-gray-300 hover:text-white border border-[#30363d] rounded transition-colors"
              >
                Edit Geofences
              </button>
            )}
          </div>
        </div>

        {/* Video Canvas Container */}
        <div className="flex-1 min-h-0">
          <VideoOverlayCanvas
            frameSrc={frameSrc}
            pipeline={pipeline}
            zones={zones}
            status={streamHealth.status}
          />
        </div>
      </div>

      {/* Right Intelligence & Explainability Sidebar */}
      <div className="xl:col-span-1 flex flex-col gap-4 h-full overflow-hidden">
        {/* Real-time Explainability Card */}
        <div className="bg-[#161b22] border border-[#30363d] p-4 rounded-lg flex flex-col h-full overflow-hidden">
          <div className="flex items-center justify-between pb-3 border-b border-[#30363d]">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              Real-Time Risk Intelligence
            </h2>
            <span className="text-[11px] font-mono px-2 py-0.5 bg-[#21262d] text-gray-400 rounded">
              DETERMINISTIC
            </span>
          </div>

          {/* Active Risk Decisions List */}
          <div className="flex-1 overflow-y-auto space-y-3 py-3 pr-1">
            {pipeline?.risk_assessments && pipeline.risk_assessments.length > 0 ? (
              pipeline.risk_assessments.map((risk, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded border text-xs flex flex-col gap-1.5 transition-all ${
                    risk.risk_level === 4
                      ? 'bg-red-950/40 border-red-800 text-red-200'
                      : risk.risk_level === 3
                      ? 'bg-orange-950/40 border-orange-800 text-orange-200'
                      : 'bg-amber-950/30 border-amber-800 text-amber-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold tracking-wide uppercase font-mono">
                      {risk.event_type.replace('_', ' ')}
                    </span>
                    <span className="px-1.5 py-0.5 text-[10px] font-bold rounded bg-black/40">
                      LVL {risk.risk_level} • {(risk.confidence * 100).toFixed(0)}% CONF
                    </span>
                  </div>

                  {/* Explainable Text */}
                  <p className="text-gray-300 text-[11px] leading-relaxed">
                    {risk.reasoning}
                  </p>

                  {/* Operational Action */}
                  <div className="pt-2 border-t border-white/10 mt-1 flex flex-col gap-1">
                    <span className="text-[10px] uppercase tracking-wider text-gray-400 font-semibold">
                      Required Safety Action:
                    </span>
                    <span className="text-white font-medium text-[11px]">
                      {risk.recommended_action}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 text-gray-500">
                <CheckCircle2 className="w-8 h-8 text-emerald-500/50 mb-2" />
                <p className="text-xs font-medium text-gray-400">All Perimeters Clear</p>
                <p className="text-[11px] text-gray-500 mt-1">
                  Workers compliant with safety gear and clear of hazardous machinery exclusion zones.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
