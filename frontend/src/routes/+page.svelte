<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  let mounted = false;
  
  onMount(() => {
    mounted = true;
  });
</script>

<div class="hero">
  <div class="route-lines">
    <svg class="route-svg" viewBox="0 0 1920 800">
      <path class="route-line red-line" d="M 0,200 Q 480,150 960,200 T 1920,200" />
      <path class="route-line blue-line" d="M 0,400 Q 480,450 960,400 T 1920,400" />
      <path class="route-line green-line" d="M 0,600 Q 480,550 960,600 T 1920,600" />
      <circle class="station-dot" cx="200" cy="200" r="8" />
      <circle class="station-dot" cx="500" cy="400" r="8" />
      <circle class="station-dot" cx="800" cy="600" r="8" />
      <circle class="station-dot" cx="1100" cy="200" r="8" />
      <circle class="station-dot" cx="1400" cy="400" r="8" />
      <circle class="station-dot" cx="1700" cy="600" r="8" />
    </svg>
  </div>
  <div class="floating-icons">
    <span class="float-icon" style="top: 10%; left: 10%;">🚇</span>
    <span class="float-icon" style="top: 20%; right: 15%;">🚌</span>
    <span class="float-icon" style="bottom: 15%; left: 20%;">⛴️</span>
    <span class="float-icon" style="bottom: 25%; right: 10%;">💻</span>
    <span class="float-icon" style="top: 40%; left: 5%;">🗺️</span>
    <span class="float-icon" style="top: 35%; right: 8%;">⚡</span>
  </div>
  <div class="hero-content" class:visible={mounted}>
    <h1 class="glitch-text">🚇 HK Smart Transport</h1>
    <p class="tagline typing-effect">Your intelligent guide to Hong Kong's public transport</p>
    <p class="description">
      Navigate Hong Kong with ease using our smart transport planner. Find routes, 
      discover nearby stations, and plan your journey across MTR, buses, and ferries.
    </p>
    <button class="cta-button pulse" on:click={() => goto('/route-planner')}>
      <span class="button-icon">▶</span> Get Started
    </button>
  </div>
</div>

<div class="features-wrapper">
  <div class="map-grid"></div>
  <div class="features">
  <div class="feature-card fade-in" on:click={() => goto('/route-planner')} on:keydown={(e) => e.key === 'Enter' && goto('/route-planner')} role="button" tabindex="0" style="animation-delay: 0.1s">
    <div class="feature-icon pulse-icon">🗺️</div>
    <h3>Route Planner</h3>
    <p>Plan your journey with multi-modal routes combining MTR, buses, and walking directions</p>
    <div class="card-accent"></div>
  </div>

  <div class="feature-card fade-in" on:click={() => goto('/nearby-stations')} on:keydown={(e) => e.key === 'Enter' && goto('/nearby-stations')} role="button" tabindex="0" style="animation-delay: 0.2s">
    <div class="feature-icon pulse-icon">📍</div>
    <h3>Nearby Stations</h3>
    <p>Find MTR stations, bus stops, and ferry piers near any location in Hong Kong</p>
    <div class="card-accent"></div>
  </div>

  <div class="feature-card fade-in" on:click={() => goto('/itinerary')} on:keydown={(e) => e.key === 'Enter' && goto('/itinerary')} role="button" tabindex="0" style="animation-delay: 0.3s">
    <div class="feature-icon pulse-icon">🤖</div>
    <h3>AI Itinerary</h3>
    <p>Let AI plan your day trip with optimized routes to multiple destinations</p>
    <div class="card-accent"></div>
  </div>

  <div class="feature-card fade-in" on:click={() => goto('/multi')} on:keydown={(e) => e.key === 'Enter' && goto('/multi')} role="button" tabindex="0" style="animation-delay: 0.4s">
    <div class="feature-icon pulse-icon">🚏</div>
    <h3>Multi-Stop Routing</h3>
    <p>Plan complex journeys with multiple stops and optimize your travel route</p>
    <div class="card-accent"></div>
  </div>
</div>
</div>

<div class="info-section slide-up" class:visible={mounted}>
  <h2>Why Choose HK Smart Transport?</h2>
  <div class="info-grid">
    <div class="info-item zoom-in" style="animation-delay: 0.5s">
      <span class="info-emoji bounce">⚡</span>
      <h4>Real-time Data</h4>
      <p>Access up-to-date transport information from official HK sources</p>
      <div class="code-line">{'> status: connected'}</div>
    </div>
    <div class="info-item zoom-in" style="animation-delay: 0.6s">
      <span class="info-emoji bounce">🎯</span>
      <h4>Smart Routes</h4>
      <p>Get the fastest and most efficient routes for your journey</p>
      <div class="code-line">{'> algorithm: optimized'}</div>
    </div>
    <div class="info-item zoom-in" style="animation-delay: 0.7s">
      <span class="info-emoji bounce">🗺️</span>
      <h4>Interactive Maps</h4>
      <p>Visual route planning with detailed maps and directions</p>
      <div class="code-line">{'> maps: interactive'}</div>
    </div>
  </div>
</div>

<div class="about-section slide-up" class:visible={mounted}>
  <div class="about-content">
    <div class="terminal-header">
      <span class="terminal-dot red"></span>
      <span class="terminal-dot yellow"></span>
      <span class="terminal-dot green"></span>
      <span class="terminal-title">project-info.md</span>
    </div>
    <h2>About This Project</h2>
    <p>
      Personal project making Hong Kong transport navigation easier. Combines MTR, buses, and ferries into one smart planner.
      <span class="cursor-blink">|</span>
    </p>
    <div class="tech-stack">
      <span class="tech-badge glow">SvelteKit</span>
      <span class="tech-badge glow">TypeScript</span>
      <span class="tech-badge glow">Python</span>
      <span class="tech-badge glow">FastAPI</span>
      <span class="tech-badge glow">Leaflet</span>
      <span class="tech-badge glow">OpenStreetMap</span>
    </div>
    
    <div class="developer-info">
      <div class="dev-avatar pulse">👨‍💻</div>
      <div class="dev-info-content">
        <h3>Mirza Usama Ikram</h3>
        <p class="dev-title">Full Stack Developer <span class="status-indicator">● Online</span></p>
        <div class="contact-links">
          <a href="https://github.com/mirzausamaikram" target="_blank" rel="noopener noreferrer" title="GitHub Profile" class="social-link">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
          </a>
          <a href="mailto:mirzausamaikram@gmail.com" title="Send Email" class="social-link">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
              <polyline points="22,6 12,13 2,6"/>
            </svg>
          </a>
        </div>
      </div>
      <a href="https://github.com/mirzausamaikram/hk-smart-transport" target="_blank" rel="noopener noreferrer" class="repo-link shine">
        <span class="button-icon">{'</>'}</span> View Source Code →
      </a>
    </div>
  </div>
</div>

<style>
  /* Animations */
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(50px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes zoomIn {
    from {
      opacity: 0;
      transform: scale(0.8);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }

  @keyframes float {
    0%, 100% {
      transform: translateY(0px);
    }
    50% {
      transform: translateY(-20px);
    }
  }

  @keyframes pulse {
    0%, 100% {
      transform: scale(1);
      box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
    }
    50% {
      transform: scale(1.05);
      box-shadow: 0 12px 32px rgba(59, 130, 246, 0.6);
    }
  }

  @keyframes bounce {
    0%, 100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(-10px);
    }
  }

  @keyframes glitch {
    0% {
      text-shadow: 2px 2px #ff00de, -2px -2px #00fff9;
    }
    25% {
      text-shadow: -2px -2px #ff00de, 2px 2px #00fff9;
    }
    50% {
      text-shadow: 2px -2px #ff00de, -2px 2px #00fff9;
    }
    75% {
      text-shadow: -2px 2px #ff00de, 2px -2px #00fff9;
    }
    100% {
      text-shadow: 2px 2px #ff00de, -2px -2px #00fff9;
    }
  }

  @keyframes blink {
    0%, 50%, 100% {
      opacity: 1;
    }
    25%, 75% {
      opacity: 0;
    }
  }

  @keyframes shine {
    0% {
      background-position: -200% center;
    }
    100% {
      background-position: 200% center;
    }
  }

  @keyframes glow {
    0%, 100% {
      box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    }
    50% {
      box-shadow: 0 4px 16px rgba(59, 130, 246, 0.6);
    }
  }

  .fade-in {
    opacity: 0;
    animation: fadeIn 0.8s ease-out forwards;
  }

  .slide-up {
    opacity: 0;
  }

  .slide-up.visible {
    animation: slideUp 0.8s ease-out forwards;
  }

  .zoom-in {
    opacity: 0;
    animation: zoomIn 0.6s ease-out forwards;
  }

  .pulse {
    animation: pulse 2s ease-in-out infinite;
  }

  .pulse-icon:hover {
    animation: bounce 0.5s ease;
  }

  .bounce {
    display: inline-block;
    animation: bounce 2s ease-in-out infinite;
  }

  .glitch-text:hover {
    animation: glitch 0.3s linear;
  }

  .cursor-blink {
    animation: blink 1s step-end infinite;
  }

  .shine {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 50%, #1e293b 100%);
    background-size: 200% auto;
    animation: shine 3s linear infinite;
  }

  .glow {
    animation: glow 2s ease-in-out infinite;
  }

  .floating-icons {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    overflow: hidden;
  }

  .float-icon {
    position: absolute;
    font-size: 2.5em;
    opacity: 0.15;
    animation: float 6s ease-in-out infinite;
  }

  .float-icon:nth-child(1) {
    animation-delay: 0s;
    animation-duration: 5s;
  }

  .float-icon:nth-child(2) {
    animation-delay: 1s;
    animation-duration: 7s;
  }

  .float-icon:nth-child(3) {
    animation-delay: 2s;
    animation-duration: 6s;
  }

  .float-icon:nth-child(4) {
    animation-delay: 0.5s;
    animation-duration: 8s;
  }

  .float-icon:nth-child(5) {
    animation-delay: 1.5s;
    animation-duration: 5.5s;
  }

  .float-icon:nth-child(6) {
    animation-delay: 2.5s;
    animation-duration: 6.5s;
  }

  .hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    color: white;
    padding: 80px 20px;
    text-align: center;
    margin: -25px -10px 40px -10px;
    position: relative;
    overflow: hidden;
  }

  .hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
      linear-gradient(rgba(59, 130, 246, 0.05) 1px, transparent 1px),
      linear-gradient(90deg, rgba(59, 130, 246, 0.05) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: float 20s linear infinite;
  }

  .route-lines {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    opacity: 0.3;
    z-index: 0;
  }

  .route-svg {
    width: 100%;
    height: 100%;
  }

  .route-line {
    fill: none;
    stroke-width: 4;
    stroke-linecap: round;
    animation: dashMove 20s linear infinite;
    stroke-dasharray: 10 5;
  }

  .red-line {
    stroke: #ef4444;
  }

  .blue-line {
    stroke: #3b82f6;
    animation-delay: 2s;
  }

  .green-line {
    stroke: #10b981;
    animation-delay: 4s;
  }

  .station-dot {
    fill: white;
    opacity: 0.6;
    animation: pulse 2s ease-in-out infinite;
  }

  @keyframes dashMove {
    0% {
      stroke-dashoffset: 0;
    }
    100% {
      stroke-dashoffset: 100;
    }
  }

  .hero-content {
    max-width: 800px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
    opacity: 0;
    transform: translateY(30px);
  }

  .hero-content.visible {
    animation: fadeIn 1s ease-out forwards;
  }

  .hero h1 {
    font-size: 3.5em;
    margin: 0 0 20px 0;
    font-weight: 700;
  }

  .tagline {
    font-size: 1.5em;
    margin: 0 0 20px 0;
    color: #cbd5e1;
  }

  .typing-effect {
    border-right: 1px solid #cbd5e1;
    white-space: nowrap;
    overflow: hidden;
    display: inline-block;
    animation: blink 2.5s step-end infinite;
  }


  .description {
    font-size: 1.1em;
    line-height: 1.6;
    color: #e2e8f0;
    margin: 0 0 40px 0;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
  }

  .cta-button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    padding: 16px 48px;
    font-size: 1.2em;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
    position: relative;
    overflow: hidden;
  }

  .cta-button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
  }

  .cta-button:hover::before {
    left: 100%;
  }

  .cta-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(59, 130, 246, 0.5);
  }

  .button-icon {
    display: inline-block;
    transition: transform 0.3s;
  }

  .cta-button:hover .button-icon {
    transform: translateX(5px);
  }

  .features-wrapper {
    position: relative;
    padding: 60px 0;
    background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    margin: 0 -10px;
  }

  .map-grid {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
      radial-gradient(circle, #cbd5e1 1px, transparent 1px),
      radial-gradient(circle, #cbd5e1 1px, transparent 1px);
    background-size: 40px 40px;
    background-position: 0 0, 20px 20px;
    opacity: 0.3;
    pointer-events: none;
  }

  .features {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 25px;
    margin: 0 auto;
    max-width: 1200px;
    padding: 0 20px;
    position: relative;
    z-index: 1;
  }

  .feature-card {
    background: white;
    padding: 10px;
    border-radius: 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    cursor: pointer;
    text-align: center;
    position: relative;
    overflow: hidden;
  }

  .feature-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
    border: 2px solid #3b82f6;
  }

  .card-accent {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
    transform: scaleX(0);
    transition: transform 0.3s ease;
  }

  .feature-card:hover .card-accent {
    transform: scaleX(1);
  }

  .feature-icon {
    font-size: 2.8em;
    margin-bottom: 12px;
  }

  .feature-card h3 {
    color: #1e293b;
    margin: 0 0 10px 0;
    font-size: 1.15em;
  }

  .feature-card p {
    color: #64748b;
    margin: 0;
    line-height: 1.5;
    font-size: 0.9em;
  }

  .info-section {
    max-width: 1200px;
    margin: 60px auto;
    padding: 40px 20px;
    text-align: center;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(139, 92, 246, 0.05) 50%, rgba(236, 72, 153, 0.05) 100%);
    border-radius: 24px;
    position: relative;
  }

  .info-section::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 24px;
    padding: 2px;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
    -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    opacity: 0.3;
  }

  .info-section h2 {
    font-size: 2.2em;
    color: #1e293b;
    margin-bottom: 40px;
  }

  .info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 30px;
  }

  .info-item {
    padding: 20px;
    background: linear-gradient(135deg, #f8fafc 0%, #fff 100%);
    border-radius: 16px;
    border: 1px solid #e2e8f0;
    transition: all 0.3s ease;
  }

  .info-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    border-color: #3b82f6;
  }

  .info-emoji {
    font-size: 3em;
    display: block;
    margin-bottom: 15px;
  }

  .info-item h4 {
    color: #1e293b;
    margin: 0 0 10px 0;
    font-size: 1.3em;
  }

  .info-item p {
    color: #64748b;
    margin: 0 0 10px 0;
    line-height: 1.6;
  }

  .code-line {
    font-family: 'Courier New', monospace;
    font-size: 0.85em;
    color: #10b981;
    background: #0f172a;
    padding: 5px 10px;
    border-radius: 4px;
    margin-top: 10px;
    text-align: left;
  }

  @media (max-width: 768px) {
    .hero h1 {
      font-size: 2.5em;
    }

    .tagline {
      font-size: 1.2em;
    }

    .features {
      grid-template-columns: 1fr;
    }

    .developer-info {
      flex-direction: column;
      text-align: center;
    }

    .dev-info-content {
      text-align: center;
    }

    .contact-links {
      justify-content: center;
    }
  }

  .about-section {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    padding: 60px 20px;
    margin-top: 40px;
    position: relative;
  }

  .about-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899, #3b82f6);
    background-size: 200% auto;
    animation: shine 3s linear infinite;
  }

  .about-content {
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
  }

  .terminal-header {
    background: #1e293b;
    padding: 10px 15px;
    border-radius: 8px 8px 0 0;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: -5px;
  }

  .terminal-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
  }

  .terminal-dot.red {
    background: #ef4444;
  }

  .terminal-dot.yellow {
    background: #f59e0b;
  }

  .terminal-dot.green {
    background: #10b981;
  }

  .terminal-title {
    color: #94a3b8;
    font-size: 0.85em;
    margin-left: auto;
    font-family: 'Courier New', monospace;
  }

  .about-content h2 {
    font-size: 2.2em;
    color: #1e293b;
    margin-bottom: 30px;
    margin-top: 20px;
  }

  .about-content p {
    font-size: 1.1em;
    line-height: 1.8;
    color: #475569;
    margin-bottom: 20px;
  }

  .tech-stack {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    justify-content: center;
    margin: 30px 0;
  }

  .tech-badge {
    background: white;
    color: #1e293b;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.95em;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
  }

  .tech-badge:hover {
    transform: translateY(-3px);
  }

  .developer-info {
    margin: 40px auto 0;
    padding: 20px 40px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    max-width: 600px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 25px;
    border: 2px solid transparent;
    transition: border-color 0.3s ease;
  }

  .developer-info:hover {
    border-color: #3b82f6;
  }

  .dev-avatar {
    font-size: 3.5em;
    margin: 0;
    flex-shrink: 0;
  }

  .dev-info-content {
    flex: 1;
    text-align: left;
  }

  .developer-info h3 {
    color: #1e293b;
    font-size: 1.3em;
    margin: 0 0 3px 0;
  }

  .dev-title {
    color: #64748b;
    font-size: 0.9em;
    margin: 0 0 15px 0;
  }

  .status-indicator {
    color: #10b981;
    font-size: 0.8em;
    margin-left: 5px;
  }

  .contact-links {
    display: flex;
    gap: 12px;
    justify-content: flex-start;
    flex-wrap: wrap;
    margin-bottom: 0;
  }

  .social-link {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    text-decoration: none;
    border-radius: 50%;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  }

  .social-link:hover {
    transform: translateY(-3px) scale(1.1) rotate(5deg);
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.5);
  }

  .contact-links svg {
    flex-shrink: 0;
  }

  .repo-link {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    color: white;
    text-decoration: none;
    font-weight: 600;
    font-size: 0.95em;
    border-radius: 8px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    flex-shrink: 0;
    position: relative;
    overflow: hidden;
  }

  .repo-link::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  }

  .repo-link:hover::after {
    left: 100%;
    transition: left 0.5s;
  }

  .repo-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    background: linear-gradient(135deg, #334155 0%, #1e293b 100%);
  }
</style>
