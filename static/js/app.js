// AI Travel Planner — Frontend Application Logic
document.addEventListener("DOMContentLoaded", () => {
  // Global State
  let currentTrip = null;
  let savedTrips = [];
  let pendingDeleteTripId = null;

  // DOM Elements
  const themeToggleBtn = document.getElementById("theme-toggle-btn");
  const modelSelect = document.getElementById("model-select");
  const ollamaStatusBadge = document.getElementById("ollama-status-badge");
  const ollamaStatusText = document.getElementById("ollama-status-text");
  const dbStatusBadge = document.getElementById("db-status-badge");
  const dbStatusText = document.getElementById("db-status-text");
  
  // Navigation & Sidebar
  const toggleSidebarBtn = document.getElementById("toggle-sidebar-btn");
  const closeSidebarMobileBtn = document.getElementById("close-sidebar-mobile-btn");
  const sidebar = document.getElementById("sidebar");
  const sidebarOverlay = document.getElementById("sidebar-overlay");
  const savedTripsList = document.getElementById("saved-trips-list");
  const tripCountBadge = document.getElementById("trip-count-badge");
  const tripSearchInput = document.getElementById("trip-search-input");
  const newTripBtn = document.getElementById("new-trip-btn");
  const brandLogoBtn = document.getElementById("brand-logo-btn");

  // Input Section
  const tripInputContainer = document.getElementById("trip-input-container");
  const tabNaturalBtn = document.getElementById("tab-natural-btn");
  const tabBuilderBtn = document.getElementById("tab-builder-btn");
  const tabNaturalContent = document.getElementById("tab-natural-content");
  const tabBuilderContent = document.getElementById("tab-builder-content");
  const naturalPromptInput = document.getElementById("natural-prompt-input");
  const generatePlanBtn = document.getElementById("generate-plan-btn");
  const generationLoader = document.getElementById("generation-loader");
  const loaderStatusTitle = document.getElementById("loader-status-title");
  const loaderStatusSubtitle = document.getElementById("loader-status-subtitle");

  // Form elements
  const formDestination = document.getElementById("form-destination");
  const formOrigin = document.getElementById("form-origin");
  const formDuration = document.getElementById("form-duration");
  const formSeason = document.getElementById("form-season");
  const formSpecial = document.getElementById("form-special");
  let selectedBudget = "Moderate";
  let selectedStyle = "Culture & History";
  let selectedTravelers = "Solo";

  // Trip Display Elements
  const tripDisplayContainer = document.getElementById("trip-display-container");
  const tripTitle = document.getElementById("trip-title");
  const tripDestBadge = document.getElementById("trip-dest-badge");
  const tripDurationBadge = document.getElementById("trip-duration-badge");
  const tripBudgetBadge = document.getElementById("trip-budget-badge");
  const tripModelBadge = document.getElementById("trip-model-badge");
  const tripMetaInfo = document.getElementById("trip-meta-info");

  // Export buttons
  const copyPlanBtn = document.getElementById("copy-plan-btn");
  const downloadMdBtn = document.getElementById("download-md-btn");
  const printPlanBtn = document.getElementById("print-plan-btn");
  const scrollToChatBtn = document.getElementById("scroll-to-chat-btn");

  // Section tabs
  const sectionTabs = document.querySelectorAll(".section-tab");
  const sectionPanes = document.querySelectorAll(".section-pane");

  // Chat Elements
  const chatMessagesContainer = document.getElementById("chat-messages-container");
  const chatEmptyState = document.getElementById("chat-empty-state");
  const chatInput = document.getElementById("chat-input");
  const chatSendBtn = document.getElementById("chat-send-btn");

  // Delete modal
  const deleteModal = document.getElementById("delete-modal");
  const cancelDeleteBtn = document.getElementById("cancel-delete-btn");
  const confirmDeleteBtn = document.getElementById("confirm-delete-btn");

  // ---------------- THEME INITIALIZATION ----------------
  function initTheme() {
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark" || (!savedTheme && window.matchMedia("(prefers-color-scheme: dark)").matches)) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }

  themeToggleBtn.addEventListener("click", () => {
    const isDark = document.documentElement.classList.toggle("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");
    lucide.createIcons();
  });

  initTheme();

  // ---------------- HEALTH & MODEL CHECK ----------------
  async function checkSystemHealth() {
    try {
      const res = await fetch("/api/health");
      if (!res.ok) throw new Error("Health check failed");
      const data = await res.json();

      // Update Ollama status
      if (data.ollama_online) {
        ollamaStatusBadge.className = "flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/50 text-emerald-700 dark:text-emerald-300";
        ollamaStatusBadge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span><span class="font-medium">Ollama Online (${data.ollama_latency_ms}ms)</span>`;
      } else {
        ollamaStatusBadge.className = "flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/50 text-rose-700 dark:text-rose-300";
        ollamaStatusBadge.innerHTML = `<span class="w-2 h-2 rounded-full bg-rose-500"></span><span class="font-medium">Ollama Offline</span>`;
      }

      // Update Models Dropdown
      if (data.available_models && data.available_models.length > 0) {
        const currentVal = modelSelect.value;
        modelSelect.innerHTML = "";
        data.available_models.forEach(m => {
          const opt = document.createElement("option");
          opt.value = m;
          opt.textContent = m;
          if (m === currentVal || (!currentVal && m === data.selected_model)) {
            opt.selected = true;
          }
          modelSelect.appendChild(opt);
        });
      }

      // Update Database status
      if (data.database_online) {
        const isPg = data.database_type.includes("PostgreSQL");
        dbStatusBadge.className = isPg 
          ? "flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-800/50 text-blue-700 dark:text-blue-300"
          : "flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800/50 text-amber-700 dark:text-amber-300";
        dbStatusBadge.innerHTML = `<span class="w-2 h-2 rounded-full ${isPg ? 'bg-blue-500' : 'bg-amber-500'}"></span><span class="font-medium">${data.database_type} (${data.database_latency_ms}ms)</span>`;
      } else {
        dbStatusBadge.className = "flex items-center space-x-1.5 px-2.5 py-1.5 rounded-lg bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800/50 text-rose-700 dark:text-rose-300";
        dbStatusBadge.innerHTML = `<span class="w-2 h-2 rounded-full bg-rose-500"></span><span class="font-medium">DB Offline</span>`;
      }
    } catch (err) {
      console.warn("Health check error:", err);
    }
  }

  // Periodic health check every 20s
  checkSystemHealth();
  setInterval(checkSystemHealth, 20000);

  // ---------------- SIDEBAR & SAVED TRIPS ----------------
  function toggleSidebar(open) {
    if (open) {
      sidebar.classList.remove("-translate-x-full");
      sidebarOverlay.classList.remove("hidden");
    } else {
      sidebar.classList.add("-translate-x-full");
      sidebarOverlay.classList.add("hidden");
    }
  }

  toggleSidebarBtn.addEventListener("click", () => {
    const isClosed = sidebar.classList.contains("-translate-x-full");
    toggleSidebar(isClosed);
  });
  closeSidebarMobileBtn.addEventListener("click", () => toggleSidebar(false));
  sidebarOverlay.addEventListener("click", () => toggleSidebar(false));

  async function loadSavedTrips() {
    try {
      const res = await fetch("/api/trips");
      if (!res.ok) throw new Error("Could not load trips");
      savedTrips = await res.json();
      renderSavedTripsList(savedTrips);
    } catch (err) {
      savedTripsList.innerHTML = `<div class="text-center py-6 text-xs text-rose-500">Failed to load saved trips: ${err.message}</div>`;
    }
  }

  function renderSavedTripsList(trips) {
    tripCountBadge.textContent = trips.length;
    if (trips.length === 0) {
      savedTripsList.innerHTML = `
        <div class="text-center py-10 px-4 text-xs text-slate-400">
          <i data-lucide="map" class="w-8 h-8 mx-auto mb-2 opacity-40"></i>
          <p class="font-medium text-slate-500 dark:text-slate-400">No saved trips yet</p>
          <p class="text-[11px] mt-1 text-slate-400">Generate your first trip to save it in PostgreSQL.</p>
        </div>
      `;
      lucide.createIcons();
      return;
    }

    savedTripsList.innerHTML = trips.map(t => {
      const isSelected = currentTrip && currentTrip.id === t.id;
      const dateStr = t.created_at ? new Date(t.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : '';
      return `
        <div data-trip-id="${t.id}" class="trip-card group cursor-pointer p-3 rounded-xl border ${isSelected ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-950/40' : 'border-slate-200/80 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/50 hover:border-slate-300 dark:hover:border-slate-700'} transition-all flex items-start justify-between">
          <div class="flex-1 min-w-0 pr-2">
            <h4 class="font-bold text-xs text-slate-800 dark:text-slate-200 truncate group-hover:text-blue-600 dark:group-hover:text-blue-400">${escapeHtml(t.title)}</h4>
            <div class="flex items-center space-x-1.5 mt-1 text-[11px] text-slate-500 dark:text-slate-400">
              <span class="truncate">${escapeHtml(t.destination)}</span>
              <span>•</span>
              <span class="font-medium">${t.duration_days}d</span>
              ${dateStr ? `<span>•</span><span>${dateStr}</span>` : ''}
            </div>
          </div>
          <button data-delete-id="${t.id}" class="delete-trip-btn opacity-0 group-hover:opacity-100 p-1 rounded-md text-slate-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-all" title="Delete Trip">
            <i data-lucide="trash-2" class="w-3.5 h-3.5 pointer-events-none"></i>
          </button>
        </div>
      `;
    }).join("");

    lucide.createIcons();

    // Attach click listeners to cards
    savedTripsList.querySelectorAll(".trip-card").forEach(el => {
      el.addEventListener("click", (e) => {
        if (e.target.closest(".delete-trip-btn")) return;
        const id = el.getAttribute("data-trip-id");
        openTrip(id);
      });
    });

    // Attach click listeners to delete buttons
    savedTripsList.querySelectorAll(".delete-trip-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const id = btn.getAttribute("data-delete-id");
        promptDeleteTrip(id);
      });
    });
  }

  // Search filter
  tripSearchInput.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase().trim();
    if (!q) {
      renderSavedTripsList(savedTrips);
      return;
    }
    const filtered = savedTrips.filter(t => 
      t.title.toLowerCase().includes(q) || 
      t.destination.toLowerCase().includes(q)
    );
    renderSavedTripsList(filtered);
  });

  // ---------------- TABS: PLAIN ENGLISH VS BUILDER ----------------
  tabNaturalBtn.addEventListener("click", () => {
    tabNaturalBtn.className = "flex-1 py-3 px-4 text-xs sm:text-sm font-semibold flex items-center justify-center space-x-2 border-b-2 border-blue-600 text-blue-600 dark:text-blue-400 bg-blue-50/40 dark:bg-blue-950/20 transition-all";
    tabBuilderBtn.className = "flex-1 py-3 px-4 text-xs sm:text-sm font-semibold flex items-center justify-center space-x-2 border-b-2 border-transparent text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 transition-all";
    tabNaturalContent.classList.remove("hidden");
    tabBuilderContent.classList.add("hidden");
  });

  tabBuilderBtn.addEventListener("click", () => {
    tabBuilderBtn.className = "flex-1 py-3 px-4 text-xs sm:text-sm font-semibold flex items-center justify-center space-x-2 border-b-2 border-blue-600 text-blue-600 dark:text-blue-400 bg-blue-50/40 dark:bg-blue-950/20 transition-all";
    tabNaturalBtn.className = "flex-1 py-3 px-4 text-xs sm:text-sm font-semibold flex items-center justify-center space-x-2 border-b-2 border-transparent text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 transition-all";
    tabBuilderContent.classList.remove("hidden");
    tabNaturalContent.classList.add("hidden");
  });

  // Prompt chip click handler
  document.querySelectorAll(".prompt-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      naturalPromptInput.value = chip.textContent.trim().replace(/^[^\w\s]+/, "").trim();
      naturalPromptInput.focus();
    });
  });

  // Form options selectors
  document.querySelectorAll(".budget-option").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".budget-option").forEach(b => {
        b.className = "budget-option p-3 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 hover:border-blue-500 text-left transition-all";
      });
      btn.className = "budget-option active-option p-3 rounded-xl border-2 border-blue-600 bg-blue-50/50 dark:bg-blue-950/40 text-left transition-all";
      selectedBudget = btn.getAttribute("data-value");
    });
  });

  document.querySelectorAll(".style-option").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".style-option").forEach(b => {
        b.className = "style-option px-3 py-1.5 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 transition-all";
      });
      btn.className = "style-option active-pill px-3 py-1.5 rounded-full text-xs font-medium bg-blue-600 text-white transition-all";
      selectedStyle = btn.getAttribute("data-value");
    });
  });

  document.querySelectorAll(".traveler-option").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".traveler-option").forEach(b => {
        b.className = "traveler-option px-3 py-1.5 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 transition-all";
      });
      btn.className = "traveler-option active-pill px-3 py-1.5 rounded-full text-xs font-medium bg-blue-600 text-white transition-all";
      selectedTravelers = btn.getAttribute("data-value");
    });
  });

  // ---------------- GENERATE TRIP ----------------
  generatePlanBtn.addEventListener("click", async () => {
    const isNatural = !tabNaturalContent.classList.contains("hidden");
    const naturalPrompt = naturalPromptInput.value.trim();
    const destination = formDestination.value.trim();

    if (isNatural && !naturalPrompt) {
      showToast("Please describe your trip in plain English or switch to the Interactive Builder.", "warning");
      naturalPromptInput.focus();
      return;
    }

    if (!isNatural && !destination) {
      showToast("Please enter a destination in the builder form.", "warning");
      formDestination.focus();
      return;
    }

    const payload = {
      model: modelSelect.value
    };

    if (isNatural) {
      payload.prompt = naturalPrompt;
    } else {
      payload.destination = destination;
      payload.origin = formOrigin.value.trim() || undefined;
      payload.duration_days = parseInt(formDuration.value) || 4;
      payload.start_date = formSeason.value.trim() || undefined;
      payload.budget_tier = selectedBudget;
      payload.travel_style = selectedStyle;
      payload.travelers = selectedTravelers;
      payload.special_interests = formSpecial.value.trim() || undefined;
    }

    // Show Progress Loader
    generatePlanBtn.disabled = true;
    generationLoader.classList.remove("hidden");
    generationLoader.scrollIntoView({ behavior: "smooth" });

    // Step-by-step progress simulation
    const steps = [
      { title: "Consulting AI Concierge...", sub: "Generating flights, accommodation, and day-by-day plan via Ollama." },
      { title: "Analyzing Flight Routes & Hubs...", sub: "Finding best airports and transit options." },
      { title: "Selecting Neighborhoods & Stays...", sub: "Matching boutique hotels to your budget." },
      { title: "Pacing the Day-by-Day Itinerary...", sub: "Creating balanced morning, afternoon, and evening experiences." },
      { title: "Finalizing Budget & Saving to Database...", sub: "Persisting itinerary in PostgreSQL." }
    ];
    let stepIdx = 0;
    const progressInterval = setInterval(() => {
      stepIdx = (stepIdx + 1) % steps.length;
      loaderStatusTitle.textContent = steps[stepIdx].title;
      loaderStatusSubtitle.textContent = steps[stepIdx].sub;
    }, 4500);

    try {
      const res = await fetch("/api/trips/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      clearInterval(progressInterval);

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server returned ${res.status}`);
      }

      const trip = await res.json();
      currentTrip = trip;
      showToast("Trip plan generated and saved successfully!", "success");

      // Reload saved trips in sidebar
      await loadSavedTrips();

      // Render the trip
      displayTrip(trip);

    } catch (err) {
      clearInterval(progressInterval);
      showToast(`Generation failed: ${err.message}`, "error");
    } finally {
      generatePlanBtn.disabled = false;
      generationLoader.classList.add("hidden");
    }
  });

  // ---------------- OPEN & DISPLAY TRIP ----------------
  async function openTrip(tripId) {
    try {
      const res = await fetch(`/api/trips/${tripId}`);
      if (!res.ok) throw new Error("Could not retrieve trip details");
      const trip = await res.json();
      currentTrip = trip;
      displayTrip(trip);
      if (window.innerWidth < 1024) {
        toggleSidebar(false);
      }
    } catch (err) {
      showToast(`Error opening trip: ${err.message}`, "error");
    }
  }

  function displayTrip(trip) {
    // Hide input container, show display container
    tripInputContainer.classList.add("hidden");
    tripDisplayContainer.classList.remove("hidden");
    window.scrollTo({ top: 0, behavior: "smooth" });

    // Header info
    tripTitle.textContent = trip.title;
    tripDestBadge.textContent = trip.destination;
    tripDurationBadge.textContent = `${trip.duration_days} Days`;
    tripBudgetBadge.textContent = trip.budget_tier || "Moderate";
    tripModelBadge.textContent = trip.model_used;

    const dateStr = trip.created_at ? new Date(trip.created_at).toLocaleDateString() : "";
    tripMetaInfo.textContent = `Saved in PostgreSQL • Model: ${trip.model_used} ${dateStr ? `• Created: ${dateStr}` : ""}`;

    // 1. Overview
    const ov = trip.overview || {};
    document.getElementById("overview-summary").textContent = ov.summary || "Complete customized travel itinerary.";
    document.getElementById("overview-best-time").textContent = ov.best_time_to_visit || "Year-round";
    document.getElementById("overview-currency").textContent = ov.local_currency || "EUR (€)";
    document.getElementById("overview-language").textContent = ov.language || "English / Local";
    document.getElementById("overview-emergency").textContent = ov.emergency_number || "112";

    const highlightsList = document.getElementById("overview-highlights");
    const highlights = ov.highlights || [];
    highlightsList.innerHTML = highlights.map(h => `
      <li class="flex items-center space-x-2 bg-slate-50 dark:bg-slate-950 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800">
        <i data-lucide="check" class="w-4 h-4 text-emerald-500 shrink-0"></i>
        <span>${escapeHtml(h)}</span>
      </li>
    `).join("");

    // 2. Flights
    const fl = trip.flights || {};
    document.getElementById("flight-departure").textContent = fl.departure_airports || (trip.origin || "Major European hubs");
    document.getElementById("flight-arrival").textContent = fl.arrival_airports || `Nearest airport to ${trip.destination}`;
    document.getElementById("flight-duration").textContent = fl.flight_duration_approx || "Direct flight";
    document.getElementById("flight-cost").textContent = fl.estimated_cost_range || "Market rates";
    document.getElementById("flight-airlines").textContent = fl.recommended_airlines_options || "Major European airlines / Rail";
    document.getElementById("flight-airport-transit").textContent = fl.ground_transit_from_airport || "Express airport train or airport shuttle.";
    document.getElementById("flight-local-transit").textContent = fl.local_transit_tips || "Walking and local metro recommended.";

    // 3. Hotels
    const ht = trip.hotels || {};
    const neighborhoodsList = document.getElementById("hotels-neighborhoods-list");
    const areas = ht.recommended_areas || [];
    neighborhoodsList.innerHTML = areas.map(a => `
      <div class="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200/80 dark:border-slate-800 space-y-1.5">
        <div class="flex items-center justify-between">
          <h5 class="font-bold text-slate-800 dark:text-slate-200 text-sm">${escapeHtml(a.area_name)}</h5>
          <span class="text-[11px] px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 font-medium">${escapeHtml(a.vibe || "")}</span>
        </div>
        <p class="text-xs text-emerald-700 dark:text-emerald-400"><strong>Pros:</strong> ${escapeHtml(a.pros || "")}</p>
        <p class="text-xs text-slate-500 dark:text-slate-400"><strong>Cons:</strong> ${escapeHtml(a.cons || "")}</p>
      </div>
    `).join("");

    const suggestionsList = document.getElementById("hotels-suggestions-list");
    const suggestions = ht.suggestions || [];
    suggestionsList.innerHTML = suggestions.map(s => `
      <div class="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200/80 dark:border-slate-800 space-y-2">
        <div class="flex items-start justify-between">
          <div>
            <h5 class="font-bold text-slate-800 dark:text-slate-200 text-sm">${escapeHtml(s.name)}</h5>
            <span class="text-xs text-slate-500 dark:text-slate-400">${escapeHtml(s.area || "")}</span>
          </div>
          <span class="text-xs font-bold text-emerald-600 dark:text-emerald-400">${escapeHtml(s.approx_rate_per_night || "")}</span>
        </div>
        <p class="text-xs text-slate-600 dark:text-slate-300">${escapeHtml(s.why_recommended || "")}</p>
      </div>
    `).join("");

    document.getElementById("hotels-booking-advice").textContent = ht.booking_advice || "Reserve lodging 4-6 weeks in advance for best selection.";

    // 4. Weather
    const wt = trip.weather || {};
    document.getElementById("weather-vibe").textContent = wt.season_vibe || "Pleasant travel weather";
    document.getElementById("weather-temp").textContent = wt.temp_range_celsius || "18°C - 24°C";
    document.getElementById("weather-rain").textContent = wt.rain_likelihood || "Low";

    const packingList = document.getElementById("weather-packing-list");
    const packItems = wt.what_to_pack || ["Comfortable walking shoes", "Layered clothing", "Compact umbrella", "Universal adapter"];
    packingList.innerHTML = packItems.map(p => `
      <label class="flex items-center space-x-2 bg-slate-50 dark:bg-slate-950 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800 cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-900 transition-all">
        <input type="checkbox" class="rounded text-blue-600 focus:ring-blue-500 w-4 h-4 border-slate-300">
        <span class="text-xs text-slate-700 dark:text-slate-300">${escapeHtml(p)}</span>
      </label>
    `).join("");

    // 5. Itinerary Days
    const itinerary = trip.itinerary || [];
    document.getElementById("itinerary-days-count").textContent = `${itinerary.length} Days`;
    const timeline = document.getElementById("itinerary-timeline");
    timeline.innerHTML = itinerary.map(d => `
      <div class="relative pl-6 sm:pl-8 pb-6 border-l-2 border-blue-500/30 dark:border-blue-500/20 last:border-l-0 last:pb-0">
        <!-- Day Badge Indicator -->
        <div class="absolute -left-3.5 top-0 w-7 h-7 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center shadow-md shadow-blue-500/20">
          ${d.day_number}
        </div>
        
        <div class="bg-slate-50 dark:bg-slate-950 p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 space-y-4">
          <div class="flex items-center justify-between border-b border-slate-200/60 dark:border-slate-800/60 pb-3">
            <h4 class="font-bold text-base text-slate-900 dark:text-white">Day ${d.day_number}: ${escapeHtml(d.day_title)}</h4>
          </div>

          <!-- Morning / Afternoon / Evening Grid -->
          <div class="space-y-3 text-xs sm:text-sm">
            <div class="flex items-start space-x-2.5">
              <span class="px-2 py-0.5 rounded-md bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 font-semibold text-[11px] shrink-0 mt-0.5">🌅 Morning</span>
              <p class="text-slate-700 dark:text-slate-300 leading-relaxed">${escapeHtml(d.morning)}</p>
            </div>

            <div class="flex items-start space-x-2.5">
              <span class="px-2 py-0.5 rounded-md bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300 font-semibold text-[11px] shrink-0 mt-0.5">☀️ Afternoon</span>
              <p class="text-slate-700 dark:text-slate-300 leading-relaxed">${escapeHtml(d.afternoon)}</p>
            </div>

            <div class="flex items-start space-x-2.5">
              <span class="px-2 py-0.5 rounded-md bg-indigo-100 dark:bg-indigo-950/60 text-indigo-800 dark:text-indigo-300 font-semibold text-[11px] shrink-0 mt-0.5">🌙 Evening</span>
              <p class="text-slate-700 dark:text-slate-300 leading-relaxed">${escapeHtml(d.evening)}</p>
            </div>
          </div>

          <!-- Dining & Transit footer -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t border-slate-200/60 dark:border-slate-800/60 text-xs">
            ${d.dining_recommendation ? `
              <div class="flex items-center space-x-1.5 text-slate-600 dark:text-slate-400">
                <i data-lucide="utensils" class="w-3.5 h-3.5 text-rose-500 shrink-0"></i>
                <span><strong>Dining:</strong> ${escapeHtml(d.dining_recommendation)}</span>
              </div>
            ` : ''}
            ${d.transit_tips ? `
              <div class="flex items-center space-x-1.5 text-slate-600 dark:text-slate-400">
                <i data-lucide="footprints" class="w-3.5 h-3.5 text-blue-500 shrink-0"></i>
                <span><strong>Transit:</strong> ${escapeHtml(d.transit_tips)}</span>
              </div>
            ` : ''}
          </div>
        </div>
      </div>
    `).join("");

    // 6. Budget
    const bg = trip.budget || {};
    document.getElementById("budget-total").textContent = bg.estimated_total_range || "Estimated Cost Range";
    const bdCards = document.getElementById("budget-breakdown-cards");
    const breakdown = bg.breakdown || {};
    bdCards.innerHTML = Object.entries(breakdown).map(([k, v]) => `
      <div class="bg-slate-50 dark:bg-slate-950 p-3 rounded-xl border border-slate-200/80 dark:border-slate-800 text-center">
        <span class="text-slate-400 block text-[11px] mb-1 capitalize">${k.replace(/_/g, " ")}</span>
        <span class="font-bold text-slate-800 dark:text-slate-200 text-sm text-emerald-600 dark:text-emerald-400">${escapeHtml(String(v))}</span>
      </div>
    `).join("");

    const tipsList = document.getElementById("budget-tips-list");
    const tips = bg.money_saving_tips || [];
    tipsList.innerHTML = tips.map(t => `
      <li class="flex items-start space-x-2">
        <i data-lucide="check-circle" class="w-4 h-4 text-emerald-500 shrink-0 mt-0.5"></i>
        <span>${escapeHtml(t)}</span>
      </li>
    `).join("");

    // Render Chat Messages
    renderChatMessages(trip.messages || []);

    // Switch to Overview tab by default
    switchSection("section-overview");

    // Refresh lucide icons
    lucide.createIcons();

    // Re-highlight active trip in sidebar
    renderSavedTripsList(savedTrips);
  }

  // ---------------- SECTION TABS SWITCHER ----------------
  function switchSection(sectionId) {
    sectionTabs.forEach(tab => {
      if (tab.getAttribute("data-section") === sectionId) {
        tab.className = "section-tab active-tab pb-2 border-b-2 border-blue-600 text-blue-600 dark:text-blue-400 whitespace-nowrap flex items-center space-x-1.5 font-bold";
      } else {
        tab.className = "section-tab pb-2 border-b-2 border-transparent text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 whitespace-nowrap flex items-center space-x-1.5";
      }
    });

    sectionPanes.forEach(pane => {
      if (pane.id === sectionId) {
        pane.classList.remove("hidden");
      } else {
        pane.classList.add("hidden");
      }
    });
  }

  sectionTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetId = tab.getAttribute("data-section");
      switchSection(targetId);
    });
  });

  // ---------------- EXPORT ACTIONS: COPY, MARKDOWN, PRINT ----------------
  copyPlanBtn.addEventListener("click", () => {
    if (!currentTrip) return;
    const textToCopy = currentTrip.raw_markdown || `${currentTrip.title}\nDestination: ${currentTrip.destination}`;
    navigator.clipboard.writeText(textToCopy).then(() => {
      showToast("Trip plan copied to clipboard in clean Markdown!", "success");
    }).catch(() => {
      showToast("Could not access clipboard", "error");
    });
  });

  downloadMdBtn.addEventListener("click", () => {
    if (!currentTrip) return;
    window.location.href = `/api/trips/${currentTrip.id}/export/markdown`;
  });

  printPlanBtn.addEventListener("click", () => {
    // Show all sections momentarily for printing
    sectionPanes.forEach(p => p.classList.remove("hidden"));
    window.print();
    // Restore current active tab
    const activeTab = document.querySelector(".section-tab.active-tab");
    if (activeTab) {
      switchSection(activeTab.getAttribute("data-section"));
    }
  });

  scrollToChatBtn.addEventListener("click", () => {
    document.getElementById("chat-section").scrollIntoView({ behavior: "smooth" });
    chatInput.focus();
  });

  // ---------------- FOLLOW-UP QUESTIONS & CHAT ----------------
  function renderChatMessages(messages) {
    if (!messages || messages.length === 0) {
      chatEmptyState.classList.remove("hidden");
      chatMessagesContainer.innerHTML = "";
      return;
    }

    chatEmptyState.classList.add("hidden");
    chatMessagesContainer.innerHTML = messages.map(m => {
      const isUser = m.role === "user";
      const formattedContent = marked.parse(m.content);
      return `
        <div class="flex items-start space-x-2.5 ${isUser ? 'justify-end' : 'justify-start'}">
          ${!isUser ? `
            <div class="w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 text-xs">
              <i data-lucide="bot" class="w-4 h-4"></i>
            </div>
          ` : ''}
          <div class="max-w-[85%] rounded-2xl p-3 text-xs sm:text-sm ${isUser ? 'bg-blue-600 text-white rounded-br-none' : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-100 rounded-bl-none border border-slate-200 dark:border-slate-700/80'}">
            <div class="prose-chat">${formattedContent}</div>
          </div>
          ${isUser ? `
            <div class="w-7 h-7 rounded-full bg-slate-300 dark:bg-slate-700 text-slate-800 dark:text-slate-200 flex items-center justify-center shrink-0 text-xs">
              <i data-lucide="user" class="w-4 h-4"></i>
            </div>
          ` : ''}
        </div>
      `;
    }).join("");

    lucide.createIcons();
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
  }

  async function sendChatMessage(text) {
    if (!currentTrip || !text.trim()) return;

    chatInput.value = "";
    chatSendBtn.disabled = true;

    // Append optimistic user message
    const tempUserMsg = { role: "user", content: text };
    const currentMessages = currentTrip.messages || [];
    currentMessages.push(tempUserMsg);
    renderChatMessages(currentMessages);

    try {
      const res = await fetch(`/api/trips/${currentTrip.id}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          model: modelSelect.value
        })
      });

      if (!res.ok) throw new Error("Failed to get chat response");
      const data = await res.json();

      // Replace optimistic message and append assistant message
      currentTrip.messages = currentTrip.messages.filter(m => m !== tempUserMsg);
      currentTrip.messages.push(data.user_message);
      currentTrip.messages.push(data.assistant_message);
      renderChatMessages(currentTrip.messages);

    } catch (err) {
      showToast(`Chat error: ${err.message}`, "error");
    } finally {
      chatSendBtn.disabled = false;
    }
  }

  chatSendBtn.addEventListener("click", () => {
    sendChatMessage(chatInput.value);
  });

  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage(chatInput.value);
    }
  });

  // Quick prompt chips in chat
  document.querySelectorAll(".chat-quick-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const q = chip.textContent.trim().replace(/^[^\w\s]+/, "").trim();
      sendChatMessage(q);
    });
  });

  // ---------------- RESET / NEW TRIP ----------------
  function resetToNewTrip() {
    currentTrip = null;
    tripDisplayContainer.classList.add("hidden");
    tripInputContainer.classList.remove("hidden");
    naturalPromptInput.value = "";
    window.scrollTo({ top: 0, behavior: "smooth" });
    renderSavedTripsList(savedTrips);
  }

  newTripBtn.addEventListener("click", resetToNewTrip);
  brandLogoBtn.addEventListener("click", resetToNewTrip);

  // ---------------- DELETE TRIP ----------------
  function promptDeleteTrip(tripId) {
    pendingDeleteTripId = tripId;
    deleteModal.classList.remove("hidden");
  }

  cancelDeleteBtn.addEventListener("click", () => {
    pendingDeleteTripId = null;
    deleteModal.classList.add("hidden");
  });

  confirmDeleteBtn.addEventListener("click", async () => {
    if (!pendingDeleteTripId) return;
    try {
      const res = await fetch(`/api/trips/${pendingDeleteTripId}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Delete failed");

      showToast("Trip deleted from PostgreSQL", "info");

      if (currentTrip && currentTrip.id === pendingDeleteTripId) {
        resetToNewTrip();
      }

      await loadSavedTrips();
    } catch (err) {
      showToast(`Delete failed: ${err.message}`, "error");
    } finally {
      pendingDeleteTripId = null;
      deleteModal.classList.add("hidden");
    }
  });

  // ---------------- TOAST NOTIFICATIONS ----------------
  function showToast(message, type = "info") {
    const toastContainer = document.getElementById("toast-container");
    const toast = document.createElement("div");

    let bg = "bg-slate-900 dark:bg-white text-white dark:text-slate-900";
    let icon = "info";
    if (type === "success") {
      bg = "bg-emerald-600 text-white";
      icon = "check-circle";
    } else if (type === "warning") {
      bg = "bg-amber-600 text-white";
      icon = "alert-triangle";
    } else if (type === "error") {
      bg = "bg-rose-600 text-white";
      icon = "alert-octagon";
    }

    toast.className = `flex items-center space-x-2 px-4 py-2.5 rounded-xl shadow-lg text-xs font-semibold pointer-events-auto transition-all transform translate-y-2 opacity-0 duration-200 ${bg}`;
    toast.innerHTML = `<i data-lucide="${icon}" class="w-4 h-4 shrink-0"></i><span>${escapeHtml(message)}</span>`;

    toastContainer.appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
      toast.classList.remove("translate-y-2", "opacity-0");
    }, 10);

    setTimeout(() => {
      toast.classList.add("opacity-0", "translate-y-2");
      setTimeout(() => toast.remove(), 250);
    }, 4000);
  }

  // ---------------- UTILS ----------------
  function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  // Load saved trips on launch
  loadSavedTrips();
});
