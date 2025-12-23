<script lang="ts">
  import NearbyMap from "$lib/components/NearbyMap.svelte";

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
  let searchRadius = 800; // meters

  let activeType = "ALL";
  const types = ["ALL", "Bus Stop", "MTR", "Ferry Pier", "Minibus", "Taxi"];

  function useMyLocation() {
    navigator.geolocation.getCurrentPosition((pos) => {
      center = {
        lat: pos.coords.latitude,
        lng: pos.coords.longitude
      };
      fetchNearby();
    });
  }

  // ✅ FINAL FIXED FETCH FUNCTION
  async function fetchNearby() {
    loading = true;

    try {
      // Build URL with type filter if not ALL
      let url = `http://127.0.0.1:8000/api/nearby/?lat=${center.lat}&lng=${center.lng}&radius=${searchRadius}`;
      
      // If specific type selected, request it from backend
      if (activeType !== "ALL") {
        // Convert display name to backend type name
        const typeMap: { [key: string]: string } = {
          "Bus Stop": "Bus Stop",
          "MTR": "MTR",
          "Ferry Pier": "Ferry Pier",
          "Minibus": "Minibus",
          "Taxi": "Taxi Stand"
        };
        const backendType = typeMap[activeType] || activeType;
        url += `&types=${encodeURIComponent(backendType)}`;
        // Also increase limit when filtering by type to get more results
        url += "&limit=200";
      } else {
        // When showing ALL types, increase limit so we get a mix
        url += "&limit=200";
      }

      const res = await fetch(url);

      const data = await res.json();

      // 🔥 Critical final fix: backend returns {results: [...]}
      if (data && Array.isArray(data.results)) {
        // Deduplicate by name: keep first occurrence
        const seen = new Set<string>();
        stations = data.results.filter((s: Station) => {
          if (seen.has(s.name)) return false;
          seen.add(s.name);
          return true;
        });
      } else {
        console.warn("Nearby API returned unexpected structure:", data);
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
</script>

<div class="card">
  <h1>Nearby Stations</h1>

  <div class="controls">
    <button on:click={useMyLocation}>📍 Use My Location</button>
    <button on:click={fetchNearby}>🔍 Search Nearby</button>
  </div>

  <!-- Filter Buttons -->
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

  <h2>Nearest Stops:</h2>

 {#if loading}
  <p>Loading...</p>
{:else if stations.length === 0}
  <p>No stops found. Click on the map or use your location to search.</p>
{:else}
  <ul class="list">
      {#each stations as s (s.name)}
          <li>
              <b>{s.type}</b> — {s.name}<br />
              {Math.round(s.distance)} m • {Math.round(s.walk_min)} min walk
          </li>
      {/each}
  </ul>
{/if}

</div>

<style>
  .card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    width: 900px;
    margin: auto;
    box-shadow: 0 4px 18px rgba(0,0,0,0.06);
  }
  .controls {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
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
  }
  button.selected {
    background: #1e40af;
  }
  .list {
    line-height: 1.5rem;
  }
</style>
