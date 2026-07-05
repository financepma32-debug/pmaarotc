"""
AR OTC + AR GT Dashboard — PT Pinus Merah Abadi | FAD Team
Fix: header tidak terpotong, timestamp realtime, SO Block 1 tabel, menu GT
Supabase: project pma-arotc — tabel os_master (OTC) | bucket arotcgt (GT)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client
from datetime import datetime

st.set_page_config(
    page_title="AR Dashboard — PMA FAD",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');

/* ── Reset & Base ─────────────────────────────────── */
html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
* { box-sizing: border-box; }

[data-testid="stAppViewContainer"] { background: #FFFFFF; }
[data-testid="stSidebar"] {
    background: #FAFAFA;
    border-right: 1px solid #ECECEC;
}
[data-testid="stSidebar"] * { font-size: 13px; color: #374151; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label { font-size: 11px; color: #9CA3AF; font-weight: 500; text-transform: uppercase; letter-spacing: .6px; }

.block-container { padding: 3.5rem 2.4rem 3rem !important; max-width: 100% !important; }

/* ── Header ───────────────────────────────────────── */
.pma-header {
    background: #B01C2E;
    border-radius: 16px;
    padding: 20px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 20px;
    width: 100%;
}
.pma-hl { flex: 1; min-width: 0; }
.pma-title {
    color: #fff;
    font-size: 16px;
    font-weight: 600;
    margin: 0;
    letter-spacing: -.2px;
    white-space: normal !important;
    overflow: visible !important;
}
.pma-sub { color: rgba(255,255,255,.55); font-size: 12px; margin: 4px 0 0; font-weight: 400; }
.pma-date {
    color: rgba(255,255,255,.90);
    font-size: 13px;
    font-weight: 500;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
    flex-shrink: 0;
}

/* ── Sticky header freeze ────────────────────────── */
.pma-sticky {
    position: sticky;
    top: 0;
    z-index: 999;
    background: #FFFFFF;
    padding-bottom: 8px;
    padding-top: 4px;
}

/* ── Meta bar (update + count) ────────────────────── */
.upd-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 11.5px;
    color: #9CA3AF;
    margin-bottom: 24px;
    padding: 0 2px;
}
.upd-bar strong { color: #374151; font-weight: 600; }

/* ── KPI Cards ────────────────────────────────────── */
.kpi-grid { display: flex; gap: 16px; margin-bottom: 28px; }
.kpi {
    flex: 1;
    background: #FFFFFF;
    border: 1px solid #ECECEC;
    border-radius: 16px;
    padding: 20px 20px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04), 0 1px 2px rgba(0,0,0,.03);
    position: relative;
    overflow: hidden;
    min-height: 100px;
}
.kpi::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: #ECECEC;
    border-radius: 16px 16px 0 0;
}
.kpi.accent-red::before   { background: #B01C2E; }
.kpi.accent-green::before { background: #059669; }
.kpi.accent-amber::before { background: #D97706; }
.kpi.accent-blue::before  { background: #2563EB; }
.kpi.accent-slate::before { background: #64748B; }

.kpi-icon {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 14px;
}
.kpi-icon.red   { background: #FEF2F2; }
.kpi-icon.green { background: #ECFDF5; }
.kpi-icon.amber { background: #FFFBEB; }
.kpi-icon.blue  { background: #EFF6FF; }
.kpi-icon.slate { background: #F8FAFC; }

.kpi-icon svg { width: 16px; height: 16px; }

.kpi-lbl {
    font-size: 11px;
    font-weight: 500;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: .7px;
    margin: 0 0 6px;
    display: block;
}
.kpi-val {
    font-size: 24px;
    font-weight: 700;
    color: #111827;
    line-height: 1;
    margin: 0 0 6px;
    font-variant-numeric: tabular-nums;
    letter-spacing: -.5px;
}
.kpi-sub {
    font-size: 11.5px;
    color: #9CA3AF;
    margin: 0;
    line-height: 1.4;
}

/* ── Aging Bucket Strip ───────────────────────────── */
.bk-strip {
    display: flex;
    gap: 8px;
    margin-bottom: 32px;
    padding: 0;
}
.bk-cell {
    flex: 1;
    background: #FFFFFF;
    border: 1px solid #ECECEC;
    border-radius: 12px;
    padding: 14px 12px 12px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.bk-cell::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 0 0 12px 12px;
}
.bk-lbl {
    font-size: 9px;
    font-weight: 600;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: .6px;
    margin: 0 0 6px;
    display: block;
}
.bk-val {
    font-size: 13px;
    font-weight: 700;
    color: #111827;
    font-variant-numeric: tabular-nums;
    display: block;
}
.bk-total {
    background: #111827;
    border-color: #111827;
}
.bk-total .bk-lbl { color: rgba(255,255,255,.5); }
.bk-total .bk-val  { color: #FFFFFF; }

/* ── SO Block Cards ───────────────────────────────── */
.so-wrap { display: flex; gap: 16px; margin-bottom: 20px; }
.so-card {
    flex: 1;
    background: #FFFFFF;
    border: 1px solid #ECECEC;
    border-radius: 16px;
    padding: 20px 20px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,.04);
}
.so-card.warn { border-top: 3px solid #D97706; }
.so-card.soft { border-top: 3px solid #EA580C; }
.so-card.crit { border-top: 3px solid #B01C2E; }

.so-tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: .5px;
    text-transform: uppercase;
    border-radius: 6px;
    padding: 3px 8px;
    margin-bottom: 12px;
}
.so-tag.warn { background: #FFFBEB; color: #92400E; }
.so-tag.soft { background: #FFF7ED; color: #9A3412; }
.so-tag.crit { background: #FEF2F2; color: #991B1B; }

.so-tag-dot {
    width: 6px; height: 6px; border-radius: 50%;
    display: inline-block;
}
.so-tag.warn .so-tag-dot { background: #D97706; }
.so-tag.soft .so-tag-dot { background: #EA580C; }
.so-tag.crit .so-tag-dot { background: #B01C2E; }

.so-val {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
    margin: 0 0 6px;
    letter-spacing: -.5px;
    font-variant-numeric: tabular-nums;
}
.so-sub  { font-size: 12px; color: #6B7280; margin: 0 0 6px; }
.so-desc { font-size: 11px; color: #9CA3AF; margin: 0; }

/* ── Section Title ────────────────────────────────── */
.sec {
    font-size: 11px;
    font-weight: 600;
    color: #374151;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 32px 0 12px;
    padding-bottom: 10px;
    border-bottom: 1px solid #F3F4F6;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sec::before {
    content: '';
    width: 3px; height: 14px;
    background: #B01C2E;
    border-radius: 2px;
    display: inline-block;
    flex-shrink: 0;
}

/* ── Tables ───────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid #F3F4F6 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] thead th {
    background: #F9FAFB !important;
    color: #6B7280 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: .5px !important;
    border-bottom: 1px solid #F3F4F6 !important;
}
[data-testid="stDataFrame"] tbody td {
    font-size: 12.5px !important;
    color: #374151 !important;
    border-bottom: 1px solid #F9FAFB !important;
}

/* ── Tabs ─────────────────────────────────────────── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #ECECEC;
    background: transparent;
    padding: 0;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-size: 13px;
    font-weight: 500;
    padding: 10px 20px;
    border-radius: 0;
    color: #9CA3AF;
    background: transparent;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: #111827 !important;
    font-weight: 600 !important;
    background: transparent !important;
    border-bottom: 2px solid #B01C2E !important;
}

/* ── Sidebar buttons & controls ──────────────────── */
[data-testid="stSidebar"] .stButton button {
    background: #111827;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 500;
    padding: 8px 0;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #1F2937;
}

/* ── Expander ─────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #ECECEC !important;
    border-radius: 12px !important;
    background: #FFFFFF !important;
}

/* ── Download button ──────────────────────────────── */
[data-testid="stDownloadButton"] button {
    background: #FFFFFF !important;
    border: 1px solid #ECECEC !important;
    color: #374151 !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
}
[data-testid="stDownloadButton"] button:hover {
    border-color: #B01C2E !important;
    color: #B01C2E !important;
}
</style>
""", unsafe_allow_html=True)

# ── KONSTANTA ────────────────────────────────────────────────────────────────
BUCKETS = ["CURRENT","1-7 DAYS","8-30 DAYS","31-60 DAYS",
           "61-90 DAYS","91-120 DAYS","121+ DAYS","<2026"]
BUCKET_COLOR = {
    "CURRENT":"#0F9D58","1-7 DAYS":"#F5A623","8-30 DAYS":"#F5A623",
    "31-60 DAYS":"#E65C00","61-90 DAYS":"#E65C00",
    "91-120 DAYS":"#C8192E","121+ DAYS":"#8C0A1C","<2026":"#6B6B6B",
}
SO_MAP = {
    "1-7 DAYS":"WARNING SO","8-30 DAYS":"WARNING SO",
    "31-60 DAYS":"SOFT BLOCK","61-90 DAYS":"SOFT BLOCK",
    "91-120 DAYS":"CRITICAL BLOCK","121+ DAYS":"CRITICAL BLOCK","<2026":"CRITICAL BLOCK",
}
CHART_PALETTE = ["#C8192E","#F5A623","#0F9D58","#1A73E8",
                 "#9B27AF","#E65C00","#00897B","#E91E8C","#546E7A","#6D4C41"]

# OTC — 49 kolom
OTC_NUMERIC = {
    "NOMINAL","Nilai Faktur","Saldo Awal","Movement","Saldo Akhir",
    "CURRENT","1-7 DAYS","8-30 DAYS","31-60 DAYS","61-90 DAYS",
    "91-120 DAYS","121+ DAYS","<2026",
    "OVERDUE","OVERDUE?","ACTUAL PELUNASAN","TARGET PELUNASAN",
    "DUE DATE","Qty Faktur Gantung",
}
OTC_DATE = {"Tanggal Faktur","Tanggal JT","Tgl Target Pelunasan System",
            "Tgl Konfirmasi","TANGGAL HARI INII","batas 2025"}
OTC_ALL_COLS = [
    "NAMA AREA","NAMA SALES","No Faktur","NAMA TOKO","KATEGORI OVERDUE",
    "REGION","JENIS OUTLET","ASM","RBM","NOMINAL","GROUPING OS",
    "No Faktur SAP","Tanggal Faktur","Tanggal JT","Nilai Faktur","Saldo Awal",
    "TOP","No Faktur Scylla","No Faktur SAP2","Tgl Target Pelunasan System",
    "Tipe Transaksi","Movement","Saldo Akhir",
    "Kronologi","Jenis BA","No BA","BAP","Tgl Konfirmasi","Action Plan","Penyelesaian",
    "BERAPA HARI?","KELOMPOK",
    "CURRENT","1-7 DAYS","8-30 DAYS","31-60 DAYS","61-90 DAYS",
    "91-120 DAYS","121+ DAYS","<2026",
    "KELOMPOK2","OVERDUE","TANGGAL HARI INII","batas 2025","OVERDUE?",
    "ACTUAL PELUNASAN","TARGET PELUNASAN","DUE DATE","Qty Faktur Gantung",
]

# GT — kolom dari gt_to_master.py
GT_NUMERIC = {
    "Nominal","Nilai Faktur","Movement","Saldo Akhir",
    "CURRENT","1-7 DAYS","8-30 DAYS","31-60 DAYS","61-90 DAYS",
    "91-120 DAYS","121+ DAYS","<2026",
    "OVERDUE","OVERDUE?","ACTUAL PELUNASAN","TARGET PELUNASAN","DUE DATE","Qty Faktur",
}
GT_DATE = {"Tanggal Faktur","Tanggal JT","Tgl Target Pelunasan","TANGGAL HARI INII","batas 2025"}
GT_ALL_COLS = [
    "Nama Area","Nama Sales","Nama Toko","Kategori Overdue","Region",
    "Jenis Outlet","Nominal","Grouping OS","RBM","ASM","No Faktur",
    "No Faktur Scylla","Tanggal Faktur","Tanggal JT","Nilai Faktur","TOP",
    "JENIS KASUS","KRONOLOGI","JENIS BA","NO BA","BAP","TGL KONFIRMASI",
    "ACTION PLAN","PENYELESAIAN","No Faktur SAP","Tipe Transaksi",
    "Movement","Saldo Akhir","Tgl Target Pelunasan",
    "BERAPA HARI?","KELOMPOK",
    "CURRENT","1-7 DAYS","8-30 DAYS","31-60 DAYS","61-90 DAYS",
    "91-120 DAYS","121+ DAYS","<2026",
    "KELOMPOK2","OVERDUE","TANGGAL HARI INII","batas 2025","OVERDUE?",
    "ACTUAL PELUNASAN","TARGET PELUNASAN","DUE DATE","Qty Faktur",
]

# ── FORMAT ───────────────────────────────────────────────────────────────────
def M(v):
    v = float(v)
    if abs(v)>=1_000_000_000: return f"{v/1_000_000_000:.2f}M"
    if abs(v)>=1_000_000:     return f"{v/1_000_000:.1f}Jt"
    return f"{v:,.0f}"
def R(v): return f"{float(v):,.0f}"
def P(n,d): return f"{n/d*100:.1f}%" if d else "–"

# ── SUPABASE — project sama, anon/service role sama ──────────────────────────
@st.cache_resource(show_spinner=False)
def get_sb():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

@st.cache_data(ttl=300, show_spinner=False)
def load_otc():
    sb = get_sb()
    last_updated = "–"
    try:
        meta = sb.table("upload_log").select("uploaded_at,total_rows") \
                 .order("uploaded_at",desc=True).limit(1).execute()
        if meta.data:
            raw = meta.data[0].get("uploaded_at","")
            try:
                dt = datetime.fromisoformat(raw.replace("Z","+00:00"))
                last_updated = dt.strftime("%d %b %Y · %H:%M WIB")
            except Exception:
                last_updated = raw
    except Exception:
        pass
    try:
        rows,page,SZ = [],0,1000
        while True:
            r = sb.table("os_master").select("*").range(page*SZ,(page+1)*SZ-1).execute()
            if not r.data: break
            rows.extend(r.data)
            if len(r.data)<SZ: break
            page+=1
        if not rows: return pd.DataFrame(), last_updated
        df = pd.DataFrame(rows)
        for c in ("id","created_at"):
            if c in df.columns: df.drop(columns=c,inplace=True)
        for col in OTC_ALL_COLS:
            if col not in df.columns: df[col]=None
        df = df[[c for c in OTC_ALL_COLS if c in df.columns]].copy()
        for col in OTC_NUMERIC:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col],errors="coerce").fillna(0)
        for col in OTC_DATE:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col],errors="coerce")
        return df, last_updated
    except Exception as e:
        st.error(f"Gagal ambil data OTC: {e}")
        return pd.DataFrame(), last_updated

@st.cache_data(ttl=300, show_spinner=False)
def load_gt():
    """Load data GT dari tabel gt_master di Supabase."""
    sb = get_sb()
    last_updated = "–"
    try:
        meta = sb.table("upload_log_gt").select("uploaded_at,total_rows") \
                 .order("uploaded_at",desc=True).limit(1).execute()
        if meta.data:
            raw = meta.data[0].get("uploaded_at","")
            try:
                dt = datetime.fromisoformat(raw.replace("Z","+00:00"))
                last_updated = dt.strftime("%d %b %Y · %H:%M WIB")
            except Exception:
                last_updated = raw
    except Exception:
        pass
    try:
        rows,page,SZ = [],0,1000
        while True:
            r = sb.table("gt_master").select("*").range(page*SZ,(page+1)*SZ-1).execute()
            if not r.data: break
            rows.extend(r.data)
            if len(r.data)<SZ: break
            page+=1
        if not rows: return pd.DataFrame(), last_updated
        df = pd.DataFrame(rows)
        for c in ("id","created_at"):
            if c in df.columns: df.drop(columns=c,inplace=True)
        for col in GT_ALL_COLS:
            if col not in df.columns: df[col]=None
        df = df[[c for c in GT_ALL_COLS if c in df.columns]].copy()
        for col in GT_NUMERIC:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col],errors="coerce").fillna(0)
        for col in GT_DATE:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col],errors="coerce")
        return df, last_updated
    except Exception as e:
        st.error(f"Gagal ambil data GT: {e}")
        return pd.DataFrame(), last_updated

# ── PLOTLY ───────────────────────────────────────────────────────────────────
FONT = dict(family="Inter,sans-serif",size=11,color="#1E1E1E")
def plot_base(fig, h=300, margin=None):
    m = margin or dict(t=14,b=10,l=6,r=6)
    fig.update_layout(
        plot_bgcolor="#FFFFFF", paper_bgcolor="rgba(0,0,0,0)",
        font=FONT, height=h, margin=m,
        xaxis=dict(gridcolor="#EDE5DC",linecolor="#D0C8BF",tickfont_size=10),
        yaxis=dict(gridcolor="#EDE5DC",linecolor="#D0C8BF",tickfont_size=10),
        showlegend=False,
    )
    return fig

def sec(t): st.markdown(f"<div class='sec'>{t}</div>", unsafe_allow_html=True)


# KPI icon registry — pure SVG, no emoji
_KPI_ICONS = {
    "outstanding": '''<svg viewBox="0 0 24 24" fill="none" stroke="#B01C2E" stroke-width="1.8" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18.75a60.07 60.07 0 0115.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 013 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 00-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 01-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 003 15h-.75M15 10.5a3 3 0 11-6 0 3 3 0 016 0zm3 0h.008v.008H18V10.5zm-12 0h.008v.008H6V10.5z"/></svg>''',
    "overdue":     '''<svg viewBox="0 0 24 24" fill="none" stroke="#B01C2E" stroke-width="1.8" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>''',
    "current":     '''<svg viewBox="0 0 24 24" fill="none" stroke="#059669" stroke-width="1.8" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>''',
    "collection":  '''<svg viewBox="0 0 24 24" fill="none" stroke="#D97706" stroke-width="1.8" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" d="M2.25 18L9 11.25l4.306 4.307a11.95 11.95 0 015.814-5.519l2.74-1.22m0 0l-5.94-2.28m5.94 2.28l-2.28 5.941"/></svg>''',
    "duedate":     '''<svg viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="1.8" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5"/></svg>''',
    "qty":         '''<svg viewBox="0 0 24 24" fill="none" stroke="#64748B" stroke-width="1.8" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 010 3.75H5.625a1.875 1.875 0 010-3.75z"/></svg>''',
}

_KPI_META = {
    # cls        → (accent, icon_key, icon_color_cls)
    "":          ("accent-red",   "outstanding", "red"),
    "green":     ("accent-green", "current",     "green"),
    "gold":      ("accent-amber", "collection",  "amber"),
    "stone":     ("accent-blue",  "duedate",     "blue"),
    "orange":    ("accent-slate", "qty",         "slate"),
    "overdue":   ("accent-red",   "overdue",     "red"),
}

def kpi(co, label, val, sub="", cls=""):
    accent, icon_key, icon_cls = _KPI_META.get(cls, ("accent-red","outstanding","red"))
    icon_svg = _KPI_ICONS.get(icon_key, _KPI_ICONS["outstanding"])
    with co:
        st.markdown(
            f"<div class='kpi {accent}'>"
            f"<div class='kpi-icon {icon_cls}'>{icon_svg}</div>"
            f"<span class='kpi-lbl'>{label}</span>"
            f"<div class='kpi-val'>{val}</div>"
            f"<div class='kpi-sub'>{sub}</div>"
            f"</div>", unsafe_allow_html=True)


def dl_btn(df_export, filename, label="Download CSV"):
    csv = df_export.to_csv(index=False,sep=";",encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(label, data=csv,
                       file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                       mime="text/csv", use_container_width=True)

def bucket_strip(dff):
    bv = {b: dff[b].sum() if b in dff.columns else 0 for b in BUCKETS}
    grand = sum(bv.values())
    cells = "".join([
        f"<div class='bk-cell' style='--bk-accent:{BUCKET_COLOR[b]}'>"
        f"<span class='bk-lbl'>{b}</span>"
        f"<span class='bk-val'>{M(bv[b])}</span>"
        f"<style>.bk-cell[style*='{BUCKET_COLOR[b]}']::after{{background:{BUCKET_COLOR[b]};}}</style>"
        f"</div>"
        for b in BUCKETS
    ])
    cells += (
        f"<div class='bk-cell bk-total'>"
        f"<span class='bk-lbl'>Total</span>"
        f"<span class='bk-val'>{M(grand)}</span></div>"
    )
    st.markdown(f"<div class='bk-strip'>{cells}</div>", unsafe_allow_html=True)
    return bv, grand

def pma_header(title, last_updated, n_faktur):
    st.markdown(f"""
    <div class="pma-sticky">
      <div class="pma-header">
        <div class="pma-hl">
          <p class="pma-title">{title}</p>
          <p class="pma-sub">PT Pinus Merah Abadi &nbsp;·&nbsp; FAD Team</p>
        </div>
        <span class="pma-date">{datetime.now().strftime('%d %b %Y')}</span>
      </div>
      <div class="upd-bar">
        <span>Update terakhir: <strong>{last_updated}</strong></span>
        <span>{n_faktur:,} faktur ditampilkan</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# PAGE: AR OTC
# ════════════════════════════════════════════════════════════════════
def page_otc():
    with st.spinner("Memuat data OTC..."):
        df, last_updated = load_otc()

    if df.empty:
        st.warning("Belum ada data OTC. Jalankan **JALANKAN_UPLOAD.bat** untuk upload data.")
        return

    # ── SIDEBAR ───────────────────────────────────────────────────
    st.sidebar.markdown("### Filter OTC")
    def sb(label, col, src):
        opts = ["Semua"] + sorted(src[col].dropna().unique().tolist())
        return st.sidebar.selectbox(label, opts, key=f"otc_{col}")

    sel_region = sb("Region",       "REGION",       df)
    d0 = df if sel_region=="Semua" else df[df["REGION"]==sel_region]
    sel_area   = sb("Nama Area",    "NAMA AREA",    d0)
    d1 = d0 if sel_area=="Semua" else d0[d0["NAMA AREA"]==sel_area]
    sel_jenis  = sb("Jenis Outlet", "JENIS OUTLET", d1)
    sel_asm    = sb("ASM",          "ASM",          d1)
    sel_rbm    = sb("RBM",          "RBM",          d1)
    sel_grp    = sb("Grouping OS",  "GROUPING OS",  d1)
    sel_bkt    = st.sidebar.multiselect("Kelompok Aging", BUCKETS, default=BUCKETS, key="otc_bkt")
    st.sidebar.markdown("---")
    if st.sidebar.button("↺ Refresh OTC", use_container_width=True, key="ref_otc"):
        st.cache_data.clear(); st.rerun()
    st.sidebar.caption(f"Terakhir diperbarui: {last_updated}")

    dff = df.copy()
    if sel_region!="Semua": dff=dff[dff["REGION"]      ==sel_region]
    if sel_area  !="Semua": dff=dff[dff["NAMA AREA"]   ==sel_area]
    if sel_jenis !="Semua": dff=dff[dff["JENIS OUTLET"] ==sel_jenis]
    if sel_asm   !="Semua": dff=dff[dff["ASM"]         ==sel_asm]
    if sel_rbm   !="Semua": dff=dff[dff["RBM"]         ==sel_rbm]
    if sel_grp   !="Semua": dff=dff[dff["GROUPING OS"] ==sel_grp]
    if sel_bkt:              dff=dff[dff["KELOMPOK"].isin(sel_bkt)]
    if dff.empty:
        st.warning("Tidak ada data sesuai filter."); return

    pma_header("AR Outstanding MT — MTI NKA", last_updated, len(dff))

    # KPI
    tn=dff["NOMINAL"].sum(); to=dff["OVERDUE"].sum(); tc=dff["CURRENT"].sum()
    ta=dff["ACTUAL PELUNASAN"].sum(); tt=dff["TARGET PELUNASAN"].sum()
    td=dff["DUE DATE"].sum(); tq=int(dff["Qty Faktur Gantung"].sum())
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    kpi(c1,"Total Outstanding",M(tn),f"Nilai Faktur {M(dff['Nilai Faktur'].sum())}")
    kpi(c2,"Overdue",M(to),P(to,tn)+" dari outstanding")
    kpi(c3,"Current",M(tc),P(tc,tn)+" dari total","green")
    kpi(c4,"% Collection",P(ta,tt),f"Actual {M(ta)} / Target {M(tt)}","gold")
    kpi(c5,"Due Date Hari Ini",M(td),"Nominal jatuh tempo hari ini","stone")
    kpi(c6,"Qty Faktur Gantung",f"{tq:,}",f"{len(dff):,} baris data","orange")
    st.markdown("<br>",unsafe_allow_html=True)

    bv, grand = bucket_strip(dff)

    # ════ SO BLOCK — 1 TABEL dengan kolom SO Status, Area, Kode Customer, dll ════
    sec("STATUS SO BLOCK — REKOMENDASI TINDAKAN")

    df_ov = dff[dff["KELOMPOK"]!="CURRENT"].copy()
    df_ov["SO Status"] = df_ov["KELOMPOK"].map(SO_MAP)

    wn = df_ov[df_ov["SO Status"]=="WARNING SO"]["NOMINAL"].sum()
    sn = df_ov[df_ov["SO Status"]=="SOFT BLOCK"]["NOMINAL"].sum()
    cn = df_ov[df_ov["SO Status"]=="CRITICAL BLOCK"]["NOMINAL"].sum()
    wf = (df_ov["SO Status"]=="WARNING SO").sum()
    sf = (df_ov["SO Status"]=="SOFT BLOCK").sum()
    cf = (df_ov["SO Status"]=="CRITICAL BLOCK").sum()
    wa = df_ov[df_ov["SO Status"]=="WARNING SO"]["NAMA AREA"].nunique()
    sa = df_ov[df_ov["SO Status"]=="SOFT BLOCK"]["NAMA AREA"].nunique()
    ca = df_ov[df_ov["SO Status"]=="CRITICAL BLOCK"]["NAMA AREA"].nunique()

    st.markdown(f"""
    <div class="so-wrap">
      <div class="so-card warn">
        <span class="so-tag warn"><span class="so-tag-dot"></span>Warning SO</span>
        <p class="so-val">{M(wn)}</p>
        <p class="so-sub">{wf:,} faktur · {wa} area</p>
        <p class="so-desc">1–7 hari & 8–30 hari — segera follow up</p>
      </div>
      <div class="so-card soft">
        <span class="so-tag soft"><span class="so-tag-dot"></span>Soft Block</span>
        <p class="so-val">{M(sn)}</p>
        <p class="so-sub">{sf:,} faktur · {sa} area</p>
        <p class="so-desc">31–60 & 61–90 hari — hold pengiriman baru</p>
      </div>
      <div class="so-card crit">
        <span class="so-tag crit"><span class="so-tag-dot"></span>Critical Block</span>
        <p class="so-val">{M(cn)}</p>
        <p class="so-sub">{cf:,} faktur · {ca} area</p>
        <p class="so-desc">91+ hari & &lt;2026 — blokir SO, eskalasi manajemen</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # SATU TABEL SO BLOCK — kolom: Status | Area | Nama Toko | ASM | RBM | No Faktur | Qty | Nilai Faktur
    # Kode Customer = No Faktur SAP (identitas customer di SAP)
    so_cols_src = {
        "SO Status":     "SO Status",
        "Nama Area":     "NAMA AREA",
        "Kode Customer": "No Faktur SAP",
        "Nama Toko":     "NAMA TOKO",
        "ASM":           "ASM",
        "RBM":           "RBM",
        "No Faktur":     "No Faktur",
        "Kelompok":      "KELOMPOK",
    }
    tbl_so = df_ov.copy()
    # Qty faktur per toko per SO Status — dibangun dari groupby
    so_out_cols = ["SO Status","NAMA AREA","No Faktur SAP","NAMA TOKO","ASM","RBM",
                   "No Faktur","KELOMPOK","NOMINAL","Nilai Faktur"]
    so_out_cols = [c for c in so_out_cols if c in tbl_so.columns]
    tbl_so = tbl_so[so_out_cols].copy()

    # Tambah kolom Qty Faktur per Nama Toko
    qty_map = tbl_so.groupby("NAMA TOKO")["No Faktur"].transform("count") if "NAMA TOKO" in tbl_so.columns else 0
    tbl_so.insert(tbl_so.columns.get_loc("No Faktur")+1 if "No Faktur" in tbl_so.columns else len(tbl_so.columns),
                  "Qty Faktur", qty_map)

    # Format angka
    for c in ["NOMINAL","Nilai Faktur"]:
        if c in tbl_so.columns: tbl_so[c] = tbl_so[c].apply(M)

    # Rename kolom akhir
    rename_map = {
        "SO Status":"SO Status","NAMA AREA":"Nama Area","No Faktur SAP":"Kode Customer",
        "NAMA TOKO":"Nama Toko","ASM":"ASM","RBM":"RBM",
        "No Faktur":"No Faktur","Qty Faktur":"Qty Faktur",
        "NOMINAL":"Nilai OS","Nilai Faktur":"Nilai Faktur","KELOMPOK":"Kelompok",
    }
    tbl_so.rename(columns=rename_map, inplace=True)
    tbl_so.insert(0,"#",range(1,len(tbl_so)+1))

    # Urutkan: Critical dulu, lalu Soft Block, lalu Warning SO
    order = {"CRITICAL BLOCK":0,"SOFT BLOCK":1,"WARNING SO":2}
    if "SO Status" in tbl_so.columns:
        tbl_so["_ord"] = tbl_so["SO Status"].map(order).fillna(3)
        tbl_so = tbl_so.sort_values("_ord").drop(columns="_ord")

    st.dataframe(tbl_so, use_container_width=True, hide_index=True, height=400)
    dl_btn(df_ov[so_out_cols], "SO_BLOCK_DETAIL", "Download SO Block Detail")

    # Chart distribusi SO Block per area (top 10)
    sec("DISTRIBUSI SO BLOCK PER NAMA AREA")
    pivot = (df_ov.groupby(["NAMA AREA","SO Status"])["NOMINAL"]
             .sum().unstack(fill_value=0).reset_index())
    for k in ["WARNING SO","SOFT BLOCK","CRITICAL BLOCK"]:
        if k not in pivot.columns: pivot[k]=0
    pivot["TOTAL"] = pivot[["WARNING SO","SOFT BLOCK","CRITICAL BLOCK"]].sum(axis=1)
    pivot = pivot.nlargest(10,"TOTAL")
    fig_so = go.Figure()
    for col_key,color,name in [
        ("CRITICAL BLOCK","#C8192E","Critical Block"),
        ("SOFT BLOCK","#E65C00","Soft Block"),
        ("WARNING SO","#F5A623","Warning SO"),
    ]:
        if col_key in pivot.columns:
            fig_so.add_trace(go.Bar(
                name=name, x=pivot["NAMA AREA"], y=pivot[col_key],
                marker_color=color,
                text=pivot[col_key].apply(lambda v: M(v) if v>0 else ""),
                textposition="inside", textfont=dict(size=9,color="#fff"),
            ))
    plot_base(fig_so, h=340)
    fig_so.update_layout(barmode="stack",showlegend=True,
        legend=dict(orientation="h",x=0,y=1.06,font_size=11),
        xaxis_tickangle=-30,yaxis_tickformat=",")
    st.plotly_chart(fig_so, use_container_width=True)

    # ════ KOMPOSISI ════
    sec("KOMPOSISI OUTSTANDING")
    ca2,cb2 = st.columns([5,4])
    with ca2:
        grp_os = (dff[dff["NOMINAL"]>0].groupby("GROUPING OS")["NOMINAL"]
                  .sum().sort_values().reset_index())
        grp_os.columns = ["Kategori","Nominal"]
        fig_h = go.Figure(go.Bar(
            x=grp_os["Nominal"], y=grp_os["Kategori"], orientation="h",
            marker_color=CHART_PALETTE[:len(grp_os)],
            text=[M(v) for v in grp_os["Nominal"]],
            textposition="outside", textfont=dict(size=10,color="#1E1E1E"),
        ))
        plot_base(fig_h, h=300); fig_h.update_layout(xaxis_tickformat=",")
        st.plotly_chart(fig_h, use_container_width=True)
    with cb2:
        pl=[b for b in BUCKETS if bv[b]>0]
        pv=[bv[b] for b in BUCKETS if bv[b]>0]
        pc=[BUCKET_COLOR[b] for b in BUCKETS if bv[b]>0]
        fig_pie = go.Figure(go.Pie(labels=pl,values=pv,marker_colors=pc,hole=0.55,
            textinfo="percent",textfont_size=11,
            hovertemplate="%{label}: %{value:,.0f}<extra></extra>"))
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            height=300,margin=dict(t=12,b=12,l=0,r=0),showlegend=True,
            legend=dict(font_size=10,x=1.01,y=0.5,xanchor="left"),
            annotations=[dict(text=f"<b>{M(grand)}</b><br><span style='font-size:9px'>Total OS</span>",
                x=0.5,y=0.5,showarrow=False,font=dict(size=14,color="#1E1E1E"))])
        st.plotly_chart(fig_pie, use_container_width=True)

    # ════ WILAYAH & KATEGORI ════
    sec("OUTSTANDING PER WILAYAH & KATEGORI")
    cc2,cd2 = st.columns(2)
    with cc2:
        st.caption("**Per Nama Area**")
        t_area = (dff.groupby("NAMA AREA")
                  .agg(NF=("Nilai Faktur","sum"),Cur=("CURRENT","sum"),Ov=("OVERDUE","sum"))
                  .reset_index().sort_values("NF",ascending=False))
        t_area["% C/OD"]=t_area.apply(lambda r: P(r["Cur"],r["Cur"]+r["Ov"]),axis=1)
        for c in ["NF","Cur","Ov"]: t_area[c]=t_area[c].apply(M)
        t_area.columns=["Nama Area","Nilai Faktur","Current","Overdue","% Curr/OD"]
        st.dataframe(t_area,use_container_width=True,hide_index=True,height=320)
    with cd2:
        st.caption("**Per Kategori Overdue**")
        t_kat=(dff[dff["NOMINAL"]>0].groupby("KATEGORI OVERDUE")
               .agg(Nominal=("NOMINAL","sum"),Faktur=("No Faktur","count"))
               .reset_index().sort_values("Nominal",ascending=False))
        t_kat["%"]=t_kat["Nominal"].apply(lambda v: P(v,tn))
        t_kat["Nominal"]=t_kat["Nominal"].apply(R)
        t_kat.columns=["Kategori Overdue","Nominal","Jml Faktur","%"]
        st.dataframe(t_kat,use_container_width=True,hide_index=True,height=320)
    dw1,dw2=st.columns(2)
    with dw1: dl_btn(dff.groupby("NAMA AREA").agg(NF=("Nilai Faktur","sum"),Cur=("CURRENT","sum"),Ov=("OVERDUE","sum")).reset_index(),"OUTSTANDING_PER_AREA")
    with dw2: dl_btn(dff[dff["NOMINAL"]>0].groupby("KATEGORI OVERDUE").agg(Nominal=("NOMINAL","sum"),Faktur=("No Faktur","count")).reset_index(),"OUTSTANDING_PER_KATEGORI")

    # ════ COLLECTION ════
    sec("COLLECTION — ACTUAL vs TARGET PELUNASAN")
    ce2,cf2=st.columns([5,4])
    with ce2:
        t_coll=(dff.groupby("NAMA AREA").agg(Actual=("ACTUAL PELUNASAN","sum"),Target=("TARGET PELUNASAN","sum")).reset_index())
        t_coll=t_coll[t_coll["Target"]>0].nlargest(12,"Target")
        fig_c=go.Figure()
        fig_c.add_trace(go.Bar(name="Target",x=t_coll["NAMA AREA"],y=t_coll["Target"],marker_color="#D0C8BE",text=[M(v) for v in t_coll["Target"]],textposition="outside",textfont=dict(size=9,color="#555")))
        fig_c.add_trace(go.Bar(name="Actual",x=t_coll["NAMA AREA"],y=t_coll["Actual"],marker_color="#C8192E",text=[M(v) for v in t_coll["Actual"]],textposition="outside",textfont=dict(size=9,color="#C8192E")))
        plot_base(fig_c,h=320)
        fig_c.update_layout(barmode="group",showlegend=True,legend=dict(orientation="h",x=0,y=1.08,font_size=11),xaxis_tickangle=-30,yaxis_tickformat=",")
        st.plotly_chart(fig_c,use_container_width=True)
    with cf2:
        st.caption("**Collection Rate per ASM**")
        t_asm=(dff.groupby("ASM").agg(Actual=("ACTUAL PELUNASAN","sum"),Target=("TARGET PELUNASAN","sum"),OS=("NOMINAL","sum")).reset_index())
        t_asm=t_asm[t_asm["Target"]>0].sort_values("Target",ascending=False)
        t_asm["%Coll"]=t_asm.apply(lambda r: P(r["Actual"],r["Target"]),axis=1)
        for c in ["Actual","Target","OS"]: t_asm[c]=t_asm[c].apply(M)
        t_asm.columns=["ASM","Actual","Target","Outstanding","% Coll"]
        st.dataframe(t_asm,use_container_width=True,hide_index=True,height=320)
    dc1,dc2=st.columns(2)
    with dc1: dl_btn(dff.groupby("NAMA AREA").agg(Actual=("ACTUAL PELUNASAN","sum"),Target=("TARGET PELUNASAN","sum")).reset_index(),"COLLECTION_PER_AREA")
    with dc2: dl_btn(dff.groupby("ASM").agg(Actual=("ACTUAL PELUNASAN","sum"),Target=("TARGET PELUNASAN","sum"),OS=("NOMINAL","sum")).reset_index(),"COLLECTION_PER_ASM")

    # ════ OUTLET & RBM ════
    sec("BREAKDOWN JENIS OUTLET & RBM")
    cg2,ch2=st.columns([4,5])
    with cg2:
        t_out=(dff.groupby("JENIS OUTLET").agg(OS=("NOMINAL","sum"),OV=("OVERDUE","sum")).reset_index().sort_values("OS",ascending=False).head(12))
        t_out["%OD"]=t_out.apply(lambda r: P(r["OV"],r["OS"]),axis=1)
        for c in ["OS","OV"]: t_out[c]=t_out[c].apply(M)
        t_out.columns=["Jenis Outlet","Outstanding","Overdue","%OD"]
        st.dataframe(t_out,use_container_width=True,hide_index=True,height=320)
    with ch2:
        t_rbm=(dff.groupby("RBM").agg(OS=("NOMINAL","sum"),OV=("OVERDUE","sum"),Akt=("ACTUAL PELUNASAN","sum"),Tgt=("TARGET PELUNASAN","sum")).reset_index().sort_values("OS",ascending=False))
        t_rbm["%OD"]=t_rbm.apply(lambda r: P(r["OV"],r["OS"]),axis=1)
        t_rbm["%Coll"]=t_rbm.apply(lambda r: P(r["Akt"],r["Tgt"]),axis=1)
        for c in ["OS","OV","Akt","Tgt"]: t_rbm[c]=t_rbm[c].apply(M)
        t_rbm.columns=["RBM","Outstanding","Overdue","Actual Pel.","Target Pel.","%OD","%Coll"]
        st.dataframe(t_rbm,use_container_width=True,hide_index=True,height=320)
    do1,do2=st.columns(2)
    with do1: dl_btn(dff.groupby("JENIS OUTLET").agg(OS=("NOMINAL","sum"),OV=("OVERDUE","sum")).reset_index(),"BREAKDOWN_OUTLET")
    with do2: dl_btn(dff.groupby("RBM").agg(OS=("NOMINAL","sum"),OV=("OVERDUE","sum"),Akt=("ACTUAL PELUNASAN","sum"),Tgt=("TARGET PELUNASAN","sum")).reset_index(),"BREAKDOWN_RBM")

    # ════ DETAIL FAKTUR ════
    ovrd_ct=int((dff["OVERDUE?"]>0).sum())
    sec(f"DETAIL FAKTUR — {ovrd_ct:,} FAKTUR OVERDUE")
    COLS=["NAMA AREA","RBM","ASM","NAMA SALES","NAMA TOKO","No Faktur","Tanggal Faktur","Tanggal JT","Nilai Faktur","NOMINAL","Saldo Akhir","KELOMPOK","OVERDUE?","GROUPING OS"]
    cols_ok=[c for c in COLS if c in dff.columns]
    tbl=dff[cols_ok].copy()
    if "Tanggal Faktur" in tbl.columns: tbl["Tanggal Faktur"]=tbl["Tanggal Faktur"].dt.strftime("%d %b %Y")
    if "Tanggal JT" in tbl.columns: tbl["Tanggal JT"]=tbl["Tanggal JT"].dt.strftime("%d %b %Y")
    for c in ["Nilai Faktur","Saldo Akhir"]:
        if c in tbl.columns: tbl[c]=tbl[c].apply(R)
    tbl.rename(columns={"NAMA AREA":"Nama Area","NAMA SALES":"Nama Sales","NAMA TOKO":"Nama Toko","Saldo Akhir":"Sisa AR","OVERDUE?":"Hari OD","KELOMPOK":"Kelompok","GROUPING OS":"Grouping OS"},inplace=True)
    tbl.insert(0,"#",range(1,len(tbl)+1))
    with st.expander(f"Tampilkan {len(tbl):,} baris · OS Total: {M(tn)}",expanded=False):
        st.dataframe(tbl,use_container_width=True,hide_index=True,height=440)
        dl_btn(dff[cols_ok],"OS_MTI_NKA_DETAIL","Download Detail Faktur")

# ════════════════════════════════════════════════════════════════════
# PAGE: AR GT
# ════════════════════════════════════════════════════════════════════
def page_gt():
    with st.spinner("Memuat data GT..."):
        df, last_updated = load_gt()

    if df.empty:
        st.warning("Belum ada data OTC. Jalankan **JALANKAN_SEMUA.bat** untuk upload data GT.")
        return

    # ── SIDEBAR ───────────────────────────────────────────────────
    st.sidebar.markdown("### Filter OTC")
    def sb(label, col, src):
        opts = ["Semua"] + sorted(src[col].dropna().unique().tolist())
        return st.sidebar.selectbox(label, opts, key=f"gt_{col}")

    sel_region = sb("Region",       "Region",       df)
    d0 = df if sel_region=="Semua" else df[df["Region"]==sel_region]
    sel_area   = sb("Nama Area",    "Nama Area",    d0)
    d1 = d0 if sel_area=="Semua" else d0[d0["Nama Area"]==sel_area]
    sel_jenis  = sb("Jenis Outlet", "Jenis Outlet", d1)
    sel_asm    = sb("ASM",          "ASM",          d1)
    sel_rbm    = sb("RBM",          "RBM",          d1)
    sel_grp    = sb("Grouping OS",  "Grouping OS",  d1)
    sel_bkt    = st.sidebar.multiselect("Kelompok Aging", BUCKETS, default=BUCKETS, key="gt_bkt")
    st.sidebar.markdown("---")
    if st.sidebar.button("↺ Refresh GT", use_container_width=True, key="ref_gt"):
        st.cache_data.clear(); st.rerun()
    st.sidebar.caption(f"Update GT: {last_updated}")

    dff = df.copy()
    if sel_region!="Semua": dff=dff[dff["Region"]      ==sel_region]
    if sel_area  !="Semua": dff=dff[dff["Nama Area"]   ==sel_area]
    if sel_jenis !="Semua": dff=dff[dff["Jenis Outlet"] ==sel_jenis]
    if sel_asm   !="Semua": dff=dff[dff["ASM"]         ==sel_asm]
    if sel_rbm   !="Semua": dff=dff[dff["RBM"]         ==sel_rbm]
    if sel_grp   !="Semua": dff=dff[dff["Grouping OS"] ==sel_grp]
    if sel_bkt:              dff=dff[dff["KELOMPOK"].isin(sel_bkt)]
    if dff.empty:
        st.warning("Tidak ada data sesuai filter."); return

    pma_header("AR Outstanding GT", last_updated, len(dff))

    # KPI
    tn=dff["Nominal"].sum(); to=dff["OVERDUE"].sum(); tc=dff["CURRENT"].sum()
    ta=dff["ACTUAL PELUNASAN"].sum(); tt=dff["TARGET PELUNASAN"].sum()
    td=dff["DUE DATE"].sum(); tq=int(dff["Qty Faktur"].sum())
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    kpi(c1,"Total Outstanding GT",M(tn),f"Nilai Faktur {M(dff['Nilai Faktur'].sum())}")
    kpi(c2,"Overdue",M(to),P(to,tn)+" dari outstanding")
    kpi(c3,"Current",M(tc),P(tc,tn)+" dari total","green")
    kpi(c4,"% Collection",P(ta,tt),f"Actual {M(ta)} / Target {M(tt)}","gold")
    kpi(c5,"Due Date Hari Ini",M(td),"Nominal jatuh tempo hari ini","stone")
    kpi(c6,"Qty Faktur",f"{tq:,}",f"{len(dff):,} baris data","orange")
    st.markdown("<br>",unsafe_allow_html=True)

    bv, grand = bucket_strip(dff)

    # ════ SO BLOCK — 1 TABEL dengan kolom SO Status, Area, Kode Customer, dll ════
    sec("STATUS SO BLOCK — REKOMENDASI TINDAKAN")

    df_ov = dff[dff["KELOMPOK"]!="CURRENT"].copy()
    df_ov["SO Status"] = df_ov["KELOMPOK"].map(SO_MAP)

    wn = df_ov[df_ov["SO Status"]=="WARNING SO"]["Nominal"].sum()
    sn = df_ov[df_ov["SO Status"]=="SOFT BLOCK"]["Nominal"].sum()
    cn = df_ov[df_ov["SO Status"]=="CRITICAL BLOCK"]["Nominal"].sum()
    wf = (df_ov["SO Status"]=="WARNING SO").sum()
    sf = (df_ov["SO Status"]=="SOFT BLOCK").sum()
    cf = (df_ov["SO Status"]=="CRITICAL BLOCK").sum()
    wa = df_ov[df_ov["SO Status"]=="WARNING SO"]["Nama Area"].nunique()
    sa = df_ov[df_ov["SO Status"]=="SOFT BLOCK"]["Nama Area"].nunique()
    ca = df_ov[df_ov["SO Status"]=="CRITICAL BLOCK"]["Nama Area"].nunique()

    st.markdown(f"""
    <div class="so-wrap">
      <div class="so-card warn">
        <span class="so-tag warn"><span class="so-tag-dot"></span>Warning SO</span>
        <p class="so-val">{M(wn)}</p>
        <p class="so-sub">{wf:,} faktur · {wa} area</p>
        <p class="so-desc">1–7 hari & 8–30 hari — segera follow up</p>
      </div>
      <div class="so-card soft">
        <span class="so-tag soft"><span class="so-tag-dot"></span>Soft Block</span>
        <p class="so-val">{M(sn)}</p>
        <p class="so-sub">{sf:,} faktur · {sa} area</p>
        <p class="so-desc">31–60 & 61–90 hari — hold pengiriman baru</p>
      </div>
      <div class="so-card crit">
        <span class="so-tag crit"><span class="so-tag-dot"></span>Critical Block</span>
        <p class="so-val">{M(cn)}</p>
        <p class="so-sub">{cf:,} faktur · {ca} area</p>
        <p class="so-desc">91+ hari & &lt;2026 — blokir SO, eskalasi manajemen</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # SATU TABEL SO BLOCK — kolom: Status | Area | Nama Toko | ASM | RBM | No Faktur | Qty | Nilai Faktur
    # Kode Customer = No Faktur SAP (identitas customer di SAP)
    so_cols_src = {
        "SO Status":     "SO Status",
        "Nama Area":     "Nama Area",
        "Kode Customer": "No Faktur SAP",
        "Nama Toko":     "Nama Toko",
        "ASM":           "ASM",
        "RBM":           "RBM",
        "No Faktur":     "No Faktur",
        "Kelompok":      "KELOMPOK",
    }
    tbl_so = df_ov.copy()
    # Qty faktur per toko per SO Status — dibangun dari groupby
    so_out_cols = ["SO Status","Nama Area","No Faktur SAP","Nama Toko","ASM","RBM",
                   "No Faktur","KELOMPOK","Nominal","Nilai Faktur"]
    so_out_cols = [c for c in so_out_cols if c in tbl_so.columns]
    tbl_so = tbl_so[so_out_cols].copy()

    # Tambah kolom Qty Faktur per Nama Toko
    qty_map = tbl_so.groupby("Nama Toko")["No Faktur"].transform("count") if "Nama Toko" in tbl_so.columns else 0
    tbl_so.insert(tbl_so.columns.get_loc("No Faktur")+1 if "No Faktur" in tbl_so.columns else len(tbl_so.columns),
                  "Qty Faktur", qty_map)

    # Format angka
    for c in ["Nominal","Nilai Faktur"]:
        if c in tbl_so.columns: tbl_so[c] = tbl_so[c].apply(M)

    # Rename kolom akhir
    rename_map = {
        "SO Status":"SO Status","Nama Area":"Nama Area","No Faktur SAP":"Kode Customer",
        "Nama Toko":"Nama Toko","ASM":"ASM","RBM":"RBM",
        "No Faktur":"No Faktur","Qty Faktur":"Qty Faktur",
        "Nominal":"Nilai OS","Nilai Faktur":"Nilai Faktur","KELOMPOK":"Kelompok",
    }
    tbl_so.rename(columns=rename_map, inplace=True)
    tbl_so.insert(0,"#",range(1,len(tbl_so)+1))

    # Urutkan: Critical dulu, lalu Soft Block, lalu Warning SO
    order = {"CRITICAL BLOCK":0,"SOFT BLOCK":1,"WARNING SO":2}
    if "SO Status" in tbl_so.columns:
        tbl_so["_ord"] = tbl_so["SO Status"].map(order).fillna(3)
        tbl_so = tbl_so.sort_values("_ord").drop(columns="_ord")

    st.dataframe(tbl_so, use_container_width=True, hide_index=True, height=400)
    dl_btn(df_ov[so_out_cols], "GT_SO_BLOCK_DETAIL", "Download SO Block GT")

    # Chart distribusi SO Block per area (top 10)
    sec("DISTRIBUSI SO BLOCK PER NAMA AREA")
    pivot = (df_ov.groupby(["Nama Area","SO Status"])["Nominal"]
             .sum().unstack(fill_value=0).reset_index())
    for k in ["WARNING SO","SOFT BLOCK","CRITICAL BLOCK"]:
        if k not in pivot.columns: pivot[k]=0
    pivot["TOTAL"] = pivot[["WARNING SO","SOFT BLOCK","CRITICAL BLOCK"]].sum(axis=1)
    pivot = pivot.nlargest(10,"TOTAL")
    fig_so = go.Figure()
    for col_key,color,name in [
        ("CRITICAL BLOCK","#C8192E","Critical Block"),
        ("SOFT BLOCK","#E65C00","Soft Block"),
        ("WARNING SO","#F5A623","Warning SO"),
    ]:
        if col_key in pivot.columns:
            fig_so.add_trace(go.Bar(
                name=name, x=pivot["Nama Area"], y=pivot[col_key],
                marker_color=color,
                text=pivot[col_key].apply(lambda v: M(v) if v>0 else ""),
                textposition="inside", textfont=dict(size=9,color="#fff"),
            ))
    plot_base(fig_so, h=340)
    fig_so.update_layout(barmode="stack",showlegend=True,
        legend=dict(orientation="h",x=0,y=1.06,font_size=11),
        xaxis_tickangle=-30,yaxis_tickformat=",")
    st.plotly_chart(fig_so, use_container_width=True)

    # ════ KOMPOSISI ════
    sec("KOMPOSISI OUTSTANDING")
    ca2,cb2 = st.columns([5,4])
    with ca2:
        grp_os = (dff[dff["Nominal"]>0].groupby("Grouping OS")["Nominal"]
                  .sum().sort_values().reset_index())
        grp_os.columns = ["Kategori","Nominal"]
        fig_h = go.Figure(go.Bar(
            x=grp_os["Nominal"], y=grp_os["Kategori"], orientation="h",
            marker_color=CHART_PALETTE[:len(grp_os)],
            text=[M(v) for v in grp_os["Nominal"]],
            textposition="outside", textfont=dict(size=10,color="#1E1E1E"),
        ))
        plot_base(fig_h, h=300); fig_h.update_layout(xaxis_tickformat=",")
        st.plotly_chart(fig_h, use_container_width=True)
    with cb2:
        pl=[b for b in BUCKETS if bv[b]>0]
        pv=[bv[b] for b in BUCKETS if bv[b]>0]
        pc=[BUCKET_COLOR[b] for b in BUCKETS if bv[b]>0]
        fig_pie = go.Figure(go.Pie(labels=pl,values=pv,marker_colors=pc,hole=0.55,
            textinfo="percent",textfont_size=11,
            hovertemplate="%{label}: %{value:,.0f}<extra></extra>"))
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            height=300,margin=dict(t=12,b=12,l=0,r=0),showlegend=True,
            legend=dict(font_size=10,x=1.01,y=0.5,xanchor="left"),
            annotations=[dict(text=f"<b>{M(grand)}</b><br><span style='font-size:9px'>Total OS</span>",
                x=0.5,y=0.5,showarrow=False,font=dict(size=14,color="#1E1E1E"))])
        st.plotly_chart(fig_pie, use_container_width=True)

    # ════ WILAYAH & KATEGORI ════
    sec("OUTSTANDING PER WILAYAH & KATEGORI")
    cc2,cd2 = st.columns(2)
    with cc2:
        st.caption("**Per Nama Area**")
        t_area = (dff.groupby("Nama Area")
                  .agg(NF=("Nilai Faktur","sum"),Cur=("CURRENT","sum"),Ov=("OVERDUE","sum"))
                  .reset_index().sort_values("NF",ascending=False))
        t_area["% C/OD"]=t_area.apply(lambda r: P(r["Cur"],r["Cur"]+r["Ov"]),axis=1)
        for c in ["NF","Cur","Ov"]: t_area[c]=t_area[c].apply(M)
        t_area.columns=["Nama Area","Nilai Faktur","Current","Overdue","% Curr/OD"]
        st.dataframe(t_area,use_container_width=True,hide_index=True,height=320)
    with cd2:
        st.caption("**Per Kategori Overdue**")
        t_kat=(dff[dff["Nominal"]>0].groupby("Kategori Overdue")
               .agg(Nominal=("Nominal","sum"),Faktur=("No Faktur","count"))
               .reset_index().sort_values("Nominal",ascending=False))
        t_kat["%"]=t_kat["Nominal"].apply(lambda v: P(v,tn))
        t_kat["Nominal"]=t_kat["Nominal"].apply(R)
        t_kat.columns=["Kategori Overdue","Nominal","Jml Faktur","%"]
        st.dataframe(t_kat,use_container_width=True,hide_index=True,height=320)
    dw1,dw2=st.columns(2)
    with dw1: dl_btn(dff.groupby("Nama Area").agg(NF=("Nilai Faktur","sum"),Cur=("CURRENT","sum"),Ov=("OVERDUE","sum")).reset_index(),"GT_OUTSTANDING_PER_AREA")
    with dw2: dl_btn(dff[dff["Nominal"]>0].groupby("Kategori Overdue").agg(Nominal=("Nominal","sum"),Faktur=("No Faktur","count")).reset_index(),"GT_OUTSTANDING_PER_KATEGORI")

    # ════ COLLECTION ════
    sec("COLLECTION — ACTUAL vs TARGET PELUNASAN")
    ce2,cf2=st.columns([5,4])
    with ce2:
        t_coll=(dff.groupby("Nama Area").agg(Actual=("ACTUAL PELUNASAN","sum"),Target=("TARGET PELUNASAN","sum")).reset_index())
        t_coll=t_coll[t_coll["Target"]>0].nlargest(12,"Target")
        fig_c=go.Figure()
        fig_c.add_trace(go.Bar(name="Target",x=t_coll["Nama Area"],y=t_coll["Target"],marker_color="#D0C8BE",text=[M(v) for v in t_coll["Target"]],textposition="outside",textfont=dict(size=9,color="#555")))
        fig_c.add_trace(go.Bar(name="Actual",x=t_coll["Nama Area"],y=t_coll["Actual"],marker_color="#C8192E",text=[M(v) for v in t_coll["Actual"]],textposition="outside",textfont=dict(size=9,color="#C8192E")))
        plot_base(fig_c,h=320)
        fig_c.update_layout(barmode="group",showlegend=True,legend=dict(orientation="h",x=0,y=1.08,font_size=11),xaxis_tickangle=-30,yaxis_tickformat=",")
        st.plotly_chart(fig_c,use_container_width=True)
    with cf2:
        st.caption("**Collection Rate per ASM**")
        t_asm=(dff.groupby("ASM").agg(Actual=("ACTUAL PELUNASAN","sum"),Target=("TARGET PELUNASAN","sum"),OS=("Nominal","sum")).reset_index())
        t_asm=t_asm[t_asm["Target"]>0].sort_values("Target",ascending=False)
        t_asm["%Coll"]=t_asm.apply(lambda r: P(r["Actual"],r["Target"]),axis=1)
        for c in ["Actual","Target","OS"]: t_asm[c]=t_asm[c].apply(M)
        t_asm.columns=["ASM","Actual","Target","Outstanding","% Coll"]
        st.dataframe(t_asm,use_container_width=True,hide_index=True,height=320)
    dc1,dc2=st.columns(2)
    with dc1: dl_btn(dff.groupby("Nama Area").agg(Actual=("ACTUAL PELUNASAN","sum"),Target=("TARGET PELUNASAN","sum")).reset_index(),"GT_COLLECTION_PER_AREA")
    with dc2: dl_btn(dff.groupby("ASM").agg(Actual=("ACTUAL PELUNASAN","sum"),Target=("TARGET PELUNASAN","sum"),OS=("Nominal","sum")).reset_index(),"GT_COLLECTION_PER_ASM")

    # ════ OUTLET & RBM ════
    sec("BREAKDOWN JENIS OUTLET & RBM")
    cg2,ch2=st.columns([4,5])
    with cg2:
        t_out=(dff.groupby("Jenis Outlet").agg(OS=("Nominal","sum"),OV=("OVERDUE","sum")).reset_index().sort_values("OS",ascending=False).head(12))
        t_out["%OD"]=t_out.apply(lambda r: P(r["OV"],r["OS"]),axis=1)
        for c in ["OS","OV"]: t_out[c]=t_out[c].apply(M)
        t_out.columns=["Jenis Outlet","Outstanding","Overdue","%OD"]
        st.dataframe(t_out,use_container_width=True,hide_index=True,height=320)
    with ch2:
        t_rbm=(dff.groupby("RBM").agg(OS=("Nominal","sum"),OV=("OVERDUE","sum"),Akt=("ACTUAL PELUNASAN","sum"),Tgt=("TARGET PELUNASAN","sum")).reset_index().sort_values("OS",ascending=False))
        t_rbm["%OD"]=t_rbm.apply(lambda r: P(r["OV"],r["OS"]),axis=1)
        t_rbm["%Coll"]=t_rbm.apply(lambda r: P(r["Akt"],r["Tgt"]),axis=1)
        for c in ["OS","OV","Akt","Tgt"]: t_rbm[c]=t_rbm[c].apply(M)
        t_rbm.columns=["RBM","Outstanding","Overdue","Actual Pel.","Target Pel.","%OD","%Coll"]
        st.dataframe(t_rbm,use_container_width=True,hide_index=True,height=320)
    do1,do2=st.columns(2)
    with do1: dl_btn(dff.groupby("Jenis Outlet").agg(OS=("Nominal","sum"),OV=("OVERDUE","sum")).reset_index(),"GT_BREAKDOWN_OUTLET")
    with do2: dl_btn(dff.groupby("RBM").agg(OS=("Nominal","sum"),OV=("OVERDUE","sum"),Akt=("ACTUAL PELUNASAN","sum"),Tgt=("TARGET PELUNASAN","sum")).reset_index(),"GT_BREAKDOWN_RBM")

    # ════ DETAIL FAKTUR ════
    ovrd_ct=int((dff["OVERDUE?"]>0).sum())
    sec(f"DETAIL FAKTUR — {ovrd_ct:,} FAKTUR OVERDUE")
    COLS=["Nama Area","RBM","ASM","Nama Sales","Nama Toko","No Faktur","Tanggal Faktur","Tanggal JT","Nilai Faktur","Nominal","Saldo Akhir","KELOMPOK","OVERDUE?","Grouping OS"]
    cols_ok=[c for c in COLS if c in dff.columns]
    tbl=dff[cols_ok].copy()
    if "Tanggal Faktur" in tbl.columns: tbl["Tanggal Faktur"]=tbl["Tanggal Faktur"].dt.strftime("%d %b %Y")
    if "Tanggal JT" in tbl.columns: tbl["Tanggal JT"]=tbl["Tanggal JT"].dt.strftime("%d %b %Y")
    for c in ["Nilai Faktur","Saldo Akhir"]:
        if c in tbl.columns: tbl[c]=tbl[c].apply(R)
    tbl.rename(columns={"Nama Area":"Nama Area","Nama Sales":"Nama Sales","Nama Toko":"Nama Toko","Saldo Akhir":"Sisa AR","OVERDUE?":"Hari OD","KELOMPOK":"Kelompok","Grouping OS":"Grouping OS"},inplace=True)
    tbl.insert(0,"#",range(1,len(tbl)+1))
    with st.expander(f"Tampilkan {len(tbl):,} baris · OS Total: {M(tn)}",expanded=False):
        st.dataframe(tbl,use_container_width=True,hide_index=True,height=440)
        dl_btn(dff[cols_ok],"GT_DETAIL","Download Detail Faktur GT")

# ════════════════════════════════════════════════════════════════════


# ═══════════════════════════════════════════════════════════════
# AUTH — Login dengan NIK + Password
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600, show_spinner=False)
def load_users() -> dict:
    """Ambil daftar user dari tabel app_users di Supabase."""
    try:
        sb   = get_sb()
        resp = sb.table("app_users").select("nik,nama,password").execute()
        return {r["nik"]: r for r in (resp.data or [])}
    except Exception:
        return {}


def check_login() -> bool:
    """
    Tampilkan halaman login jika belum login.
    Return True jika sudah login, False jika belum.
    """
    # Sudah login → langsung lanjut
    if st.session_state.get("logged_in"):
        return True

    # ── Halaman Login ────────────────────────────────────────────
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: #FFFFFF; }
    .login-wrap {
        max-width: 400px;
        margin: 80px auto 0;
        padding: 40px 36px 32px;
        background: #FFFFFF;
        border: 1px solid #ECECEC;
        border-radius: 18px;
        box-shadow: 0 4px 24px rgba(0,0,0,.07);
    }
    .login-logo {
        width: 42px; height: 42px;
        background: #B01C2E;
        border-radius: 10px;
        margin: 0 auto 20px;
        display: flex; align-items: center; justify-content: center;
    }
    .login-title {
        font-size: 18px; font-weight: 700;
        color: #111827; text-align: center;
        margin: 0 0 4px;
    }
    .login-sub {
        font-size: 12px; color: #9CA3AF;
        text-align: center; margin: 0 0 28px;
    }
    .login-error {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 12.5px;
        color: #991B1B;
        margin-bottom: 14px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-wrap">
      <div class="login-logo">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
             stroke="#fff" stroke-width="2" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round"
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
        </svg>
      </div>
      <p class="login-title">AR Dashboard</p>
      <p class="login-sub">PT Pinus Merah Abadi · FAD Team</p>
    </div>
    """, unsafe_allow_html=True)

    # Form login — letakkan di bawah card HTML karena Streamlit form
    # harus di dalam Python component
    with st.container():
        col_pad1, col_form, col_pad2 = st.columns([1, 2, 1])
        with col_form:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            nik  = st.text_input("NIK", placeholder="Masukkan NIK Anda",
                                  key="login_nik", label_visibility="visible")
            pwd  = st.text_input("Password", type="password",
                                  placeholder="Masukkan password",
                                  key="login_pwd", label_visibility="visible")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            login_btn = st.button("Masuk", use_container_width=True,
                                   key="login_btn", type="primary")

            if login_btn:
                users = load_users()
                if not nik.strip():
                    st.markdown("<div class='login-error'>NIK tidak boleh kosong.</div>",
                                unsafe_allow_html=True)
                elif nik.strip() not in users:
                    st.markdown("<div class='login-error'>NIK tidak ditemukan.</div>",
                                unsafe_allow_html=True)
                elif users[nik.strip()]["password"] != pwd.strip():
                    st.markdown("<div class='login-error'>Password salah.</div>",
                                unsafe_allow_html=True)
                else:
                    user = users[nik.strip()]
                    st.session_state["logged_in"]   = True
                    st.session_state["user_nik"]    = nik.strip()
                    st.session_state["user_nama"]   = user["nama"]
                    st.rerun()

    return False


def render_change_password():
    """
    Panel ganti password — ditampilkan di sidebar bawah setelah login.
    Verifikasi password lama → update ke Supabase.
    """
    with st.sidebar.expander("Ganti Password", expanded=False):
        pwd_lama  = st.text_input("Password lama", type="password", key="cp_old")
        pwd_baru  = st.text_input("Password baru", type="password", key="cp_new")
        pwd_konfirm = st.text_input("Konfirmasi password baru", type="password", key="cp_confirm")
        ganti_btn = st.button("Simpan", use_container_width=True, key="cp_btn")

        if ganti_btn:
            nik   = st.session_state.get("user_nik", "")
            users = load_users()
            user  = users.get(nik)

            if not all([pwd_lama, pwd_baru, pwd_konfirm]):
                st.error("Semua kolom wajib diisi.")
            elif user is None:
                st.error("Session tidak valid, silakan login ulang.")
            elif user["password"] != pwd_lama.strip():
                st.error("Password lama salah.")
            elif len(pwd_baru.strip()) < 6:
                st.error("Password baru minimal 6 karakter.")
            elif pwd_baru.strip() != pwd_konfirm.strip():
                st.error("Konfirmasi password tidak cocok.")
            else:
                try:
                    sb = get_sb()
                    sb.table("app_users").update(
                        {"password": pwd_baru.strip()}
                    ).eq("nik", nik).execute()
                    # Clear cache user agar password baru langsung berlaku
                    load_users.clear()
                    st.success("Password berhasil diperbarui.")
                except Exception as e:
                    st.error(f"Gagal menyimpan: {e}")


def main():
    if not check_login():
        return

    # Tombol logout di sidebar
    with st.sidebar:
        nama = st.session_state.get("user_nama", "")
        nik  = st.session_state.get("user_nik", "")
        st.markdown(
            f"<div style='padding:10px 0 6px;font-size:12px;color:#374151'>"
            f"<div style='font-weight:600'>{nama}</div>"
            f"<div style='color:#9CA3AF;font-size:11px'>NIK {nik}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        if st.button("Keluar", use_container_width=True, key="logout_btn"):
            for k in ["logged_in","user_nik","user_nama"]:
                st.session_state.pop(k, None)
            st.rerun()
        st.markdown("<hr style='margin:8px 0;border-color:#ECECEC'>", unsafe_allow_html=True)

    render_change_password()

    tab1, tab2 = st.tabs(["AR OTC — MTI NKA", "AR GT"])
    with tab1:
        page_otc()
    with tab2:
        page_gt()

if __name__ == "__main__":
    main()
