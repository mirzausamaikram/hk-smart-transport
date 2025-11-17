<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { searchRoute } from '$lib/api';
  import MapComponent from '$lib/components/MapComponents.svelte'; 

  let start = '';
  let end = '';
  let preference: 'fastest' | 'cheapest' | 'fewest' = 'fastest';
  let transportMode: 'transit' | 'bus' | 'mtr' | 'taxi' = 'transit'; 
  let result: any = null;
  let loading = false;
  let geolocating = true;
  let mapMarkers: {lat:number; lng:number; title:string}[] = [];
  let polyline: string | null = null;
  let mapLat: number = 22.3029;
  let mapLng: number = 114.1772;
  let mapZoom: number = 12;

  async function fetchUserLocation() {
    if (!navigator.geolocation) {
      console.warn('Geolocation not supported by browser. Falling back to default.');
      start = 'Central, Hong Kong'; 
      geolocating = false;
      return;
    }

    navigator.geolocation.getCurrentPosition(
      pos => {
        const currentLat = pos.coords.latitude;
        const currentLng = pos.coords.longitude;
        
        start = `${currentLat},${currentLng}`;
        mapLat = currentLat;
        mapLng = currentLng;
        mapZoom = 14;
        
        mapMarkers = [{ 
            lat: currentLat, 
            lng: currentLng, 
            title: 'Your Current Location' 
        }];
        
        geolocating = false;
      },
      err => {
        console.error('Failed to get location:', err);
        start = 'Central, Hong Kong'; // Fallback address
        geolocating = false;
      },
      { enableHighAccuracy: false, timeout: 5000, maximumAge: 0 }
    );
  }

  onMount(() => {
    fetchUserLocation();
  });

  async function handleSubmit() {
    loading = true;
    polyline = null;
    
    try { 
      result = await searchRoute({ start, end, preference, transportMode }); 
      
      const route = result.routes[0];
      const startLoc = route.legs[0].start_location;
      const endLoc = route.legs[route.legs.length - 1].end_location;

      mapMarkers = [ 
        { lat: startLoc.lat, lng: startLoc.lng, title: `Start: ${start}` }, 
        { lat: endLoc.lat, lng: endLoc.lng, title: `End: ${end}` } 
      ]; 
      
      polyline = route.polyline;
      
      if (google?.maps?.geometry && polyline) {
        const bounds = new google.maps.LatLngBounds();
        const pathCoords = google.maps.geometry.encoding.decodePath(polyline);
        
        pathCoords.forEach((coord: any) => {
          bounds.extend(coord);
        });
        
        mapLat = bounds.getCenter().lat();
        mapLng = bounds.getCenter().lng();
        mapZoom = 13; 
      } else {
        if (mapMarkers.length === 2) {
          mapLat = (mapMarkers[0].lat + mapMarkers[1].lat) / 2;
          mapLng = (mapMarkers[0].lng + mapMarkers[1].lng) / 2;
          mapZoom = 13;
        }
      }
      
    } catch (e) { 
      console.error("Route search failed:", e);
      alert('Route search failed. Check console for details.');
    } finally { 
      loading = false;
    } 
  }
  function handleMapClick(e: CustomEvent) {
    const latLng: google.maps.LatLng = e.detail;
    const lat = latLng.lat();
    const lng = latLng.lng();
    end = `${lat},${lng}`;
    mapMarkers.push({ lat, lng, title: 'End Location' });
  }
  
  const goToItinerary = () => goto('/routes/Itinerary');
  const goToNearby = () => goto('/nearby');
</script>

<h1>Route Planner</h1>

<div class="nav-sub-bar">
    <button on:click={goToNearby} class="nav-button">
        📍 Nearby Station Finder
    </button>
    <button on:click={goToItinerary} class="nav-button">
        🗺️ Make Itinerary
    </button>
</div>

<div class="route-content">
  <div class="form-section card">
    <form on:submit|preventDefault={handleSubmit}>
      <h2>Plan Your Route</h2>
      <label>
        Start Location:
        <input 
          bind:value={start}
          required 
          placeholder="e.g. Central (or your current location)" 
          disabled={geolocating}
        />
        {#if geolocating}
          <small class="loading-text">Fetching current location...</small>
        {/if}
      </label>
      <br/><br/>
      <label>
        End Location:
        <input bind:value={end} required placeholder="Where do you want to go?" />
      </label>
      <br/><br/>
      
      <div class="mode-options">
        <label>
            Transport Mode:
            <select bind:value={transportMode}>
                <option value="transit">Public Transport (All)</option>
                <option value="mtr">MTR Only</option>
                <option value="bus">Bus / Minibus Only</option>
                <option value="taxi">Taxi / Car</option>
            </select>
        </label>
        
        <label>
          Preference:
          <select bind:value={preference}>
            <option value="fastest">Fastest</option>
            <option value="cheapest">Cheapest</option>
            <option value="fewest">Fewest transfers</option>
          </select>
        </label>
      </div>

      <br/>
      <button type="submit" disabled={loading || geolocating || !end.trim()}>
        {#if loading}
          Searching...
        {:else}
          Find Route
        {/if}
      </button>
    </form>
    
    {#if result}
      <div class="results-card">
        <h3>Optimal Route Found</h3>
        <p class="summary-line">
            Time: <span class="data-highlight">{result.routes[0].time}</span> |
            Fare: <span class="data-highlight">HK${result.routes[0].fare}</span> |
            Transfers: <span class="data-highlight">{result.routes[0].transfers}</span>
        </p> 
        <h4>Step-by-Step Instructions:</h4>
        <ol class="steps-list">
          {#each result.routes[0].steps as step}
            <li>{step.instruction}</li>
          {/each}
        </ol>
      </div>
    {/if}
  </div>

  <div class="map-section">
    <h3>Interactive Route Map</h3>
    <div class="map-wrapper">
        <MapComponent 
          lat={mapLat} 
          lng={mapLng} 
          zoom={mapZoom} 
          markers={mapMarkers} 
          polyline={polyline} 
          on:mapclick={handleMapClick} 
        />
    </div>
  </div>
</div>


<style>
    /* Global Page Layout */
    :global(body) {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        background-color: #f4f7f6;
        color: #333;
    }
    h1 {
        color: #007bff;
        border-bottom: 2px solid #007bff;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    /* Navigation Sub-Bar */
    .nav-sub-bar {
        display: flex;
        justify-content: flex-end;
        gap: 15px;
        margin-bottom: 25px;
    }
    .nav-button {
        padding: 10px 15px;
        border: 1px solid #007bff;
        background-color: #ffffff;
        color: #007bff;
        cursor: pointer;
        font-weight: 600;
        border-radius: 6px;
        transition: all 0.2s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .nav-button:hover {
        background-color: #007bff;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 123, 255, 0.3);
    }
    
    /* Main Content Layout */
    .route-content {
      display: flex;
      gap: 30px;
    }
    
    .form-section {
      flex: 1;
      min-width: 400px;
    }
    .map-section {
      flex: 2;
      min-width: 500px;
    }

    .map-wrapper {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        height: 600px;
        /* Define a fixed height for the map container */
    }
    
    /* Card Styles */
    .card {
        background: #ffffff;
        padding: 30px;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
        margin-bottom: 30px;
    }
    .results-card {
        background: #e9f5ff; /* Light blue background for results */
        padding: 20px;
        border-radius: 8px;
        margin-top: 20px;
        border: 1px solid #cce5ff;
    }

    /* Form Element Styling */
    form h2, .results-card h3 {
        color: #0056b3;
        margin-top: 0;
        margin-bottom: 20px;
        font-size: 1.5em;
        font-weight: 500;
    }
    form label {
      display: block;
      margin-bottom: 15px;
      font-weight: 600;
      color: #555;
    }
    form input, form select {
      width: 100%;
      padding: 12px;
      box-sizing: border-box;
      margin-top: 5px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 1em;
      transition: border-color 0.2s;
    }
    form input:focus, form select:focus {
        border-color: #007bff;
        outline: none;
        box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
    }
    .mode-options {
      display: flex;
      gap: 20px;
      margin-top: 15px;
    }
    .mode-options label {
      flex: 1;
      font-weight: 500;
      margin-bottom: 0;
    }
    
    /* Submit Button */
    form button[type="submit"] {
      width: 100%;
      padding: 15px;
      background-color: #007bff;
      color: white;
      border: none;
      cursor: pointer;
      border-radius: 6px;
      font-size: 1.2em;
      font-weight: bold;
      margin-top: 25px;
      transition: background-color 0.2s, box-shadow 0.2s;
    }
    form button[type="submit"]:hover:not(:disabled) {
      background-color: #0056b3;
      box-shadow: 0 4px 8px rgba(0, 123, 255, 0.4);
    }
    form button:disabled {
      background-color: #cccccc;
      cursor: not-allowed;
      box-shadow: none;
    }
    .loading-text {
      display: block;
      color: #007bff;
      font-style: italic;
      margin-top: 5px;
      font-weight: normal;
      font-size: 0.9em;
    }

    /* Results Formatting */
    .summary-line {
        font-size: 1.1em;
        font-weight: 500;
        margin-bottom: 15px;
        color: #333;
    }
    .data-highlight {
        color: #28a745; /* Green for key data */
        font-weight: bold;
    }
    h4 {
        color: #0056b3;
        margin-top: 15px;
        margin-bottom: 10px;
        font-size: 1.1em;
    }
    .steps-list {
        padding-left: 20px;
        list-style-type: decimal;
    }
    .steps-list li {
        margin-bottom: 8px;
        line-height: 1.4;
    }
</style>