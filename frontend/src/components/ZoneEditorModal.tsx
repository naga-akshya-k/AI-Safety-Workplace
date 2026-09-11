import React, { useState, useRef, useEffect } from 'react';
import { Camera, Zone } from '../types/safety';
import { zoneApi } from '../services/api';
import { X, Plus, Trash2, CheckCircle, Sliders } from 'lucide-react';

interface ZoneEditorModalProps {
  camera: Camera;
  onClose: () => void;
  onZoneCreated: () => void;
}

export const ZoneEditorModal: React.FC<ZoneEditorModalProps> = ({ camera, onClose, onZoneCreated }) => {
  const [existingZones, setExistingZones] = useState<Zone[]>([]);
  const [points, setPoints] = useState<number[][]>([]);
  const [zoneName, setZoneName] = useState('');
  const [zoneType, setZoneType] = useState<'EXCLUSION_ZONE' | 'PPE_MANDATORY' | 'HAZARD_ZONE'>('EXCLUSION_ZONE');
  const [severityLevel, setSeverityLevel] = useState<number>(4);
  const [dwellThreshold, setDwellThreshold] = useState<number>(3);
  const [requiredPPE, setRequiredPPE] = useState<string[]>(['hardhat', 'vest']);
  const [saving, setSaving] = useState(false);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const loadZones = async () => {
    try {
      const data = await zoneApi.listForCamera(camera.id);
      setExistingZones(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadZones();
  }, [camera.id]);

  // Redraw canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw background grid
    ctx.fillStyle = '#111827';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.strokeStyle = '#1f2937';
    ctx.lineWidth = 1;
    for (let x = 0; x < canvas.width; x += 40) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y < canvas.height; y += 40) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(canvas.width, y);
      ctx.stroke();
    }

    // Draw existing zones
    existingZones.forEach((z) => {
      if (!z.polygon_coords || z.polygon_coords.length < 3) return;
      ctx.beginPath();
      z.polygon_coords.forEach(([px, py], i) => {
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.closePath();
      ctx.strokeStyle = z.zone_type === 'EXCLUSION_ZONE' ? 'rgba(239, 68, 68, 0.6)' : 'rgba(234, 179, 8, 0.6)';
      ctx.lineWidth = 2;
      ctx.fillStyle = z.zone_type === 'EXCLUSION_ZONE' ? 'rgba(239, 68, 68, 0.1)' : 'rgba(234, 179, 8, 0.1)';
      ctx.fill();
      ctx.stroke();
    });

    // Draw currently drafting points
    if (points.length > 0) {
      ctx.beginPath();
      points.forEach(([px, py], i) => {
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      if (points.length >= 3) {
        ctx.closePath();
        ctx.fillStyle = 'rgba(56, 189, 248, 0.15)';
        ctx.fill();
      }
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2.5;
      ctx.stroke();

      // Vertices
      points.forEach(([px, py]) => {
        ctx.beginPath();
        ctx.arc(px, py, 5, 0, 2 * Math.PI);
        ctx.fillStyle = '#38bdf8';
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();
      });
    }
  }, [points, existingZones]);

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = Math.round((e.clientX - rect.left) * scaleX);
    const y = Math.round((e.clientY - rect.top) * scaleY);

    setPoints((prev) => [...prev, [x, y]]);
  };

  const handleSave = async () => {
    if (points.length < 3 || !zoneName.trim()) return;
    setSaving(true);
    try {
      await zoneApi.create({
        camera_id: camera.id,
        name: zoneName,
        zone_type: zoneType,
        polygon_coords: points,
        required_ppe: requiredPPE,
        severity_level: severityLevel,
        dwell_threshold_seconds: dwellThreshold,
      });
      setPoints([]);
      setZoneName('');
      await loadZones();
      onZoneCreated();
    } catch (err) {
      console.error('Failed to create zone:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (zoneId: number) => {
    try {
      await zoneApi.delete(zoneId);
      loadZones();
      onZoneCreated();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/85 flex items-center justify-center p-6 z-50 overflow-y-auto">
      <div className="bg-[#161b22] border border-[#30363d] rounded-xl max-w-5xl w-full flex flex-col max-h-[92vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[#30363d] bg-[#0d1117]">
          <div className="flex items-center gap-3">
            <Sliders className="w-5 h-5 text-emerald-400" />
            <div>
              <h2 className="text-base font-bold text-white">
                Zone Geofence Studio — Cam #{camera.id}: {camera.name}
              </h2>
              <p className="text-xs text-gray-400">
                Click on the canvas to place boundary vertices (minimum 3 points required to create a polygon).
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 text-gray-400 hover:text-white rounded-lg">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Studio Content */}
        <div className="p-6 overflow-y-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Canvas Area */}
          <div className="lg:col-span-2 flex flex-col gap-2">
            <div className="relative border border-[#30363d] rounded-lg overflow-hidden bg-black aspect-video">
              <canvas
                ref={canvasRef}
                width={854}
                height={480}
                onClick={handleCanvasClick}
                className="w-full h-full cursor-crosshair object-contain"
              />
            </div>
            <div className="flex items-center justify-between text-xs text-gray-400 font-mono">
              <span>Points Placed: {points.length}</span>
              <button
                onClick={() => setPoints([])}
                className="text-red-400 hover:underline"
              >
                Clear Vertices
              </button>
            </div>
          </div>

          {/* Form & Existing Zones */}
          <div className="flex flex-col gap-4">
            <div className="bg-[#0d1117] border border-[#30363d] p-4 rounded-lg flex flex-col gap-3">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                Create New Geofence
              </h3>

              <div>
                <label className="text-[11px] text-gray-400 block mb-1">Zone Name</label>
                <input
                  type="text"
                  placeholder="e.g. Robot Cell A Perimeter"
                  value={zoneName}
                  onChange={(e) => setZoneName(e.target.value)}
                  className="w-full bg-[#161b22] border border-[#30363d] text-white p-2 text-xs rounded focus:outline-none focus:border-green-500"
                />
              </div>

              <div>
                <label className="text-[11px] text-gray-400 block mb-1">Zone Type</label>
                <select
                  value={zoneType}
                  onChange={(e: any) => setZoneType(e.target.value)}
                  className="w-full bg-[#161b22] border border-[#30363d] text-white p-2 text-xs rounded focus:outline-none focus:border-green-500"
                >
                  <option value="EXCLUSION_ZONE">Exclusion Zone (Zero Tolerance)</option>
                  <option value="PPE_MANDATORY">PPE Mandatory Zone</option>
                  <option value="HAZARD_ZONE">Machinery Hazard Corridor</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="text-[11px] text-gray-400 block mb-1">Severity Level</label>
                  <select
                    value={severityLevel}
                    onChange={(e) => setSeverityLevel(Number(e.target.value))}
                    className="w-full bg-[#161b22] border border-[#30363d] text-white p-2 text-xs rounded"
                  >
                    <option value={2}>Level 2 (Medium)</option>
                    <option value={3}>Level 3 (High)</option>
                    <option value={4}>Level 4 (Critical)</option>
                  </select>
                </div>
                <div>
                  <label className="text-[11px] text-gray-400 block mb-1">Dwell Alarm (s)</label>
                  <input
                    type="number"
                    min={1}
                    max={30}
                    value={dwellThreshold}
                    onChange={(e) => setDwellThreshold(Number(e.target.value))}
                    className="w-full bg-[#161b22] border border-[#30363d] text-white p-2 text-xs rounded"
                  />
                </div>
              </div>

              <button
                disabled={points.length < 3 || !zoneName.trim() || saving}
                onClick={handleSave}
                className="mt-2 w-full py-2 bg-[#238636] hover:bg-[#2ea043] disabled:opacity-40 text-white text-xs font-semibold rounded flex items-center justify-center gap-1.5 transition-colors"
              >
                <CheckCircle className="w-4 h-4" /> Save Zone Geofence
              </button>
            </div>

            {/* Existing Active Zones List */}
            <div className="flex-1 overflow-y-auto">
              <span className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider block mb-2">
                Active Camera Geofences ({existingZones.length})
              </span>
              <div className="space-y-2">
                {existingZones.map((z) => (
                  <div
                    key={z.id}
                    className="bg-[#0d1117] border border-[#30363d] p-2.5 rounded flex items-center justify-between text-xs"
                  >
                    <div>
                      <span className="font-semibold text-white block">{z.name}</span>
                      <span className="text-[11px] text-gray-400 font-mono">
                        {z.zone_type} • Dwell {z.dwell_threshold_seconds}s
                      </span>
                    </div>
                    <button
                      onClick={() => handleDelete(z.id)}
                      className="p-1.5 text-gray-400 hover:text-red-400 rounded hover:bg-[#21262d]"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
