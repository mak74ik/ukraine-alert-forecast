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
let regionMetadata = {};
let fullTimelineData = [];
let currentTimelineFilter = "all";
let radarEnabled = true;
let hoverPointIndex = null;

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

    // REAL-TIME LIVE GROUND-TRUTH SIREN MODE (Strict Red = Active, Strict Green = Calm)
    if (!nationalOverview) {
        return { fillColor: '#15803d', weight: isSelected ? 3.5 : 1.5, color: '#334155', fillOpacity: 0.65 };
    }

    const reg = nationalOverview.regions.find(r => r.id === regionId);
    if (!reg) {
        return { fillColor: '#15803d', weight: isSelected ? 3.5 : 1.5, color: '#334155', fillOpacity: 0.65 };
    }

    // STRICT ACTIVE SIREN
    if (reg.is_active) {
        if (reg.is_partial) {
            return {
                fillColor: '#ea580c', // Orange for partial
                weight: isSelected ? 3.5 : 2,
                opacity: 1,
                color: isSelected ? '#ffffff' : '#f97316',
                dashArray: '4, 4',
                fillOpacity: isSelected ? 0.85 : 0.60
            };
        }
        return {
            fillColor: '#ef4444', // Solid Bright Red for siren
            weight: isSelected ? 3.5 : (regionId === 'UA-30' ? 3 : 1.5),
            opacity: 1,
            color: isSelected ? '#ffffff' : (regionId === 'UA-30' ? '#ffffff' : '#ef4444'),
            fillOpacity: isSelected ? 0.90 : 0.70
        };
    }

    // STRICT CALM REGION (Solid Green)
    return {
        fillColor: '#15803d', // Green
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

            const regData = nationalOverview ? nationalOverview.regions.find(r => r.id === regId) : null;
            let tooltipContent = `<strong>${name}</strong>`;
            
            if (regData && regData.is_active) {
                if (regData.is_partial && regData.sub_regions && regData.sub_regions.length > 0) {
                    const cities = regData.sub_regions.map(c => c.name_ua).join(', ');
                    tooltipContent += `<br><span class="text-amber-400 font-semibold">⚠️ Локальна загроза: ${cities}</span>`;
                } else {
                    tooltipContent += `<br><span class="text-red-400 font-bold">🔴 ПОВІТРЯНА ТРИВОГА</span>`;
                }
            } else {
                tooltipContent += `<br><span class="text-emerald-400 font-semibold">🟢 Відбій тривоги</span>`;
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
            if (data.is_partial && data.sub_regions && data.sub_regions.length > 0) {
                badge.className = "px-3 py-1 text-xs font-bold rounded-full bg-orange-500/20 text-orange-400 border border-orange-500/30 animate-pulse";
                badge.innerText = `⚠️ ЧАСТКОВА ТРИВОГА (В ОКРЕМИХ РАЙОНАХ)`;
                const citiesList = data.sub_regions.map(c => c.name_ua).join(', ');
                descEl.innerHTML = `<span class="text-amber-300 font-semibold">Локалізовані райони під загрозою:</span> ${citiesList}`;
            } else {
                badge.className = "px-3 py-1 text-xs font-bold rounded-full bg-red-500/20 text-red-400 border border-red-500/30 animate-pulse";
                badge.innerText = `🔴 ПОВІТРЯНА ТРИВОГА (ВСЯ ОБЛАСТЬ)`;
                descEl.innerText = `Зафіксовано активну загрозу: ${data.current_threat}`;
            }
        } else {
            badge.className = "px-3 py-1 text-xs font-bold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
            badge.innerText = `🟢 ВІДБІЙ ТРИВОГИ`;
            descEl.innerText = "Прямої загрози зараз немає. Фоновий рівень безпечний.";
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
async function loadRecentLogs() {
    try {
        const res = await fetch('/api/logs?limit=30');
        const logs = await res.json();
        const container = document.getElementById('threatFeedContainer');
        container.innerHTML = '';

        logs.forEach(log => appendLogItem(log, false));
    } catch (e) {
        console.error("Error loading logs:", e);
    }
}

function appendLogItem(log, prepend = true) {
    const container = document.getElementById('threatFeedContainer');
    if (!container) return;
    const item = document.createElement('div');
    
    const isClear = log.is_clear;
    const badgeColor = isClear ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-red-500/20 text-red-400 border-red-500/30';
    const badgeText = isClear ? 'ВІДБІЙ' : (log.threat_type || 'ЗАГРОЗА');

    item.className = "p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs flex flex-col gap-1.5 transition-all hover:border-slate-700 shadow-sm";
    
    const timeStr = new Date(log.created_at || log.timestamp).toLocaleTimeString('uk-UA', { timeZone: 'Europe/Kyiv' });

    let subRegionBadge = '';
    if (log.sub_regions && log.sub_regions.length > 0) {
        const names = log.sub_regions.map(s => s.name_ua).join(', ');
        subRegionBadge = `<span class="px-2 py-0.5 text-[10px] font-bold rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">📍 ${names}</span>`;
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
        "єРадар ППО": "fa-satellite text-blue-400"
    };

    const iconClass = channelIcons[log.channel] || "fa-satellite-dish text-slate-400";

    item.innerHTML = `
        <div class="flex items-center justify-between gap-2 flex-wrap">
            <div class="flex items-center gap-1.5 flex-wrap">
                <i class="fa-solid ${iconClass} text-xs"></i>
                <span class="font-bold text-slate-200">${log.channel || 'Моніторинг'}</span>
                <span class="px-2 py-0.5 text-[10px] font-bold rounded-full ${badgeColor} border">${badgeText}</span>
                ${subRegionBadge}
            </div>
            <span class="text-[10px] text-slate-400 font-mono">${timeStr}</span>
        </div>
        <p class="text-slate-200 text-xs leading-relaxed font-sans">${log.raw_text}</p>
        ${log.direction ? `<div class="text-[10px] text-blue-400 font-medium"><i class="fa-solid fa-compass mr-1"></i>Курс: ${log.direction}</div>` : ''}
    `;

    if (prepend) {
        container.insertBefore(item, container.firstChild);
        if (container.children.length > 40) {
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
window.addEventListener('DOMContentLoaded', async () => {
    initIntroSplash();
    initMap();
    initControls();
    
    await loadRegionsList();
    await loadOverview();
    await loadRegionForecast(selectedRegionId);
    await loadRecentLogs();
    
    initWebSocket();
    
    setInterval(() => {
        loadOverview();
        loadRegionForecast(selectedRegionId);
    }, 10000);
});
