<style>
  @keyframes driftDown {
    from {
      background-position: 0 0, 0 0;
    }
    to {
      background-position: 0 600px, 0 800px;
    }
  }

  :global(body) {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
    background: radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.08), transparent 30%),
      radial-gradient(circle at 80% 10%, rgba(236, 72, 153, 0.08), transparent 32%),
      radial-gradient(circle at 50% 80%, rgba(16, 185, 129, 0.08), transparent 28%),
      linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f8fafc 100%);
    background-attachment: fixed;
    margin: 0;
    padding: 0;
    position: relative;
    overflow-x: hidden;
  }

  :global(body)::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
      radial-gradient(2px 2px at 20% 20%, rgba(255, 255, 255, 0.45), transparent 55%),
      radial-gradient(2px 2px at 80% 30%, rgba(255, 255, 255, 0.35), transparent 55%);
    background-repeat: repeat;
    background-size: 220px 220px, 320px 320px;
    animation: driftDown 18s linear infinite;
    opacity: 0.5;
    z-index: 0;
  }

  nav {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    padding: 0;
    display: flex;
    gap: 0;
    align-items: stretch;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  }

  nav a {
    color: #cbd5e1;
    text-decoration: none;
    font-size: 0.95rem;
    font-weight: 500;
    padding: 18px 28px;
    transition: all 0.2s ease;
    border-bottom: 3px solid transparent;
    white-space: nowrap;
  }

  nav a:hover {
    color: #fff;
    background: rgba(255,255,255,0.08);
    border-bottom-color: #3b82f6;
  }

  nav a:active {
    color: #fff;
    background: rgba(59, 130, 246, 0.2);
    border-bottom-color: #60a5fa;
  }

  main {
    max-width: 950px;
    margin: 25px auto;
    padding: 10px;
  }

  :global(.card) {
    background: white;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 4px 18px rgba(0,0,0,0.07);
    margin-bottom: 20px;
  }

  :global(button) {
    padding: 12px 24px;
    border: none;
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border-radius: 10px;
    cursor: pointer;
    font-size: 0.95rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
  }

  :global(button:hover) {
    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
  }

  :global(button:active) {
    transform: translateY(0);
  }

  :global(input), :global(textarea) {
    width: 100%;
    padding: 8px 10px;
    border-radius: 8px;
    border: 1px solid #d1d5db;
    margin-bottom: 10px;
  }
</style>

<nav>
  <a href="/">🏠 Home</a>
  <a href="/route-planner">🗺️ Route Planner</a>
  <a href="/nearby-stations">📍 Nearby Stations</a>
  <a href="/itinerary">🤖 AI Itinerary</a>
  <a href="/multi">🚏 Multi-Stop</a>
</nav>


<main>
  <slot />
</main>
