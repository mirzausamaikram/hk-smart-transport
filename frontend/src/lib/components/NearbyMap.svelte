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

        // Primary Leaflet click handler
        map.on("click", (e: any) => {
            dispatch("mapclick", {
                lat: e.latlng.lat,
                lng: e.latlng.lng
            });
            setUserMarker(e.latlng.lat, e.latlng.lng);
        });

        // Fallback: listen on container to convert clicks to lat/lng
        // Ensures selection works even if some layer swallows Leaflet's click
        if (mapDiv) {
            const onContainerClick = (ev: MouseEvent) => {
                try {
                    const pt = map.mouseEventToContainerPoint(ev);
                    const latlng = map.containerPointToLatLng(pt);
                    dispatch("mapclick", { lat: latlng.lat, lng: latlng.lng });
                    setUserMarker(latlng.lat, latlng.lng);
                } catch {}
            };
            mapDiv.addEventListener("click", onContainerClick);
            // remove on destroy
            onDestroy(() => {
                mapDiv?.removeEventListener("click", onContainerClick);
            });
        }

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
        if (!L || !map) return;

        // Create a blue dot-like divIcon
        const dotHtml = `<span style="display:block;width:16px;height:16px;border-radius:50%;background:#2563eb;border:2px solid #fff;box-shadow:0 0 0 1px rgba(0,0,0,0.12);"></span>`;
        const dotIcon = L.divIcon({ html: dotHtml, className: 'nearby-user-icon', iconSize: [16,16], iconAnchor: [8,8] });

        if (!userMarker) {
            userMarker = L.marker([lat, lng], { icon: dotIcon, draggable: true })
                .addTo(map)
                .bindTooltip('Selected location', { permanent: false });

            // Dragging the marker will update selection
            userMarker.on('dragend', () => {
                const pos = userMarker.getLatLng();
                // Move the radius circle
                if (radiusCircle) radiusCircle.setLatLng(pos);
                // Notify parent to fetch
                dispatch('mapclick', { lat: pos.lat, lng: pos.lng });
            });
        } else {
            userMarker.setLatLng([lat, lng]);
        }

        if (!radiusCircle) {
            radiusCircle = L.circle([lat, lng], {
                radius: searchRadius,
                color: '#3b82f6',
                fillColor: '#3b82f6',
                fillOpacity: 0.08,
                weight: 2,
                dashArray: '5, 5'
            }).addTo(map);
        } else {
            radiusCircle.setLatLng([lat, lng]);
            radiusCircle.setRadius(searchRadius);
        }
    }

    // update when center changes
    $: if (map && center) {
        setUserMarker(center.lat, center.lng);
        map.panTo([center.lat, center.lng]);
    }

    // keep circle radius in sync when slider changes
    $: if (radiusCircle && searchRadius) {
        try { radiusCircle.setRadius(searchRadius); } catch {}
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
        cursor: crosshair;
    }
</style>
