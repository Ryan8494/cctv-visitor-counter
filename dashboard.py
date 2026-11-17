"""
dashboard.py — Dashboard Streamlit untuk manajer.

Membaca data dari SQLite (hanya baca, tidak menulis).
Menampilkan: pengunjung per jam, tren antrean, jam sibuk akhir pekan,
dan saran kapan menambah pegawai.

Jalankan: streamlit run dashboard.py
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ── Konfigurasi halaman ───────────────────────────────────────

st.set_page_config(
    page_title="Dashboard Pemantauan Pengunjung",
    page_icon="📊",
    layout="wide",
)


def load_config(path: str = "config.json") -> dict:
    """Muat konfigurasi."""
    config_path = os.path.join(os.path.dirname(__file__), path)
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_resource
def get_connection(db_path: str) -> sqlite3.Connection:
    """Buat koneksi database (di-cache)."""
    return sqlite3.connect(db_path, check_same_thread=False)


def load_visits(conn: sqlite3.Connection) -> pd.DataFrame:
    """Muat data kunjungan."""
    df = pd.read_sql_query("SELECT ts, direction FROM visits ORDER BY ts", conn)
    if not df.empty:
        df["ts"] = pd.to_datetime(df["ts"])
        df["hour"] = df["ts"].dt.hour
        df["date"] = df["ts"].dt.date
        df["dayofweek"] = df["ts"].dt.dayofweek
    return df


def load_queue_samples(conn: sqlite3.Connection) -> pd.DataFrame:
    """Muat data sampel antrean."""
    df = pd.read_sql_query(
        "SELECT ts, people_in_zone, max_wait_sec FROM queue_samples ORDER BY ts",
        conn,
    )
    if not df.empty:
        df["ts"] = pd.to_datetime(df["ts"])
        df["hour"] = df["ts"].dt.hour
        df["date"] = df["ts"].dt.date
        df["dayofweek"] = df["ts"].dt.dayofweek
    return df


def load_events(conn: sqlite3.Connection) -> pd.DataFrame:
    """Muat data event/alert."""
    df = pd.read_sql_query("SELECT ts, event, detail FROM events ORDER BY ts", conn)
    if not df.empty:
        df["ts"] = pd.to_datetime(df["ts"])
        df["hour"] = df["ts"].dt.hour
        df["date"] = df["ts"].dt.date
        df["dayofweek"] = df["ts"].dt.dayofweek
    return df


# ── Halaman utama ─────────────────────────────────────────────

def main():
    st.title("📊 Dashboard Pemantauan Pengunjung & Antrean")
    st.caption("Sistem pemantauan pintu masuk dan antrean berbasis computer vision")

    config = load_config()
    db_path = config.get("db_path", "data.db")

    if not os.path.exists(db_path):
        st.error(
            f"Database '{db_path}' tidak ditemukan. "
            "Jalankan `python simulate.py` untuk membuat data simulasi, "
            "atau `python monitor.py` untuk mulai mendeteksi."
        )
        return

    conn = get_connection(db_path)
    df_visits = load_visits(conn)
    df_queue = load_queue_samples(conn)
    df_events = load_events(conn)

    if df_visits.empty:
        st.warning("Belum ada data kunjungan. Jalankan monitor atau simulasi terlebih dahulu.")
        return

    # ── Sidebar filter ────────────────────────────────────────
    st.sidebar.header("🔧 Filter")

    # Filter tanggal
    min_date = df_visits["date"].min()
    max_date = df_visits["date"].max()
    date_range = st.sidebar.date_input(
        "Rentang tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range

    # Persentil untuk jam sibuk
    percentile = st.sidebar.slider(
        "Persentil jam sibuk", 50, 95, 75, 5,
        help="Jam dianggap sibuk jika pengunjung ≥ persentil ini"
    )

    # Filter hari
    day_filter = st.sidebar.selectbox(
        "Filter hari",
        ["Semua", "Akhir pekan saja", "Sabtu", "Minggu", "Hari kerja"],
    )

    # ── Terapkan filter ───────────────────────────────────────
    mask_visits = (df_visits["date"] >= start_date) & (df_visits["date"] <= end_date)
    mask_queue = pd.Series([True] * len(df_queue))
    mask_events = pd.Series([True] * len(df_events))

    if not df_queue.empty:
        mask_queue = (df_queue["date"] >= start_date) & (df_queue["date"] <= end_date)
    if not df_events.empty:
        mask_events = (df_events["date"] >= start_date) & (df_events["date"] <= end_date)

    day_map = {
        "Akhir pekan saja": lambda dow: dow >= 5,
        "Sabtu": lambda dow: dow == 5,
        "Minggu": lambda dow: dow == 6,
        "Hari kerja": lambda dow: dow < 5,
    }
    if day_filter in day_map:
        fn = day_map[day_filter]
        mask_visits = mask_visits & df_visits["dayofweek"].apply(fn)
        if not df_queue.empty:
            mask_queue = mask_queue & df_queue["dayofweek"].apply(fn)
        if not df_events.empty:
            mask_events = mask_events & df_events["dayofweek"].apply(fn)

    fv = df_visits[mask_visits]
    fq = df_queue[mask_queue] if not df_queue.empty else df_queue
    fe = df_events[mask_events] if not df_events.empty else df_events

    # ── Metrik ringkasan ──────────────────────────────────────
    st.header("📈 Ringkasan")
    col1, col2, col3, col4 = st.columns(4)

    visitors_in = len(fv[fv["direction"] == "IN"])
    visitors_out = len(fv[fv["direction"] == "OUT"])
    alert_count = len(fe) if not fe.empty else 0

    col1.metric("Pengunjung Masuk", f"{visitors_in:,}")
    col2.metric("Pengunjung Keluar", f"{visitors_out:,}")
    col3.metric("Total Alert", f"{alert_count:,}")
    if not fq.empty:
        avg_queue = fq["people_in_zone"].mean()
        col4.metric("Rata-rata Antrean", f"{avg_queue:.1f} orang")
    else:
        col4.metric("Rata-rata Antrean", "N/A")

    # ── Grafik pengunjung per jam ─────────────────────────────
    st.header("👥 Pengunjung per Jam")

    visitors_in_df = fv[fv["direction"] == "IN"]
    if not visitors_in_df.empty:
        hourly = visitors_in_df.groupby("hour").size().reindex(range(24), fill_value=0)
        fig = px.bar(
            x=hourly.index,
            y=hourly.values,
            labels={"x": "Jam", "y": "Jumlah Pengunjung Masuk"},
            title="Distribusi Pengunjung Masuk per Jam",
        )
        fig.update_layout(xaxis_dtick=1)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Tidak ada data pengunjung untuk filter yang dipilih.")

    # ── Tren antrean ──────────────────────────────────────────
    st.header("🧍 Tren Antrean")

    if not fq.empty:
        col_a, col_b = st.columns(2)

        with col_a:
            hourly_queue = fq.groupby("hour")["people_in_zone"].mean()
            hourly_queue = hourly_queue.reindex(range(24), fill_value=0)
            fig_q = px.bar(
                x=hourly_queue.index,
                y=hourly_queue.values,
                labels={"x": "Jam", "y": "Rata-rata Orang di Antrean"},
                title="Rata-rata Panjang Antrean per Jam",
            )
            fig_q.update_layout(xaxis_dtick=1)
            st.plotly_chart(fig_q, use_container_width=True)

        with col_b:
            hourly_wait = fq.groupby("hour")["max_wait_sec"].mean()
            hourly_wait = hourly_wait.reindex(range(24), fill_value=0)
            fig_w = px.line(
                x=hourly_wait.index,
                y=hourly_wait.values,
                labels={"x": "Jam", "y": "Rata-rata Waktu Tunggu Maks (detik)"},
                title="Rata-rata Waktu Tunggu Terlama per Jam",
                markers=True,
            )
            fig_w.update_layout(xaxis_dtick=1)
            st.plotly_chart(fig_w, use_container_width=True)
    else:
        st.info("Tidak ada data antrean.")

    # ── Analisis jam sibuk akhir pekan ────────────────────────
    st.header("🔥 Analisis Jam Sibuk (Akhir Pekan)")

    # Filter data akhir pekan saja
    weekend_visits = df_visits[
        (df_visits["dayofweek"] >= 5) &
        (df_visits["date"] >= start_date) &
        (df_visits["date"] <= end_date)
    ]
    weekend_events = pd.DataFrame()
    if not df_events.empty:
        weekend_events = df_events[
            (df_events["dayofweek"] >= 5) &
            (df_events["date"] >= start_date) &
            (df_events["date"] <= end_date)
        ]

    # Cek jumlah akhir pekan
    if not weekend_visits.empty:
        unique_weekends = weekend_visits["date"].nunique()
        num_weekend_days = unique_weekends

        if num_weekend_days < 4:
            st.warning(
                f"⚠️ Data masih sedikit ({num_weekend_days} hari akhir pekan). "
                "Saran jam sibuk mungkin belum bermakna. "
                "Kumpulkan data minimal beberapa akhir pekan untuk tren yang akurat."
            )

        # Pengunjung masuk per jam di akhir pekan
        wk_in = weekend_visits[weekend_visits["direction"] == "IN"]
        hourly_wk = wk_in.groupby("hour").size().reindex(range(24), fill_value=0)

        # Rata-rata per hari akhir pekan
        if num_weekend_days > 0:
            hourly_avg = hourly_wk / num_weekend_days
        else:
            hourly_avg = hourly_wk

        # Alert per jam di akhir pekan
        hourly_alerts = pd.Series(0, index=range(24))
        if not weekend_events.empty:
            alert_counts = weekend_events.groupby("hour").size()
            for h in alert_counts.index:
                hourly_alerts[h] = alert_counts[h]

        # Rata-rata antrean per jam di akhir pekan
        hourly_queue_avg = pd.Series(0.0, index=range(24))
        if not df_queue.empty:
            weekend_queue = df_queue[
                (df_queue["dayofweek"] >= 5) &
                (df_queue["date"] >= start_date) &
                (df_queue["date"] <= end_date)
            ]
            if not weekend_queue.empty:
                q_avg = weekend_queue.groupby("hour")["people_in_zone"].mean()
                for h in q_avg.index:
                    hourly_queue_avg[h] = q_avg[h]

        # Tentukan jam sibuk
        threshold = hourly_avg.quantile(percentile / 100)
        busy_hours = []

        for hour in range(24):
            is_busy_visitors = hourly_avg.get(hour, 0) >= threshold
            is_busy_alerts = hourly_alerts.get(hour, 0) >= 2
            if is_busy_visitors or is_busy_alerts:
                busy_hours.append({
                    "jam": hour,
                    "pengunjung_avg": hourly_avg.get(hour, 0),
                    "antrean_avg": hourly_queue_avg.get(hour, 0),
                    "alert": hourly_alerts.get(hour, 0),
                    "alasan": [],
                })
                if is_busy_visitors:
                    busy_hours[-1]["alasan"].append("pengunjung tinggi")
                if is_busy_alerts:
                    busy_hours[-1]["alasan"].append("banyak alert")

        if busy_hours:
            st.subheader("📋 Saran Penambahan Pegawai")

            for bh in busy_hours:
                jam = bh["jam"]
                reasons = " dan ".join(bh["alasan"])
                st.info(
                    f"🕐 **Pukul {jam:02d}:00-{jam + 1:02d}:00**: "
                    f"rata-rata {bh['pengunjung_avg']:.0f} pengunjung, "
                    f"antrean {bh['antrean_avg']:.1f} orang, "
                    f"{bh['alert']} alert. "
                    f"**Tambah pegawai** ({reasons})."
                )

            # Visualisasi jam sibuk
            fig_busy = go.Figure()
            fig_busy.add_trace(go.Bar(
                x=hourly_avg.index,
                y=hourly_avg.values,
                name="Pengunjung (rata-rata)",
                marker_color=["red" if any(bh["jam"] == h for bh in busy_hours)
                               else "steelblue" for h in range(24)],
            ))
            fig_busy.add_hline(
                y=threshold,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Ambang P{percentile}",
            )
            fig_busy.update_layout(
                title="Jam Sibuk Akhir Pekan",
                xaxis_title="Jam",
                yaxis_title="Rata-rata Pengunjung Masuk",
                xaxis_dtick=1,
            )
            st.plotly_chart(fig_busy, use_container_width=True)
        else:
            st.success("Tidak ada jam yang terdeteksi sibuk dengan ambang saat ini.")
    else:
        st.info("Tidak ada data akhir pekan untuk dianalisis.")

    # ── Tabel event terbaru ───────────────────────────────────
    st.header("🔔 Event/Alert Terbaru")

    if not fe.empty:
        recent = fe.sort_values("ts", ascending=False).head(50)
        st.dataframe(
            recent[["ts", "event", "detail"]].rename(columns={
                "ts": "Waktu",
                "event": "Event",
                "detail": "Detail",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Belum ada event/alert.")


if __name__ == "__main__":
    main()
