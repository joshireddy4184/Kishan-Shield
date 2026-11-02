// Kishan Shield AI - Real-World Client Application Controller
// Comprehensive Multilingual, Real-Time Device GPS Location, & Agricultural Decision Engine

let leafletMap = null;
let currentLanguage = localStorage.getItem('kisanshield_lang') || 'en';

let currentFarmer = {
  name: "Ramesh Patil",
  state: "Maharashtra",
  district: "Nashik",
  village: "Pimpalgaon",
  lat: null,
  lon: null,
  crop: "Onion",
  acres: 3.0,
  yield_q: 50.0,
  invested_rs: 52000.0,
  additional_rs: 18000.0,
  is_live_location: false,
  location_status: "detecting" // "detecting" | "live" | "manual"
};

document.addEventListener('DOMContentLoaded', () => {
  console.log("Kishan Shield AI Client Initialized.");
  setLanguage(currentLanguage);
  
  // Mandatory: Attempt automatic real-time device location detection on load
  autoDetectDeviceLocation(false);
  
  loadFarmMemory();
  loadModelMetrics();
  
  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
});

// Centralized Translation Helper
function t(key, lang = currentLanguage) {
  if (typeof TRANSLATIONS !== 'undefined') {
    if (TRANSLATIONS[lang] && TRANSLATIONS[lang][key] !== undefined) {
      return TRANSLATIONS[lang][key];
    }
    if (TRANSLATIONS['en'] && TRANSLATIONS['en'][key] !== undefined) {
      return TRANSLATIONS['en'][key];
    }
  }
  return key;
}

// Immediate Language Switcher
function setLanguage(lang) {
  currentLanguage = lang || 'en';
  localStorage.setItem('kisanshield_lang', currentLanguage);
  
  // Set HTML language and Direction (RTL for Urdu)
  document.documentElement.lang = currentLanguage;
  if (currentLanguage === 'ur') {
    document.documentElement.setAttribute('dir', 'rtl');
  } else {
    document.documentElement.setAttribute('dir', 'ltr');
  }

  const select = document.getElementById('lang-select');
  if (select) select.value = currentLanguage;
  
  updateUILanguage();
}

function changeLanguage(lang) {
  setLanguage(lang);
}

function updateUILanguage() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const translated = t(key);
    if (translated) {
      el.innerHTML = translated;
    }
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    const translated = t(key);
    if (translated) {
      el.placeholder = translated;
    }
  });

  // Chat placeholder & buttons
  const chatInput = document.getElementById('chat-input');
  if (chatInput) chatInput.placeholder = t('chat.placeholder');

  const chatSendBtn = document.getElementById('chat-send-btn');
  if (chatSendBtn) chatSendBtn.innerText = t('chat.sendBtn');

  const chatFloatBtn = document.getElementById('chat-float-btn');
  if (chatFloatBtn) chatFloatBtn.innerHTML = `<span style="font-size: 1.2rem;">🤖</span> ${t('chat.floatBtn')}`;

  // Update dynamic location labels
  updateLocationUI();

  // Re-render market table for current language
  if (document.getElementById('market-table-body')) {
    loadNearbyMarkets();
  }

  if (typeof lucide !== 'undefined') {
    lucide.createIcons();
  }
}

// Automatic Real-Time Device Location Detection
function autoDetectDeviceLocation(isManualRefresh = false) {
  const topbarDot = document.getElementById('loc-indicator-dot');
  const topbarText = document.getElementById('topbar-loc-text');
  const topbarBadge = document.getElementById('topbar-loc-badge');
  const obStatus = document.getElementById('location-status');
  const dashDot = document.getElementById('dash-gps-dot');
  const dashMode = document.getElementById('dash-loc-mode');
  const dashName = document.getElementById('dash-loc-name');
  const dashCoords = document.getElementById('dash-loc-coords');

  currentFarmer.location_status = "detecting";

  // Visual indicating state
  if (topbarDot) topbarDot.className = 'dot-gps-detecting';
  if (topbarText) topbarText.innerText = t('topbar.gpsDetecting');
  if (obStatus) obStatus.innerHTML = `<em>${t('topbar.gpsDetecting')}</em>`;
  if (dashDot) dashDot.className = 'dot-gps-detecting';
  if (dashMode) {
    dashMode.className = 'indicator-pill pill-amber';
    dashMode.innerText = "GPS Detecting...";
  }
  if (dashName) dashName.innerText = t('topbar.gpsDetecting');
  if (dashCoords) dashCoords.innerText = "Connecting to device GPS satellites...";

  if (!navigator.geolocation) {
    handleLocationFailure("Geolocation not supported by this browser/device.");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      const lat = pos.coords.latitude;
      const lon = pos.coords.longitude;
      currentFarmer.lat = lat;
      currentFarmer.lon = lon;
      currentFarmer.is_live_location = true;
      currentFarmer.location_status = "live";

      // Reverse geocode to get actual village/locality, district, state
      fetch(`/api/reverse-geocode?lat=${lat}&lon=${lon}`)
        .then(res => res.json())
        .then(geo => {
          if (geo.village || geo.locality) {
            currentFarmer.village = geo.village || geo.locality;
          }
          if (geo.district) {
            currentFarmer.district = geo.district;
          }
          if (geo.state) {
            currentFarmer.state = geo.state;
          }

          // Update form fields
          const stateInput = document.getElementById('ob-state');
          if (stateInput && currentFarmer.state) stateInput.value = currentFarmer.state;
          const distInput = document.getElementById('ob-district');
          if (distInput && currentFarmer.district) distInput.value = currentFarmer.district;

          updateLocationUI();
          fetchRealtimeWeather(lat, lon);
          loadNearbyMarkets();
          
          if (isManualRefresh) {
            alert(`📍 Location updated: ${currentFarmer.village ? currentFarmer.village + ', ' : ''}${currentFarmer.district}, ${currentFarmer.state}\nLat: ${lat.toFixed(4)}, Lon: ${lon.toFixed(4)}`);
          }
        })
        .catch(err => {
          console.warn("Reverse geocode fetch failed, using coordinates directly:", err);
          updateLocationUI();
          fetchRealtimeWeather(lat, lon);
          loadNearbyMarkets();
        });
    },
    (err) => {
      console.warn("Geolocation permission denied or timed out:", err.message);
      handleLocationFailure(err.message);
    },
    { enableHighAccuracy: true, timeout: 8000, maximumAge: 30000 }
  );
}

function handleLocationFailure(reason) {
  currentFarmer.is_live_location = false;
  currentFarmer.location_status = "manual";
  // Safe regional default coordinate if null
  if (!currentFarmer.lat || !currentFarmer.lon) {
    currentFarmer.lat = 19.9975;
    currentFarmer.lon = 73.7898;
  }
  
  updateLocationUI();
  fetchRealtimeWeather(currentFarmer.lat, currentFarmer.lon);
  loadNearbyMarkets();
}

function updateLocationUI() {
  const topbarDot = document.getElementById('loc-indicator-dot');
  const topbarText = document.getElementById('topbar-loc-text');
  const topbarBadge = document.getElementById('topbar-loc-badge');
  const obStatus = document.getElementById('location-status');
  const dashDot = document.getElementById('dash-gps-dot');
  const dashMode = document.getElementById('dash-loc-mode');
  const dashName = document.getElementById('dash-loc-name');
  const dashCoords = document.getElementById('dash-loc-coords');

  const locDisplay = `${currentFarmer.village ? currentFarmer.village + ', ' : ''}${currentFarmer.district}, ${currentFarmer.state}`;

  if (currentFarmer.is_live_location && currentFarmer.lat) {
    if (topbarDot) topbarDot.className = 'dot-gps-live';
    if (topbarText) topbarText.innerText = `${t('topbar.gpsLive')} ${currentFarmer.village || currentFarmer.district}`;
    if (topbarBadge) topbarBadge.title = `Live GPS: ${currentFarmer.lat.toFixed(4)}, ${currentFarmer.lon.toFixed(4)}`;
    
    if (obStatus) {
      obStatus.innerHTML = `<strong>📍 ${t('topbar.gpsLive')}</strong> ${locDisplay} <span style="font-size:0.8rem; color:var(--text-muted);">(Lat: ${currentFarmer.lat.toFixed(4)}, Lon: ${currentFarmer.lon.toFixed(4)})</span>`;
      obStatus.style.color = "#15803d";
    }

    if (dashDot) dashDot.className = 'dot-gps-live';
    if (dashMode) {
      dashMode.className = 'indicator-pill pill-green';
      dashMode.innerText = t('dash.gpsActive');
    }
    if (dashName) dashName.innerText = locDisplay;
    if (dashCoords) dashCoords.innerText = `GPS Coordinates: ${currentFarmer.lat.toFixed(4)}° N, ${currentFarmer.lon.toFixed(4)}° E (High Accuracy)`;
  } else {
    if (topbarDot) topbarDot.className = 'dot-gps-manual';
    if (topbarText) topbarText.innerText = `${t('topbar.gpsManual')} ${currentFarmer.district}, ${currentFarmer.state}`;
    if (topbarBadge) topbarBadge.title = `Manual Location: ${currentFarmer.district}, ${currentFarmer.state}`;

    if (obStatus) {
      obStatus.innerHTML = `<strong>⚙️ Geolocation unavailable or denied.</strong> Using manually selected location: <em>${currentFarmer.district}, ${currentFarmer.state}</em>.`;
      obStatus.style.color = "#b45309";
    }

    if (dashDot) dashDot.className = 'dot-gps-manual';
    if (dashMode) {
      dashMode.className = 'indicator-pill pill-amber';
      dashMode.innerText = "Manual Location";
    }
    if (dashName) dashName.innerText = `${currentFarmer.district}, ${currentFarmer.state}`;
    if (dashCoords) dashCoords.innerText = `Coordinates: Manual Regional Fallback (${currentFarmer.lat?.toFixed(4) || '19.9975'}, ${currentFarmer.lon?.toFixed(4) || '73.7898'})`;
  }
}

// Real-Time Weather & Spraying Advisory Service
function fetchRealtimeWeather(lat, lon) {
  fetch(`/api/weather?lat=${lat}&lon=${lon}`)
    .then(res => res.json())
    .then(data => {
      const cur = data.current || {};
      const spray = data.spraying_advisory || {};
      const forecast = data.forecast_3day || [];

      // Topbar Pill
      const topIcon = document.getElementById('topbar-weather-icon');
      if (topIcon) topIcon.innerText = cur.icon || '☀️';
      const topTemp = document.getElementById('topbar-weather-temp');
      if (topTemp) topTemp.innerText = `${cur.temperature_c ?? '--'}°C`;

      // Dashboard Banner
      const dashIcon = document.getElementById('dash-weather-icon');
      if (dashIcon) dashIcon.innerText = cur.icon || '☀️';
      const dashTemp = document.getElementById('dash-weather-temp');
      if (dashTemp) dashTemp.innerText = `${cur.temperature_c ?? '--'}°C`;
      const dashDesc = document.getElementById('dash-weather-desc');
      if (dashDesc) dashDesc.innerText = `${cur.condition_text || 'Clear'} | Hum: ${cur.relative_humidity}%`;
      const dashSpray = document.getElementById('dash-spraying-status');
      if (dashSpray) {
        dashSpray.innerText = `${spray.status || 'FAVORABLE'}: ${spray.advisory || 'Good conditions'}`;
        dashSpray.style.color = spray.status === 'FAVORABLE' ? '#15803d' : (spray.status === 'UNFAVORABLE' ? '#b91c1c' : '#b45309');
      }

      // Weather View Details
      const vwIcon = document.getElementById('weather-view-icon');
      if (vwIcon) vwIcon.innerText = cur.icon || '☀️';
      const vwTemp = document.getElementById('weather-view-temp');
      if (vwTemp) vwTemp.innerText = `${cur.temperature_c ?? '--'}°C`;
      const vwDesc = document.getElementById('weather-view-desc');
      if (vwDesc) vwDesc.innerText = cur.condition_text || 'Clear Sky';
      const vwLoc = document.getElementById('weather-view-loc');
      if (vwLoc) vwLoc.innerText = `${currentFarmer.village ? currentFarmer.village + ', ' : ''}${currentFarmer.district}, ${currentFarmer.state} (${lat.toFixed(4)}, ${lon.toFixed(4)})`;
      
      const vwHum = document.getElementById('weather-view-humidity');
      if (vwHum) vwHum.innerText = `${cur.relative_humidity}%`;
      const vwWind = document.getElementById('weather-view-wind');
      if (vwWind) vwWind.innerText = `${cur.wind_speed_kmh} km/h`;
      const vwPrecip = document.getElementById('weather-view-precip');
      if (vwPrecip) vwPrecip.innerText = `${cur.precipitation_mm} mm`;

      const sprayPill = document.getElementById('weather-spray-pill');
      if (sprayPill) {
        sprayPill.innerText = spray.status || 'FAVORABLE';
        sprayPill.className = `indicator-pill ${spray.status === 'FAVORABLE' ? 'pill-green' : (spray.status === 'UNFAVORABLE' ? 'pill-red' : 'pill-amber')}`;
      }
      const sprayReason = document.getElementById('weather-spray-reason');
      if (sprayReason) sprayReason.innerText = spray.advisory || "";

      // 3-Day Forecast Cards
      const forecastGrid = document.getElementById('weather-forecast-cards');
      if (forecastGrid && forecast.length > 0) {
        forecastGrid.innerHTML = '';
        forecast.forEach(f => {
          const card = document.createElement('div');
          card.className = 'forecast-day-card';
          card.innerHTML = `
            <div style="font-weight: 700; font-size: 0.95rem; color: var(--text-main); margin-bottom: 4px;">${f.day || f.date}</div>
            <div style="font-size: 2.2rem; margin: 8px 0;">${f.icon || '☀️'}</div>
            <div style="font-size: 1.15rem; font-weight: 800; color: var(--primary-emerald);">${f.temp_max_c}° / ${f.temp_min_c}°C</div>
            <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;">${f.condition_text}</div>
            <div style="font-size: 0.8rem; margin-top: 6px; color: ${f.rain_probability_pct > 40 ? '#b91c1c' : '#15803d'}; font-weight: 600;">
              🌧️ Rain: ${f.rain_probability_pct}%
            </div>
            <div class="indicator-pill ${f.spraying_risk === 'Low Risk' ? 'pill-green' : 'pill-amber'}" style="font-size: 0.75rem; padding: 2px 8px; margin-top: 8px;">
              Spray: ${f.spraying_risk || 'Low Risk'}
            </div>
          `;
          forecastGrid.appendChild(card);
        });
      }
    })
    .catch(err => console.error("Weather fetch failed:", err));
}

// View Navigation Switcher
function switchView(viewId) {
  document.querySelectorAll('.view-container').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  
  const target = document.getElementById(viewId);
  if (target) target.classList.add('active');
  
  const activeNav = Array.from(document.querySelectorAll('.nav-item')).find(el => {
    return el.getAttribute('onclick') && el.getAttribute('onclick').includes(viewId);
  });
  if (activeNav) activeNav.classList.add('active');

  if (viewId === 'v-map') {
    setTimeout(initLeafletMap, 200);
  }
}

// Chat Drawer Toggle
function toggleChat(show) {
  const drawer = document.getElementById('chat-drawer');
  const floatBtn = document.getElementById('chat-float-btn');
  if (show) {
    if (drawer) drawer.classList.remove('collapsed');
    if (floatBtn) floatBtn.classList.add('hidden');
    const input = document.getElementById('chat-input');
    if (input) input.focus();
  } else {
    if (drawer) drawer.classList.add('collapsed');
    if (floatBtn) floatBtn.classList.remove('hidden');
  }
}

// Form Handlers
function handleOnboarding(e) {
  e.preventDefault();
  currentFarmer.name = document.getElementById('ob-name').value;
  currentFarmer.state = document.getElementById('ob-state').value;
  currentFarmer.district = document.getElementById('ob-district').value;
  currentFarmer.crop = document.getElementById('ob-crop').value;
  currentFarmer.acres = parseFloat(document.getElementById('ob-acres').value) || 3.0;
  
  fetch('/farmer/profile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: currentFarmer.name,
      state: currentFarmer.state,
      district: currentFarmer.district,
      village: currentFarmer.village,
      latitude: currentFarmer.lat || 19.9975,
      longitude: currentFarmer.lon || 73.7800,
      preferred_language: currentLanguage
    })
  })
  .then(res => res.json())
  .then(data => {
    alert(`Farmer Profile Saved for ${currentFarmer.name}! Farm dashboard updated.`);
    updateDashboardUI();
    loadNearbyMarkets();
    switchView('v-dashboard');
  })
  .catch(err => console.error("Onboarding error:", err));
}

function updateDashboardUI() {
  const cropEl = document.getElementById('dash-crop-acreage');
  if (cropEl) cropEl.innerText = `${currentFarmer.crop} (${currentFarmer.acres} Acres)`;
}

// Real Farm Assessment (Unified Decision Passport)
function assessFarmDecisions() {
  const payload = {
    farmer_name: currentFarmer.name,
    state: currentFarmer.state,
    district: currentFarmer.district,
    village: currentFarmer.village,
    latitude: currentFarmer.lat || 19.9975,
    longitude: currentFarmer.lon || 73.7800,
    crop: currentFarmer.crop,
    land_area_acres: currentFarmer.acres,
    expected_yield_quintals: currentFarmer.yield_q,
    money_invested_rs: currentFarmer.invested_rs,
    expected_additional_cost_rs: currentFarmer.additional_rs
  };

  fetch('/decision/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(res => res.json())
  .then(data => {
    // Populate Decision Passport
    const passCode = document.getElementById('pass-code');
    if (passCode) passCode.innerText = data.passport_code;
    
    const passFarmer = document.getElementById('pass-farmer');
    if (passFarmer) passFarmer.innerText = `${data.farmer_name} | ${data.crop} (${data.land_area_acres} Acres) | ${data.location}`;
    
    const passRec = document.getElementById('pass-recommendation');
    if (passRec) passRec.innerText = data.master_recommendation;
    
    const passTrust = document.getElementById('pass-trust');
    if (passTrust) passTrust.innerText = `${data.module_summaries.krishiproof.trust_score}/100 (${data.module_summaries.krishiproof.risk_level} RISK)`;
    
    const passInput = document.getElementById('pass-input');
    if (passInput) passInput.innerText = `₹${data.module_summaries.inputtruth.avoidable_cost_rs.toLocaleString()} AVOIDABLE`;
    
    const passMarket = document.getElementById('pass-market');
    if (passMarket) passMarket.innerText = data.module_summaries.marketshield.best_market;
    
    const passFc = document.getElementById('pass-forecast');
    if (passFc) passFc.innerText = `${data.module_summaries.price_forecast.direction} (${data.module_summaries.price_forecast.confidence})`;
    
    const passReason = document.getElementById('pass-reason');
    if (passReason) passReason.innerText = data.primary_reason;

    // Also update dashboard summary recommendation
    const dashAction = document.getElementById('dash-action');
    if (dashAction) dashAction.innerText = data.master_recommendation;
    const dashReason = document.getElementById('dash-action-reason');
    if (dashReason) dashReason.innerText = data.primary_reason;
    
    switchView('v-passport');
  })
  .catch(err => {
    console.error("Decision Assessment error:", err);
    switchView('v-passport');
  });
}

// 1. KrishiProof Advice Engine
function evaluateKrishiProof() {
  const rawText = document.getElementById('kp-text').value;
  fetch('/advice/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_text: rawText, crop: currentFarmer.crop, land_area_acres: currentFarmer.acres })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('kp-score').innerText = `${data.trust_score}/100`;
    document.getElementById('kp-risk-pill').innerText = `${data.risk_level} ADVICE RISK`;
    document.getElementById('kp-risk-pill').className = `indicator-pill ${data.risk_level === 'HIGH' ? 'pill-red' : 'pill-amber'}`;
    document.getElementById('kp-bias').innerText = `Commercial Bias: ${data.commercial_bias_risk}`;
    
    const ul = document.getElementById('kp-reasons');
    ul.innerHTML = '';
    data.reasons.forEach(r => {
      const li = document.createElement('li');
      li.innerText = r;
      ul.appendChild(li);
    });
  });
}

// 2. InputTruth Invoice Engine
function evaluateInputTruth() {
  const prod = document.getElementById('it-prod').value;
  const qty = parseFloat(document.getElementById('it-qty').value);
  const price = parseFloat(document.getElementById('it-price').value);

  fetch('/input/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      product_name: prod, purchased_quantity_kg: qty, unit_price_rs: price,
      crop: currentFarmer.crop, land_area_acres: currentFarmer.acres
    })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('it-avoidable').innerText = `₹${data.avoidable_expenditure_rs.toLocaleString()}`;
    document.getElementById('it-purchased-str').innerText = `${data.purchased_quantity_kg} kg`;
    document.getElementById('it-rec-str').innerText = `${data.recommended_quantity_kg} kg`;
    document.getElementById('it-excess-str').innerText = `${data.potential_excess_kg} kg`;
    document.getElementById('it-note').innerText = `"${data.assessment_note}"`;
  });
}

// 3. FarmExit Crop Economics Engine
function evaluateFarmExit() {
  const sunk = parseFloat(document.getElementById('fe-sunk').value);
  const rem = parseFloat(document.getElementById('fe-rem').value);
  const yld = parseFloat(document.getElementById('fe-yield').value);
  const pr = parseFloat(document.getElementById('fe-price').value);

  fetch('/crop/economics', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      money_invested_rs: sunk, expected_additional_cost_rs: rem,
      expected_yield_quintals: yld, current_price_rs_per_q: pr,
      forecast_price_rs_per_q: pr * 1.05
    })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('fe-rec').innerText = data.recommendation;
    document.getElementById('fe-be-total').innerText = `₹${data.break_even_price_total_rs}/q`;
    document.getElementById('fe-be-rem').innerText = `₹${data.break_even_price_remaining_rs}/q`;
    document.getElementById('fe-profit').innerText = `₹${data.expected_profit_rs.toLocaleString()}`;
    document.getElementById('fe-roi').innerText = `+${data.roi_percentage}%`;
  });
}

// 4. MarketShield APMC Net Realization Engine
function loadNearbyMarkets() {
  const lat = currentFarmer.lat || 19.9975;
  const lon = currentFarmer.lon || 73.7800;

  fetch('/markets/nearby', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      latitude: lat, longitude: lon,
      commodity: currentFarmer.crop, quantity_quintals: currentFarmer.yield_q
    })
  })
  .then(res => res.json())
  .then(data => {
    renderMarketTable(data.markets);
    updateDashboardMarketUI(data.best_market);
  })
  .catch(err => console.error("Market load error:", err));
}

function renderMarketTable(markets) {
  const tbody = document.getElementById('market-table-body');
  if (!tbody || !markets) return;
  tbody.innerHTML = '';
  
  markets.forEach((m, idx) => {
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid var(--border-color)';
    tr.innerHTML = `
      <td style="padding: 10px; font-weight: 700;">${m.name} ${idx === 0 ? '🏆 (BEST)' : ''}</td>
      <td>${m.distance_km} km</td>
      <td>₹${m.modal_price}/q</td>
      <td style="color: #b91c1c;">-₹${m.transport_cost_per_q}/q</td>
      <td style="color: #b91c1c;">-₹${m.other_costs_per_q}/q</td>
      <td style="font-weight: 800; color: #15803d; font-size: 1.05rem;">₹${m.net_realization_per_q}/q</td>
      <td><button class="btn-primary" style="padding: 4px 10px; font-size: 0.78rem;" onclick="selectMarket('${m.name}')">${t('ms.selectBtn')}</button></td>
    `;
    tbody.appendChild(tr);
  });
}

function selectMarket(marketName) {
  alert(`Selected ${marketName} as your primary destination market!`);
}

function updateDashboardMarketUI(bestMarket) {
  if (!bestMarket) return;
  const bmEl = document.getElementById('dash-best-market');
  if (bmEl) bmEl.innerText = bestMarket.name;
  const mdEl = document.getElementById('dash-market-details');
  if (mdEl) mdEl.innerHTML = `Gross Price: ₹${bestMarket.modal_price}/q | Transport (${bestMarket.distance_km}km): ₹${bestMarket.transport_cost_per_q}/q | Net Realization: <strong style="color:#15803d;">₹${bestMarket.net_realization_per_q}/q</strong>`;
}

// 5. APMC Geographic Map
function initLeafletMap() {
  const mapDiv = document.getElementById('map-container');
  if (!mapDiv) return;
  
  const lat = currentFarmer.lat || 19.9975;
  const lon = currentFarmer.lon || 73.7800;

  if (!leafletMap) {
    leafletMap = L.map('map-container').setView([lat, lon], 10);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '© OpenStreetMap contributors'
    }).addTo(leafletMap);
  } else {
    leafletMap.setView([lat, lon], 10);
    leafletMap.invalidateSize();
  }

  // Clear existing markers if any
  leafletMap.eachLayer((layer) => {
    if (layer instanceof L.Marker || layer instanceof L.CircleMarker) {
      leafletMap.removeLayer(layer);
    }
  });

  // Farmer's real or approximate location marker
  const farmerIconDesc = currentFarmer.is_live_location ? "📍 Live GPS Farm Location" : "📍 Farm Location (Manual)";
  L.marker([lat, lon])
    .addTo(leafletMap)
    .bindPopup(`<b>${farmerIconDesc}</b><br>${currentFarmer.name}<br>${currentFarmer.village ? currentFarmer.village + ', ' : ''}${currentFarmer.district}, ${currentFarmer.state}`)
    .openPopup();

  // Surrounding APMC Markets markers
  const apmcs = [
    { name: "Pimpalgaon Baswant APMC", lat: 20.1714, lon: 73.9876, gross: 2650, net: 2420 },
    { name: "Lasalgaon APMC", lat: 20.1472, lon: 74.2272, gross: 2720, net: 2410 },
    { name: "Nashik Main Market Yard", lat: 19.9975, lon: 73.7898, gross: 2540, net: 2400 }
  ];

  apmcs.forEach(m => {
    L.circleMarker([m.lat, m.lon], { color: '#15803d', radius: 10, fillOpacity: 0.85 })
      .addTo(leafletMap)
      .bindPopup(`<b>🟢 ${m.name}</b><br>Gross Price: ₹${m.gross}/q<br><b>Net Realization: ₹${m.net}/q</b>`);
  });
}

// 6. What-If Simulator
function runSimulation() {
  const arrPct = parseFloat(document.getElementById('sim-arr').value);
  const dropPct = parseFloat(document.getElementById('sim-drop').value);

  fetch('/scenario/simulate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ arrival_change_pct: arrPct, price_shock_pct: dropPct })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('sim-net-price').innerText = `₹${data.simulated_scenario.net_price_rs_per_q}/q`;
    document.getElementById('sim-profit-delta').innerText = `₹${data.simulated_scenario.profit_impact_rs.toLocaleString()}`;
    document.getElementById('sim-action').innerText = data.recommended_mitigation_action;
  });
}

// 7. Farm Memory
function loadFarmMemory() {
  fetch('/farm-memory/history')
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById('memory-cards');
    if (!container) return;
    container.innerHTML = '';
    data.memories.forEach(m => {
      const div = document.createElement('div');
      div.className = 'card';
      div.innerHTML = `
        <div class="card-title">${m.season} — ${m.crop}</div>
        <div class="indicator-pill pill-green" style="margin-bottom: 8px;">Decision: ${m.decision_taken}</div>
        <div style="font-size: 0.88rem; color: var(--text-muted); display: flex; flex-direction: column; gap: 4px;">
          <div>• Expected Price: ₹${m.expected_price}/q | Realized: <strong>₹${m.actual_realized_price}/q</strong></div>
          <div>• Realized Profit: <strong style="color: #15803d;">₹${m.profit_rs.toLocaleString()}</strong></div>
          <div style="margin-top: 6px; font-style: italic; background: rgba(0,0,0,0.02); padding: 8px; border-radius: 6px; border: 1px solid var(--border-color);">
            "Historical Learning: ${m.historical_learning}"
          </div>
        </div>
      `;
      container.appendChild(div);
    });
  });
}

// 8. ML Model Metrics
function loadModelMetrics() {
  fetch('/model/evaluation')
  .then(res => res.json())
  .then(data => {
    const accEl = document.getElementById('admin-acc');
    if (accEl) accEl.innerText = `${data.test_directional_accuracy_pct}%`;
    const maeEl = document.getElementById('admin-mae');
    if (maeEl) maeEl.innerText = `₹${data.test_mae_rs_per_q}/q`;
    const precEl = document.getElementById('admin-prec');
    if (precEl) precEl.innerText = `${data.test_precision} / ${data.test_recall}`;
  })
  .catch(err => console.error("Metrics load error:", err));
}

// 9. Multilingual Chatbot
function handleChatKeyDown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendChatMessage();
  }
}

function formatMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>');
}

function sendChatMessage() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;

  const chatBox = document.getElementById('chat-box');
  
  // User message bubble
  const userDiv = document.createElement('div');
  userDiv.className = 'chat-msg user';
  userDiv.innerText = msg;
  chatBox.appendChild(userDiv);

  input.value = '';
  chatBox.scrollTop = chatBox.scrollHeight;

  // Loading indicator bubble
  const loadingDiv = document.createElement('div');
  loadingDiv.className = 'chat-msg assistant';
  loadingDiv.id = 'chat-loading-msg';
  loadingDiv.innerHTML = t('chat.thinkingMsg');
  chatBox.appendChild(loadingDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  const payload = {
    message: msg,
    farmer_name: currentFarmer.name,
    crop: currentFarmer.crop,
    state: currentFarmer.state,
    district: currentFarmer.district,
    lat: currentFarmer.lat || 19.9975,
    lon: currentFarmer.lon || 73.7800,
    acres: currentFarmer.acres,
    yield_q: currentFarmer.yield_q,
    is_live_location: currentFarmer.is_live_location,
    language: currentLanguage
  };

  fetch('/ai/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(res => res.json())
  .then(data => {
    const loader = document.getElementById('chat-loading-msg');
    if (loader) loader.remove();

    const botDiv = document.createElement('div');
    botDiv.className = 'chat-msg assistant';
    botDiv.innerHTML = formatMarkdown(data.reply);
    chatBox.appendChild(botDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  })
  .catch(err => {
    const loader = document.getElementById('chat-loading-msg');
    if (loader) loader.remove();

    const errDiv = document.createElement('div');
    errDiv.className = 'chat-msg assistant';
    errDiv.innerHTML = t('chat.errorMsg');
    chatBox.appendChild(errDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  });
}
