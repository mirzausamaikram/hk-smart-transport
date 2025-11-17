<script lang="ts">
  // FIX: Changed 'searchRoute' to the correct function for this page
  import { saveItinerary } from '$lib/api'; 
  import MapComponent from '$lib/components/MapComponents.svelte';


  let stopsInput = '';
  let touristMode = false;
  let result: any = null;
  let loading = false;
  let mapMarkers: {lat:number; lng:number; title:string}[] = [];

  async function handleSubmit() {
    const stops = stopsInput.split(',').map(s => s.trim()).filter(Boolean);
    if (stops.length < 2) { alert('Enter at least 2 stops'); return; }
    loading = true;
    try {
      // FIX: Now calling the correctly imported function
      result = await saveItinerary({ stops, tourist_mode: touristMode }); 
      // NOTE: Map markers use hardcoded offsets; this will be updated with real coordinates later
      mapMarkers = stops.map((s,i) => ({ lat: 22.3+i*0.01, lng: 114.17+i*0.01, title: s }));
    } catch (e) {
      console.error(e);
      alert('Error generating itinerary');
    } finally {
      loading = false;
    }
  }
</script>

<h1>Itinerary Solver</h1>

<form on:submit|preventDefault={handleSubmit}>
  <label>
    Stops (comma-separated):
    <input bind:value={stopsInput} placeholder="Central, Tsim Sha Tsui, Mong Kok" />
  </label>
  <br/><br/>
  <label>
    <input type="checkbox" bind:checked={touristMode} />
    Tourist mode (add museums/restaurants)
  </label>
  <br/><br/>
  <button type="submit" disabled={loading}>Generate Itinerary</button>
</form>

{#if result}
  <h2>Itinerary</h2>
  <p>Total time: {result.itinerary.total_time} min | Fare: HK${result.itinerary.total_fare}</p>
  <ol>
    {#each result.itinerary.stops as stop}
      <li>{stop}</li>
    {/each}
  </ol>

  {#if touristMode && result.itinerary.pois}
    <h3>Suggested POIs</h3>
    <ul>
      {#each result.itinerary.pois as poi}
        <li>{poi.name} ({poi.dwell_time} min)</li>
      {/each}
    </ul>
  {/if}

  <h3>Map (approximate)</h3>
  <MapComponent lat={22.3029} lng={114.1772} zoom={12} markers={mapMarkers} />
{/if}