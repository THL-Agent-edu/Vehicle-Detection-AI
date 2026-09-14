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
  processedImage?: string;
  resultImageUrl?: string;
  processingTime: number;
  averageConfidence?: number;
  sourceFile?: string;
  detectionId?: string;
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

export interface DataManagementItem {
  name: string;
  size: string;
  time: string;
  status: 'Processed' | 'Processing' | 'Failed';
}

export type FileStatus = 'pending' | 'processing' | 'processed' | 'ready' | 'failed';

export interface UploadedFile {
  id: string;
  fileName: string;
  fileType: 'image' | 'video' | 'file';
  fileSize: number;
  uploadedAt: string;
  status: FileStatus;
  previewUrl?: string;
}

export interface DataStatistics {
  totalFiles: number;
  totalImages: number;
  totalVideos: number;
  readyForDetection: number;
}

export interface DataManagementResponse {
  summary: {
    total_files: number;
    processed: number;
    processing: number;
    failed: number;
  };
  recent_sources: DataManagementItem[];
  metrics: Array<{
    label: string;
    value: string;
    delta: string;
  }>;
}

export interface DetectionSettings {
  model: string;
  confidence: number;
  iou: number;
  imageSize: number;
  mode: 'Image' | 'Video' | 'Camera';
}

export interface Detection {
  className: string;
  confidence: number;
  boundingBox?: BoundingBox;
}

export interface DetectionResult {
  detectionId: string;
  sourceFile: string;
  totalVehicles: number;
  averageConfidence: number;
  processingTime: number;
  detections: Detection[];
  resultUrl?: string;
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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

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

const mockDataStatistics: DataStatistics = {
  totalFiles: 0,
  totalImages: 0,
  totalVideos: 0,
  readyForDetection: 0,
};

const toUploadedFile = (item: Partial<UploadedFile> & { id?: string; fileName?: string; fileType?: UploadedFile['fileType']; fileSize?: number; uploadedAt?: string; status?: UploadedFile['status'] }): UploadedFile | null => {
  if (!item || !item.id || !item.fileName) {
    return null
  }

  return {
    id: String(item.id),
    fileName: item.fileName,
    fileType: item.fileType ?? 'file',
    fileSize: Number(item.fileSize ?? 0),
    uploadedAt: item.uploadedAt ?? new Date().toISOString(),
    status: item.status ?? 'pending',
    previewUrl: item.previewUrl,
  }
}

const normalizeDetectionResponse = (
  payload: Partial<DetectionResponse & DetectionResult> | null | undefined,
  fallbackSource = 'Unknown source',
): DetectionResult | null => {
  if (!payload) {
    return null;
  }

  const rawDetections = Array.isArray(payload.detections) ? payload.detections : [];
  const detections: Detection[] = rawDetections
    .filter((item): item is VehicleDetectionResult => Boolean(item && typeof item.className === 'string'))
    .map((item) => ({
      className: item.className,
      confidence: Number(item.confidence ?? 0),
      boundingBox: item.boundingBox ?? { x: 0, y: 0, width: 0, height: 0 },
    }));

  if (detections.length === 0 && !payload.processedImage && !payload.resultUrl && !payload.resultImageUrl) {
    return null;
  }

  const totalVehicles = detections.length > 0
    ? detections.length
    : (typeof payload.totalVehicles === 'number' ? payload.totalVehicles : 0);

  const averageConfidence = detections.length > 0
    ? Number((detections.reduce((sum, item) => sum + item.confidence, 0) / detections.length).toFixed(1))
    : (typeof payload.averageConfidence === 'number' ? payload.averageConfidence : 0);

  return {
    detectionId: payload.detectionId ?? `det-${Date.now()}`,
    sourceFile: payload.sourceFile ?? fallbackSource,
    totalVehicles,
    averageConfidence,
    processingTime: Number(payload.processingTime ?? 0),
    detections,
    resultUrl: payload.resultUrl ?? payload.processedImage ?? payload.resultImageUrl,
  };
};

export const api = {
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const message = await response.text();
      throw new Error(message || `Upload failed (${response.status})`);
    }

    const payload = await response.json();
    const requiredFields = ['id', 'fileName', 'fileType', 'status'];
    const missingFields = requiredFields.filter((field) => !(field in payload) || payload[field] == null || payload[field] === '');

    if (!payload || typeof payload !== 'object' || missingFields.length > 0) {
      throw new Error(`Upload response missing required metadata: ${missingFields.join(', ') || 'unknown fields'}`);
    }

    return payload as {
      id: string;
      fileName: string;
      fileType: string;
      status: string;
      fileSize?: number;
      uploadedAt?: string;
    };
  },
  getDataStatistics: async (): Promise<DataStatistics> => {
    try {
      const data = await apiRequest<{ summary?: { total_files?: number; processed?: number; processing?: number; failed?: number }; metrics?: Array<{ label?: string; value?: string }> }>('/data-management')
      const summary = data.summary ?? {}
      const totalFiles = Number(summary.total_files ?? 0)
      const processed = Number(summary.processed ?? 0)
      const processing = Number(summary.processing ?? 0)
      const failed = Number(summary.failed ?? 0)

      return {
        totalFiles,
        totalImages: Math.max(0, totalFiles - processing - failed),
        totalVideos: processing,
        readyForDetection: Math.max(0, processed),
      }
    } catch {
      return mockDataStatistics
    }
  },
  getFiles: async (): Promise<UploadedFile[]> => {
    const list = await apiRequest<Array<{ id?: string; fileName?: string; fileType?: UploadedFile['fileType']; fileSize?: number; uploadedAt?: string; status?: UploadedFile['status']; previewUrl?: string }>>('/files')
    const mapped = list
      .map((item) => toUploadedFile(item))
      .filter((item): item is UploadedFile => Boolean(item))

    return mapped
  },
  getReadyFiles: async (): Promise<UploadedFile[]> => (await api.getFiles()).filter((file) => file.status === 'ready' || file.status === 'processed'),
  getFileById: async (id: string): Promise<UploadedFile | undefined> => (await api.getFiles()).find((file) => file.id === id),
  getUploadedFiles: () => apiRequest<UploadedFileRecord[]>('/files'),
  getDataManagementData: () => apiRequest<DataManagementResponse>('/data-management'),
  preprocessFile: async (fileId: string): Promise<{ success: boolean; fileId: string }> => ({ success: true, fileId }),
  deleteFile: async (fileId: string): Promise<{ success: boolean; fileId: string }> => ({ success: true, fileId }),
  retryProcessing: async (fileId: string): Promise<{ success: boolean; fileId: string }> => ({ success: true, fileId }),
  detectImage: async (fileId: string, settings: DetectionSettings): Promise<DetectionResult> => {
    const raw = await api.runVehicleDetection({
      fileId,
      mode: settings.mode,
      settings,
    });

    const normalized = normalizeDetectionResponse(raw, fileId);

    if (!normalized) {
      throw new Error('No detection result returned by the backend.');
    }

    return normalized;
  },
  detectVideo: async (fileId: string, settings: DetectionSettings): Promise<DetectionResult> => {
    const raw = await api.runVehicleDetection({
      fileId,
      mode: settings.mode,
      settings,
    });

    const normalized = normalizeDetectionResponse(raw, fileId);

    if (!normalized) {
      throw new Error('No detection result returned by the backend.');
    }

    return normalized;
  },
  startCameraDetection: async (_settings: DetectionSettings): Promise<DetectionResult> => {
    const raw = await api.runVehicleDetection({
      mode: _settings.mode,
      settings: _settings,
    });

    const normalized = normalizeDetectionResponse(raw, 'Camera Feed');

    if (!normalized) {
      throw new Error('No camera detection result returned by the backend.');
    }

    return normalized;
  },
  getDetectionResult: async (detectionId: string): Promise<DetectionResult> => {
    const response = await apiRequest<DetectionResponse>(`/detect/${detectionId}`);
    const normalized = normalizeDetectionResponse(response, 'Unknown source');

    if (!normalized) {
      throw new Error('No detection result available for this ID.');
    }

    return normalized;
  },
  downloadDetectionResult: async (detectionId: string): Promise<{ downloadUrl: string }> => {
    const result = await api.getDetectionResult(detectionId);

    return {
      downloadUrl: result.resultUrl ?? `data:text/plain;charset=utf-8,download-${detectionId}`,
    };
  },
  runVehicleDetection: (payload: { fileId?: string; mode: string; file?: File; settings?: DetectionSettings }) =>
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
