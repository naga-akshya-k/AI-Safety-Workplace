export interface Camera {
  id: number;
  name: string;
  location: string;
  stream_source: string;
  fps: number;
  width: number;
  height: number;
  is_active: boolean;
  status: 'HEALTHY' | 'DEGRADED' | 'OFFLINE' | 'UNKNOWN';
  current_fps: number;
  last_frame_time?: string;
  created_at: string;
}

export interface Zone {
  id: number;
  camera_id: number;
  name: string;
  zone_type: 'EXCLUSION_ZONE' | 'PPE_MANDATORY' | 'HAZARD_ZONE' | 'MACHINERY_COLLISION';
  polygon_coords: number[][]; // normalized or pixel coordinates
  required_ppe: string[];
  severity_level: number;
  dwell_threshold_seconds: number;
  is_active: boolean;
  created_at: string;
}

export interface TrackedWorker {
  track_id: number;
  bbox: number[]; // [x1, y1, x2, y2]
  label: string;
  confidence: number;
  ground_pt?: number[];
  keypoints?: number[][]; // 17 x 3 [x, y, conf]
}

export interface PPEItem {
  label: string;
  confidence: number;
  bbox: number[];
}

export interface RiskAssessment {
  risk_level: number; // 0..4
  risk_name: 'NORMAL' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  event_type: string;
  confidence: number;
  reasoning: string;
  recommended_action: string;
  details: Record<string, any>;
  timestamp: number;
}

export interface AuditLog {
  id: number;
  user_id?: number;
  action: string;
  previous_status: string;
  new_status: string;
  reason?: string;
  timestamp: string;
}

export interface Incident {
  id: number;
  camera_id: number;
  zone_id?: number;
  event_type: string;
  risk_level: number;
  status: 'PENDING_REVIEW' | 'ACKNOWLEDGED' | 'CONFIRMED_HAZARD' | 'FALSE_POSITIVE_OVERRIDE' | 'RESOLVED';
  confidence: number;
  duration_seconds: number;
  explainability: Record<string, any>;
  recommended_action?: string;
  evidence_snapshot_path?: string;
  assigned_to_user_id?: number;
  operator_notes?: string;
  created_at: string;
  updated_at: string;
  audit_logs?: AuditLog[];
}

export interface SensorReading {
  sensor_id: string;
  sensor_type: string;
  zone_id?: number;
  value: number;
  unit: string;
  status: 'NORMAL' | 'WARNING' | 'CRITICAL';
  timestamp: string;
}

export interface StreamHealth {
  status: string;
  fps: number;
  frame_count: number;
}

export interface PipelineOutput {
  camera_id: number;
  timestamp: number;
  frame_width?: number;
  frame_height?: number;
  max_risk_level: number;
  risk_assessments: RiskAssessment[];
  tracked_workers: TrackedWorker[];
  vehicles: any[];
  ppe_items: PPEItem[];
  zone_violations: any[];
  fall_evaluations: any[];
  proximity_alerts: any[];
  fire_smoke_alerts: any[];
  sensor_anomalies: any[];
  inference_time_ms: number;
  new_incident_ids: number[];
}

export interface WebSocketPayload {
  camera_id: number;
  status: string;
  health: StreamHealth;
  frame: string | null;
  pipeline: PipelineOutput | null;
  zones: Zone[];
  timestamp: number;
}
