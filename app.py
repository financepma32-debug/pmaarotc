"""
AR OTC + AR GT Dashboard — PT Pinus Merah Abadi | FAD Team
Fix: header tidak terpotong, timestamp realtime, SO Block 1 tabel, menu GT
Supabase: project pma-arotc — tabel os_master (OTC) | bucket arotcgt (GT)
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client
from datetime import datetime, timezone, timedelta

WIB = timezone(timedelta(hours=7))  # Asia/Jakarta, UTC+7 (tanpa DST)

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
    background: #111827 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 500;
    padding: 8px 0;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #1F2937 !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] .stButton button p,
[data-testid="stSidebar"] .stButton button span {
    color: #FFFFFF !important;
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

/* ── Ranking RBM/KAM table ─────────────────────────── */
.rbm-table-wrap {
    overflow-x: auto;
    border: 1.5px solid #D1D5DB;
    border-radius: 12px;
    margin-bottom: 28px;
}
.rbm-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.rbm-table th, .rbm-table td {
    padding: 9px 12px;
    text-align: center;
    border-bottom: 1px solid #D1D5DB;
    border-right: 1px solid #E5E7EB;
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
}
.rbm-table th:last-child, .rbm-table td:last-child { border-right: none; }
.rbm-table thead th {
    font-size: 10.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .4px;
    color: #6B7280;
    background: #F3F4F6;
    border-bottom: 1.5px solid #9CA3AF;
    border-right: 1px solid #D1D5DB;
}
.rbm-table td:first-child, .rbm-table th:first-child {
    text-align: left;
    font-weight: 600;
    color: #111827;
}
.rbm-table tbody tr:last-child td { border-bottom: none; }
.rbm-th-blue   { background: #F3F4F6 !important; color: #6B7280 !important; }
.rbm-th-amber  { background: #F3F4F6 !important; color: #6B7280 !important; }

/* Varian scroll — tampilin ~10 baris, sisanya scroll di dalam box */
.rbm-table-wrap.scroll-box { max-height: 470px; overflow-y: auto; }
.rbm-table-wrap.scroll-box .rbm-table thead th { position: sticky; z-index: 2; height: 36px; box-sizing: border-box; }
.rbm-table-wrap.scroll-box .rbm-table thead tr:first-child th { top: 0; z-index: 3; }
.rbm-table-wrap.scroll-box .rbm-table thead tr:last-child th  { top: 36px; z-index: 2; }
.rbm-table-wrap.scroll-box .rbm-table thead tr:only-child th  { top: 0; z-index: 3; }

/* ── Tabel detail per Kode Customer — kolom beku (freeze) ─── */
.cust-table-wrap {
    overflow-x: auto;
    overflow-y: auto;
    max-height: 460px;
    border: 1.5px solid #D1D5DB;
    border-radius: 12px;
    margin-bottom: 28px;
}
.cust-table thead th { position: sticky; z-index: 2; height: 36px; box-sizing: border-box; }
.cust-table thead tr:first-child th { top: 0; z-index: 3; }
.cust-table thead tr:last-child th  { top: 36px; z-index: 2; }
.cust-table thead tr:only-child th  { top: 0; z-index: 3; }
.cust-table thead th.cust-frz { z-index: 5; }
.cust-table thead tr:first-child th.cust-frz { z-index: 6; }
.cust-table { width: 100%; min-width: 1410px; table-layout: fixed; border-collapse: collapse; font-size: 12.5px; }
.cust-table th, .cust-table td {
    padding: 9px 12px;
    text-align: center;
    border-bottom: 1px solid #D1D5DB;
    border-right: 1px solid #E5E7EB;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-variant-numeric: tabular-nums;
}
.cust-table th:last-child, .cust-table td:last-child { border-right: none; }
.cust-table thead th {
    font-size: 10.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .4px;
    color: #6B7280;
    background: #F3F4F6;
    border-bottom: 1.5px solid #9CA3AF;
    border-right: 1px solid #D1D5DB;
}
.cust-table tbody tr:last-child td { border-bottom: none; }

/* Nama Outlet — boleh wrap ke baris baru di antara kata (bukan per huruf) */
.cust-table td.cust-outlet, .cust-table th.cust-outlet {
    white-space: normal;
    overflow-wrap: normal;
    text-overflow: clip;
    text-align: left;
}
.cust-table td.cust-kode, .cust-table th.cust-kode { text-align: left; font-weight: 600; color: #111827; }

/* Freeze No, Kode Customer, Nama Outlet, Grouping Outlet */
.cust-table th.cust-frz, .cust-table td.cust-frz {
    position: sticky;
    background: #FFFFFF;
    z-index: 1;
}
.cust-table thead th.cust-frz { background: #F9FAFB; z-index: 3; }
.cust-table td.cust-frz-0, .cust-table th.cust-frz-0 { left: 0px;   width: 50px;  }
.cust-table td.cust-frz-1, .cust-table th.cust-frz-1 { left: 50px;  width: 110px; }
.cust-table td.cust-frz-2, .cust-table th.cust-frz-2 { left: 160px; width: 170px; }
.cust-table td.cust-frz-3, .cust-table th.cust-frz-3 { left: 330px; width: 150px;
    box-shadow: 3px 0 6px -2px rgba(0,0,0,0.12); }

/* ── Tabel detail rekonsiliasi Sampling EO — SPLIT 2 tabel (bukan sticky) ─── */
/* Kiri = kolom freeze (No..Sisa AR), Kanan = kolom scroll, digabung 1 scroll vertikal bareng */
.eo-split-wrap {
    display: flex;
    align-items: flex-start;
    max-height: 460px;
    overflow: auto;
    border: 1.5px solid #D1D5DB;
    border-radius: 12px;
    margin-bottom: 28px;
}
.eo-frozen-col { flex: 0 0 auto; position: sticky; left: 0; z-index: 5; background: #FFFFFF; }
.eo-scroll-col { flex: 0 0 auto; }
.eo-tbl { border-collapse: collapse; font-size: 12.5px; table-layout: fixed; }
.eo-tbl th, .eo-tbl td {
    box-sizing: border-box;
    padding: 9px 14px;
    text-align: center;
    border-bottom: 1px solid #D1D5DB;
    border-right: 1px solid #E5E7EB;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    font-variant-numeric: tabular-nums;
    height: 40px;
}
.eo-tbl th:last-child, .eo-tbl td:last-child { border-right: none; }
.eo-tbl thead th {
    position: sticky;
    top: 0;
    z-index: 2;
    font-size: 10.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .4px;
    color: #6B7280;
    background: #F3F4F6;
    border-bottom: 1.5px solid #9CA3AF;
    border-right: 1px solid #D1D5DB;
}
.eo-tbl tbody tr:last-child td { border-bottom: none; }
.eo-tbl td.eo-area, .eo-tbl th.eo-area { text-align: left; font-weight: 600; color: #111827; }
.eo-frozen-col .eo-tbl { border-right: 1.5px solid #D1D5DB; box-shadow: 3px 0 6px -2px rgba(0,0,0,0.12); }
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
    "Kode Customer","PIC","Deadline","KET",
]

# GT — kolom dari gt_to_master.py
GT_NUMERIC = {
    "Nominal","Nilai Faktur","Movement","Saldo Akhir",
    "CURRENT","1-7 DAYS","8-30 DAYS","31-60 DAYS","61-90 DAYS",
    "91-120 DAYS","121+ DAYS","<2026",
    "OVERDUE","OVERDUE?","ACTUAL PELUNASAN","TARGET PELUNASAN","DUE DATE","Qty Faktur",
    "NILAI DN KLAIM","NOMINAL BAYAR 2",
}
GT_DATE = {"Tanggal Faktur","Tanggal JT","Tgl Target Pelunasan","TANGGAL HARI INII","batas 2025",
           "TGL BAYAR KE FINANCE","DEADLINE"}
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
    "NILAI DN KLAIM","NO SURKOM","NO DN AREA","KURANG KELENGKAPAN 1",
    "TGL BAYAR KE FINANCE","NOMINAL BAYAR 2","NO PO","NO SURAT JALAN",
    "DEADLINE","PJ/PIC","PELAKU","STATUS KLAIM","PRINCIPAL","Kode Customer",
]

# ── FORMAT ───────────────────────────────────────────────────────────────────
def M(v):
    v = float(v)
    if abs(v)>=1_000_000_000: return f"{v/1_000_000_000:.2f}".replace(".",",") + "M"
    if abs(v)>=1_000_000:     return f"{v/1_000_000:.1f}".replace(".",",") + "Jt"
    return f"{v:,.0f}"
def R(v): return f"{float(v):,.0f}"
def P(n,d): return f"{n/d*100:.1f}%" if d else "–"
def D(v):
    """Format angka BUKAN uang (qty/jumlah baris) — pemisah ribuan pakai titik, cth: 46.482"""
    return f"{int(round(float(v))):,}".replace(",",".")

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
                dt_wib = dt.astimezone(WIB)
                last_updated = dt_wib.strftime("%d %b %Y · %H:%M WIB")
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
                dt_wib = dt.astimezone(WIB)
                last_updated = dt_wib.strftime("%d %b %Y · %H:%M WIB")
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
        <span>{D(n_faktur)} faktur ditampilkan</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── RANKING RBM/KAM — tabel header 2 lapis (Current/Overdue vs Collection) ──
def render_rbm_ranking_table(dff):
    if "RBM" not in dff.columns or dff.empty:
        st.info("Data RBM/KAM tidak tersedia.")
        return

    g = dff.groupby("RBM", dropna=False).agg(
        nilai_faktur=("Nilai Faktur", "sum"),
        current=("CURRENT", "sum"),
        overdue=("OVERDUE", "sum"),
        sisa_ar=("NOMINAL", "sum"),
        actual=("ACTUAL PELUNASAN", "sum"),
        target=("TARGET PELUNASAN", "sum"),
    ).reset_index()
    g["RBM"] = g["RBM"].fillna("–").replace("", "–")
    g["pct_od"]   = g.apply(lambda r: (r["overdue"]/r["sisa_ar"]*100) if r["sisa_ar"] else 0, axis=1)
    g["pct_coll"] = g.apply(lambda r: (r["actual"]/r["target"]*100) if r["target"] else 0, axis=1)
    g = g.sort_values("pct_od", ascending=False)

    rows_html = ""
    for i, r in enumerate(g.itertuples(), start=1):
        rows_html += (
            "<tr>"
            f"<td>{i}</td>"
            f"<td>{r.RBM}</td>"
            f"<td>{M(r.nilai_faktur)}</td>"
            f"<td>{M(r.current)}</td>"
            f"<td>{M(r.overdue)}</td>"
            f"<td>{M(r.sisa_ar)}</td>"
            f"<td>{r.pct_od:.2f}%</td>"
            f"<td>{M(r.actual)}</td>"
            f"<td>{M(r.target)}</td>"
            f"<td>{r.pct_coll:.2f}%</td>"
            "</tr>"
        )

    st.markdown(f"""
    <div class="rbm-table-wrap">
    <table class="rbm-table">
    <thead>
    <tr>
        <th rowspan="2">No</th>
        <th rowspan="2">RBM/KAM</th>
        <th rowspan="2">Nilai Faktur</th>
        <th colspan="4" class="rbm-th-blue">Sisa AR Current Vs Overdue</th>
        <th colspan="3" class="rbm-th-amber">Collection AR Overdue</th>
    </tr>
    <tr>
        <th class="rbm-th-blue">Current</th>
        <th class="rbm-th-blue">Overdue</th>
        <th class="rbm-th-blue">Sisa AR</th>
        <th class="rbm-th-blue">%OD</th>
        <th class="rbm-th-amber">Actual Pelunasan</th>
        <th class="rbm-th-amber">Target Pelunasan</th>
        <th class="rbm-th-amber">%Coll</th>
    </tr>
    </thead>
    <tbody>
    {rows_html}
    </tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)


# ── OUTSTANDING BY AREA (GT) — Nama Area, RBM, ROM, Nilai Faktur, Current/Overdue/Sisa AR/%OD ──
def render_area_ranking_table(dff):
    needed = ["Nama Area","RBM","ASM"]
    if not all(c in dff.columns for c in needed) or dff.empty:
        st.info("Data Nama Area tidak tersedia.")
        return

    g = dff.groupby(needed, dropna=False).agg(
        nilai_faktur=("Nilai Faktur", "sum"),
        current=("CURRENT", "sum"),
        overdue=("OVERDUE", "sum"),
        sisa_ar=("Nominal", "sum"),
    ).reset_index()
    for c in needed:
        g[c] = g[c].fillna("–").replace("", "–")
    g["pct_od"] = g.apply(lambda r: (r["overdue"]/r["sisa_ar"]*100) if r["sisa_ar"] else 0, axis=1)
    g = g.sort_values("sisa_ar", ascending=False)

    rows_html = ""
    for i, row in enumerate(g.itertuples(index=False), start=1):
        r = dict(zip(g.columns, row))
        rows_html += (
            "<tr>"
            f"<td>{i}</td>"
            f"<td>{r['Nama Area']}</td>"
            f"<td>{r['RBM']}</td>"
            f"<td>{r['ASM']}</td>"
            f"<td>{M(r['nilai_faktur'])}</td>"
            f"<td>{M(r['current'])}</td>"
            f"<td>{M(r['overdue'])}</td>"
            f"<td>{M(r['sisa_ar'])}</td>"
            f"<td>{r['pct_od']:.2f}%</td>"
            "</tr>"
        )

    st.markdown(f"""
    <div class="rbm-table-wrap scroll-box">
    <table class="rbm-table">
    <thead>
    <tr>
        <th rowspan="2">No</th>
        <th rowspan="2">Nama Area</th>
        <th rowspan="2">RBM</th>
        <th rowspan="2">ROM</th>
        <th rowspan="2">Nilai Faktur</th>
        <th colspan="4" class="rbm-th-blue">Sisa AR Current Vs Overdue</th>
    </tr>
    <tr>
        <th class="rbm-th-blue">Current</th>
        <th class="rbm-th-blue">Overdue</th>
        <th class="rbm-th-blue">Sisa AR</th>
        <th class="rbm-th-blue">%OD</th>
    </tr>
    </thead>
    <tbody>
    {rows_html}
    </tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)


# ── RINGKASAN PER RBM/KAM (GT) — RBM(I), Nilai Faktur(O), Current(AH), Overdue(AQ), Sisa AR(G), Actual(AU), Target(AV) ──
def render_rbm_kam_table(dff):
    needed = ["RBM"]
    if not all(c in dff.columns for c in needed) or dff.empty:
        st.info("Data RBM/KAM tidak tersedia.")
        return

    g = dff.groupby(needed, dropna=False).agg(
        nilai_faktur=("Nilai Faktur", "sum"),
        current=("CURRENT", "sum"),
        overdue=("OVERDUE", "sum"),
        sisa_ar=("Nominal", "sum"),
        actual=("ACTUAL PELUNASAN", "sum"),
        target=("TARGET PELUNASAN", "sum"),
    ).reset_index()
    for c in needed:
        g[c] = g[c].fillna("–").replace("", "–")
    g["pct_od"]   = g.apply(lambda r: (r["overdue"]/r["sisa_ar"]*100) if r["sisa_ar"] else 0, axis=1)
    g["pct_coll"] = g.apply(lambda r: (r["actual"]/r["target"]*100) if r["target"] else 0, axis=1)
    g = g.sort_values("pct_od", ascending=False)

    rows_html = ""
    for i, row in enumerate(g.itertuples(index=False), start=1):
        r = dict(zip(g.columns, row))
        rows_html += (
            "<tr>"
            f"<td>{i}</td>"
            f"<td>{r['RBM']}</td>"
            f"<td>{M(r['nilai_faktur'])}</td>"
            f"<td>{M(r['current'])}</td>"
            f"<td>{M(r['overdue'])}</td>"
            f"<td>{M(r['sisa_ar'])}</td>"
            f"<td>{r['pct_od']:.2f}%</td>"
            f"<td>{M(r['actual'])}</td>"
            f"<td>{M(r['target'])}</td>"
            f"<td>{r['pct_coll']:.2f}%</td>"
            "</tr>"
        )

    st.markdown(f"""
    <div class="rbm-table-wrap scroll-box">
    <table class="rbm-table">
    <thead>
    <tr>
        <th rowspan="2">No</th>
        <th rowspan="2">RBM/KAM</th>
        <th rowspan="2">Nilai Faktur</th>
        <th colspan="4" class="rbm-th-blue">Sisa AR Current Vs Overdue</th>
        <th colspan="3" class="rbm-th-amber">Collection AR Overdue</th>
    </tr>
    <tr>
        <th class="rbm-th-blue">Current</th>
        <th class="rbm-th-blue">Overdue</th>
        <th class="rbm-th-blue">Sisa AR</th>
        <th class="rbm-th-blue">%OD</th>
        <th class="rbm-th-amber">Actual Pelunasan</th>
        <th class="rbm-th-amber">Target Pelunasan</th>
        <th class="rbm-th-amber">%Coll</th>
    </tr>
    </thead>
    <tbody>
    {rows_html}
    </tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)


# ── SAMPLING EO — Nama Area x Grouping OS (khusus Sampling EO Belum/Sudah Diterima) ──
def render_sampling_eo_table(dff):
    needed = ["Nama Area", "Grouping OS", "Nominal", "NILAI DN KLAIM", "No Faktur"]
    if not all(c in dff.columns for c in needed) or dff.empty:
        st.info("Data Sampling EO tidak tersedia.")
        return

    d = dff[dff["Grouping OS"].astype(str).str.upper().str.contains("SAMPLING EO", na=False)].copy()
    if d.empty:
        st.info("Tidak ada data Sampling EO Belum/Sudah Diterima.")
        return

    d["Grouping OS"] = d["Grouping OS"].astype(str).str.upper().apply(
        lambda x: "BELUM TERIMA" if "BELUM" in x else ("SUDAH TERIMA" if "SUDAH" in x else x)
    )

    g = d.groupby(["Nama Area", "Grouping OS"], dropna=False).agg(
        qty=("No Faktur", "count"),
        sisa_ar=("Nominal", "sum"),
        dn_klaim=("NILAI DN KLAIM", "sum"),
    ).reset_index()
    g["diff"] = g["dn_klaim"] - g["sisa_ar"]
    g = g.sort_values(["Nama Area", "Grouping OS"])

    rows_html = ""
    for i, row in enumerate(g.itertuples(index=False), start=1):
        r = dict(zip(g.columns, row))
        rows_html += (
            "<tr>"
            f"<td>{i}</td>"
            f"<td>{r['Nama Area']}</td>"
            f"<td>{r['Grouping OS']}</td>"
            f"<td>{D(int(r['qty']))}</td>"
            f"<td>{M(r['sisa_ar'])}</td>"
            f"<td>{M(r['dn_klaim'])}</td>"
            f"<td>{M(r['diff'])}</td>"
            "</tr>"
        )

    st.markdown(f"""
    <div class="rbm-table-wrap scroll-box">
    <table class="rbm-table">
    <thead>
    <tr>
        <th>No</th>
        <th>Nama Area</th>
        <th>Grouping OS</th>
        <th>Qty Faktur</th>
        <th>Nilai Sisa AR</th>
        <th>Nilai DN Klaim</th>
        <th>DIFF.</th>
    </tr>
    </thead>
    <tbody>
    {rows_html}
    </tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)
    dl_btn(g.rename(columns={"qty":"Qty Faktur","sisa_ar":"Nilai Sisa AR","dn_klaim":"Nilai DN Klaim","diff":"DIFF."}), "GT_SAMPLING_EO")


# ── DETAIL REKONSILIASI FAKTUR SAMPLING EO (per baris faktur) ──
def render_sampling_eo_detail_table(dff):
    needed = ["Nama Area", "ASM", "No Faktur", "Tanggal Faktur", "Nilai Faktur",
              "Nominal", "OVERDUE", "Grouping OS", "STATUS KLAIM", "PRINCIPAL",
              "NO SURKOM", "NO DN AREA", "NILAI DN KLAIM", "KURANG KELENGKAPAN 1",
              "TGL BAYAR KE FINANCE", "NOMINAL BAYAR 2"]
    missing = [c for c in needed if c not in dff.columns]
    if missing or dff.empty:
        st.info(f"Data belum lengkap untuk tabel ini. Kolom hilang: {missing}" if missing else "Data tidak tersedia.")
        return

    d = dff[dff["Grouping OS"].astype(str).str.upper().str.contains("SAMPLING EO", na=False)].copy()
    if d.empty:
        st.info("Tidak ada data Sampling EO Belum/Sudah Diterima.")
        return

    d["Grouping OS"] = d["Grouping OS"].astype(str).str.upper().apply(
        lambda x: "BELUM TERIMA" if "BELUM" in x else ("SUDAH TERIMA" if "SUDAH" in x else x)
    )
    d["Tanggal Faktur_f"]       = pd.to_datetime(d["Tanggal Faktur"], errors="coerce").dt.strftime("%d/%m/%Y").fillna("")
    d["TGL BAYAR KE FINANCE_f"] = pd.to_datetime(d["TGL BAYAR KE FINANCE"], errors="coerce").dt.strftime("%d/%m/%Y").fillna("")
    d = d.sort_values("Nama Area")

    frozen_html = ""
    scroll_html = ""
    for i, row in enumerate(d.itertuples(index=False), start=1):
        r = dict(zip(d.columns, row))
        frozen_html += (
            "<tr>"
            f"<td>{i}</td>"
            f"<td class='eo-area'>{r['Nama Area']}</td>"
            f"<td>{r['ASM']}</td>"
            f"<td>{r['No Faktur']}</td>"
            f"<td>{r['Tanggal Faktur_f']}</td>"
            f"<td>{M(r['Nilai Faktur'])}</td>"
            f"<td>{M(r['Nominal'])}</td>"
            "</tr>"
        )
        scroll_html += (
            "<tr>"
            f"<td>{M(r['OVERDUE'])}</td>"
            f"<td>{r['Grouping OS']}</td>"
            f"<td>{r['STATUS KLAIM'] if pd.notna(r['STATUS KLAIM']) else '–'}</td>"
            f"<td>{r['PRINCIPAL'] if pd.notna(r['PRINCIPAL']) else '–'}</td>"
            f"<td>{r['NO SURKOM'] if pd.notna(r['NO SURKOM']) else '–'}</td>"
            f"<td>{r['NO DN AREA'] if pd.notna(r['NO DN AREA']) else '–'}</td>"
            f"<td>{M(r['NILAI DN KLAIM'])}</td>"
            f"<td>{r['KURANG KELENGKAPAN 1'] if pd.notna(r['KURANG KELENGKAPAN 1']) else '–'}</td>"
            f"<td>{r['TGL BAYAR KE FINANCE_f']}</td>"
            f"<td>{M(r['NOMINAL BAYAR 2'])}</td>"
            "</tr>"
        )

    st.markdown(f"""
    <div class="eo-split-wrap">
        <div class="eo-frozen-col">
        <table class="eo-tbl" style="width:796px;">
        <colgroup>
            <col style="width:46px"><col style="width:145px"><col style="width:145px">
            <col style="width:120px"><col style="width:120px"><col style="width:110px"><col style="width:110px">
        </colgroup>
        <thead><tr>
            <th>No</th><th>Nama Area</th><th>ROM</th><th>No Faktur</th>
            <th>Tanggal Faktur</th><th>Nilai Faktur</th><th>Sisa AR</th>
        </tr></thead>
        <tbody>{frozen_html}</tbody>
        </table>
        </div>
        <div class="eo-scroll-col">
        <table class="eo-tbl" style="width:1680px;">
        <colgroup>
            <col style="width:100px"><col style="width:150px"><col style="width:200px"><col style="width:110px">
            <col style="width:230px"><col style="width:230px"><col style="width:130px">
            <col style="width:230px"><col style="width:160px"><col style="width:140px">
        </colgroup>
        <thead><tr>
            <th>Overdue</th><th>Grouping OS</th><th>Status Klaim</th><th>Principal</th>
            <th>No Surkom</th><th>No DN Area</th><th>Nilai DN Klaim</th>
            <th>Kurang Kelengkapan 1</th><th>Tgl Bayar ke Finance</th><th>Nominal Bayar</th>
        </tr></thead>
        <tbody>{scroll_html}</tbody>
        </table>
        </div>
    </div>
    """, unsafe_allow_html=True)
    dl_btn(d[needed], "GT_SAMPLING_EO_DETAIL", "Download Detail Faktur")


# ── Split-table Detail Faktur GT — freeze #, Nama Area, RBM, Kode Customer, Nama Toko ──
def render_detail_faktur_split(tbl, frz_cols=None):
    if frz_cols is None:
        frz_cols = ["#","Nama Area","RBM","Kode Customer","Nama Toko"]
    frz_cols   = [c for c in frz_cols if c in tbl.columns]
    scroll_cols = [c for c in tbl.columns if c not in frz_cols]

    frz_widths = {"#":46,"No":46,"Nama Area":150,"RBM":150,"Kode Customer":120,"Nama Toko":180,
                  "No Faktur":130}
    scr_widths = {"No Faktur":120,"Tanggal Faktur":110,"Tanggal JT":110,"Nilai Faktur":110,"Sisa AR":110,
                  "Kelompok":90,"Grouping OS":150,"NO PO":120,"NO SURAT JALAN":150,"KRONOLOGI":200,
                  "ACTION PLAN":200,"DEADLINE":110,"PJ/PIC":110,"NO BA":110,"JENIS BA":120,
                  "JENIS KASUS":150,"PELAKU":120,"PENYELESAIAN":200,
                  "Kategori SO":140,"OVERDUE (Kelompok)":140,"KET":180}

    frz_w = [frz_widths.get(c,120) for c in frz_cols]
    scr_w = [scr_widths.get(c,130) for c in scroll_cols]

    frozen_html, scroll_html = "", ""
    for row in tbl.itertuples(index=False):
        r = dict(zip(tbl.columns, row))
        frozen_html += "<tr>" + "".join(
            f"<td class='eo-area'>{r[c]}</td>" if c=="Nama Area" else f"<td>{r[c]}</td>" for c in frz_cols
        ) + "</tr>"
        scroll_html += "<tr>" + "".join(f"<td>{r[c] if pd.notna(r[c]) else '–'}</td>" for c in scroll_cols) + "</tr>"

    frz_colgroup = "".join(f'<col style="width:{w}px">' for w in frz_w)
    scr_colgroup = "".join(f'<col style="width:{w}px">' for w in scr_w)
    frz_head = "".join(f"<th>{c}</th>" for c in frz_cols)
    scr_head = "".join(f"<th>{c}</th>" for c in scroll_cols)
    frz_total = sum(frz_w)
    scr_total = sum(scr_w)

    st.markdown(f"""
    <div class="eo-split-wrap">
        <div class="eo-frozen-col">
        <table class="eo-tbl" style="width:{frz_total}px;">
        <colgroup>{frz_colgroup}</colgroup>
        <thead><tr>{frz_head}</tr></thead>
        <tbody>{frozen_html}</tbody>
        </table>
        </div>
        <div class="eo-scroll-col">
        <table class="eo-tbl" style="width:{scr_total}px;">
        <colgroup>{scr_colgroup}</colgroup>
        <thead><tr>{scr_head}</tr></thead>
        <tbody>{scroll_html}</tbody>
        </table>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_customer_detail_table(dff):
    """Tabel detail per Kode Customer/Outlet — di bawah ranking RBM/KAM."""
    needed = ["Kode Customer","NAMA TOKO","JENIS OUTLET","RBM","ASM"]
    if not all(c in dff.columns for c in needed) or dff.empty:
        st.info("Data Kode Customer tidak tersedia.")
        return

    g = dff.groupby(needed, dropna=False).agg(
        nilai_faktur=("Nilai Faktur", "sum"),
        current=("CURRENT", "sum"),
        overdue=("OVERDUE", "sum"),
        sisa_ar=("NOMINAL", "sum"),
        actual=("ACTUAL PELUNASAN", "sum"),
        target=("TARGET PELUNASAN", "sum"),
    ).reset_index()
    for c in needed:
        g[c] = g[c].fillna("–").replace("", "–")
    g["pct_od"]   = g.apply(lambda r: (r["overdue"]/r["sisa_ar"]*100) if r["sisa_ar"] else 0, axis=1)
    g["pct_coll"] = g.apply(lambda r: (r["actual"]/r["target"]*100) if r["target"] else 0, axis=1)
    g = g.sort_values("sisa_ar", ascending=False)

    rows_html = ""
    for i, row in enumerate(g.itertuples(index=False), start=1):
        r = dict(zip(g.columns, row))
        rows_html += (
            "<tr>"
            f"<td class='cust-frz cust-frz-0'>{i}</td>"
            f"<td class='cust-frz cust-frz-1 cust-kode'>{r['Kode Customer']}</td>"
            f"<td class='cust-frz cust-frz-2 cust-outlet'>{r['NAMA TOKO']}</td>"
            f"<td class='cust-frz cust-frz-3'>{r['JENIS OUTLET']}</td>"
            f"<td>{r['RBM']}</td>"
            f"<td>{r['ASM']}</td>"
            f"<td>{M(r['nilai_faktur'])}</td>"
            f"<td>{M(r['current'])}</td>"
            f"<td>{M(r['overdue'])}</td>"
            f"<td>{M(r['sisa_ar'])}</td>"
            f"<td>{r['pct_od']:.2f}%</td>"
            f"<td>{M(r['actual'])}</td>"
            f"<td>{M(r['target'])}</td>"
            f"<td>{r['pct_coll']:.2f}%</td>"
            "</tr>"
        )

    st.markdown(f"""
    <div class="cust-table-wrap">
    <table class="cust-table">
    <colgroup>
        <col style="width:50px">
        <col style="width:110px">
        <col style="width:170px">
        <col style="width:150px">
        <col style="width:100px">
        <col style="width:100px">
        <col style="width:100px">
        <col style="width:90px">
        <col style="width:90px">
        <col style="width:90px">
        <col style="width:70px">
        <col style="width:110px">
        <col style="width:110px">
        <col style="width:70px">
    </colgroup>
    <thead>
    <tr>
        <th rowspan="2" class="cust-frz cust-frz-0">No</th>
        <th rowspan="2" class="cust-frz cust-frz-1">Kode Customer</th>
        <th rowspan="2" class="cust-frz cust-frz-2 cust-outlet">Nama Outlet</th>
        <th rowspan="2" class="cust-frz cust-frz-3">Grouping Outlet</th>
        <th rowspan="2">RBM/KAM</th>
        <th rowspan="2">ROM</th>
        <th rowspan="2">Nilai Faktur</th>
        <th colspan="4" class="rbm-th-blue">Sisa AR Current Vs Overdue</th>
        <th colspan="3" class="rbm-th-amber">Collection AR Overdue</th>
    </tr>
    <tr>
        <th class="rbm-th-blue">Current</th>
        <th class="rbm-th-blue">Overdue</th>
        <th class="rbm-th-blue">Sisa AR</th>
        <th class="rbm-th-blue">%OD</th>
        <th class="rbm-th-amber">Actual Pelunasan</th>
        <th class="rbm-th-amber">Target Pelunasan</th>
        <th class="rbm-th-amber">%Coll</th>
    </tr>
    </thead>
    <tbody>
    {rows_html}
    </tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# PAGE: AR OTC
# ════════════════════════════════════════════════════════════════════
def page_otc(filters=None):
    with st.spinner("Memuat data OTC..."):
        df, last_updated = load_otc()

    if df.empty:
        st.warning("Belum ada data OTC. Jalankan **JALANKAN_UPLOAD.bat** untuk upload data.")
        return

    # ── SIDEBAR ───────────────────────────────────────────────────
    if filters is None: filters = {}
    dff = df.copy()
    if filters.get("region","Semua")!="Semua" and "REGION" in dff.columns: dff=dff[dff["REGION"]==filters["region"]]
    if filters.get("area","Semua")!="Semua" and "NAMA AREA" in dff.columns: dff=dff[dff["NAMA AREA"]==filters["area"]]
    if filters.get("asm","Semua")!="Semua" and "ASM" in dff.columns: dff=dff[dff["ASM"]==filters["asm"]]
    if filters.get("rbm","Semua")!="Semua" and "RBM" in dff.columns: dff=dff[dff["RBM"]==filters["rbm"]]
    if filters.get("sales","Semua")!="Semua" and "NAMA SALES" in dff.columns: dff=dff[dff["NAMA SALES"]==filters["sales"]]
    if filters.get("jenis","Semua")!="Semua" and "JENIS OUTLET" in dff.columns: dff=dff[dff["JENIS OUTLET"]==filters["jenis"]]
    if filters.get("toko","Semua")!="Semua" and "NAMA TOKO" in dff.columns: dff=dff[dff["NAMA TOKO"]==filters["toko"]]
    if filters.get("kat","Semua")!="Semua" and "KATEGORI OVERDUE" in dff.columns: dff=dff[dff["KATEGORI OVERDUE"]==filters["kat"]]
    if filters.get("grp","Semua")!="Semua" and "GROUPING OS" in dff.columns: dff=dff[dff["GROUPING OS"]==filters["grp"]]
    if filters.get("top","Semua")!="Semua" and "TOP" in dff.columns: dff=dff[dff["TOP"]==filters["top"]]
    bkt=filters.get("bkt",BUCKETS)
    if bkt and "KELOMPOK" in dff.columns: dff=dff[dff["KELOMPOK"].isin(bkt)]
    so_kat=filters.get("so_kat","Semua")
    if so_kat!="Semua" and "KELOMPOK" in dff.columns:
        _tmp=dff[dff["KELOMPOK"]!="CURRENT"].copy(); _tmp["_SO"]=_tmp["KELOMPOK"].map(SO_MAP)
        dff=dff[dff["No Faktur"].isin(_tmp[_tmp["_SO"]==so_kat]["No Faktur"])]
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
    kpi(c6,"Qty Faktur Gantung",D(tq),f"{D(len(dff))} baris data","orange")
    st.markdown("<br>",unsafe_allow_html=True)

    bv, grand = bucket_strip(dff)

    # ════ RANKING RBM/KAM BERDASARKAN OUTSTANDING ════
    sec("RANKING KAM/RBM BERDASARKAN OUTSTANDING & COLLECTION")
    render_rbm_ranking_table(dff)

    # ════ TABEL DETAIL PER KODE CUSTOMER (judul sementara, ganti sesuai kebutuhan) ════
    sec("OUTSTANDING & COLLECTION BY OUTLET")
    render_customer_detail_table(dff)

    # ════ SO BLOCK — 1 TABEL dengan kolom SO Status, Area, Kode Customer, dll ════
    sec("STATUS SO BLOCK — REKOMENDASI TINDAKAN")

    df_ov = dff.copy()
    df_ov["SO Kat"] = df_ov["KELOMPOK"].map({
        "CURRENT":"Warning SO","1-7 DAYS":"Warning SO","8-30 DAYS":"Warning SO",
        "31-60 DAYS":"Block SO","61-90 DAYS":"Block SO",
        "91-120 DAYS":"Critical Block SO","121+ DAYS":"Critical Block SO","<2026":"Critical Block SO",
    }).fillna("Warning SO")

    # Pivot menggunakan pivot_table — kompatibel semua versi pandas
    grp_cols = [c for c in ["RBM","NAMA AREA","NAMA TOKO"] if c in df_ov.columns]
    if grp_cols:
        # Qty faktur per toko
        qty = df_ov.groupby(grp_cols)["No Faktur"].count().reset_index().rename(columns={"No Faktur":"Qty Faktur"})
        # Pivot nominal per kategori SO
        piv = df_ov.pivot_table(index=grp_cols, columns="SO Kat", values="NOMINAL", aggfunc="sum", fill_value=0).reset_index()
        piv.columns.name = None
        # Gabung
        tbl_so = qty.merge(piv, on=grp_cols, how="left")
        # Pastikan kolom ada
        for col in ["Warning SO","Block SO","Critical Block SO"]:
            if col not in tbl_so.columns: tbl_so[col] = 0
        # Total nilai faktur
        if "Nilai Faktur" in df_ov.columns:
            tot = df_ov.groupby(grp_cols)["Nilai Faktur"].sum().reset_index().rename(columns={"Nilai Faktur":"Total Nilai Faktur"})
            tbl_so = tbl_so.merge(tot, on=grp_cols, how="left")
        # Kode Customer per toko (ambil kode customer pertama yang ditemukan di grup)
        if "Kode Customer" in df_ov.columns:
            kc = df_ov.groupby(grp_cols)["Kode Customer"].first().reset_index()
            tbl_so = tbl_so.merge(kc, on=grp_cols, how="left")
        # Filter hanya yang ada outstanding
        tbl_so = tbl_so[(tbl_so.get("Warning SO",0)!=0)|(tbl_so.get("Block SO",0)!=0)|(tbl_so.get("Critical Block SO",0)!=0)]
        tbl_so = tbl_so.sort_values("Critical Block SO", ascending=False).reset_index(drop=True)
        tbl_so.insert(0,"Nomor", range(1, len(tbl_so)+1))
        tbl_so.rename(columns={"NAMA AREA":"Nama Area","NAMA TOKO":"Nama Toko"}, inplace=True)
        # Pindahkan "Kode Customer" ke posisi tepat setelah "Nama Area"
        if "Kode Customer" in tbl_so.columns:
            cols = list(tbl_so.columns)
            cols.remove("Kode Customer")
            insert_at = cols.index("Nama Area") + 1
            cols.insert(insert_at, "Kode Customer")
            tbl_so = tbl_so[cols]
        for col in ["Warning SO","Block SO","Critical Block SO","Total Nilai Faktur"]:
            if col in tbl_so.columns:
                tbl_so[col] = tbl_so[col].apply(lambda x: f"{x:,.0f}" if x!=0 else "-")
        st.dataframe(tbl_so, use_container_width=True, hide_index=True, height=440)
        dl_btn(df_ov, "SO_BLOCK_DETAIL", "Download SO Block Detail")


    # Chart distribusi SO Block per area (top 10)
    sec("DISTRIBUSI SO BLOCK PER NAMA AREA")
    pivot = (df_ov.groupby(["NAMA AREA","SO Kat"])["NOMINAL"]
             .sum().unstack(fill_value=0).reset_index())
    for k in ["Warning SO","Block SO","Critical Block SO"]:
        if k not in pivot.columns: pivot[k]=0
    pivot["TOTAL"] = pivot[["Warning SO","Block SO","Critical Block SO"]].sum(axis=1)
    pivot = pivot.nlargest(10,"TOTAL")
    fig_so = go.Figure()
    for col_key,color,name in [
        ("Critical Block SO","#C8192E","Critical Block"),
        ("Block SO","#E65C00","Block SO"),
        ("Warning SO","#F5A623","Warning SO"),
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
        area_os = (dff[dff["NOMINAL"]>0].groupby("NAMA AREA")["NOMINAL"]
                   .sum().sort_values(ascending=False))
        top10 = area_os.head(10)
        rest = area_os.iloc[10:].sum()
        pl = top10.index.tolist()
        pv = top10.values.tolist()
        pc = CHART_PALETTE[:len(pl)]
        if rest > 0:
            pl.append("Lainnya")
            pv.append(rest)
            pc.append("#9E9E9E")
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
        t_kat.columns=["Kategori Overdue","Nominal","Jml Faktur","%OD"]
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
    sec(f"DETAIL FAKTUR — {D(ovrd_ct)} FAKTUR OVERDUE")
    COLS=["NAMA AREA","RBM","Kode Customer","NAMA TOKO","No Faktur","Tanggal Faktur","Tanggal JT",
          "Nilai Faktur","NOMINAL","KELOMPOK","GROUPING OS","Action Plan","Deadline","PIC","KET"]
    cols_ok=[c for c in COLS if c in dff.columns]
    tbl=dff[cols_ok].copy()
    tbl["Kategori SO"] = dff["KELOMPOK"].map({
        "CURRENT":"Warning SO","1-7 DAYS":"Warning SO","8-30 DAYS":"Warning SO",
        "31-60 DAYS":"Block SO","61-90 DAYS":"Block SO",
        "91-120 DAYS":"Critical Block SO","121+ DAYS":"Critical Block SO","<2026":"Critical Block SO",
    }).fillna("Warning SO")
    if "Tanggal Faktur" in tbl.columns: tbl["Tanggal Faktur"]=tbl["Tanggal Faktur"].dt.strftime("%d %b %Y")
    if "Tanggal JT" in tbl.columns: tbl["Tanggal JT"]=tbl["Tanggal JT"].dt.strftime("%d %b %Y")
    for c in ["Nilai Faktur","NOMINAL"]:
        if c in tbl.columns: tbl[c]=tbl[c].apply(R)
    tbl.rename(columns={"NAMA AREA":"Nama Area","NAMA TOKO":"Nama Toko","NOMINAL":"Sisa AR",
                         "KELOMPOK":"OVERDUE (Kelompok)","GROUPING OS":"Grouping OS",
                         "PIC":"PJ/PIC","Deadline":"DEADLINE"},inplace=True)
    DISPLAY_ORDER=["Nama Area","RBM","Kode Customer","Nama Toko","No Faktur","Tanggal Faktur","Tanggal JT",
                   "Nilai Faktur","Sisa AR","Kategori SO","OVERDUE (Kelompok)","Grouping OS","Action Plan",
                   "DEADLINE","PJ/PIC","KET"]
    tbl = tbl[[c for c in DISPLAY_ORDER if c in tbl.columns]]
    tbl.insert(0,"No",range(1,len(tbl)+1))
    with st.expander(f"Tampilkan {D(len(tbl))} baris · OS Total: {M(tn)}",expanded=False):
        render_detail_faktur_split(tbl, frz_cols=["No","Nama Area","RBM","Kode Customer","Nama Toko","No Faktur"])
        dl_btn(dff[cols_ok],"OS_MTI_NKA_DETAIL","Download Detail Faktur")


# ════════════════════════════════════════════════════════════════════
# PAGE: AR GT
# ════════════════════════════════════════════════════════════════════
def page_gt(filters=None):
    with st.spinner("Memuat data GT..."):
        df, last_updated = load_gt()

    if df.empty:
        st.warning("Belum ada data OTC. Jalankan **JALANKAN_SEMUA.bat** untuk upload data GT.")
        return

    # ── SIDEBAR ───────────────────────────────────────────────────
    if filters is None: filters = {}
    dff = df.copy()
    if filters.get("region","Semua")!="Semua" and "Region" in dff.columns: dff=dff[dff["Region"]==filters["region"]]
    if filters.get("area","Semua")!="Semua" and "Nama Area" in dff.columns: dff=dff[dff["Nama Area"]==filters["area"]]
    if filters.get("asm","Semua")!="Semua" and "ASM" in dff.columns: dff=dff[dff["ASM"]==filters["asm"]]
    if filters.get("rbm","Semua")!="Semua" and "RBM" in dff.columns: dff=dff[dff["RBM"]==filters["rbm"]]
    if filters.get("sales","Semua")!="Semua" and "Nama Sales" in dff.columns: dff=dff[dff["Nama Sales"]==filters["sales"]]
    if filters.get("jenis","Semua")!="Semua" and "Jenis Outlet" in dff.columns: dff=dff[dff["Jenis Outlet"]==filters["jenis"]]
    if filters.get("toko","Semua")!="Semua" and "Nama Toko" in dff.columns: dff=dff[dff["Nama Toko"]==filters["toko"]]
    if filters.get("kat","Semua")!="Semua" and "Kategori Overdue" in dff.columns: dff=dff[dff["Kategori Overdue"]==filters["kat"]]
    if filters.get("grp","Semua")!="Semua" and "Grouping OS" in dff.columns: dff=dff[dff["Grouping OS"]==filters["grp"]]
    if filters.get("top","Semua")!="Semua" and "TOP" in dff.columns: dff=dff[dff["TOP"]==filters["top"]]
    bkt=filters.get("bkt",BUCKETS)
    if bkt and "KELOMPOK" in dff.columns: dff=dff[dff["KELOMPOK"].isin(bkt)]
    so_kat=filters.get("so_kat","Semua")
    if so_kat!="Semua" and "KELOMPOK" in dff.columns:
        _tmp=dff[dff["KELOMPOK"]!="CURRENT"].copy(); _tmp["_SO"]=_tmp["KELOMPOK"].map(SO_MAP)
        dff=dff[dff["No Faktur"].isin(_tmp[_tmp["_SO"]==so_kat]["No Faktur"])]
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
    kpi(c6,"Qty Faktur",D(tq),f"{D(len(dff))} baris data","orange")
    st.markdown("<br>",unsafe_allow_html=True)

    bv, grand = bucket_strip(dff)

    # ════ RANKING KAM/RBM ════
    sec("RANKING KAM/RBM BERDASARKAN OUTSTANDING & COLLECTION")
    render_rbm_kam_table(dff)

    # ════ OUTSTANDING BY AREA ════
    sec("OUTSTANDING BY AREA")
    render_area_ranking_table(dff)

    # ════ SO BLOCK — 1 TABEL dengan kolom SO Status, Area, Kode Customer, dll ════
    sec("STATUS SO BLOCK GT — REKOMENDASI TINDAKAN")

    df_ov = dff.copy()
    df_ov["SO Kat"] = df_ov["KELOMPOK"].map({
        "CURRENT":"Warning SO","1-7 DAYS":"Warning SO","8-30 DAYS":"Warning SO",
        "31-60 DAYS":"Block SO","61-90 DAYS":"Block SO",
        "91-120 DAYS":"Critical Block SO","121+ DAYS":"Critical Block SO","<2026":"Critical Block SO",
    }).fillna("Warning SO")

    # RBM mungkin kosong di RDI — filter hanya kolom yang punya nilai
    _base_cols = ["RBM","Nama Area","Nama Toko"]
    grp_cols = [c for c in _base_cols if c in df_ov.columns and df_ov[c].notna().any()]
    if not grp_cols:
        grp_cols = [c for c in ["Nama Area","Nama Toko"] if c in df_ov.columns]
    if grp_cols:
        qty = df_ov.groupby(grp_cols)["No Faktur"].count().reset_index().rename(columns={"No Faktur":"Qty Faktur"})
        piv = df_ov.pivot_table(index=grp_cols, columns="SO Kat", values="Nominal", aggfunc="sum", fill_value=0).reset_index()
        piv.columns.name = None
        tbl_so = qty.merge(piv, on=grp_cols, how="left")
        for col in ["Warning SO","Block SO","Critical Block SO"]:
            if col not in tbl_so.columns: tbl_so[col] = 0
        if "Nilai Faktur" in df_ov.columns:
            tot = df_ov.groupby(grp_cols)["Nilai Faktur"].sum().reset_index().rename(columns={"Nilai Faktur":"Total Nilai Faktur"})
            tbl_so = tbl_so.merge(tot, on=grp_cols, how="left")
        tbl_so = tbl_so[(tbl_so.get("Warning SO",0)!=0)|(tbl_so.get("Block SO",0)!=0)|(tbl_so.get("Critical Block SO",0)!=0)]
        tbl_so = tbl_so.sort_values("Critical Block SO", ascending=False).reset_index(drop=True)
        tbl_so.insert(0,"Nomor", range(1, len(tbl_so)+1))
        tbl_so.rename(columns={"No Faktur SAP":"Kode Customer"}, inplace=True)
        for col in ["Warning SO","Block SO","Critical Block SO","Total Nilai Faktur"]:
            if col in tbl_so.columns:
                tbl_so[col] = tbl_so[col].apply(lambda x: f"{x:,.0f}" if x!=0 else "-")
        st.dataframe(tbl_so, use_container_width=True, hide_index=True, height=440)
        dl_btn(df_ov, "GT_SO_BLOCK_DETAIL", "Download SO Block GT")


    # Chart distribusi SO Block per area (top 10)
    sec("DISTRIBUSI SO BLOCK PER NAMA AREA")
    pivot = (df_ov.groupby(["Nama Area","SO Kat"])["Nominal"]
             .sum().unstack(fill_value=0).reset_index())
    for k in ["Warning SO","Block SO","Critical Block SO"]:
        if k not in pivot.columns: pivot[k]=0
    pivot["TOTAL"] = pivot[["Warning SO","Block SO","Critical Block SO"]].sum(axis=1)
    pivot = pivot.nlargest(10,"TOTAL")
    fig_so = go.Figure()
    for col_key,color,name in [
        ("Critical Block SO","#C8192E","Critical Block"),
        ("Block SO","#E65C00","Block SO"),
        ("Warning SO","#F5A623","Warning SO"),
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
        area_os = (dff[dff["Nominal"]>0].groupby("Nama Area")["Nominal"]
                   .sum().sort_values(ascending=False))
        top10 = area_os.head(10)
        rest = area_os.iloc[10:].sum()
        pl = top10.index.tolist()
        pv = top10.values.tolist()
        pc = CHART_PALETTE[:len(pl)]
        if rest > 0:
            pl.append("Lainnya")
            pv.append(rest)
            pc.append("#9E9E9E")
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
        t_kat.columns=["Kategori Overdue","Nominal","Jml Faktur","%OD"]
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

    # ════ SAMPLING EO — BELUM/SUDAH DITERIMA ════
    sec("SAMPLING EO — BELUM & SUDAH DITERIMA")
    render_sampling_eo_table(dff)

    sec("Detail Rekonsiliasi Faktur Sampling EO (Status Terima dan blm Terima")
    render_sampling_eo_detail_table(dff)

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
    sec(f"DETAIL FAKTUR — {D(ovrd_ct)} FAKTUR OVERDUE")
    COLS=["Nama Area","RBM","Kode Customer","Nama Toko","No Faktur","Tanggal Faktur","Tanggal JT",
          "Nilai Faktur","Nominal","KELOMPOK","Grouping OS","NO PO","NO SURAT JALAN","KRONOLOGI",
          "ACTION PLAN","DEADLINE","NO BA","JENIS BA","JENIS KASUS","PELAKU","PENYELESAIAN"]
    cols_ok=[c for c in COLS if c in dff.columns]
    tbl=dff[cols_ok].copy()
    if "Tanggal Faktur" in tbl.columns: tbl["Tanggal Faktur"]=tbl["Tanggal Faktur"].dt.strftime("%d %b %Y")
    if "Tanggal JT" in tbl.columns: tbl["Tanggal JT"]=tbl["Tanggal JT"].dt.strftime("%d %b %Y")
    for c in ["Nilai Faktur","Nominal"]:
        if c in tbl.columns: tbl[c]=tbl[c].apply(R)
    tbl.rename(columns={"Nominal":"Sisa AR","KELOMPOK":"Kelompok"},inplace=True)
    tbl.insert(0,"#",range(1,len(tbl)+1))
    with st.expander(f"Tampilkan {D(len(tbl))} baris · OS Total: {M(tn)}",expanded=False):
        render_detail_faktur_split(tbl, frz_cols=["#","Nama Area","RBM","Kode Customer","Nama Toko"])
        dl_btn(dff[cols_ok],"GT_DETAIL","Download Detail Faktur GT")

# ════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=300, show_spinner=False)
def load_rdi():
    sb = get_sb()
    last_updated = "–"
    try:
        meta = sb.table("upload_log_rdi").select("uploaded_at,total_rows") \
                 .order("uploaded_at",desc=True).limit(1).execute()
        if meta.data:
            raw = meta.data[0].get("uploaded_at","")
            try:
                dt = datetime.fromisoformat(raw.replace("Z","+00:00"))
                dt_wib = dt.astimezone(WIB)
                last_updated = dt_wib.strftime("%d %b %Y · %H:%M WIB")
            except Exception:
                last_updated = raw
    except Exception:
        pass
    try:
        rows,page,SZ = [],0,1000
        while True:
            r = sb.table("rdi_master").select("*").range(page*SZ,(page+1)*SZ-1).execute()
            if not r.data: break
            rows.extend(r.data)
            if len(r.data)<SZ: break
            page+=1
        if not rows: return pd.DataFrame(), last_updated
        df = pd.DataFrame(rows)
        for c in ("id","created_at"):
            if c in df.columns: df.drop(columns=c,inplace=True)
        RDI_ALL = [
            "Nama Area","Nama Sales","Nama Toko","Kategori Overdue","Region",
            "Jenis Outlet","Nominal","Grouping OS","RBM","ASM","No Faktur",
            "No Faktur Scylla","Tanggal Faktur","Tanggal JT","Nilai Faktur","TOP",
            "JENIS KASUS","KRONOLOGI","JENIS BA","NO BA","BAP","TGL KONFIRMASI",
            "ACTION PLAN","PENYELESAIAN",
            "BERAPA HARI?","KELOMPOK",
            "CURRENT","1-7 DAYS","8-30 DAYS","31-60 DAYS","61-90 DAYS",
            "91-120 DAYS","121+ DAYS","<2026",
            "KELOMPOK2","OVERDUE","TANGGAL HARI INII","batas 2025","OVERDUE?",
            "ACTUAL PELUNASAN","TARGET PELUNASAN","TODAY+1","DUE DATE","Qty Faktur Gantung",
        ]
        RDI_NUM = {
            "Nominal","Nilai Faktur","CURRENT","1-7 DAYS","8-30 DAYS","31-60 DAYS",
            "61-90 DAYS","91-120 DAYS","121+ DAYS","<2026",
            "OVERDUE","OVERDUE?","ACTUAL PELUNASAN","TARGET PELUNASAN",
            "DUE DATE","Qty Faktur Gantung",
        }
        RDI_DT = {"Tanggal Faktur","Tanggal JT","TANGGAL HARI INII","batas 2025","TODAY+1"}
        for col in RDI_ALL:
            if col not in df.columns: df[col]=None
        df = df[[c for c in RDI_ALL if c in df.columns]].copy()
        for col in RDI_NUM:
            if col in df.columns:
                df[col]=pd.to_numeric(df[col],errors="coerce").fillna(0)
        for col in RDI_DT:
            if col in df.columns:
                df[col]=pd.to_datetime(df[col],errors="coerce")
        return df, last_updated
    except Exception as e:
        st.error(f"Gagal ambil data RDI: {e}")
        return pd.DataFrame(), last_updated




# ════════════════════════════════════════════════════════════════════════════
# PAGE: AR RDI
# ════════════════════════════════════════════════════════════════════════════
def page_rdi(filters=None):
    with st.spinner("Memuat data RDI..."):
        df, last_updated = load_rdi()

    if df.empty:
        st.info("Belum ada data RDI. Jalankan **JALANKAN_SEMUA.bat** untuk upload data RDI.")
        return

    # Sidebar
    if filters is None: filters = {}
    dff = df.copy()
    if filters.get("region","Semua")!="Semua" and "Region" in dff.columns: dff=dff[dff["Region"]==filters["region"]]
    if filters.get("area","Semua")!="Semua" and "Nama Area" in dff.columns: dff=dff[dff["Nama Area"]==filters["area"]]
    if filters.get("asm","Semua")!="Semua" and "ASM" in dff.columns: dff=dff[dff["ASM"]==filters["asm"]]
    if filters.get("rbm","Semua")!="Semua" and "RBM" in dff.columns: dff=dff[dff["RBM"]==filters["rbm"]]
    if filters.get("sales","Semua")!="Semua" and "Nama Sales" in dff.columns: dff=dff[dff["Nama Sales"]==filters["sales"]]
    if filters.get("jenis","Semua")!="Semua" and "Jenis Outlet" in dff.columns: dff=dff[dff["Jenis Outlet"]==filters["jenis"]]
    if filters.get("toko","Semua")!="Semua" and "Nama Toko" in dff.columns: dff=dff[dff["Nama Toko"]==filters["toko"]]
    if filters.get("kat","Semua")!="Semua" and "Kategori Overdue" in dff.columns: dff=dff[dff["Kategori Overdue"]==filters["kat"]]
    if filters.get("grp","Semua")!="Semua" and "Grouping OS" in dff.columns: dff=dff[dff["Grouping OS"]==filters["grp"]]
    if filters.get("top","Semua")!="Semua" and "TOP" in dff.columns: dff=dff[dff["TOP"]==filters["top"]]
    bkt=filters.get("bkt",BUCKETS)
    if bkt and "KELOMPOK" in dff.columns: dff=dff[dff["KELOMPOK"].isin(bkt)]
    so_kat=filters.get("so_kat","Semua")
    if so_kat!="Semua" and "KELOMPOK" in dff.columns:
        _tmp=dff[dff["KELOMPOK"]!="CURRENT"].copy(); _tmp["_SO"]=_tmp["KELOMPOK"].map(SO_MAP)
        dff=dff[dff["No Faktur"].isin(_tmp[_tmp["_SO"]==so_kat]["No Faktur"])]
    if dff.empty:
        st.warning("Tidak ada data sesuai filter."); return

    pma_header("AR Outstanding RDI", last_updated, len(dff))

    # KPI
    tn  = dff["Nominal"].sum()            if "Nominal"           in dff.columns else 0
    to  = dff["OVERDUE"].sum()            if "OVERDUE"           in dff.columns else 0
    tc  = dff["CURRENT"].sum()            if "CURRENT"           in dff.columns else 0
    ta  = dff["ACTUAL PELUNASAN"].sum()   if "ACTUAL PELUNASAN"  in dff.columns else 0
    tt  = dff["TARGET PELUNASAN"].sum()   if "TARGET PELUNASAN"  in dff.columns else 0
    td  = dff["DUE DATE"].sum()           if "DUE DATE"          in dff.columns else 0
    tq  = int(dff["Qty Faktur Gantung"].sum()) if "Qty Faktur Gantung" in dff.columns else 0
    tnf = dff["Nilai Faktur"].sum()       if "Nilai Faktur"      in dff.columns else 0

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    kpi(c1,"Total Outstanding RDI", M(tn),  f"Nilai Faktur {M(tnf)}")
    kpi(c2,"Overdue",               M(to),  P(to,tn)+" dari outstanding")
    kpi(c3,"Current",               M(tc),  P(tc,tn)+" dari total","green")
    kpi(c4,"% Collection",          P(ta,tt),f"Actual {M(ta)} / Target {M(tt)}","gold")
    kpi(c5,"Due Date Hari Ini",     M(td),  "Nominal jatuh tempo hari ini","stone")
    kpi(c6,"Qty Faktur Gantung",    D(tq),f"{D(len(dff))} baris data","orange")
    st.markdown("<br>",unsafe_allow_html=True)

    bv, grand = bucket_strip(dff)

    # SO Block
    sec("STATUS SO BLOCK RDI — REKOMENDASI TINDAKAN")

    df_ov = dff.copy()
    df_ov["SO Kat"] = df_ov["KELOMPOK"].map({
        "CURRENT":"Warning SO","1-7 DAYS":"Warning SO","8-30 DAYS":"Warning SO",
        "31-60 DAYS":"Block SO","61-90 DAYS":"Block SO",
        "91-120 DAYS":"Critical Block SO","121+ DAYS":"Critical Block SO","<2026":"Critical Block SO",
    }).fillna("Warning SO")

    # RBM mungkin kosong di RDI — filter hanya kolom yang punya nilai
    _base_cols = ["RBM","Nama Area","Nama Toko"]
    grp_cols = [c for c in _base_cols if c in df_ov.columns and df_ov[c].notna().any()]
    if not grp_cols:
        grp_cols = [c for c in ["Nama Area","Nama Toko"] if c in df_ov.columns]
    if grp_cols:
        qty = df_ov.groupby(grp_cols)["No Faktur"].count().reset_index().rename(columns={"No Faktur":"Qty Faktur"})
        piv = df_ov.pivot_table(index=grp_cols, columns="SO Kat", values="Nominal", aggfunc="sum", fill_value=0).reset_index()
        piv.columns.name = None
        tbl_so = qty.merge(piv, on=grp_cols, how="left")
        for col in ["Warning SO","Block SO","Critical Block SO"]:
            if col not in tbl_so.columns: tbl_so[col] = 0
        if "Nilai Faktur" in df_ov.columns:
            tot = df_ov.groupby(grp_cols)["Nilai Faktur"].sum().reset_index().rename(columns={"Nilai Faktur":"Total Nilai Faktur"})
            tbl_so = tbl_so.merge(tot, on=grp_cols, how="left")
        tbl_so = tbl_so[(tbl_so.get("Warning SO",0)!=0)|(tbl_so.get("Block SO",0)!=0)|(tbl_so.get("Critical Block SO",0)!=0)]
        tbl_so = tbl_so.sort_values("Critical Block SO", ascending=False).reset_index(drop=True)
        tbl_so.insert(0,"Nomor", range(1, len(tbl_so)+1))
        tbl_so.rename(columns={"No Faktur SAP":"Kode Customer"}, inplace=True)
        for col in ["Warning SO","Block SO","Critical Block SO","Total Nilai Faktur"]:
            if col in tbl_so.columns:
                tbl_so[col] = tbl_so[col].apply(lambda x: f"{x:,.0f}" if x!=0 else "-")
        st.dataframe(tbl_so, use_container_width=True, hide_index=True, height=440)
        dl_btn(df_ov, "RDI_SO_BLOCK_DETAIL", "Download SO Block RDI")


    # Komposisi
    sec("KOMPOSISI OUTSTANDING RDI")
    ca2,cb2 = st.columns([5,4])
    with ca2:
        if "Grouping OS" in dff.columns:
            grp_os=(dff[dff["Nominal"]>0].groupby("Grouping OS")["Nominal"]
                    .sum().sort_values().reset_index())
            grp_os.columns=["Kategori","Nominal"]
            fig_h=go.Figure(go.Bar(x=grp_os["Nominal"],y=grp_os["Kategori"],orientation="h",
                marker_color=CHART_PALETTE[:len(grp_os)],
                text=[M(v) for v in grp_os["Nominal"]],
                textposition="outside",textfont=dict(size=10,color="#1E1E1E")))
            plot_base(fig_h,h=300); fig_h.update_layout(xaxis_tickformat=",")
            st.plotly_chart(fig_h,use_container_width=True)
    with cb2:
        area_os = (dff[dff["Nominal"]>0].groupby("Nama Area")["Nominal"]
                   .sum().sort_values(ascending=False))
        top10 = area_os.head(10)
        rest = area_os.iloc[10:].sum()
        pl = top10.index.tolist()
        pv = top10.values.tolist()
        pc = CHART_PALETTE[:len(pl)]
        if rest > 0:
            pl.append("Lainnya")
            pv.append(rest)
            pc.append("#9E9E9E")
        fig_pie=go.Figure(go.Pie(labels=pl,values=pv,marker_colors=pc,hole=0.55,
            textinfo="percent",textfont_size=11,
            hovertemplate="%{label}: %{value:,.0f}<extra></extra>"))
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
            height=300,margin=dict(t=12,b=12,l=0,r=0),showlegend=True,
            legend=dict(font_size=10,x=1.01,y=0.5,xanchor="left"),
            annotations=[dict(text=f"<b>{M(grand)}</b><br><span style='font-size:9px'>Total OS</span>",
                x=0.5,y=0.5,showarrow=False,font=dict(size=14,color="#1E1E1E"))])
        st.plotly_chart(fig_pie,use_container_width=True)

    # Wilayah
    sec("OUTSTANDING RDI PER WILAYAH")
    if "Nama Area" in dff.columns:
        t_area=(dff.groupby("Nama Area")
                .agg(NF=("Nilai Faktur","sum"),Cur=("CURRENT","sum"),Ov=("OVERDUE","sum"))
                .reset_index().sort_values("NF",ascending=False))
        t_area["%C/OD"]=t_area.apply(lambda r: P(r["Cur"],r["Cur"]+r["Ov"]),axis=1)
        for c in ["NF","Cur","Ov"]: t_area[c]=t_area[c].apply(M)
        t_area.columns=["Nama Area","Nilai Faktur","Current","Overdue","%Curr/OD"]
        st.dataframe(t_area,use_container_width=True,hide_index=True,height=340)
        dl_btn(t_area,"RDI_OUTSTANDING_PER_AREA")

    # Detail faktur
    ovrd_ct=int((dff["OVERDUE?"]>0).sum()) if "OVERDUE?" in dff.columns else 0
    sec(f"DETAIL FAKTUR RDI — {D(ovrd_ct)} FAKTUR OVERDUE")
    COLS=["Nama Area","ASM","Nama Sales","Nama Toko","No Faktur",
          "Tanggal Faktur","Tanggal JT","Nilai Faktur","Nominal",
          "KELOMPOK","OVERDUE?","Grouping OS"]
    cols_ok=[c for c in COLS if c in dff.columns]
    tbl=dff[cols_ok].copy()
    if "Tanggal Faktur" in tbl.columns: tbl["Tanggal Faktur"]=tbl["Tanggal Faktur"].dt.strftime("%d %b %Y")
    if "Tanggal JT"     in tbl.columns: tbl["Tanggal JT"]    =tbl["Tanggal JT"].dt.strftime("%d %b %Y")
    for c in ["Nilai Faktur","Nominal"]:
        if c in tbl.columns: tbl[c]=tbl[c].apply(R)
    tbl.rename(columns={"OVERDUE?":"Hari OD","KELOMPOK":"Kelompok","Grouping OS":"Grouping OS"},inplace=True)
    tbl.insert(0,"#",range(1,len(tbl)+1))
    with st.expander(f"Tampilkan {D(len(tbl))} baris · OS Total: {M(tn)}",expanded=False):
        st.dataframe(tbl,use_container_width=True,hide_index=True,height=440)
        dl_btn(dff[cols_ok],"RDI_DETAIL","Download Detail Faktur RDI")



def preload_all():
    """
    Muat OTC + GT + RDI secara paralel menggunakan threading.
    Dipanggil sekali di awal setelah login — hasilnya masuk ke cache Streamlit
    sehingga saat user klik tab, data sudah siap.
    """
    import threading

    results = {}

    def _load(name, fn):
        try:
            df, ts = fn()
            results[name] = (df, ts)
        except Exception as e:
            results[name] = (None, "–")

    threads = [
        threading.Thread(target=_load, args=("otc", load_otc)),
        threading.Thread(target=_load, args=("gt",  load_gt)),
        threading.Thread(target=_load, args=("rdi", load_rdi)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


# ═══════════════════════════════════════════════════════════════
# AUTH — Login dengan NIK + Password
# ═══════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def load_users() -> dict:
    """Ambil daftar user dari tabel app_users di Supabase."""
    try:
        sb   = get_sb()
        resp = sb.table("app_users").select("nik,nama,password,akses_proyek").execute()
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
        display: none;
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

    st.markdown(f"""
    <div class="login-wrap">
      <div style="display:flex;align-items:center;justify-content:center;margin-bottom:24px">
        <img src="data:image/png;base64,UklGRpCoAQBXRUJQVlA4WAoAAAAQAAAA/w8A/wgAQUxQSFfHAAAN/yckSPD/eGtEpO5JjNy2jeTK/v+vuyQ5zZwiYgIyfX3SaakStSimMAhUfqSZPB2n1oCvNU2XqbKBC/X2Rs+pAjAQv1Z5ADQcIINsc5rjFnmutu9mrr+8r2vbls2Jtm3djvOyco1VFAkJTvCmabfH/Zl7bfb9Re7u0jctSEMTIoQQIIG4ayXlXnXJeWwTVQndPM/zdvd1juOqiP5PAFAg/v6jiEjvtrY9a2vb1v08b/oCoGC3NtIM539eI7ZmWxLwhTc9zw+JKIRn6cLTEf2fAN22tjduJGnvB4RD+KCRlGXG3v8lzW+7KpUSTXgPfAepNiJLS1oEDyL6PwH6sG1bJqnxrud5v+ruUYYRGJjgEgjuCYMzBA9BE8K6b9zdsxuX3WTdkt/GhRAjDBLcgzuEYXCXYbS763uf+4/vq6qvKj2/I8PmOCqi/xPA0P9D//vvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///5v+n/T/5v+3/T/pv83/b/p/03/b/p/0/+b/t/0/6b/N/2/6f9N/2/6f9P/m/7f9P+m/zf9v+n/Tf9v+n/T/5v+3/T/pv9TxaYh/0ymYf4MM0lD/JGwCNPwfk7yiBjij+RD/llKlnMwvH+iICI0vB+JIkqG+DNzUAzzhyExzL9bUoSG93NaHhGh4f1SqyjLnE1D+42MtsqJyczQ/gaJkIb3i4xSYoh/hZl7aIg/zM0ihvczS8kiZw3thxUtoiwZ4t8LWRnD+4kipZwDDetnarXcJtrD+0Eq3Mq2GNZfpFSozMP8uZtnScP6IcxMYmh/GeauiKH9qq1UZjSsnwVeeI5gWH9hVlhkNKxfNRVSjuH9rCxzjN6snxGlYMe4WT+MSplji836m0i1kseYb9ovEsplWnncrB82lRKx6c362ahUio5xs35gysExetN+RqFkWpv3A2dZoBk37xcphbKb+eb9gFI51Fub9TMmZFlo5pv1wyaovJk/HClVQ6MlDe8XQi1rtDysny1ltdJaMzKcvzHKqlmjZQ3nBzEqlEutGBnazwqlkNsa0s8CSUSG9DOWQzm0HBnaPw+qZHkeNaxfhFDNnDeH9sOEcpnYyEP62RBKpZLXhvXDlkqlMqvlcH62EVmW0cqmYfwwUUEhU1NiOP/cysjKbmWG9HeUpCrN0JB+6xWy0MrD+dnrsqykZkjD+EGMzpTVaGQxnH8rQqnUlTXKrCH9mmSh1lNqTJQxlJ/XZ1lXqRmTGs4PkEM1i2U5rJ+BUJIiD+cHGCGFCIbyV25QFkKwdqAh/HCEEFQqaTIzjL+dSwrlUIp21jB+REdKIZQyTQRD+dsmUyiVop01nF+UnGVZRRMRGsoPi5CVqjGeg6H8IgSyUoV2GRq+z0RLBIWKlVEy3L6QIv4W2HaQyMoWbWm4PVSCGP0twM5LUiiZohxyTyEEYuvbKLeQCOWk3B5yj1AOajX4llZESFnmFpMx7F6WhdiI34KIpeBQ8aI9GWioPWVZKa/72xBBQpXCy8nMkPtZKMVm/DZRdgYhFKZ2aLg9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/WCNbDtqBW++QjYY0wjIXPwOamWzEmpALDsFWQWxA2Fn3UmtbDpBw9JfXy+riC2Iylsul1VkC4negrvPcDqOEQ0F1/1lnWy6EQ0FN5/VklFdMIII7j+VppU1Nm0MwJXpnPnK17GKbFOMhoN//xdqZTs6EHzsJ7LeVKbpMwEctek5uPpvjKps1ggx1AS88AiqIAZ//IFOgHoTTz2FKoj+lvdPojpQ/8QTz6AKosu723WNivHfgGoQDQbuqx+79/Zljz+zdi2di2jTtESyVU8sv3P5Y8+9sLakyyJKBvHudl33tmw1AoE6iBUP1yC6fOhFNBi1YtXyOkTT9sAqVFMbd0UdAjUFTz+JKl0+vAJVEM2O3x+dQA3BU0+jCqKf+b42qglqJ+5trN5TRKZb8cAaVEGgpmDt/XWIqnjsOdRbfaHINClWL1cNYvhJMzrHwOF0lmjSjI5SX3A6SwyiGZ2jk9NR6g3M6DZ6gwgzAAFYjdr0NcuMqqhajdoMptMxupFTH3RpVgfRyRnUqIBZB4iG5HQpgdNZonkzOko1TmepEZzOQfNmdI4+4HSOGrwvImd6NqOjRPNmHSComtGwaNO4GZ1j6Ampi9/C6KJhqVO/o4sBlbroMjo1K3XVsFSpVU3/pZp61QxsdOo+OnQtdeoyBqaj1EXj0U01uuir1KljdNF0dNFPqYu+Rhcdoy/NSp36KnVRLzXVV6mLof+H/h/6f+j/of+H/h/6f+j/of+H/h/6f+j/of+H/h/6f+j/of+H/h/6f+j/of+H/h/6f+j/of+H/h/6f+j/of+H/h/6f+h///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9978KAFZQOCAS4QAA0AYKnQEqABAACT5tNppJpD+/qqCR2CPwDYlpbv/J55+60S2kpVnYuR+u4adXFzp/6F+QDxP44d0dI2xCoS+gG/0Er/DP29/tvDf8w8p/8RvyA+5Ri347vrgeYPanPADp96f9sfyP9v/ov3B/f/zHYz9ofkv8t+1n+C/aP6MLf/ef8B/kP8h/ff2L+7j+h/5PLX3j/o+c95j+0f7r/E/k38xP+p/2/8f+5Xy4/UH/p/0HwEfx/+g/6T+9f5//4f47/////62v+l/hvfz+8H/Z/Zn4G/0//C/9b/Rfvx8uv/S/9H/F95P9o/4f7h/9D5Bv6f/cP/l/w/e+/4///91f/F/9D///9z4E/5z/of/R7PP/V/9n+2/fn/2/Zv/Tv9x/9f9P/zP/z/3vsL/mf9w/9H7W//3/r/QB/0v//7AH/Z/9vuU/wD9+vcv6+/3r8Xf2q8qv9b/gf83/p/3m/wPoj+rfy/5lfvB/pOnXGn+d/k/Or/geCPzl1FPzX+v75fcv9qPYU+Dfv3mafg/tB65/af/ze4L/Sf796g/8vxo/tf/W/bv4CP5f/e//R/mfZ1/9v9n6J/rT/6+4P/N/7j+yntu///23/uV///+v8Ef62/+YDPjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx4Bvu1U4e8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx4CMUx9WLqacPcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjdGyDR9hKVOHvJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eAMlkxyoviFOHvJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eAMdNnN+hK4vgvysoB7yf6PHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eNxY0Ugitnga/Ppfcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePG6OGYixz3kdhxLp3bdH3JxXK/ZAj/R48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48BBbR2VXHvTRkJBcRE+uvoxpFVfT3GnvJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eNxgR1w/wVxaJPyE+ptbG/WqnD3k/0ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eABf57OgTi91wBKgiG8ezPJbmBAPeT/R48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHgHOWAr4H4H4GzNKAR/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjwBVnOGQYYNlWOxNoGvKNxZ7iZiFaBjGnvJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjc5p8piVw7aTWLie2OsL5/OY+aqcb5FN47Uf94eMXeZir1eb/wNsOhx+Pq4/9wze/6iyit+/41BE5WFbvHPtIecn0qNeQVC5KMhvSnbr7TStrNh7jT3k/0ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjdCdSES/a3T+Q03htST0hpmz9Anw7pbc2LWPHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48A5ywEOFfluXHJTJ40sv07s8kSKYhzvBZGTtHfA68/A/A/A/A/A/s5OqjKkiTou0E+Z6axkYhQayiTjbJ7t+0L18xcH6PHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePAQTFAWhMfjt9Hil2hPXv6TWneGuut+j+mnvJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjwDfdocF7yUzpt7om0P+pCSMuCUFVHw7/l4H4HXn9x8D8D8DssemKRHl9nQ/GZf9f0aOkjZqTbMA/LLfpUAR/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjwD/avkHP9kGmk0Vudg2ingWM+xB1maUAj/R48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eAb7tCzoHMdN5llziy8nmtLSGxVd2Yj+B3UfuNeLjet2fwP7j69xlLlDaIf/l5QrXSQt9zAsuPaOv79x2D9IejJVSHvRIHtLqx8Pf6AMRUCWIUeB+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjwBNLFkbcZYWj4ktkh1brMPj41dCIK1U1rM0oBH+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjxub7tDgvdp2zq0q6CX3h3YluEvDYX9X9X9XyXEOmH5T34MkLlOaUz0kLYNev///9Yg5X3//1QDegc9PRn7gvlpkMI6iLJ4QjeT/R48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjwBaeC9NUmF/kZC2K/Xc0fkkoPeotRQrp9p6JpzQXjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eAb7tDh9v5JooBIKgRXiGbfjI1H9C+4BPWk1tP9X/KdbyBJaYR//+J/X/////Vf0aN9tiy5QtEY7kwfws/0ePHjca3eUZmxcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48bi/QdljuCevToAcDc0hTWjtZe+TXndwGMAVb1Vnh7jT3k/0ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjcOPkAM6xEUBvUBAJfM3wlLbcl/0LwP2e96YJMvcdhspXV7//lf2/8///ov//++Sb2KOeZXGnvJ/o8AwE5VV9Pcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjwBmL1QRBVPqZUOjQFbfe7O3jWVXtvt2RM0/dJCU5gQD3k/0ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePG5vu0OGo486sCQ+FgTTiFVef3H2XGIXjaehyJb6JX/E/////BfoX/+Ce5esHygoPGdYsOvo8ePHgpFW4vJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjxub8Bs4NzH95izHAzxDSMOXdZZA2c+8lvmOSzHPq0kJmVmID8DzmnuNPeT/R48ePHjx48ePHjx48ePHjx48ePHjx48eNzfgZp02xdGImPAV/g8UnVeVq/3H2W45M+/K5J5t73+9s////99//9vi2uGfI+iz7XsFh5zT3GnvJ/oAZIwnDKr6e4095P9Hjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePG6D8Dflb45wlLxVSOEFncVMGn0CFgsdGnb0JiyycZtK5cPeT/R48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx4Bvu0Vg1sJyJq2WIOM3LhjhjKxnvZSb4sOnDQhyz/777P+heee7kI6+4lFV9Pcae8n+jx48bsTAYF+wriW0oBH+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eNxVvg1/0OZpBmyAoTCzwtUT/M0cDPute0i/PtEIH5OYEA95P9Hjx48ePHjx48ePHjx48ePHjx48ePHjx48eAb7tFd5xsiVWvIgG4LVAIyVTO/y9DM5FX27JuXv/////tehcB66olAyf6PHjx48ePHjx48ePAYA653TT3k/0ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx43GTf+wFZ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nHrFAT3h9B+zD+7G6/qJ+Qeadv5O8mj3E4qLDq6111c7vdWlWr2Qdj/10ZYgnQ4No8FJ9L3nPgvFj5CwvJ9kgj6Q19OxRTqTds3kNGTfoj9TOiuGDSQgZVfT3GnvJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48BCeE6fzAGcy+Ltm9SMq/KWEhn6BWJkMBpH5yxvpFhNkQ27XDuqOECQ4ij/mALfFnBxFsu03/tnZwf18PVtmB28SrMBeEVM/JE0yVkuYEA95P9Hjx48ePHjx48ePHjx48ePHjx48A9wagVfT+XsmDP0PKLozNmdZsuVKAjWlzyIzpp8gUPIwh+PbxI/8Rt1sCldr+8IOQCgJwyq+nuNPeT/R48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eAtededededededededededz5xgEawR0rIfykasjMYczNKAR/o8ePHjx48ePHjx48ePHjx48ePHjdCQYV11nMyf6PHjx48ePHjx48ePHjx4+z43GO87lYAsDALanDKr6e4095P9Hjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHgIqbRBLlDCnShzOYEA95P9Hjx48ePHjx48ePHjx48ePHjx48Aze+bW6wllA9Hjx48ePHjx48ePHjx48eXv/KiL759aFXAct2j/PkLWPHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjxuMyVvj+5XEHYhvH1Th7yf6PHjx48ePHjx48ePHjx48ePHjx48biNjoF5BH+jx48ePHjx48ePHjx48fmO2XtkyI9KPG4HQrxBztfR48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eAFhJIPeyB75XYXyaFw9xp7yf6PHjx48ePHjx48ePHjx48ePHjx4AsPxTh/0TePHjx48ePHjx48ePHjx+/tP6nU/XQEGCd4u/cU4ZVfT3GnvJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eN0J1TCBg63BTOmS3JX3SlTh7yf6PHjx48ePHjx48ePHjx48ePHjx48bh10w6fCzNKAR/o8ePHjx48ePHlt//V2/x+a/wmDv8NpVuLyf6PHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjcIYdYmwxJvpFgMpLVL9Z1DGCLOuTVX8ov47/85lac0BmBZ0uSWqlbF+bSu7kLdfLZDx7FCbK0/Bsfjlyp3Cs18XtbF2lteJDaa+STGEaQxhd7Qn1msWiq+nuNPeT/R48ePHjx48ePHjwFrwdt9Pcae8n+jx48ePG+pH/nNZwU1b1Vh6JkNo/+VThlV9Pcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx43N5BzQjFSguy2mU23I5kgjHnLXl3FeWzFGZgsQWerRglirc8VZiVTJdpxsxvh4/DvFDKyC3DGSU6GjFxVeb+15v6/r+yoec09xp7yf6PHjx48ePHjx48ePAGYPFpiIWZpQCP9Hjx48ePAbwfwwTaW0D14rkzV/SZDq7w5FeYbJP9Hjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx4Bvu0OOBDGhUrWA5//nBeVemCGJZxlVPYQMpTOPhimBEnqmayeFRmCysj81AcBSxULbkK/t0nXOefAZPeT/R48ePHjx48ePHjx48ePHjx4C13CnpD0zciehw9Hjx48eA8vz2NTHBTjG1LP+EkIdE8wr5EnulV9Pcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjxub7kCu8ICyVl0utD/wy0rYZshSiaOwSNP/RvRAOIuP/wGSRE1jSYr+2x19Hjx48ePHjx48ePHjx48ePHjx48ePHjx48BI/VpPT9M053Ag7+vFUk/4pkolqJWW/wXwhJmIojIo0Df45qruQxK2KCo/PE8Yqvp7jT3k/0ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePAFd7P758wiHSPP/c9eyA0eABkzL9fughdon+sIln9NY8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx4AzBjn3aUSap/0hREY4H/LPTXbb3PpKedtuBqm99f/LQ7fZuzPjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePAN+Bmg5d8hdS/QOJ3136tqRkOhz0qsgjh3qGoG7Gnx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePAG2K2LEWE0nYOf8ajNGNSumQn89vR9xW3MMUy3/BJ2aES9P9Hjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjwEJ1ojASFzTUz2gQocgjdFoGXwnEQCdI7KQJ1KPnEE5VV9Pcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48Ba7vFu+QEgnT1j85eacarwl3oQ50y7iScmHYj/T6cHCB1w7v/B6yoec09xp7yf6PHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjxutededd89P2oudzlLK5v6I22HMBxeT/R48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48Ba8q8NTS5EWHP3t8KzlwaQ2//gfCB23mt5f9stPksStDCKGZxh/3ATqlKyYnx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx43WvOu6jOfv7m+ONVZf4NQy39nwHyBJHwyqzhVJVGdAYleI8BAFo4ucaW2jEgq2SvQWxUyoec09xp7yf6PHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePG615v7XgXPv8mpr9AD4B49b8XOvOvO5A7Rcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePG4AA/v70uAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMD+OIAAAAAAAAif8KJcTp05qDyraYT77BkVfmYwc3Yc0ZQO7AAAAAAAAP+W1Aang+RO3k/D2wX+89Mm4hzXGH32sigMGo4LQEp13aAPS07Tj3unQAAAAAAAAM5WnZYeq79WpQoFpFWqOB37ORpzouKOxt/uUXIDIQ5H2s9xOR6c6YgpuKZOVD8v4wAAAAAAAAyx7BmuJXeVd3zREmA3J1j7N5vwi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"
             style="height:120px;width:auto;object-fit:contain">
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
                    akses_raw = (user.get("akses_proyek") or "").strip()
                    if akses_raw.upper() == "ALL":
                        akses = "ALL"
                    else:
                        akses = [a.strip() for a in akses_raw.split(",") if a.strip()]
                    st.session_state["logged_in"]   = True
                    st.session_state["user_nik"]    = nik.strip()
                    st.session_state["user_nama"]   = user["nama"]
                    st.session_state["user_akses"]  = akses
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
                    # Clear cache dan reset session agar login ulang dengan password baru
                    load_users.clear()
                    st.session_state["pwd_changed"] = True
                    st.success("Password berhasil diperbarui. Silakan login ulang.")
                    # Otomatis logout setelah 2 detik agar user login dengan password baru
                    import time as _time
                    _time.sleep(1.5)
                    for k in ["logged_in","user_nik","user_nama","user_akses"]:
                        st.session_state.pop(k, None)
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menyimpan: {e}")


PROJECTS = [
    {
        "key": "fad_arotc",
        "title": "AR Outstanding",
        "subtitle": "Channel MT, GT, RDI",
        "active": True,
    },
    {
        "key": "proyek_b",
        "title": "Proyek B",
        "subtitle": "COMING SOON!",
        "active": False,
    },
    {
        "key": "proyek_c",
        "title": "Proyek C",
        "subtitle": "COMING SOON!",
        "active": False,
    },
]


PROJECT_ICONS = {
    "fad_arotc": "📈",
    "proyek_b":  "🛠️",
    "proyek_c":  "📐",
}
PROJECT_ICON_BG = {
    "fad_arotc": "linear-gradient(135deg,#EDE9FE,#DBEAFE)",
    "proyek_b":  "linear-gradient(135deg,#FEF3C7,#FDE68A)",
    "proyek_c":  "linear-gradient(135deg,#DBEAFE,#BFDBFE)",
}


LOGO_B64 = "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"


def render_project_picker():
    """Halaman pilih proyek — tampil setelah login, sebelum masuk ke dashboard."""
    nama = st.session_state.get("user_nama", "")

    st.markdown(f"""
    <div style="text-align:center; margin-bottom:20px; padding:28px 20px;
                border-radius:20px; height:150px; display:flex; align-items:center;
                justify-content:center; overflow:hidden; position:relative;
                background:linear-gradient(135deg,#B01C2E 0%,#7A1420 100%);">
        <img src="data:image/png;base64,{LOGO_B64}"
             style="width:380px; max-width:70vw; height:auto; opacity:0.9;
                    filter:brightness(0) invert(1); opacity:0.16;">
        <div style="position:absolute; color:#FFFFFF; font-size:15px; font-weight:600;
                    letter-spacing:1px; opacity:0.9;">PT. PINUS MERAH ABADI</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .pp-header { display:flex; align-items:flex-start; justify-content:space-between;
                 margin-bottom:8px; padding-top:4px; position:relative; z-index:1; }
    .pp-greet { font-size:15px; color:#6B7280; font-weight:500; line-height:1.3; }
    .pp-greet b { color:#111827; font-weight:700; }
    .pp-title { font-size:30px; font-weight:800; color:#111827; margin-top:2px; }
    .pp-bell { font-size:20px; background:#F3F4F6; border-radius:50%; width:44px; height:44px;
               display:flex; align-items:center; justify-content:center; flex-shrink:0; }
    .pp-card { border:1px solid #ECECEC; border-radius:18px; padding:22px 22px 18px;
               margin-bottom:14px; background:#FFFFFF; box-shadow:0 2px 8px rgba(0,0,0,0.05);
               height:190px; display:flex; flex-direction:column; justify-content:space-between;
               position:relative; z-index:1; }
    .pp-card.pp-disabled { background:#FAFAFA; opacity:0.7; }
    .pp-icon { width:56px; height:56px; border-radius:16px; display:flex; align-items:center;
               justify-content:center; font-size:26px; margin-bottom:14px;
               box-shadow: inset 0 0 0 1px rgba(0,0,0,0.03); }
    .pp-card-title-row { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
    .pp-card-title { font-size:16.5px; font-weight:700; color:#111827; }
    .pp-badge-wip { font-size:10px; font-weight:700; color:#B01C2E; background:#FCE8EA;
                    padding:3px 9px; border-radius:999px; white-space:nowrap; }
    .pp-card-subtitle { font-size:12.5px; color:#9CA3AF; margin-top:4px; }
    .stButton > button {
        background: linear-gradient(135deg,#B01C2E,#E0293D) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 999px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 10px 0 !important;
        box-shadow: 0 4px 10px rgba(176,28,46,0.28) !important;
    }
    .stButton > button:disabled {
        background: #D1D5DB !important;
        color: #9CA3AF !important;
        box-shadow: none !important;
        opacity: 1 !important;
    }
    </style>
    <div class="pp-header">
        <div>
            <div class="pp-greet">Halo, <b>""" + nama + """!</b></div>
            <div class="pp-title">Pilih Proyek</div>
        </div>
        <div class="pp-bell">🔔</div>
    </div>
    <hr style='margin:8px 0 22px;border-color:#ECECEC'>
    """, unsafe_allow_html=True)

    akses = st.session_state.get("user_akses", [])
    cols = st.columns(3)
    for i, p in enumerate(PROJECTS):
        boleh_akses = (akses == "ALL") or (p["key"] in akses)
        subtitle = p["subtitle"] if boleh_akses else "Tidak ada akses"
        icon = PROJECT_ICONS.get(p["key"], "📁")
        icon_bg = PROJECT_ICON_BG.get(p["key"], "#F3F4F6")
        wip_badge = "" if p["active"] else '<span class="pp-badge-wip">Work in Progress</span>'
        with cols[i % 3]:
            card_html = (
                f'<div class="pp-card {"" if boleh_akses else "pp-disabled"}">'
                f'<div>'
                f'<div class="pp-icon" style="background:{icon_bg}">{icon}</div>'
                f'<div class="pp-card-title-row">'
                f'<span class="pp-card-title">{p["title"]}</span>'
                f'{wip_badge}'
                f'</div>'
                f'<div class="pp-card-subtitle">{subtitle}</div>'
                f'</div>'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)
            btn_label = "Go to Dashboard" if p["active"] else "Buka"
            if boleh_akses:
                if st.button(btn_label, key=f"open_{p['key']}", use_container_width=True):
                    st.session_state["active_project"] = p["key"]
                    st.rerun()
            else:
                st.button(btn_label, key=f"open_{p['key']}", use_container_width=True, disabled=True)

    with st.sidebar:
        st.markdown(
            "<div style='font-size:11px;font-weight:700;color:#B01C2E;"
            "text-transform:uppercase;letter-spacing:.8px;padding:4px 0 8px'>Akun</div>",
            unsafe_allow_html=True)
        if st.button("Refresh Akses", use_container_width=True, key="refresh_akses_picker"):
            load_users.clear()
            # muat ulang data akses user yang sedang login, tanpa perlu login ulang
            users = load_users()
            u = users.get(st.session_state.get("user_nik"))
            if u:
                akses_raw = (u.get("akses_proyek") or "").strip()
                st.session_state["user_akses"] = "ALL" if akses_raw.upper()=="ALL" else \
                    [a.strip() for a in akses_raw.split(",") if a.strip()]
            st.rerun()
        if st.button("Keluar", use_container_width=True, key="logout_btn_picker"):
            for k in ["logged_in","user_nik","user_nama","user_akses","preloaded","active_project"]:
                st.session_state.pop(k, None)
            st.rerun()


def render_coming_soon(proj: dict):
    """Halaman placeholder untuk proyek yang sudah bisa diakses tapi belum jadi."""
    with st.sidebar:
        st.markdown(
            "<div style='font-size:11px;font-weight:700;color:#B01C2E;"
            "text-transform:uppercase;letter-spacing:.8px;padding:4px 0 8px'>Akun</div>",
            unsafe_allow_html=True)
        if st.button("Ganti Proyek", use_container_width=True, key="switch_project_btn_cs"):
            st.session_state.pop("active_project", None)
            st.rerun()
        if st.button("Keluar", use_container_width=True, key="logout_btn_cs"):
            for k in ["logged_in","user_nik","user_nama","user_akses","preloaded","active_project"]:
                st.session_state.pop(k, None)
            st.rerun()

    st.markdown(f"""
    <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;
                min-height:60vh;text-align:center'>
        <div style='font-size:13px;font-weight:600;color:#9CA3AF;text-transform:uppercase;
                    letter-spacing:1px;margin-bottom:12px'>{proj["title"]}</div>
        <div style='font-size:48px;font-weight:800;color:#B01C2E;letter-spacing:-1px'>COMING SOON!</div>
        <div style='font-size:14px;color:#9CA3AF;margin-top:16px;max-width:420px'>
            Proyek ini sedang dalam pengembangan. Kamu akan diberi tahu begitu sudah siap digunakan.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("← Kembali ke Pilih Proyek", key="back_to_picker_cs"):
        st.session_state.pop("active_project", None)
        st.rerun()


def main():
    if not check_login():
        return

    # Belum pilih proyek → tampilkan halaman pemilihan proyek dulu
    if not st.session_state.get("active_project"):
        render_project_picker()
        return

    # Proyek dipilih tapi belum benar-benar jadi → tampilkan placeholder Coming Soon
    _proj = next((p for p in PROJECTS if p["key"] == st.session_state["active_project"]), None)
    if _proj and not _proj["active"]:
        render_coming_soon(_proj)
        return

    # Preload semua data paralel (sekali, hasilnya di-cache)
    if not st.session_state.get("preloaded"):
        with st.spinner("Memuat data dashboard..."):
            preload_all()
        st.session_state["preloaded"] = True

    # Tombol logout di sidebar
    with st.sidebar:
        nama = st.session_state.get("user_nama", "")
        nik  = st.session_state.get("user_nik", "")
        st.markdown(
            f"<div style='padding:8px 0 4px;text-align:center'>"
            f"<img src='data:image/png;base64,UklGRpCoAQBXRUJQVlA4WAoAAAAQAAAA/w8A/wgAQUxQSFfHAAAN/yckSPD/eGtEpO5JjNy2jeTK/v+vuyQ5zZwiYgIyfX3SaakStSimMAhUfqSZPB2n1oCvNU2XqbKBC/X2Rs+pAjAQv1Z5ADQcIINsc5rjFnmutu9mrr+8r2vbls2Jtm3djvOyco1VFAkJTvCmabfH/Zl7bfb9Re7u0jctSEMTIoQQIIG4ayXlXnXJeWwTVQndPM/zdvd1juOqiP5PAFAg/v6jiEjvtrY9a2vb1v08b/oCoGC3NtIM539eI7ZmWxLwhTc9zw+JKIRn6cLTEf2fAN22tjduJGnvB4RD+KCRlGXG3v8lzW+7KpUSTXgPfAepNiJLS1oEDyL6PwH6sG1bJqnxrud5v+ruUYYRGJjgEgjuCYMzBA9BE8K6b9zdsxuX3WTdkt/GhRAjDBLcgzuEYXCXYbS763uf+4/vq6qvKj2/I8PmOCqi/xPA0P9D//vvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///7777///vvvv//++++///5v+n/T/5v+3/T/pv83/b/p/03/b/p/0/+b/t/0/6b/N/2/6f9N/2/6f9P/m/7f9P+m/zf9v+n/Tf9v+n/T/5v+3/T/pv9TxaYh/0ymYf4MM0lD/JGwCNPwfk7yiBjij+RD/llKlnMwvH+iICI0vB+JIkqG+DNzUAzzhyExzL9bUoSG93NaHhGh4f1SqyjLnE1D+42MtsqJyczQ/gaJkIb3i4xSYoh/hZl7aIg/zM0ihvczS8kiZw3thxUtoiwZ4t8LWRnD+4kipZwDDetnarXcJtrD+0Eq3Mq2GNZfpFSozMP8uZtnScP6IcxMYmh/GeauiKH9qq1UZjSsnwVeeI5gWH9hVlhkNKxfNRVSjuH9rCxzjN6snxGlYMe4WT+MSplji836m0i1kseYb9ovEsplWnncrB82lRKx6c362ahUio5xs35gysExetN+RqFkWpv3A2dZoBk37xcphbKb+eb9gFI51Fub9TMmZFlo5pv1wyaovJk/HClVQ6MlDe8XQi1rtDysny1ltdJaMzKcvzHKqlmjZQ3nBzEqlEutGBnazwqlkNsa0s8CSUSG9DOWQzm0HBnaPw+qZHkeNaxfhFDNnDeH9sOEcpnYyEP62RBKpZLXhvXDlkqlMqvlcH62EVmW0cqmYfwwUUEhU1NiOP/cysjKbmWG9HeUpCrN0JB+6xWy0MrD+dnrsqykZkjD+EGMzpTVaGQxnH8rQqnUlTXKrCH9mmSh1lNqTJQxlJ/XZ1lXqRmTGs4PkEM1i2U5rJ+BUJIiD+cHGCGFCIbyV25QFkKwdqAh/HCEEFQqaTIzjL+dSwrlUIp21jB+REdKIZQyTQRD+dsmUyiVop01nF+UnGVZRRMRGsoPi5CVqjGeg6H8IgSyUoV2GRq+z0RLBIWKlVEy3L6QIv4W2HaQyMoWbWm4PVSCGP0twM5LUiiZohxyTyEEYuvbKLeQCOWk3B5yj1AOajX4llZESFnmFpMx7F6WhdiI34KIpeBQ8aI9GWioPWVZKa/72xBBQpXCy8nMkPtZKMVm/DZRdgYhFKZ2aLg9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/WCNbDtqBW++QjYY0wjIXPwOamWzEmpALDsFWQWxA2Fn3UmtbDpBw9JfXy+riC2Iylsul1VkC4negrvPcDqOEQ0F1/1lnWy6EQ0FN5/VklFdMIII7j+VppU1Nm0MwJXpnPnK17GKbFOMhoN//xdqZTs6EHzsJ7LeVKbpMwEctek5uPpvjKps1ggx1AS88AiqIAZ//IFOgHoTTz2FKoj+lvdPojpQ/8QTz6AKosu723WNivHfgGoQDQbuqx+79/Zljz+zdi2di2jTtESyVU8sv3P5Y8+9sLakyyJKBvHudl33tmw1AoE6iBUP1yC6fOhFNBi1YtXyOkTT9sAqVFMbd0UdAjUFTz+JKl0+vAJVEM2O3x+dQA3BU0+jCqKf+b42qglqJ+5trN5TRKZb8cAaVEGgpmDt/XWIqnjsOdRbfaHINClWL1cNYvhJMzrHwOF0lmjSjI5SX3A6SwyiGZ2jk9NR6g3M6DZ6gwgzAAFYjdr0NcuMqqhajdoMptMxupFTH3RpVgfRyRnUqIBZB4iG5HQpgdNZonkzOko1TmepEZzOQfNmdI4+4HSOGrwvImd6NqOjRPNmHSComtGwaNO4GZ1j6Ampi9/C6KJhqVO/o4sBlbroMjo1K3XVsFSpVU3/pZp61QxsdOo+OnQtdeoyBqaj1EXj0U01uuir1KljdNF0dNFPqYu+Rhcdoy/NSp36KnVRLzXVV6mLof+H/h/6f+j/of+H/h/6f+j/of+H/h/6f+j/of+H/h/6f+j/of+H/h/6f+j/of+H/h/6f+j/of+H/h/6f+j/of+H/h/6f+h///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9999///3333///ffff//9978KAFZQOCAS4QAA0AYKnQEqABAACT5tNppJpD+/qqCR2CPwDYlpbv/J55+60S2kpVnYuR+u4adXFzp/6F+QDxP44d0dI2xCoS+gG/0Er/DP29/tvDf8w8p/8RvyA+5Ri347vrgeYPanPADp96f9sfyP9v/ov3B/f/zHYz9ofkv8t+1n+C/aP6MLf/ef8B/kP8h/ff2L+7j+h/5PLX3j/o+c95j+0f7r/E/k38xP+p/2/8f+5Xy4/UH/p/0HwEfx/+g/6T+9f5//4f47/////62v+l/hvfz+8H/Z/Zn4G/0//C/9b/Rfvx8uv/S/9H/F95P9o/4f7h/9D5Bv6f/cP/l/w/e+/4///91f/F/9D///9z4E/5z/of/R7PP/V/9n+2/fn/2/Zv/Tv9x/9f9P/zP/z/3vsL/mf9w/9H7W//3/r/QB/0v//7AH/Z/9vuU/wD9+vcv6+/3r8Xf2q8qv9b/gf83/p/3m/wPoj+rfy/5lfvB/pOnXGn+d/k/Or/geCPzl1FPzX+v75fcv9qPYU+Dfv3mafg/tB65/af/ze4L/Sf796g/8vxo/tf/W/bv4CP5f/e//R/mfZ1/9v9n6J/rT/6+4P/N/7j+yntu///23/uV///+v8Ef62/+YDPjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx4Bvu1U4e8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx4CMUx9WLqacPcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjdGyDR9hKVOHvJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eAMlkxyoviFOHvJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eAMdNnN+hK4vgvysoB7yf6PHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eNxY0Ugitnga/Ppfcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePG6OGYixz3kdhxLp3bdH3JxXK/ZAj/R48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48BBbR2VXHvTRkJBcRE+uvoxpFVfT3GnvJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eNxgR1w/wVxaJPyE+ptbG/WqnD3k/0ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eABf57OgTi91wBKgiG8ezPJbmBAPeT/R48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHgHOWAr4H4H4GzNKAR/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjwBVnOGQYYNlWOxNoGvKNxZ7iZiFaBjGnvJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjc5p8piVw7aTWLie2OsL5/OY+aqcb5FN47Uf94eMXeZir1eb/wNsOhx+Pq4/9wze/6iyit+/41BE5WFbvHPtIecn0qNeQVC5KMhvSnbr7TStrNh7jT3k/0ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjdCdSES/a3T+Q03htST0hpmz9Anw7pbc2LWPHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48A5ywEOFfluXHJTJ40sv07s8kSKYhzvBZGTtHfA68/A/A/A/A/A/s5OqjKkiTou0E+Z6axkYhQayiTjbJ7t+0L18xcH6PHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePAQTFAWhMfjt9Hil2hPXv6TWneGuut+j+mnvJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjwDfdocF7yUzpt7om0P+pCSMuCUFVHw7/l4H4HXn9x8D8D8DssemKRHl9nQ/GZf9f0aOkjZqTbMA/LLfpUAR/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjwD/avkHP9kGmk0Vudg2ingWM+xB1maUAj/R48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eAb7tCzoHMdN5llziy8nmtLSGxVd2Yj+B3UfuNeLjet2fwP7j69xlLlDaIf/l5QrXSQt9zAsuPaOv79x2D9IejJVSHvRIHtLqx8Pf6AMRUCWIUeB+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjwBNLFkbcZYWj4ktkh1brMPj41dCIK1U1rM0oBH+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjxub7tDgvdp2zq0q6CX3h3YluEvDYX9X9X9XyXEOmH5T34MkLlOaUz0kLYNev///9Yg5X3//1QDegc9PRn7gvlpkMI6iLJ4QjeT/R48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjwBaeC9NUmF/kZC2K/Xc0fkkoPeotRQrp9p6JpzQXjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eAb7tDh9v5JooBIKgRXiGbfjI1H9C+4BPWk1tP9X/KdbyBJaYR//+J/X/////Vf0aN9tiy5QtEY7kwfws/0ePHjca3eUZmxcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48bi/QdljuCevToAcDc0hTWjtZe+TXndwGMAVb1Vnh7jT3k/0ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjcOPkAM6xEUBvUBAJfM3wlLbcl/0LwP2e96YJMvcdhspXV7//lf2/8///ov//++Sb2KOeZXGnvJ/o8AwE5VV9Pcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjwBmL1QRBVPqZUOjQFbfe7O3jWVXtvt2RM0/dJCU5gQD3k/0ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePG5vu0OGo486sCQ+FgTTiFVef3H2XGIXjaehyJb6JX/E/////BfoX/+Ce5esHygoPGdYsOvo8ePHgpFW4vJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjxub8Bs4NzH95izHAzxDSMOXdZZA2c+8lvmOSzHPq0kJmVmID8DzmnuNPeT/R48ePHjx48ePHjx48ePHjx48ePHjx48eNzfgZp02xdGImPAV/g8UnVeVq/3H2W45M+/K5J5t73+9s////99//9vi2uGfI+iz7XsFh5zT3GnvJ/oAZIwnDKr6e4095P9Hjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePG6D8Dflb45wlLxVSOEFncVMGn0CFgsdGnb0JiyycZtK5cPeT/R48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx4Bvu0Vg1sJyJq2WIOM3LhjhjKxnvZSb4sOnDQhyz/777P+heee7kI6+4lFV9Pcae8n+jx48bsTAYF+wriW0oBH+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eNxVvg1/0OZpBmyAoTCzwtUT/M0cDPute0i/PtEIH5OYEA95P9Hjx48ePHjx48ePHjx48ePHjx48ePHjx48eAb7tFd5xsiVWvIgG4LVAIyVTO/y9DM5FX27JuXv/////tehcB66olAyf6PHjx48ePHjx48ePAYA653TT3k/0ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx43GTf+wFZ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nHrFAT3h9B+zD+7G6/qJ+Qeadv5O8mj3E4qLDq6111c7vdWlWr2Qdj/10ZYgnQ4No8FJ9L3nPgvFj5CwvJ9kgj6Q19OxRTqTds3kNGTfoj9TOiuGDSQgZVfT3GnvJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48BCeE6fzAGcy+Ltm9SMq/KWEhn6BWJkMBpH5yxvpFhNkQ27XDuqOECQ4ij/mALfFnBxFsu03/tnZwf18PVtmB28SrMBeEVM/JE0yVkuYEA95P9Hjx48ePHjx48ePHjx48ePHjx48A9wagVfT+XsmDP0PKLozNmdZsuVKAjWlzyIzpp8gUPIwh+PbxI/8Rt1sCldr+8IOQCgJwyq+nuNPeT/R48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eAtededededededededededz5xgEawR0rIfykasjMYczNKAR/o8ePHjx48ePHjx48ePHjx48ePHjdCQYV11nMyf6PHjx48ePHjx48ePHjx4+z43GO87lYAsDALanDKr6e4095P9Hjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHgIqbRBLlDCnShzOYEA95P9Hjx48ePHjx48ePHjx48ePHjx48Aze+bW6wllA9Hjx48ePHjx48ePHjx48eXv/KiL759aFXAct2j/PkLWPHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjxuMyVvj+5XEHYhvH1Th7yf6PHjx48ePHjx48ePHjx48ePHjx48biNjoF5BH+jx48ePHjx48ePHjx48fmO2XtkyI9KPG4HQrxBztfR48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eAFhJIPeyB75XYXyaFw9xp7yf6PHjx48ePHjx48ePHjx48ePHjx4AsPxTh/0TePHjx48ePHjx48ePHjx+/tP6nU/XQEGCd4u/cU4ZVfT3GnvJ/o8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48eN0J1TCBg63BTOmS3JX3SlTh7yf6PHjx48ePHjx48ePHjx48ePHjx48bh10w6fCzNKAR/o8ePHjx48ePHlt//V2/x+a/wmDv8NpVuLyf6PHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjcIYdYmwxJvpFgMpLVL9Z1DGCLOuTVX8ov47/85lac0BmBZ0uSWqlbF+bSu7kLdfLZDx7FCbK0/Bsfjlyp3Cs18XtbF2lteJDaa+STGEaQxhd7Qn1msWiq+nuNPeT/R48ePHjx48ePHjwFrwdt9Pcae8n+jx48ePG+pH/nNZwU1b1Vh6JkNo/+VThlV9Pcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx43N5BzQjFSguy2mU23I5kgjHnLXl3FeWzFGZgsQWerRglirc8VZiVTJdpxsxvh4/DvFDKyC3DGSU6GjFxVeb+15v6/r+yoec09xp7yf6PHjx48ePHjx48ePAGYPFpiIWZpQCP9Hjx48ePAbwfwwTaW0D14rkzV/SZDq7w5FeYbJP9Hjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx4Bvu0OOBDGhUrWA5//nBeVemCGJZxlVPYQMpTOPhimBEnqmayeFRmCysj81AcBSxULbkK/t0nXOefAZPeT/R48ePHjx48ePHjx48ePHjx4C13CnpD0zciehw9Hjx48eA8vz2NTHBTjG1LP+EkIdE8wr5EnulV9Pcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjxub7kCu8ICyVl0utD/wy0rYZshSiaOwSNP/RvRAOIuP/wGSRE1jSYr+2x19Hjx48ePHjx48ePHjx48ePHjx48ePHjx48BI/VpPT9M053Ag7+vFUk/4pkolqJWW/wXwhJmIojIo0Df45qruQxK2KCo/PE8Yqvp7jT3k/0ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePAFd7P758wiHSPP/c9eyA0eABkzL9fughdon+sIln9NY8ePHjx48ePHjx48ePHjx48ePHjx48ePHjx4AzBjn3aUSap/0hREY4H/LPTXbb3PpKedtuBqm99f/LQ7fZuzPjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePAN+Bmg5d8hdS/QOJ3136tqRkOhz0qsgjh3qGoG7Gnx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePAG2K2LEWE0nYOf8ajNGNSumQn89vR9xW3MMUy3/BJ2aES9P9Hjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjwEJ1ojASFzTUz2gQocgjdFoGXwnEQCdI7KQJ1KPnEE5VV9Pcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48Ba7vFu+QEgnT1j85eacarwl3oQ50y7iScmHYj/T6cHCB1w7v/B6yoec09xp7yf6PHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjxutededd89P2oudzlLK5v6I22HMBxeT/R48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48Ba8q8NTS5EWHP3t8KzlwaQ2//gfCB23mt5f9stPksStDCKGZxh/3ATqlKyYnx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx43WvOu6jOfv7m+ONVZf4NQy39nwHyBJHwyqzhVJVGdAYleI8BAFo4ucaW2jEgq2SvQWxUyoec09xp7yf6PHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePG615v7XgXPv8mpr9AD4B49b8XOvOvO5A7Rcae8n+jx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePHjx48ePG4AA/v70uAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMD+OIAAAAAAAAif8KJcTp05qDyraYT77BkVfmYwc3Yc0ZQO7AAAAAAAAP+W1Aang+RO3k/D2wX+89Mm4hzXGH32sigMGo4LQEp13aAPS07Tj3unQAAAAAAAAM5WnZYeq79WpQoFpFWqOB37ORpzouKOxt/uUXIDIQ5H2s9xOR6c6YgpuKZOVD8v4wAAAAAAAAyx7BmuJXeVd3zREmA3J1j7N5vwi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' "
            f"style='height:120px;width:auto;object-fit:contain'>"
            f"</div>"
            f"<hr style='margin:8px 0;border-color:#ECECEC'>"
            f"<div style='padding:4px 0 6px;font-size:12px;color:#374151'>"
            f"<div style='font-weight:600'>{nama}</div>"
            f"<div style='color:#9CA3AF;font-size:11px'>NIK {nik}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        c_gp, c_out = st.columns(2)
        with c_gp:
            if st.button("Ganti Proyek", use_container_width=True, key="switch_project_btn"):
                st.session_state.pop("active_project", None)
                st.rerun()
        with c_out:
            if st.button("Keluar", use_container_width=True, key="logout_btn"):
                for k in ["logged_in","user_nik","user_nama","user_akses","preloaded","active_project"]:
                    st.session_state.pop(k, None)
                st.rerun()
        st.markdown("<hr style='margin:8px 0;border-color:#ECECEC'>", unsafe_allow_html=True)

    render_change_password()

    # ── UNIFIED SIDEBAR FILTER — opsi menyesuaikan tab aktif ──
    st.sidebar.markdown(
        "<div style='font-size:11px;font-weight:700;color:#B01C2E;"
        "text-transform:uppercase;letter-spacing:.8px;padding:4px 0 8px'>Filter</div>",
        unsafe_allow_html=True)

    # Pilih sumber data untuk opsi filter
    prev_tab = st.session_state.get("f_tab_prev", None)
    tab_sel = st.sidebar.selectbox(
        "Lihat Data",
        ["— Pilih Data —", "AR OTC — MTI NKA", "AR GT", "AR RDI"],
        key="f_tab_sel"
    )

    # Reset semua filter saat tab berubah
    if tab_sel != prev_tab:
        for k in ["f_region","f_area","f_asm","f_rbm","f_sales",
                  "f_jenis","f_toko","f_kat","f_grp","f_top","f_bkt","f_so"]:
            if k in st.session_state:
                del st.session_state[k]
        st.session_state["f_tab_prev"] = tab_sel
        if tab_sel != "— Pilih Data —":
            st.rerun()

    # Belum pilih → sembunyikan filter, tetap tampilkan konten OTC default
    if tab_sel == "— Pilih Data —":
        st.sidebar.markdown(
            "<div style='font-size:12px;color:#9CA3AF;padding:8px 0'>"
            "Pilih data di atas untuk mengaktifkan filter.</div>",
            unsafe_allow_html=True)
        # Tampilkan tab tanpa filter
        tab1, tab2, tab3 = st.tabs(["Channel MT PMA", "Channel GT PMA", "PT RDI"])
        with tab1: page_otc({})
        with tab2: page_gt({})
        with tab3: page_rdi({})
        return

    # Load data referensi sesuai tab yang dipilih
    if tab_sel == "AR OTC — MTI NKA":
        _df_ref, _ = load_otc()
        col_region = "REGION"; col_area = "NAMA AREA"; col_asm = "ASM"
        col_rbm = "RBM"; col_sales = "NAMA SALES"; col_jenis = "JENIS OUTLET"
        col_toko = "NAMA TOKO"; col_kat = "KATEGORI OVERDUE"; col_grp = "GROUPING OS"
        col_top = "TOP"
    elif tab_sel == "AR GT":
        _df_ref, _ = load_gt()
        col_region = "Region"; col_area = "Nama Area"; col_asm = "ASM"
        col_rbm = "RBM"; col_sales = "Nama Sales"; col_jenis = "Jenis Outlet"
        col_toko = "Nama Toko"; col_kat = "Kategori Overdue"; col_grp = "Grouping OS"
        col_top = "TOP"
    else:
        _df_ref, _ = load_rdi()
        col_region = "Region"; col_area = "Nama Area"; col_asm = "ASM"
        col_rbm = "RBM"; col_sales = "Nama Sales"; col_jenis = "Jenis Outlet"
        col_toko = "Nama Toko"; col_kat = "Kategori Overdue"; col_grp = "Grouping OS"
        col_top = "TOP"

    def _sel(label, col, src, key):
        if col not in src.columns: return "Semua"
        return st.sidebar.selectbox(label, ["Semua"]+sorted(src[col].dropna().unique().tolist()), key=key)

    sel_region = _sel("Region",       col_region, _df_ref, "f_region")
    _r0 = _df_ref if sel_region=="Semua" else _df_ref[_df_ref[col_region]==sel_region]
    sel_area   = _sel("Nama Area",    col_area,   _r0,     "f_area")
    _r1 = _r0 if sel_area=="Semua" else _r0[_r0[col_area]==sel_area]
    sel_asm    = _sel("ASM",          col_asm,    _r1,     "f_asm")
    sel_rbm    = _sel("RBM",          col_rbm,    _r1,     "f_rbm")
    sel_sales  = _sel("Nama Sales",   col_sales,  _r1,     "f_sales")
    sel_jenis  = _sel("Channel / Jenis Outlet", col_jenis, _r1, "f_jenis")
    sel_toko   = _sel("Nama Toko",    col_toko,   _r1,     "f_toko")
    sel_kat    = _sel("Kategori Overdue", col_kat, _r1,    "f_kat")
    sel_grp    = _sel("Grouping OS",  col_grp,    _r1,     "f_grp")
    sel_top    = _sel("TOP",          col_top,    _r1,     "f_top")
    sel_bkt    = st.sidebar.multiselect("Aging Days", BUCKETS, default=BUCKETS, key="f_bkt")
    sel_so     = st.sidebar.selectbox("SO Block",
                   ["Semua","WARNING SO","SOFT BLOCK","CRITICAL BLOCK"], key="f_so")
    st.sidebar.markdown("---")
    if st.sidebar.button("Refresh Data", use_container_width=True, key="ref_all"):
        st.cache_data.clear(); st.session_state["preloaded"]=False; st.rerun()

    filters = {"region":sel_region,"area":sel_area,"asm":sel_asm,"rbm":sel_rbm,
               "sales":sel_sales,"jenis":sel_jenis,"toko":sel_toko,"kat":sel_kat,
               "grp":sel_grp,"top":sel_top,"bkt":sel_bkt,"so_kat":sel_so}

    # Tab konten — ikut pilihan di sidebar
    tab1, tab2, tab3 = st.tabs(["Channel MT PMA", "Channel GT PMA", "PT RDI"])
    with tab1:
        page_otc(filters)
    with tab2:
        page_gt(filters)
    with tab3:
        page_rdi(filters)

if __name__ == "__main__":
    main()
