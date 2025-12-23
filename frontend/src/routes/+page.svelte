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
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 25px;
    margin: 40px auto;
    max-width: 1200px;
    padding: 0 20px;
  }

  .feature-card {
    background: white;
    padding: 30px;
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
    font-size: 3.5em;
    margin-bottom: 15px;
  }

  .feature-card h3 {
    color: #1e293b;
    margin: 0 0 12px 0;
    font-size: 1.4em;
  }

  .feature-card p {
    color: #64748b;
    margin: 0;
    line-height: 1.6;
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
</style>
