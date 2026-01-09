<script lang="ts">
  import SearchBar from "$lib/components/SearchBar.svelte";
  import LeafletMap from "$lib/components/LeafletMap.svelte";
  import { page } from "$app/stores";
  import { onMount } from "svelte";

  // Types
  type Place = { name: string; lat: number; lng: number };
  type LatLng = { lat: number; lng: number };
  type Marker = { lat: number; lng: number; title: string; color: string };
  type Instruction = { type: string; instruction: string; distance_m: number; duration_s?: number };
  type TransitOption = { type: string; stop_name: string; instruction: string; stop_lat: number; stop_lng: number };
  type RouteStep = { type: string; instruction: string; distance_m?: number; duration_min: number; action?: string; bus_number?: string; get_off_at?: string; exit_info?: string };
  type RouteOption = { option_name: string; total_duration_min: number; steps: RouteStep[] };

  // State
  let start: Place | null = null;
  let end: Place | null = null;
  let startName = "";
  let endName = "";
  let markers: Marker[] = [];
  let polyline: LatLng[] = [];
  let instructions: Instruction[] = [];
  let transitOptions: TransitOption[] = [];
  let showInstructions = false;
  let selectedTransit: TransitOption | null = null;
  let routeOptions: RouteOption[] = [];
  let selectedRouteOption: RouteOption | null = null;
  let walkOnly = false;
  let collapsedSections: { [key: string]: boolean } = {
    routeOptions: false,
    detailedRoute: false,
    walking: false
  };
  let navigationMode = false;
  let currentStep = 0;
  let recentLocations: Place[] = [];
  let distance = 0;
  let duration = 0;
  let showAllRoutes = false;
  let refreshInterval: number | null = null;
  let lastRefreshTime = Date.now();

  // Constants
  const API_BASE = "http://127.0.0.1:8000/api/route";
  
  // MTR Line Colors
  const MTR_LINE_COLORS: { [key: string]: string } = {
    'Tsuen Wan Line': '#E2231A',
    'Island Line': '#0860A8',
    'Kwun Tong Line': '#00A54F',
    'Tuen Mun Line': '#9B2E87',
    'Tung Chung Line': '#F48221',
    'East Rail Line': '#5EB7E8',
    'South Island Line': '#CBCD00',
    'Disneyland Resort Line': '#F173AC',
    'Airport Express': '#007A70',
  };
  
  // Get MTR line color from stop name
  function getMTRLineColor(stopName: string): string {
    // Try to detect line from stop name or return default
    for (const [line, color] of Object.entries(MTR_LINE_COLORS)) {
      // This is a simplified check - in production you'd query actual line info
      if (stopName.includes(line.split(' ')[0])) return color;
    }
    return '#0860A8'; // Default to Island Line blue
  }

  // Parse URL params and populate fields on mount
  onMount(() => {
    // Load recent locations from localStorage
    const saved = localStorage.getItem('recentLocations');
    if (saved) {
      try {
        recentLocations = JSON.parse(saved);
      } catch (e) {
        recentLocations = [];
      }
    }
    
    const params = $page.url.searchParams;
    
    // Read coordinates directly from URL params
    const fromLat = params.get('fromLat');
    const fromLng = params.get('fromLng');
    const fromName = params.get('fromName');
    const toLat = params.get('toLat');
    const toLng = params.get('toLng');
    const toName = params.get('toName');
    const walkOnlyParam = params.get('walkOnly');
    const fromParam = params.get('from');
    const toParam = params.get('to');

    // Walk-only mode: hide transit sections and focus on walking
    if (walkOnlyParam && (walkOnlyParam === '1' || walkOnlyParam.toLowerCase() === 'true')) {
      walkOnly = true;
    }

    if (fromLat && fromLng) {
      const lat = parseFloat(fromLat);
      const lng = parseFloat(fromLng);
      if (!isNaN(lat) && !isNaN(lng)) {
        start = { name: fromName || "Selected Location", lat, lng };
        startName = fromName || "Selected Location";
      }
    }

    if (toLat && toLng) {
      const lat = parseFloat(toLat);
      const lng = parseFloat(toLng);
      if (!isNaN(lat) && !isNaN(lng)) {
        end = { name: toName || "Destination", lat, lng };
        endName = toName || "Destination";
      }
    }

    if (fromParam && !start) {
      // from param is "lat,lng" format
      const [lat, lng] = fromParam.split(',').map(Number);
      if (!isNaN(lat) && !isNaN(lng)) {
        start = { name: "Selected Location", lat, lng };
        startName = "Selected Location";
      }
    }

    if (toParam && !end) {
      // to param is the station name (we'll geocode it or use it as is)
      endName = toParam;
      // Try to fetch coordinates for this station name via the geocode API
      fetch(`http://127.0.0.1:8000/api/geocode/?query=${encodeURIComponent(toParam)}`)
        .then(res => res.json())
        .then(data => {
          if (data && data.lat && data.lng) {
            end = { name: toParam, lat: data.lat, lng: data.lng };
            endName = toParam;
            updateMarkers();
            // Auto-trigger route if both start and end are set
            if (start && end) {
              setTimeout(() => getRoute(), 500);
            }
          }
        })
        .catch(err => console.warn('Could not geocode destination:', err));
    }

    updateMarkers();
    
    // Auto-trigger route if both start and end are set
    if (start && end) {
      setTimeout(() => getRoute(), 500);
    }
    
    // Start auto-refresh for transit ETAs (every 60 seconds)
    startAutoRefresh();
    
    // Cleanup on unmount
    return () => {
      stopAutoRefresh();
    };
  });
  
  // Auto-refresh transit ETAs
  function startAutoRefresh() {
    if (refreshInterval) return; // Already running
    refreshInterval = window.setInterval(() => {
      if (selectedTransit && routeOptions.length > 0) {
        // Silently refresh transit details
        getTransitDetails(selectedTransit, true);
        lastRefreshTime = Date.now();
      }
    }, 60000); // 60 seconds
  }
  
  function stopAutoRefresh() {
    if (refreshInterval) {
      clearInterval(refreshInterval);
      refreshInterval = null;
    }
  }

  // Update markers on map
  function updateMarkers() {
    markers = [];
    if (start) markers.push({ ...start, title: "Start", color: "#4CAF50" });
    if (end) markers.push({ ...end, title: "Destination", color: "#FF5722" });
  }

  // Swap start and end locations
  function swapLocations() {
    const temp = start;
    const tempName = startName;
    start = end;
    startName = endName;
    end = temp;
    endName = tempName;
    updateMarkers();
    if (start && end) {
      getRoute();
    }
  }

  // Clear all selections and reset route
  function clearRoute() {
    start = null;
    end = null;
    startName = "";
    endName = "";
    markers = [];
    polyline = [];
    distance = 0;
    duration = 0;
    instructions = [];
    transitOptions = [];
    selectedTransit = null;
    routeOptions = [];
    selectedRouteOption = null;
    showInstructions = false;
    navigationMode = false;
    currentStep = 0;
  }

  // Use My Location as start
  function useMyLocation() {
    navigator.geolocation.getCurrentPosition(
      pos => {
        start = {
          name: "My Location",
          lat: pos.coords.latitude,
          lng: pos.coords.longitude
        };
        startName = "My Location";
        updateMarkers();
      },
      error => {
        alert("Could not get your location. Please enable location services.");
        console.error("Geolocation error:", error);
      }
    );
  }

  // MAP CLICK → set start first, then end
  function handleMapClick(e: CustomEvent<{ lat: number; lng: number }>) {
    if (!start) {
      start = { name: "Picked Location", lat: e.detail.lat, lng: e.detail.lng };
      startName = start.name;
    } else {
      end = { name: "Picked Location", lat: e.detail.lat, lng: e.detail.lng };
      endName = end.name;
    }
    updateMarkers();
    if (start && end) {
      getRoute();
    }
  }

  // GET ROUTE WITH ENHANCED INSTRUCTIONS
  async function getRoute() {
    if (!start || !end) {
      alert("Select start and destination first!");
      return;
    }

    // Save to recent locations
    saveToRecent(start);
    saveToRecent(end);

    try {
      const res = await fetch(`${API_BASE}/enhanced`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start_lat: start.lat,
          start_lng: start.lng,
          end_lat: end.lat,
          end_lng: end.lng,
          walk_only: walkOnly
        })
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();

      if (!Array.isArray(data.polyline)) {
        alert("Backend returned invalid polyline.");
        return;
      }

      polyline = data.polyline.map(([lat, lng, style]: [number, number, string]) => ({
        lat,
        lng,
        style: (style === 'dotted' ? 'dotted' : 'solid') as 'dotted' | 'solid'
      }));
      instructions = data.instructions || [];
      transitOptions = walkOnly ? [] : (data.transit_options || []);
      showInstructions = true;

      updateMarkers();
    } catch (error) {
      console.error("Error fetching route:", error);
      alert("Failed to get route. Please try again.");
    }
  }
  
  // Get detailed transit route instructions
  async function getTransitDetails(option: TransitOption, silentRefresh = false) {
    if (!silentRefresh) {
      selectedTransit = option;
      routeOptions = [];
      selectedRouteOption = null;
    }
    
    try {
      const res = await fetch(`${API_BASE}/transit-detail`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start_lat: start!.lat,
          start_lng: start!.lng,
          end_lat: end!.lat,
          end_lng: end!.lng,
          stop_name: option.stop_name,
          stop_type: option.type,
          stop_lat: option.stop_lat,
          stop_lng: option.stop_lng
        })
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      routeOptions = data.route_options || [];
      
      // Auto-select and show first option immediately
      if (routeOptions.length > 0 && !silentRefresh) {
        selectRouteOption(routeOptions[0]);
      }
      
      // Auto-select first option and expand sections
      if (routeOptions.length > 0) {
        selectRouteOption(routeOptions[0]);
        collapsedSections['routeOptions'] = false;
        collapsedSections['detailedRoute'] = false;
      }
    } catch (error) {
      console.error("Error fetching transit details:", error);
      if (!silentRefresh) {
        alert("Failed to get transit details. Please try again.");
      }
    }
  }
  
  function selectRouteOption(option: RouteOption) {
    selectedRouteOption = option;
  }

  // Save location to recent
  function saveToRecent(place: Place) {
    const exists = recentLocations.find(p => p.lat === place.lat && p.lng === place.lng);
    if (!exists) {
      recentLocations = [place, ...recentLocations.slice(0, 9)]; // Keep 10 most recent
      localStorage.setItem('recentLocations', JSON.stringify(recentLocations));
    }
  }

  // Share route as URL
  function shareRoute() {
    if (!start || !end) {
      alert('Please select start and destination first');
      return;
    }
    const params = new URLSearchParams({
      fromLat: start.lat.toString(),
      fromLng: start.lng.toString(),
      fromName: start.name,
      toLat: end.lat.toString(),
      toLng: end.lng.toString(),
      toName: end.name
    });
    const url = `${window.location.origin}/route-planner?${params.toString()}`;
    navigator.clipboard.writeText(url).then(() => {
      alert('Route link copied to clipboard!');
    });
  }

  // Toggle section collapse
  function toggleSection(section: string) {
    collapsedSections[section] = !collapsedSections[section];
  }
</script>

<div class="planner-shell">
  <div class="planner-bg">
    <div class="planner-routes">
      <svg viewBox="0 0 1920 800" preserveAspectRatio="none">
        <path class="route-line red" d="M0,180 Q480,140 960,180 T1920,180" />
        <path class="route-line blue" d="M0,360 Q480,420 960,360 T1920,360" />
        <path class="route-line green" d="M0,540 Q480,500 960,540 T1920,540" />
        <circle class="station" cx="220" cy="180" r="6" />
        <circle class="station" cx="640" cy="360" r="6" />
        <circle class="station" cx="1060" cy="540" r="6" />
        <circle class="station" cx="1480" cy="360" r="6" />
      </svg>
    </div>
    <div class="planner-grid"></div>
  </div>

  <div class="card">
    <h1>Route Planner</h1>

  <div class="inputs">

    <button on:click={useMyLocation}>📍 Use My Location</button>
      <!-- START -->
      <SearchBar
        placeholder="Start location..."
        bind:value={startName}
        on:select={(e: CustomEvent<Place>) => {
          start = e.detail;
          startName = start.name;
          updateMarkers();
        }}
      />

      <button class="swap-btn" on:click={swapLocations} title="Swap start and destination">↕️</button>

      <!-- END -->
      <SearchBar
        placeholder="Destination..."
        bind:value={endName}
        on:select={(e: CustomEvent<Place>) => {
          end = e.detail;
          endName = end.name;
          updateMarkers();
        }}
      />


    <button on:click={getRoute}>Get Route</button>
    <button class="clear-btn" on:click={clearRoute}>🔄 Clear</button>
    {#if start && end}
      <button class="share-btn" on:click={shareRoute}>🔗 Share</button>
    {/if}
  </div>

  <LeafletMap
    {markers}
    {polyline}
    center={{ lat: 22.3027, lng: 114.1772 }}
    on:mapclick={handleMapClick}
  />

  {#if showInstructions && (transitOptions.length > 0 || instructions.length > 0)}
    <div class="instructions-panel">
      <div class="instructions-header">
        <h2>{walkOnly ? '🚶 Walking Route' : '🗺️ Route Instructions'}</h2>
        {#if navigationMode}
          <button class="nav-mode-btn" on:click={() => navigationMode = false}>📋 View All</button>
        {:else}
          <button class="nav-mode-btn" on:click={() => navigationMode = true}>🧭 Navigation</button>
        {/if}
      </div>
      
      {#if !walkOnly && transitOptions.length > 0}
        <div class="transit-section">
          <h3>🚇 Nearby Public Transport</h3>
          {#each transitOptions as option}
            <button class="transit-option" on:click={() => getTransitDetails(option)}>
              <div class="transit-icon">{option.type === 'MTR' ? '🚇' : option.type === 'Ferry' ? '⛴️' : '🚌'}</div>
              <div class="transit-details">
                <strong>{option.stop_name}</strong>
                <p>{option.instruction}</p>
              </div>
              <div class="arrow">→</div>
            </button>
          {/each}
        </div>
      {/if}
      
      {#if !walkOnly && routeOptions.length > 0 && selectedTransit}
        <div class="route-options-section">
          <div class="section-header">
            <div class="section-title">
              <h3>🛣️ Route Options via {selectedTransit.stop_name}</h3>
            </div>
            {#if routeOptions.length > 1}
              <button class="show-all-btn" on:click={() => showAllRoutes = !showAllRoutes}>
                {showAllRoutes ? '📋 Compare' : '🔀 Show All'}
              </button>
            {/if}
            <span class="refresh-indicator" title="Last updated: {new Date(lastRefreshTime).toLocaleTimeString()}">
              🔄 Auto-refresh
            </span>
          </div>
          <div class="options-grid" class:show-all={showAllRoutes}>
              {#each (showAllRoutes ? routeOptions : routeOptions.slice(0, 3)) as option}
                <button 
                  class="route-option-card" 
                  class:selected={selectedRouteOption === option}
                  on:click={() => selectRouteOption(option)}
                >
                  <div class="option-header">
                    <h4>{option.option_name}</h4>
                    <span class="duration-badge">{option.total_duration_min} min</span>
                  </div>
                  <div class="option-summary">
                    {#each option.steps as step, i}
                      <span class="step-icon">
                        {#if step.type === 'walk'}🚶
                        {:else if step.type === 'bus'}🚌
                        {:else if step.type === 'mtr'}🚇
                        {:else if step.type === 'ferry'}⛴️
                        {:else if step.type === 'transfer'}🔄
                        {/if}
                      </span>
                      {#if i < option.steps.length - 1}
                        <span class="step-arrow">→</span>
                      {/if}
                    {/each}
                  </div>
                </button>
              {/each}
            </div>
        </div>
      {/if}
      
      {#if !walkOnly && selectedRouteOption}
        <div class="detailed-route">
          <h3>📍 {selectedRouteOption.option_name}</h3>
            <p class="route-duration">Total Time: <strong>{selectedRouteOption.total_duration_min} minutes</strong></p>
            <div class="timeline">
              {#each selectedRouteOption.steps as step, i}
            <div class="timeline-step" class:completed={navigationMode && currentStep > i} class:active={navigationMode && currentStep === i}>
              <div class="timeline-marker">
                <div class="timeline-icon" class:walk={step.type === 'walk'} class:bus={step.type === 'bus'} class:mtr={step.type === 'mtr'} class:ferry={step.type === 'ferry'}>
                  {#if step.type === 'walk'}🚶
                  {:else if step.type === 'bus'}🚌
                  {:else if step.type === 'mtr'}🚇
                  {:else if step.type === 'ferry'}⛴️
                  {:else if step.type === 'transfer'}🔄
                  {/if}
                </div>
                {#if i < selectedRouteOption.steps.length - 1}
                  <div class="timeline-line" class:walk={step.type === 'walk'} class:bus={step.type === 'bus'} class:mtr={step.type === 'mtr'} class:ferry={step.type === 'ferry'}></div>
                {/if}
              </div>
              <div class="timeline-content">
                <div class="step-type-label">{step.action}</div>
                {#if step.bus_number}
                  <p class="bus-info">Bus: <strong>{step.bus_number}</strong></p>
                {/if}
                {#if step.get_off_at}
                  <p class="stop-info">Get off at: <strong>{step.get_off_at}</strong></p>
                {/if}
                {#if step.exit_info}
                  <p class="exit-info">🚪 {step.exit_info}</p>
                {/if}
                <p class="instruction">{step.instruction}</p>
                {#if step.distance_m}
                  <small>{step.distance_m}m • {step.duration_min} min</small>
                {:else if step.duration_min}
                  <small>{step.duration_min} min</small>
                {/if}
              </div>
            </div>
            {/each}
          </div>
        </div>
      {/if}

      {#if instructions.length > 0}
        <div class="walking-section">
          <button class="section-toggle" on:click={() => toggleSection('walking')}>
            <h3>🚶 Walking Directions</h3>
            <span class="toggle-icon">{collapsedSections['walking'] ? '▼' : '▲'}</span>
          </button>
          {#if !collapsedSections['walking']}
            {#if navigationMode && instructions.length > 0}
            <!-- Navigation Mode: Show one step at a time -->
            <div class="navigation-mode">
              <div class="step current-step">
                <div class="step-number">{currentStep + 1}</div>
                <div class="step-content">
                  <p>{instructions[currentStep].instruction}</p>
                  <small>{instructions[currentStep].distance_m}m • {Math.round((instructions[currentStep].duration_s ?? 0) / 60)} min</small>
                </div>
              </div>
              <div class="nav-controls">
                <button on:click={() => currentStep = Math.max(0, currentStep - 1)} disabled={currentStep === 0}>← Previous</button>
                <span class="step-counter">{currentStep + 1} of {instructions.length}</span>
                <button on:click={() => currentStep = Math.min(instructions.length - 1, currentStep + 1)} disabled={currentStep === instructions.length - 1}>Next →</button>
              </div>
            </div>
          {:else}
            {#each instructions as step, i}
              <div class="step">
                <div class="step-number">{i + 1}</div>
                <div class="step-content">
                  <p>{step.instruction}</p>
                  <small>{step.distance_m}m • {Math.round((step.duration_s ?? 0) / 60)} min</small>
                </div>
              </div>
            {/each}
          {/if}
        {/if}
        </div>
      {/if}
    </div>
  {/if}
</div>
</div>
<style>
  .card {
    background: white;
    padding: 20px;
    margin: 20px auto;
    width: 85%;
    border-radius: 14px;
    box-shadow: 0px 0px 12px rgba(0,0,0,0.15);
    position: relative;
    z-index: 1;
  }

  .planner-shell {
    position: relative;
    padding: 40px 0 60px;
    background: radial-gradient(circle at 5% 30%, rgba(59, 130, 246, 0.22), transparent 38%),
      radial-gradient(circle at 95% 30%, rgba(236, 72, 153, 0.20), transparent 38%),
      radial-gradient(circle at 50% 95%, rgba(16, 185, 129, 0.14), transparent 32%),
      linear-gradient(135deg, #f5f7fb 0%, #eef2ff 45%, #f8fafc 100%);
    overflow: hidden;
    isolation: isolate;
  }

  .planner-bg {
    position: absolute;
    inset: 0;
    overflow: hidden;
    z-index: 0;
    mix-blend-mode: multiply;
  }

  .planner-shell::before {
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
      120deg,
      rgba(59, 130, 246, 0.07) 0,
      rgba(59, 130, 246, 0.07) 12px,
      transparent 12px,
      transparent 24px
    );
    opacity: 0.35;
    pointer-events: none;
    mix-blend-mode: soft-light;
    z-index: 0;
  }

  .planner-shell::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at -10% 50%, rgba(59, 130, 246, 0.28), transparent 34%),
      radial-gradient(circle at 110% 50%, rgba(236, 72, 153, 0.25), transparent 34%),
      linear-gradient(180deg, rgba(15, 23, 42, 0.04), transparent 60%);
    pointer-events: none;
    z-index: 0;
  }

  .planner-grid {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(15, 23, 42, 0.06) 1px, transparent 1px),
      linear-gradient(90deg, rgba(15, 23, 42, 0.06) 1px, transparent 1px);
    background-size: 80px 80px;
    filter: blur(0.1px);
    opacity: 0.4;
  }

  .planner-routes {
    position: absolute;
    inset: 0;
    opacity: 0.25;
    pointer-events: none;
  }

  .planner-routes svg {
    width: 100%;
    height: 100%;
  }

  .route-line {
    fill: none;
    stroke-width: 4;
    stroke-linecap: round;
    stroke-dasharray: 8 10;
    animation: dashFlow 18s linear infinite;
  }

  .route-line.red { stroke: #ef4444; animation-delay: 0s; }
  .route-line.blue { stroke: #3b82f6; animation-delay: 2s; }
  .route-line.green { stroke: #10b981; animation-delay: 4s; }

  .station {
    fill: #f8fafc;
    stroke: #1e293b;
    stroke-width: 2;
    animation: stationPulse 2.8s ease-in-out infinite;
  }

  @keyframes dashFlow {
    0% { stroke-dashoffset: 0; }
    100% { stroke-dashoffset: 200; }
  }

  @keyframes stationPulse {
    0%, 100% { transform: scale(1); opacity: 0.9; }
    50% { transform: scale(1.2); opacity: 1; }
  }
  .inputs {
    display: grid;
    grid-template-columns: auto 1fr 1fr auto;
    gap: 10px;
    margin-bottom: 10px;
    align-items: stretch;
  }

  .inputs button {
    white-space: nowrap;
    padding: 12px 20px;
    min-width: fit-content;
    height: 48px;
    align-self: stretch;
  }

  .inputs .swap-btn {
    background: #8b5cf6;
    padding: 12px;
    min-width: 48px;
    font-size: 1.2em;
  }

  .inputs .swap-btn:hover {
    background: #7c3aed;
    transform: rotate(180deg);
    transition: all 0.3s;
  }

  .inputs .clear-btn {
    background: #64748b;
  }

  .inputs .clear-btn:hover {
    background: #475569;
  }

  .inputs .share-btn {
    background: #10b981;
  }

  .inputs .share-btn:hover {
    background: #059669;
  }

  /* Make search bars expand equally and match button height */
  .inputs :global(.search-wrapper) { max-width: none; width: 100%; }
  .inputs :global(.input-wrap) { height: 48px; }
  
  .instructions-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }

  .nav-mode-btn {
    padding: 8px 16px;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9em;
  }

  .nav-mode-btn:hover {
    background: #2563eb;
  }

  .section-toggle {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: transparent;
    border: none;
    padding: 10px 0;
    cursor: pointer;
    text-align: left;
  }

  .section-toggle h3 {
    margin: 0;
  }

  .toggle-icon {
    font-size: 1.2em;
    color: #64748b;
  }

  .navigation-mode {
    background: white;
    border-radius: 12px;
    padding: 20px;
    margin: 15px 0;
  }

  .current-step {
    font-size: 1.1em;
    padding: 15px;
    background: #eff6ff;
    border-left: 4px solid #3b82f6;
  }

  .nav-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 15px;
    gap: 10px;
  }

  .nav-controls button {
    padding: 10px 20px;
    background: #3b82f6;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
  }

  .nav-controls button:disabled {
    background: #cbd5e1;
    cursor: not-allowed;
  }

  .nav-controls button:not(:disabled):hover {
    background: #2563eb;
  }

  .step-counter {
    color: #64748b;
    font-weight: 600;
  }
  
  .instructions-panel {
    margin-top: 20px;
    background: #f8f9fa;
    padding: 20px;
    border-radius: 12px;
    max-height: 500px;
    overflow-y: auto;
  }
  
  .instructions-panel h2 {
    margin-top: 0;
    color: #1e40af;
  }
  
  .instructions-panel h3 {
    margin: 20px 0 10px 0;
    color: #334155;
    font-size: 1.1em;
  }
  
  .transit-section {
    margin-bottom: 20px;
  }
  
  .transit-option {
    display: flex;
    align-items: center;
    gap: 15px;
    background: white;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 10px;
    border: 2px solid #e5e7eb;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .transit-option:hover {
    border-color: #3b82f6;
    background: #f0f7ff;
    transform: translateX(5px);
  }
  
  .arrow {
    margin-left: auto;
    font-size: 20px;
    color: #6b7280;
  }
  
  .transit-icon {
    font-size: 2em;
  }
  
  .transit-details {
    flex: 1;
  }
  
  .transit-details strong {
    color: #1e40af;
    display: block;
    margin-bottom: 5px;
  }
  
  .transit-details p {
    margin: 0;
    color: #64748b;
  }
  
  .walking-section {
    background: white;
    padding: 15px;
    border-radius: 8px;
  }
  
  .step {
    display: flex;
    gap: 15px;
    padding: 12px 0;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .step:last-child {
    border-bottom: none;
  }
  
  .step-number {
    background: #3b82f6;
    color: white;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    flex-shrink: 0;
  }
  
  .step-content {
    flex: 1;
  }
  
  .step-content p {
    margin: 0 0 5px 0;
    color: #334155;
  }
  
  .step-content small {
    color: #64748b;
  }
  
  .detailed-route {
    margin-top: 20px;
    background: white;
    padding: 20px;
    border-radius: 10px;
    border: 2px solid #3b82f6;
  }
  
  .detailed-route h3 {
    margin-top: 0;
    color: #1e40af;
  }
  
  .bus-info {
    margin: 5px 0;
    color: #059669;
    font-size: 1.05em;
  }
  
  .stop-info {
    margin: 5px 0;
    color: #dc2626;
  }
  
  .instruction {
    margin: 8px 0;
    color: #475569;
  }
  
  .route-options-section {
    margin: 20px 0;
  }
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .section-title h3 {
    margin: 0;
    color: #1e40af;
  }
  
  .show-all-btn {
    padding: 6px 14px;
    background: #8b5cf6;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85em;
    transition: all 0.2s;
  }
  
  .show-all-btn:hover {
    background: #7c3aed;
    transform: translateY(-1px);
  }
  
  .refresh-indicator {
    padding: 6px 12px;
    background: #f0fdf4;
    color: #15803d;
    border-radius: 6px;
    font-size: 0.8em;
    border: 1px solid #bbf7d0;
  }
  
  .route-options-section h3 {
    margin-bottom: 15px;
    color: #1e40af;
  }
  
  .options-grid {
    display: grid;
    gap: 12px;
  }
  
  .route-option-card {
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 10px;
    padding: 15px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
    width: 100%;
  }
  
  .route-option-card:hover {
    border-color: #3b82f6;
    background: #f0f7ff;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(59, 130, 246, 0.2);
  }
  
  .route-option-card.selected {
    border-color: #3b82f6;
    background: #eff6ff;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  .option-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .option-header h4 {
    margin: 0;
    font-size: 1.1em;
    color: #1e293b;
  }
  
  .duration-badge {
    background: #3b82f6;
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 0.9em;
    font-weight: bold;
  }
  
  .option-summary {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 1.3em;
  }
  
  .step-icon {
    opacity: 0.8;
  }
  
  .step-arrow {
    color: #9ca3af;
    font-size: 0.8em;
  }
  
  .route-duration {
    background: #f0f9ff;
    padding: 10px;
    border-radius: 6px;
    margin-bottom: 15px;
    color: #0c4a6e;
  }
  
  .exit-info {
    margin: 5px 0;
    color: #7c3aed;
    font-weight: 500;
  }

  /* Timeline Stepper Styles */
  .timeline {
    padding: 20px 0;
  }

  .timeline-step {
    display: flex;
    gap: 20px;
    position: relative;
    opacity: 0.6;
    transition: all 0.3s ease;
  }

  .timeline-step.active {
    opacity: 1;
    transform: scale(1.02);
    background: #f0f9ff;
    padding: 10px;
    border-radius: 10px;
    margin: 0 -10px;
  }

  .timeline-step.completed {
    opacity: 1;
  }

  .timeline-marker {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 50px;
  }

  .timeline-icon {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3em;
    background: #e5e7eb;
    border: 3px solid #fff;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    z-index: 2;
    transition: all 0.3s ease;
  }

  .timeline-icon.walk {
    background: #dbeafe;
    border-color: #3b82f6;
  }

  .timeline-icon.bus {
    background: #fef3c7;
    border-color: #f59e0b;
  }

  .timeline-icon.mtr {
    background: #ddd6fe;
    border-color: #8b5cf6;
  }

  .timeline-icon.ferry {
    background: #d1fae5;
    border-color: #10b981;
  }

  .timeline-step.active .timeline-icon {
    transform: scale(1.15);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  }

  .timeline-line {
    width: 4px;
    flex-grow: 1;
    background: #e5e7eb;
    margin: 8px 0;
    position: relative;
    transition: all 0.3s ease;
  }

  .timeline-line.walk {
    background: repeating-linear-gradient(
      to bottom,
      #3b82f6,
      #3b82f6 8px,
      transparent 8px,
      transparent 16px
    );
  }

  .timeline-line.bus {
    background: #f59e0b;
    width: 6px;
  }

  .timeline-line.mtr {
    background: #8b5cf6;
    width: 8px;
  }

  .timeline-line.ferry {
    background: #10b981;
    width: 6px;
  }

  .timeline-step.completed .timeline-line {
    background: #10b981;
  }

  .timeline-content {
    flex: 1;
    padding-bottom: 25px;
  }

  .step-type-label {
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 8px;
    font-size: 1.05em;
  }

  .timeline-step.active .step-type-label {
    color: #0c4a6e;
    font-size: 1.1em;
  }

  .instruction {
    color: #475569;
    margin: 8px 0;
    line-height: 1.5;
  }

  .bus-info, .stop-info {
    margin: 6px 0;
    color: #64748b;
  }

  .bus-info strong, .stop-info strong {
    color: #1e293b;
  }

  /* Section header with multiple controls */
  .section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }

  .show-all-btn {
    padding: 8px 16px;
    background: #6366f1;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9em;
    white-space: nowrap;
  }

  .show-all-btn:hover {
    background: #4f46e5;
  }

  .refresh-indicator {
    display: inline-block;
    padding: 6px 12px;
    background: #dcfce7;
    color: #166534;
    border-radius: 8px;
    font-size: 0.85em;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
  }

  .options-grid.show-all {
    max-height: none;
  }

  .options-grid:not(.show-all) {
    max-height: 400px;
    overflow-y: auto;
  }
</style>
