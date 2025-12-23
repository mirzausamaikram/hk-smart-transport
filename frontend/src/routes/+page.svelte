<script lang="ts">
  import { goto } from '$app/navigation';
</script>

<div class="hero">
  <div class="hero-content">
    <h1>🚇 HK Smart Transport</h1>
    <p class="tagline">Your intelligent guide to Hong Kong's public transport</p>
    <p class="description">
      Navigate Hong Kong with ease using our smart transport planner. Find routes, 
      discover nearby stations, and plan your journey across MTR, buses, and ferries.
    </p>
    <button class="cta-button" on:click={() => goto('/route-planner')}>
      Get Started →
    </button>
  </div>
</div>

<div class="features">
  <div class="feature-card" on:click={() => goto('/route-planner')} on:keydown={(e) => e.key === 'Enter' && goto('/route-planner')} role="button" tabindex="0">
    <div class="feature-icon">🗺️</div>
    <h3>Route Planner</h3>
    <p>Plan your journey with multi-modal routes combining MTR, buses, and walking directions</p>
  </div>

  <div class="feature-card" on:click={() => goto('/nearby-stations')} on:keydown={(e) => e.key === 'Enter' && goto('/nearby-stations')} role="button" tabindex="0">
    <div class="feature-icon">📍</div>
    <h3>Nearby Stations</h3>
    <p>Find MTR stations, bus stops, and ferry piers near any location in Hong Kong</p>
  </div>

  <div class="feature-card" on:click={() => goto('/itinerary')} on:keydown={(e) => e.key === 'Enter' && goto('/itinerary')} role="button" tabindex="0">
    <div class="feature-icon">🤖</div>
    <h3>AI Itinerary</h3>
    <p>Let AI plan your day trip with optimized routes to multiple destinations</p>
  </div>

  <div class="feature-card" on:click={() => goto('/multi')} on:keydown={(e) => e.key === 'Enter' && goto('/multi')} role="button" tabindex="0">
    <div class="feature-icon">🚏</div>
    <h3>Multi-Stop Routing</h3>
    <p>Plan complex journeys with multiple stops and optimize your travel route</p>
  </div>
</div>

<div class="info-section">
  <h2>Why Choose HK Smart Transport?</h2>
  <div class="info-grid">
    <div class="info-item">
      <span class="info-emoji">⚡</span>
      <h4>Real-time Data</h4>
      <p>Access up-to-date transport information from official HK sources</p>
    </div>
    <div class="info-item">
      <span class="info-emoji">🎯</span>
      <h4>Smart Routes</h4>
      <p>Get the fastest and most efficient routes for your journey</p>
    </div>
    <div class="info-item">
      <span class="info-emoji">🗺️</span>
      <h4>Interactive Maps</h4>
      <p>Visual route planning with detailed maps and directions</p>
    </div>
  </div>
</div>

<div class="about-section">
  <div class="about-content">
    <h2>About This Project</h2>
    <p>
      Personal project making Hong Kong transport navigation easier. Combines MTR, buses, and ferries into one smart planner.
    </p>
    <div class="tech-stack">
      <span class="tech-badge">SvelteKit</span>
      <span class="tech-badge">TypeScript</span>
      <span class="tech-badge">Python</span>
      <span class="tech-badge">FastAPI</span>
      <span class="tech-badge">Leaflet</span>
      <span class="tech-badge">OpenStreetMap</span>
    </div>
    
    <div class="developer-info">
      <div class="dev-avatar">👨‍💻</div>
      <div class="dev-info-content">
        <h3>Mirza Usama Ikram</h3>
        <p class="dev-title">Full Stack Developer</p>
        <div class="contact-links">
          <a href="https://github.com/mirzausamaikram" target="_blank" rel="noopener noreferrer" title="GitHub Profile">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
          </a>
          <a href="mailto:mirzausamaikram@gmail.com" title="Send Email">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
              <polyline points="22,6 12,13 2,6"/>
            </svg>
          </a>
        </div>
      </div>
      <a href="https://github.com/mirzausamaikram/hk-smart-transport" target="_blank" rel="noopener noreferrer" class="repo-link">
        View Source Code →
      </a>
    </div>
  </div>
</div>

<style>
  .hero {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    color: white;
    padding: 80px 20px;
    text-align: center;
    margin: -25px -10px 40px -10px;
  }

  .hero-content {
    max-width: 800px;
    margin: 0 auto;
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
  }

  .cta-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px rgba(59, 130, 246, 0.5);
  }

  .features {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 25px;
    margin: 40px auto;
    max-width: 1200px;
    padding: 0 20px;
  }

  .feature-card {
    background: white;
    padding: 10px;
    border-radius: 16px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    cursor: pointer;
    text-align: center;
  }

  .feature-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
    border: 2px solid #3b82f6;
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
    margin: 0;
    line-height: 1.6;
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
  }

  .about-section {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    padding: 60px 20px;
    margin-top: 40px;
  }

  .about-content {
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
  }

  .about-content h2 {
    font-size: 2.2em;
    color: #1e293b;
    margin-bottom: 30px;
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
  }

  .github-link {
    margin-top: 30px;
    font-size: 1.1em;
  }

  .github-link a {
    color: #3b82f6;
    text-decoration: none;
    font-weight: 600;
    border-bottom: 2px solid transparent;
    transition: border-color 0.2s;
  }

  .github-link a:hover {
    border-bottom-color: #3b82f6;
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

  .dev-name {
    font-size: 1.3em;
    font-weight: 600;
    color: #3b82f6;
    margin-bottom: 20px;
  }

  .contact-links {
    display: flex;
    gap: 12px;
    justify-content: flex-start;
    flex-wrap: wrap;
    margin-bottom: 0;
  }

  .contact-links a {
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

  .contact-links a:hover {
    transform: translateY(-3px) scale(1.1);
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
  }

  .repo-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    background: linear-gradient(135deg, #334155 0%, #1e293b 100%);
  }

  .repo-link::before {
    content: "⭐";
    font-size: 1.1em;
  }

  .github-repo {
    margin-top: 30px;
    font-size: 1em;
    color: #64748b;
  }

  .github-repo a {
    color: #3b82f6;
    text-decoration: none;
    font-weight: 600;
    border-bottom: 2px solid transparent;
    transition: border-color 0.2s;
  }

  .github-repo a:hover {
    border-bottom-color: #3b82f6;
  }
</style>
