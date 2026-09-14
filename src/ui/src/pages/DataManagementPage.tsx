import type { RefObject } from 'react'
import type { DataStatistics, UploadedFile } from '../services/api'
import { formatBytes } from '../utils/fileUtils'

type FileTypeFilter = 'all' | 'image' | 'video'
type StatusFilter = 'all' | UploadedFile['status']

type DataManagementPageProps = {
  statistics: DataStatistics
  files: UploadedFile[]
  searchTerm: string
  typeFilter: FileTypeFilter
  statusFilter: StatusFilter
  selectedFile: UploadedFile | null
  pendingDeleteId: string | null
  uploadError: string | null
  processingProgress: Record<string, number>
  fileInputRef: RefObject<HTMLInputElement | null>
  onSearchChange: (value: string) => void
  onTypeFilterChange: (value: FileTypeFilter) => void
  onStatusFilterChange: (value: StatusFilter) => void
  onBrowseClick: () => void
  onUploadFiles: (fileList: FileList | null) => void
  onPreprocess: (fileId: string) => void
  onRetry: (fileId: string) => void
  onDeleteRequest: (fileId: string) => void
  onDeleteConfirm: (fileId: string) => void
  onSelectFile: (item: UploadedFile) => void
  onClosePreview: () => void
  onCancelDelete: () => void
}

const getStatusColor = (status: UploadedFile['status']) => {
  switch (status) {
    case 'ready':
    case 'processed':
      return 'success'
    case 'processing':
      return 'warning'
    case 'pending':
      return 'neutral'
    case 'failed':
      return 'danger'
    default:
      return 'neutral'
  }
}

export function DataManagementPage({
  statistics,
  files,
  searchTerm,
  typeFilter,
  statusFilter,
  selectedFile,
  pendingDeleteId,
  uploadError,
  processingProgress,
  fileInputRef,
  onSearchChange,
  onTypeFilterChange,
  onStatusFilterChange,
  onBrowseClick,
  onUploadFiles,
  onPreprocess,
  onRetry,
  onDeleteRequest,
  onDeleteConfirm,
  onSelectFile,
  onClosePreview,
  onCancelDelete,
}: DataManagementPageProps) {
  const filteredFiles = files.filter((item) => {
    const query = searchTerm.trim().toLowerCase()
    const matchesSearch = !query || item.fileName.toLowerCase().includes(query)
    const matchesType = typeFilter === 'all' || item.fileType === typeFilter
    const matchesStatus = statusFilter === 'all' || item.status === statusFilter

    return matchesSearch && matchesType && matchesStatus
  })

  return (
    <>
      <section className="stats-grid data-stats-grid">
        <div className="stat-card blue">
          <div className="stat-card-topline">
            <span>Total Files</span>
            <span className="card-delta">Updated today</span>
          </div>
          <div className="stat-card-value">{String(statistics.totalFiles)}</div>
        </div>

        <div className="stat-card green">
          <div className="stat-card-topline">
            <span>Images</span>
            <span className="card-delta">Ready</span>
          </div>
          <div className="stat-card-value">{String(statistics.totalImages)}</div>
        </div>

        <div className="stat-card amber">
          <div className="stat-card-topline">
            <span>Videos</span>
            <span className="card-delta">In queue</span>
          </div>
          <div className="stat-card-value">{String(statistics.totalVideos)}</div>
        </div>

        <div className="stat-card gray">
          <div className="stat-card-topline">
            <span>Ready for Detection</span>
            <span className="card-delta">Available</span>
          </div>
          <div className="stat-card-value">{String(statistics.readyForDetection)}</div>
        </div>
      </section>

      <section className="content-grid split-2">
        <article className="section-card upload-card">
          <div className="section-header compact upload-header">
            <div>
              <p className="eyebrow">Input data</p>
              <h2>Upload Data</h2>
            </div>
          </div>

          <p className="upload-subtitle">Upload images or videos for vehicle detection.</p>
          <p className="upload-meta">Supported: JPG, JPEG, PNG, MP4 · Max size: 50 MB</p>

          <div
            className="upload-box"
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault()
              onUploadFiles(event.dataTransfer.files)
            }}
            onClick={onBrowseClick}
            role="button"
            tabIndex={0}
            onKeyDown={(event) => {
              if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault()
                onBrowseClick()
              }
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".jpg,.jpeg,.png,.mp4"
              multiple
              hidden
              onChange={(event) => onUploadFiles(event.target.files)}
            />
            <div className="upload-icon">+</div>
            <p>Drag and drop images or videos</p>
            <button
              type="button"
              className="primary-btn small"
              onClick={(event) => {
                event.stopPropagation()
                onBrowseClick()
              }}
            >
              Select files
            </button>
          </div>

          {uploadError ? <div className="error-message">{uploadError}</div> : null}
        </article>

        <article className="section-card">
          <div className="section-header compact">
            <h2>Recent Sources</h2>
          </div>

          <div className="file-toolbar">
            <input
              type="text"
              className="search-input"
              placeholder="Search files..."
              value={searchTerm}
              onChange={(event) => onSearchChange(event.target.value)}
            />

            <div className="filter-row">
              <select value={typeFilter} onChange={(event) => onTypeFilterChange(event.target.value as FileTypeFilter)}>
                <option value="all">All</option>
                <option value="image">Images</option>
                <option value="video">Videos</option>
              </select>

              <select value={statusFilter} onChange={(event) => onStatusFilterChange(event.target.value as StatusFilter)}>
                <option value="all">All</option>
                <option value="pending">Pending</option>
                <option value="processing">Processing</option>
                <option value="processed">Processed</option>
                <option value="ready">Ready</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>

          <div className="table-list">
            {filteredFiles.length === 0 ? (
              <div className="empty-state">No files match your current filters.</div>
            ) : (
              filteredFiles.map((item) => (
                <div key={item.id} className="list-row file-row">
                  <div className="file-main">
                    <div className="file-icon">{item.fileType === 'video' ? '🎬' : item.fileType === 'image' ? '🖼️' : '📄'}</div>
                    <div>
                      <strong>{item.fileName}</strong>
                      <span>{new Date(item.uploadedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                  </div>

                  <span className="file-size">{formatBytes(item.fileSize)}</span>

                  <div className="file-actions-wrap">
                    {item.status === 'processing' ? (
                      <div className="mini-progress">
                        <div className="mini-progress-bar" style={{ width: `${processingProgress[item.id] ?? 0}%` }} />
                      </div>
                    ) : null}
                    <span className={`status-pill ${getStatusColor(item.status)}`}>{item.status}</span>

                    <div className="action-buttons">
                      <button type="button" className="table-action" onClick={() => onSelectFile(item)}>
                        View
                      </button>
                      <button type="button" className="table-action" onClick={() => onPreprocess(item.id)}>
                        Preprocess
                      </button>
                      {item.status === 'failed' ? (
                        <button type="button" className="table-action" onClick={() => onRetry(item.id)}>
                          Retry
                        </button>
                      ) : null}
                      <button type="button" className="table-action danger" onClick={() => onDeleteRequest(item.id)}>
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </article>
      </section>

      {selectedFile ? (
        <div className="modal-backdrop" onClick={onClosePreview}>
          <div className="preview-modal" onClick={(event) => event.stopPropagation()}>
            <div className="modal-header">
              <div>
                <p className="eyebrow">File preview</p>
                <h3>{selectedFile.fileName}</h3>
              </div>
              <button type="button" className="close-btn" onClick={onClosePreview}>×</button>
            </div>

            <div className="preview-body">
              {selectedFile.fileType === 'image' && selectedFile.previewUrl ? (
                <img src={selectedFile.previewUrl} alt={selectedFile.fileName} className="preview-image" />
              ) : selectedFile.fileType === 'video' && selectedFile.previewUrl ? (
                <video src={selectedFile.previewUrl} controls className="preview-video" />
              ) : (
                <div className="preview-placeholder">{selectedFile.fileType === 'video' ? '🎬' : '📄'}</div>
              )}
            </div>

            <div className="preview-meta">
              <div><span>File Name</span><strong>{selectedFile.fileName}</strong></div>
              <div><span>File Type</span><strong>{selectedFile.fileType.toUpperCase()}</strong></div>
              <div><span>File Size</span><strong>{formatBytes(selectedFile.fileSize)}</strong></div>
              <div><span>Upload Time</span><strong>{new Date(selectedFile.uploadedAt).toLocaleString()}</strong></div>
              <div><span>Status</span><strong>{selectedFile.status}</strong></div>
            </div>

            <div className="modal-actions">
              <button type="button" className="primary-btn small" onClick={() => onPreprocess(selectedFile.id)}>
                Preprocess
              </button>
              <button type="button" className="secondary-btn small" onClick={() => onDeleteRequest(selectedFile.id)}>
                Delete
              </button>
              <button type="button" className="ghost-btn small" onClick={onClosePreview}>
                Close
              </button>
            </div>
          </div>
        </div>
      ) : null}

      {pendingDeleteId ? (
        <div className="modal-backdrop" onClick={onCancelDelete}>
          <div className="confirm-modal" onClick={(event) => event.stopPropagation()}>
            <h3>Delete file</h3>
            <p>Are you sure you want to delete this file?</p>
            <div className="modal-actions">
              <button type="button" className="secondary-btn small" onClick={onCancelDelete}>
                Cancel
              </button>
              <button type="button" className="primary-btn small" onClick={() => onDeleteConfirm(pendingDeleteId)}>
                Delete
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  )
}
