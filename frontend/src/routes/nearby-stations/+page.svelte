<script lang="ts">
  import NearbyMap from "$lib/components/NearbyMap.svelte";
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";

  type Station = {
    name: string;
    type: string;
    distance: number;
    walk_min: number;
    lat: number;
    lng: number;
  };

  let center = { lat: 22.3027, lng: 114.1772 };
  let stations: Station[] = [];
  let loading = false;
  let searchRadius = 800;

  let geoStatus: "idle" | "granted" | "prompt" | "denied" = "idle";
  let activeType = "ALL";
  const types = ["ALL", "Bus Stop", "MTR", "Ferry Pier", "Minibus", "Taxi"];

  function useMyLocation() {
    if (!("geolocation" in navigator)) {
      geoStatus = "denied";
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        center = {
          lat: pos.coords.latitude,
          lng: pos.coords.longitude
        };
        geoStatus = "granted";
        fetchNearby();
      },
      (err) => {
        geoStatus = err.code === 1 ? "denied" : "prompt";
        console.warn("Geolocation error:", err);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  }

  onMount(async () => {
    try {
      const nav = navigator as any;
      if (nav.permissions && nav.permissions.query) {
        const result = await nav.permissions.query({ name: "geolocation" });
        geoStatus = result.state;
        
        if (result.state === "granted") {
          useMyLocation();
        }
        
        result.onchange = () => {
          geoStatus = result.state;
        };
      } else {
        useMyLocation();
      }
    } catch (e) {
      console.warn("Permissions check failed:", e);
      useMyLocation(); // Fallback to prompt
    }
  });

  async function fetchNearby() {
    loading = true;
    try {
      // FIXED: Completed the template literal and added missing parameters
      let url = `http://localhost:8000/api/nearby?lat=${center.lat}&lng=${center.lng}&radius=${searchRadius}`;

      if (activeType !== "ALL") {
        const typeMap: { [key: string]: string } = {
          "Bus Stop": "Bus Stop",
          "MTR": "MTR",
          "Ferry Pier": "Ferry Pier",
          "Minibus": "Minibus",
          "Taxi": "Taxi Stand"
        };
        const backendType = typeMap[activeType] || activeType;
        url += `&types=${encodeURIComponent(backendType)}`;
      }
      
      url += "&limit=200";

      const res = await fetch(url);
      const data = await res.json();

      if (data && Array.isArray(data.results)) {
        const seen = new Set<string>();
        stations = data.results.filter((s: Station) => {
          const key = `${s.name}-${s.type}`; // Unique key to handle same names on different modes
          if (seen.has(key)) return false;
          seen.add(key);
          return true;
        });
      } else {
        stations = [];
      }
    } catch (err) {
      console.error("Nearby API error:", err);
      stations = [];
    }
    loading = false;
  }

  function mapClick(e: CustomEvent<{ lat: number; lng: number }>) {
    center = { lat: e.detail.lat, lng: e.detail.lng };
    fetchNearby();
  }

  function getDirections(station: Station) {
    const params = new URLSearchParams({
      fromLat: center.lat.toString(),
      fromLng: center.lng.toString(),
      fromName: 'Selected Location',
      toLat: station.lat.toString(),
      toLng: station.lng.toString(),
      toName: station.name
    });

    if (station.type === "Bus Stop" || station.type?.toLowerCase().includes("bus")) {
      params.set("walkOnly", "1");
    }
    goto(`/route-planner?${params.toString()}`);
  }

  function openInMaps(station: Station) {
    // FIXED: Completed the Google Maps URL
    const url = `https://www.google.com/maps/dir/?api=1&destination=${station.lat},${station.lng}&travelmode=walking`;
    window.open(url, '_blank');
  }
</script>

<div class="card">
  <h1>Nearby Stations</h1>

  {#if geoStatus === "denied"}
    <div class="permission-banner error">
      <span>📍 Location access is blocked. Enable it in browser settings or click on the map to set a point.</span>
      <button class="retry" on:click={useMyLocation}>Retry</button>
    </div>
  {/if}

  <div class="controls">
    <button on:click={useMyLocation}>📍 Use My Location</button>
    <button on:click={fetchNearby}>🔍 Search Nearby</button>
    <div class="radius">
      <label for="radius-input">Radius: {searchRadius} m</label>
      <input id="radius-input" type="range" min="200" max="2000" step="100" bind:value={searchRadius} on:change={fetchNearby} />
    </div>
  </div>

  <div class="filters">
    {#each types as t}
      <button
        class:selected={activeType === t}
        on:click={() => {
          activeType = t;
          fetchNearby();
        }}
      >
        {t}
      </button>
    {/each}
  </div>

  <NearbyMap {center} {stations} {searchRadius} on:mapclick={mapClick} />

  <p class="hint">Tip: Click anywhere or drag the blue dot to choose a location.</p>

  <h2>Nearest Stops:</h2>

  {#if loading}
    <p>Loading...</p>
  {:else if stations.length === 0}
    <p>No stops found. Click on the map or use your location to search.</p>
  {:else}
    <ul class="list">
      {#each stations as s (s.name)}
        <li>
          <div class="station-info">
            <div class="station-details">
              <b>{s.type}</b> — {s.name}<br />
              <span class="distance">{Math.round(s.distance)} m • {Math.round(s.walk_min)} min walk</span>
            </div>
            <div class="station-actions">
              <button class="action-btn" on:click={() => getDirections(s)} title="Get directions in Route Planner">
                🚶 Directions
              </button>
              <button class="action-btn maps" on:click={() => openInMaps(s)} title="Open in Google Maps">
                🗺️ Maps
              </button>
            </div>
          </div>
        </li>
      {/each}
    </ul>
  {/if}
</div>

<style>
  /* Styles remain identical to your original code */
  .card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    max-width: 900px; /* Changed to max-width for better responsiveness */
    margin: auto;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
    position: relative;
    z-index: 1;
  }
  .permission-banner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    background: #fee2e2; /* Light red for error */
    border: 1px solid #ef4444;
    color: #991b1b;
    padding: 10px 12px;
    border-radius: 10px;
    margin-bottom: 12px;
  }
  .permission-banner .retry {
    padding: 6px 12px;
    border: none;
    border-radius: 8px;
    background: #991b1b;
    color: white;
    cursor: pointer;
  }
  .controls {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
    flex-wrap: wrap;
  }
  .radius {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-left: auto;
  }
  .radius input[type="range"] {
    width: 200px;
  }
  .filters {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 12px;
  }
  button {
    padding: 8px 14px;
    border: none;
    border-radius: 8px;
    background: #334155;
    color: white;
    cursor: pointer;
    transition: opacity 0.2s;
  }
  button:hover {
    opacity: 0.9;
  }
  button.selected {
    background: #1e40af;
  }
  .list {
    list-style: none;
    padding: 0;
  }
  .list li {
    margin-bottom: 12px;
    padding: 12px;
    background: #f8fafc;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    transition: all 0.2s;
  }
  .list li:hover {
    background: #f1f5f9;
    border-color: #cbd5e1;
  }
  .station-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
  }
  .station-details {
    flex: 1;
  }
  .distance {
    color: #64748b;
    font-size: 0.9em;
  }
  .station-actions {
    display: flex;
    gap: 6px;
    flex-shrink: 0;
  }
  .action-btn {
    padding: 6px 12px;
    font-size: 0.85em;
    background: #3b82f6;
    border-radius: 6px;
    white-space: nowrap;
    transition: all 0.2s;
  }
  .action-btn:hover {
    background: #2563eb;
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  }
  .action-btn.maps {
    background: #10b981;
  }
  .action-btn.maps:hover {
    background: #059669;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
  }
  .hint {
    color: #64748b;
    font-size: 0.9rem;
    margin-top: 8px;
  }
</style>