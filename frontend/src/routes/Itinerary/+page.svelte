<script lang="ts">
  import { onMount } from "svelte";
  import { marked } from "marked";
  import LeafletMap from "$lib/components/LeafletMap.svelte";

  type ItineraryOption = {
    id: number;
    title: string;
    itinerary: string;
    estimated_cost: string;
    duration: string;
  };

  type Coordinates = {
    lat: number;
    lng: number;
  };

  let start_place = "";
  let end_place = "";
  let transport = "MTR";
  let preference = "moderate";
  let selectedDate = "";
  let selectedTime = "";
  let budget = "";
  let interests: string[] = [];
  let loading = false;
  let itineraryOptions: ItineraryOption[] = [];
  let selectedOption: ItineraryOption | null = null;
  let errorMessage = "";


  let markers: Array<{ lat: number; lng: number; title: string; color: string }> = [];

  let poiMarkers: Array<{ lat: number; lng: number; name: string; description?: string; type?: string }> = [];
  let showPois = true;

  let routeOptions: any[] = [];
  let selectedRoute: any = null;
  let routePolyline: { lat: number; lng: number }[] = [];

  const preferences = [
    { id: "fast", label: "⚡ Fast", description: "Quickest routes" },
    { id: "cheap", label: "💰 Cheap", description: "Most economical" },
    { id: "tourist", label: "📸 Tourist", description: "Popular attractions" },
    { id: "sightseeing", label: "🏛️ Sightseeing", description: "Scenic routes" },
    { id: "moderate", label: "⚖️ Moderate", description: "Balanced experience" }
  ];

  const interestOptions = [
    { id: "food", label: "🍜 Food", icon: "🍜" },
    { id: "culture", label: "🏛️ Culture", icon: "🏛️" },
    { id: "shopping", label: "🛍️ Shopping", icon: "🛍️" },
    { id: "nature", label: "🌿 Nature", icon: "🌿" },
    { id: "nightlife", label: "🌃 Nightlife", icon: "🌃" },
    { id: "history", label: "📚 History", icon: "📚" },
    { id: "adventure", label: "🎢 Adventure", icon: "🎢" },
    { id: "relaxation", label: "🧘 Relaxation", icon: "🧘" }
  ];

  const transportOptions = ["MTR", "Bus", "Tram", "Ferry", "Walk", "Taxi", "Mixed"];

  onMount(() => {

    const today = new Date().toISOString().split('T')[0];
    selectedDate = today;
    selectedTime = "09:00";
  });

  function toggleInterest(id: string) {
    if (interests.includes(id)) {
      interests = interests.filter(i => i !== id);
    } else {
      interests = [...interests, id];
    }
  }

  async function geocodePlace(place: string): Promise<Coordinates | null> {
    try {
      const res = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(place)}&format=json`);
      const data = await res.json();
      if (data && data.length > 0) {
        return {
          lat: parseFloat(data[0].lat),
          lng: parseFloat(data[0].lon)
        };
      }
    } catch (e) {
      console.error("Geocoding error:", e);
    }
    return null;
  }

  async function generateItinerary() {
    if (!start_place || !end_place) {
      alert("Please enter both start and end locations.");
      return;
    }

    loading = true;
    errorMessage = "";
    itineraryOptions = [];
    selectedOption = null;
    markers = [];

    try {

      const [startCoords, endCoords] = await Promise.all([
        geocodePlace(start_place),
        geocodePlace(end_place)
      ]);

      const res = await fetch(`http://localhost:8000/api/itinerary/ai`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          start_place,
          end_place,
          transport,
          preference,
          date: selectedDate,
          time: selectedTime,
          budget: budget ? parseFloat(budget) : null,
          interests: interests.length > 0 ? interests : null,
          num_options: 3
        })
      });

      const data = await res.json();

      if (data.options && Array.isArray(data.options)) {
        itineraryOptions = data.options.map((opt: any, idx: number) => ({
          id: idx,
          title: opt.title || `Option ${idx + 1}`,
          itinerary: opt.itinerary,
          estimated_cost: opt.estimated_cost || "N/A",
          duration: opt.duration || "N/A"
        }));

        if (itineraryOptions.length > 0) {
          selectedOption = itineraryOptions[0];
        }
      } else if (data.itinerary) {

        itineraryOptions = [{
          id: 0,
          title: "Recommended Route",
          itinerary: data.itinerary,
          estimated_cost: "N/A",
          duration: "N/A"
        }];
        selectedOption = itineraryOptions[0];
      } else {
        errorMessage = "Error: " + JSON.stringify(data.error || "No itinerary generated");
      }


      markers = [
        {
          lat: startCoords?.lat || 22.3027,
          lng: startCoords?.lng || 114.1772,
          title: start_place,
          color: "#4CAF50"
        },
        {
          lat: endCoords?.lat || 22.3127,
          lng: endCoords?.lng || 114.1872,
          title: end_place,
          color: "#FF5722"
        }
      ];

      poiMarkers = [];
      if (data.pois && Array.isArray(data.pois)) {
        poiMarkers = data.pois.map((p: any) => ({ lat: Number(p.lat), lng: Number(p.lng), name: p.name, description: p.description || '', type: p.type || '' }));
      }

      if (startCoords && endCoords) {
        try {
          const rres = await fetch("http://localhost:8000/api/route/enhanced", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              start_lat: startCoords.lat,
              start_lng: startCoords.lng,
              end_lat: endCoords.lat,
              end_lng: endCoords.lng
            })
          });
          const rdata = await rres.json();
          routeOptions = rdata.route_options || [];

          routePolyline = (rdata.polyline || []).map((p: any) => ({ lat: p[0], lng: p[1] }));
          selectedRoute = routeOptions.length > 0 ? routeOptions[0] : null;
        } catch (e) {
          console.error("Route fetch error:", e);
        }
      }
    } catch (e) {
      errorMessage = "Something went wrong: " + (e as Error).message;
    }

    loading = false;
  }

  function copyText() {
    if (selectedOption) {
      navigator.clipboard.writeText(selectedOption.itinerary);
      alert("Itinerary copied!");
    }
  }

  function selectOption(option: ItineraryOption) {
    selectedOption = option;
  }

  function showRouteOnMap(route: any) {

    if (route && route.polyline) {
      routePolyline = route.polyline.map((p: any) => ({ lat: p[0], lng: p[1] }));
    } else {

    }
    selectedRoute = route;
  }
</script>

<div class="container">
  <div class="card">
    <h1>✨ AI-Powered Hong Kong Itinerary Planner</h1>
    <p class="subtitle">Create your perfect Hong Kong experience with personalized recommendations</p>


    <div class="section">
      <h3>📍 Locations</h3>
      <div class="inputs">
        <input placeholder="Start location (e.g., Tsim Sha Tsui)..." bind:value={start_place} />
        <input placeholder="End location (e.g., Victoria Peak)..." bind:value={end_place} />
      </div>
    </div>


    <div class="section">
      <h3>📅 When are you planning?</h3>
      <div class="datetime-inputs">
        <div class="input-group">
          <label for="date">Date</label>
          <input id="date" type="date" bind:value={selectedDate} />
        </div>
        <div class="input-group">
          <label for="startTime">Start Time</label>
          <input id="startTime" type="time" bind:value={selectedTime} />
        </div>
        <div class="input-group">
          <label for="budget">Budget (HKD)</label>
          <input id="budget" type="number" placeholder="e.g., 500" bind:value={budget} />
        </div>
      </div>
    </div>


    <div class="section">
      <h3>🚇 Preferred Transport</h3>
      <div class="transport-grid">
        {#each transportOptions as t}
          <button
            class="transport-btn"
            class:active={transport === t}
            on:click={() => transport = t}
          >
            {#if t === "MTR"}🚇
            {:else if t === "Bus"}🚌
            {:else if t === "Tram"}🚊
            {:else if t === "Ferry"}⛴️
            {:else if t === "Walk"}🚶
            {:else if t === "Taxi"}🚕
            {:else}🔀
            {/if}
            {t}
          </button>
        {/each}
      </div>
    </div>


    <div class="section">
      <h3>🎯 Route Preference</h3>
      <div class="preference-grid">
        {#each preferences as pref}
          <button
            class="preference-btn"
            class:active={preference === pref.id}
            on:click={() => preference = pref.id}
          >
            <span class="pref-label">{pref.label}</span>
            <span class="pref-desc">{pref.description}</span>
          </button>
        {/each}
      </div>
    </div>


    <div class="section">
      <h3>❤️ What interests you?</h3>
      <div class="interests-grid">
        {#each interestOptions as interest}
          <button
            class="interest-btn"
            class:active={interests.includes(interest.id)}
            on:click={() => toggleInterest(interest.id)}
          >
            <span class="interest-icon">{interest.icon}</span>
            <span>{interest.label.replace(interest.icon, '').trim()}</span>
          </button>
        {/each}
      </div>
    </div>


    <button class="generate-btn" on:click={generateItinerary} disabled={loading}>
      {#if loading}
        ⏳ Generating your perfect itinerary…
      {:else}
        ✨ Generate Itinerary
      {/if}
    </button>

    {#if errorMessage}
      <div class="error-box">
        <strong>⚠️ Error:</strong> {errorMessage}
      </div>
    {/if}


    {#if itineraryOptions.length > 0}
      <div class="options-section">
        <h3>🗺️ Choose Your Itinerary</h3>
        <div class="options-grid">
          {#each itineraryOptions as option}
            <button
              class="option-card"
              class:selected={selectedOption?.id === option.id}
              on:click={() => selectOption(option)}
            >
              <h4>{option.title}</h4>
              <div class="option-meta">
                <span>💰 {option.estimated_cost}</span>
                <span>⏱️ {option.duration}</span>
              </div>
            </button>
          {/each}
        </div>
      </div>
    {/if}


    {#if selectedOption}
      <div class="result-section">
        <div class="result-header">
          <h3>📋 {selectedOption.title}</h3>
          <button class="copy-btn" on:click={copyText}>📋 Copy to Clipboard</button>
        </div>
        <div class="result-content">{@html marked.parse(selectedOption.itinerary)}</div>
      </div>
    {/if}


    {#if routeOptions.length > 0}
      <div class="options-section">
        <h3>🛣️ Route Options</h3>
        <div class="options-grid">
          {#each routeOptions as ro, i}
            <button class="option-card" on:click={() => showRouteOnMap(ro)}>
              <h4>{ro.option_name || `Option ${i+1}`}</h4>
              <div class="option-meta">
                <span>⏱️ {ro.total_duration_min} min</span>
                <span>Steps: {ro.steps ? ro.steps.length : 0}</span>
              </div>
            </button>
          {/each}
        </div>

        {#if selectedRoute}
          <div class="result-section">
            <h4>{selectedRoute.option_name}</h4>
            <div>
              {#each selectedRoute.steps as step}
                <div style="margin-bottom:8px">
                  <strong>{step.type}</strong>: {step.instruction}
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    {/if}


    {#if markers.length > 0 || poiMarkers.length > 0}
      <div class="map-section">
        <h3>🗺️ Route Map</h3>
        <div class="map-controls">
          <label><input type="checkbox" bind:checked={showPois} /> Show POIs</label>
        </div>
        <LeafletMap {markers} {poiMarkers} {showPois} polyline={routePolyline} center={{ lat: 22.3027, lng: 114.1772 }} />
      </div>
    {/if}
  </div>
</div>

<style>
  .container {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40px 20px;
  }

  .card {
    background: white;
    padding: 40px;
    max-width: 1200px;
    margin: auto;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  }

  h1 {
    font-size: 2.5em;
    margin: 0 0 10px 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .subtitle {
    color: #64748b;
    font-size: 1.1em;
    margin-bottom: 30px;
  }

  .section {
    margin: 40px 0;
    padding: 15px;
    background: #f8fafc;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
  }

  .section h3 {
    margin: 0 0 25px 0;
    color: #1e293b;
    font-size: 1.3em;
    font-weight: 600;
  }

  .inputs {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px;
  }

  input {
    padding: 4px 5px;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1em;
    transition: all 0.2s;
  }

  input:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
  }

  .datetime-inputs {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 30px;
  }

  .input-group {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .input-group label {
    font-weight: 600;
    color: #475569;
    font-size: 0.95em;
  }

  .transport-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
    gap: 20px;
  }

  .transport-btn {
    padding: 5px;
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.95em;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    color: #0f172a;
  }

  .transport-btn:hover {
    border-color: #667eea;
    transform: translateY(-3px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  }

  .transport-btn.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-color: transparent;
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  }

  .preference-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 22px;
  }

  .preference-btn {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    padding: 6px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
    display: flex;
    flex-direction: column;
    gap: 8px;
    color: #0f172a;
  }

  .preference-btn:hover {
    border-color: #667eea;
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.15);
  }

  .preference-btn.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-color: transparent;
    color: white;
    box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  }

  .pref-label {
    font-size: 1.1em;
    font-weight: bold;
  }

  .pref-desc {
    font-size: 0.9em;
    opacity: 0.8;
  }

  .interests-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 20px;
  }

  .interest-btn {
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 10px;
    padding: 5px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    font-size: 0.95em;
    color: #0f172a;
    min-height: 60px;
  }

  .interest-btn:hover {
    border-color: #667eea;
    transform: scale(1.08);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
  }

  .interest-btn.active {
    background: #eff6ff;
    border-color: #3b82f6;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    color: #0f172a;
  }

  .interest-icon {
    font-size: 1.8em;
  }

  .generate-btn {
    width: 100%;
    padding: 18px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 1.2em;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s;
    margin-top: 20px;
  }

  .generate-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
  }

  .generate-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .options-section {
    margin: 30px 0;
  }

  .options-section h3 {
    margin-bottom: 15px;
    color: #1e293b;
  }

  .options-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
  }

  .option-card {
    background: white;
    border: 3px solid #e2e8f0;
    border-radius: 12px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
  }

  .option-card:hover {
    border-color: #667eea;
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.2);
  }

  .option-card.selected {
    border-color: #667eea;
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
  }

  .option-card h4 {
    margin: 0 0 10px 0;
    color: #0f172a;
  }

  .option-meta {
    display: flex;
    gap: 15px;
    font-size: 0.9em;
    color: #64748b;
  }

  .result-section {
    margin: 30px 0;
    background: #f8fafc;
    border-radius: 12px;
    padding: 25px;
  }

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }

  .result-header h3 {
    margin: 0;
    color: #1e293b;
  }

  .copy-btn {
    padding: 10px 20px;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .copy-btn:hover {
    background: #5568d3;
    transform: translateY(-2px);
  }

  .result-content {
    background: white;
    padding: 20px;
    border-radius: 8px;
    line-height: 1.8;
  }

  .result-content :global(h1),
  .result-content :global(h2),
  .result-content :global(h3) {
    color: #1e293b;
    margin-top: 20px;
  }

  .result-content :global(ul),
  .result-content :global(ol) {
    padding-left: 25px;
  }

  .result-content :global(li) {
    margin: 8px 0;
  }

  .map-section {
    margin-top: 30px;
  }

  .map-section h3 {
    margin-bottom: 15px;
    color: #1e293b;
  }

  .map-controls {
    margin-bottom: 10px;
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .error-box {
    background: #fee2e2;
    border: 2px solid #ef4444;
    color: #991b1b;
    padding: 15px;
    border-radius: 8px;
    margin: 20px 0;
  }

  @media (max-width: 768px) {
    .card {
      padding: 20px;
    }

    h1 {
      font-size: 1.8em;
    }

    .inputs {
      grid-template-columns: 1fr;
    }

    .datetime-inputs {
      grid-template-columns: 1fr;
    }

    .result-header {
      flex-direction: column;
      gap: 10px;
      align-items: flex-start;
    }

    .copy-btn {
      width: 100%;
    }
  }
</style>
