import emailjs from "@emailjs/browser";
import { useEffect, useState } from 'react'
import './App.css'
import './Landing.css'


function HomePage({ onLogin }) {
  return (
    <div className="landing-page">
      <header className="landing-nav">
        <div className="landing-logo">
          <span className="landing-logo-mark">◢</span>
          <span>GhatNetra</span>
        </div>

        <nav className="landing-links">
          <a href="#home">Home</a>
          <a href="#about">About</a>
          <a href="#features">Features</a>
          <a href="#contact">Contact</a>
        </nav>

        <button className="landing-login" onClick={onLogin}>
          Login
        </button>
      </header>

      <section className="landing-hero" id="home">
        <div className="landing-copy">
          <div className="landing-tagline">
            AI Powered | Safer Ghats | Smarter Decisions
          </div>

          <h1>
            Ghat Crowd
            <br />
            <span>Management System</span>
          </h1>

          <p>
            Using AI and real-time analytics to monitor crowd movement,
            estimate occupancy, and provide decision support for safer,
            better-managed ghats.
          </p>

          <div className="landing-actions">
            <button className="landing-primary" onClick={onLogin}>
              Get Started
            </button>
            <a className="landing-secondary" href="#features">
              Learn More
            </a>
          </div>
        </div>

                <div className="landing-scene">
          <img
            src="/image.png"
            alt="Crowd Vision AI"
            className="crowd-vision-image"
          />
        </div>
      </section>

     <section className="landing-feature-section" id="features">
  <div className="section-heading">
    <small>OUR FEATURES</small>
    <h2>Smart technology for safer crowd management.</h2>
    <p>
      CrowdNetra uses AI, real-time monitoring and intelligent decision
      support to help authorities manage crowded public spaces efficiently.
    </p>
  </div>

  <div className="feature-cards">

    <div className="feature-card">
      <div className="big-feature-icon">👥</div>
      <h3>Real-time Crowd Monitoring</h3>
      <p>
        AI-powered camera analysis detects people and monitors crowd
        density in different zones.
      </p>
    </div>

    <div className="feature-card">
      <div className="big-feature-icon">📊</div>
      <h3>AI Based Prediction</h3>
      <p>
        Analyse crowd trends and provide prediction-based decision
        support for better planning.
      </p>
    </div>

    <div className="feature-card">
      <div className="big-feature-icon">🚪</div>
      <h3>Controlled Entry &amp; Exit</h3>
      <p>
        Monitor entry and exit conditions and support safer movement
        through crowd control recommendations.
      </p>
    </div>

    <div className="feature-card">
      <div className="big-feature-icon">🛡️</div>
      <h3>Safety &amp; Alerts</h3>
      <p>
        Identify high-density zones and support authorities with
        timely safety alerts.
      </p>
    </div>

    <div className="feature-card">
      <div className="big-feature-icon">🗺️</div>
      <h3>Ghat GIS &amp; Diversions</h3>
      <p>
        Visualize ghat zones and support safer route and diversion
        planning.
      </p>
    </div>

    <div className="feature-card">
      <div className="big-feature-icon">🔍</div>
      <h3>AI Lost Person Search</h3>
      <p>
        Assist in searching for a missing person using visual
        similarity analysis.
      </p>
    </div>

  </div>
</section>

<section className="landing-contact" id="contact">

  <div className="contact-heading">
    <small>CONTACT US</small>
    <h2>Let's make public spaces safer.</h2>
    <p>
      Have a question about CrowdNetra or want to know more about
      our crowd management system? Get in touch with us.
    </p>
  </div>

  <div className="contact-content">

    <div className="contact-info">

      <div className="contact-item">
        <span>📧</span>
        <div>
          <strong>Email</strong>
          <p>support@crowdnetra.ai</p>
        </div>
      </div>

      <div className="contact-item">
        <span>📍</span>
        <div>
          <strong>Location</strong>
          <p>Madhya Pradesh, India</p>
        </div>
      </div>

      <div className="contact-item">
        <span>🏢</span>
        <div>
          <strong>Organization</strong>
          <p>MPSTDC</p>
        </div>
      </div>

    </div>

   <div className="contact-card">
  <h3>Get in Touch</h3>

  <form
    onSubmit={(e) => {
      e.preventDefault()

      const form = e.currentTarget
      const name = form.name.value.trim()
      const email = form.email.value.trim()
      const message = form.message.value.trim()

      if (!name || !email || !message) {
        alert("Please fill in all fields.")
        return
      }

      if (!email.includes("@")) {
        alert("Please enter a valid email address.")
        return
      }

      alert("Message sent successfully!")

      form.reset()
    }}
  >

    <input
      type="text"
      name="name"
      placeholder="Your Name"
    />

    <input
      type="email"
      name="email"
      placeholder="Your Email"
    />

    <textarea
      name="message"
      placeholder="Your Message"
      rows="4"
    />

    <button type="submit">
      Send Message
    </button>

  </form>
</div>

  </div>

</section>

     <section className="landing-about-page" id="about">

  <div className="about-top">
    <small>SMART CROWD MANAGEMENT</small>

    <h2>
      Transforming <span>Ghat Safety</span>
    </h2>

    <p>
      AI-powered technology for safer, smarter and better-managed
      public spaces.
    </p>
  </div>

  <div className="about-content">

    <div className="about-image-card">
      <img
        src="/image.png"
        alt="CrowdNetra AI Crowd Monitoring"
      />
    </div>

    <div className="about-text">

      <h3>
        Revolutionizing <span>Crowd Management</span>
      </h3>

      <p>
        CrowdNetra combines computer vision, real-time monitoring
        and intelligent decision support to help authorities
        understand crowd density, movement and safety conditions.
      </p>

      <div className="about-info-card">
        <h4>AI-Powered Crowd Monitoring</h4>
        <p>
          AI-based camera analysis detects people and monitors
          crowd density across different zones in real time.
        </p>
      </div>

      <div className="about-info-card">
        <h4>Predictive Decision Support</h4>
        <p>
          Crowd trends and occupancy information help authorities
          plan safer entry, exit and crowd-control strategies.
        </p>
      </div>

      <div className="about-info-card">
        <h4>Safer Public Spaces</h4>
        <p>
          Zone monitoring, safety alerts and intelligent
          recommendations support faster response during crowded
          situations.
        </p>
      </div>

    </div>

  </div>

</section>
<section className="landing-contact-page" id="contact">

  <div className="contact-top">
    <small>GET IN TOUCH</small>

    <h2>
      Contact <span>CrowdNetra</span>
    </h2>

    <p>
      Connect with us for information, support and collaboration
      related to smart crowd management.
    </p>
  </div>

  <div className="contact-content">

    <div className="contact-image-card">
      <img
        src="/image.png"
        alt="CrowdNetra Contact"
      />
    </div>

    <div className="contact-details">

      <div className="contact-info-card">
        <div className="contact-icon">🏢</div>

        <div>
          <h3>Our Office</h3>

          <p>
            Madhya Pradesh, India
          </p>

          <p>
            Smart Ghat Management Project
          </p>
        </div>
      </div>


      <div className="contact-info-card">
        <div className="contact-icon">📞</div>

        <div>
          <h3>Get in Touch</h3>

          <p>
            Email: support@crowdnetra.ai
          </p>

          <p>
            Phone: +91 XXXXX XXXXX
          </p>
        </div>
      </div>


      <div className="contact-info-card">
        <div className="contact-icon">🤖</div>

        <div>
          <h3>AI Support</h3>

          <p>
            Ask about crowd monitoring, zones, safety,
            gates and decision support.
          </p>
        </div>
      </div>

    </div>

  </div>


  <div className="contact-support">

    <div>
      <h2>Need assistance?</h2>

      <p>
        Our smart crowd management system helps authorities
        monitor and respond to crowd situations efficiently.
      </p>
    </div>

    <a href="#home">
      Back to Home
    </a>

  </div>

</section>

      <footer id="contact">
        <strong>◢ GhatNetra</strong>
        <span>Safer Ghats • Smarter Decisions • A Better Tomorrow</span>
      </footer>
    </div>
  )
}

function LoginPage({ onBack, onSuccess }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')

  const handleLogin = (event) => {
    event.preventDefault()

    if (!username.trim() || !password) {
      setMessage('Please enter username and password.')
      return
    }

    setMessage('')
    onSuccess()
  }

  return (
    <div className="login-screen">
      <div className="login-left">
        <button className="login-brand" onClick={onBack}>
          <span>◢</span> GhatNetra
        </button>

        <div className="login-intro">
          <h1>GhatNetra</h1>
          <p>AI Ghat Crowd Management System</p>
          <div className="login-quote">
            “Technology for safer
            <br />
            and better ghats.”
          </div>
          <div className="login-art">⌁ &nbsp; ॐ &nbsp; ⌁</div>
        </div>
      </div>

      <div className="login-right">
        <form className="login-card" onSubmit={handleLogin}>
          <h2>Welcome Back</h2>
          <p>Login to your account</p>

          <label>Email / Username</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter your email or username"
          />

          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
          />

          <div className="login-options">
            <span>□ Remember me</span>
            <span>Forgot password?</span>
          </div>

          <button className="login-submit" type="submit">
            Login
          </button>

          {message && <div className="login-message">{message}</div>}

          <div className="login-note">
            Don't have an account? &nbsp; Contact admin
          </div>
        </form>

        <button className="back-home" onClick={onBack}>
          ← Back to Home
        </button>
      </div>
    </div>
  )
}

function App() {
  const [page, setPage] = useState('home')

  if (page === 'home') {
    return <HomePage onLogin={() => setPage('login')} />
  }

  if (page === 'login') {
    return (
      <LoginPage
        onBack={() => setPage('home')}
        onSuccess={() => {
          window.location.href = 'http://localhost:8501'
        }}
      />
    )
  }

  return <Dashboard />
}

export default App


function Dashboard() {
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