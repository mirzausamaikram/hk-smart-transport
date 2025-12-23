<script lang="ts">
// @ts-nocheck
  import LeafletMap from "$lib/components/LeafletMap.svelte";
  import SearchBar from "$lib/components/SearchBar.svelte";

  type Stop = { lat: number; lng: number; title: string; color: string };
  type LatLng = { lat: number; lng: number };

  let stops: Stop[] = [];
  let markers: Stop[] = [];
  let polyline: LatLng[] = [];

  let poiMarkers: { lat: number; lng: number; name: string; description?: string; type?: string }[] = [];
  let showPois = true;
  let stopSuggestions: any[] = []; // per-stop POI suggestions (top 3)

  let distance = 0;
  let duration = 0;
  let instructions: any[] = [];
  let transitOptions: any[] = [];
  let showInstructions = false;
  let routeOptions: any[] = [];
  let selectedTransit: any = null;
  let selectedRouteOption: any = null;

  // Get detailed transit route instructions (similar to route planner)
  async function getTransitDetails(option: any) {
    selectedTransit = option;
    routeOptions = [];
    selectedRouteOption = null;

    if (stops.length < 2) {
      alert('Need start and end stops for transit details');
      return;
    }

    try {
      const start = stops[0];
      const end = stops[stops.length - 1];
      const res = await fetch(`http://127.0.0.1:8000/api/route/transit-detail`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_lat: start.lat,
          start_lng: start.lng,
          end_lat: end.lat,
          end_lng: end.lng,
          stop_name: option.stop_name,
          stop_type: option.type,
          stop_lat: option.stop_lat,
          stop_lng: option.stop_lng
        })
      });

      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      routeOptions = data.route_options || [];
    } catch (error) {
      console.error('Error fetching transit details:', error);
      alert('Failed to get transit details. Please try again.');
    }
  }

  function selectRouteOption(option: any) {
    selectedRouteOption = option;
  }

  // UI state
  let searchValue = "";
  let alternatives: any[] = [];

  // ---------------------------------------------------
  // ADD STOP BY CLICKING MAP
  // ---------------------------------------------------
  function handleMapClick(e: CustomEvent<{ lat: number; lng: number }>) {
    stops = [...stops, {
      lat: e.detail.lat,
      lng: e.detail.lng,
      title: "",
      color: ""
    }];
    updateMarkers();
    fetchPoisForStop(stops.length - 1);
  }

  // add stop from search selection
  function addStopFromSearch(r: any) {
    if (!r || !r.lat || !r.lon) return;
    stops = [...stops, { lat: r.lat, lng: r.lon, title: r.name || "", color: "" }];
    updateMarkers();
    searchValue = "";
    fetchPoisForStop(stops.length - 1);
  }

  // ---------------------------------------------------
  // UPDATE MARKER COLORS + TITLES
  // ---------------------------------------------------
  function updateMarkers() {
    markers = stops.map((s, i) => ({
      ...s,
      title:
        i === 0
          ? "Start"
          : i === stops.length - 1
          ? "Destination"
          : `Stop ${i}`,
      color:
        i === 0
          ? "green"
          : i === stops.length - 1
          ? "red"
          : "yellow"
    }));
  }

  // ---------------------------------------------------
  // UNDO LAST STOP
  // ---------------------------------------------------
  function undo() {
    stops = stops.slice(0, -1);
    updateMarkers();
  }

  function moveUp(i: number) {
    if (i <= 0) return;
    const arr = [...stops];
    const tmp = arr[i - 1];
    arr[i - 1] = arr[i];
    arr[i] = tmp;
    stops = arr;
    updateMarkers();
  }

  function moveDown(i: number) {
    if (i >= stops.length - 1) return;
    const arr = [...stops];
    const tmp = arr[i + 1];
    arr[i + 1] = arr[i];
    arr[i] = tmp;
    stops = arr;
    updateMarkers();
  }

  function removeAt(i: number) {
    stops = stops.filter((_, idx) => idx !== i);
    updateMarkers();
  }

  function updateTitle(i: number, title: string) {
    stops = stops.map((s, idx) => (idx === i ? { ...s, title } : s));
    updateMarkers();
  }

  function setMode(i: number, mode: string) {
    stops = stops.map((s, idx) => (idx === i ? { ...s, mode } : s));
  }

  function setTime(i: number, t: string) {
    stops = stops.map((s, idx) => (idx === i ? { ...s, time: t } : s));
  }

  // ---------------------------------------------------
  // CLEAR ALL
  // ---------------------------------------------------
  function clearAll() {
    stops = [];
    markers = [];
    polyline = [];
    distance = 0;
    duration = 0;
  }

  // ---------------------------------------------------
  // GET MULTI-STOP ROUTE
  // ---------------------------------------------------
  async function getRoute() {
    if (stops.length < 2) {
      alert("Please add at least Start + Destination.");
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/api/route/multistop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ points: stops.map((s) => ({ lat: s.lat, lng: s.lng })) })
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();

      if (!Array.isArray(data.polyline)) {
        alert("Backend returned invalid polyline.");
        return;
      }

      polyline = data.polyline.map((p: [number, number]) => ({ lat: p[0], lng: p[1] }));
      // clear POI layer by default when new route fetched
      poiMarkers = [];

      distance = data.distance_m;
      duration = data.duration_s;

      // enhanced fields (from route planner): instructions + transit options
      instructions = data.instructions || [];
      transitOptions = data.transit_options || [];
      showInstructions = (instructions.length > 0) || (transitOptions.length > 0);

      updateMarkers();
    } catch (error) {
      console.error('Error fetching multistop route:', error);
      alert('Failed to get route. Please try again.');
    }
  }

  // ---------------------------------------------------
  // AI OPTIMIZED ROUTE (TSP)
  // ---------------------------------------------------
  async function optimizeRoute() {
    if (stops.length < 3) {
      alert("Add at least 3 stops for AI optimization.");
      return;
    }

    const res = await fetch("http://127.0.0.1:8000/api/route/optimize", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        points: stops.map(s => ({ lat: s.lat, lng: s.lng }))
      })
    });

    const data = await res.json();

    if (data.optimized) {
      stops = data.optimized.map((p: any) => ({
        lat: p.lat,
        lng: p.lng,
        title: "",
        color: ""
      }));
      updateMarkers();
    }

    if (Array.isArray(data.polyline)) {
      polyline = data.polyline.map((p: [number, number]) => ({
        lat: p[0],
        lng: p[1]
      }));

      distance = data.distance_m;
      duration = data.duration_s;
    } else {
      alert("Optimization failed.");
    }
  }

  // Fetch nearby POIs for a single stop and show on map
  async function fetchNearby(i: number) {
    const s = stops[i];
    if (!s) return;
    // backward-compatible nearby call (legacy)
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/nearby?lat=${s.lat}&lng=${s.lng}`);
      const data = await res.json();
      poiMarkers = (data.results || []).map((p: any) => ({ lat: p.lat, lng: p.lon || p.lng, name: p.name, description: p.desc, type: p.type }));
      showPois = true;
    } catch (e) {
      console.warn('nearby fetch failed', e);
      poiMarkers = [];
    }
  }

  // Fetch POI suggestions (top N) from new pois router and keep per-stop suggestions
  async function fetchPoisForStop(i: number, limit = 3) {
    const s = stops[i];
    if (!s) return;
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/pois/nearby?lat=${s.lat}&lng=${s.lng}&limit=${limit}`);
      if (!res.ok) throw new Error(`status ${res.status}`);
      const data = await res.json();
      stopSuggestions[i] = (data.results || []).map((p: any) => ({ ...p }));
      // trigger reactivity
      stopSuggestions = [...stopSuggestions];
    } catch (e) {
      console.warn('pois fetch failed', e);
      stopSuggestions[i] = [];
      stopSuggestions = [...stopSuggestions];
    }
  }

  function quickAddPoi(i: number, poi: any) {
    const newStop = { lat: poi.lat, lng: poi.lon || poi.lng, title: poi.name || poi.title || '', color: '' };
    const arr = [...stops];
    arr.splice(i + 1, 0, newStop);
    stops = arr;
    updateMarkers();
    // fetch suggestions for the newly inserted stop as well
    fetchPoisForStop(i + 1);
  }

  // Generate a small inline SVG path preview for an alternative polyline
  function svgPreviewPath(points: [number, number][], w = 160, h = 60) {
    if (!points || points.length === 0) return '';
    const lats = points.map(p => p[0]);
    const lngs = points.map(p => p[1]);
    const minLat = Math.min(...lats), maxLat = Math.max(...lats);
    const minLng = Math.min(...lngs), maxLng = Math.max(...lngs);
    const pad = 0.02; // small padding
    const latRange = maxLat - minLat || 0.0001;
    const lngRange = maxLng - minLng || 0.0001;
    const coords = points.map(p => {
      const x = ((p[1] - minLng) / lngRange) * (w - 8) + 4;
      const y = (1 - (p[0] - minLat) / latRange) * (h - 8) + 4;
      return `${x},${y}`;
    });
    return `M ${coords.join(' L ')}`;
  }

  // Save itinerary to localStorage
  function saveItinerary(name = "untitled") {
    const payload = { name, stops };
    const key = `itinerary:${name}`;
    localStorage.setItem(key, JSON.stringify(payload));
    alert(`Saved as ${key}`);
  }

  // Generate share link with encoded stops in query
  function shareItinerary() {
    const encoded = encodeURIComponent(JSON.stringify(stops));
    const url = `${location.origin}${location.pathname}?stops=${encoded}`;
    navigator.clipboard?.writeText(url).then(() => alert('Share link copied to clipboard'));
  }

  // Try to load stops from ?stops= query param
  function loadFromQuery() {
    const params = new URLSearchParams(location.search);
    const s = params.get('stops');
    if (!s) return;
    try {
      const parsed = JSON.parse(decodeURIComponent(s));
      if (Array.isArray(parsed)) {
        stops = parsed.map((p: any) => ({ lat: p.lat, lng: p.lng, title: p.title || '', color: '' }));
        updateMarkers();
      }
    } catch (e) {
      console.warn('failed to parse stops from query', e);
    }
  }

  

  // Request route alternatives (backend must support)
  async function getAlternatives() {
    if (stops.length < 2) return;
    const res = await fetch('http://127.0.0.1:8000/api/route/alternatives', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ points: stops.map(s => ({ lat: s.lat, lng: s.lng })) }) });
    try {
      const data = await res.json();
      alternatives = data.alternatives || [];
    } catch (e) { alternatives = []; }
  }

  // initialize from query param when component mounts
  import { onMount } from 'svelte';
  onMount(() => loadFromQuery());
</script>

  <div class="card">
  <h1>Multi-Stop Route Planner</h1>

  <div class="top-row">
    <div class="left">
      <SearchBar bind:value={searchValue} placeholder="Search places or addresses" on:select={(e) => addStopFromSearch(e.detail)} />

      <div class="buttons">
        ye<button on:click={undo}>↩ Undo</button>
        <button on:click={clearAll}>🗑 Clear</button>
        <button on:click={getRoute}>🚀 Get Route</button>
        <button on:click={optimizeRoute}>✨ Optimize</button>
        <button on:click={getAlternatives}>🔁 Alternatives</button>
        <button on:click={shareItinerary}>🔗 Share</button>
      </div>

      <div class="stops">
        <h3>Stops</h3>
        {#if stops.length === 0}
          <p>Click map or use search to add stops.</p>
        {:else}
          <ol>
            {#each stops as s, i}
              <li class="stop-row">
                <div class="left-col">
                  <span class="drag-handle">☰</span>
                  <input class="title" value={s.title} placeholder={`Stop ${i + 1}`} on:input={(ev: Event) => updateTitle(i, (ev.currentTarget as HTMLInputElement).value)} />
                  <select on:change={(ev: Event) => setMode(i, (ev.currentTarget as HTMLSelectElement).value)}>
                    <option value="">Mode</option>
                    <option value="walk">Walk</option>
                    <option value="bus">Bus</option>
                    <option value="mtr">MTR</option>
                    <option value="ferry">Ferry</option>
                  </select>
                  <input type="time" on:change={(ev: Event) => setTime(i, (ev.currentTarget as HTMLInputElement).value)} />
                </div>
                <div class="right-col">
                  <button title="Move up" on:click={() => moveUp(i)}>⬆</button>
                  <button title="Move down" on:click={() => moveDown(i)}>⬇</button>
                  <button title="Nearby POIs" on:click={() => fetchNearby(i)}>📍</button>
                  <button title="Remove" on:click={() => removeAt(i)}>✖</button>
                </div>
                <div class="coords">({s.lat.toFixed(5)}, {s.lng.toFixed(5)})</div>
              </li>
              {#if stopSuggestions[i] && stopSuggestions[i].length}
                <li class="suggestions-row">
                  <div class="suggestions">
                    <strong>Suggested nearby places</strong>
                    <div class="suggest-grid">
                      {#each stopSuggestions[i] as poi}
                        <div class="poi-card">
                          <div class="poi-header">
                            <div class="poi-name">{poi.name}</div>
                            <div class="poi-distance">{(poi.distance || poi.distance_m) ? Math.round(poi.distance || poi.distance_m) + ' m' : ''}</div>
                          </div>
                          {#if poi.opening_hours}
                            <div class="poi-hours">⏰ {poi.opening_hours}</div>
                          {/if}
                          {#if poi.visit_note}
                            <div class="poi-note">{poi.visit_note}</div>
                          {/if}
                          <div class="poi-actions">
                            <button on:click={() => quickAddPoi(i, poi)}>+ Add</button>
                            <button on:click={() => { poiMarkers = [...poiMarkers, { lat: poi.lat, lng: poi.lon || poi.lng, name: poi.name }]; showPois = true; }}>Show</button>
                          </div>
                        </div>
                      {/each}
                    </div>
                  </div>
                </li>
              {/if}
            {/each}
          </ol>
        {/if}
      </div>

      

      {#if alternatives.length}
        <div class="alts">
          <h4>Alternatives</h4>
          <div class="alts-grid">
            {#each alternatives as alt}
              <div class="alt-card">
                <svg width="160" height="60" viewBox="0 0 160 60" class="alt-preview">
                  <path d={svgPreviewPath(alt.polyline || [])} fill="none" stroke="#2b6cb0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <div class="alt-meta">
                  <div><strong>{Math.round((alt.duration_s||0)/60)} min</strong></div>
                  <div>{Math.round(alt.distance_m||0)} m</div>
                </div>
                <div class="alt-actions">
                  <button on:click={() => { polyline = (alt.polyline || []).map((p:[number,number])=>({lat:p[0],lng:p[1]})); distance = alt.distance_m || distance; duration = alt.duration_s || duration; }}>Apply</button>
                  <button on:click={() => { polyline = (alt.polyline || []).map((p:[number,number])=>({lat:p[0],lng:p[1]})); }}>Show</button>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      {#if distance}
        <div class="stats">
          <p><b>Total:</b> {Math.round(distance)} m — {Math.round(duration/60)} min</p>
          <button on:click={() => saveItinerary('saved-' + Date.now())}>Save</button>
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
                        <small>{step.instruction} {step.duration_min ? `• ${step.duration_min} min` : ''}</small>
                      {/each}
                    </div>
                  </button>
                {/each}
              </div>

              {#if selectedRouteOption}
                <div class="route-action">
                  <button on:click={() => {
                    if (selectedRouteOption.polyline) {
                      polyline = selectedRouteOption.polyline.map((p:[number,number])=>({lat:p[0],lng:p[1]}));
                    }
                    distance = selectedRouteOption.distance_m || distance;
                    duration = selectedRouteOption.duration_s || duration;
                  }}>Apply Option</button>
                </div>
              {/if}
            </div>
          {/if}

          {#if instructions.length > 0}
            <div class="instructions-list">
              <h3>Step-by-step</h3>
              <ol>
                {#each instructions as inst}
                  <li>{inst.instruction} <small>({inst.distance_m} m)</small></li>
                {/each}
              </ol>
            </div>
          {/if}
        </div>
      {/if}
    </div>

    <div class="right">
      <LeafletMap
        {markers}
        {polyline}
        {poiMarkers}
        {showPois}
        center={{ lat: 22.3027, lng: 114.1772 }}
        on:mapclick={handleMapClick}
      />
    </div>
  </div>
</div>

<style>
  .card {
    background: white;
    padding: 20px;
    margin: 20px auto;
    width: 90%;
    border-radius: 14px;
    box-shadow: 0px 0px 12px rgba(0,0,0,0.15);
  }

  .buttons {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
  }

  .stops {
    margin-top: 20px;
  }

  .stats {
    margin-top: 20px;
    background: #eef3ff;
    padding: 15px;
    border-radius: 10px;
    width: 250px;
  }
  .suggestions-row { list-style: none; margin: 8px 0 16px 0; }
  .suggestions { background: #fff7ed; padding: 10px; border-radius: 8px; border: 1px solid #ffe7c2; }
  .suggest-grid { display: flex; gap: 8px; margin-top: 8px; }
  .poi-card { background: white; border-radius: 8px; border: 1px solid #e6e6e6; padding: 8px; width: 210px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
  .poi-header { display:flex; justify-content:space-between; align-items:center; font-weight:600; }
  .poi-hours, .poi-note { font-size: 12px; color: #555; margin-top:4px; }
  .poi-actions { display:flex; gap:6px; margin-top:8px; }

  .alts-grid { display:flex; gap:12px; flex-wrap:wrap; margin-top:10px; }
  .alt-card { background:#ffffff; border-radius:8px; padding:8px; width:180px; box-shadow:0 4px 12px rgba(0,0,0,0.06); display:flex; flex-direction:column; align-items:center; }
  .alt-preview { background: linear-gradient(180deg,#f7fbff,#ffffff); border-radius:6px; }
  .alt-meta { margin-top:8px; font-size:13px; color:#333; }
  .alt-actions { display:flex; gap:8px; margin-top:8px; }
  
</style>
