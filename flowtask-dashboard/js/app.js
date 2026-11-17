/**
 * app.js — Engine Dashboard VisionCCTV
 * Merender metrik riil SQLite, SVG Charts, Analisis Jam Sibuk,
 * Simulasi Deteksi Garis & Antrean, dan Filter Persentil.
 */

document.addEventListener("DOMContentLoaded", () => {
  const data = cctvRealData;
  let currentPercentile = 75;
  let simInterval = null;

  // Inisialisasi semua komponen
  renderKpiCards();
  renderDonutChart();
  renderHourlyTrafficChart();
  renderQueueTrendChart();
  renderBusyHoursAnalysis(currentPercentile);
  renderEventsTable();
  setupSimulationClock();
  setupEventListeners();

  /* ==========================================================================
     1. KPI Cards
     ========================================================================== */
  function renderKpiCards() {
    document.getElementById("kpi-in").textContent = data.summary.totalIn.toLocaleString("id-ID");
    document.getElementById("kpi-out").textContent = data.summary.totalOut.toLocaleString("id-ID");
    document.getElementById("kpi-occupancy").textContent = `+${data.summary.currentOccupancy.toLocaleString("id-ID")} orang di dalam`;
    document.getElementById("kpi-queue").innerHTML = `${data.summary.avgQueue} <small style="font-size:14px;font-weight:500;">orang</small>`;
    document.getElementById("kpi-alerts").textContent = data.summary.totalAlerts.toLocaleString("id-ID");
  }

  /* ==========================================================================
     2. Donut Chart (Distribusi Kunjungan IN vs OUT)
     ========================================================================== */
  function renderDonutChart() {
    const container = document.getElementById("cctv-donut-container");
    const total = data.summary.totalIn + data.summary.totalOut;
    const inPercent = data.summary.totalIn / total;
    const outPercent = data.summary.totalOut / total;

    const size = 155;
    const strokeWidth = 18;
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;

    const inDash = inPercent * circumference;
    const outDash = outPercent * circumference;
    const inRotation = 0;
    const outRotation = inPercent * 360;

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
        <div class="donut-center-number">28.6K</div>
        <div class="donut-center-label">Total Lintasan</div>
      </div>
    `;
  }

  /* ==========================================================================
     3. Dual Bar Chart (Trafik Pengunjung Masuk vs Keluar per Jam)
     ========================================================================== */
  function renderHourlyTrafficChart() {
    const container = document.getElementById("hourly-traffic-chart");
    container.innerHTML = "";

    // Jam operasional restoran: 08:00 sampai 21:00
    const hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21];
    const maxVal = 2000; // Skala maksimum

    hours.forEach(h => {
      const inVal = data.hourlyAll.in[h] || 0;
      const outVal = data.hourlyAll.out[h] || 0;

      const heightIn = (inVal / maxVal) * 100;
      const heightOut = (outVal / maxVal) * 100;

      const col = document.createElement("div");
      col.className = "cctv-bar-col";
      col.innerHTML = `
        <div class="bar-dual-wrap" title="Pukul ${String(h).padStart(2, '0')}:00 — Masuk: ${inVal.toLocaleString()} | Keluar: ${outVal.toLocaleString()}">
          <div class="bar-in" style="height: ${heightIn}%;"></div>
          <div class="bar-out" style="height: ${heightOut}%;"></div>
        </div>
        <span class="col-hour-label">${String(h).padStart(2, '0')}</span>
      `;
      container.appendChild(col);
    });
  }

  /* ==========================================================================
     4. Queue Trend Chart (Panjang Antrean & Waktu Tunggu)
     ========================================================================== */
  function renderQueueTrendChart() {
    const container = document.getElementById("queue-trend-chart");
    container.innerHTML = "";

    const hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21];
    const maxQueue = 8.0; // Maksimum rata-rata antrean kasir

    hours.forEach(h => {
      const queueVal = data.hourlyAll.avgQueue[h] || 0;
      const waitVal = data.hourlyAll.avgWait[h] || 0;
      const heightQ = (queueVal / maxQueue) * 100;

      const col = document.createElement("div");
      col.className = "cctv-bar-col";
      col.innerHTML = `
        <div class="bar-dual-wrap" title="Pukul ${String(h).padStart(2, '0')}:00 — Rata-rata antrean: ${queueVal} orang | Waktu tunggu: ${waitVal} detik">
          <div class="bar-queue" style="height: ${heightQ}%;"></div>
        </div>
        <span class="col-hour-label">${String(h).padStart(2, '0')}</span>
      `;
      container.appendChild(col);
    });
  }

  /* ==========================================================================
     5. Analisis Jam Sibuk Akhir Pekan & Saran Penambahan Pegawai
     Sesuai logika AGENTS.md:
     - Jam sibuk jika pengunjung/jam >= persentil ATAU ada >= 2 alert
     ========================================================================== */
  function renderBusyHoursAnalysis(percentile) {
    const chartContainer = document.getElementById("busy-bar-chart");
    const adviceList = document.getElementById("advice-list");

    chartContainer.innerHTML = "";
    adviceList.innerHTML = "";

    const hours = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21];
    const weekendIn = hours.map(h => data.weekend.hourlyIn[h] || 0);

    // Hitung ambang persentil
    const sorted = [...weekendIn].sort((a, b) => a - b);
    const pIndex = Math.min(Math.floor((percentile / 100) * sorted.length), sorted.length - 1);
    const threshold = sorted[pIndex];

    const maxChartVal = 110; // Nilai puncak ~99 pengunjung
    const threshPercent = (threshold / maxChartVal) * 100;

    // Tambahkan garis ambang
    const threshLine = document.createElement("div");
    threshLine.className = "threshold-line";
    threshLine.style.bottom = `${threshPercent + 10}%`;
    threshLine.innerHTML = `<span class="threshold-tag">Ambang P${percentile}: ${threshold.toFixed(0)} org/jam</span>`;
    chartContainer.appendChild(threshLine);

    const busyHoursList = [];

    hours.forEach(h => {
      const visitorsAvg = data.weekend.hourlyIn[h] || 0;
      const alertsCount = data.weekend.hourlyAlerts[h] || 0;
      const queueAvg = data.weekend.hourlyQueue[h] || 0;

      const isVisitorsHigh = visitorsAvg >= threshold;
      const isAlertsHigh = alertsCount >= 2;
      const isBusy = isVisitorsHigh || isAlertsHigh;

      const heightBar = (visitorsAvg / maxChartVal) * 100;

      const col = document.createElement("div");
      col.className = "busy-col";
      col.innerHTML = `
        <div class="bar-busy ${isBusy ? 'is-busy' : 'is-normal'}" 
             style="height: ${heightBar}%;"
             title="Pukul ${String(h).padStart(2, '0')}:00: rata-rata ${visitorsAvg} pengunjung/jam, ${alertsCount} alert antrean">
        </div>
        <span class="col-hour-label">${String(h).padStart(2, '0')}</span>
      `;
      chartContainer.appendChild(col);

      if (isBusy) {
        let reasons = [];
        let staffAdvice = "Tambah 1 pegawai";

        if (isVisitorsHigh && isAlertsHigh) {
          reasons.push("pengunjung tinggi", "antrean padat");
        } else if (isVisitorsHigh) {
          reasons.push("pengunjung melampaui batas ambang");
        } else {
          reasons.push("banyak peringatan antrean");
        }

        if (visitorsAvg >= 80 || alertsCount >= 150) {
          staffAdvice = "Tambah 2–3 pegawai kasir/pelayan (Jam Puncak Tertinggi)";
        } else if (visitorsAvg >= 60 || alertsCount >= 100) {
          staffAdvice = "Tambah 2 pegawai kasir";
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
          <p style="color:var(--color-success);font-weight:600;">Tidak ada jam sibuk yang melebihi ambang saat ini. Kapasitas staf mencukupi.</p>
        </div>
      `;
    } else {
      busyHoursList.forEach(item => {
        const advEl = document.createElement("div");
        advEl.className = `advice-item ${item.visitors >= 80 ? 'alert-peak' : ''}`;
        advEl.innerHTML = `
          <div>
            <span class="advice-time">🕐 Pukul ${String(item.hour).padStart(2, '0')}:00 – ${String(item.hour + 1).padStart(2, '0')}:00</span>: 
            rata-rata <strong>${item.visitors.toFixed(0)} pengunjung/jam</strong>, antrean <strong>${item.queue.toFixed(1)} orang</strong>, 
            tercatat <strong>${item.alerts} alert antrean</strong>.
          </div>
          <div class="advice-badge-add">👉 ${item.advice} (${item.reasons}).</div>
        `;
        adviceList.appendChild(advEl);
      });
    }
  }

  /* ==========================================================================
     6. Tabel Log Kejadian & Alert
     ========================================================================== */
  function renderEventsTable(filterText = "") {
    const tbody = document.getElementById("events-table-body");
    tbody.innerHTML = "";

    const events = data.recentEvents.filter(ev => 
      ev.event.toLowerCase().includes(filterText.toLowerCase()) ||
      ev.detail.toLowerCase().includes(filterText.toLowerCase()) ||
      ev.ts.includes(filterText)
    );

    if (events.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;padding:16px;color:var(--color-text-muted);">Tidak ada data alert yang cocok dengan pencarian.</td></tr>`;
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
     7. Simulasi Jam & Pergerakan CCTV
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
     8. Event Listeners & Modal Controls
     ========================================================================== */
  function setupEventListeners() {
    // Slider persentil jam sibuk
    const slider = document.getElementById("percentile-slider");
    const display = document.getElementById("percentile-val-display");

    slider.addEventListener("input", (e) => {
      const val = parseInt(e.target.value, 10);
      currentPercentile = val;
      display.textContent = `P${val} ${val === 75 ? '(Rekomendasi)' : ''}`;
      renderBusyHoursAnalysis(val);
      showToast(`Ambang diatur ke Persentil ${val}`);
    });

    // Filter hari
    document.getElementById("filter-day-select").addEventListener("change", (e) => {
      const selected = e.target.value;
      showToast(`Filter hari: ${e.target.options[e.target.selectedIndex].text}`);
    });

    // Real-time search filter
    document.getElementById("search-input").addEventListener("input", (e) => {
      const val = e.target.value.trim();
      renderEventsTable(val);
    });

    // Tombol lonceng notifikasi
    document.getElementById("notif-btn").addEventListener("click", () => {
      showToast("Terdapat 2.257 alert antrean tercatat di database.");
      const alertsSection = document.getElementById("alerts-section");
      if (alertsSection) alertsSection.scrollIntoView({ behavior: "smooth" });
    });

    // Navigasi sidebar scroll smooth
    document.querySelectorAll(".nav-item").forEach(item => {
      item.addEventListener("click", (e) => {
        const href = item.getAttribute("href");
        if (href && href.startsWith("#")) {
          e.preventDefault();
          document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
          item.classList.add("active");

          if (href === "#config") {
            openConfigModal();
          } else if (href === "#busy-hours") {
            document.getElementById("busy-hours-section")?.scrollIntoView({ behavior: "smooth" });
          } else if (href === "#alerts") {
            document.getElementById("alerts-section")?.scrollIntoView({ behavior: "smooth" });
          } else {
            window.scrollTo({ top: 0, behavior: "smooth" });
          }
        }
      });
    });

    // Modal Konfigurasi
    const configModal = document.getElementById("config-modal");
    document.getElementById("btn-nav-config").addEventListener("click", (e) => {
      e.preventDefault();
      openConfigModal();
    });

    function openConfigModal() {
      configModal.classList.add("open");
    }

    function closeConfigModal() {
      configModal.classList.remove("open");
    }

    document.getElementById("config-modal-close").addEventListener("click", closeConfigModal);
    document.getElementById("config-modal-cancel").addEventListener("click", closeConfigModal);
    document.getElementById("config-modal-save").addEventListener("click", () => {
      closeConfigModal();
      showToast("Parameter config.json berhasil diperbarui!");
    });

    // Tombol simulasi gerak orang CCTV
    document.getElementById("btn-toggle-sim").addEventListener("click", () => {
      const boxes = document.querySelectorAll(".person-sim-box");
      boxes.forEach(b => {
        const rx = (Math.random() - 0.5) * 16;
        const ry = (Math.random() - 0.5) * 16;
        b.style.transform = `translate(${rx}px, ${ry}px)`;
      });
      showToast("Simulasi ByteTrack ID diperbarui.");
    });
  }

  // Toast Helper
  function showToast(msg) {
    const toast = document.getElementById("toast-notification");
    toast.querySelector(".toast-text").textContent = msg;
    toast.classList.add("show");
    setTimeout(() => {
      toast.classList.remove("show");
    }, 2800);
  }
});
