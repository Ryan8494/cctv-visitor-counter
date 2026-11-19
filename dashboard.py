"""
dashboard.py — Dashboard Streamlit untuk manajer restoran & pemantauan CCTV.

Membaca data dari SQLite (hanya baca, tidak menulis).
Menampilkan:
- Pengunjung masuk/keluar per jam
- Tren dan waktu tunggu antrean kasir
- Okupansi meja dan rata-rata durasi duduk
- Analisis jam sibuk akhir pekan berbasis persentil
- Ringkasan harian dan saran penjadwalan staf via modul summary.py

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

from summary import generate_daily_summary


# ── Konfigurasi Halaman ───────────────────────────────────────

st.set_page_config(
    page_title="Dashboard Pemantauan Restoran & CCTV",
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
    """Muat data kunjungan pintu."""
    try:
        df = pd.read_sql_query("SELECT ts, direction FROM visits ORDER BY ts", conn)
        if not df.empty:
            df["ts"] = pd.to_datetime(df["ts"])
            df["hour"] = df["ts"].dt.hour
            df["date"] = df["ts"].dt.date
            df["dayofweek"] = df["ts"].dt.dayofweek
        return df
    except Exception:
        return pd.DataFrame()


def load_queue_samples(conn: sqlite3.Connection) -> pd.DataFrame:
    """Muat data sampel antrean kasir."""
    try:
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
    except Exception:
        return pd.DataFrame()


def load_table_sessions(conn: sqlite3.Connection) -> pd.DataFrame:
    """Muat data sesi duduk meja."""
    try:
        df = pd.read_sql_query(
            "SELECT table_name, start_ts, end_ts, duration_sec FROM table_sessions ORDER BY start_ts",
            conn,
        )
        if not df.empty:
            df["start_ts"] = pd.to_datetime(df["start_ts"])
            df["end_ts"] = pd.to_datetime(df["end_ts"])
            df["hour"] = df["start_ts"].dt.hour
            df["date"] = df["start_ts"].dt.date
            df["dayofweek"] = df["start_ts"].dt.dayofweek
            df["duration_min"] = df["duration_sec"] / 60.0
        return df
    except Exception:
        return pd.DataFrame()


def load_occupancy_samples(conn: sqlite3.Connection) -> pd.DataFrame:
    """Muat data sampel okupansi meja."""
    try:
        df = pd.read_sql_query(
            "SELECT ts, occupied, total FROM occupancy_samples ORDER BY ts",
            conn,
        )
        if not df.empty:
            df["ts"] = pd.to_datetime(df["ts"])
            df["hour"] = df["ts"].dt.hour
            df["date"] = df["ts"].dt.date
            df["dayofweek"] = df["ts"].dt.dayofweek
            df["ratio"] = df["occupied"] / df["total"].replace(0, 1)
        return df
    except Exception:
        return pd.DataFrame()


def load_events(conn: sqlite3.Connection) -> pd.DataFrame:
    """Muat data event/alert."""
    try:
        df = pd.read_sql_query("SELECT ts, event, detail FROM events ORDER BY ts", conn)
        if not df.empty:
            df["ts"] = pd.to_datetime(df["ts"])
            df["hour"] = df["ts"].dt.hour
            df["date"] = df["ts"].dt.date
            df["dayofweek"] = df["ts"].dt.dayofweek
        return df
    except Exception:
        return pd.DataFrame()


# ── Halaman Utama ─────────────────────────────────────────────

def main():
    st.title("📊 Dashboard Asisten Manajer Restoran (CCTV)")
    st.caption("Monitoring Pintu Masuk, Okupansi Meja, dan Antrean Kasir")

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
    df_tables = load_table_sessions(conn)
    df_occ = load_occupancy_samples(conn)
    df_events = load_events(conn)

    if df_visits.empty and df_tables.empty:
        st.warning("Belum ada data di database. Jalankan `python simulate.py` atau `python monitor.py` terlebih dahulu.")
        return

    # ── Sidebar Filter ────────────────────────────────────────
    st.sidebar.header("🔧 Pengaturan & Filter")

    # Filter tanggal
    dates = []
    if not df_visits.empty:
        dates.extend([df_visits["date"].min(), df_visits["date"].max()])
    if not df_tables.empty:
        dates.extend([df_tables["date"].min(), df_tables["date"].max()])

    min_date = min(dates) if dates else datetime.now().date()
    max_date = max(dates) if dates else datetime.now().date()

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

    percentile = st.sidebar.slider(
        "Persentil jam sibuk", 50, 95, 75, 5,
        help="Jam dianggap sibuk jika pengunjung >= persentil ini"
    )

    day_filter = st.sidebar.selectbox(
        "Filter hari",
        ["Semua", "Akhir pekan saja", "Sabtu", "Minggu", "Hari kerja"],
    )

    # ── Terapkan Filter ───────────────────────────────────────
    day_map = {
        "Akhir pekan saja": lambda dow: dow >= 5,
        "Sabtu": lambda dow: dow == 5,
        "Minggu": lambda dow: dow == 6,
        "Hari kerja": lambda dow: dow < 5,
    }

    def apply_filter(df: pd.DataFrame, ts_col: str = "date") -> pd.DataFrame:
        if df.empty:
            return df
        mask = (df[ts_col] >= start_date) & (df[ts_col] <= end_date)
        if day_filter in day_map:
            mask = mask & df["dayofweek"].apply(day_map[day_filter])
        return df[mask]

    fv = apply_filter(df_visits)
    fq = apply_filter(df_queue)
    ft = apply_filter(df_tables)
    focc = apply_filter(df_occ)
    fe = apply_filter(df_events)

    # ── 1. Metrik Ringkasan Utama ─────────────────────────────
    st.header("📈 Metrik Utama")
    col1, col2, col3, col4, col5 = st.columns(5)

    visitors_in = len(fv[fv["direction"] == "IN"]) if not fv.empty else 0
    visitors_out = len(fv[fv["direction"] == "OUT"]) if not fv.empty else 0
    alert_count = len(fe) if not fe.empty else 0

    col1.metric("Pengunjung Masuk", f"{visitors_in:,}")
    col2.metric("Pengunjung Keluar", f"{visitors_out:,}")
    col3.metric("Total Alert", f"{alert_count:,}")

    if not fq.empty:
        col4.metric("Rata-rata Antrean", f"{fq['people_in_zone'].mean():.1f} org")
    else:
        col4.metric("Rata-rata Antrean", "N/A")

    if not ft.empty:
        col5.metric("Rata-rata Durasi Meja", f"{ft['duration_min'].mean():.0f} mnt")
    elif not focc.empty:
        col5.metric("Rata-rata Okupansi", f"{focc['ratio'].mean():.0%}")
    else:
        col5.metric("Okupansi Meja", "N/A")

    st.markdown("---")

    # ── 2. Pintu Masuk & Antrean Kasir ────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("👥 Pengunjung Masuk per Jam")
        if not fv.empty:
            vin = fv[fv["direction"] == "IN"]
            hourly_v = vin.groupby("hour").size().reindex(range(24), fill_value=0)
            fig_v = px.bar(
                x=hourly_v.index,
                y=hourly_v.values,
                labels={"x": "Jam", "y": "Jumlah Masuk"},
                title="Pola Kunjungan Masuk (08:00–22:00)",
            )
            fig_v.update_layout(xaxis_dtick=1)
            st.plotly_chart(fig_v, use_container_width=True)
        else:
            st.info("Tidak ada data kunjungan untuk filter ini.")

    with col_right:
        st.subheader("🧍 Tren Antrean Kasir per Jam")
        if not fq.empty:
            hourly_q = fq.groupby("hour")["people_in_zone"].mean().reindex(range(24), fill_value=0)
            fig_q = px.bar(
                x=hourly_q.index,
                y=hourly_q.values,
                labels={"x": "Jam", "y": "Rata-rata Orang"},
                title="Panjang Antrean Kasir per Jam",
            )
            fig_q.update_layout(xaxis_dtick=1)
            st.plotly_chart(fig_q, use_container_width=True)
        else:
            st.info("Tidak ada data antrean untuk filter ini.")

    # ── 3. Okupansi Meja & Durasi Duduk ───────────────────────
    st.markdown("---")
    st.subheader("🪑 Pemantauan Meja Pengunjung")
    col_t1, col_t2 = st.columns(2)

    with col_t1:
        if not focc.empty:
            hourly_occ = focc.groupby("hour")["ratio"].mean().reindex(range(24), fill_value=0)
            fig_occ = px.line(
                x=hourly_occ.index,
                y=hourly_occ.values * 100,
                labels={"x": "Jam", "y": "Rasio Okupansi Meja (%)"},
                title="Rata-rata Tingkat Keterisian Meja (%)",
                markers=True,
            )
            fig_occ.update_layout(xaxis_dtick=1)
            st.plotly_chart(fig_occ, use_container_width=True)
        else:
            st.info("Belum ada data sampel okupansi meja.")

    with col_t2:
        if not ft.empty:
            table_counts = ft["table_name"].value_counts().reset_index()
            table_counts.columns = ["Meja", "Total Sesi"]
            fig_tbl = px.bar(
                table_counts,
                x="Meja",
                y="Total Sesi",
                title="Jumlah Sesi Pengunjung per Meja",
                color="Meja",
            )
            st.plotly_chart(fig_tbl, use_container_width=True)
        else:
            st.info("Belum ada data sesi meja.")

    # ── 4. Ringkasan Harian & Saran Staf via summary.py ───────
    st.markdown("---")
    st.header("📋 Ringkasan Harian & Saran Staf Manajer")

    # Siapkan agregat per jam untuk modul summary.py
    hourly_vis_dict = {}
    if not fv.empty:
        vin = fv[fv["direction"] == "IN"]
        hourly_vis_dict = vin.groupby("hour").size().to_dict()

    hourly_occ_dict = {}
    if not focc.empty:
        hourly_occ_dict = focc.groupby("hour")["ratio"].mean().to_dict()

    hourly_q_dict = {}
    if not fq.empty:
        hourly_q_dict = fq.groupby("hour")["people_in_zone"].mean().to_dict()

    hourly_alert_dict = {}
    if not fe.empty:
        hourly_alert_dict = fe.groupby("hour").size().to_dict()

    num_days = max(1, (end_date - start_date).days + 1) if isinstance(start_date, datetime) or hasattr(start_date, "day") else 1

    summary_result = generate_daily_summary(
        hourly_visitors=hourly_vis_dict,
        hourly_occupancy_ratio=hourly_occ_dict,
        hourly_queue_avg=hourly_q_dict,
        hourly_alerts=hourly_alert_dict,
        num_days_sample=num_days,
        percentile=percentile,
    )

    if summary_result["warning"]:
        st.warning(f"⚠️ {summary_result['warning']}")

    st.success(f"**Ringkasan**: {summary_result['summary_text']}")

    if summary_result["busy_hours"]:
        st.subheader("💡 Jadwal Tambahan Staf yang Disarankan:")
        for bh in summary_result["busy_hours"]:
            h = bh["hour"]
            reasons = ", ".join(bh["reasons"])
            st.info(
                f"🕐 **Pukul {h:02d}:00–{h + 1:02d}:00**: "
                f"rata-rata {bh['visitors']} tamu, antrean {bh['queue_avg']:.1f} orang ({reasons}). "
                f"**Disarankan: Tambah 1 pegawai kasir/pelayan**."
            )
    else:
        st.info("Operasional stabil: belum ada jam yang melebihi ambang batas sibuk.")

    # ── 5. Tabel Event & Alert Terbaru ────────────────────────
    st.markdown("---")
    st.subheader("🔔 Log Alert & Kejadian Terbaru")
    if not fe.empty:
        recent = fe.sort_values("ts", ascending=False).head(50)
        st.dataframe(
            recent[["ts", "event", "detail"]].rename(columns={
                "ts": "Waktu",
                "event": "Jenis Event",
                "detail": "Keterangan Detail",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Belum ada alert yang tercatat.")


if __name__ == "__main__":
    main()
