<script lang="ts">
    import { onMount, onDestroy, createEventDispatcher } from "svelte";

    export let center = { lat: 22.3027, lng: 114.1772 };
    export let stations: Array<any> = [];
    export let searchRadius: number = 800; // in meters

    let mapDiv: HTMLDivElement;
    let map: any;
    let stationLayer: any; // will be a MarkerClusterGroup
    let userMarker: any;
    let radiusCircle: any;

    let L: any;
    const dispatch = createEventDispatcher();

    let icons: any = {};

    function colorForType(type: string) {
        switch ((type || '').toLowerCase()) {
            case 'mtr': return '#e11d48';
            case 'bus stop': return '#2563eb';
            case 'minibus': return '#f59e0b';
            case 'ferry pier': return '#06b6d4';
            case 'taxi stand': return '#10b981';
            default: return '#6b7280';
        }
    }

    onMount(async () => {
        L = await import("leaflet");

        // load markercluster (modifies L with markerClusterGroup method)
        // @ts-ignore — markercluster adds method to L at runtime
        await import("leaflet.markercluster");

        map = L.map(mapDiv).setView([center.lat, center.lng], 15);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19
        }).addTo(map);

        // use a MarkerClusterGroup so many stops cluster nicely
        stationLayer = L.markerClusterGroup();
        stationLayer.addTo(map);

        map.on("click", (e: any) => {
            dispatch("mapclick", {
                lat: e.latlng.lat,
                lng: e.latlng.lng
            });
            setUserMarker(e.latlng.lat, e.latlng.lng);
        });

        setUserMarker(center.lat, center.lng);
    });

    onDestroy(() => {
        try {
            if (map) map.remove();
        } catch (err) {
            // ignore
        }
    });

    // user marker updater & radius circle
    function setUserMarker(lat: number, lng: number) {
        if (!L) return;

        if (userMarker) userMarker.remove();
        if (radiusCircle) radiusCircle.remove();

        // Draw a distinct blue circle marker for the user's location
        userMarker = L.circleMarker([lat, lng], {
            radius: 10,
            color: '#2563eb',
            fillColor: '#2563eb',
            fillOpacity: 1,
            weight: 2
        }).addTo(map).bindTooltip('You are here', { permanent: false });

        // Draw radius circle around user (800m or searchRadius)
        radiusCircle = L.circle([lat, lng], {
            radius: searchRadius,
            color: '#3b82f6',
            fillColor: '#3b82f6',
            fillOpacity: 0.08,
            weight: 2,
            dashArray: '5, 5'
        }).addTo(map);
    }

    // update when center changes
    $: if (map && center) {
        setUserMarker(center.lat, center.lng);
        map.panTo([center.lat, center.lng]);
    }

    // update stations (NO RETURNS inside reactive block)
    $: if (map && stationLayer && Array.isArray(stations)) {
        stationLayer.clearLayers();

        stations
            .filter(s => s.lat !== undefined && s.lng !== undefined)
            .forEach((s) => {
                const color = colorForType(s.type);

                // Use a small colored div icon so clustering works (markercluster clusters L.marker)
                const html = `
                    <span style="display:block;width:14px;height:14px;border-radius:50%;background:${color};border:2px solid #fff;box-shadow:0 0 0 1px rgba(0,0,0,0.12);"></span>
                `;

                const icon = L.divIcon({
                    html,
                    className: 'nearby-div-icon',
                    iconSize: [18, 18],
                    iconAnchor: [9, 9]
                });

                const m = L.marker([s.lat, s.lng], { icon })
                    .bindPopup(`<b>${s.type}</b><br>${s.name}`);

                stationLayer.addLayer(m);
            });
    }
</script>

<div bind:this={mapDiv} style="height: 500px"></div>

<style>
    :global(.leaflet-container) {
        height: 100%;
        width: 100%;
    }
</style>
