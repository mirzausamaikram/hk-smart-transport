<script lang="ts">
  import SearchBar from "$lib/components/SearchBar.svelte";
  import LeafletMap from "$lib/components/LeafletMap.svelte";

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
  let distance = 0;
  let duration = 0;
  let instructions: Instruction[] = [];
  let transitOptions: TransitOption[] = [];
  let showInstructions = false;
  let selectedTransit: TransitOption | null = null;
  let routeOptions: RouteOption[] = [];
  let selectedRouteOption: RouteOption | null = null;

  // Constants
  const API_BASE = "http://127.0.0.1:8000/api/route";

  // Update markers on map
  function updateMarkers() {
    markers = [];
    if (start) markers.push({ ...start, title: "Start", color: "#4CAF50" });
    if (end) markers.push({ ...end, title: "Destination", color: "#FF5722" });
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
  }

  // GET ROUTE WITH ENHANCED INSTRUCTIONS
  async function getRoute() {
    if (!start || !end) {
      alert("Select start and destination first!");
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/enhanced`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start_lat: start.lat,
          start_lng: start.lng,
          end_lat: end.lat,
          end_lng: end.lng
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

      polyline = data.polyline.map(([lat, lng]: [number, number]) => ({ lat, lng }));
      distance = data.distance_m;
      duration = data.duration_s;
      instructions = data.instructions || [];
      transitOptions = data.transit_options || [];
      showInstructions = true;

      updateMarkers();
    } catch (error) {
      console.error("Error fetching route:", error);
      alert("Failed to get route. Please try again.");
    }
  }
  
  // Get detailed transit route instructions
  async function getTransitDetails(option: TransitOption) {
    selectedTransit = option;
    routeOptions = [];
    selectedRouteOption = null;
    
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
    } catch (error) {
      console.error("Error fetching transit details:", error);
      alert("Failed to get transit details. Please try again.");
    }
  }
  
  function selectRouteOption(option: RouteOption) {
    selectedRouteOption = option;
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
  </div>

  <LeafletMap
    {markers}
    {polyline}
    center={{ lat: 22.3027, lng: 114.1772 }}
    on:mapclick={handleMapClick}
  />

  {#if distance}
    <div class="stats">
      <p><b>Distance:</b> {Math.round(distance)} m</p>
      <p><b>Duration:</b> {Math.round(duration / 60)} min walk</p>
    </div>
  {/if}

  {#if showInstructions && (transitOptions.length > 0 || instructions.length > 0)}
    <div class="instructions-panel">
      <h2>🗺️ Route Instructions</h2>
      
      {#if transitOptions.length > 0}
        <div class="transit-section">
          <h3>🚇 Nearby Public Transport</h3>
          {#each transitOptions as option}
            <button class="transit-option" on:click={() => getTransitDetails(option)}>
              <div class="transit-icon">{option.type === 'MTR' ? '🚇' : '🚌'}</div>
              <div class="transit-details">
                <strong>{option.stop_name}</strong>
                <p>{option.instruction}</p>
              </div>
              <div class="arrow">→</div>
            </button>
          {/each}
        </div>
      {/if}
      
      {#if routeOptions.length > 0 && selectedTransit}
        <div class="route-options-section">
          <h3>🛣️ Route Options via {selectedTransit.stop_name}</h3>
          <div class="options-grid">
            {#each routeOptions as option}
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
      
      {#if selectedRouteOption}
        <div class="detailed-route">
          <h3>📍 {selectedRouteOption.option_name}</h3>
          <p class="route-duration">Total Time: <strong>{selectedRouteOption.total_duration_min} minutes</strong></p>
          {#each selectedRouteOption.steps as step, i}
            <div class="detail-step">
              <div class="step-number">{i + 1}</div>
              <div class="step-info">
                <div class="step-type">
                  {#if step.type === 'walk'}🚶
                  {:else if step.type === 'bus'}🚌
                  {:else if step.type === 'mtr'}🚇
                  {:else if step.type === 'transfer'}🔄
                  {/if}
                  {step.action}
                </div>
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
      {/if}

      {#if instructions.length > 0}
        <div class="walking-section">
          <h3>🚶 Walking Directions</h3>
          {#each instructions as step, i}
            <div class="step">
              <div class="step-number">{i + 1}</div>
              <div class="step-content">
                <p>{step.instruction}</p>
                <small>{step.distance_m}m • {Math.round((step.duration_s ?? 0) / 60)} min</small>
              </div>
            </div>
          {/each}
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
    display: flex;
    gap: 8px;
    margin-bottom: 10px;
    align-items: center;
  }

  .inputs button {
    white-space: nowrap;
    padding: 12px 20px;
    min-width: fit-content;
  }
  .stats {
    margin-top: 20px;
    background: #eef3ff;
    padding: 15px;
    border-radius: 10px;
    width: 250px;
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
  
  .detail-step {
    display: flex;
    gap: 15px;
    padding: 15px 0;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .detail-step:last-child {
    border-bottom: none;
  }
  
  .step-info {
    flex: 1;
  }
  
  .step-type {
    font-weight: bold;
    color: #1e40af;
    margin-bottom: 8px;
    font-size: 1.1em;
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
</style>
