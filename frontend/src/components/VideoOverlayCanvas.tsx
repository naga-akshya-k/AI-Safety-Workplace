import React, { useRef, useEffect } from 'react';
import { PipelineOutput, Zone } from '../types/safety';

interface VideoOverlayCanvasProps {
  frameSrc: string | null;
  pipeline: PipelineOutput | null;
  zones: Zone[];
  status: string;
}

export const VideoOverlayCanvas: React.FC<VideoOverlayCanvasProps> = ({
  frameSrc,
  pipeline,
  zones,
  status,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const imageRef = useRef<HTMLImageElement | null>(null);

  useEffect(() => {
    if (!frameSrc) return;
    const img = new Image();
    img.src = frameSrc;
    img.onload = () => {
      imageRef.current = img;
      render();
    };
  }, [frameSrc, pipeline, zones]);

  const render = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = imageRef.current;
    if (!img) return;

    // Set canvas dimensions to match image
    canvas.width = img.width;
    canvas.height = img.height;

    // 1. Draw Camera Base Frame
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

    // 2. Draw Zones & Geofences
    if (zones && zones.length > 0) {
      zones.forEach((zone) => {
        if (!zone.polygon_coords || zone.polygon_coords.length < 3) return;

        ctx.beginPath();
        zone.polygon_coords.forEach(([x, y], idx) => {
          if (idx === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.closePath();

        // Style based on zone type
        if (zone.zone_type === 'EXCLUSION_ZONE') {
          ctx.strokeStyle = 'rgba(239, 68, 68, 0.9)'; // Red
          ctx.lineWidth = 3;
          ctx.fillStyle = 'rgba(239, 68, 68, 0.15)';
        } else if (zone.zone_type === 'PPE_MANDATORY') {
          ctx.strokeStyle = 'rgba(234, 179, 8, 0.9)'; // Yellow
          ctx.lineWidth = 2;
          ctx.fillStyle = 'rgba(234, 179, 8, 0.12)';
        } else {
          ctx.strokeStyle = 'rgba(249, 115, 22, 0.9)'; // Orange
          ctx.lineWidth = 2;
          ctx.fillStyle = 'rgba(249, 115, 22, 0.12)';
        }
        ctx.fill();
        ctx.stroke();

        // Zone Label Tag
        const [firstX, firstY] = zone.polygon_coords[0];
        ctx.fillStyle = ctx.strokeStyle;
        ctx.font = 'bold 12px monospace';
        const tagText = `[${zone.zone_type.replace('_', ' ')}] ${zone.name}`;
        const metrics = ctx.measureText(tagText);
        ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
        ctx.fillRect(firstX, firstY - 20, metrics.width + 12, 20);
        ctx.fillStyle = '#ffffff';
        ctx.fillText(tagText, firstX + 6, firstY - 6);
      });
    }

    if (!pipeline) return;

    // 3. Draw Tracked Workers
    if (pipeline.tracked_workers) {
      pipeline.tracked_workers.forEach((worker) => {
        const [x1, y1, x2, y2] = worker.bbox;
        const w = x2 - x1;
        const h = y2 - y1;

        // Check if this worker has active violation
        const isViolator = pipeline.zone_violations?.some((v) => v.track_id === worker.track_id);
        const fallData = pipeline.fall_evaluations?.find((f) => f.track_id === worker.track_id);
        const isFallen = fallData?.is_hazard;

        let boxColor = '#38bdf8'; // Blue normal
        if (isFallen) boxColor = '#ef4444'; // Red fall
        else if (isViolator) boxColor = '#f97316'; // Orange zone breach

        ctx.strokeStyle = boxColor;
        ctx.lineWidth = 2.5;
        ctx.strokeRect(x1, y1, w, h);

        // Ground contact point indicator (feet)
        if (worker.ground_pt) {
          const [gx, gy] = worker.ground_pt;
          ctx.beginPath();
          ctx.arc(gx, gy, 4, 0, 2 * Math.PI);
          ctx.fillStyle = '#10b981';
          ctx.fill();
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }

        // Draw Skeleton Keypoints if available
        if (worker.keypoints && worker.keypoints.length >= 17) {
          ctx.fillStyle = '#22c55e';
          worker.keypoints.forEach(([kx, ky, conf]) => {
            if (conf > 0.3) {
              ctx.beginPath();
              ctx.arc(kx, ky, 3, 0, 2 * Math.PI);
              ctx.fill();
            }
          });
        }

        // Worker ID & Status Tag
        const tag = `Worker #${worker.track_id}${isFallen ? ' [FALL / IMMOBILE!]' : ''}`;
        ctx.font = 'bold 11px monospace';
        const tagWidth = ctx.measureText(tag).width;
        ctx.fillStyle = boxColor;
        ctx.fillRect(x1, y1 - 18, tagWidth + 10, 18);
        ctx.fillStyle = '#0f172a';
        ctx.fillText(tag, x1 + 5, y1 - 5);
      });
    }

    // 4. Draw Vehicles & Machinery
    if (pipeline.vehicles) {
      pipeline.vehicles.forEach((vehicle) => {
        const [x1, y1, x2, y2] = vehicle.bbox;
        ctx.strokeStyle = '#eab308'; // Yellow for machinery
        ctx.lineWidth = 2.5;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

        const vTag = `MACHINERY: ${vehicle.label.toUpperCase()}`;
        ctx.font = 'bold 11px monospace';
        const vWidth = ctx.measureText(vTag).width;
        ctx.fillStyle = '#eab308';
        ctx.fillRect(x1, y1 - 18, vWidth + 8, 18);
        ctx.fillStyle = '#000000';
        ctx.fillText(vTag, x1 + 4, y1 - 5);
      });
    }

    // 5. Draw Proximity Collision Vectors
    if (pipeline.proximity_alerts) {
      pipeline.proximity_alerts.forEach((alert) => {
        const worker = pipeline.tracked_workers.find((w) => w.track_id === alert.worker_id);
        const vehicle = pipeline.vehicles.find((v) => v.track_id === alert.vehicle_id);
        if (worker && vehicle) {
          const wx = (worker.bbox[0] + worker.bbox[2]) / 2;
          const wy = worker.bbox[3];
          const vx = (vehicle.bbox[0] + vehicle.bbox[2]) / 2;
          const vy = vehicle.bbox[3];

          ctx.beginPath();
          ctx.setLineDash([6, 6]);
          ctx.moveTo(wx, wy);
          ctx.lineTo(vx, vy);
          ctx.strokeStyle = alert.severity >= 4 ? '#ef4444' : '#f97316';
          ctx.lineWidth = 3;
          ctx.stroke();
          ctx.setLineDash([]); // Reset dash

          // Draw Distance Tag
          const midX = (wx + vx) / 2;
          const midY = (wy + vy) / 2;
          ctx.fillStyle = '#ef4444';
          ctx.font = 'bold 11px monospace';
          ctx.fillText(`COLLISION PROXIMITY: ${alert.distance_meters}m`, midX, midY - 6);
        }
      });
    }

    // 6. Draw Fire / Smoke Hazard Highlights
    if (pipeline.fire_smoke_alerts && pipeline.fire_smoke_alerts.length > 0) {
      pipeline.fire_smoke_alerts.forEach((fs) => {
        if (fs.bbox) {
          const [x1, y1, x2, y2] = fs.bbox;
          ctx.strokeStyle = '#ef4444';
          ctx.lineWidth = 3;
          ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
          ctx.fillStyle = 'rgba(239, 68, 68, 0.3)';
          ctx.fillRect(x1, y1, x2 - x1, y2 - y1);
          ctx.fillStyle = '#ffffff';
          ctx.font = 'bold 12px monospace';
          ctx.fillText('CRITICAL: FIRE/SMOKE DETECTED', x1, y1 - 8);
        }
      });
    }
  };

  return (
    <div className="relative w-full h-full bg-black flex items-center justify-center overflow-hidden rounded-lg border border-[#30363d]">
      <canvas ref={canvasRef} className="max-w-full max-h-full object-contain" />
      {(!frameSrc || status.includes('UNKNOWN') || status.includes('DEGRADED')) && (
        <div className="absolute inset-0 bg-black/70 flex flex-col items-center justify-center p-6 text-center">
          <div className="w-4 h-4 rounded-full bg-amber-500 animate-ping mb-4" />
          <h3 className="text-amber-400 font-bold text-base tracking-wider font-mono">
            {status || 'UNKNOWN / MONITORING_DEGRADED'}
          </h3>
          <p className="text-gray-400 text-xs mt-2 max-w-md">
            Safety protocol engaged: system never assumes safe operations during camera or inference feed latency.
          </p>
        </div>
      )}
    </div>
  );
};
