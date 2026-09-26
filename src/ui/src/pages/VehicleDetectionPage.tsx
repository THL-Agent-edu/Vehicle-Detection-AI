import { useEffect, useRef, useState } from 'react'
import type { Dispatch, RefObject, SetStateAction } from 'react'
import type { DetectionResult, DetectionSettings, UploadedFile } from '../services/api'
import { formatBytes } from '../utils/fileUtils'

type SourceMode = 'data' | 'upload' | 'camera'

type VehicleDetectionPageProps = {
  files: UploadedFile[]
  sourceMode: SourceMode
  setSourceMode: (mode: SourceMode) => void
  selectedReadyFileId: string | null
  setSelectedReadyFileId: (id: string | null) => void
  settings: DetectionSettings
  setSettings: Dispatch<SetStateAction<DetectionSettings>>
  sourceUploadFile: File | null
  setSourceUploadFile: (file: File | null) => void
  isCameraRunning: boolean
  setIsCameraRunning: Dispatch<SetStateAction<boolean>>
  isProcessing: boolean
  processingMessage: string
  latestResult: DetectionResult | null
  errorMessage: string | null
  sourceModalOpen: boolean
  setSourceModalOpen: (open: boolean) => void
  onRunDetection: () => void
  onDownloadResult: () => void
  onClearResult: () => void
  uploadSourceInputRef: RefObject<HTMLInputElement | null>
}

const getReadyFiles = (files: UploadedFile[]) => files.filter((item) => item.status === 'ready' || item.status === 'processed')

export function VehicleDetectionPage({
  files,
  sourceMode,
  setSourceMode,
  selectedReadyFileId,
  setSelectedReadyFileId,
  settings,
  setSettings,
  sourceUploadFile,
  setSourceUploadFile,
  isCameraRunning,
  setIsCameraRunning,
  isProcessing,
  processingMessage,
  latestResult,
  errorMessage,
  sourceModalOpen,
  setSourceModalOpen,
  onRunDetection,
  onDownloadResult,
  onClearResult,
  uploadSourceInputRef,
}: VehicleDetectionPageProps) {
  const readyFiles = getReadyFiles(files)
  const selectedSource = sourceMode === 'data'
    ? readyFiles.find((item) => item.id === selectedReadyFileId) ?? null
    : sourceMode === 'upload' && sourceUploadFile
      ? {
          id: sourceUploadFile.name,
          fileName: sourceUploadFile.name,
          fileType: sourceUploadFile.name.toLowerCase().endsWith('.mp4') ? 'video' : 'image',
          fileSize: sourceUploadFile.size,
          uploadedAt: new Date().toISOString(),
          status: 'ready' as const,
        }
      : null

  const isVideoSource = selectedSource?.fileType === 'video'
    || (sourceMode === 'upload' && !!sourceUploadFile && sourceUploadFile.name.toLowerCase().endsWith('.mp4'))

  const sourcePreviewUrl = isVideoSource
    ? (sourceMode === 'data' && selectedSource ? `http://127.0.0.1:8000/uploads/${selectedSource.id}` : null)
      ?? (sourceMode === 'upload' && sourceUploadFile ? URL.createObjectURL(sourceUploadFile) : null)
    : latestResult?.resultUrl
      ?? (sourceMode === 'data' && selectedSource ? `http://127.0.0.1:8000/uploads/${selectedSource.id}` : null)
      ?? (sourceMode === 'upload' && sourceUploadFile ? URL.createObjectURL(sourceUploadFile) : null)
      ?? null

  const [previewAspectRatio, setPreviewAspectRatio] = useState<number | null>(null)
  const [currentVideoSecond, setCurrentVideoSecond] = useState(0)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const videoSyncFrameRef = useRef<number | null>(null)

  const getVideoFrameTimestamp = (frame: { timestamp?: number; second?: number; frame?: number } | undefined | null) => {
    if (!frame) {
      return 0
    }

    if (typeof frame.timestamp === 'number' && Number.isFinite(frame.timestamp)) {
      return frame.timestamp
    }

    if (typeof frame.second === 'number' && Number.isFinite(frame.second)) {
      return frame.second
    }

    if (typeof frame.frame === 'number' && Number.isFinite(frame.frame)) {
      return frame.frame
    }

    return 0
  }

  useEffect(() => {
    setCurrentVideoSecond(0)
  }, [latestResult?.detectionId, selectedReadyFileId, sourceUploadFile?.name, sourceMode])

  const findNearestVideoFrame = (time: number) => {
    if (!latestResult?.videoFrames || latestResult.videoFrames.length === 0) {
      return null
    }

    let nearest = latestResult.videoFrames[0]
    let nearestDistance = Number.POSITIVE_INFINITY

    for (const frame of latestResult.videoFrames) {
      const timestamp = getVideoFrameTimestamp(frame)
      const distance = Math.abs(timestamp - time)
      if (distance < nearestDistance) {
        nearest = frame
        nearestDistance = distance
      }
    }

    return nearest
  }

  const resolvedVideoFrames = latestResult?.videoFrames ?? []

  useEffect(() => {
    if (!isVideoSource || resolvedVideoFrames.length === 0 || !videoRef.current) {
      return
    }

    const video = videoRef.current
    const targetFrame = findNearestVideoFrame(video.currentTime || 0)
    if (targetFrame) {
      setCurrentVideoSecond(getVideoFrameTimestamp(targetFrame))
    }
  }, [isVideoSource, resolvedVideoFrames.length, latestResult?.detectionId])

  useEffect(() => {
    if (!isVideoSource || !latestResult?.videoFrames || latestResult.videoFrames.length === 0) {
      return
    }

    const video = videoRef.current
    if (!video) {
      return
    }

    const stopSyncLoop = () => {
      if (videoSyncFrameRef.current !== null) {
        if (typeof video.cancelVideoFrameCallback === 'function') {
          video.cancelVideoFrameCallback(videoSyncFrameRef.current)
        }
        cancelAnimationFrame(videoSyncFrameRef.current)
        videoSyncFrameRef.current = null
      }
    }

    const syncVideoOverlay = () => {
      const currentTime = Number.isFinite(video.currentTime) ? video.currentTime : 0
      const matchedFrame = findNearestVideoFrame(currentTime)
      const nextTime = matchedFrame ? getVideoFrameTimestamp(matchedFrame) : currentTime
      setCurrentVideoSecond(nextTime)

      if (!video.paused) {
        if (typeof video.requestVideoFrameCallback === 'function') {
          videoSyncFrameRef.current = video.requestVideoFrameCallback(() => syncVideoOverlay())
        } else {
          videoSyncFrameRef.current = requestAnimationFrame(syncVideoOverlay)
        }
      }
    }

    const handleSeeked = () => {
      stopSyncLoop()
      syncVideoOverlay()
    }

    const handlePause = () => {
      stopSyncLoop()
      syncVideoOverlay()
    }

    const handleTimeUpdate = () => {
      syncVideoOverlay()
    }

    video.addEventListener('timeupdate', handleTimeUpdate)
    video.addEventListener('seeked', handleSeeked)
    video.addEventListener('play', syncVideoOverlay)
    video.addEventListener('pause', handlePause)

    if (!video.paused) {
      syncVideoOverlay()
    }

    return () => {
      stopSyncLoop()
      video.removeEventListener('timeupdate', handleTimeUpdate)
      video.removeEventListener('seeked', handleSeeked)
      video.removeEventListener('play', syncVideoOverlay)
      video.removeEventListener('pause', handlePause)
    }
  }, [isVideoSource, latestResult?.videoFrames, latestResult?.detectionId])

  const activeVideoDetections = sourceMode !== 'camera' && latestResult?.videoFrames && latestResult.videoFrames.length > 0
    ? findNearestVideoFrame(currentVideoSecond)?.detections
      ?? latestResult.videoFrames[latestResult.videoFrames.length - 1].detections
    : latestResult?.detections ?? []

  const getVehicleStyle = (label: string) => {
    const normalized = label.toLowerCase()
    const palette: Record<string, { border: string; fill: string; badge: string }> = {
      car: { border: '#2563eb', fill: 'rgba(37, 99, 235, 0.10)', badge: '#2563eb' },
      truck: { border: '#f59e0b', fill: 'rgba(245, 158, 11, 0.12)', badge: '#f59e0b' },
      bus: { border: '#10b981', fill: 'rgba(16, 185, 129, 0.12)', badge: '#10b981' },
      motorcycle: { border: '#8b5cf6', fill: 'rgba(139, 92, 246, 0.12)', badge: '#8b5cf6' },
      bicycle: { border: '#ec4899', fill: 'rgba(236, 72, 153, 0.12)', badge: '#ec4899' },
      van: { border: '#14b8a6', fill: 'rgba(20, 184, 166, 0.12)', badge: '#14b8a6' },
      person: { border: '#ef4444', fill: 'rgba(239, 68, 68, 0.12)', badge: '#ef4444' },
    }

    const matched = palette[normalized] ?? palette.car
    return {
      borderColor: matched.border,
      background: matched.fill,
      boxShadow: `inset 0 0 0 1px rgba(255, 255, 255, 0.5)`,
      labelBackground: matched.badge,
      scoreBackground: matched.badge,
    }
  }

  useEffect(() => {
    if (!sourcePreviewUrl || !sourcePreviewUrl.toLowerCase().match(/\.(jpg|jpeg|png|bmp|webp)$/)) {
      setPreviewAspectRatio(null)
      return
    }

    const image = new Image()
    image.onload = () => {
      if (image.naturalWidth > 0 && image.naturalHeight > 0) {
        setPreviewAspectRatio(image.naturalWidth / image.naturalHeight)
      } else {
        setPreviewAspectRatio(null)
      }
    }
    image.onerror = () => setPreviewAspectRatio(null)
    image.src = sourcePreviewUrl

    return () => {
      image.onload = null
      image.onerror = null
    }
  }, [sourcePreviewUrl])

  return (
    <>
      <section className="vehicle-header-bar">
        <div>
          <p className="eyebrow">AI VEHICLE DETECTION</p>
          <h2>Vehicle Detection</h2>
        </div>
        <button type="button" className="primary-btn small">Detection History</button>
      </section>

      <section className="vehicle-layout">
        <div className="vehicle-column left-layout">
          <article className="section-card">
            <div className="section-header compact">
              <h2>Source</h2>
            </div>

            <div className="source-mode-toggle">
              {['data', 'upload', 'camera'].map((option) => (
                <button
                  key={option}
                  type="button"
                  className={`mode-pill ${sourceMode === option ? 'active' : ''}`}
                  onClick={() => setSourceMode(option as SourceMode)}
                >
                  {option === 'data' ? 'Data Management' : option === 'upload' ? 'Upload New File' : 'Camera'}
                </button>
              ))}
            </div>

            {sourceMode === 'data' ? (
              <div className="source-panel">
                <div className="selected-source-box">
                  {selectedSource ? (
                    <>
                      <div className="source-icon">{selectedSource.fileType === 'video' ? '🎬' : '🖼️'}</div>
                      <div className="source-copy">
                        <strong>{selectedSource.fileName}</strong>
                        <span>{selectedSource.fileType.toUpperCase()} • {formatBytes(selectedSource.fileSize)} • Ready</span>
                      </div>
                    </>
                  ) : (
                    <div className="source-copy empty-copy">No ready file selected.</div>
                  )}
                </div>
                <button type="button" className="secondary-btn small" onClick={() => setSourceModalOpen(true)}>
                  Change Source
                </button>
              </div>
            ) : null}

            {sourceMode === 'upload' ? (
              <div className="source-panel upload-panel">
                <input
                  ref={uploadSourceInputRef}
                  type="file"
                  accept=".jpg,.jpeg,.png,.mp4"
                  hidden
                  onChange={(event) => setSourceUploadFile(event.target.files?.[0] ?? null)}
                />
                <div className="upload-compact-box" onClick={() => uploadSourceInputRef.current?.click()} role="button" tabIndex={0}>
                  <div className="upload-icon compact">+</div>
                  <div>
                    <strong>{sourceUploadFile ? sourceUploadFile.name : 'Select a file to upload'}</strong>
                    <span>{sourceUploadFile ? `${formatBytes(sourceUploadFile.size)} • Ready for FastAPI` : 'JPG, JPEG, PNG, MP4 • Max 500 MB'}</span>
                  </div>
                </div>
              </div>
            ) : null}

            {sourceMode === 'camera' ? (
              <div className="source-panel camera-panel">
                <div className="camera-preview-box">
                  <span className="camera-label">Camera Feed</span>
                  <div className="camera-status-badge">
                    <span className={`status-dot ${isCameraRunning ? 'green' : 'gray'}`} />
                    {isCameraRunning ? 'Online' : 'Offline'}
                  </div>
                </div>

                <button
                  type="button"
                  className={isCameraRunning ? 'secondary-btn small' : 'primary-btn small'}
                  onClick={() => setIsCameraRunning((current) => !current)}
                >
                  {isCameraRunning ? 'Stop Camera' : 'Start Camera'}
                </button>
              </div>
            ) : null}
          </article>

          <article className="section-card detection-settings-card">
            <div className="section-header compact">
              <h2>Detection Settings</h2>
            </div>

            <div className="field-group compact-fields">
              <label>
                Detection Model
                <select value={settings.model} onChange={(event) => setSettings((current) => ({ ...current, model: event.target.value }))}>
                  <option value="best.pt">best.pt</option>
                  <option value="best_v2.pt">best_v2.pt</option>
                  <option value="ensemble">ensemble</option>
                  <option value="yolov8n.pt">yolov8n.pt</option>
                  <option value="yolov8s.pt">yolov8s.pt</option>
                </select>
              </label>

              <label>
                Confidence Threshold
                <input
                  type="number"
                  min={0.1}
                  max={1}
                  step={0.01}
                  value={settings.confidence}
                  onChange={(event) => setSettings((current) => ({ ...current, confidence: Number(event.target.value) }))}
                />
              </label>

              <label>
                IoU Threshold
                <input
                  type="number"
                  min={0.1}
                  max={1}
                  step={0.01}
                  value={settings.iou}
                  onChange={(event) => setSettings((current) => ({ ...current, iou: Number(event.target.value) }))}
                />
              </label>

              <label>
                Image Size
                <select value={settings.imageSize} onChange={(event) => setSettings((current) => ({ ...current, imageSize: Number(event.target.value) }))}>
                  <option value={320}>320 × 320</option>
                  <option value={640}>640 × 640</option>
                  <option value={1280}>1280 × 1280</option>
                </select>
              </label>

              <div className="mode-selection">
                <span>Detection Mode</span>
                <div className="radio-row">
                  {(['Image', 'Video', 'Camera'] as const).map((mode) => (
                    <label key={mode} className="radio-option">
                      <input
                        type="radio"
                        name="detectionMode"
                        checked={settings.mode === mode}
                        onChange={() => setSettings((current) => ({ ...current, mode }))}
                      />
                      <span>{mode}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </article>
        </div>

        <div className="vehicle-column right-layout">
          <article className="section-card detection-preview-card">
            <div className="section-header compact">
              <h2>Detection Preview</h2>
            </div>

            <div className="detection-preview-box">
              {sourcePreviewUrl ? (
                <div
                  className="detection-overlay-surface"
                  style={previewAspectRatio ? { aspectRatio: `${previewAspectRatio}` } : undefined}
                >
                  {(selectedSource?.fileType === 'video' || (sourceMode === 'upload' && sourceUploadFile && sourceUploadFile.name.toLowerCase().endsWith('.mp4'))) ? (
                    <video
                      ref={videoRef}
                      key={`${selectedSource?.id ?? sourceUploadFile?.name ?? 'video'}-${latestResult?.detectionId ?? 'new'}`}
                      src={sourcePreviewUrl}
                      controls
                      className="detection-source-video"
                      onLoadedMetadata={(event) => {
                        const { videoWidth, videoHeight } = event.currentTarget
                        if (videoWidth > 0 && videoHeight > 0) {
                          setPreviewAspectRatio(videoWidth / videoHeight)
                        }
                      }}
                      onSeeked={(event) => {
                        const currentTime = Number.isFinite(event.currentTarget.currentTime) ? event.currentTarget.currentTime : 0
                        const matchedFrame = findNearestVideoFrame(currentTime)
                        if (matchedFrame) {
                          setCurrentVideoSecond(getVideoFrameTimestamp(matchedFrame))
                        }
                      }}
                    />
                  ) : (
                    <img src={sourcePreviewUrl} alt="Detection source preview" className="detection-source-image" />
                  )}
                  {activeVideoDetections && activeVideoDetections.length > 0 ? (
                    activeVideoDetections.map((item, index) => {
                      const box = item.boundingBox ?? { x: 15 + index * 18, y: 22 + index * 12, width: 24, height: 16 }
                      const style = getVehicleStyle(item.className)
                      return (
                        <div
                          key={`${item.className}-${index}-${currentVideoSecond}`}
                          className="bbox-box"
                          style={{
                            left: `${box.x}%`,
                            top: `${box.y}%`,
                            width: `${box.width}%`,
                            height: `${box.height}%`,
                            borderColor: style.borderColor,
                            background: style.background,
                            boxShadow: style.boxShadow,
                          }}
                        >
                          <span className="bbox-label" style={{ background: style.labelBackground }}>{item.className}</span>
                          <span className="bbox-score" style={{ background: style.scoreBackground }}>{item.confidence.toFixed(1)}%</span>
                        </div>
                      )
                    })
                  ) : null}
                </div>
              ) : (
                <div className="empty-preview">No detection result yet</div>
              )}
            </div>

            <div className="detection-actions">
              {!latestResult ? (
                <button type="button" className="primary-btn" onClick={onRunDetection} disabled={isProcessing}>
                  {isProcessing ? 'Running...' : 'Start Detection'}
                </button>
              ) : (
                <>
                  <button type="button" className="primary-btn" onClick={onRunDetection} disabled={isProcessing}>
                    {isProcessing ? 'Running...' : 'Run Again'}
                  </button>
                  <button type="button" className="secondary-btn" onClick={onDownloadResult}>Download Result</button>
                  <button type="button" className="ghost-btn" onClick={onClearResult}>Clear</button>
                </>
              )}
            </div>

            {isProcessing ? <div className="processing-state"><div className="spinner" /><span>{processingMessage}</span></div> : null}
            {!isProcessing && latestResult && !errorMessage ? <div className="success-state">Detection completed successfully.</div> : null}
            {errorMessage ? <div className="error-message detection-error">{errorMessage}</div> : null}
          </article>

          <article className="section-card">
            <div className="section-header compact">
              <h2>Detection Results</h2>
            </div>

            {latestResult ? (
              <>
                <div className="result-summary-grid">
                  <div><span>Total Vehicles</span><strong>{latestResult.totalVehicles}</strong></div>
                  <div><span>Average Confidence</span><strong>{latestResult.averageConfidence.toFixed(1)}%</strong></div>
                </div>

                <div className="class-summary">
                  {Object.entries(
                    latestResult.detections.reduce((acc, item) => {
                      acc[item.className] = (acc[item.className] ?? 0) + 1
                      return acc
                    }, {} as Record<string, number>),
                  ).map(([label, count]) => (
                    <div key={label} className="class-summary-row">
                      <span>{label}</span>
                      <strong>{count}</strong>
                    </div>
                  ))}
                </div>

                <div className="result-list">
                  {latestResult.detections.map((item, index) => (
                    <div key={`${item.className}-${index}`} className="result-item">
                      <span>{item.className}</span>
                      <strong>{item.confidence.toFixed(1)}%</strong>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="empty-state small-empty">No detection result yet.</div>
            )}
          </article>
        </div>
      </section>

      <section className="section-card summary-card">
        <div className="section-header compact">
          <h2>Detection Summary</h2>
        </div>

        {latestResult ? (
          <div className="summary-grid">
            <div><span>Source</span><strong>{latestResult.sourceFile}</strong></div>
            <div><span>Model</span><strong>{settings.model}</strong></div>
            <div><span>Processing Time</span><strong>{latestResult.processingTime.toFixed(2)} s</strong></div>
            <div><span>Total Vehicles</span><strong>{latestResult.totalVehicles}</strong></div>
            <div><span>Average Confidence</span><strong>{latestResult.averageConfidence.toFixed(1)}%</strong></div>
          </div>
        ) : (
          <div className="empty-state small-empty">Run detection to update the summary.</div>
        )}
      </section>

      {sourceModalOpen ? (
        <div className="modal-backdrop" onClick={() => setSourceModalOpen(false)}>
          <div className="confirm-modal source-modal" onClick={(event) => event.stopPropagation()}>
            <div className="modal-header">
              <div>
                <p className="eyebrow">Ready files</p>
                <h3>Select a source</h3>
              </div>
              <button type="button" className="close-btn" onClick={() => setSourceModalOpen(false)}>×</button>
            </div>

            {readyFiles.length === 0 ? (
              <div className="empty-state small-empty">No ready files available.</div>
            ) : (
              <div className="source-list">
                {readyFiles.map((file) => (
                  <button
                    key={file.id}
                    type="button"
                    className={`source-list-item ${selectedReadyFileId === file.id ? 'selected' : ''}`}
                    onClick={() => {
                      setSelectedReadyFileId(file.id)
                      setSourceMode('data')
                      setSourceModalOpen(false)
                    }}
                  >
                    <div className="source-icon">{file.fileType === 'video' ? '🎬' : '🖼️'}</div>
                    <div className="source-copy">
                      <strong>{file.fileName}</strong>
                      <span>{file.fileType.toUpperCase()} • {formatBytes(file.fileSize)} • Ready</span>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : null}
    </>
  )
}
