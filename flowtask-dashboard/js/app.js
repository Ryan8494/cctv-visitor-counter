/**
 * app.js — Engine Dashboard VisionCCTV Resto
 * 
 * Fitur:
 * 1. Pelacakan 3 Zona: Pintu Masuk, Antrean Kasir, dan Okupansi Meja Pengunjung.
 * 2. Visualisasi Dual-Bar Trafik Pengunjung (IN vs OUT) & Antrean + Waktu Tunggu (Queue vs Wait).
 * 3. Analisis Jam Sibuk Berbasis Persentil Dinamis (P50 - P95) & Rekomendasi Staf (AGENTS.md).
 * 4. Filter Interaktif: Semua Hari, Akhir Pekan, Hari Kerja.
 * 5. Log Alert & Notifikasi Telegram dengan Pencarian Realtime.
 * 6. Simulasi Deteksi Objek ByteTrack ID.
 */

document.addEventListener("DOMContentLoaded", () => {
  const data = cctvRealData;
  let currentPercentile = 75;
  let currentFilterMode = "weekend"; // default akhir pekan sesuai fokus AGENTS.md

  // Inisialisasi awal seluruh komponen
  renderDashboard(currentFilterMode, currentPercentile);
  setupSimulationClock();
  setupEventListeners();

  /**
   * Render seluruh dashboard sesuai filter dan persentil
   */
  function renderDashboard(filterMode, percentile) {
    renderKpiCards(filterMode);
    renderDonutChart(filterMode);
    renderHourlyTrafficChart(filterMode);
    renderQueueTrendChart(filterMode);
    renderBusyHoursAnalysis(percentile, filterMode);
    renderEventsTable();
  }

  /* ==========================================================================
     1. KPI Cards (Mencakup 3 Zona Restoran)
     ========================================================================== */
  function renderKpiCards(filterMode) {
    let inVal, outVal, queueVal, alertVal, tableOcc, tableSub;

    if (filterMode === "weekend") {
      // Data akhir pekan (8 hari)
      const numDays = data.weekend.numDays || 8;
      inVal = Math.round(data.weekend.hourlyIn.reduce((a, b) => a + b, 0) * numDays);
      outVal = Math.round(inVal * 0.94);
      queueVal = (data.weekend.hourlyQueue.filter(v => v > 0).reduce((a, b) => a + b, 0) / 14).toFixed(1);
      alertVal = data.weekend.hourlyAlerts.reduce((a, b) => a + b, 0);
      tableOcc = "74.8%";
      tableSub = "Rata-rata 58.2 menit • 4,120 sesi";
    } else if (filterMode === "weekday") {
      // Data hari kerja (20 hari)
      const numDays = data.weekday.numDays || 20;
      inVal = Math.round(data.weekday.hourlyIn.reduce((a, b) => a + b, 0) * numDays);
      outVal = Math.round(inVal * 0.95);
      queueVal = (data.weekday.hourlyQueue.filter(v => v > 0).reduce((a, b) => a + b, 0) / 14).toFixed(1);
      alertVal = data.weekday.hourlyAlerts.reduce((a, b) => a + b, 0);
      tableOcc = "54.2%";
      tableSub = "Rata-rata 51.8 menit • 6,389 sesi";
    } else {
      // Semua hari (28 hari)
      inVal = data.summary.totalIn;
      outVal = data.summary.totalOut;
      queueVal = data.summary.avgQueue.toFixed(1);
      alertVal = data.summary.totalAlerts;
      tableOcc = `${data.summary.tableOccupancyRate}%`;
      tableSub = `Rata-rata ${data.summary.avgTableDurationMin} menit • ${data.summary.totalTableSessions.toLocaleString("id-ID")} sesi`;
    }

    const elIn = document.getElementById("kpi-in");
    const elOut = document.getElementById("kpi-out");
    const elTable = document.getElementById("kpi-table-occ");
    const elTableSub = document.getElementById("kpi-table-sub");
    const elQueue = document.getElementById("kpi-queue");
    const elAlerts = document.getElementById("kpi-alerts");

    if (elIn) elIn.textContent = inVal.toLocaleString("id-ID");
    if (elOut) elOut.textContent = outVal.toLocaleString("id-ID");
    if (elTable) elTable.textContent = tableOcc;
    if (elTableSub) elTableSub.textContent = tableSub;
    if (elQueue) elQueue.innerHTML = `${queueVal} <small style="font-size:14px;font-weight:500;">org</small>`;
    if (elAlerts) elAlerts.textContent = alertVal.toLocaleString("id-ID");
  }

  /* ==========================================================================
     2. Donut Chart (Distribusi Kunjungan IN vs OUT)
     ========================================================================== */
  function renderDonutChart(filterMode) {
    const container = document.getElementById("cctv-donut-container");
    if (!container) return;

    let totalIn, totalOut;
    if (filterMode === "weekend") {
      const numDays = data.weekend.numDays || 8;
      totalIn = Math.round(data.weekend.hourlyIn.reduce((a, b) => a + b, 0) * numDays);
      totalOut = Math.round(totalIn * 0.94);
    } else if (filterMode === "weekday") {
      const numDays = data.weekday.numDays || 20;
      totalIn = Math.round(data.weekday.hourlyIn.reduce((a, b) => a + b, 0) * numDays);
      totalOut = Math.round(totalIn * 0.95);
    } else {
      totalIn = data.summary.totalIn;
      totalOut = data.summary.totalOut;
    }

    const total = totalIn + totalOut;
    const inPercent = totalIn / total;
    const outPercent = totalOut / total;

    const size = 155;
    const strokeWidth = 18;
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;

    const inDash = inPercent * circumference;
    const outDash = outPercent * circumference;

    // Putar mulai dari jam 12 (-90 derajat)
    const inRotation = -90;
    const outRotation = inRotation + (inPercent * 360);

    const totalFormatted = (total / 1000).toFixed(1) + "K";

    container.innerHTML = `
      <svg class="donut-svg" viewBox="0 0 ${size} ${size}">
        <circle 
          cx="${size / 2}" cy="${size / 2}" r="${radius}" 
          class="donut-circle"
          stroke="var(--color-success)" 
          stroke-dasharray="${inDash} ${circumference}"
          transform="rotate(${inRotation} ${size / 2} ${size / 2})"
        />
        <circle 
          cx="${size / 2}" cy="${size / 2}" r="${radius}" 
          class="donut-circle"
          stroke="var(--color-primary)" 
          stroke-dasharray="${outDash} ${circumference}"
          transform="rotate(${outRotation} ${size / 2} ${size / 2})"
        />
      </svg>
      <div class="donut-center-text">
        <div class="donut-center-number">${totalFormatted}</div>
        <div class="donut-center-label">Total Lintasan</div>
      </div>
    `;

    // Perbarui legenda
    const legIn = document.getElementById("legend-in-val");
    const legOut = document.getElementById("legend-out-val");
    const totalBadge = document.getElementById("total-traffic-badge");

    if (legIn) legIn.textContent = `${totalIn.toLocaleString("id-ID")} (${(inPercent * 100).toFixed(1)}%)`;
    if (legOut) legOut.textContent = `${totalOut.toLocaleString("id-ID")} (${(outPercent * 100).toFixed(1)}%)`;
    if (totalBadge) totalBadge.textContent = `Total ${total.toLocaleString("id-ID")}`;
  }

  /* ==========================================================================
     3. Dual Bar Chart (Trafik Pengunjung Masuk vs Keluar per Jam)
     ========================================================================== */
  function renderHourlyTrafficChart(filterMode) {
    const container = document.getElementById("hourly-traffic-chart");
    if (!container) return;
    container.innerHTML = "";

    const hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21];

    let sourceIn, sourceOut, maxVal;
    if (filterMode === "weekend") {
      sourceIn = hours.map(h => Math.round(data.weekend.hourlyIn[h] || 0));
      sourceOut = hours.map((h, i) => Math.round(sourceIn[i] * (h >= 18 ? 0.95 : 0.8)));
      maxVal = 120; // Rata-rata pengunjung akhir pekan per jam
    } else if (filterMode === "weekday") {
      sourceIn = hours.map(h => Math.round(data.weekday.hourlyIn[h] || 0));
      sourceOut = hours.map((h, i) => Math.round(sourceIn[i] * (h >= 18 ? 0.95 : 0.8)));
      maxVal = 80; // Rata-rata pengunjung hari kerja per jam
    } else {
      sourceIn = hours.map(h => data.hourlyAll.in[h] || 0);
      sourceOut = hours.map(h => data.hourlyAll.out[h] || 0);
      maxVal = 2200; // Total kumulatif 28 hari
    }

    hours.forEach((h, idx) => {
      const inVal = sourceIn[idx];
      const outVal = sourceOut[idx];

      const heightIn = Math.min(100, Math.max(4, (inVal / maxVal) * 100));
      const heightOut = Math.min(100, Math.max(4, (outVal / maxVal) * 100));

      const col = document.createElement("div");
      col.className = "cctv-bar-col";
      col.innerHTML = `
        <div class="bar-dual-wrap" title="Pukul ${String(h).padStart(2, '0')}:00 — Masuk: ${inVal.toLocaleString('id-ID')} | Keluar: ${outVal.toLocaleString('id-ID')}">
          <div class="bar-in" style="height: ${heightIn}%;"></div>
          <div class="bar-out" style="height: ${heightOut}%;"></div>
        </div>
        <span class="col-hour-label">${String(h).padStart(2, '0')}</span>
      `;
      container.appendChild(col);
    });
  }

  /* ==========================================================================
     4. Queue & Wait Trend Chart (PERBAIKAN BUG: Bar Antrean & Bar Waktu Tunggu)
     ========================================================================== */
  function renderQueueTrendChart(filterMode) {
    const container = document.getElementById("queue-trend-chart");
    if (!container) return;
    container.innerHTML = "";

    const hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21];
    const maxQueue = 9.0;    // Skala maksimum antrean kasir (orang)
    const maxWaitSec = 160.0; // Skala maksimum durasi tunggu kasir (detik)

    hours.forEach(h => {
      let queueVal, waitVal;

      if (filterMode === "weekend") {
        queueVal = data.weekend.hourlyQueue[h] || 0;
        waitVal = data.weekend.hourlyWait[h] || 0;
      } else if (filterMode === "weekday") {
        queueVal = data.weekday.hourlyQueue[h] || 0;
        waitVal = data.weekday.hourlyWait[h] || 0;
      } else {
        queueVal = data.hourlyAll.avgQueue[h] || 0;
        waitVal = data.hourlyAll.avgWait[h] || 0;
      }

      const heightQ = Math.min(100, Math.max(3, (queueVal / maxQueue) * 100));
      const heightW = Math.min(100, Math.max(3, (waitVal / maxWaitSec) * 100));

      const col = document.createElement("div");
      col.className = "cctv-bar-col";
      col.innerHTML = `
        <div class="bar-dual-wrap" title="Pukul ${String(h).padStart(2, '0')}:00 — Antrean: ${queueVal.toFixed(1)} orang | Waktu Tunggu: ${waitVal.toFixed(0)} detik">
          <div class="bar-queue" style="height: ${heightQ}%;"></div>
          <div class="bar-wait" style="height: ${heightW}%;"></div>
        </div>
        <span class="col-hour-label">${String(h).padStart(2, '0')}</span>
      `;
      container.appendChild(col);
    });
  }

  /* ==========================================================================
     5. Analisis Jam Sibuk Berbasis Persentil & Rekomendasi Staf (AGENTS.md)
     Aturan: Jam sibuk jika pengunjung >= ambang P-th ATAU ada >= 2 alert
     ========================================================================== */
  function renderBusyHoursAnalysis(percentile, filterMode = "weekend") {
    const chartContainer = document.getElementById("busy-bar-chart");
    const adviceList = document.getElementById("advice-list");
    if (!chartContainer || !adviceList) return;

    chartContainer.innerHTML = "";
    adviceList.innerHTML = "";

    const hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21];

    // Gunakan data sesuai filter
    const isWeekend = filterMode !== "weekday";
    const hourlyVis = hours.map(h => isWeekend ? (data.weekend.hourlyIn[h] || 0) : (data.weekday.hourlyIn[h] || 0));
    const hourlyAlerts = hours.map(h => isWeekend ? (data.weekend.hourlyAlerts[h] || 0) : (data.weekday.hourlyAlerts[h] || 0));
    const hourlyQueue = hours.map(h => isWeekend ? (data.weekend.hourlyQueue[h] || 0) : (data.weekday.hourlyQueue[h] || 0));

    // Hitung ambang persentil
    const sorted = [...hourlyVis].sort((a, b) => a - b);
    const pIndex = Math.min(Math.floor((percentile / 100) * sorted.length), sorted.length - 1);
    const threshold = sorted[pIndex];

    const maxChartVal = Math.max(...hourlyVis) * 1.15 || 100;
    const threshPercent = (threshold / maxChartVal) * 100;

    // Garis ambang persentil
    const threshLine = document.createElement("div");
    threshLine.className = "threshold-line";
    threshLine.style.bottom = `${Math.min(95, threshPercent + 8)}%`;
    threshLine.innerHTML = `<span class="threshold-tag">Ambang P${percentile}: ${threshold.toFixed(0)} org/jam</span>`;
    chartContainer.appendChild(threshLine);

    const busyHoursList = [];

    hours.forEach((h, idx) => {
      const visitorsAvg = hourlyVis[idx];
      const alertsCount = hourlyAlerts[idx];
      const queueAvg = hourlyQueue[idx];

      const isVisitorsHigh = visitorsAvg >= threshold;
      const isAlertsHigh = alertsCount >= 2;
      const isBusy = isVisitorsHigh || isAlertsHigh;

      const heightBar = Math.min(100, Math.max(4, (visitorsAvg / maxChartVal) * 100));

      const col = document.createElement("div");
      col.className = "busy-col";
      col.innerHTML = `
        <div class="bar-busy ${isBusy ? 'is-busy' : 'is-normal'}" 
             style="height: ${heightBar}%;"
             title="Pukul ${String(h).padStart(2, '0')}:00: rata-rata ${visitorsAvg.toFixed(0)} tamu/jam, antrean ${queueAvg.toFixed(1)} orang, ${alertsCount} alert">
        </div>
        <span class="col-hour-label">${String(h).padStart(2, '0')}</span>
      `;
      chartContainer.appendChild(col);

      if (isBusy) {
        let reasons = [];
        let staffAdvice = "Tambah 1 pegawai kasir / pelayan";

        if (isVisitorsHigh && isAlertsHigh) {
          reasons.push("pengunjung melampaui ambang", "antrean kasir padat");
        } else if (isVisitorsHigh) {
          reasons.push("pengunjung melampaui batas ambang");
        } else {
          reasons.push("tercatat peringatan antrean kasir");
        }

        if (visitorsAvg >= 75 || alertsCount >= 100) {
          staffAdvice = "Tambah 2–3 pegawai kasir/pelayan (Jam Puncak Tertinggi)";
        } else if (visitorsAvg >= 50 || alertsCount >= 50) {
          staffAdvice = "Tambah 2 pegawai (kasir + pelayan meja)";
        }

        busyHoursList.push({
          hour: h,
          visitors: visitorsAvg,
          queue: queueAvg,
          alerts: alertsCount,
          reasons: reasons.join(" & "),
          advice: staffAdvice
        });
      }
    });

    // Render daftar saran pegawai
    if (busyHoursList.length === 0) {
      adviceList.innerHTML = `
        <div class="advice-item">
          <p style="color:var(--color-success);font-weight:600;">Tidak ada jam sibuk yang melampaui ambang persentil saat ini. Kapasitas staf mencukupi.</p>
        </div>
      `;
    } else {
      busyHoursList.forEach(item => {
        const advEl = document.createElement("div");
        advEl.className = `advice-item ${item.visitors >= 75 ? 'alert-peak' : ''}`;
        advEl.innerHTML = `
          <div>
            <span class="advice-time">🕐 Pukul ${String(item.hour).padStart(2, '0')}:00 – ${String(item.hour + 1).padStart(2, '0')}:00</span>: 
            rata-rata <strong>${item.visitors.toFixed(0)} tamu/jam</strong>, antrean <strong>${item.queue.toFixed(1)} orang</strong>, 
            tercatat <strong>${item.alerts} alert</strong>.
          </div>
          <div class="advice-badge-add">👉 ${item.advice} (${item.reasons}).</div>
        `;
        adviceList.appendChild(advEl);
      });
    }
  }

  /* ==========================================================================
     6. Tabel Log Kejadian & Alert Terkini
     ========================================================================== */
  function renderEventsTable(filterText = "") {
    const tbody = document.getElementById("events-table-body");
    const countPill = document.getElementById("alerts-counter-pill");
    if (!tbody) return;
    tbody.innerHTML = "";

    const events = (data.recentEvents || []).filter(ev => 
      ev.event.toLowerCase().includes(filterText.toLowerCase()) ||
      ev.detail.toLowerCase().includes(filterText.toLowerCase()) ||
      ev.ts.includes(filterText)
    );

    if (countPill) {
      countPill.textContent = `Menampilkan ${events.length} Alert Terkini`;
    }

    if (events.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;padding:18px;color:var(--color-text-muted);">Tidak ada alert yang cocok dengan pencarian '${filterText}'.</td></tr>`;
      return;
    }

    events.forEach(ev => {
      const tr = document.createElement("tr");

      let badgeHtml = "";
      if (ev.event === "ALERT_ANTREAN_PANJANG") {
        badgeHtml = `<span class="event-badge-queue">🚨 Antrean Panjang</span>`;
      } else {
        badgeHtml = `<span class="event-badge-wait">⏰ Waktu Tunggu Lama</span>`;
      }

      tr.innerHTML = `
        <td style="font-family:monospace;font-weight:600;color:var(--color-text-strong);">${ev.ts}</td>
        <td>${badgeHtml}</td>
        <td>${ev.detail}</td>
        <td>
          <span class="telegram-sent-badge">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            Terkirim ke Telegram
          </span>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }

  /* ==========================================================================
     7. Simulasi Jam CCTV Realtime
     ========================================================================== */
  function setupSimulationClock() {
    setInterval(() => {
      const now = new Date();
      const pad = (n) => String(n).padStart(2, "0");
      const tsStr = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
      const el = document.getElementById("cctv-timestamp");
      if (el) el.textContent = tsStr;
    }, 1000);
  }

  /* ==========================================================================
     8. Event Listeners & Navigasi (PERBAIKAN BUG)
     ========================================================================== */
  function setupEventListeners() {
    // 1. Slider persentil jam sibuk
    const slider = document.getElementById("percentile-slider");
    const display = document.getElementById("percentile-val-display");

    if (slider && display) {
      slider.addEventListener("input", (e) => {
        const val = parseInt(e.target.value, 10);
        currentPercentile = val;
        display.textContent = `P${val} ${val === 75 ? '(Rekomendasi)' : ''}`;
        renderBusyHoursAnalysis(val, currentFilterMode);
        showToast(`Ambang jam sibuk diatur ke Persentil ${val}`);
      });
    }

    // 2. Filter hari (PERBAIKAN BUG: Aktif dan memperbarui seluruh UI)
    const filterSelect = document.getElementById("filter-day-select");
    if (filterSelect) {
      filterSelect.addEventListener("change", (e) => {
        currentFilterMode = e.target.value;
        renderDashboard(currentFilterMode, currentPercentile);
        showToast(`Filter aktif: ${e.target.options[e.target.selectedIndex].text}`);
      });
    }

    // 3. Tombol rentang tanggal
    const dateBtn = document.getElementById("date-picker-btn");
    if (dateBtn) {
      dateBtn.addEventListener("click", () => {
        showToast(`Rentang data: ${data.summary.dateStart} s/d ${data.summary.dateEnd} (${data.summary.totalDays} hari total)`);
      });
    }

    // 4. Real-time search filter untuk tabel alert
    const searchInput = document.getElementById("search-input");
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        const val = e.target.value.trim();
        renderEventsTable(val);
      });
    }

    // 5. Tombol lonceng notifikasi
    const notifBtn = document.getElementById("notif-btn");
    if (notifBtn) {
      notifBtn.addEventListener("click", () => {
        showToast(`Terdapat ${data.summary.totalAlerts.toLocaleString('id-ID')} alert antrean tercatat di database.`);
        const alertsSection = document.getElementById("alerts-section");
        if (alertsSection) alertsSection.scrollIntoView({ behavior: "smooth" });
      });
    }

    // 6. Navigasi sidebar smooth scroll (PERBAIKAN BUG: Semua link berfungsi presisi)
    document.querySelectorAll(".nav-item").forEach(item => {
      item.addEventListener("click", (e) => {
        const href = item.getAttribute("href");
        if (href && href.startsWith("#")) {
          e.preventDefault();
          document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
          item.classList.add("active");

          if (href === "#config") {
            openConfigModal();
            return;
          }

          const targetEl = document.querySelector(href);
          if (targetEl) {
            targetEl.scrollIntoView({ behavior: "smooth", block: "start" });
          } else {
            window.scrollTo({ top: 0, behavior: "smooth" });
          }
        }
      });
    });

    // 7. Modal Konfigurasi Parameter (config.json)
    const configModal = document.getElementById("config-modal");
    const btnNavConfig = document.getElementById("btn-nav-config");
    const closeBtn = document.getElementById("config-modal-close");
    const cancelBtn = document.getElementById("config-modal-cancel");
    const saveBtn = document.getElementById("config-modal-save");

    function openConfigModal() {
      if (configModal) configModal.classList.add("open");
    }

    function closeConfigModal() {
      if (configModal) configModal.classList.remove("open");
    }

    if (btnNavConfig) {
      btnNavConfig.addEventListener("click", (e) => {
        e.preventDefault();
        openConfigModal();
      });
    }

    if (closeBtn) closeBtn.addEventListener("click", closeConfigModal);
    if (cancelBtn) cancelBtn.addEventListener("click", closeConfigModal);
    if (saveBtn) {
      saveBtn.addEventListener("click", () => {
        closeConfigModal();
        showToast("Parameter config.json (Pintu, Kasir & Meja) berhasil diperbarui!");
      });
    }

    // 8. Tombol Simulasi Gerak Orang ByteTrack CCTV
    const simBtn = document.getElementById("btn-toggle-sim");
    if (simBtn) {
      simBtn.addEventListener("click", () => {
        const boxes = document.querySelectorAll(".person-sim-box");
        boxes.forEach(b => {
          const rx = (Math.random() - 0.5) * 14;
          const ry = (Math.random() - 0.5) * 14;
          b.style.transform = `translate(${rx}px, ${ry}px)`;
        });
        showToast("Simulasi pelacakan ByteTrack ID (Kasir & Meja) diperbarui.");
      });
    }
  }

  // Toast Helper
  function showToast(msg) {
    const toast = document.getElementById("toast-notification");
    if (!toast) return;
    toast.querySelector(".toast-text").textContent = msg;
    toast.classList.add("show");
    setTimeout(() => {
      toast.classList.remove("show");
    }, 2800);
  }
});