import { useState } from 'react'
import './App.css'
import { Header } from './components/Header'
import { MetricBar } from './components/MetricBar'
import { Sidebar } from './components/Sidebar'
import { StatCard } from './components/StatCard'

const navItems = [
  'Data Management',
  'Vehicle Detection',
  'System Information',
  'Reports',
  'Settings',
]

const fileRows = [
  { name: 'traffic_lane_01.jpg', time: '08:42', status: 'Processed', size: '2.4 MB' },
  { name: 'city_entrance.mp4', time: '09:15', status: 'Processing', size: '18.1 MB' },
  { name: 'parking_area_02.jpg', time: '10:30', status: 'Failed', size: '1.7 MB' },
]

const detectionRows = [
  { id: 'V-1042', vehicle: 'Sedan', confidence: 96, zone: 'North gate', time: '09:12:35' },
  { id: 'V-1043', vehicle: 'Truck', confidence: 92, zone: 'Inbound lane', time: '09:12:55' },
  { id: 'V-1044', vehicle: 'Van', confidence: 95, zone: 'South gate', time: '09:13:12' },
]

const systemCards = [
  { label: 'AI model', value: 'YOLOv8n', detail: 'Optimized detection pipeline' },
  { label: 'Backend', value: 'FastAPI', detail: 'REST API layer ready' },
  { label: 'Data source', value: 'Camera + Upload', detail: 'Image and video support' },
  { label: 'Processing', value: 'Real-time', detail: 'Average 220 ms / frame' },
]

const reportRows = [
  { date: '2025-07-14', file: 'city_morning.mp4', type: 'Video', total: 184, runtime: '03:44', status: 'Completed' },
  { date: '2025-07-14', file: 'lot_a_01.jpg', type: 'Image', total: 42, runtime: '00:52', status: 'Completed' },
  { date: '2025-07-13', file: 'night_shift.mp4', type: 'Video', total: 217, runtime: '05:11', status: 'Processing' },
]

const detectionBars = [68, 81, 74, 89, 76, 92, 88]

const metrics = [
  { label: 'Vehicles detected', value: '14,892', delta: '+12.4%', tone: 'blue' },
  { label: 'Average confidence', value: '96.8%', delta: '+2.1%', tone: 'green' },
  { label: 'Alerts requiring review', value: '47', delta: '5 new', tone: 'amber' },
]

function App() {
  const [activePage, setActivePage] = useState('Data Management')

  const renderPage = () => {
    if (activePage === 'Vehicle Detection') {
      return (
        <>
          <section className="stats-grid three-up">
            {metrics.map((metric) => (
              <StatCard
                key={metric.label}
                label={metric.label}
                value={metric.value}
                delta={metric.delta}
                tone={metric.tone as 'blue' | 'green' | 'amber' | 'gray'}
              />
            ))}
          </section>

          <section className="content-grid split-2">
            <article className="section-card large">
              <div className="section-header">
                <div>
                  <p className="eyebrow">Live detection</p>
                  <h2>Camera feed overview</h2>
                </div>
                <button type="button" className="secondary-btn small">
                  Refresh
                </button>
              </div>

              <div className="preview-panel">
                <div className="camera-overlay">
                  <span className="status-dot green" />
                  Streaming
                </div>
              </div>
            </article>

            <article className="section-card">
              <div className="section-header compact">
                <h2>Detection quality</h2>
              </div>

              <div className="metric-stack">
                <MetricBar label="Vehicle recognition" value={96} color="#2563eb" />
                <MetricBar label="Vehicle type" value={92} color="#10b981" />
                <MetricBar label="Traffic flow" value={88} color="#f59e0b" />
                <MetricBar label="Safety scoring" value={90} color="#8b5cf6" />
              </div>
            </article>
          </section>

          <section className="bottom-grid two-panel">
            <article className="section-card">
              <div className="section-header compact">
                <h2>Latest detections</h2>
                <span>Last 3 minutes</span>
              </div>

              <div className="table-list detections">
                {detectionRows.map((row) => (
                  <div key={row.id} className="list-row detection-row">
                    <div>
                      <strong>{row.id}</strong>
                      <span>{row.vehicle}</span>
                    </div>
                    <div>
                      <strong>{row.zone}</strong>
                      <span>{row.time}</span>
                    </div>
                    <div className="confidence-badge">{row.confidence}%</div>
                  </div>
                ))}
              </div>
            </article>

            <article className="section-card">
              <div className="section-header compact">
                <h2>Flow by hour</h2>
                <span>24h</span>
              </div>

              <div className="chart-bars" aria-label="Traffic flow chart">
                {detectionBars.map((value, index) => (
                  <div key={value + index} className="bar-column">
                    <span className="bar-fill" style={{ height: `${value}%` }} />
                    <label>{['00h', '04h', '08h', '12h', '16h', '20h', '24h'][index]}</label>
                  </div>
                ))}
              </div>
            </article>
          </section>
        </>
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
            <button type="button" className="primary-btn small">
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
                {reportRows.map((row) => (
                  <tr key={`${row.date}-${row.file}`}>
                    <td>{row.date}</td>
                    <td>{row.file}</td>
                    <td>{row.type}</td>
                    <td>{row.total}</td>
                    <td>{row.runtime}</td>
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
              <h2>Detection settings</h2>
            </div>

            <div className="field-group">
              <label>
                Model version
                <select defaultValue="YOLOv8n">
                  <option>YOLOv8n</option>
                  <option>YOLOv8s</option>
                  <option>YOLOv8m</option>
                </select>
              </label>

              <label>
                Confidence threshold
                <input type="range" defaultValue={78} />
              </label>

              <label>
                Input mode
                <select defaultValue="Camera + image">
                  <option>Camera + image</option>
                  <option>Image only</option>
                  <option>Video only</option>
                </select>
              </label>
            </div>
          </article>

          <article className="section-card">
            <div className="section-header compact">
              <h2>Integration</h2>
            </div>

            <div className="field-group">
              <label>
                API base URL
                <input defaultValue="http://localhost:8000/api" />
              </label>

              <label>
                Max file size
                <input defaultValue="50 MB" />
              </label>

              <label>
                Supported formats
                <input defaultValue=".jpg, .png, .mp4" />
              </label>
            </div>
          </article>
        </section>
      )
    }

    return (
      <>
        <section className="stats-grid three-up">
          {metrics.map((metric) => (
            <StatCard
              key={metric.label}
              label={metric.label}
              value={metric.value}
              delta={metric.delta}
              tone={metric.tone as 'blue' | 'green' | 'amber' | 'gray'}
            />
          ))}
        </section>

        <section className="content-grid split-2">
          <article className="section-card">
            <div className="section-header compact">
              <div>
                <p className="eyebrow">Upload queue</p>
                <h2>Data management</h2>
              </div>
            </div>

            <div className="upload-box">
              <div className="upload-icon">+</div>
              <p>Drag and drop images or videos</p>
              <button type="button" className="primary-btn small">
                Select files
              </button>
            </div>
          </article>

          <article className="section-card">
            <div className="section-header compact">
              <h2>Recent sources</h2>
            </div>

            <div className="table-list">
              {fileRows.map((row) => (
                <div key={row.name} className="list-row file-row">
                  <div>
                    <strong>{row.name}</strong>
                    <span>{row.time}</span>
                  </div>
                  <span className="file-size">{row.size}</span>
                  <span className={`status-pill ${row.status.toLowerCase()}`}>{row.status}</span>
                </div>
              ))}
            </div>
          </article>
        </section>
      </>
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
        />

        {renderPage()}
      </main>
    </div>
  )
}

export default App
