import type { DataStatistics, UploadedFile } from '../services/api'

export const formatBytes = (size: number): string => {
  if (size < 1024) {
    return `${size} B`
  }

  const units = ['KB', 'MB', 'GB']
  let value = size / 1024
  let unitIndex = 0

  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024
    unitIndex += 1
  }

  return `${value.toFixed(value >= 10 ? 0 : 1)} ${units[unitIndex]}`
}

export const getFileType = (fileName: string): UploadedFile['fileType'] => {
  const extension = fileName.split('.').pop()?.toLowerCase() ?? ''

  if (extension === 'mp4') {
    return 'video'
  }

  if (['jpg', 'jpeg', 'png'].includes(extension)) {
    return 'image'
  }

  return 'file'
}

export const buildDataStatistics = (items: UploadedFile[]): DataStatistics => ({
  totalFiles: items.length,
  totalImages: items.filter((item) => item.fileType === 'image').length,
  totalVideos: items.filter((item) => item.fileType === 'video').length,
  readyForDetection: items.filter((item) => item.status === 'ready' || item.status === 'processed').length,
})
