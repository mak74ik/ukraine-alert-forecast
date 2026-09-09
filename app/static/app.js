/**
 * UA Air Raid Alert Forecast & Live Neptun Airborne Radar Engine.
 * Clean, lightweight, self-contained standalone build.
 * Features 3D Waving Flag Intro Splash, Circular Iris Reveal,
 * Strict Live Ground-Truth Siren Mapping (Red = Siren, Green = Calm),
 * and Zero-Lag Native Canvas Timeline Engine.
 */

// Global State
let selectedRegionId = "UA-32"; // Default: Kyiv Oblast
let map = null;
let geojsonLayer = null;
let hotspotsLayer = null;
let radarTracksLayer = null;
let socket = null;
let audioEnabled = true;
let nationalOverview = null;
let nationalMatrix = null;
let activeForecastStepIndex = null; // null = LIVE mode, number = 24h forecast index
let isTimelapsePlaying = false;
let timelapseTimer = null;
let regionMetadata = {};
let fullTimelineData = [];
let currentTimelineFilter = "all";
let radarEnabled = true;
let hoverPointIndex = null;
let currentUserProfile = { username: null, region_id: 'UA-32', is_subscribed: false, precision_mode: 'standard' };

// Web Audio Synthesizer
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playAlertSiren() {
    if (!audioEnabled || audioCtx.state === 'suspended') return;
    try {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = "sawtooth";
        
        const now = audioCtx.currentTime;
        osc.frequency.setValueAtTime(440, now);
        osc.frequency.linearRampToValueAtTime(880, now + 0.5);
        osc.frequency.linearRampToValueAtTime(440, now + 1.0);

        gain.gain.setValueAtTime(0.15, now);
        gain.gain.linearRampToValueAtTime(0.01, now + 1.2);

        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(now + 1.2);
    } catch (e) {
        console.warn("Audio error:", e);
    }
}

// 1. Intro Splash Screen & Circular Reveal Controller
function initIntroSplash() {
    const splash = document.getElementById('introSplash');
    const pBar = document.getElementById('splashProgressBar');
    const statusText = document.getElementById('splashStatusText');
    const enterBtn = document.getElementById('enterAppBtn');

    if (!splash) return;

    let progress = 20;
    const interval = setInterval(() => {
        progress += Math.floor(Math.random() * 25) + 15;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
            if (pBar) pBar.style.width = '100%';
            if (statusText) statusText.innerText = "Готово! Запуск захищеного монітора...";

            setTimeout(() => {
                dismissSplash();
            }, 500);
        } else {
            if (pBar) pBar.style.width = `${progress}%`;
        }
    }, 150);

    const dismissSplash = () => {
        splash.classList.add('splash-hidden');
        if (map) {
            setTimeout(() => map.invalidateSize(), 300);
        }
        drawCanvasTimeline();
    };

    if (enterBtn) {
        enterBtn.addEventListener('click', dismissSplash);
    }
}

// 2. Leaflet Map with Strict Live Ground-Truth & Kyiv City layering
function initMap() {
    map = L.map('ukraineMap', {
        center: [48.5, 31.5],
        zoom: 6,
        zoomControl: true,
        attributionControl: false
    });

    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        subdomains: 'abcd',
        maxZoom: 10,
        minZoom: 5
    }).addTo(map);

    hotspotsLayer = L.layerGroup().addTo(map);
    radarTracksLayer = L.layerGroup().addTo(map);

    renderGeoJsonLayer();
}

function getRegionStyle(regionId) {
    const isSelected = regionId === selectedRegionId;

    // 1. FORECAST MODE (24h Scrubber Active)
    if (activeForecastStepIndex !== null && nationalMatrix && nationalMatrix.steps && nationalMatrix.steps[activeForecastStepIndex]) {
        const step = nationalMatrix.steps[activeForecastStepIndex];
        const prob = (step.regions_risk && step.regions_risk[regionId] !== undefined) ? step.regions_risk[regionId] : 0.05;
        const level = (step.regions_alert_level && step.regions_alert_level[regionId]) ? step.regions_alert_level[regionId] : 'CLEAR';

        if (level === 'YELLOW') {
            return {
                fillColor: '#eab308',
                weight: isSelected ? 3.5 : (regionId === 'UA-30' ? 2.5 : 1.5),
                opacity: 1,
                color: isSelected ? '#ffffff' : '#facc15',
                fillOpacity: Math.min(0.92, Math.max(0.45, 0.35 + prob * 0.55))
            };
        } else if (level === 'RED') {
            return {
                fillColor: '#ef4444',
                weight: isSelected ? 3.5 : (regionId === 'UA-30' ? 3 : 1.5),
                opacity: 1,
                color: isSelected ? '#ffffff' : '#f87171',
                fillOpacity: Math.min(0.95, Math.max(0.60, 0.45 + prob * 0.55))
            };
        } else if (level === 'ORANGE') {
            return {
                fillColor: '#f97316',
                weight: isSelected ? 3.5 : (regionId === 'UA-30' ? 2.5 : 1.5),
                opacity: 1,
                color: isSelected ? '#ffffff' : '#fb923c',
                fillOpacity: Math.min(0.90, Math.max(0.50, 0.40 + prob * 0.55))
            };
        } else {
            return {
                fillColor: '#15803d',
                weight: isSelected ? 3.5 : (regionId === 'UA-30' ? 2 : 1.5),
                opacity: 1,
                color: isSelected ? '#ffffff' : (regionId === 'UA-30' ? '#fbbf24' : '#1e293b'),
                fillOpacity: 0.65
            };
        }
    }

    // 2. LIVE REAL-TIME SIREN MODE (Sept 1 Reform)
    if (!nationalOverview) {
        return { fillColor: '#15803d', weight: isSelected ? 3.5 : 1.5, color: '#334155', fillOpacity: 0.65 };
    }

    const reg = nationalOverview.regions.find(r => r.id === regionId);
    if (!reg) {
        return { fillColor: '#15803d', weight: isSelected ? 3.5 : 1.5, color: '#334155', fillOpacity: 0.65 };
    }

    if (reg.is_active) {
        if (reg.is_partial) {
            return {
                fillColor: '#ea580c',
                weight: isSelected ? 3.5 : 2,
                opacity: 1,
                color: isSelected ? '#ffffff' : '#f97316',
                dashArray: '4, 4',
                fillOpacity: isSelected ? 0.85 : 0.65
            };
        }

        const alertLvl = reg.alert_level || 'RED';
        if (alertLvl === 'YELLOW') {
            return {
                fillColor: '#eab308', // Solid Yellow for Shaheds / UAVs
                weight: isSelected ? 3.5 : (regionId === 'UA-30' ? 3 : 1.8),
                opacity: 1,
                color: isSelected ? '#ffffff' : '#facc15',
                fillOpacity: isSelected ? 0.95 : 0.85
            };
        } else if (alertLvl === 'ORANGE') {
            return {
                fillColor: '#f97316', // Solid Orange for KABs
                weight: isSelected ? 3.5 : (regionId === 'UA-30' ? 3 : 1.8),
                opacity: 1,
                color: isSelected ? '#ffffff' : '#fb923c',
                fillOpacity: isSelected ? 0.95 : 0.85
            };
        }

        return {
            fillColor: '#ef4444', // Solid Bright Red for Missiles
            weight: isSelected ? 3.5 : (regionId === 'UA-30' ? 3 : 1.8),
            opacity: 1,
            color: isSelected ? '#ffffff' : (regionId === 'UA-30' ? '#ffffff' : '#ef4444'),
            fillOpacity: isSelected ? 0.95 : 0.85
        };
    }

    return {
        fillColor: '#15803d',
        weight: isSelected ? 3.5 : (regionId === 'UA-30' ? 2 : 1.5),
        opacity: 1,
        color: isSelected ? '#ffffff' : (regionId === 'UA-30' ? '#fbbf24' : '#1e293b'),
        fillOpacity: isSelected ? 0.85 : 0.60
    };
}

function renderGeoJsonLayer() {
    if (geojsonLayer) {
        map.removeLayer(geojsonLayer);
    }

    if (typeof UKRAINE_GEOJSON === 'undefined') return;

    geojsonLayer = L.geoJSON(UKRAINE_GEOJSON, {
        style: (feature) => getRegionStyle(feature.properties.id),
        onEachFeature: (feature, layer) => {
            const regId = feature.properties.id;
            const name = feature.properties.name;

            let tooltipContent = `<strong>${name}</strong>`;

            if (activeForecastStepIndex !== null && nationalMatrix && nationalMatrix.steps && nationalMatrix.steps[activeForecastStepIndex]) {
                const step = nationalMatrix.steps[activeForecastStepIndex];
                const prob = Math.round(((step.regions_risk && step.regions_risk[regId]) || 0) * 100);
                const lvl = (step.regions_alert_level && step.regions_alert_level[regId]) || 'CLEAR';
                
                tooltipContent += `<br><span class="text-sky-300 font-mono text-[11px]">Прогноз на ${step.time_display}</span>`;
                if (lvl === 'YELLOW') {
                    tooltipContent += `<br><span class="text-yellow-300 font-bold">🟡 ЖОВТИЙ РІВЕНЬ (БПЛА) • ${prob}%</span><br><span class="text-[10px] text-yellow-200/80">Робота дозволена за наявності укриття</span>`;
                } else if (lvl === 'RED') {
                    tooltipContent += `<br><span class="text-red-400 font-bold">🔴 ЧЕРВОНИЙ РІВЕНЬ (РАКЕТИ) • ${prob}%</span><br><span class="text-[10px] text-red-200/80">Пряма загроза • Негайно в укриття!</span>`;
                } else if (lvl === 'ORANGE') {
                    tooltipContent += `<br><span class="text-orange-400 font-bold">🟠 ПОМАРАНЧЕВИЙ (КАБ) • ${prob}%</span>`;
                } else {
                    tooltipContent += `<br><span class="text-emerald-400 font-semibold">🟢 Відбій загрози (${prob}% фоновий)</span>`;
                }
            } else {
                const regData = nationalOverview ? nationalOverview.regions.find(r => r.id === regId) : null;
                if (regData && regData.is_active) {
                    if (regData.is_partial && regData.sub_regions && regData.sub_regions.length > 0) {
                        const cities = regData.sub_regions.map(c => c.name_ua).join(', ');
                        tooltipContent += `<br><span class="text-amber-400 font-semibold">⚠️ Локальна загроза: ${cities}</span>`;
                    } else {
                        const lvl = regData.alert_level || 'RED';
                        if (lvl === 'YELLOW') {
                            tooltipContent += `<br><span class="text-yellow-400 font-bold">🟡 ЖОВТИЙ РІВЕНЬ (БПЛА)</span><br><span class="text-[10px] text-yellow-200">Робота дозволена за наявності укриття</span>`;
                        } else if (lvl === 'ORANGE') {
                            tooltipContent += `<br><span class="text-orange-400 font-bold">🟠 ПОМАРАНЧЕВИЙ РІВЕНЬ (КАБ)</span>`;
                        } else {
                            tooltipContent += `<br><span class="text-red-400 font-bold">🔴 ЧЕРВОНИЙ РІВЕНЬ (РАКЕТИ)</span><br><span class="text-[10px] text-red-200">Негайно прямуйте в укриття!</span>`;
                        }
                    }
                } else {
                    tooltipContent += `<br><span class="text-emerald-400 font-semibold">🟢 Відбій тривоги (Штатний режим)</span>`;
                }
            }

            layer.bindTooltip(tooltipContent, {
                sticky: true,
                direction: 'auto',
                className: 'bg-slate-900 text-white border border-slate-700 px-2.5 py-1.5 rounded-md text-xs font-sans shadow-lg'
            });

            if (regId === 'UA-30') {
                layer.bringToFront();
            }

            layer.on({
                mouseover: (e) => {
                    const l = e.target;
                    l.setStyle({ weight: 3.5, fillOpacity: 0.95, color: '#f8fafc' });
                    if (regId === 'UA-30') l.bringToFront();
                },
                mouseout: (e) => {
                    if (geojsonLayer) geojsonLayer.resetStyle(e.target);
                    const kyivLayer = geojsonLayer.getLayers().find(lay => lay.feature && lay.feature.properties.id === 'UA-30');
                    if (kyivLayer) kyivLayer.bringToFront();
                },
                click: () => {
                    selectRegion(regId);
                }
            });
        }
    }).addTo(map);

    geojsonLayer.eachLayer((lay) => {
        if (lay.feature && lay.feature.properties.id === 'UA-30') {
            lay.bringToFront();
        }
    });

    renderHotspotMarkers();
    renderRadarTracks();

    if (geojsonLayer.getLayers().length > 0) {
        map.fitBounds(geojsonLayer.getBounds(), { padding: [10, 10] });
    }
}

// 3. Render Sub-Regional Pinpoint Hotspots (Cities/Raions)
function renderHotspotMarkers() {
    if (!hotspotsLayer) return;
    hotspotsLayer.clearLayers();

    if (!nationalOverview || !nationalOverview.hotspots) return;

    nationalOverview.hotspots.forEach(spot => {
        if (spot.lat && spot.lon) {
            const circle = L.circleMarker([spot.lat, spot.lon], {
                radius: 8,
                fillColor: '#ef4444',
                color: '#ffffff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.9
            });

            circle.bindTooltip(`📍 <strong>${spot.name_ua}</strong><br><span class="text-red-300">Локалізована небезпека</span>`, {
                sticky: true,
                className: 'bg-red-950 text-white border border-red-700 px-2 py-1 rounded text-xs'
            });

            circle.addTo(hotspotsLayer);
        }
    });
}

// 4. Render Neptun-Style Live Airborne Radar Targets & Vectors
function renderRadarTracks() {
    if (!radarTracksLayer) return;
    radarTracksLayer.clearLayers();

    if (!radarEnabled || !nationalOverview || !nationalOverview.radar_tracks) return;

    nationalOverview.radar_tracks.forEach(trk => {
        if (trk.lat && trk.lon) {
            if (trk.predicted_lat_15m && trk.predicted_lon_15m) {
                const vectorLine = L.polyline([[trk.lat, trk.lon], [trk.predicted_lat_15m, trk.predicted_lon_15m]], {
                    color: trk.color || '#eab308',
                    weight: 2.5,
                    dashArray: '4, 4',
                    opacity: 0.8
                });
                vectorLine.addTo(radarTracksLayer);
            }

            const iconHtml = `
                <div class="relative flex items-center justify-center" style="transform: rotate(${trk.heading_deg}deg);">
                    <div class="absolute w-8 h-8 rounded-full bg-red-500/30 radar-pulse-circle"></div>
                    <div class="w-6 h-6 rounded-full bg-slate-900 border border-yellow-400 flex items-center justify-center shadow-lg text-yellow-400 text-xs">
                        <i class="fa-solid fa-paper-plane" style="transform: rotate(-45deg);"></i>
                    </div>
                </div>
            `;

            const radarIcon = L.divIcon({
                html: iconHtml,
                className: 'radar-target-marker',
                iconSize: [28, 28],
                iconAnchor: [14, 14]
            });

            const marker = L.marker([trk.lat, trk.lon], { icon: radarIcon });

            const tooltipHtml = `
                <div class="p-1">
                    <div class="font-bold text-yellow-400 text-xs flex items-center gap-1.5">
                        <i class="fa-solid fa-radar"></i> ${trk.id}: ${trk.title}
                    </div>
                    <div class="text-[11px] text-slate-300 mt-1">
                        <div>Швидкість: <strong>${trk.speed_kmh} км/год</strong> • Курс: <strong>${trk.heading_deg}°</strong></div>
                        ${trk.target_city ? `<div>Напрямок: <span class="text-amber-300 font-semibold">${trk.target_city}</span></div>` : ''}
                        <div class="text-[10px] text-slate-400 mt-0.5">${trk.description}</div>
                    </div>
                </div>
            `;

            marker.bindTooltip(tooltipHtml, {
                sticky: true,
                direction: 'top',
                className: 'bg-slate-900 text-white border border-amber-500/50 rounded-lg p-2 shadow-2xl'
            });

            marker.addTo(radarTracksLayer);
        }
    });
}

// 5. GUARANTEED NATIVE CANVAS TIMELINE ENGINE (Zero Lag / Zero CDN Bugs)
function drawCanvasTimeline() {
    const canvas = document.getElementById('timelineChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();

    const w = rect.width > 50 ? rect.width : (canvas.parentElement ? canvas.parentElement.clientWidth - 16 : 580);
    const h = rect.height > 50 ? rect.height : 210;

    canvas.width = w * dpr;
    canvas.height = h * dpr;
    ctx.scale(dpr, dpr);

    ctx.clearRect(0, 0, w, h);

    if (!fullTimelineData || fullTimelineData.length === 0) {
        ctx.fillStyle = '#64748b';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Завантаження прогнозу на 24 години...', w / 2, h / 2);
        return;
    }

    const liveIndex = fullTimelineData.findIndex(p => p.is_live);
    let points = [];

    if (currentTimelineFilter === "past") {
        points = fullTimelineData.filter(p => p.is_past || p.is_live);
    } else if (currentTimelineFilter === "live") {
        const start = Math.max(0, liveIndex - 12);
        const end = Math.min(fullTimelineData.length, liveIndex + 36);
        points = fullTimelineData.slice(start, end);
    } else if (currentTimelineFilter === "6h") {
        const start = Math.max(0, liveIndex);
        const end = Math.min(fullTimelineData.length, liveIndex + (6 * 12));
        points = fullTimelineData.slice(start, end);
    } else if (currentTimelineFilter === "12h") {
        const start = Math.max(0, liveIndex);
        const end = Math.min(fullTimelineData.length, liveIndex + (12 * 12));
        points = fullTimelineData.slice(start, end);
    } else if (currentTimelineFilter === "24h") {
        const start = Math.max(0, liveIndex);
        points = fullTimelineData.slice(start);
    } else {
        points = fullTimelineData;
    }

    if (points.length < 2) points = fullTimelineData;

    const padLeft = 38;
    const padRight = 15;
    const padTop = 15;
    const padBottom = 26;

    const plotW = Math.max(10, w - padLeft - padRight);
    const plotH = Math.max(10, h - padTop - padBottom);

    // 1. Grid Lines & Y-Axis Labels
    ctx.strokeStyle = 'rgba(51, 65, 85, 0.3)';
    ctx.lineWidth = 1;
    ctx.fillStyle = '#94a3b8';
    ctx.font = '10px monospace';
    ctx.textAlign = 'right';

    [0, 25, 50, 75, 100].forEach(val => {
        const y = padTop + plotH - (val / 100.0) * plotH;
        ctx.beginPath();
        ctx.moveTo(padLeft, y);
        ctx.lineTo(w - padRight, y);
        ctx.stroke();
        ctx.fillText(`${val}%`, padLeft - 6, y + 3);
    });

    // 2. Map coordinates
    const coords = points.map((p, i) => {
        const x = padLeft + (i / (points.length - 1)) * plotW;
        const prob = Math.min(1.0, Math.max(0.0, p.probability));
        const y = padTop + plotH - (prob * plotH);
        return { x, y, prob, data: p };
    });

    // 3. Draw Gradient Fill Area
    const grad = ctx.createLinearGradient(0, padTop, 0, padTop + plotH);
    grad.addColorStop(0, 'rgba(239, 68, 68, 0.35)');
    grad.addColorStop(0.5, 'rgba(234, 179, 8, 0.20)');
    grad.addColorStop(1, 'rgba(34, 197, 94, 0.05)');

    ctx.beginPath();
    ctx.moveTo(coords[0].x, padTop + plotH);
    coords.forEach(pt => ctx.lineTo(pt.x, pt.y));
    ctx.lineTo(coords[coords.length - 1].x, padTop + plotH);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();

    // 4. Draw Line with Smooth Quadratic Segments
    ctx.beginPath();
    ctx.moveTo(coords[0].x, coords[0].y);
    for (let i = 0; i < coords.length - 1; i++) {
        const xc = (coords[i].x + coords[i + 1].x) / 2;
        const yc = (coords[i].y + coords[i + 1].y) / 2;
        ctx.quadraticCurveTo(coords[i].x, coords[i].y, xc, yc);
    }
    ctx.lineTo(coords[coords.length - 1].x, coords[coords.length - 1].y);
    ctx.strokeStyle = '#eab308';
    ctx.lineWidth = 2.5;
    ctx.stroke();

    // 5. Draw LIVE marker & X-Axis Timestamp Labels
    ctx.textAlign = 'center';
    const labelStep = Math.max(1, Math.floor(points.length / 8));

    coords.forEach((pt, idx) => {
        if (idx % labelStep === 0 || idx === coords.length - 1) {
            ctx.fillStyle = pt.data.is_live ? '#ef4444' : '#94a3b8';
            ctx.font = pt.data.is_live ? 'bold 10px monospace' : '10px monospace';
            ctx.fillText(pt.data.time_display, pt.x, h - 8);
        }

        if (pt.data.is_live) {
            ctx.strokeStyle = '#ef4444';
            ctx.lineWidth = 1.5;
            ctx.setLineDash([3, 3]);
            ctx.beginPath();
            ctx.moveTo(pt.x, padTop);
            ctx.lineTo(pt.x, padTop + plotH);
            ctx.stroke();
            ctx.setLineDash([]);

            ctx.beginPath();
            ctx.arc(pt.x, pt.y, 7, 0, Math.PI * 2);
            ctx.fillStyle = '#ef4444';
            ctx.fill();
            ctx.lineWidth = 2;
            ctx.strokeStyle = '#ffffff';
            ctx.stroke();
        }
    });

    // 6. Interactive Hover Tooltip
    if (hoverPointIndex !== null && coords[hoverPointIndex]) {
        const hoverPt = coords[hoverPointIndex];

        ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(hoverPt.x, padTop);
        ctx.lineTo(hoverPt.x, padTop + plotH);
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(hoverPt.x, hoverPt.y, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();

        const pct = Math.round(hoverPt.prob * 100);
        const timeStr = `${hoverPt.data.time_display} ${hoverPt.data.is_live ? '(ЗАРАЗ)' : (hoverPt.data.is_past ? '(Минуле)' : '(Прогноз)')}`;
        const threatStr = `Загроза: ${hoverPt.data.threat_title}`;

        ctx.font = 'bold 11px sans-serif';
        const boxW = 160;
        const boxH = 46;
        let boxX = hoverPt.x - boxW / 2;
        if (boxX < padLeft) boxX = padLeft;
        if (boxX + boxW > w - padRight) boxX = w - padRight - boxW;
        let boxY = hoverPt.y - boxH - 10;
        if (boxY < padTop) boxY = hoverPt.y + 12;

        ctx.fillStyle = 'rgba(15, 23, 42, 0.95)';
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(boxX, boxY, boxW, boxH, 6);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.textAlign = 'left';
        ctx.fillText(`Час: ${timeStr}`, boxX + 8, boxY + 16);
        ctx.fillStyle = pct >= 70 ? '#ef4444' : (pct >= 45 ? '#f97316' : '#22c55e');
        ctx.fillText(`Ймовірність: ${pct}% • ${threatStr}`, boxX + 8, boxY + 34);
    }
}

// 6. Update Forecast Details for Selected Region
async function loadRegionForecast(regionId) {
    try {
        const res = await fetch(`/api/forecast/${regionId}`);
        const data = await res.json();
        
        document.getElementById('selectedRegionName').innerText = data.region_name;
        
        const badge = document.getElementById('currentAlertBadge');
        const descEl = document.getElementById('threatDescription');

        if (data.is_active_now) {
            const lvl = data.alert_level || 'RED';
            if (lvl === 'YELLOW') {
                badge.className = "px-3 py-1 text-xs font-bold rounded-full bg-yellow-500/20 text-yellow-300 border border-yellow-500/40 animate-pulse";
                badge.innerText = `🟡 ЖОВТИЙ РІВЕНЬ (БПЛА / ДРОНИ)`;
                descEl.innerHTML = `<span class="text-yellow-300 font-semibold">Загроза ударних дронів (Шахеди).</span> Робота дозволена за наявності укриття.`;
            } else if (lvl === 'ORANGE') {
                badge.className = "px-3 py-1 text-xs font-bold rounded-full bg-orange-500/20 text-orange-300 border border-orange-500/40 animate-pulse";
                badge.innerText = `🟠 ПОМАРАНЧЕВИЙ РІВЕНЬ (КАБ / АВІАЦІЯ)`;
                descEl.innerHTML = `<span class="text-orange-300 font-semibold">Активність тактичної авіації / загроза КАБ.</span> Підвищена небезпека.`;
            } else {
                badge.className = "px-3 py-1 text-xs font-bold rounded-full bg-red-500/20 text-red-300 border border-red-500/40 animate-pulse";
                badge.innerText = `🔴 ЧЕРВОНИЙ РІВЕНЬ (РАКЕТИ / БАЛІСТИКА)`;
                descEl.innerHTML = `<span class="text-red-300 font-semibold">Пряма ракетна або балістична загроза!</span> Негайно прямуйте в укриття!`;
            }

            if (data.is_partial && data.sub_regions && data.sub_regions.length > 0) {
                const citiesList = data.sub_regions.map(c => c.name_ua).join(', ');
                descEl.innerHTML += `<div class="mt-1 text-[11px] text-amber-300 font-medium"><i class="fa-solid fa-location-dot mr-1"></i>Локалізовано: <span class="text-slate-200">${citiesList}</span></div>`;
            }
        } else {
            badge.className = "px-3 py-1 text-xs font-bold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
            badge.innerText = `🟢 ВІДБІЙ ТРИВОГИ`;
            descEl.innerText = "Прямої загрози зараз немає. Фоновий рівень безпечний (Штатний режим).";
        }

        document.getElementById('avg24hRisk').innerText = `${Math.round(data.avg_24h_risk * 100)}%`;

        renderRiskWindows(data.high_risk_windows);

        fullTimelineData = data.timeline;
        drawCanvasTimeline();

        updateThreatBreakdown(data);

    } catch (e) {
        console.error("Failed to load region forecast:", e);
    }
}

function renderRiskWindows(windows) {
    const container = document.getElementById('riskWindowsContainer');
    container.innerHTML = '';

    if (!windows || windows.length === 0) {
        container.innerHTML = `
            <div class="col-span-full py-2 text-center text-xs text-slate-500 bg-slate-900/50 rounded-lg border border-slate-800">
                <i class="fa-solid fa-check-circle text-emerald-500 mr-1"></i> Критичних сплесків загрози на найближчі години не виявлено
            </div>
        `;
        return;
    }

    windows.forEach(w => {
        const isCrit = w.probability >= 80;
        const bg = isCrit ? 'bg-red-950/40 border-red-800/60 text-red-300' : 'bg-amber-950/40 border-amber-800/60 text-amber-300';
        const icon = isCrit ? 'fa-triangle-exclamation text-red-400' : 'fa-clock text-amber-400';

        const card = document.createElement('div');
        card.className = `p-2 rounded-xl border ${bg} flex flex-col justify-between`;
        card.innerHTML = `
            <div class="flex items-center justify-between">
                <span class="text-xs font-mono font-bold tracking-wide">${w.interval_str}</span>
                <span class="text-xs font-black">${w.probability}%</span>
            </div>
            <div class="flex items-center gap-1.5 mt-1 text-[11px] truncate">
                <i class="fa-solid ${icon} text-[10px]"></i>
                <span class="truncate">${w.threat_title}</span>
            </div>
        `;
        container.appendChild(card);
    });
}

function updateThreatBreakdown(data) {
    const base = data.avg_24h_risk * 100;
    const shahed = Math.min(90, Math.max(5, Math.round(base * 1.2)));
    const mig = Math.min(70, Math.max(8, Math.round(base * 0.9)));
    const ballistic = Math.min(65, Math.max(5, Math.round(base * 0.8)));
    const strategic = Math.min(60, Math.max(3, Math.round(base * 0.5)));

    document.getElementById('riskShahed').innerText = `${shahed}%`;
    document.getElementById('barShahed').style.width = `${shahed}%`;

    document.getElementById('riskMig').innerText = `${mig}%`;
    document.getElementById('barMig').style.width = `${mig}%`;

    document.getElementById('riskBallistic').innerText = `${ballistic}%`;
    document.getElementById('barBallistic').style.width = `${ballistic}%`;

    document.getElementById('riskStrategic').innerText = `${strategic}%`;
    document.getElementById('barStrategic').style.width = `${strategic}%`;
}

// 7. Load National Overview & Regions List
async function loadOverview() {
    try {
        const res = await fetch('/api/overview');
        nationalOverview = await res.json();
        
        document.getElementById('activeAlertsCounter').innerText = `${nationalOverview.active_alerts_count} / ${nationalOverview.total_regions}`;
        
        if (nationalOverview.near_term_predictions) {
            renderNearTermPredictions(nationalOverview.near_term_predictions);
        }
        
        renderGeoJsonLayer();
    } catch (e) {
        console.error("Error loading overview:", e);
    }
}

async function loadRegionsList() {
    try {
        const res = await fetch('/api/regions');
        const regions = await res.json();
        
        const select = document.getElementById('regionSelect');
        select.innerHTML = '';

        regions.forEach(r => {
            regionMetadata[r.id] = r;
            const opt = document.createElement('option');
            opt.value = r.id;
            opt.innerText = `${r.name_ua} (${r.short_ua})`;
            if (r.id === selectedRegionId) opt.selected = true;
            select.appendChild(opt);
        });

        select.addEventListener('change', (e) => {
            selectRegion(e.target.value);
        });
    } catch (e) {
        console.error("Error loading regions list:", e);
    }
}

function selectRegion(regionId) {
    selectedRegionId = regionId;
    document.getElementById('regionSelect').value = regionId;
    if (geojsonLayer) {
        geojsonLayer.setStyle((feature) => getRegionStyle(feature.properties.id));
    }
    loadRegionForecast(regionId);
}

// 8. Live Feed & Threat Logs
const TELEGRAM_CHANNEL_URLS = {
    "ПС ЗСУ (Офіційно)": "https://t.me/kpszsu",
    "Оповіщення України": "https://t.me/air_alert_ua",
    "ДСНС України (Офіційно)": "https://t.me/DSNS_GOV_UA",
    "Генштаб ЗСУ": "https://t.me/GeneralStaffZSU",
    "Оперативний ЗСУ": "https://t.me/operativnoZSU",
    "Николаевский Ванёк": "https://t.me/vanek_nikolaev",
    "Радар Інфо": "https://t.me/radarradar_ua",
    "Військовий Монітор": "https://t.me/war_monitor",
    "єРадар ППО": "https://t.me/eRadarrua",
    "Monitor War UA": "https://t.me/monitorwarr",
    "Радар Ракета / БПЛА": "https://t.me/radar_raketa",
    "U-Radar Україна": "https://t.me/u_radar",
    "Київ Оперативний": "https://t.me/kievreal1",
    "Харків Тривога": "https://t.me/kharkiv_alerts",
    "Дніпро Оперативний": "https://t.me/dnipro_alerts",
    "Одеса Офіційно": "https://t.me/odesa_alerts",
    "Запоріжжя Інфо": "https://t.me/zaporizhzhia_alerts",
    "Миколаїв Моніторинг": "https://t.me/mykolaiv_alerts",
    "Суми Оповіщення": "https://t.me/sumy_alerts",
    "Чернігів Інфо": "https://t.me/chernihiv_alerts",
    "Полтава Моніторинг": "https://t.me/poltava_alerts",
    "Вінниця Сповіщення": "https://t.me/vinnytsia_alerts",
    "Хмельницький Радар": "https://t.me/khmelnytskyi_alerts",
    "Львів Оповіщення": "https://t.me/lviv_alerts",
    "Волинь Інфо": "https://t.me/volyn_alerts",
    "Черкаси Оперативний": "https://t.me/cherkasy_alerts"
};

async function loadRecentLogs() {
    try {
        const res = await fetch('/api/logs?limit=40');
        const logs = await res.json();
        const container = document.getElementById('threatFeedContainer');
        container.innerHTML = '';

        if (!logs || logs.length === 0) {
            container.innerHTML = `
                <div class="py-8 text-center text-xs text-slate-400 bg-slate-900/40 rounded-xl border border-slate-800/60 flex flex-col items-center justify-center gap-2">
                    <i class="fa-solid fa-satellite-dish animate-pulse text-sky-400 text-lg"></i>
                    <span>Очікування нових повідомлень з 26 каналів моніторингу... Стрічка оновлюється наживо.</span>
                </div>
            `;
            return;
        }

        logs.forEach(log => appendLogItem(log, false));
    } catch (e) {
        console.error("Error loading logs:", e);
    }
}

function appendLogItem(log, prepend = true) {
    const container = document.getElementById('threatFeedContainer');
    if (!container) return;

    // Clear empty state placeholder if present
    const emptyPlaceholder = container.querySelector('.fa-satellite-dish');
    if (emptyPlaceholder && emptyPlaceholder.parentElement) {
        container.innerHTML = '';
    }

    const item = document.createElement('div');
    
    const isClear = log.is_clear;
    let badgeClass = 'bg-red-500/20 text-red-300 border-red-500/40';
    let badgeText = '🔴 ТРИВОГА';

    if (isClear) {
        badgeClass = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
        badgeText = '🟢 ВІДБІЙ';
    } else if (log.threat_type === 'SHAHED' || log.threat_type === 'RECON_UAV') {
        badgeClass = 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40';
        badgeText = '🟡 ЖОВТИЙ (БПЛА)';
    } else if (log.threat_type === 'TACTICAL_KAB' || log.threat_type === 'TACTICAL_AVIATION') {
        badgeClass = 'bg-orange-500/20 text-orange-300 border-orange-500/40';
        badgeText = '🟠 ПОМАРАНЧЕВИЙ (КАБ)';
    } else if (log.threat_type === 'BALLISTIC' || log.threat_type === 'MIG31K' || log.threat_type === 'STRATEGIC_TU') {
        badgeClass = 'bg-red-500/20 text-red-300 border-red-500/40';
        badgeText = '🔴 ЧЕРВОНИЙ (РАКЕТИ)';
    }

    item.className = "p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs flex flex-col gap-1.5 transition-all hover:border-slate-700 shadow-sm";
    
    const timeStr = new Date(log.created_at || log.timestamp).toLocaleTimeString('uk-UA', { timeZone: 'Europe/Kyiv' });

    let subRegionBadge = '';
    if (log.sub_regions && log.sub_regions.length > 0) {
        const names = log.sub_regions.map(s => s.name_ua).join(', ');
        subRegionBadge = `<span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">📍 ${names}</span>`;
    }

    let regionsBadge = '';
    if (log.region_ids) {
        const rIds = typeof log.region_ids === 'string' ? log.region_ids.split(',') : log.region_ids;
        const validNames = rIds.map(id => regionMetadata[id.trim()] ? regionMetadata[id.trim()].short_ua : null).filter(Boolean);
        if (validNames.length > 0 && validNames.length <= 4) {
            regionsBadge = `<span class="px-2 py-0.5 text-[10px] font-medium rounded-full bg-slate-800 text-slate-300 border border-slate-700">🇺🇦 ${validNames.join(', ')}</span>`;
        }
    }

    const channelIcons = {
        "ПС ЗСУ (Офіційно)": "fa-shield-halved text-blue-400",
        "Оповіщення України": "fa-bullhorn text-red-400",
        "ДСНС України (Офіційно)": "fa-truck-medical text-orange-400",
        "Генштаб ЗСУ": "fa-award text-yellow-400",
        "Николаевский Ванёк": "fa-eye text-emerald-400",
        "Радар Інфо": "fa-radar text-yellow-400",
        "Оперативний ЗСУ": "fa-bolt text-amber-400",
        "Військовий Монітор": "fa-crosshairs text-purple-400",
        "єРадар ППО": "fa-satellite text-blue-400",
        "Monitor War UA": "https://t.me/monitorwarr",
        "Черкаси Оперативний": "fa-tower-broadcast text-emerald-400"
    };

    const iconClass = channelIcons[log.channel] || "fa-satellite-dish text-slate-400";
    const chUrl = TELEGRAM_CHANNEL_URLS[log.channel];

    const sourceEl = chUrl 
        ? `<a href="${chUrl}" target="_blank" rel="noopener" class="font-bold text-sky-400 hover:text-sky-300 hover:underline flex items-center gap-1 transition" title="Відкрити канал в Telegram">${log.channel} <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i></a>`
        : `<span class="font-bold text-slate-200">${log.channel || 'Моніторинг'}</span>`;

    item.innerHTML = `
        <div class="flex items-center justify-between gap-2 flex-wrap">
            <div class="flex items-center gap-1.5 flex-wrap">
                <i class="fa-solid ${iconClass} text-xs"></i>
                ${sourceEl}
                <span class="px-2 py-0.5 text-[10px] font-bold rounded-full ${badgeClass} border">${badgeText}</span>
                ${subRegionBadge}
                ${regionsBadge}
            </div>
            <span class="text-[10px] text-slate-400 font-mono">${timeStr}</span>
        </div>
        <p class="text-slate-200 text-xs leading-relaxed font-sans">${log.raw_text}</p>
        ${log.direction ? `<div class="text-[10px] text-blue-400 font-medium"><i class="fa-solid fa-compass mr-1"></i>Курс: ${log.direction}</div>` : ''}
    `;

    if (prepend) {
        container.insertBefore(item, container.firstChild);
        if (container.children.length > 50) {
            container.removeChild(container.lastChild);
        }
    } else {
        container.appendChild(item);
    }
}

// 9. WebSocket Setup with Auto-Reconnect
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
        console.log("WebSocket connected");
    };

    socket.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'THREAT_UPDATE' || data.type === 'NEW_THREAT_EVENT') {
                if (data.event) {
                    appendLogItem(data.event, true);
                    if (!data.event.is_clear) {
                        playAlertSiren();
                    }
                }
                if (data.overview) {
                    nationalOverview = data.overview;
                    document.getElementById('activeAlertsCounter').innerText = `${nationalOverview.active_alerts_count} / ${nationalOverview.total_regions}`;
                    renderGeoJsonLayer();
                }
                loadRegionForecast(selectedRegionId);
            }
        } catch (e) {
            console.error("WS Parse error:", e);
        }
    };

    socket.onclose = () => {
        setTimeout(initWebSocket, 2500);
    };
}

// 10. Event Listeners & Canvas Mouse Interaction
function initControls() {
    setInterval(() => {
        const now = new Date();
        document.getElementById('liveClock').innerText = now.toLocaleTimeString('uk-UA', { timeZone: 'Europe/Kyiv' });
    }, 1000);

    const soundBtn = document.getElementById('soundToggleBtn');
    soundBtn.addEventListener('click', () => {
        if (audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
        audioEnabled = !audioEnabled;
        soundBtn.innerHTML = audioEnabled 
            ? '<i class="fa-solid fa-volume-high text-emerald-400"></i>' 
            : '<i class="fa-solid fa-volume-xmark text-slate-500"></i>';
    });

    const radarToggle = document.getElementById('toggleRadarLayer');
    if (radarToggle) {
        radarToggle.addEventListener('change', (e) => {
            radarEnabled = e.target.checked;
            renderRadarTracks();
        });
    }

    const syncBtn = document.getElementById('syncNowBtn');
    syncBtn.addEventListener('click', async () => {
        try {
            syncBtn.disabled = true;
            syncBtn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i> Синхронізація...';
            await fetch('/api/sync_now', { method: 'POST' });
            await loadOverview();
            await loadRegionForecast(selectedRegionId);
        } catch (e) {
            console.error("Sync error:", e);
        } finally {
            syncBtn.disabled = false;
            syncBtn.innerHTML = '<i class="fa-solid fa-rotate text-emerald-400"></i> Синхронізувати';
        }
    });

    // Timeline Filter Buttons
    const setFilter = (f) => {
        currentTimelineFilter = f;
        drawCanvasTimeline();
    };

    document.getElementById('btnViewPast').addEventListener('click', () => setFilter('past'));
    document.getElementById('btnViewLive').addEventListener('click', () => setFilter('live'));
    document.getElementById('btnView6h').addEventListener('click', () => setFilter('6h'));
    document.getElementById('btnView12h').addEventListener('click', () => setFilter('12h'));
    document.getElementById('btnView24h').addEventListener('click', () => setFilter('24h'));
    document.getElementById('btnViewFuture').addEventListener('click', () => setFilter('24h'));

    // Canvas Interactive Hover
    const canvas = document.getElementById('timelineChart');
    if (canvas) {
        canvas.addEventListener('mousemove', (e) => {
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const padLeft = 38;
            const padRight = 15;
            const plotW = rect.width - padLeft - padRight;

            if (mouseX >= padLeft && mouseX <= rect.width - padRight && fullTimelineData.length > 1) {
                const ratio = (mouseX - padLeft) / plotW;
                hoverPointIndex = Math.min(fullTimelineData.length - 1, Math.max(0, Math.round(ratio * (fullTimelineData.length - 1))));
            } else {
                hoverPointIndex = null;
            }
            drawCanvasTimeline();
        });

        canvas.addEventListener('mouseleave', () => {
            hoverPointIndex = null;
            drawCanvasTimeline();
        });
    }

    window.addEventListener('resize', () => {
        drawCanvasTimeline();
    });
}

// Global Startup

// ==========================================
// 11. 24-Hour Predictive Forecast Engine & Map Scrubber
// ==========================================

function renderNearTermPredictions(predictions) {
    const container = document.getElementById('nearTermContainer');
    if (!container) return;
    container.innerHTML = '';

    if (!predictions || predictions.length === 0) {
        container.innerHTML = '<div class="col-span-full py-1.5 text-center text-xs text-slate-500 italic bg-slate-900/40 rounded-lg border border-slate-800"><i class="fa-solid fa-shield-check text-emerald-500 mr-1"></i> Прямих векторів підльоту на найближчі 60 хв не зафіксовано</div>';
        return;
    }

    predictions.forEach(p => {
        const isRed = p.alert_level === 'RED';
        const cardBg = isRed ? 'bg-red-950/40 border-red-800/60' : 'bg-yellow-950/40 border-yellow-800/60';
        const badgeBg = isRed ? 'bg-red-500/20 text-red-300 border-red-500/40' : 'bg-yellow-500/20 text-yellow-300 border-yellow-500/40';
        const icon = isRed ? 'fa-triangle-exclamation text-red-400' : 'fa-paper-plane text-yellow-400';

        const card = document.createElement('div');
        card.className = `p-2 rounded-xl border ${cardBg} flex items-center justify-between gap-2 shadow-sm transition hover:scale-[1.01] cursor-pointer`;
        card.onclick = () => selectRegion(p.region_id);
        card.innerHTML = `
            <div class="flex items-center gap-2 min-w-0">
                <i class="fa-solid ${icon} text-sm flex-shrink-0"></i>
                <div class="min-w-0">
                    <div class="font-bold text-xs text-white truncate">${p.name_ua}</div>
                    <div class="text-[10px] text-slate-400 truncate">${p.threat_title}</div>
                </div>
            </div>
            <div class="text-right flex-shrink-0">
                <span class="px-2 py-0.5 text-[10px] font-mono font-bold rounded-full ${badgeBg} border block">
                    ~${p.eta_minutes} хв
                </span>
                <span class="text-[10px] text-slate-400 font-semibold">${Math.round(p.probability * 100)}%</span>
            </div>
        `;
        container.appendChild(card);
    });
}

async function loadMatrix() {
    try {
        const res = await fetch('/api/matrix');
        if (res.ok) {
            nationalMatrix = await res.json();
            const slider = document.getElementById('forecastTimeSlider');
            if (slider && nationalMatrix.steps) {
                slider.max = nationalMatrix.steps.length - 1;
                if (activeForecastStepIndex === null) {
                    const liveIdx = nationalMatrix.steps.findIndex(s => s.is_live);
                    slider.value = liveIdx >= 0 ? liveIdx : 0;
                }
            }
        }
    } catch (e) {
        console.error('Failed to load matrix:', e);
    }
}

function setLiveMode() {
    activeForecastStepIndex = null;
    if (isTimelapsePlaying) {
        stopTimelapse();
    }
    const modeEl = document.getElementById('mapModeText');
    if (modeEl) modeEl.innerText = '● РЕАЛЬНИЙ ЧАС (LIVE)';
    
    const badge = document.getElementById('mapTimeLabel');
    if (badge) {
        badge.className = 'text-xs font-mono font-bold px-2.5 py-1 rounded bg-red-500/20 text-red-400 border border-red-500/30 flex items-center gap-1.5';
    }

    const scrubberStatus = document.getElementById('scrubberTimeStatus');
    if (scrubberStatus) scrubberStatus.innerText = 'Режим: Поточний стан (Live)';

    const scrubberTarget = document.getElementById('scrubberTargetTime');
    if (scrubberTarget) scrubberTarget.innerText = 'Зараз';

    if (nationalMatrix && nationalMatrix.steps) {
        const liveIdx = nationalMatrix.steps.findIndex(s => s.is_live);
        const slider = document.getElementById('forecastTimeSlider');
        if (slider && liveIdx >= 0) slider.value = liveIdx;
    }

    if (geojsonLayer) {
        geojsonLayer.setStyle(feature => getRegionStyle(feature.properties.id));
    }
}

function setForecastStep(index) {
    if (!nationalMatrix || !nationalMatrix.steps || !nationalMatrix.steps[index]) return;
    activeForecastStepIndex = index;
    const step = nationalMatrix.steps[index];

    const slider = document.getElementById('forecastTimeSlider');
    if (slider) slider.value = index;

    const modeEl = document.getElementById('mapModeText');
    if (modeEl) modeEl.innerText = `ПРОГНОЗ НА ${step.time_display}`;

    const badge = document.getElementById('mapTimeLabel');
    if (badge) {
        badge.className = 'text-xs font-mono font-bold px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1.5';
    }

    const scrubberStatus = document.getElementById('scrubberTimeStatus');
    if (scrubberStatus) {
        scrubberStatus.innerText = step.is_live ? 'Режим: Зараз (Live)' : `Прогноз: ${step.time_display}`;
    }

    const scrubberTarget = document.getElementById('scrubberTargetTime');
    if (scrubberTarget) {
        const d = new Date(step.time);
        scrubberTarget.innerText = d.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' });
    }

    if (geojsonLayer) {
        geojsonLayer.setStyle(feature => getRegionStyle(feature.properties.id));
    }
}

function setForecastOffsetMinutes(mins) {
    if (!nationalMatrix || !nationalMatrix.steps) return;
    const target = Date.now() + mins * 60 * 1000;
    let closestIdx = 0;
    let minDiff = Infinity;
    nationalMatrix.steps.forEach((s, idx) => {
        const diff = Math.abs(new Date(s.time).getTime() - target);
        if (diff < minDiff) {
            minDiff = diff;
            closestIdx = idx;
        }
    });
    setForecastStep(closestIdx);
}

function toggleTimelapse() {
    if (isTimelapsePlaying) {
        stopTimelapse();
    } else {
        startTimelapse();
    }
}

function startTimelapse() {
    if (!nationalMatrix || !nationalMatrix.steps) return;
    isTimelapsePlaying = true;
    const btn = document.getElementById('btnPlayTimelapse');
    const playText = document.getElementById('playBtnText');
    if (btn) btn.className = 'px-3 py-1 text-xs font-bold rounded-lg bg-red-600 hover:bg-red-500 text-white transition flex items-center gap-1.5 shadow-sm';
    if (playText) playText.innerText = 'Пауза';

    const liveIdx = nationalMatrix.steps.findIndex(s => s.is_live);
    let currentIdx = (activeForecastStepIndex !== null) ? activeForecastStepIndex : (liveIdx >= 0 ? liveIdx : 0);

    timelapseTimer = setInterval(() => {
        currentIdx++;
        if (currentIdx >= nationalMatrix.steps.length) {
            currentIdx = (liveIdx >= 0 ? liveIdx : 0);
        }
        setForecastStep(currentIdx);
    }, 400);
}

function stopTimelapse() {
    isTimelapsePlaying = false;
    if (timelapseTimer) {
        clearInterval(timelapseTimer);
        timelapseTimer = null;
    }
    const btn = document.getElementById('btnPlayTimelapse');
    const playText = document.getElementById('playBtnText');
    if (btn) btn.className = 'px-3 py-1 text-xs font-bold rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition flex items-center gap-1.5 shadow-sm';
    if (playText) playText.innerText = '24г Таймлапс';
}

function initScrubberControls() {
    const btnLive = document.getElementById('fcBtnLive');
    if (btnLive) btnLive.onclick = setLiveMode;

    const btn30m = document.getElementById('fcBtn30m');
    if (btn30m) btn30m.onclick = () => setForecastOffsetMinutes(30);

    const btn1h = document.getElementById('fcBtn1h');
    if (btn1h) btn1h.onclick = () => setForecastOffsetMinutes(60);

    const btn2h = document.getElementById('fcBtn2h');
    if (btn2h) btn2h.onclick = () => setForecastOffsetMinutes(120);

    const btn4h = document.getElementById('fcBtn4h');
    if (btn4h) btn4h.onclick = () => setForecastOffsetMinutes(240);

    const btn8h = document.getElementById('fcBtn8h');
    if (btn8h) btn8h.onclick = () => setForecastOffsetMinutes(480);

    const btn12h = document.getElementById('fcBtn12h');
    if (btn12h) btn12h.onclick = () => setForecastOffsetMinutes(720);

    const btn24h = document.getElementById('fcBtn24h');
    if (btn24h) btn24h.onclick = () => setForecastOffsetMinutes(1440);

    const btnPlay = document.getElementById('btnPlayTimelapse');
    if (btnPlay) btnPlay.onclick = toggleTimelapse;

    const slider = document.getElementById('forecastTimeSlider');
    if (slider) {
        slider.oninput = (e) => {
            if (isTimelapsePlaying) stopTimelapse();
            setForecastStep(parseInt(e.target.value));
        };
    }
}

// ==========================================
// 12. Lightweight Native Telegram Auth & Channels Modal
// ==========================================


function showInAppToast(message, icon = "fa-circle-check", color = "text-emerald-400") {
    let toast = document.getElementById('inAppToast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'inAppToast';
        toast.className = 'fixed bottom-6 right-6 z-50 bg-slate-900/95 border border-slate-700 px-4 py-3 rounded-xl shadow-2xl flex items-center gap-3 text-sm text-white transition-all duration-300 transform translate-y-12 opacity-0 pointer-events-none';
        document.body.appendChild(toast);
    }
    toast.innerHTML = `<i class="fa-solid ${icon} ${color} text-lg"></i><span class="font-medium">${message}</span>`;
    toast.classList.remove('translate-y-12', 'opacity-0', 'pointer-events-none');
    setTimeout(() => {
        toast.classList.add('translate-y-12', 'opacity-0', 'pointer-events-none');
    }, 3500);
}
function initTelegramAuth() {
    try {
        const saved = localStorage.getItem('ua_alert_user_profile');
        if (saved) {
            currentUserProfile = JSON.parse(saved);
            updateAuthHeaderDisplay();
        }
    } catch (e) {}

    const authBtn = document.getElementById('telegramAuthBtn');
    if (authBtn) {
        authBtn.onclick = openTelegramModal;
    }

    const closeBtn = document.getElementById('closeModalBtn');
    if (closeBtn) {
        closeBtn.onclick = closeTelegramModal;
    }

    const regSelect = document.getElementById('tgRegionSelect');
    if (regSelect) {
        regSelect.onchange = (e) => loadRegionChannels(e.target.value);
    }

    const confirmBtn = document.getElementById('btnConfirmSub');
    if (confirmBtn) {
        confirmBtn.onclick = handleConfirmSubscription;
    }

    const logoutBtn = document.getElementById('btnTgLogout');
    if (logoutBtn) {
        logoutBtn.onclick = handleLogout;
    }

    const scanRegionBtn = document.getElementById('btnScanRegionChannels');
    if (scanRegionBtn) {
        scanRegionBtn.onclick = handleScanRegionChannels;
    }

    const scanCustomBtn = document.getElementById('btnScanCustomChannel');
    if (scanCustomBtn) {
        scanCustomBtn.onclick = handleScanCustomChannel;
    }

    const quickScanBtn = document.getElementById('btnQuickScanTg');
    if (quickScanBtn) {
        quickScanBtn.onclick = handleScanRegionChannels;
    }
}

function handleLogout() {
    currentUserProfile = { username: null, region_id: 'UA-32', is_subscribed: false, precision_mode: 'standard' };
    try {
        localStorage.removeItem('ua_alert_user_profile');
    } catch (e) {}
    updateAuthHeaderDisplay();
    openTelegramModal();
    showInAppToast('Ви вийшли з облікового запису', 'fa-arrow-right-from-bracket', 'text-slate-400');
}

function updateAuthHeaderDisplay() {
    const btnText = document.getElementById('tgBtnText');
    const authBtn = document.getElementById('telegramAuthBtn');
    const quickScanBtn = document.getElementById('btnQuickScanTg');
    if (!btnText || !authBtn) return;

    if (currentUserProfile && currentUserProfile.username) {
        if (currentUserProfile.is_subscribed) {
            btnText.innerHTML = `@${currentUserProfile.username} <span class="text-amber-400 font-bold ml-1">⚡ Ultra</span>`;
            authBtn.className = 'px-3 py-1.5 text-xs font-semibold bg-emerald-950/40 hover:bg-emerald-950/60 text-emerald-300 border border-emerald-500/50 rounded-lg transition flex items-center gap-1.5 shadow-sm';
        } else {
            btnText.innerHTML = `@${currentUserProfile.username}`;
        }
        if (quickScanBtn) quickScanBtn.classList.remove('hidden');
    } else {
        btnText.innerText = 'Telegram Монітор';
        if (quickScanBtn) quickScanBtn.classList.add('hidden');
    }
}

async function handleScanRegionChannels() {
    const regSelect = document.getElementById('tgRegionSelect');
    const activeReg = regSelect && regSelect.value ? regSelect.value : (currentUserProfile?.region_id || selectedRegionId || 'UA-32');
    const regName = regionMetadata[activeReg]?.name_ua || activeReg;

    const btn = document.getElementById('btnScanRegionChannels');
    const btnText = document.getElementById('btnScanRegionText');
    const quickBtn = document.getElementById('btnQuickScanTg');
    const quickText = document.getElementById('btnQuickScanText');
    const feedback = document.getElementById('tgScanFeedback');

    if (btn) btn.disabled = true;
    if (btnText) btnText.innerHTML = `<i class="fa-solid fa-spinner animate-spin"></i> Сканування каналів ${regName}...`;
    if (quickBtn) quickBtn.disabled = true;
    if (quickText) quickText.innerHTML = `Сканування...`;

    if (feedback) {
        feedback.classList.remove('hidden');
        feedback.innerHTML = `<div class="text-sky-400 flex items-center gap-1.5"><i class="fa-solid fa-satellite-dish animate-pulse"></i> Сканування 5 каналів для регіону <strong>${regName}</strong>...</div>`;
    }

    try {
        const res = await fetch('/api/auth/scan_region', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                region_id: activeReg,
                username: currentUserProfile ? currentUserProfile.username : null
            })
        });

        const data = await res.json();
        
        if (data.status === 'success') {
            let detailsHtml = '';
            if (data.channel_results) {
                detailsHtml = data.channel_results.map(ch => {
                    const statusIcon = ch.status === 'success' ? '✅' : '⚠️';
                    const threatsBadge = ch.threats_found > 0 
                        ? `<span class="text-amber-400 font-bold">${ch.threats_found} загроз</span>`
                        : `<span class="text-emerald-400">чисто</span>`;
                    return `<div class="text-[11px] text-slate-300">${statusIcon} <strong>${ch.channel}</strong>: ${ch.messages_found} постів, ${threatsBadge}</div>`;
                }).join('');
            }

            if (feedback) {
                feedback.innerHTML = `
                    <div class="text-emerald-400 font-bold flex items-center gap-1">
                        <i class="fa-solid fa-circle-check"></i> Сканування завершено успішно!
                    </div>
                    <div class="text-slate-300 text-[11px]">Опрацьовано <strong>${data.total_messages_found}</strong> повідомлень, виявлено <strong>${data.total_threats_found}</strong> подій.</div>
                    <div class="mt-1 space-y-0.5 border-t border-slate-800 pt-1">${detailsHtml}</div>
                `;
            }

            showInAppToast(`Проскановано 5 каналів: знайдено ${data.total_threats_found} загроз`, 'fa-radar', 'text-emerald-400');
            
            await loadOverview();
            await loadRecentLogs();
            await loadRegionForecast(activeReg);
        } else {
            if (feedback) {
                feedback.innerHTML = `<div class="text-red-400"><i class="fa-solid fa-triangle-exclamation"></i> Помилка: ${data.error || 'Не вдалося виконати сканування'}</div>`;
            }
        }
    } catch (e) {
        console.error("Scan error:", e);
        if (feedback) {
            feedback.innerHTML = `<div class="text-red-400">Помилка мережі при скануванні</div>`;
        }
    } finally {
        if (btn) btn.disabled = false;
        if (btnText) btnText.innerHTML = `Просканувати 5 каналів області зараз`;
        if (quickBtn) quickBtn.disabled = false;
        if (quickText) quickText.innerHTML = `Сканувати ТГ`;
    }
}

async function handleScanCustomChannel() {
    const inp = document.getElementById('tgCustomChannelInput');
    if (!inp || !inp.value.trim()) {
        showInAppToast('Введіть посилання або username каналу', 'fa-circle-exclamation', 'text-amber-400');
        return;
    }

    const channelVal = inp.value.trim();
    const btn = document.getElementById('btnScanCustomChannel');
    const feedback = document.getElementById('tgScanFeedback');

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `<i class="fa-solid fa-spinner animate-spin"></i>`;
    }

    if (feedback) {
        feedback.classList.remove('hidden');
        feedback.innerHTML = `<div class="text-sky-400"><i class="fa-solid fa-satellite-dish animate-pulse"></i> Сканування ${channelVal}...</div>`;
    }

    try {
        const res = await fetch('/api/auth/scan_channel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                channel: channelVal,
                username: currentUserProfile ? currentUserProfile.username : null
            })
        });

        const data = await res.json();
        if (data.status === 'success') {
            if (feedback) {
                let threatsList = '';
                if (data.threats && data.threats.length > 0) {
                    threatsList = data.threats.map(t => `<div class="text-[10px] text-amber-300">• [${t.alert_level}] ${t.text}</div>`).join('');
                } else {
                    threatsList = `<div class="text-[10px] text-emerald-400">Активних загроз у свіжих постах не виявлено.</div>`;
                }

                feedback.innerHTML = `
                    <div class="text-emerald-400 font-bold flex items-center gap-1">
                        <i class="fa-solid fa-circle-check"></i> Канал ${data.channel} успішно проскановано!
                    </div>
                    <div class="text-slate-300 text-[11px]">Знайдено <strong>${data.messages_found}</strong> повідомлень, <strong>${data.threats_found}</strong> загроз.</div>
                    <div class="mt-1 space-y-0.5 border-t border-slate-800 pt-1">${threatsList}</div>
                `;
            }

            showInAppToast(`Канал ${data.channel}: знайдено ${data.threats_found} загроз`, 'fa-circle-check', 'text-emerald-400');
            inp.value = '';

            await loadOverview();
            await loadRecentLogs();
            await loadRegionForecast(selectedRegionId);
        } else {
            if (feedback) {
                feedback.innerHTML = `<div class="text-red-400"><i class="fa-solid fa-triangle-exclamation"></i> Помилка: ${data.error || 'Не вдалося отримати дані каналу'}</div>`;
            }
        }
    } catch (e) {
        if (feedback) {
            feedback.innerHTML = `<div class="text-red-400">Помилка запиту сканування каналу</div>`;
        }
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `<i class="fa-solid fa-magnifying-glass"></i> <span>Сканувати</span>`;
        }
    }
}

async function openTelegramModal() {
    const modal = document.getElementById('telegramModal');
    if (!modal) return;
    modal.classList.remove('hidden');

    const regSelect = document.getElementById('tgRegionSelect');
    if (regSelect && regSelect.options.length === 0) {
        Object.keys(regionMetadata).forEach(regId => {
            const opt = document.createElement('option');
            opt.value = regId;
            opt.innerText = regionMetadata[regId].name_ua;
            if (regId === (currentUserProfile.region_id || selectedRegionId)) opt.selected = true;
            regSelect.appendChild(opt);
        });
    }

    const profileCard = document.getElementById('tgProfileCard');
    const inputSec = document.getElementById('tgInputSection');
    const userInp = document.getElementById('tgUsernameInput');
    const confirmText = document.getElementById('btnConfirmText');

    if (currentUserProfile && currentUserProfile.username) {
        if (profileCard) profileCard.classList.remove('hidden');
        if (inputSec) inputSec.classList.add('hidden');
        const pUname = document.getElementById('tgProfileUsername');
        if (pUname) pUname.innerText = '@' + currentUserProfile.username;
        const pAvatar = document.getElementById('tgUserAvatar');
        if (pAvatar) pAvatar.innerText = currentUserProfile.username.substring(0, 2).toUpperCase();
        const pReg = document.getElementById('tgProfileRegionLabel');
        if (pReg) pReg.innerText = regionMetadata[currentUserProfile.region_id]?.name_ua || 'Обрана область';
        if (confirmText) confirmText.innerText = 'Оновити канали та статус';
    } else {
        if (profileCard) profileCard.classList.add('hidden');
        if (inputSec) inputSec.classList.remove('hidden');
        if (userInp) userInp.value = '';
        if (confirmText) confirmText.innerText = 'Зберегти та увімкнути Ultra-Precision';
    }

    const activeReg = regSelect ? regSelect.value : (currentUserProfile.region_id || selectedRegionId);
    if (regSelect) regSelect.value = activeReg;
    await loadRegionChannels(activeReg);
}

function closeTelegramModal() {
    const modal = document.getElementById('telegramModal');
    if (modal) modal.classList.add('hidden');
}

async function loadRegionChannels(regId) {
    const container = document.getElementById('tgChannelsList');
    if (!container) return;
    container.innerHTML = '<div class="py-2 text-center text-xs text-slate-400"><i class="fa-solid fa-spinner animate-spin mr-1"></i> Завантаження каналів області...</div>';

    try {
        const res = await fetch(`/api/channels/${regId}`);
        const data = await res.json();
        container.innerHTML = '';

        if (!data.channels || data.channels.length === 0) {
            container.innerHTML = '<div class="text-xs text-slate-400">Канали відсутні</div>';
            return;
        }

        data.channels.forEach(ch => {
            const isOff = ch.is_official;
            const badge = isOff 
                ? '<span class="px-1.5 py-0.5 rounded text-[10px] bg-blue-500/20 text-blue-300 border border-blue-500/40 font-semibold">Офіційний</span>'
                : '<span class="px-1.5 py-0.5 rounded text-[10px] bg-amber-500/20 text-amber-300 border border-amber-500/40 font-semibold">Радар / Монітор</span>';

            const item = document.createElement('div');
            item.className = 'p-2 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between gap-2 shadow-sm';
            item.innerHTML = `
                <div class="min-w-0">
                    <div class="flex items-center gap-1.5 flex-wrap">
                        <span class="font-bold text-xs text-white truncate">${ch.name}</span>
                        ${badge}
                    </div>
                    <span class="text-[11px] text-slate-400 font-mono">@${ch.username}</span>
                </div>
                <a href="${ch.url}" target="_blank" class="flex-shrink-0 px-2.5 py-1 text-[11px] font-semibold bg-sky-600/20 hover:bg-sky-600/30 text-sky-400 border border-sky-500/30 rounded-lg transition flex items-center gap-1">
                    <span>Відкрити</span>
                    <i class="fa-solid fa-arrow-up-right-from-square text-[9px]"></i>
                </a>
            `;
            container.appendChild(item);
        });
    } catch (e) {
        container.innerHTML = '<div class="text-xs text-red-400">Помилка завантаження списку каналів</div>';
    }
}

async function handleConfirmSubscription() {
    const userInp = document.getElementById('tgUsernameInput');
    const regSelect = document.getElementById('tgRegionSelect');
    const btn = document.getElementById('btnConfirmSub');

    let uname = (userInp ? userInp.value.trim() : '') || 'user_monitor';
    uname = uname.replace(/^@/, '');
    const regId = regSelect ? regSelect.value : 'UA-32';

    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin mr-1"></i> Активація...';
    }

    try {
        const res = await fetch('/api/auth/confirm_subscription', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: uname, region_id: regId })
        });
        const data = await res.json();
        
        currentUserProfile = {
            username: uname,
            region_id: regId,
            is_subscribed: true,
            precision_mode: 'ultra'
        };

        try {
            localStorage.setItem('ua_alert_user_profile', JSON.stringify(currentUserProfile));
        } catch (e) {}

        updateAuthHeaderDisplay();
        closeTelegramModal();
        selectRegion(regId);

        showInAppToast('✅ Режим надвисокої точності (Ultra-Precision) успішно активовано!', 'fa-shield-halved', 'text-sky-400');
    } catch (e) {
        console.error('Subscription error:', e);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-shield-halved mr-1"></i><span>Я підписався • Увімкнути надвисоку точність</span>';
        }
    }
}

window.addEventListener('DOMContentLoaded', async () => {
    initIntroSplash();
    initMap();
    initControls();
    initScrubberControls();
    initTelegramAuth();
    
    await loadRegionsList();
    await loadOverview();
    await loadMatrix();
    await loadRegionForecast(selectedRegionId);
    await loadRecentLogs();
    
    initWebSocket();
    
    setInterval(() => {
        if (activeForecastStepIndex === null) {
            loadOverview();
        }
        loadRegionForecast(selectedRegionId);
    }, 10000);

    setInterval(() => {
        loadMatrix();
    }, 45000);
});
