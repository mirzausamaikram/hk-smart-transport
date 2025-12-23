<style>
  nav {
    background: #0f172a;
    padding: 12px 20px;
    display: flex;
    gap: 20px;
  }

  nav a {
    color: #e2e8f0;
    text-decoration: none;
    font-size: 1rem;
  }

  nav a:hover {
    color: white;
  }

  main {
    max-width: 900px;
    margin: 20px auto;
    padding: 0 15px;
  }
  :global(body) {
    font-family: "Inter", sans-serif;
    background: #f3f4f6;
  }

  nav {
    background: #0f172a;
    padding: 14px 20px;
    display: flex;
    gap: 25px;
    align-items: center;
  }

  nav a {
    color: #cbd5e1;
    text-decoration: none;
    font-size: 1rem;
    font-weight: 500;
  }

  nav a:hover {
    color: #fff;
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
