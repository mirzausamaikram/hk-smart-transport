<style>
  :global(body) {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
    background: #f8fafc;
    margin: 0;
    padding: 0;
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
  }

  nav a:hover {
    color: #fff;
    background: rgba(255,255,255,0.08);
    border-bottom-color: #3b82f6;
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
    padding: 10px 15px;
    border: none;
    background: #2563eb;
    color: white;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.95rem;
  }
  
  :global(button:hover) {
    background: #1e40af;
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
  <a href="/">Route Planner</a>
  <a href="/nearby-stations">Nearby Stations</a>
  <a href="/itinerary">AI Itinerary</a>
  <a href="/multi">Multi-Stop Routing</a>
</nav>


<main>
  <slot />
</main>
