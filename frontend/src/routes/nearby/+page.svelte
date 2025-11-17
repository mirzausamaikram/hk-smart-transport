<script lang="ts">
  import { onMount } from 'svelte';
  import { getNearby } from '$lib/api';
  import MapComponent from '$lib/components/MapComponents.svelte';

  let lat = 0;
  let lng = 0;
  let stops: any[] = [];
  let pois: string[] = [];
  let loading = false;
  let mapMarkers: {lat: number; lng: number; title: string}[] = [];

  async function locateAndSearch() {
    loading = true;
    if (!navigator.geolocation) {
      alert('Geolocation not supported');
      loading = false;
      return;
    }
    navigator.geolocation.getCurrentPosition(async (pos) => {
      lat = pos.coords.latitude;
      lng = pos.coords.longitude;

      const data = await getNearby(lat, lng);
      stops = data.stops;
      pois = data.pois;

      mapMarkers = stops.map(s => ({
        lat: s.lat,
        lng: s.lon,
        title: s.name
      }));
      loading = false;
    }, (err) => {
      console.error(err);
      alert('Failed to get location');
      loading = false;
    });
  }

  onMount(() => {
    locateAndSearch();
  });
</script>

<h1>Nearby Transport Finder</h1>
<p>Latitude: {lat.toFixed(4)}, Longitude: {lng.toFixed(4)}</p>

{#if loading}
  <p>Loading…</p>
{:else}
  <h2>Stops within 1 km</h2>
  <ul>
    {#each stops as stop}
      <li>{stop.name} – {stop.dist_m.toFixed(2)} m</li>
    {/each}
  </ul>

  <h2>Tourist POIs</h2>
  <ul>
    {#each pois as poi}
      <li>{poi}</li>
    {/each}
  </ul>

  <h3>Map</h3>
  <MapComponent lat={lat} lng={lng} zoom={14} markers={mapMarkers} />
{/if}
<style>
  :global(body) {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }
.map {
  width: 100%;
  height: 400px;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}
body {
  font-family: 'Arial', sans-serif;
  background-color: #f4f7f6;
  color: #333;
  line-height: 1.6;
  padding: 20px;
}

h1, h2, h3 {
  color: #007bff;
  margin-bottom: 15px;
}

h1 {
  font-size: 2em;
  margin-bottom: 20px;
}

h2 {
  font-size: 1.5em;
  margin-top: 20px;
}

h3 {
  font-size: 1.2em;
  margin-top: 20px;
}

p {
  margin-bottom: 15px;
}

ul {
  list-style: disc;
  margin-left: 20px;
}

li {
  margin-bottom: 5px;
}

.map-section {
  margin-top: 20px;
}

.map-component {
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  height: 400px;
  width: 100%;
}

.loading {
  color: #007bff;
  text-align: center;
  margin-top: 20px;
}

.error {
  color: #ff4d4d4d;
  text-align: center;
  margin-top: 20px;
}
</style>
