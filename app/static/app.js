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
let raionsLayer = null;
let hotspotsLayer = null;
let radarTracksLayer = null;
let socket = null;
let audioEnabled = false;
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

// Map Tile Layers
let satelliteTileLayer = null;
let darkTileLayer = null;
let currentTileMode = 'satellite';

// 1. Intro Splash Screen & Location Onboarding Controller
function populateOnboardingDropdowns() {
    const oblastSelect = document.getElementById('onboardingOblastSelect');
    const raionSelect = document.getElementById('onboardingRaionSelect');
    if (!oblastSelect || !raionSelect) return;

    // Ordered list of Ukrainian Oblasts
    const oblastList = [
        { id: "UA-32", name: "Київська область" },
        { id: "UA-30", name: "м. Київ" },
        { id: "UA-05", name: "Вінницька область" },
        { id: "UA-07", name: "Волинська область" },
        { id: "UA-12", name: "Дніпропетровська область" },
        { id: "UA-14", name: "Донецька область" },
        { id: "UA-18", name: "Житомирська область" },
        { id: "UA-21", name: "Закарпатська область" },
        { id: "UA-23", name: "Запорізька область" },
        { id: "UA-26", name: "Івано-Франківська область" },
        { id: "UA-35", name: "Кіровоградська область" },
        { id: "UA-09", name: "Луганська область" },
        { id: "UA-46", name: "Львівська область" },
        { id: "UA-48", name: "Миколаївська область" },
        { id: "UA-51", name: "Одеська область" },
        { id: "UA-53", name: "Полтавська область" },
        { id: "UA-56", name: "Рівненська область" },
        { id: "UA-59", name: "Сумська область" },
        { id: "UA-61", name: "Тернопільська область" },
        { id: "UA-63", name: "Харківська область" },
        { id: "UA-65", name: "Херсонська область" },
        { id: "UA-68", name: "Хмельницька область" },
        { id: "UA-71", name: "Черкаська область" },
        { id: "UA-74", name: "Чернігівська область" },
        { id: "UA-77", name: "Чернівецька область" },
        { id: "UA-43", name: "АР Крим" }
    ];

    const currentSavedOblast = localStorage.getItem('user_home_oblast') || 'UA-32';
    const currentSavedRaion = localStorage.getItem('user_home_raion') || '';

    oblastSelect.innerHTML = '';
    oblastList.forEach(ob => {
        const opt = document.createElement('option');
        opt.value = ob.id;
        opt.innerText = ob.name;
        if (ob.id === currentSavedOblast) opt.selected = true;
        oblastSelect.appendChild(opt);
    });

    const updateRaionsForOblast = (oblastId) => {
        raionSelect.innerHTML = '<option value="">Вся область (за замовчуванням)</option>';
        if (typeof UKRAINE_RAIONS_GEOJSON !== 'undefined' && UKRAINE_RAIONS_GEOJSON.features) {
            const raionNames = new Set();
            UKRAINE_RAIONS_GEOJSON.features.forEach(f => {
                if (f.properties && f.properties.oblast_id === oblastId && f.properties.raion_name_ua) {
                    raionNames.add(f.properties.raion_name_ua);
                }
            });
            const sortedRaions = Array.from(raionNames).sort((a, b) => a.localeCompare(b, 'uk'));
            sortedRaions.forEach(rName => {
                const opt = document.createElement('option');
                opt.value = rName;
                opt.innerText = `${rName} район`;
                if (rName === currentSavedRaion) opt.selected = true;
                raionSelect.appendChild(opt);
            });
        }
    };

    updateRaionsForOblast(oblastSelect.value);
    oblastSelect.onchange = () => updateRaionsForOblast(oblastSelect.value);
}

function updateHomeDistrictWidget() {
    const homeOblast = localStorage.getItem('user_home_oblast') || 'UA-32';
    const homeRaion = localStorage.getItem('user_home_raion') || '';
    const oblastName = regionMetadata[homeOblast]?.name_ua || (homeOblast === 'UA-30' ? 'м. Київ' : 'Київська область');

    const textEl = document.getElementById('headerHomeDistrictText');
    const badgeEl = document.getElementById('headerHomeDistrictStatusBadge');
    if (!textEl || !badgeEl) return;

    textEl.innerText = homeRaion ? `${homeRaion} р-н, ${oblastName}` : oblastName;

    if (!nationalOverview || !nationalOverview.regions) {
        badgeEl.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-slate-800 text-slate-400 border border-slate-700';
        badgeEl.innerText = 'Оновлення...';
        return;
    }

    const reg = nationalOverview.regions.find(r => r.id === homeOblast);
    if (!reg || !reg.is_active) {
        badgeEl.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
        badgeEl.innerText = '🟢 Спокійно';
        return;
    }

    // Oblast has active alert!
    if (reg.is_partial && homeRaion) {
        const isMatched = (reg.sub_regions || []).some(sub => {
            const sName = (sub.name_ua || '').toLowerCase();
            const rLower = homeRaion.toLowerCase();
            return sName.includes(rLower) || rLower.includes(sName);
        });

        if (isMatched) {
            const lvl = reg.alert_level || 'RED';
            const bgClass = lvl === 'RED' ? 'bg-red-500/25 text-red-300 border-red-500/50 animate-pulse' : 'bg-yellow-500/25 text-yellow-300 border-yellow-500/50 animate-pulse';
            badgeEl.className = `px-2 py-0.5 rounded text-[10px] font-bold border ${bgClass}`;
            badgeEl.innerText = `🔴 ТРИВОГА В ${homeRaion.toUpperCase()} Р-НІ`;
        } else {
            badgeEl.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
            badgeEl.innerText = '🟢 У районі спокійно (тривога в іншій частині)';
        }
    } else {
        const lvl = reg.alert_level || 'RED';
        const lvlText = lvl === 'RED' ? '🔴 ТРИВОГА (РАКЕТИ)' : (lvl === 'ORANGE' ? '🟠 ЗАГРОЗА КАБ' : '🟡 ЗАГРОЗА БПЛА');
        const bgClass = lvl === 'RED' ? 'bg-red-500/25 text-red-300 border-red-500/50 animate-pulse' : 'bg-yellow-500/25 text-yellow-300 border-yellow-500/50 animate-pulse';
        badgeEl.className = `px-2 py-0.5 rounded text-[10px] font-bold border ${bgClass}`;
        badgeEl.innerText = lvlText;
    }
}

function initIntroSplash() {
    const splash = document.getElementById('introSplash');
    const flagContainer = document.getElementById('flagContainer');
    const pBar = document.getElementById('splashProgressBar');
    const statusText = document.getElementById('splashStatusText');
    const loadingSection = document.getElementById('splashLoadingSection');
    const onboardingCard = document.getElementById('onboardingCard');
    const submitBtn = document.getElementById('onboardingSubmitBtn');

    if (!splash) return;

    const savedOblast = localStorage.getItem('user_home_oblast');
    const savedRaion = localStorage.getItem('user_home_raion');

    if (savedOblast) {
        selectedRegionId = savedOblast;
        updateHomeDistrictWidget();
        
        let progress = 35;
        const interval = setInterval(() => {
            progress += 30;
            if (pBar) pBar.style.width = `${Math.min(100, progress)}%`;
            if (progress >= 100) {
                clearInterval(interval);
                if (statusText) statusText.innerText = "Автономна синхронізація завершена";
                setTimeout(dismissSplash, 400);
            }
        }, 120);
    } else {
        // First Launch: Smooth progress, flag lifts, then Onboarding form appears!
        let progress = 20;
        const interval = setInterval(() => {
            progress += 25;
            if (pBar) pBar.style.width = `${Math.min(100, progress)}%`;
            if (progress >= 100) {
                clearInterval(interval);
                if (statusText) statusText.innerText = "Оберіть вашу область та район для сповіщень";
                if (loadingSection) loadingSection.classList.add('hidden');
                
                // Lift Flag
                if (flagContainer) flagContainer.classList.add('flag-lifted');
                
                // Show Onboarding Card
                if (onboardingCard) onboardingCard.classList.remove('hidden');
                populateOnboardingDropdowns();
            }
        }, 180);
    }

    if (submitBtn) {
        submitBtn.onclick = () => {
            const oblastSelect = document.getElementById('onboardingOblastSelect');
            const raionSelect = document.getElementById('onboardingRaionSelect');
            if (oblastSelect) {
                const chosenOblast = oblastSelect.value || 'UA-32';
                const chosenRaion = raionSelect ? raionSelect.value : '';
                localStorage.setItem('user_home_oblast', chosenOblast);
                localStorage.setItem('user_home_raion', chosenRaion);
                selectedRegionId = chosenOblast;
                selectRegion(chosenOblast);
                updateHomeDistrictWidget();
            }
            dismissSplash();
        };
    }

    function dismissSplash() {
        splash.classList.add('splash-hidden');
        if (map) {
            setTimeout(() => map.invalidateSize(), 300);
        }
        drawCanvasTimeline();
    }
}

// 2. Leaflet Map with ESRI High-Res Satellite & Dark Layer Switcher
function setMapTileMode(mode) {
    currentTileMode = mode;
    const btnSat = document.getElementById('btnLayerSatellite');
    const btnDark = document.getElementById('btnLayerDark');

    if (mode === 'satellite') {
        if (map && darkTileLayer && map.hasLayer(darkTileLayer)) map.removeLayer(darkTileLayer);
        if (map && satelliteTileLayer && !map.hasLayer(satelliteTileLayer)) satelliteTileLayer.addTo(map);
        if (btnSat) btnSat.className = 'px-2 py-0.5 rounded-md font-bold bg-sky-600 text-white shadow-sm transition flex items-center gap-1';
        if (btnDark) btnDark.className = 'px-2 py-0.5 rounded-md font-medium text-slate-400 hover:text-slate-200 transition flex items-center gap-1';
    } else {
        if (map && satelliteTileLayer && map.hasLayer(satelliteTileLayer)) map.removeLayer(satelliteTileLayer);
        if (map && darkTileLayer && !map.hasLayer(darkTileLayer)) darkTileLayer.addTo(map);
        if (btnDark) btnDark.className = 'px-2 py-0.5 rounded-md font-bold bg-slate-700 text-white shadow-sm transition flex items-center gap-1';
        if (btnSat) btnSat.className = 'px-2 py-0.5 rounded-md font-medium text-slate-400 hover:text-slate-200 transition flex items-center gap-1';
    }
}

function initMap() {
    map = L.map('ukraineMap', {
        center: [48.5, 31.5],
        zoom: 6,
        zoomControl: true,
        attributionControl: false
    });

    // ESRI High-Resolution Satellite World Imagery
    satelliteTileLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 18,
        minZoom: 5,
        attribution: 'Esri Satellite'
    });

    // CartoDB Dark Alternative Layer
    darkTileLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        subdomains: 'abcd',
        maxZoom: 18,
        minZoom: 5
    });

    // Default to Satellite
    satelliteTileLayer.addTo(map);

    // Wire up Layer Switcher Buttons
    const btnSat = document.getElementById('btnLayerSatellite');
    const btnDark = document.getElementById('btnLayerDark');
    if (btnSat) btnSat.onclick = () => setMapTileMode('satellite');
    if (btnDark) btnDark.onclick = () => setMapTileMode('dark');

    hotspotsLayer = L.layerGroup().addTo(map);
    radarTracksLayer = L.layerGroup().addTo(map);

    // Re-render hotspots on zoom change for zoom-responsive sizing
    map.on('zoomend', () => {
        renderHotspotMarkers();
    });

    renderGeoJsonLayer();
}

function isRaionMatch(raionFeature, subRegionsList) {
    if (!subRegionsList || subRegionsList.length === 0) return false;
    const p = raionFeature.properties || {};
    const rName = (p.raion_name_ua || '').toLowerCase();

    for (const sub of subRegionsList) {
        const subName = (sub.name_ua || '').toLowerCase();
        if (subName.includes(rName) || rName.includes(subName)) return true;
        
        const stem = rName.replace(/(ський|цький|зький| район)$/g, '').trim();
        if (stem && stem.length >= 3 && subName.includes(stem)) return true;

        if (sub.aliases) {
            for (const al of sub.aliases) {
                const alLower = al.toLowerCase();
                if (rName.includes(alLower) || alLower.includes(stem)) return true;
            }
        }
    }
    return false;
}

function getRaionStyle(feature) {
    const p = feature.properties || {};
    const oblastId = p.oblast_id;
    const isSelected = oblastId === selectedRegionId;

    // 1. FORECAST MODE
    if (activeForecastStepIndex !== null && nationalMatrix && nationalMatrix.steps && nationalMatrix.steps[activeForecastStepIndex]) {
        const step = nationalMatrix.steps[activeForecastStepIndex];
        const prob = (step.regions_risk && step.regions_risk[oblastId] !== undefined) ? step.regions_risk[oblastId] : 0.05;
        const level = (step.regions_alert_level && step.regions_alert_level[oblastId]) ? step.regions_alert_level[oblastId] : 'CLEAR';

        if (level === 'YELLOW') {
            return {
                fillColor: '#eab308',
                weight: isSelected ? 2.5 : 1,
                opacity: 0.9,
                color: isSelected ? '#ffffff' : '#ca8a04',
                fillOpacity: Math.min(0.85, Math.max(0.40, 0.30 + prob * 0.55))
            };
        } else if (level === 'RED') {
            return {
                fillColor: '#ef4444',
                weight: isSelected ? 2.5 : 1,
                opacity: 0.9,
                color: isSelected ? '#ffffff' : '#dc2626',
                fillOpacity: Math.min(0.90, Math.max(0.50, 0.40 + prob * 0.55))
            };
        } else if (level === 'ORANGE') {
            return {
                fillColor: '#f97316',
                weight: isSelected ? 2.5 : 1,
                opacity: 0.9,
                color: isSelected ? '#ffffff' : '#ea580c',
                fillOpacity: Math.min(0.85, Math.max(0.45, 0.35 + prob * 0.55))
            };
        } else {
            return {
                fillColor: '#0f172a',
                weight: 0.6,
                opacity: 0.6,
                color: isSelected ? '#38bdf8' : '#1e293b',
                fillOpacity: isSelected ? 0.35 : 0.15
            };
        }
    }

    // 2. LIVE REAL-TIME MODE
    if (!nationalOverview || !nationalOverview.regions) {
        return { fillColor: '#0f172a', weight: 0.6, opacity: 0.5, color: '#1e293b', fillOpacity: 0.15 };
    }

    const reg = nationalOverview.regions.find(r => r.id === oblastId);
    if (!reg || !reg.is_active) {
        return {
            fillColor: '#0f172a',
            weight: 0.6,
            opacity: 0.7,
            color: isSelected ? '#38bdf8' : '#1e293b',
            fillOpacity: isSelected ? 0.30 : 0.12
        };
    }

    const alertLvl = reg.alert_level || 'YELLOW';
    const activeFill = alertLvl === 'RED' ? '#ef4444' : (alertLvl === 'ORANGE' ? '#f97316' : '#eab308');
    const activeStroke = alertLvl === 'RED' ? '#fca5a5' : (alertLvl === 'ORANGE' ? '#fdba74' : '#fde047');

    if (reg.is_partial) {
        // Partial alert in oblast: ONLY the specific matched district lights up!
        if (isRaionMatch(feature, reg.sub_regions)) {
            return {
                fillColor: activeFill,
                weight: 2.8,
                opacity: 1,
                color: '#ffffff',
                fillOpacity: 0.92,
                dashArray: ''
            };
        } else {
            // Calm district inside partially alarmed oblast
            return {
                fillColor: '#090d16',
                weight: 0.8,
                opacity: 0.6,
                color: '#334155',
                fillOpacity: 0.22
            };
        }
    }

    // Full oblast alert -> all districts in oblast are active
    return {
        fillColor: activeFill,
        weight: 1.2,
        opacity: 0.9,
        color: activeStroke,
        fillOpacity: 0.82
    };
}

function getRegionStyle(regionId) {
    const isSelected = regionId === selectedRegionId;

    if (activeForecastStepIndex !== null && nationalMatrix && nationalMatrix.steps && nationalMatrix.steps[activeForecastStepIndex]) {
        const step = nationalMatrix.steps[activeForecastStepIndex];
        const level = (step.regions_alert_level && step.regions_alert_level[regionId]) ? step.regions_alert_level[regionId] : 'CLEAR';

        return {
            fillColor: 'transparent',
            weight: isSelected ? 3.5 : (regionId === 'UA-30' ? 2.5 : 1.8),
            opacity: 1,
            color: isSelected ? '#ffffff' : (level === 'RED' ? '#f87171' : (level === 'ORANGE' ? '#fb923c' : (level === 'YELLOW' ? '#facc15' : '#334155'))),
            fillOpacity: 0
        };
    }

    if (!nationalOverview) {
        return { fillColor: 'transparent', weight: isSelected ? 3.5 : 1.8, color: '#334155', fillOpacity: 0 };
    }

    const reg = nationalOverview.regions.find(r => r.id === regionId);
    if (!reg) {
        return { fillColor: 'transparent', weight: isSelected ? 3.5 : 1.8, color: '#334155', fillOpacity: 0 };
    }

    if (reg.is_active) {
        if (reg.is_partial) {
            return {
                fillColor: 'transparent',
                weight: isSelected ? 3.2 : 2.0,
                opacity: 0.9,
                color: isSelected ? '#ffffff' : '#f97316',
                dashArray: '6, 4',
                fillOpacity: 0
            };
        }

        const alertLvl = reg.alert_level || 'YELLOW';
        const color = alertLvl === 'RED' ? '#ef4444' : (alertLvl === 'ORANGE' ? '#f97316' : '#eab308');
        return {
            fillColor: 'transparent',
            weight: isSelected ? 3.5 : 2.2,
            opacity: 1,
            color: isSelected ? '#ffffff' : color,
            fillOpacity: 0
        };
    }

    return {
        fillColor: 'transparent',
        weight: isSelected ? 3.5 : (regionId === 'UA-30' ? 2.2 : 1.5),
        opacity: 0.8,
        color: isSelected ? '#38bdf8' : (regionId === 'UA-30' ? '#fbbf24' : '#1e293b'),
        fillOpacity: 0
    };
}

function renderGeoJsonLayer() {
    if (geojsonLayer) {
        map.removeLayer(geojsonLayer);
    }
    if (raionsLayer) {
        map.removeLayer(raionsLayer);
    }

    // 1. Render Raions Polygons Layer (Detailed Districts Level)
    if (typeof UKRAINE_RAIONS_GEOJSON !== 'undefined') {
        raionsLayer = L.geoJSON(UKRAINE_RAIONS_GEOJSON, {
            style: (feature) => getRaionStyle(feature),
            onEachFeature: (feature, layer) => {
                const p = feature.properties || {};
                const raionName = p.raion_name_ua || 'Район';
                const oblastName = p.oblast_name_ua || '';
                const oblastId = p.oblast_id;

                let tooltipHtml = `<div class="p-1">
                    <div class="font-bold text-xs text-white">📍 ${raionName} район</div>
                    ${oblastName ? `<div class="text-[10px] text-slate-400">${oblastName} область</div>` : ''}
                `;

                if (activeForecastStepIndex !== null && nationalMatrix && nationalMatrix.steps && nationalMatrix.steps[activeForecastStepIndex]) {
                    const step = nationalMatrix.steps[activeForecastStepIndex];
                    const prob = Math.round(((step.regions_risk && step.regions_risk[oblastId]) || 0) * 100);
                    const lvl = (step.regions_alert_level && step.regions_alert_level[oblastId]) || 'CLEAR';
                    
                    tooltipHtml += `<div class="text-[10px] font-mono text-sky-300 mt-0.5">Прогноз на ${step.time_display}</div>`;
                    if (lvl === 'YELLOW') {
                        tooltipHtml += `<div class="text-xs text-yellow-300 font-bold mt-0.5">🟡 ЖОВТИЙ (БПЛА) • ${prob}%</div>`;
                    } else if (lvl === 'RED') {
                        tooltipHtml += `<div class="text-xs text-red-400 font-bold mt-0.5">🔴 ЧЕРВОНИЙ (РАКЕТИ) • ${prob}%</div>`;
                    } else if (lvl === 'ORANGE') {
                        tooltipHtml += `<div class="text-xs text-orange-400 font-bold mt-0.5">🟠 ПОМАРАНЧЕВИЙ (КАБ) • ${prob}%</div>`;
                    } else {
                        tooltipHtml += `<div class="text-[11px] text-emerald-400 font-semibold mt-0.5">🟢 Спокійно (${prob}% фон)</div>`;
                    }
                } else {
                    const regData = nationalOverview ? nationalOverview.regions.find(r => r.id === oblastId) : null;
                    if (regData && regData.is_active) {
                        const isThisRaionActive = !regData.is_partial || isRaionMatch(feature, regData.sub_regions);
                        if (isThisRaionActive) {
                            const lvl = regData.alert_level || 'YELLOW';
                            const lvlTitle = lvl === 'RED' ? '🔴 ЧЕРВОНИЙ (РАКЕТИ)' : (lvl === 'ORANGE' ? '🟠 ПОМАРАНЧЕВИЙ (КАБ)' : '🟡 ЖОВТИЙ (БПЛА)');
                            const lvlColor = lvl === 'RED' ? 'text-red-400' : (lvl === 'ORANGE' ? 'text-orange-400' : 'text-yellow-400');
                            tooltipHtml += `<div class="text-xs ${lvlColor} font-bold mt-0.5">${lvlTitle}</div>`;
                            if (regData.threat_title) {
                                tooltipHtml += `<div class="text-[10px] text-slate-300">${regData.threat_title}</div>`;
                            }
                        } else {
                            tooltipHtml += `<div class="text-[11px] text-slate-400 mt-0.5">🟢 Без прямої загрози в цьому районі</div>`;
                        }
                    } else {
                        tooltipHtml += `<div class="text-[11px] text-emerald-400 font-semibold mt-0.5">🟢 Відбій загрози</div>`;
                    }
                }
                tooltipHtml += `</div>`;

                layer.bindTooltip(tooltipHtml, {
                    sticky: true,
                    direction: 'top',
                    className: 'bg-slate-950 text-white border border-slate-700 px-2.5 py-1.5 rounded-lg text-xs font-sans shadow-xl'
                });

                layer.on({
                    mouseover: (e) => {
                        const l = e.target;
                        l.setStyle({ weight: 3.2, color: '#ffffff', opacity: 1 });
                        l.bringToFront();
                    },
                    mouseout: (e) => {
                        if (raionsLayer) raionsLayer.resetStyle(e.target);
                    },
                    click: () => {
                        if (oblastId) {
                            selectRegion(oblastId);
                        }
                    }
                });
            }
        }).addTo(map);
    }

    // 2. Render Oblast Outline Layer (for clean oblast boundaries)
    if (typeof UKRAINE_GEOJSON !== 'undefined') {
        geojsonLayer = L.geoJSON(UKRAINE_GEOJSON, {
            style: (feature) => getRegionStyle(feature.properties.id),
            interactive: false
        }).addTo(map);
    }

    renderHotspotMarkers();
    renderRadarTracks();

    if (raionsLayer && raionsLayer.getLayers().length > 0) {
        map.fitBounds(raionsLayer.getBounds(), { padding: [10, 10] });
    } else if (geojsonLayer && geojsonLayer.getLayers().length > 0) {
        map.fitBounds(geojsonLayer.getBounds(), { padding: [10, 10] });
    }
}

// 3. Render Sub-Regional Pinpoint Hotspots (Cities/Raions) — Sleek Tactical Pinpoints
function renderHotspotMarkers() {
    if (!hotspotsLayer) return;
    hotspotsLayer.clearLayers();

    if (!nationalOverview || !nationalOverview.hotspots) return;

    const zoom = map ? map.getZoom() : 6;

    nationalOverview.hotspots.forEach(spot => {
        if (!spot.lat || !spot.lon) return;

        // Clean tactical pinpoint dot
        const dot = L.circleMarker([spot.lat, spot.lon], {
            radius: zoom >= 8 ? 6 : 4.5,
            fillColor: '#ef4444',
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.95
        });

        // City / Raion name label (visible at zoom >= 7)
        if (zoom >= 7) {
            const label = L.marker([spot.lat, spot.lon], {
                icon: L.divIcon({
                    html: `<div class="hotspot-label text-slate-100">📍 ${spot.name_ua}</div>`,
                    className: 'hotspot-label-container',
                    iconSize: [140, 20],
                    iconAnchor: [70, -8]
                })
            });
            label.addTo(hotspotsLayer);
        }

        dot.bindTooltip(
            `<div class="p-0.5">
                <div class="font-bold text-xs text-red-400">📍 ${spot.name_ua}</div>
                <div class="text-[10px] text-slate-300 mt-0.5">Локалізована небезпека</div>
            </div>`,
            {
                sticky: true,
                direction: 'top',
                className: 'bg-slate-950 text-white border border-slate-700 px-2.5 py-1.5 rounded-lg text-xs shadow-xl'
            }
        );

        dot.addTo(hotspotsLayer);
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
            const lvl = data.alert_level || 'YELLOW';
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
        
        updateHomeDistrictWidget();
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
        const clockEl = document.getElementById('liveClock');
        if (clockEl) {
            clockEl.innerText = now.toLocaleTimeString('uk-UA', { timeZone: 'Europe/Kyiv' });
        }
    }, 1000);

    const soundBtn = document.getElementById('soundToggleBtn');
    if (soundBtn) {
        soundBtn.addEventListener('click', () => {
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            audioEnabled = !audioEnabled;
            soundBtn.innerHTML = audioEnabled 
                ? '<i class="fa-solid fa-volume-high text-emerald-400"></i>' 
                : '<i class="fa-solid fa-volume-xmark text-slate-500"></i>';
        });
    }

    const changeLocBtn = document.getElementById('btnHeaderChangeLocation');
    if (changeLocBtn) {
        changeLocBtn.addEventListener('click', () => {
            const splash = document.getElementById('introSplash');
            const flagContainer = document.getElementById('flagContainer');
            const statusText = document.getElementById('splashStatusText');
            const loadingSection = document.getElementById('splashLoadingSection');
            const onboardingCard = document.getElementById('onboardingCard');

            if (splash) {
                if (flagContainer) flagContainer.classList.add('flag-lifted');
                if (statusText) statusText.innerText = "Зміна локації для сповіщень";
                if (loadingSection) loadingSection.classList.add('hidden');
                if (onboardingCard) onboardingCard.classList.remove('hidden');
                populateOnboardingDropdowns();
                splash.classList.remove('splash-hidden');
            }
        });
    }

    const radarToggle = document.getElementById('toggleRadarLayer');
    if (radarToggle) {
        radarToggle.addEventListener('change', (e) => {
            radarEnabled = e.target.checked;
            renderRadarTracks();
        });
    }

    const syncBtn = document.getElementById('syncNowBtn');
    if (syncBtn) {
        syncBtn.addEventListener('click', async () => {
            try {
                syncBtn.disabled = true;
                syncBtn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i> Синхронізація...';
                await fetch('/api/sync_now', { method: 'POST' });
                await loadOverview();
                await loadRegionForecast(selectedRegionId);
                showInAppToast('Синхронізація успішна', 'fa-rotate', 'text-emerald-400');
            } catch (e) {
                console.error("Sync error:", e);
            } finally {
                syncBtn.disabled = false;
                syncBtn.innerHTML = '<i class="fa-solid fa-rotate text-emerald-400"></i> Синхронізувати';
            }
        });
    }

    // Timeline Filter Buttons
    const setFilter = (f) => {
        currentTimelineFilter = f;
        drawCanvasTimeline();
    };

    const btnPast = document.getElementById('btnViewPast');
    const btnLive = document.getElementById('btnViewLive');
    const btn6h = document.getElementById('btnView6h');
    const btn12h = document.getElementById('btnView12h');
    const btn24h = document.getElementById('btnView24h');
    const btnFuture = document.getElementById('btnViewFuture');

    if (btnPast) btnPast.addEventListener('click', () => setFilter('past'));
    if (btnLive) btnLive.addEventListener('click', () => setFilter('live'));
    if (btn6h) btn6h.addEventListener('click', () => setFilter('6h'));
    if (btn12h) btn12h.addEventListener('click', () => setFilter('12h'));
    if (btn24h) btn24h.addEventListener('click', () => setFilter('24h'));
    if (btnFuture) btnFuture.addEventListener('click', () => setFilter('24h'));

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

window.addEventListener('DOMContentLoaded', async () => {
    initIntroSplash();
    initMap();
    initControls();
    initScrubberControls();
    
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
