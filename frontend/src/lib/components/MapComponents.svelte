<script lang="ts">
  import { onMount, createEventDispatcher } from 'svelte';

  export let lat: number = 22.3964;
  export let lng: number = 114.1095;
  export let zoom: number = 11;
  export let markers: { lat: number; lng: number; title?: string }[] = [];
  export let polyline: string | null = null;

  let mapDiv: HTMLDivElement;
  let map: any;
  
  // Get google from the global window object, which is set by the script tag in app.html
  let google: any = (typeof window !== 'undefined' ? (window as any).google : null); 

  // Variables to track map overlays for efficient clearing/updating
  let currentMarkers: any[] = [];
  let currentPolyline: any = null;

  const dispatch = createEventDispatcher();

  /**
   * Initializes the map when the component mounts AND the Google Maps library is loaded.
   */
  onMount(() => {
    // Function to initialize the map once the google object is ready
    const initMap = () => {
        if (!mapDiv || !google) {
            // Check again in case the component initialized before the global variable was set
            google = (window as any).google;
            if (!mapDiv || !google) {
                console.error("Map container or Google Maps API object not found.");
                return;
            }
        }
        
        // Initialize map
        map = new google.maps.Map(mapDiv, {
            center: { lat, lng },
            zoom,
        });
        
        // Draw initial markers/polyline
        updateMap(); 
        
        // Add click event listener to the map
        map.addListener('click', (event: google.maps.MapMouseEvent) => {
          dispatch('mapclick', event.latLng);
        });
    };

    // If google is already loaded (common if app.html script executes quickly)
    if (google) {
      initMap();
    } else {
      // If not loaded yet, wait for the 'googleLoaded' event dispatched from app.html
      window.addEventListener('googleLoaded', initMap);
    }
    
    // Cleanup event listener when component is destroyed
    return () => {
        window.removeEventListener('googleLoaded', initMap);
    };
  });

  /**
   * Reactive Svelte block: Runs every time the lat, lng, markers, or polyline props change.
   */
  $: if (map && google && lat !== undefined && lng !== undefined) {
    updateMap();
  }

  /**
   * Clears existing markers/polylines and redraws them based on current props.
   */
  function updateMap() {
    if (!map || !google) return;

    // 1. Update Map Center and Zoom
    map.setCenter({ lat, lng });
    map.setZoom(zoom);

    // 2. Clear old markers by setting their map property to null
    currentMarkers.forEach(marker => marker.setMap(null));
    currentMarkers = [];

    // 3. Draw new markers and track them
    if (markers && markers.length > 0) {
      markers.forEach(m => {
        // This check prevents "Cannot read properties of undefined (reading 'lat')""
        if (m && m.lat !== undefined && m.lng !== undefined) {
          const marker = new google.maps.Marker({
            position: { lat: m.lat, lng: m.lng },
            map,
            title: m.title
          });
          currentMarkers.push(marker);
        }
      });
    }

    // 4. Clear old polyline
    if (currentPolyline) {
      currentPolyline.setMap(null);
    }

    // 5. Draw new Polyline
    if (polyline && google.maps.geometry) {
      const path = google.maps.geometry.encoding.decodePath(polyline);
      currentPolyline = new google.maps.Polyline({
        path,
        geodesic: true,
        strokeColor: '#007bff',
        strokeOpacity: 1.0,
        strokeWeight: 4, 
        map
      });
    } else {
      currentPolyline = null;
    }
  }
</script>

<div bind:this={mapDiv}></div>

<style>
  div {
      width: 100%;
      height: 100%;
  }
</style>