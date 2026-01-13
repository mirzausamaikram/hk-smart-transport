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
      const res = await fetch(`http:
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


  async function fetchTransitForSegment(i: number) {
    const start = stops[i];
    const end = stops[i + 1];
    if (!start || !end) return;
    try {
      const res = await fetch('http:
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
      const res = await fetch('http:
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
      const res = await fetch('http:
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
    stops = [...stops, {
      lat: e.detail.lat,
      lng: e.detail.lng,
      title: "",
      color: ""
    }];
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




  function clearAll() {
    stops = [];
    markers = [];
    polyline = [];
    distance = 0;
    duration = 0;
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
      const res = await fetch("http:
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

      poiMarkers = [];

      distance = data.distance_m;
      duration = data.duration_s;


      instructions = data.instructions || [];
      transitOptions = data.transit_options || [];
      showInstructions = (instructions.length > 0) || (transitOptions.length > 0);

      updateMarkers();
    } catch (error) {
      console.error('Error fetching multistop route:', error);
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
      const res = await fetch("http:
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          points: stops.map(s => ({ lat: s.lat, lng: s.lng }))
        })
      });

      const data = await res.json();

      if (data.error) {
        errorMessage = `Optimization error: ${data.error}`;
        return;
      }

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

        distance = data.distance_m || 0;
        duration = data.duration_s || 0;
      } else {
        errorMessage = "Failed to get optimized route polyline.";
      }
    } catch (error) {
      console.error('Error optimizing route:', error);
      errorMessage = 'Failed to optimize route. Please try again.';
    } finally {
      isLoading = false;
    }
  }


  async function fetchNearby(i: number) {
    const s = stops[i];
    if (!s) return;

    try {
      const res = await fetch(`http:
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
      const url = new URL('http:
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

    fetchPoisForStop(i + 1);
  }


  async function routeToPoi(i: number, poi: any) {
    const s = stops[i];
    if (!s || !poi) return;
    try {
      const res = await fetch('http:
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
    const pad = 0.02;
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
    const res = await fetch('http:
    try {
      const data = await res.json();
      alternatives = data.alternatives || [];
    } catch (e) { alternatives = []; }
  }


  const originalOnMount = onMount;
  onMount(() => {
    loadFromQuery();
  });
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
              {/if}

              {#if i < stops.length - 1}
                <li class="segment-transit">
                  <div class="segment-header">
                    <strong>Transit for leg {i + 1}: {stops[i].title || `Stop ${i+1}`} → {stops[i+1].title || `Stop ${i+2}`}</strong>
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
                <button class="chip" title="Nearby MTR" on:click={() => fetchPoisForStop(i, 5, 'mtr')}>MTR</button>
                <button class="chip" title="Nearby Bus Stops" on:click={() => fetchPoisForStop(i, 5, 'bus')}>Bus</button>
                <button class="chip" title="Nearby Cafes" on:click={() => fetchPoisForStop(i, 5, 'cafe')}>Cafe</button>
                <button class="chip" title="Nearby Restaurants" on:click={() => fetchPoisForStop(i, 5, 'restaurant')}>Food</button>
                <button class="chip" title="Nearby Parks" on:click={() => fetchPoisForStop(i, 5, 'park')}>Park</button>
                <button class="chip" title="Nearby Museums" on:click={() => fetchPoisForStop(i, 5, 'museum')}>Museum</button>
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
    background: linear-gradient(135deg, #ffffff 0%, #f8fafb 100%);
    padding: 20px;
    margin: 20px auto;
    width: 90%;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08), 0 0 40px rgba(59, 130, 246, 0.05);
    border: 1px solid rgba(59, 130, 246, 0.1);
  }

  h1 {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 20px 0;
    font-size: 28px;
    font-weight: 700;
  }

  .top-row {
    display: flex;
    gap: 20px;
    height: 500px;
    max-height: 500px;
    overflow: hidden;
  }

  .left {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    padding-right: 10px;
  }

  .right {
    flex: 1;
    min-width: 300px;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  }


  .error-banner {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    border: 1px solid #fca5a5;
    border-radius: 10px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 15px;
    animation: slideDown 0.3s ease-out;
  }

  .error-text {
    color: #991b1b;
    font-weight: 500;
    font-size: 14px;
  }

  .error-close {
    background: transparent;
    border: none;
    color: #991b1b;
    font-size: 20px;
    cursor: pointer;
    padding: 0;
    display: flex;
    align-items: center;
  }

  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }


  .buttons {
    display: flex;
    gap: 8px;
    margin-bottom: 15px;
    margin-top: 15px;
    flex-wrap: wrap;
  }

  button {
    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    color: white;
    border: none;
    padding: 10px 16px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: 500;
    font-size: 13px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    display: flex;
    align-items: center;
    gap: 6px;
  }

  button:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
  }

  button:active:not(:disabled) {
    transform: translateY(0);
  }

  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .loading-spinner {
    display: inline-block;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    from {
      transform: rotate(0deg);
    }
    to {
      transform: rotate(360deg);
    }
  }


  .quick-access {
    margin-bottom: 15px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .quick-btn {
    background: linear-gradient(135deg, #ec4899 0%, #db2777 100%);
    box-shadow: 0 2px 8px rgba(236, 72, 153, 0.3);
  }

  .quick-btn:hover {
    box-shadow: 0 4px 16px rgba(236, 72, 153, 0.4);
  }

  .location-list {
    background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%);
    border: 1px solid #fbcfe8;
    border-radius: 8px;
    padding: 8px;
    margin-top: 8px;
    max-height: 200px;
    overflow-y: auto;
  }

  .location-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px;
    background: white;
    border-radius: 6px;
    margin-bottom: 6px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }

  .location-info {
    flex: 1;
  }

  .location-name {
    font-size: 13px;
    font-weight: 500;
    color: #1f2937;
  }

  .action-btn {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    padding: 6px 12px;
    font-size: 12px;
    box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3);
  }

  .action-btn:hover {
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
  }


  .template-btn {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
  }

  .templates-panel {
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    border: 1px solid #fcd34d;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 15px;
    animation: slideDown 0.3s ease-out;
  }

  .templates-panel h4 {
    margin: 0 0 10px 0;
    color: #92400e;
    font-size: 14px;
  }

  .template-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background: white;
    border-radius: 6px;
    margin-bottom: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }

  .template-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .template-info strong {
    font-size: 13px;
    color: #1f2937;
  }

  .template-stops {
    font-size: 11px;
    color: #6b7280;
  }

  .template-actions {
    display: flex;
    gap: 6px;
  }

  .load-btn {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    padding: 6px 12px;
    font-size: 12px;
  }

  .delete-btn {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    padding: 6px 10px;
    font-size: 14px;
  }


  .route-summary {
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
    border: 1px solid #93c5fd;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 15px;
    box-shadow: 0 2px 10px rgba(59, 130, 246, 0.15);
    animation: slideDown 0.3s ease-out;
  }

  .summary-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }

  .summary-header h3 {
    margin: 0;
    font-size: 15px;
    color: #1e40af;
  }

  .toggle-btn {
    background: transparent;
    color: #1e40af;
    padding: 4px 8px;
    font-size: 16px;
    box-shadow: none;
  }

  .summary-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 12px;
  }

  .stat-item {
    background: white;
    padding: 10px;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }

  .stat-label {
    font-size: 11px;
    color: #6b7280;
    margin-bottom: 4px;
  }

  .stat-value {
    font-size: 18px;
    font-weight: 700;
    color: #1e40af;
  }


  .empty-state {
    text-align: center;
    padding: 40px 20px;
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    border-radius: 10px;
    border: 2px dashed #d1d5db;
  }

  .empty-icon {
    font-size: 48px;
    margin-bottom: 12px;
  }

  .empty-state h4 {
    margin: 0 0 8px 0;
    font-size: 16px;
    color: #1f2937;
  }

  .empty-state p {
    margin: 0;
    font-size: 13px;
    color: #6b7280;
  }


  .stops {
    margin: 15px 0;
  }

  .stops h3 {
    color: #1f2937;
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 10px;
  }

  .stops ol {
    padding-left: 0;
    list-style: none;
  }

  .stop-row {
    background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
    transition: all 0.3s ease;
    animation: fadeIn 0.3s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateX(-10px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  .stop-row:hover {
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
  }

  .stop-icon {
    font-size: 20px;
    display: flex;
    align-items: center;
  }


  .stop-row:first-child {
    border-left: 4px solid #10b981;
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    border: 2px solid #86efac;
  }

  .stop-row:last-child {
    border-left: 4px solid #ef4444;
    background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%);
    border: 2px solid #fca5a5;
  }

  .stop-row:not(:first-child):not(:last-child) {
    border-left: 4px solid #3b82f6;
    background: linear-gradient(135deg, #eff6ff 0%, #bfdbfe 100%);
    border: 2px solid #93c5fd;
  }

  .left-col {
    display: flex;
    gap: 12px;
    align-items: center;
    flex: 1;
    min-width: 300px;
  }

  .drag-handle {
    cursor: grab;
    color: #6b7280;
    font-weight: bold;
    font-size: 18px;
    line-height: 1;
    display: flex;
    align-items: center;
    padding: 2px 0;
  }

  .duration-input {
    padding: 6px 10px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 12px;
    width: 80px;
    background: white;
    transition: all 0.2s ease;
  }

  .duration-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
  }

  .title {
    padding: 10px 14px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
    background: white;
    transition: all 0.2s ease;
    height: 40px;
  }

  .title {
    flex: 1;
    font-weight: 500;
    min-width: 180px;
  }

  .title:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  .right-col {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .right-col button {
    padding: 8px 12px;
    font-size: 14px;
    background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
    height: 40px;
    min-width: 40px;
  }

  .coords {
    font-size: 11px;
    color: #6b7280;
    padding: 0;
    white-space: nowrap;
    display: flex;
    align-items: center;
    width: 100%;
    margin-top: -4px;
  }


  .suggestions-row {
    list-style: none;
    margin: 12px 0 16px 0;
  }

  .suggestions {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border: 1px solid #fcd34d;
    padding: 12px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(251, 191, 36, 0.15);
  }

  .suggestions strong {
    color: #92400e;
    font-size: 13px;
  }


  .segment-transit { margin: 8px 0 14px 0; }
  .segment-header { display:flex; justify-content: space-between; align-items:center; }
  .segment-header .segment-fetch { padding:6px 10px; font-size:12px; }
  .segment-options { display:flex; flex-wrap:wrap; gap:8px; margin-top:8px; }
  .segment-route-options { display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:10px; margin-top:10px; }


  .transit-option-wrapper {
    display: flex;
    gap: 6px;
    align-items: stretch;
  }

  .transit-option {
    flex: 1;
  }

  .walk-path-btn {
    padding: 8px 12px;
    font-size: 16px;
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    border: 1px solid #fbbf24;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 6px rgba(245, 158, 11, 0.2);
    transition: all 0.2s ease;
  }

  .walk-path-btn:hover {
    background: linear-gradient(135deg, #d97706 0%, #b45309 100%);
    box-shadow: 0 3px 10px rgba(245, 158, 11, 0.3);
  }


  .nearby-chips {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 8px 0 10px 0;
    padding: 4px 0;
  }

  .chips-label {
    font-size: 12px;
    color: #6b7280;
  }

  .chip {
    padding: 6px 10px;
    font-size: 12px;
    border-radius: 999px;
    border: 1px solid #e5e7eb;
    background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
    color: #1f2937;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .chip:hover {
    background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
    border-color: #93c5fd;
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
  }

  .suggest-grid {
    display: flex;
    gap: 8px;
    margin-top: 10px;
    flex-wrap: wrap;
  }

  .poi-card {
    background: white;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    padding: 10px;
    width: 200px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
  }

  .poi-card:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }

  .poi-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 8px;
  }

  .poi-name {
    font-weight: 600;
    font-size: 13px;
    color: #1f2937;
  }

  .poi-distance {
    font-size: 11px;
    color: #6b7280;
    white-space: nowrap;
  }

  .poi-hours, .poi-note {
    font-size: 11px;
    color: #6b7280;
    margin-top: 4px;
  }

  .poi-actions {
    display: flex;
    gap: 6px;
    margin-top: 8px;
  }

  .poi-actions button {
    flex: 1;
    padding: 6px;
    font-size: 12px;
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
  }


  .stats {
    margin-top: 15px;
    background: linear-gradient(135deg, #dbeafe 0%, #e0f2fe 100%);
    border: 1px solid #bae6fd;
    padding: 15px;
    border-radius: 10px;
    width: 100%;
    box-shadow: 0 2px 8px rgba(3, 102, 214, 0.1);
  }


  .alts-grid {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 12px;
  }

  .alt-card {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border: 1px solid #bae6fd;
    border-radius: 8px;
    padding: 12px;
    width: 180px;
    box-shadow: 0 2px 8px rgba(3, 102, 214, 0.1);
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: all 0.3s ease;
    cursor: pointer;
  }

  .alt-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 16px rgba(3, 102, 214, 0.2);
  }

  .alt-preview {
    width: 100%;
    height: 60px;
    background: linear-gradient(180deg, #f7fbff, #ffffff);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .alt-meta {
    margin-top: 10px;
    font-size: 12px;
    color: #0c4a6e;
    text-align: center;
  }

  .alt-actions {
    display: flex;
    gap: 8px;
    margin-top: 10px;
    width: 100%;
  }

  .alt-actions button {
    flex: 1;
    padding: 6px;
    font-size: 11px;
  }


  .transit-section {
    margin-top: 15px;
    padding: 12px;
    background: linear-gradient(135deg, #f0fdfa 0%, #d1fae5 100%);
    border: 1px solid #a7f3d0;
    border-radius: 8px;
  }

  .transit-section h3 {
    color: #065f46;
    margin: 0 0 10px 0;
    font-size: 14px;
  }

  .transit-option {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    background: white;
    border: 1px solid #d1fae5;
    border-radius: 6px;
    padding: 10px;
    margin-bottom: 8px;
    justify-content: flex-start;
  }

  .transit-icon {
    font-size: 20px;
    width: 30px;
    text-align: center;
  }

  .transit-details {
    flex: 1;
    text-align: left;
  }

  .transit-details strong {
    color: #1f2937;
    font-size: 13px;
  }

  .transit-details p {
    margin: 4px 0 0 0;
    font-size: 11px;
    color: #6b7280;
  }


  .route-options-section {
    margin-top: 15px;
    padding: 12px;
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border: 1px solid #fcd34d;
    border-radius: 8px;
  }

  .route-options-section h3 {
    color: #92400e;
    margin: 0 0 10px 0;
    font-size: 14px;
  }

  .options-grid {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .route-option-card {
    background: white;
    border: 2px solid transparent;
    border-radius: 8px;
    padding: 10px;
    text-align: left;
    transition: all 0.3s ease;
  }

  .route-option-card:hover {
    background: #fafaf9;
    border-color: #fbbf24;
  }

  .route-option-card.selected {
    background: #fffbeb;
    border-color: #f59e0b;
    box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
  }

  .option-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }

  .option-header h4 {
    margin: 0;
    font-size: 13px;
    color: #1f2937;
  }

  .duration-badge {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
  }

  .option-summary {
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 11px;
  }

  .step-icon {
    margin-right: 6px;
  }

  .route-action {
    margin-top: 10px;
  }

  .route-action button {
    width: 100%;
  }


  .instructions-list {
    margin-top: 15px;
    padding: 12px;
    background: linear-gradient(135deg, #f3e8ff 0%, #ede9fe 100%);
    border: 1px solid #e9d5ff;
    border-radius: 8px;
  }

  .instructions-list h3 {
    color: #5b21b6;
    margin: 0 0 10px 0;
    font-size: 14px;
  }

  .instructions-list ol {
    margin: 0;
    padding-left: 20px;
  }

  .instructions-list li {
    font-size: 12px;
    color: #1f2937;
    margin-bottom: 6px;
  }

  .instructions-list small {
    color: #6b7280;
  }


  .insert-between {
    display: flex;
    justify-content: center;
    padding: 8px 0;
    margin: 8px 0 12px 0;
  }

  .insert-btn {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    border: 2px solid #34d399;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    transition: all 0.2s ease;
  }

  .insert-btn:hover {
    background: linear-gradient(135deg, #059669 0%, #047857 100%);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    transform: translateY(-2px);
  }


  @keyframes slideDown {
    from {
      opacity: 0;
      max-height: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      max-height: 500px;
      transform: translateY(0);
    }
  }


  @media (max-width: 768px) {
    .top-row {
      flex-direction: column;
      height: auto;
      max-height: none;
    }

    .right {
      min-width: 100%;
      height: 300px;
    }

    .card {
      width: 95%;
    }
  }
</style>
