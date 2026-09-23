import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchData = () => {
    setLoading(true)
    setError(null)

    fetch('http://127.0.0.1:5000/api/status')
      .then(response => {
        if (!response.ok) {
          throw new Error('Backend API error')
        }
        return response.json()
      })
      .then(result => {
        setData(result)
        setLoading(false)
      })
      .catch(error => {
        console.error('API Error:', error)
        setError('Backend se data nahi mil raha.')
        setLoading(false)
      })
  }

  useEffect(() => {
    fetchData()
  }, [])

  // Loading screen
  if (loading) {
    return (
      <div className="loading">
        <div>
          <h1>GhatNetra AI</h1>
          <p>Connecting to AI Crowd Detection...</p>
        </div>
      </div>
    )
  }

  // Error screen
  if (error || !data) {
    return (
      <div className="loading">
        <div>
          <h1>GhatNetra AI</h1>
          <p>{error || 'No data available'}</p>

          <button
            onClick={fetchData}
            style={{
              marginTop: '15px',
              padding: '10px 18px',
              borderRadius: '8px',
              border: 'none',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  // API data
  const zoneA = data.zones?.['Zone A']
  const zoneB = data.zones?.['Zone B']
  const zoneC = data.zones?.['Zone C']

  return (
    <div className="app">

      {/* ================= SIDEBAR ================= */}

      <aside className="sidebar">

        <div className="logo-box">
          <div className="logo-icon">G</div>

          <div>
            <h2>GhatNetra</h2>
            <span>AI SAFETY SYSTEM</span>
          </div>
        </div>

        <nav>
          <button className="nav-item active">
            📊 Dashboard
          </button>

          <button className="nav-item">
            🎥 Live Monitoring
          </button>

          <button className="nav-item">
            📈 Analytics
          </button>

          <button className="nav-item">
            🚨 Alerts
          </button>

          <button className="nav-item">
            ⚙️ Settings
          </button>
        </nav>

        <div className="system-status">

          <div className="status-dot"></div>

          <div>
            <strong>System Online</strong>
            <small>AI Engine Active</small>
          </div>

        </div>

      </aside>


      {/* ================= MAIN ================= */}

      <main className="main">

        {/* TOP BAR */}

        <header className="topbar">

          <div>
            <h1>Ghat Management Dashboard</h1>

            <p>
              AI-powered crowd monitoring & safety decision support
            </p>
          </div>

          <div className="location">

            📍 River Ghat

            <span>● LIVE</span>

          </div>

        </header>


        {/* ================= STATS ================= */}

        <section className="stats-grid">

          {/* Total Crowd */}

          <div className="stat-card">

            <span>Total Crowd</span>

            <strong>
              {data.total_people}
            </strong>

            <small>
              People detected by YOLO
            </small>

          </div>


          {/* Occupancy */}

          <div className="stat-card">

            <span>Occupancy</span>

            <strong>
              {data.occupancy}%
            </strong>

            <small className="safe">
              {data.overall_status}
            </small>

          </div>


          {/* Entry Gate */}

          <div className="stat-card">

            <span>Entry Gate</span>

            <strong className="open">
              {data.gate_1?.split(' (')[0]}
            </strong>

            <small>
              {data.gate_1}
            </small>

          </div>


          {/* Exit Gate */}

          <div className="stat-card">

            <span>Exit Gate</span>

            <strong className="open">
              {data.gate_2?.split(' (')[0]}
            </strong>

            <small>
              {data.gate_2}
            </small>

          </div>

        </section>


        {/* ================= MONITORING ================= */}

        <section className="content-grid">


          {/* VIDEO PANEL */}

          <div className="panel video-panel">

            <div className="panel-header">

              <h2>
                🎥 Crowd Monitoring
              </h2>

              <span className="live-badge">
                YOLO ANALYSIS
              </span>

            </div>


            <div className="video-placeholder">

              <div className="camera-icon">
                🎥
              </div>

              <h3>
                AI Crowd Detection
              </h3>

              <p>
                YOLO detected {data.total_people} people
              </p>


              <div className="detection-box box-a">
                Zone A
              </div>

              <div className="detection-box box-b">
                Zone B
              </div>

              <div className="detection-box box-c">
                Zone C
              </div>

            </div>

          </div>


          {/* ZONE STATUS */}

          <div className="panel">

            <div className="panel-header">

              <h2>
                Zone Status
              </h2>

            </div>


            {/* Zone A */}

            <div className="zone">

              <div>

                <strong>
                  Zone A — Upper Entry
                </strong>

                <small>
                  {zoneA?.count} / {zoneA?.capacity} people
                  {' '}({zoneA?.occupancy}%)
                </small>

              </div>

              <span className="low">
                {zoneA?.status}
              </span>

            </div>


            {/* Zone B */}

            <div className="zone">

              <div>

                <strong>
                  Zone B — Central Snan
                </strong>

                <small>
                  {zoneB?.count} / {zoneB?.capacity} people
                  {' '}({zoneB?.occupancy}%)
                </small>

              </div>

              <span className="low">
                {zoneB?.status}
              </span>

            </div>


            {/* Zone C */}

            <div className="zone">

              <div>

                <strong>
                  Zone C — Waterfront
                </strong>

                <small>
                  {zoneC?.count} / {zoneC?.capacity} people
                  {' '}({zoneC?.occupancy}%)
                </small>

              </div>

              <span className="low">
                {zoneC?.status}
              </span>

            </div>


            {/* Recommendation */}

            <div className="recommendation">

              <strong>
                ✓ Current Recommendation
              </strong>

              <p>
                {data.alternate_route}
              </p>

            </div>

          </div>

        </section>


        {/* ================= BOTTOM PANELS ================= */}

        <section className="bottom-grid">


          {/* GATE CONTROL */}

          <div className="panel">

            <div className="panel-header">

              <h2>
                🚪 Gate Control
              </h2>

            </div>


            <div className="gate-row">

              <span>
                Gate 1 — Entry
              </span>

              <button className="gate-open">
                {data.gate_1?.split(' (')[0]}
              </button>

            </div>


            <div className="gate-row">

              <span>
                Gate 2 — Exit
              </span>

              <button className="gate-open">
                {data.gate_2?.split(' (')[0]}
              </button>

            </div>

          </div>


          {/* ALERTS */}

          <div className="panel">

            <div className="panel-header">

              <h2>
                ⚠️ Alerts
              </h2>

            </div>


            <div className="no-alert">

              ✓ No active safety alerts

            </div>


            <p className="prediction">

              Current status:
              {' '}
              <strong>
                {data.overall_status}
              </strong>

            </p>

          </div>


          {/* DECISION SUPPORT */}

          <div className="panel">

            <div className="panel-header">

              <h2>
                🧠 Decision Support
              </h2>

            </div>


            <p className="prediction">

              <strong>
                Evacuation Time:
              </strong>

              {' '}

              {data.evacuation_time} min

            </p>


            <p className="prediction">

              <strong>
                Security:
              </strong>

              {' '}

              {data.resource_action}

            </p>


            <small>
              AI decision generated from current crowd analysis.
            </small>

          </div>

        </section>


        {/* ================= FOOTER ACTIONS ================= */}

        <div
          style={{
            marginTop: '20px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}
        >

          <small style={{ color: '#78939a' }}>
            GhatNetra AI • YOLO + Python Backend
          </small>


          <button
            onClick={fetchData}
            style={{
              background: '#19c6bd',
              color: '#062027',
              border: 'none',
              padding: '10px 18px',
              borderRadius: '8px',
              fontWeight: 'bold',
              cursor: 'pointer'
            }}
          >
            🔄 Refresh Analysis
          </button>

        </div>

      </main>

    </div>
  )
}

export default App