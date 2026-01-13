<script lang="ts">
  import { onMount, createEventDispatcher } from "svelte";
  import type { LeafletMouseEvent } from 'leaflet';

  export let center: { lat: number; lng: number };
  export let markers: { lat: number; lng: number; title: string; color: string }[] = [];
  export let polyline: { lat: number; lng: number; style?: 'solid' | 'dotted'; type?: string }[] = [];

  export let poiMarkers: { lat: number; lng: number; name: string; description?: string; type?: string }[] = [];
  export let showPois: boolean = true;

  let map: any;
  let mapDiv: HTMLDivElement;
  let layerMarkers: any;
  let layerRoute: any;
  let layerPois: any;

  const dispatch = createEventDispatcher();

  onMount(async () => {
    const L = await import("leaflet");

    map = L.map(mapDiv).setView([center.lat, center.lng], 12);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19
    }).addTo(map);

    layerMarkers = L.layerGroup().addTo(map);
    layerRoute = L.layerGroup().addTo(map);
    layerPois = L.layerGroup().addTo(map);

    map.on("click", (e: LeafletMouseEvent) => {
      dispatch("mapclick", {
        lat: e.latlng.lat,
        lng: e.latlng.lng
      });
    });
  });


  $: if (map && layerMarkers) {
    layerMarkers.clearLayers();
    import("leaflet").then((L) => {
      markers.forEach(m => {
        const iconHtml = `
          <div style="display:flex;flex-direction:column;align-items:center;">
            <div style="width:18px;height:18px;border-radius:50%;background:${m.color};box-shadow:0 1px 3px rgba(0,0,0,0.4);transform:translateY(-6px);"></div>
            <div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:10px solid ${m.color};margin-top:-4px;transform:translateY(-6px);"></div>
          </div>`;

        const icon = L.divIcon({ html: iconHtml, className: '', iconSize: [18, 28], iconAnchor: [9, 28] });

        L.marker([m.lat, m.lng], { icon }).addTo(layerMarkers).bindTooltip(m.title, { permanent: true, direction: "top" });
      });
    });
  }


  $: if (map && layerPois) {
    layerPois.clearLayers();
    if (showPois && poiMarkers && poiMarkers.length > 0) {
      import("leaflet").then((L) => {
        poiMarkers.forEach(p => {

          const color = p.type === 'museum' ? '#6b21a8' : p.type === 'restaurant' ? '#ef4444' : '#f59e0b';
          const iconHtml = `<div style="background:${color};width:18px;height:18px;border-radius:50%;border:2px solid white;box-shadow:0 0 6px rgba(0,0,0,0.3)"></div>`;
          const icon = L.divIcon({ html: iconHtml, className: '' });
          const marker = L.marker([p.lat, p.lng], { icon }).addTo(layerPois);
          const popupHtml = `<strong>${p.name}</strong><br/>${p.description || ''}`;
          marker.bindPopup(popupHtml);
        });
      });
    }
  }


  $: if (layerRoute) {
    layerRoute.clearLayers();

    if (polyline.length > 0) {
      import("leaflet").then((L) => {

        let currentSegment: { lat: number; lng: number; style?: string; type?: string }[] = [];
        let currentStyle: string = 'solid';
        let currentType: string = 'walk';

        polyline.forEach((p, idx) => {
          const style: string = p.style || 'solid';
          const type: string = p.type || 'walk';

          if ((style !== currentStyle || type !== currentType) && currentSegment.length > 0) {

            const pts = currentSegment.map((pt): [number, number] => [pt.lat, pt.lng]);


            let color = '#3b82f6';
            let weight = 5;
            let dashArray = 'none';

            if (currentType === 'walk') {
              color = '#3b82f6';
              weight = 4;
              dashArray = currentStyle === 'dotted' ? '8, 8' : 'none';
            } else if (currentType === 'bus') {
              color = '#f59e0b';
              weight = 6;
            } else if (currentType === 'mtr') {
              color = '#8b5cf6';
              weight = 8;
            } else if (currentType === 'ferry') {
              color = '#10b981';
              weight = 6;
            }

            L.polyline(pts, { color, weight, dashArray }).addTo(layerRoute);
            currentSegment = [];
            currentStyle = style;
            currentType = type;
          }
          currentSegment.push(p);
        });


        if (currentSegment.length > 1) {
          const pts = currentSegment.map((pt): [number, number] => [pt.lat, pt.lng]);

          let color = '#3b82f6';
          let weight = 5;
          let dashArray = 'none';

          if (currentType === 'walk') {
            color = '#3b82f6';
            weight = 4;
            dashArray = currentStyle === 'dotted' ? '8, 8' : 'none';
          } else if (currentType === 'bus') {
            color = '#f59e0b';
            weight = 6;
          } else if (currentType === 'mtr') {
            color = '#8b5cf6';
            weight = 8;
          } else if (currentType === 'ferry') {
            color = '#10b981';
            weight = 6;
          }

          L.polyline(pts, { color, weight, dashArray }).addTo(layerRoute);
        }


        try {
          const allPts: [number, number][] = [];
          polyline.forEach(p => allPts.push([p.lat, p.lng]));
          markers.forEach(m => allPts.push([m.lat, m.lng]));
          if (allPts.length > 0) {
            const bounds = L.latLngBounds(allPts);
            map.fitBounds(bounds, { padding: [50, 50] });
          }
        } catch (e) {

        }
      });
    }
  }


  $: if (map && layerMarkers && (!polyline || polyline.length === 0) && markers && markers.length > 0) {
    import("leaflet").then((L) => {
      try {
        const pts: [number, number][] = markers.map(m => [m.lat, m.lng]);
        const bounds = L.latLngBounds(pts);
        map.fitBounds(bounds, { padding: [60, 60] });
      } catch (e) {}
    });
  }
</script>

<div bind:this={mapDiv} style="height: 600px;"></div>

<style>
  :global(.leaflet-container) {
    height: 100%;
    width: 100%;
  }
</style>
