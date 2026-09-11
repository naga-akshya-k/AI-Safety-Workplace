import axios from 'axios';
import { Camera, Zone, Incident } from '../types/safety';

const API_BASE_URL = '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach token if present
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const cameraApi = {
  list: async (): Promise<Camera[]> => {
    const res = await apiClient.get('/cameras');
    return res.data;
  },
  get: async (id: number): Promise<Camera> => {
    const res = await apiClient.get(`/cameras/${id}`);
    return res.data;
  },
  create: async (data: Partial<Camera>): Promise<Camera> => {
    const res = await apiClient.post('/cameras', data);
    return res.data;
  },
};

export const zoneApi = {
  listForCamera: async (cameraId: number): Promise<Zone[]> => {
    const res = await apiClient.get(`/zones/camera/${cameraId}`);
    return res.data;
  },
  create: async (data: Partial<Zone>): Promise<Zone> => {
    const res = await apiClient.post('/zones', data);
    return res.data;
  },
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/zones/${id}`);
  },
};

export const incidentApi = {
  list: async (params?: { camera_id?: number; risk_level?: number; status_filter?: string }): Promise<Incident[]> => {
    const res = await apiClient.get('/incidents', { params });
    return res.data;
  },
  get: async (id: number): Promise<Incident> => {
    const res = await apiClient.get(`/incidents/${id}`);
    return res.data;
  },
  review: async (id: number, action: string, notes?: string, override_reason?: string): Promise<Incident> => {
    const res = await apiClient.post(`/incidents/${id}/review`, {
      action,
      notes,
      override_reason,
    });
    return res.data;
  },
};

export const analyticsApi = {
  getSummary: async () => {
    const res = await apiClient.get('/analytics/summary');
    return res.data;
  },
};

export const telemetryApi = {
  getLive: async () => {
    const res = await apiClient.get('/telemetry/live');
    return res.data;
  },
};
