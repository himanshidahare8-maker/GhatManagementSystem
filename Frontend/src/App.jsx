import './App.css'

function App() {
  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo-box">
          <div className="logo-icon">G</div>
          <div>
            <h2>GhatNetra</h2>
            <span>AI SAFETY SYSTEM</span>
          </div>
        </div>

        <nav>
          <button className="nav-item active">📊 Dashboard</button>
          <button className="nav-item">🎥 Live Monitoring</button>
          <button className="nav-item">📈 Analytics</button>
          <button className="nav-item">🚨 Alerts</button>
          <button className="nav-item">⚙️ Settings</button>
        </nav>

        <div className="system-status">
          <div className="status-dot"></div>
          <div>
            <strong>System Online</strong>
            <small>AI Engine Active</small>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main">
        <header className="topbar">
          <div>
            <h1>Ghat Management Dashboard</h1>
            <p>AI-powered crowd monitoring & safety decision support</p>
          </div>

          <div className="location">
            📍 River Ghat
            <span>● LIVE</span>
          </div>
        </header>

        {/* Stats */}
        <section className="stats-grid">
          <div className="stat-card">
            <span>Total Crowd</span>
            <strong>17</strong>
            <small>People detected</small>
          </div>

          <div className="stat-card">
            <span>Occupancy</span>
            <strong>3.8%</strong>
            <small className="safe">LOW</small>
          </div>

          <div className="stat-card">
            <span>Entry Gate</span>
            <strong className="open">OPEN</strong>
            <small>Normal entry</small>
          </div>

          <div className="stat-card">
            <span>Exit Gate</span>
            <strong className="open">OPEN</strong>
            <small>Normal exit</small>
          </div>
        </section>

        {/* Monitoring */}
        <section className="content-grid">
          <div className="panel video-panel">
            <div className="panel-header">
              <h2>🎥 Crowd Monitoring</h2>
              <span className="live-badge">LIVE ANALYSIS</span>
            </div>

            <div className="video-placeholder">
              <div className="camera-icon">🎥</div>
              <h3>AI Crowd Detection</h3>
              <p>YOLO detection stream will appear here</p>

              <div className="detection-box box-a">Zone A</div>
              <div className="detection-box box-b">Zone B</div>
              <div className="detection-box box-c">Zone C</div>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <h2>Zone Status</h2>
            </div>

            <div className="zone">
              <div>
                <strong>Zone A — Upper Entry</strong>
                <small>3 / 150 people</small>
              </div>
              <span className="low">LOW</span>
            </div>

            <div className="zone">
              <div>
                <strong>Zone B — Central Snan</strong>
                <small>10 / 200 people</small>
              </div>
              <span className="low">LOW</span>
            </div>

            <div className="zone">
              <div>
                <strong>Zone C — Waterfront</strong>
                <small>4 / 100 people</small>
              </div>
              <span className="low">LOW</span>
            </div>

            <div className="recommendation">
              <strong>✓ Current Recommendation</strong>
              <p>No diversion needed. Crowd level is within safe limits.</p>
            </div>
          </div>
        </section>

        {/* Bottom panels */}
        <section className="bottom-grid">
          <div className="panel">
            <div className="panel-header">
              <h2>🚪 Gate Control</h2>
            </div>

            <div className="gate-row">
              <span>Gate 1 — Entry</span>
              <button className="gate-open">OPEN</button>
            </div>

            <div className="gate-row">
              <span>Gate 2 — Exit</span>
              <button className="gate-open">OPEN</button>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <h2>⚠️ Alerts</h2>
            </div>

            <div className="no-alert">
              ✓ No active safety alerts
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <h2>🔮 Prediction</h2>
            </div>

            <p className="prediction">
              Crowd level is currently <strong>LOW</strong>.
            </p>
            <small>Prediction module will use historical data.</small>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App