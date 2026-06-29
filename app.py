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
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family:'Inter',sans-serif; }
[data-testid="stAppViewContainer"] { background:#F2EDE6; }
[data-testid="stSidebar"]          { background:#FFFFFF; border-right:1px solid #DDD5CC; }
[data-testid="stSidebar"] *        { font-size:13px; color:#1E1E1E; }
.block-container { padding:3.5rem 1.6rem 2rem !important; max-width:100% !important; }

/* ═══ HEADER FIX — tidak terpotong, judul bisa wrap ═══ */
.pma-header {
    background: linear-gradient(120deg, #C8192E 0%, #8C0A1C 100%);
    border-radius: 10px;
    padding: 14px 20px;
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 14px;
    box-shadow: 0 4px 14px rgba(180,15,40,.28);
    box-sizing: border-box;
    width: 100%;
}
.pma-hl { flex:1; min-width:0; }
.pma-title {
    color:#fff; font-size:17px; font-weight:700; margin:0;
    line-height:1.35;
    /* wrap, tidak dipotong sama sekali */
    white-space:normal !important;
    overflow:visible !important;
    text-overflow:unset !important;
    word-break:normal;
}
.pma-sub  { color:rgba(255,255,255,.68); font-size:11px; margin:3px 0 0; }
.pma-date {
    color:#fff; font-size:12px; font-weight:600;
    background:rgba(255,255,255,.18); border-radius:6px;
    padding:5px 12px; font-family:'IBM Plex Mono',monospace;
    white-space:nowrap; flex-shrink:0; align-self:center;
}

/* ═══ UPDATE BAR ═══ */
.upd-bar {
    background:#EAE2D8; border-radius:6px; padding:7px 14px;
    font-size:11px; color:#6B5E57;
    display:flex; justify-content:space-between; margin-bottom:14px;
}

/* ═══ KPI CARDS ═══ */
.kpi { background:#fff; border-radius:8px; padding:14px 12px 12px;
       border-left:4px solid #C8192E;
       box-shadow:0 1px 4px rgba(0,0,0,.07); min-height:82px; }
.kpi.green  { border-left-color:#0F9D58; }
.kpi.gold   { border-left-color:#E8A000; }
.kpi.orange { border-left-color:#E65C00; }
.kpi.stone  { border-left-color:#7B6E66; }
.kpi-lbl { font-size:9.5px; font-weight:700; color:#8C7B72; text-transform:uppercase; letter-spacing:.9px; margin:0; }
.kpi-val { font-size:20px; font-weight:700; color:#1E1E1E; font-family:'IBM Plex Mono',monospace; margin:5px 0 2px; line-height:1; }
.kpi-sub { font-size:10px; color:#A0908A; margin:0; }

/* ═══ BUCKET STRIP ═══ */
.bk-strip { display:flex; gap:5px; margin-bottom:18px; }
.bk-cell { flex:1; background:#fff; border-radius:6px; padding:9px 6px;
           text-align:center; border-top:3px solid #DDD5CC;
           box-shadow:0 1px 3px rgba(0,0,0,.06); }
.bk-lbl { font-size:8.5px; font-weight:700; color:#8C7B72; text-transform:uppercase; letter-spacing:.4px; margin:0; }
.bk-val { font-size:12.5px; font-weight:700; color:#1E1E1E; font-family:'IBM Plex Mono',monospace; margin:3px 0 0; }

/* ═══ SO BLOCK CARDS ═══ */
.so-wrap { display:flex; gap:12px; margin-bottom:12px; }
.so-card { flex:1; border-radius:10px; padding:16px 16px 13px; box-shadow:0 2px 8px rgba(0,0,0,.09); }
.so-warn { background:#FFFBF0; border-left:5px solid #F5A623; }
.so-soft { background:#FFF4EE; border-left:5px solid #E65C00; }
.so-crit { background:#FFF0F2; border-left:5px solid #C8192E; }
.so-badge { display:inline-block; font-size:9px; font-weight:700; border-radius:4px;
            padding:3px 8px; letter-spacing:.6px; text-transform:uppercase; margin-bottom:6px; }
.so-badge.warn { background:#F5A623; color:#fff; }
.so-badge.soft { background:#E65C00; color:#fff; }
.so-badge.crit { background:#C8192E; color:#fff; }
.so-val  { font-size:26px; font-weight:700; font-family:'IBM Plex Mono',monospace; color:#1E1E1E; margin:0; line-height:1.1; }
.so-sub  { font-size:11px; color:#6B5E57; margin:4px 0 0; }
.so-desc { font-size:10px; color:#9A8A82; margin:5px 0 0; font-style:italic; }

/* ═══ SECTION TITLE ═══ */
.sec { font-size:10.5px; font-weight:700; color:#C8192E; text-transform:uppercase;
       letter-spacing:1.2px; margin:22px 0 8px;
       padding-bottom:5px; border-bottom:1.5px solid #DDD5CC; }

/* ═══ TABLE ═══ */
[data-testid="stDataFrame"] thead th {
    background:#EDE5DC !important; color:#1E1E1E !important;
    font-size:11px !important; font-weight:700 !important;
    text-transform:uppercase !important; letter-spacing:.4px !important;
}
[data-testid="stDataFrame"] tbody td { font-size:12px !important; color:#333 !important; }

/* ═══ TAB MENU ═══ */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 4px; border-bottom: 2px solid #DDD5CC; padding-bottom:0;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-size:13px; font-weight:600; padding:8px 20px;
    border-radius:8px 8px 0 0; color:#8C7B72;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background:#C8192E !important; color:#fff !important;
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

def sec(t): st.markdown(f"<p class='sec'>{t}</p>", unsafe_allow_html=True)

def kpi(co, label, val, sub="", cls=""):
    with co:
        st.markdown(
            f"<div class='kpi {cls}'>"
            f"<p class='kpi-lbl'>{label}</p>"
            f"<p class='kpi-val'>{val}</p>"
            f"<p class='kpi-sub'>{sub}</p>"
            f"</div>", unsafe_allow_html=True)

def dl_btn(df_export, filename, label="⬇️ Download CSV"):
    csv = df_export.to_csv(index=False,sep=";",encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(label, data=csv,
                       file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                       mime="text/csv", use_container_width=True)

def bucket_strip(dff):
    bv = {b: dff[b].sum() if b in dff.columns else 0 for b in BUCKETS}
    grand = sum(bv.values())
    cells = "".join([
        f"<div class='bk-cell' style='border-top-color:{BUCKET_COLOR[b]}'>"
        f"<p class='bk-lbl'>{b}</p><p class='bk-val'>{M(bv[b])}</p></div>"
        for b in BUCKETS
    ])
    cells += (
        "<div class='bk-cell' style='border-top-color:#1E1E1E;background:#1E1E1E'>"
        f"<p class='bk-lbl' style='color:#CCC'>TOTAL</p>"
        f"<p class='bk-val' style='color:#fff'>{M(grand)}</p></div>"
    )
    st.markdown(f"<div class='bk-strip'>{cells}</div>", unsafe_allow_html=True)
    return bv, grand

def pma_header(title, last_updated, n_faktur):
    st.markdown(f"""
    <div class="pma-header">
      <div class="pma-hl">
        <p class="pma-title">{title}</p>
        <p class="pma-sub">PT Pinus Merah Abadi &nbsp;·&nbsp; FAD Team</p>
      </div>
      <span class="pma-date">{datetime.now().strftime('%d %b %Y')}</span>
    </div>
    <div class="upd-bar">
      <span>⏱ Update terakhir: <strong>{last_updated}</strong></span>
      <span>{n_faktur:,} faktur ditampilkan</span>
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
    st.sidebar.caption(f"Update: {last_updated}")

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
      <div class="so-card so-warn">
        <span class="so-badge warn">⚠ Warning SO</span>
        <p class="so-val">{M(wn)}</p>
        <p class="so-sub">{wf:,} faktur · {wa} area</p>
        <p class="so-desc">1–7 hari & 8–30 hari — segera follow up</p>
      </div>
      <div class="so-card so-soft">
        <span class="so-badge soft">🔶 Soft Block</span>
        <p class="so-val">{M(sn)}</p>
        <p class="so-sub">{sf:,} faktur · {sa} area</p>
        <p class="so-desc">31–60 & 61–90 hari — hold pengiriman baru</p>
      </div>
      <div class="so-card so-crit">
        <span class="so-badge crit">🔴 Critical Block</span>
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
    dl_btn(df_ov[so_out_cols], "SO_BLOCK_DETAIL", "⬇️ Download SO Block Detail")

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
        ("CRITICAL BLOCK","#C8192E","🔴 Critical Block"),
        ("SOFT BLOCK","#E65C00","🔶 Soft Block"),
        ("WARNING SO","#F5A623","⚠ Warning SO"),
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
    COLS=["NAMA AREA","RBM","ASM","NAMA SALES","NAMA TOKO","No Faktur","Tanggal Faktur","Tanggal JT","Nilai Faktur","Saldo Akhir","KELOMPOK","OVERDUE?","GROUPING OS"]
    cols_ok=[c for c in COLS if c in dff.columns]
    tbl=dff[cols_ok].copy()
    if "Tanggal Faktur" in tbl.columns: tbl["Tanggal Faktur"]=tbl["Tanggal Faktur"].dt.strftime("%d %b %Y")
    if "Tanggal JT" in tbl.columns: tbl["Tanggal JT"]=tbl["Tanggal JT"].dt.strftime("%d %b %Y")
    for c in ["Nilai Faktur","Saldo Akhir"]:
        if c in tbl.columns: tbl[c]=tbl[c].apply(R)
    tbl.rename(columns={"NAMA AREA":"Nama Area","NAMA SALES":"Nama Sales","NAMA TOKO":"Nama Toko","Saldo Akhir":"Sisa AR","OVERDUE?":"Hari OD","KELOMPOK":"Kelompok","GROUPING OS":"Grouping OS"},inplace=True)
    tbl.insert(0,"#",range(1,len(tbl)+1))
    with st.expander(f"🔽 Tampilkan {len(tbl):,} baris · OS Total: {M(tn)}",expanded=False):
        st.dataframe(tbl,use_container_width=True,hide_index=True,height=440)
        dl_btn(dff[cols_ok],"OS_MTI_NKA_DETAIL","⬇️ Download Detail Faktur")

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
      <div class="so-card so-warn">
        <span class="so-badge warn">⚠ Warning SO</span>
        <p class="so-val">{M(wn)}</p>
        <p class="so-sub">{wf:,} faktur · {wa} area</p>
        <p class="so-desc">1–7 hari & 8–30 hari — segera follow up</p>
      </div>
      <div class="so-card so-soft">
        <span class="so-badge soft">🔶 Soft Block</span>
        <p class="so-val">{M(sn)}</p>
        <p class="so-sub">{sf:,} faktur · {sa} area</p>
        <p class="so-desc">31–60 & 61–90 hari — hold pengiriman baru</p>
      </div>
      <div class="so-card so-crit">
        <span class="so-badge crit">🔴 Critical Block</span>
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
    dl_btn(df_ov[so_out_cols], "GT_SO_BLOCK_DETAIL", "⬇️ Download SO Block GT")

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
        ("CRITICAL BLOCK","#C8192E","🔴 Critical Block"),
        ("SOFT BLOCK","#E65C00","🔶 Soft Block"),
        ("WARNING SO","#F5A623","⚠ Warning SO"),
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
    COLS=["Nama Area","RBM","ASM","Nama Sales","Nama Toko","No Faktur","Tanggal Faktur","Tanggal JT","Nilai Faktur","Saldo Akhir","KELOMPOK","OVERDUE?","Grouping OS"]
    cols_ok=[c for c in COLS if c in dff.columns]
    tbl=dff[cols_ok].copy()
    if "Tanggal Faktur" in tbl.columns: tbl["Tanggal Faktur"]=tbl["Tanggal Faktur"].dt.strftime("%d %b %Y")
    if "Tanggal JT" in tbl.columns: tbl["Tanggal JT"]=tbl["Tanggal JT"].dt.strftime("%d %b %Y")
    for c in ["Nilai Faktur","Saldo Akhir"]:
        if c in tbl.columns: tbl[c]=tbl[c].apply(R)
    tbl.rename(columns={"Nama Area":"Nama Area","Nama Sales":"Nama Sales","Nama Toko":"Nama Toko","Saldo Akhir":"Sisa AR","OVERDUE?":"Hari OD","KELOMPOK":"Kelompok","Grouping OS":"Grouping OS"},inplace=True)
    tbl.insert(0,"#",range(1,len(tbl)+1))
    with st.expander(f"🔽 Tampilkan {len(tbl):,} baris · OS Total: {M(tn)}",expanded=False):
        st.dataframe(tbl,use_container_width=True,hide_index=True,height=440)
        dl_btn(dff[cols_ok],"GT_DETAIL","⬇️ Download Detail Faktur GT")

# ════════════════════════════════════════════════════════════════════


def main():
    tab1, tab2 = st.tabs(["📋  AR OTC — MTI NKA", "📊  AR GT"])
    with tab1:
        page_otc()
    with tab2:
        page_gt()

if __name__ == "__main__":
    main()
