export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface VehicleDetectionResult {
  className: string;
  confidence: number;
  boundingBox: BoundingBox;
}

export interface DetectionResponse {
  totalVehicles: number;
  detections: VehicleDetectionResult[];
  processedImage: string;
  processingTime: number;
}

export interface UploadedFileRecord {
  id: string;
  fileName: string;
  format: string;
  size: string;
  status: 'Pending' | 'Processed' | 'Failed';
}

export interface ReportRow {
  date: string;
  fileName: string;
  type: 'Image' | 'Video' | 'Camera';
  totalVehicles: number;
  processingTime: string;
  status: 'Completed' | 'Processing' | 'Failed';
}

export interface SystemInfo {
  system: string;
  description: string;
  aiModel: string;
  backend: string;
  frontend: string;
  computerVision: string;
  deepLearning: string;
  framework: string;
  version: string;
}

export interface AppSettings {
  model: string;
  confidenceThreshold: number;
  iouThreshold: number;
  inputResolution: string;
  detectionMode: 'Image' | 'Video' | 'Camera';
  maxFileSize: string;
  supportedFormats: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api';

async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export const api = {
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Upload failed');
    }

    return response.json();
  },
  getUploadedFiles: () => apiRequest<UploadedFileRecord[]>('/files'),
  preprocessFile: (fileId: string) => apiRequest<{ success: boolean }>(`/preprocess/${fileId}`, { method: 'POST' }),
  runVehicleDetection: (payload: { fileId?: string; mode: string; file?: File }) =>
    apiRequest<DetectionResponse>('/detect', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  getDetectionHistory: () => apiRequest<ReportRow[]>('/history'),
  getReports: () => apiRequest<{ totalVehicles: number; imagesProcessed: number; videosProcessed: number; detectionSessions: number }[]>('/reports'),
  getSystemInformation: () => apiRequest<SystemInfo>('/system-info'),
  getSettings: () => apiRequest<AppSettings>('/settings'),
  updateSettings: (settings: AppSettings) => apiRequest<AppSettings>('/settings', {
    method: 'PUT',
    body: JSON.stringify(settings),
  }),
};
