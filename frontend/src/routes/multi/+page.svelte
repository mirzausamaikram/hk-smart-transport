<script lang="ts">
  import LeafletMap from "$lib/components/LeafletMap.svelte";
  import SearchBar from "$lib/components/SearchBar.svelte";
  import { onMount } from 'svelte';

  type Stop = { lat: number; lng: number; title: string; color: string; duration?: number };
  type LatLng = { lat: number; lng: number };

  let stops: Stop[] = [];
  let markers: Stop[] = [];
  let polyline: LatLng[] = [];

  let poiMarkers: { lat: number; lng: number; name: string; description?: string; type?: string }[] = [];
  let showPois = true;
  let stopSuggestions: any[] = [];

  let distance = 0;
  let duration = 0;
  let instructions: any[] = [];
  let transitOptions: any[] = [];
  let showInstructions = false;
  let routeOptions: any[] = [];
  let selectedTransit: any = null;
  let selectedRouteOption: any = null;

  let segmentTransit: { options: any[]; instructions: any[] }[] = [];
  let segmentSelectedTransit: any[] = [];
  let segmentRouteOptions: any[][] = [];

  let recentLocations: any[] = [];
  let favoriteLocations: any[] = [];
  let isLoading = false;
  let errorMessage = "";
  let showFavorites = false;
  let showRecent = false;
  let showSummary = true;
  let showTemplates = false;

  let routeTemplates: any[] = [];

  function loadTemplates() {
    const saved = localStorage.getItem('routeTemplates');
    if (saved) {
      try {
        routeTemplates = JSON.parse(saved);
      } catch (e) {
        routeTemplates = [];
      }
    }
  }

  function saveAsTemplate() {
    if (stops.length < 2) return;
    const name = prompt('Enter template name:');
    if (!name) return;

    const template = {
      id: Date.now(),
      name,
      stops: stops.map(s => ({ lat: s.lat, lng: s.lng, title: s.title }))
    };

    routeTemplates = [...routeTemplates, template];
    localStorage.setItem('routeTemplates', JSON.stringify(routeTemplates));
  }

  function loadTemplate(template: any) {
    stops = template.stops.map((s: any) => ({ ...s, color: '', duration: 0 }));
    updateMarkers();
    showTemplates = false;
  }

  function deleteTemplate(id: number) {
    routeTemplates = routeTemplates.filter(t => t.id !== id);
    localStorage.setItem('routeTemplates', JSON.stringify(routeTemplates));
  }

  function getStopIcon(index: number): string {
    if (stops.length === 0) return '📍';
    if (index === 0) return '🚩';
    if (index === stops.length - 1) return '🏁';
    return '📍';
  }

  function getStopColor(index: number): string {
    if (stops.length === 0) return '#3b82f6';
    if (index === 0) return '#10b981';
    if (index === stops.length - 1) return '#ef4444';
    return '#3b82f6';
  }

  function insertStopBetween(index: number) {
    if (index >= stops.length - 1) return;
    const stop1 = stops[index];
    const stop2 = stops[index + 1];
    const midLat = (stop1.lat + stop2.lat) / 2;
    const midLng = (stop1.lng + stop2.lng) / 2;
    const newStop = { lat: midLat, lng: midLng, title: `Stop ${index + 2}`, color: '', duration: 0 };
    stops.splice(index + 1, 0, newStop);
    stops = stops;
    updateMarkers();
  }

  function setStopDuration(index: number, minutes: number) {
    stops[index].duration = minutes;
    stops = stops;
  }

  onMount(() => {
    const saved = localStorage.getItem('recentLocations');
    if (saved) {
      try {
        recentLocations = JSON.parse(saved);
      } catch (e) {
        recentLocations = [];
      }
    }
    const savedFavorites = localStorage.getItem('favoriteLocations');
    if (savedFavorites) {
      try {
        favoriteLocations = JSON.parse(savedFavorites);
      } catch (e) {
        favoriteLocations = [];
      }
    }
    loadTemplates();
    loadFromQuery();
  });

  function saveToRecent(place: any) {
    const exists = recentLocations.find(p => p.lat === place.lat && p.lng === place.lng);
    if (!exists) {
      recentLocations = [place, ...recentLocations.slice(0, 9)];
      localStorage.setItem('recentLocations', JSON.stringify(recentLocations));
    }
  }

  function toggleFavorite(place: any) {
    const isFav = favoriteLocations.find(p => p.lat === place.lat && p.lng === place.lng);
    if (isFav) {
      favoriteLocations = favoriteLocations.filter(p => !(p.lat === place.lat && p.lng === place.lng));
    } else {
      favoriteLocations = [...favoriteLocations, place];
    }
    localStorage.setItem('favoriteLocations', JSON.stringify(favoriteLocations));
  }

  function isFavorited(place: any): boolean {
    return favoriteLocations.some(p => p.lat === place.lat && p.lng === place.lng);
  }

  function addStopFromLocation(place: any) {
    stops = [...stops, { lat: place.lat, lng: place.lng, title: place.name || '', color: '' }];
    updateMarkers();
    fetchPoisForStop(stops.length - 1);
    showFavorites = false;
    showRecent = false;
  }

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
      const res = await fetch(`http://localhost:8000/api/route/enhanced`, {
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

  async function fetchTransitForSegment(i: number) {
    const start = stops[i];
    const end = stops[i + 1];
    if (!start || !end) return;
    try {
      const res = await fetch('http://localhost:8000/api/route/enhanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_lat: start.lat,
          start_lng: start.lng,
          end_lat: end.lat,
          end_lng: end.lng,
          walk_only: false
        })
      });
      const data = await res.json();
      segmentTransit[i] = {
        options: data.transit_options || [],
        instructions: data.instructions || []
      };
      segmentTransit = [...segmentTransit];
    } catch (e) {
      console.warn('segment transit fetch failed', e);
    }
  }

  async function fetchTransitDetailsForSegment(i: number, option: any) {
    const start = stops[i];
    const end = stops[i + 1];
    if (!start || !end) return;
    try {
      const res = await fetch('http://localhost:8000/api/route/enhanced', {
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
      const data = await res.json();
      segmentSelectedTransit[i] = option;
      segmentRouteOptions[i] = data.route_options || [];
      segmentSelectedTransit = [...segmentSelectedTransit];
      segmentRouteOptions = [...segmentRouteOptions];
    } catch (e) {
      console.warn('segment transit-detail failed', e);
    }
  }

  async function applyWalkingPathToTransit(i: number, option: any) {
    const start = stops[i];
    if (!start || !option) return;
    try {
      const res = await fetch('http://localhost:8000/api/route/enhanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_lat: start.lat,
          start_lng: start.lng,
          end_lat: option.stop_lat,
          end_lng: option.stop_lng,
          walk_only: true
        })
      });
      const data = await res.json();
      if (Array.isArray(data.polyline)) {
        polyline = data.polyline.map((p: [number, number]) => ({ lat: p[0], lng: p[1] }));
        distance = data.distance_m || 0;
        duration = data.duration_s || 0;
      }
    } catch (e) {
      console.warn('walking path fetch failed', e);
    }
  }

  function calculateTotalTransitTime(): number {
    let total = 0;
    for (let i = 0; i < stops.length - 1; i++) {
      if (segmentRouteOptions[i] && segmentRouteOptions[i].length > 0) {
        const firstOption = segmentRouteOptions[i][0];
        total += (firstOption.total_duration_min || 0);
      }
    }
    return total;
  }

  let searchValue = "";
  let alternatives: any[] = [];

  function handleMapClick(e: CustomEvent<{ lat: number; lng: number }>) {
    stops = [...stops, { lat: e.detail.lat, lng: e.detail.lng, title: "", color: "" }];
    updateMarkers();
    fetchPoisForStop(stops.length - 1);
  }

  function addStopFromSearch(r: any) {
    if (!r || !r.lat || !r.lon) return;
    stops = [...stops, { lat: r.lat, lng: r.lon, title: r.name || "", color: "" }];
    updateMarkers();
    searchValue = "";
    fetchPoisForStop(stops.length - 1);
  }

  function updateMarkers() {
    markers = stops.map((s, i) => ({
      ...s,
      title: i === 0 ? "Start" : i === stops.length - 1 ? "Destination" : `Stop ${i}`,
      color: i === 0 ? "green" : i === stops.length - 1 ? "red" : "yellow"
    }));
  }

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

  function clearAll() {
    stops = []; markers = []; polyline = []; distance = 0; duration = 0;
  }

  async function getRoute() {
    if (stops.length < 2) {
      errorMessage = "Please add at least Start + Destination.";
      return;
    }
    isLoading = true;
    errorMessage = "";
    stops.forEach(stop => saveToRecent(stop));
    try {
      const res = await fetch("http://localhost:8000/api/route/multistop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ points: stops.map((s) => ({ lat: s.lat, lng: s.lng })) })
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      if (!Array.isArray(data.polyline)) {
        alert("Backend returned invalid polyline.");
        return;
      }
      polyline = data.polyline.map((p: [number, number]) => ({ lat: p[0], lng: p[1] }));
      poiMarkers = [];
      distance = data.distance_m;
      duration = data.duration_s;
      instructions = data.instructions || [];
      transitOptions = data.transit_options || [];
      showInstructions = (instructions.length > 0) || (transitOptions.length > 0);
      updateMarkers();
    } catch (error) {
      errorMessage = 'Failed to get route. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  async function optimizeRoute() {
    if (stops.length < 3) {
      errorMessage = "Add at least 3 stops for AI optimization.";
      return;
    }
    isLoading = true;
    errorMessage = "";
    try {
      const res = await fetch("http://localhost:8000/tsp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ points: stops.map(s => ({ lat: s.lat, lng: s.lng })) })
      });
      const data = await res.json();
      if (data.error) {
        errorMessage = `Optimization error: ${data.error}`;
        return;
      }
      if (data.optimized) {
        stops = data.optimized.map((p: any) => ({ lat: p.lat, lng: p.lng, title: "", color: "" }));
        updateMarkers();
      }
      if (Array.isArray(data.polyline)) {
        polyline = data.polyline.map((p: [number, number]) => ({ lat: p[0], lng: p[1] }));
        distance = data.distance_m || 0;
        duration = data.duration_s || 0;
      } else {
        errorMessage = "Failed to get optimized route polyline.";
      }
    } catch (error) {
      errorMessage = 'Failed to optimize route. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  async function fetchNearby(i: number) {
    const s = stops[i];
    if (!s) return;
    try {
      // FIXED: Completed backticks and string interpolation
      const res = await fetch(`http://localhost:8000/api/nearby?lat=${s.lat}&lng=${s.lng}`);
      const data = await res.json();
      poiMarkers = (data.results || []).map((p: any) => ({ lat: p.lat, lng: p.lon || p.lng, name: p.name, description: p.desc, type: p.type }));
      showPois = true;
    } catch (e) {
      console.warn('nearby fetch failed', e);
      poiMarkers = [];
    }
  }

  async function fetchPoisForStop(i: number, limit = 5, category?: string) {
    const s = stops[i];
    if (!s) return;
    try {
      const url = new URL('http://localhost:8000/api/pois/nearby');
      url.searchParams.set('lat', String(s.lat));
      url.searchParams.set('lng', String(s.lng));
      url.searchParams.set('limit', String(limit));
      if (category) url.searchParams.set('category', category);
      const res = await fetch(url.toString());
      if (!res.ok) throw new Error(`status ${res.status}`);
      const data = await res.json();
      let results = (data.results || []).map((p: any) => ({ ...p }));
      if (category) {
        results = results.filter((p: any) =>
          (p.type && String(p.type).toLowerCase().includes(category.toLowerCase())) ||
          (p.tags && Array.isArray(p.tags) && p.tags.some((t: string) => String(t).toLowerCase().includes(category.toLowerCase())))
        );
      }
      stopSuggestions[i] = results;
      stopSuggestions = [...stopSuggestions];
    } catch (e) {
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
    fetchPoisForStop(i + 1);
  }

  async function routeToPoi(i: number, poi: any) {
    const s = stops[i];
    if (!s || !poi) return;
    try {
      const res = await fetch('http://localhost:8000/api/route/enhanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_lat: s.lat,
          start_lng: s.lng,
          end_lat: poi.lat,
          end_lng: poi.lon || poi.lng,
          walk_only: false
        })
      });
      const data = await res.json();
      if (Array.isArray(data.polyline)) {
        polyline = data.polyline.map((p: [number, number]) => ({ lat: p[0], lng: p[1] }));
        distance = data.distance_m || 0;
        duration = data.duration_s || 0;
        poiMarkers = [{ lat: poi.lat, lng: poi.lon || poi.lng, name: poi.name }];
        showPois = true;
      }
    } catch (e) {
      console.warn('routeToPoi failed', e);
    }
  }

  function svgPreviewPath(points: [number, number][], w = 160, h = 60) {
    if (!points || points.length === 0) return '';
    const lats = points.map(p => p[0]);
    const lngs = points.map(p => p[1]);
    const minLat = Math.min(...lats), maxLat = Math.max(...lats);
    const minLng = Math.min(...lngs), maxLng = Math.max(...lngs);
    const latRange = maxLat - minLat || 0.0001;
    const lngRange = maxLng - minLng || 0.0001;
    const coords = points.map(p => {
      const x = ((p[1] - minLng) / lngRange) * (w - 8) + 4;
      const y = (1 - (p[0] - minLat) / latRange) * (h - 8) + 4;
      return `${x},${y}`;
    });
    return `M ${coords.join(' L ')}`;
  }

  function saveItinerary(name = "untitled") {
    const payload = { name, stops };
    const key = `itinerary:${name}`;
    localStorage.setItem(key, JSON.stringify(payload));
    alert(`Saved as ${key}`);
  }

  function shareItinerary() {
    const encoded = encodeURIComponent(JSON.stringify(stops));
    const url = `${location.origin}${location.pathname}?stops=${encoded}`;
    navigator.clipboard?.writeText(url).then(() => alert('Share link copied to clipboard'));
  }

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

  async function getAlternatives() {
    if (stops.length < 2) return;
    try {
      const res = await fetch('http://localhost:8000/api/route/enhanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stops })
      });
      const data = await res.json();
      alternatives = data.alternatives || [];
    } catch (e) { alternatives = []; }
  }
</script>

<div class="card">
  <h1>Multi-Stop Route Planner</h1>

  <div class="top-row">
    <div class="left">
      <SearchBar bind:value={searchValue} placeholder="Search places or addresses" on:select={(e) => addStopFromSearch(e.detail)} />

      {#if errorMessage}
        <div class="error-banner">
          <span class="error-text">{errorMessage}</span>
          <button class="error-close" on:click={() => errorMessage = ""}>×</button>
        </div>
      {/if}

      <div class="buttons">
        <button on:click={undo}>↩ Undo</button>
        <button on:click={clearAll}>🗑 Clear</button>
        <button on:click={getRoute} disabled={isLoading}>
          {#if isLoading}
            <span class="loading-spinner">⟳</span> Loading...
          {:else}
            🚀 Get Route
          {/if}
        </button>
        <button on:click={getAlternatives}>🔁 Alternatives</button>
        <button on:click={shareItinerary}>🔗 Share</button>
        <button on:click={saveAsTemplate}>💾 Save Template</button>
        <button class="template-btn" on:click={() => showTemplates = !showTemplates}>📋 Templates ({routeTemplates.length})</button>
      </div>

      {#if showTemplates && routeTemplates.length > 0}
        <div class="templates-panel">
          <h4>Route Templates</h4>
          {#each routeTemplates as template}
            <div class="template-item">
              <div class="template-info">
                <strong>{template.name}</strong>
                <span class="template-stops">{template.stops.length} stops</span>
              </div>
              <div class="template-actions">
                <button class="load-btn" on:click={() => loadTemplate(template)}>Load</button>
                <button class="delete-btn" on:click={() => deleteTemplate(template.id)}>×</button>
              </div>
            </div>
          {/each}
        </div>
      {/if}

      {#if favoriteLocations.length > 0 || recentLocations.length > 0}
        <div class="quick-access">
          {#if favoriteLocations.length > 0}
            <button class="quick-btn" on:click={() => showFavorites = !showFavorites}>
              ⭐ Favorites ({favoriteLocations.length})
            </button>
            {#if showFavorites}
              <div class="location-list">
                {#each favoriteLocations as loc}
                  <div class="location-item">
                    <div class="location-info">
                      <span class="location-name">{loc.title || `(${loc.lat.toFixed(4)}, ${loc.lng.toFixed(4)})`}</span>
                    </div>
                    <button class="action-btn" on:click={() => addStopFromLocation(loc)}>Add</button>
                  </div>
                {/each}
              </div>
            {/if}
          {/if}

          {#if recentLocations.length > 0}
            <button class="quick-btn" on:click={() => showRecent = !showRecent}>
              🕐 Recent ({recentLocations.length})
            </button>
            {#if showRecent}
              <div class="location-list">
                {#each recentLocations as loc}
                  <div class="location-item">
                    <div class="location-info">
                      <span class="location-name">{loc.title || `(${loc.lat.toFixed(4)}, ${loc.lng.toFixed(4)})`}</span>
                    </div>
                    <button class="action-btn" on:click={() => addStopFromLocation(loc)}>Add</button>
                  </div>
                {/each}
              </div>
            {/if}
          {/if}
        </div>
      {/if}

      {#if distance && showSummary}
        <div class="route-summary">
          <div class="summary-header">
            <h3>📊 Route Summary</h3>
            <button class="toggle-btn" on:click={() => showSummary = !showSummary}>−</button>
          </div>
          <div class="summary-stats">
            <div class="stat-item">
              <span class="stat-label">Total Stops</span>
              <span class="stat-value">{stops.length}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Distance</span>
              <span class="stat-value">{(distance / 1000).toFixed(1)} km</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Est. Transit Time</span>
              <span class="stat-value">{calculateTotalTransitTime() > 0 ? calculateTotalTransitTime() + ' min' : Math.round(duration / 60) + ' min'}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Stop Waits</span>
              <span class="stat-value">{stops.reduce((acc, s) => acc + (s.duration || 0), 0)} min</span>
            </div>
          </div>
        </div>
      {/if}

      <div class="stops">
        <h3>Stops</h3>
        {#if stops.length === 0}
          <div class="empty-state">
            <div class="empty-icon">🗺️</div>
            <h4>No stops added yet</h4>
            <p>Click on the map or use the search bar to add your first stop</p>
          </div>
        {:else}
          <ol>
            {#each stops as s, i}
              <li class="stop-row" style="border-left: 4px solid {getStopColor(i)};">
                <div class="stop-icon">{getStopIcon(i)}</div>
                <div class="left-col">
                  <span class="drag-handle">☰</span>
                  <input class="title" value={s.title} placeholder={`Stop ${i + 1}`} on:input={(ev: Event) => updateTitle(i, (ev.currentTarget as HTMLInputElement).value)} />
                  <input
                    type="number"
                    class="duration-input"
                    placeholder="Wait (min)"
                    value={s.duration || 0}
                    on:input={(ev: Event) => setStopDuration(i, parseInt((ev.currentTarget as HTMLInputElement).value) || 0)}
                    min="0"
                    max="999"
                  />
                </div>
                <div class="right-col">
                  <button title="Move up" on:click={() => moveUp(i)}>⬆</button>
                  <button title="Move down" on:click={() => moveDown(i)}>⬇</button>
                  <button title="Nearby POIs" on:click={() => fetchNearby(i)}>📍</button>
                  <button title="Remove" on:click={() => removeAt(i)}>✖</button>
                </div>
                <div class="coords">({s.lat.toFixed(5)}, {s.lng.toFixed(5)})</div>
              </li>

              {#if i < stops.length - 1}
                <li class="insert-between">
                  <button class="insert-btn" on:click={() => insertStopBetween(i)}>
                    ➕ Insert Stop
                  </button>
                </li>
                <li class="segment-transit">
                  <div class="segment-header">
                    <strong>Transit leg {i + 1}: {stops[i].title || `Stop ${i+1}`} → {stops[i+1].title || `Stop ${i+2}`}</strong>
                    <button class="segment-fetch" on:click={() => fetchTransitForSegment(i)}>Find Options</button>
                  </div>
                  {#if segmentTransit[i] && (segmentTransit[i].options.length > 0 || segmentTransit[i].instructions.length > 0)}
                    <div class="segment-options">
                      {#each segmentTransit[i].options as opt}
                        <div class="transit-option-wrapper">
                          <button class="transit-option" on:click={() => fetchTransitDetailsForSegment(i, opt)}>
                            <div class="transit-icon">{opt.type === 'MTR' ? '🚇' : (opt.type === 'Bus' ? '🚌' : '⛴️')}</div>
                            <div class="transit-details">
                              <strong>{opt.stop_name}</strong>
                              <p>{opt.instruction}</p>
                            </div>
                            <div class="arrow">→</div>
                          </button>
                          <button class="walk-path-btn" on:click={() => applyWalkingPathToTransit(i, opt)} title="Show walking path to this stop">🚶</button>
                        </div>
                      {/each}
                    </div>
                  {/if}
                  {#if segmentRouteOptions[i] && segmentRouteOptions[i].length > 0}
                    <div class="segment-route-options">
                      {#each segmentRouteOptions[i] as ro}
                        <div class="route-option-card">
                          <div class="option-header">
                            <h4>{ro.option_name}</h4>
                            <span class="duration-badge">{ro.total_duration_min} min</span>
                          </div>
                          <div class="option-summary">
                            {#each ro.steps as step}
                              <small>{step.type === 'walk' ? '🚶' : step.type === 'bus' ? '🚌' : step.type === 'mtr' ? '🚇' : '🔄'} {step.instruction}</small>
                            {/each}
                          </div>
                        </div>
                      {/each}
                    </div>
                  {/if}
                </li>
              {/if}

              <li class="nearby-chips">
                <span class="chips-label">Nearby:</span>
                <button class="chip" on:click={() => fetchPoisForStop(i, 5, 'mtr')}>MTR</button>
                <button class="chip" on:click={() => fetchPoisForStop(i, 5, 'bus')}>Bus</button>
                <button class="chip" on:click={() => fetchPoisForStop(i, 5, 'cafe')}>Cafe</button>
                <button class="chip" on:click={() => fetchPoisForStop(i, 5, 'restaurant')}>Food</button>
                <button class="chip" on:click={() => fetchPoisForStop(i, 5, 'park')}>Park</button>
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
                          <div class="poi-actions">
                            <button on:click={() => quickAddPoi(i, poi)}>+ Add</button>
                            <button on:click={() => { poiMarkers = [...poiMarkers, { lat: poi.lat, lng: poi.lon || poi.lng, name: poi.name }]; showPois = true; }}>Show</button>
                            <button on:click={() => routeToPoi(i, poi)}>Route</button>
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
                </div>
                <div class="alt-actions">
                  <button on:click={() => { polyline = (alt.polyline || []).map((p:[number,number])=>({lat:p[0],lng:p[1]})); distance = alt.distance_m || distance; duration = alt.duration_s || duration; }}>Apply</button>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      {#if showInstructions && (transitOptions.length > 0 || instructions.length > 0)}
        <div class="instructions-panel">
          <h2>🗺️ Route Instructions</h2>
          {#if transitOptions.length > 0}
            <div class="transit-section">
                </div>
          {/if}
        </div>
      {/if}
    </div>

    <div class="right">
      <LeafletMap {markers} {polyline} {poiMarkers} {showPois} on:mapclick={handleMapClick} center={{ lat: 22.3027, lng: 114.1772 }} />
    </div>
  </div>
</div>

<style>
  .card {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin: 20px;
    max-width: 100%;
  }

  h1 {
    margin: 0 0 20px 0;
    font-size: 2em;
    color: #333;
  }

  .top-row {
    display: grid;
    grid-template-columns: 600px 1fr;
    gap: 40px;
    height: calc(100vh - 200px);
    min-height: 600px;
  }

  .left {
    overflow-y: auto;
    overflow-x: hidden;
    border-right: 1px solid #e0e0e0;
    padding-right: 25px;
  }

  .right {
    border-radius: 8px;
    overflow: hidden;
    height: 100%;
    position: relative;
  }

  .right :global(.leaflet-container) {
    height: 100%;
    width: 100%;
  }

  .stops {
    margin-top: 30px;
  }

  .stops h3 {
    margin: 0 0 20px 0;
    font-size: 1.2em;
    color: #333;
  }

  .stops ol {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .stop-row {
    display: flex;
    align-items: center;
    padding: 20px;
    background: #f9f9f9;
    margin-bottom: 20px;
    border-radius: 8px;
  }

  .stop-icon {
    font-size: 1.6em;
    margin-right: 15px;
  }

  .left-col {
    flex: 1;
    display: flex;
    gap: 15px;
    align-items: center;
  }

  .title {
    flex: 1;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 1em;
  }

  .duration-input {
    width: 100px;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 0.9em;
  }

  .right-col {
    display: flex;
    gap: 10px;
  }

  .right-col button {
    padding: 10px 14px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9em;
  }

  .right-col button:hover {
    background: #0056b3;
  }

  .coords {
    font-size: 0.85em;
    color: #999;
    margin-top: 8px;
  }

  .insert-between {
    margin: 15px 0;
    text-align: center;
  }

  .insert-btn {
    padding: 8px 16px;
    background: #28a745;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9em;
  }

  .segment-transit {
    background: #e8f4f8;
    padding: 20px;
    margin: 20px 0;
    border-radius: 8px;
    border-left: 4px solid #17a2b8;
  }

  .segment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }

  .segment-header strong {
    font-size: 1em;
  }

  .segment-fetch {
    padding: 8px 16px;
    background: #17a2b8;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9em;
  }

  .nearby-chips {
    margin: 15px 0;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 6px;
  }

  .chips-label {
    font-weight: bold;
    margin-right: 10px;
    font-size: 0.95em;
  }

  .chip {
    padding: 8px 14px;
    margin: 4px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    font-size: 0.85em;
  }

  .suggestions-row {
    margin: 20px 0;
    padding: 20px;
    background: #fff3cd;
    border-radius: 8px;
    border-left: 4px solid #ffc107;
  }

  .suggestions strong {
    display: block;
    margin-bottom: 15px;
    font-size: 1em;
  }

  .suggest-grid {
    display: grid;
    gap: 15px;
  }

  .poi-card {
    background: white;
    padding: 15px;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  }

  .poi-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 10px;
  }

  .poi-name {
    font-weight: bold;
    font-size: 0.95em;
  }

  .poi-distance {
    color: #666;
    font-size: 0.85em;
  }

  .poi-actions {
    display: flex;
    gap: 8px;
  }

  .poi-actions button {
    padding: 6px 12px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85em;
  }

  .empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #999;
  }

  .empty-icon {
    font-size: 3em;
    margin-bottom: 10px;
  }

  .buttons {
    display: flex;
    gap: 10px;
    margin: 20px 0;
    flex-wrap: wrap;
  }

  .buttons button {
    padding: 12px 18px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
    margin-right: 8px;
    font-size: 0.95em;
  }

  .buttons button:hover {
    background: #0056b3;
  }

  :global(.search-bar) {
    margin-bottom: 20px;
  }

  .error-banner {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
    padding: 12px;
    border-radius: 4px;
    margin-bottom: 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .error-close {
    background: none;
    border: none;
    color: #721c24;
    font-size: 1.2em;
    cursor: pointer;
  }

  @media (max-width: 1200px) {
    .top-row {
      grid-template-columns: 1fr;
      height: auto;
    }

    .left {
      border-right: none;
      border-bottom: 1px solid #e0e0e0;
      padding-right: 0;
      padding-bottom: 20px;
    }
  }
</style>