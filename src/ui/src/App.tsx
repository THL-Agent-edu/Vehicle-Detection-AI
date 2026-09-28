import { useEffect, useRef, useState } from 'react'
import './App.css'
import { Header } from './components/Header'
import { Sidebar } from './components/Sidebar'
import { api, type CameraStatus, type DataStatistics, type DetectionReport, type DetectionSettings, type UploadedFile, type ValidationMetrics } from './services/api'
import { DataManagementPage } from './pages/DataManagementPage'
import { VehicleDetectionPage } from './pages/VehicleDetectionPage'
import { buildDataStatistics, getFileType } from './utils/fileUtils'

const navItems = [
  'Data Management',
  'Vehicle Detection',
  'System Information',
  'Reports',
  'Settings',
]

type FileTypeFilter = 'all' | 'image' | 'video'
type StatusFilter = 'all' | UploadedFile['status']
type SourceMode = 'data' | 'upload' | 'camera'

const systemCards = [
  { label: 'AI model', value: 'YOLOv8n', detail: 'Optimized detection pipeline' },
  { label: 'Backend', value: 'FastAPI', detail: 'REST API layer ready' },
  { label: 'Data source', value: 'Camera + Upload', detail: 'Image and video support' },
  { label: 'Processing', value: 'Real-time', detail: 'Average 220 ms / frame' },
]

const defaultStatistics: DataStatistics = {
  totalFiles: 0,
  totalImages: 0,
  totalVideos: 0,
  readyForDetection: 0,
}

function App() {
  const [activePage, setActivePage] = useState('Data Management')
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [statistics, setStatistics] = useState<DataStatistics>(defaultStatistics)
  const [validationMetrics, setValidationMetrics] = useState<ValidationMetrics | null>(null)
  const [reports, setReports] = useState<DetectionReport[]>([])
  const [reportsLoading, setReportsLoading] = useState(false)
  const [settingsSaving, setSettingsSaving] = useState(false)
  const [settingsMessage, setSettingsMessage] = useState<string | null>(null)
  const [cameraStatus, setCameraStatus] = useState<CameraStatus | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState<FileTypeFilter>('all')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null)
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [processingProgress, setProcessingProgress] = useState<Record<string, number>>({})
  const [sourceMode, setSourceMode] = useState<SourceMode>('data')
  const [selectedReadyFileId, setSelectedReadyFileId] = useState<string | null>(null)
  const [settings, setSettings] = useState<DetectionSettings>({
    model: 'best_v2.pt',
    confidence: 0.5,
    iou: 0.45,
    imageSize: 640,
    mode: 'Image',
    cameraUrl: '',
  })
  const [sourceUploadFile, setSourceUploadFile] = useState<File | null>(null)
  const [isCameraRunning, setIsCameraRunning] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingMessage, setProcessingMessage] = useState('Processing... Please wait.')
  const [latestResult, setLatestResult] = useState<{
    detectionId: string
    sourceFile: string
    totalVehicles: number
    averageConfidence: number
    processingTime: number
    detections: Array<{ className: string; confidence: number; boundingBox?: { x: number; y: number; width: number; height: number } }>
    resultUrl?: string
  } | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [sourceModalOpen, setSourceModalOpen] = useState(false)
  const fileInputRef = useRef<HTMLInputElement | null>(null)
  const uploadSourceInputRef = useRef<HTMLInputElement | null>(null)

  useEffect(() => {
    if (activePage !== 'System Information') return

    api.getValidationMetrics()
      .then(setValidationMetrics)
      .catch(() => setValidationMetrics(null))
  }, [activePage])

  useEffect(() => {
    if (activePage !== 'Settings') return

    setSettingsMessage(null)
    api.getDetectionSettings()
      .then((loadedSettings) => setSettings({
        ...loadedSettings,
        cameraUrl: loadedSettings.cameraUrl ?? '',
      }))
      .catch(() => setSettingsMessage('Unable to load saved settings.'))

    api.getCameraStatus().then(setCameraStatus).catch(() => setCameraStatus(null))
  }, [activePage])

  useEffect(() => {
    if (activePage !== 'Settings' || !cameraStatus?.running) return
    const interval = window.setInterval(() => {
      api.getCameraStatus().then((status) => {
        setCameraStatus(status)
        if (status.error) setSettingsMessage(status.error)
      }).catch(() => undefined)
    }, 1000)
    return () => window.clearInterval(interval)
  }, [activePage, cameraStatus?.running])

  useEffect(() => {
    if (activePage !== 'Reports') return

    setReportsLoading(true)
    api.getReports()
      .then(setReports)
      .catch(() => setReports([]))
      .finally(() => setReportsLoading(false))
  }, [activePage])

  useEffect(() => {
    if (activePage !== 'Data Management') return

    let isMounted = true

    api.getDataStatistics()
      .then((data) => {
        if (isMounted) {
          setStatistics(data)
        }
      })
      .catch(() => {
        if (isMounted) {
          setStatistics(buildDataStatistics(files))
        }
      })

    api.getFiles()
      .then((items) => {
        if (isMounted) {
          setFiles(items)
          setStatistics(buildDataStatistics(items))
        }
      })
      .catch(() => {
        if (isMounted) {
          setStatistics(buildDataStatistics(files))
        }
      })

    return () => {
      isMounted = false
    }
  }, [activePage])

  useEffect(() => {
    setStatistics(buildDataStatistics(files))
  }, [files])

  useEffect(() => {
    if (sourceMode !== 'data') {
      return
    }

    if (!selectedReadyFileId) {
      const firstReadyFile = files.find((item) => item.status === 'ready' || item.status === 'processed')
      if (firstReadyFile) {
        setSelectedReadyFileId(firstReadyFile.id)
      }
    }
  }, [files, selectedReadyFileId, sourceMode])

  const handleBrowseClick = () => {
    fileInputRef.current?.click()
  }

  const handleUploadFiles = async (fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) {
      return
    }

    const allowedExtensions = ['jpg', 'jpeg', 'png', 'mp4']
    const maxFileSize = 500 * 1024 * 1024
    const validFiles: File[] = []

    for (const file of Array.from(fileList)) {
      const extension = file.name.split('.').pop()?.toLowerCase() ?? ''
      if (!allowedExtensions.includes(extension)) {
        setUploadError('Unsupported file format. Please upload JPG, JPEG, PNG or MP4.')
        return
      }

      if (file.size > maxFileSize) {
        setUploadError('File size exceeds the 500 MB limit.')
        return
      }

      validFiles.push(file)
    }

    if (validFiles.length === 0) {
      return
    }

    setUploadError(null)

    try {
      for (const file of validFiles) {
        const response = await api.uploadFile(file)
        if (!response || typeof response !== 'object') {
          throw new Error('Backend upload response was invalid.')
        }
      }

      const refreshed = await api.getFiles()
      setFiles(refreshed)
      setStatistics(buildDataStatistics(refreshed))
    } catch (error) {
      console.error('Upload failed', error)

      const message = error instanceof Error && /fetch|network|Failed to fetch|ECONNREFUSED|ERR_CONNECTION_REFUSED|Connection refused/i.test(error.message)
        ? 'Unable to connect to the detection server.'
        : error instanceof Error && error.message
          ? error.message
          : 'Upload failed.'

      setUploadError(message)
      setFiles((current) => current.filter((item) => item.status !== 'pending'))
    }
  }

  const handlePreprocess = (fileId: string) => {
    let progress = 0

    setFiles((current) => current.map((item) => (item.id === fileId ? { ...item, status: 'processing' } : item)))
    setProcessingProgress((current) => ({ ...current, [fileId]: 0 }))

    const interval = window.setInterval(() => {
      progress += 25
      setProcessingProgress((current) => ({
        ...current,
        [fileId]: Math.min(progress, 100),
      }))

      if (progress >= 100) {
        window.clearInterval(interval)
        setFiles((current) => current.map((item) => (item.id === fileId ? { ...item, status: 'ready' } : item)))
        setProcessingProgress((current) => ({ ...current, [fileId]: 100 }))
      }
    }, 220)
  }

  const handleRetry = (fileId: string) => {
    setFiles((current) => current.map((item) => (item.id === fileId ? { ...item, status: 'processing' } : item)))
    setProcessingProgress((current) => ({ ...current, [fileId]: 0 }))

    let progress = 0
    const interval = window.setInterval(() => {
      progress += 20
      setProcessingProgress((current) => ({
        ...current,
        [fileId]: Math.min(progress, 100),
      }))

      if (progress >= 100) {
        window.clearInterval(interval)
        setFiles((current) => current.map((item) => (item.id === fileId ? { ...item, status: 'ready' } : item)))
        setProcessingProgress((current) => ({ ...current, [fileId]: 100 }))
      }
    }, 250)
  }

  const handleDelete = (fileId: string) => {
    setFiles((current) => {
      const nextItems = current.filter((item) => item.id !== fileId)
      setStatistics(buildDataStatistics(nextItems))
      return nextItems
    })
    if (selectedFile?.id === fileId) {
      setSelectedFile(null)
    }
    setPendingDeleteId(null)
  }

  const handleRunDetection = async () => {
    try {
      setErrorMessage(null)
      setLatestResult(null)
      setIsProcessing(true)
      setProcessingMessage('Running YOLOv8...')

      let result: {
        detectionId: string
        sourceFile: string
        totalVehicles: number
        averageConfidence: number
        processingTime: number
        detections: Array<{ className: string; confidence: number; boundingBox?: { x: number; y: number; width: number; height: number } }>
        resultUrl?: string
      }

      if (sourceMode === 'data') {
        const effectiveFileId = selectedReadyFileId ?? files.find((item) => item.status === 'ready' || item.status === 'processed')?.id ?? null
        if (!effectiveFileId) {
          throw new Error('No source selected')
        }

        const sourceFile = files.find((item) => item.id === effectiveFileId)
        if (!sourceFile) throw new Error('Selected file not found')

        result = sourceFile.fileType === 'video' || settings.mode === 'Video'
          ? await api.detectVideo(effectiveFileId, {
              ...settings,
              mode: settings.mode,
            })
          : await api.detectImage(effectiveFileId, {
              ...settings,
              mode: settings.mode,
            })
      } else if (sourceMode === 'upload' && sourceUploadFile) {
        const uploadId = `upload-${Date.now()}`
        const tempFile: UploadedFile = {
          id: uploadId,
          fileName: sourceUploadFile.name,
          fileType: getFileType(sourceUploadFile.name),
          fileSize: sourceUploadFile.size,
          uploadedAt: new Date().toISOString(),
          status: 'ready',
          previewUrl: sourceUploadFile.type.startsWith('image') ? URL.createObjectURL(sourceUploadFile) : undefined,
        }

        setFiles((current) => [tempFile, ...current])
        result = tempFile.fileType === 'video' || settings.mode === 'Video'
          ? await api.detectVideo(uploadId, { ...settings, mode: settings.mode })
          : await api.detectImage(uploadId, { ...settings, mode: settings.mode })
      } else if (sourceMode === 'camera') {
        result = await api.startCameraDetection({ ...settings, mode: settings.mode })
      } else {
        throw new Error('No source selected')
      }

      setLatestResult(result)
      api.getReports().then(setReports).catch(() => undefined)
      setProcessingMessage('Detection completed successfully.')
    } catch (error) {
      console.error(error)
      setLatestResult(null)

      const message = error instanceof Error && /fetch|network|Failed to fetch|500|400|404/i.test(error.message)
        ? 'Unable to connect to the detection server.'
        : 'Vehicle detection failed.'

      setErrorMessage(message)
      setProcessingMessage(message)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleDownloadResult = async () => {
    if (!latestResult) return

    try {
      const response = await api.downloadDetectionResult(latestResult.detectionId)
      const link = document.createElement('a')
      link.href = response.downloadUrl
      link.download = `${latestResult.sourceFile.replace(/\.[^.]+$/, '')}-result.txt`
      link.click()
    } catch (error) {
      console.error('Download failed', error)
    }
  }

  const handleClearResult = () => {
    setLatestResult(null)
    setErrorMessage(null)
    setProcessingMessage('Processing... Please wait.')
  }

  const handleAnalyzeData = () => {
    setActivePage('System Information')
  }

  const handleSaveSettings = async () => {
    setSettingsSaving(true)
    setSettingsMessage(null)
    try {
      const saved = await api.updateDetectionSettings(settings)
      setSettings(saved)
      setSettingsMessage('Settings saved successfully.')
    } catch {
      setSettingsMessage('Unable to save settings.')
    } finally {
      setSettingsSaving(false)
    }
  }

  const handleStartLiveCamera = async () => {
    try {
      const response = await api.startCamera({ ...settings, mode: 'Camera' })
      setSettings((current) => ({ ...current, mode: 'Camera' }))
      setCameraStatus({ running: response.running, url: response.url, frame: 0, detections: [], error: null })
      setSettingsMessage('Traffic camera recognition started.')
    } catch (error) {
      setSettingsMessage(error instanceof Error ? error.message : 'Unable to start the traffic camera.')
    }
  }

  const handleStopLiveCamera = () => {
    api.stopCamera().then(() => setCameraStatus((current) => current ? { ...current, running: false } : null)).catch(() => undefined)
    setSettingsMessage('Traffic camera recognition stopped.')
  }

  const handleExportReports = () => {
    if (reports.length === 0) return

    const header = ['Date', 'File', 'Type', 'Vehicles', 'Runtime (s)', 'Status']
    const rows = reports.map((report) => [
      report.date,
      report.fileName,
      report.type,
      report.totalVehicles,
      report.processingTime,
      report.status,
    ])
    const csv = [header, ...rows]
      .map((row) => row.map((value) => `"${String(value).replaceAll('"', '""')}"`).join(','))
      .join('\n')
    const link = document.createElement('a')
    link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }))
    link.download = `vehicle-detection-reports-${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
    URL.revokeObjectURL(link.href)
  }

  const renderPage = () => {
    if (activePage === 'Vehicle Detection') {
      return (
        <VehicleDetectionPage
          files={files}
          sourceMode={sourceMode}
          setSourceMode={setSourceMode}
          selectedReadyFileId={selectedReadyFileId}
          setSelectedReadyFileId={setSelectedReadyFileId}
          settings={settings}
          setSettings={setSettings}
          sourceUploadFile={sourceUploadFile}
          setSourceUploadFile={setSourceUploadFile}
          isCameraRunning={isCameraRunning}
          setIsCameraRunning={setIsCameraRunning}
          isProcessing={isProcessing}
          processingMessage={processingMessage}
          latestResult={latestResult}
          errorMessage={errorMessage}
          sourceModalOpen={sourceModalOpen}
          setSourceModalOpen={setSourceModalOpen}
          onRunDetection={handleRunDetection}
          onDownloadResult={handleDownloadResult}
          onClearResult={handleClearResult}
          onOpenHistory={() => setActivePage('Reports')}
          uploadSourceInputRef={uploadSourceInputRef}
        />
      )
    }

    if (activePage === 'System Information') {
      return (
        <section className="grid-cards four-up">
          {systemCards.map((card) => (
            <article key={card.label} className="section-card info-card">
              <p className="mini-label">{card.label}</p>
              <h3>{card.value}</h3>
              <span>{card.detail}</span>
            </article>
          ))}
          {validationMetrics && (
            <article className="section-card info-card">
              <p className="mini-label">Validation F1 score</p>
              <h3>{(validationMetrics.f1 * 100).toFixed(1)}%</h3>
              <span>Precision {(validationMetrics.precision * 100).toFixed(1)}% / Recall {(validationMetrics.recall * 100).toFixed(1)}%</span>
            </article>
          )}
        </section>
      )
    }

    if (activePage === 'Reports') {
      return (
        <section className="section-card">
          <div className="section-header compact">
            <div>
              <p className="eyebrow">Analysis history</p>
              <h2>Processing reports</h2>
            </div>
            <button type="button" className="primary-btn small" onClick={handleExportReports} disabled={reports.length === 0}>
              Export report
            </button>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>File</th>
                  <th>Type</th>
                  <th>Vehicles</th>
                  <th>Runtime</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {reportsLoading ? (
                  <tr><td colSpan={6}>Loading reports...</td></tr>
                ) : reports.length === 0 ? (
                  <tr><td colSpan={6}>No detection reports yet. Run a detection to create the first report.</td></tr>
                ) : reports.map((row) => (
                  <tr key={row.id}>
                    <td>{new Date(row.date).toLocaleString()}</td>
                    <td>{row.fileName}</td>
                    <td>{row.type}</td>
                    <td>{row.totalVehicles}</td>
                    <td>{row.processingTime.toFixed(2)}s</td>
                    <td>
                      <span className={`status-pill ${row.status.toLowerCase()}`}>{row.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )
    }

    if (activePage === 'Settings') {
      return (
        <section className="settings-grid">
          <article className="section-card">
            <div className="section-header compact">
              <div>
                <p className="eyebrow">Model controls</p>
                <h2>Detection settings</h2>
              </div>
              <button type="button" className="primary-btn small" onClick={handleSaveSettings} disabled={settingsSaving}>
                {settingsSaving ? 'Saving...' : 'Save settings'}
              </button>
            </div>

            <div className="field-group">
              <label>
                Model version
                <select value={settings.model} onChange={(event) => setSettings((current) => ({ ...current, model: event.target.value }))}>
                  <option value="best.pt">best.pt</option>
                  <option value="best_v2.pt">best_v2.pt</option>
                  <option value="yolov8n.pt">yolov8n.pt</option>
                  <option value="yolov8s.pt">yolov8s.pt</option>
                </select>
              </label>

              <label>
                Confidence threshold: {settings.confidence.toFixed(2)}
                <input type="range" min="0.05" max="1" step="0.05" value={settings.confidence} onChange={(event) => setSettings((current) => ({ ...current, confidence: Number(event.target.value) }))} />
              </label>

              <label>
                IoU threshold: {settings.iou.toFixed(2)}
                <input type="range" min="0.05" max="1" step="0.05" value={settings.iou} onChange={(event) => setSettings((current) => ({ ...current, iou: Number(event.target.value) }))} />
              </label>

              <label>
                Input resolution
                <select value={settings.imageSize} onChange={(event) => setSettings((current) => ({ ...current, imageSize: Number(event.target.value) }))}>
                  <option value={320}>320 × 320</option>
                  <option value={640}>640 × 640</option>
                  <option value={1280}>1280 × 1280</option>
                </select>
              </label>

              <label>
                Detection mode
                <select value={settings.mode} onChange={(event) => setSettings((current) => ({ ...current, mode: event.target.value as DetectionSettings['mode'] }))}>
                  <option value="Image">Image</option>
                  <option value="Video">Video</option>
                  <option value="Camera">Camera</option>
                </select>
              </label>
              <label>
                Traffic camera URL
                <input type="url" placeholder="rtsp://... or https://..." value={settings.cameraUrl} onChange={(event) => setSettings((current) => ({ ...current, cameraUrl: event.target.value }))} />
              </label>
            </div>
            {settingsMessage && <p className="form-message">{settingsMessage}</p>}
          </article>

          <article className="section-card">
            <div className="section-header compact">
              <div>
                <p className="eyebrow">Remote stream</p>
                <h2>Traffic camera recognition</h2>
              </div>
              <span className={`status-pill ${cameraStatus?.running ? 'success' : 'warning'}`}>
                {cameraStatus?.running ? 'Running' : 'Stopped'}
              </span>
            </div>
            <p className="settings-help">YOLO reads the configured camera URL continuously on the backend. Supported sources: RTSP, HTTP and HTTPS streams.</p>
            <div className="camera-runtime-stats">
              <span>Frames: <strong>{cameraStatus?.frame ?? 0}</strong></span>
              <span>Vehicles: <strong>{cameraStatus?.detections.length ?? 0}</strong></span>
            </div>
            <button type="button" className={cameraStatus?.running ? 'secondary-btn small' : 'primary-btn small'} onClick={cameraStatus?.running ? handleStopLiveCamera : handleStartLiveCamera} disabled={!settings.cameraUrl.trim()}>
              {cameraStatus?.running ? 'Stop recognition' : 'Start recognition'}
            </button>
            {cameraStatus?.error && <p className="error-message">{cameraStatus.error}</p>}
          </article>

          <article className="section-card">
            <div className="section-header compact">
              <h2>Integration</h2>
            </div>

            <div className="field-group">
              <label>
                API base URL
                <input value={import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'} readOnly />
              </label>

              <label>
                Max file size
                <input value="500 MB" readOnly />
              </label>

              <label>
                Supported formats
                <input value=".jpg, .jpeg, .png, .mp4" readOnly />
              </label>
            </div>
          </article>
        </section>
      )
    }

    return (
      <DataManagementPage
        statistics={statistics}
        files={files}
        searchTerm={searchTerm}
        typeFilter={typeFilter}
        statusFilter={statusFilter}
        selectedFile={selectedFile}
        pendingDeleteId={pendingDeleteId}
        uploadError={uploadError}
        processingProgress={processingProgress}
        fileInputRef={fileInputRef}
        onSearchChange={setSearchTerm}
        onTypeFilterChange={setTypeFilter}
        onStatusFilterChange={setStatusFilter}
        onBrowseClick={handleBrowseClick}
        onUploadFiles={handleUploadFiles}
        onPreprocess={handlePreprocess}
        onRetry={handleRetry}
        onDeleteRequest={setPendingDeleteId}
        onDeleteConfirm={handleDelete}
        onSelectFile={setSelectedFile}
        onClosePreview={() => setSelectedFile(null)}
        onCancelDelete={() => setPendingDeleteId(null)}
      />
    )
  }

  return (
    <div className="app-shell">
      <Sidebar items={navItems} activeItem={activePage} onSelect={setActivePage} />

      <main className="main-panel">
        <Header
          title={activePage}
          subtitle="AI vehicle detection dashboard"
          actionLabel="Analyze data"
          onAction={handleAnalyzeData}
        />

        {renderPage()}
      </main>
    </div>
  )
}

export default App
