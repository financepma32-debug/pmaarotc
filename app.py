"""
AR OTC Dashboard — Outstanding MT MTI NKA
PT Pinus Merah Abadi | FAD Team
Palet: Nude tegas — Warm Stone #E8E0D8, Charcoal #2C2C2C, Merah PMA #A8192E
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client
from datetime import datetime

st.set_page_config(
    page_title="AR OTC — Outstanding MT MTI NKA | PMA",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — Nude Tegas
# Background  : #F0EBE3  warm stone, bukan putih, bukan krem pastel
# Surface     : #FFFFFF  kartu
# Merah PMA   : #A8192E  dari logo, lebih tua dari crimson
# Charcoal    : #2C2C2C  teks utama
# Stone mid   : #8C7B72  label, caption
# Border      : #D9D0C7  garis pemisah
# WARNING SO  : #B8860B  dark goldenrod — serius tapi bukan merah
# SOFT BLOCK  : #C05000  burnt orange — tahap kedua
# CRITICAL    : #A8192E  merah PMA penuh — bahaya
# ════════════════════════════════════════════════════════════════════

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family:'Inter',sans-serif; }

[data-testid="stAppViewContainer"] { background:#F0EBE3; }
[data-testid="stSidebar"]          { background:#FAF8F5; border-right:1px solid #D9D0C7; }
[data-testid="stSidebar"] *        { font-size:13px; color:#2C2C2C; }
.block-container { padding:1rem 1.8rem 2rem; max-width:1440px; }

/* ── HEADER ── */
.pma-header {
    background: #A8192E;
    border-radius: 8px;
    padding: 14px 22px;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 16px;
    box-shadow: 0 2px 8px rgba(168,25,46,.25);
}
.pma-title { color:#fff; font-size:18px; font-weight:700; margin:0; letter-spacing:-.2px; white-space:nowrap; }
.pma-sub   { color:rgba(255,255,255,.65); font-size:11px; margin:2px 0 0; }
.pma-date  {
    color:#fff; font-size:12px; font-weight:600;
    background:rgba(255,255,255,.18); border-radius:5px;
    padding:5px 12px; font-family:'IBM Plex Mono',monospace;
    white-space:nowrap; flex-shrink:0;
}

/* ── UPDATE BAR ── */
.upd-bar {
    background:#EDE6DD; border-radius:6px; padding:7px 14px;
    font-size:11px; color:#6B5E57;
    display:flex; justify-content:space-between; margin-bottom:16px;
}

/* ── KPI CARD ── */
.kpi {
    background:#fff; border-radius:7px;
    padding:14px 12px 12px;
    border-left:4px solid #A8192E;
    box-shadow:0 1px 3px rgba(0,0,0,.06);
    min-height:82px;
}
.kpi.green  { border-left-color:#1A6B3C; }
.kpi.gold   { border-left-color:#B8860B; }
.kpi.orange { border-left-color:#C05000; }
.kpi.stone  { border-left-color:#8C7B72; }
.kpi-lbl { font-size:9.5px; font-weight:700; color:#8C7B72; text-transform:uppercase; letter-spacing:.9px; margin:0; }
.kpi-val { font-size:21px; font-weight:700; color:#2C2C2C; font-family:'IBM Plex Mono',monospace; margin:5px 0 2px; line-height:1; }
.kpi-sub { font-size:10px; color:#A8998F; margin:0; }

/* ── BUCKET STRIP ── */
.bk-strip { display:flex; gap:5px; margin-bottom:18px; }
.bk-cell  {
    flex:1; background:#fff; border-radius:6px;
    padding:9px 6px; text-align:center;
    border-top:3px solid #D9D0C7;
    box-shadow:0 1px 2px rgba(0,0,0,.05);
}
.bk-lbl { font-size:8.5px; font-weight:700; color:#8C7B72; text-transform:uppercase; letter-spacing:.4px; margin:0; }
.bk-val { font-size:12px; font-weight:700; color:#2C2C2C; font-family:'IBM Plex Mono',monospace; margin:3px 0 0; }

/* ── SO BLOCK CARDS ── */
.so-wrap { display:flex; gap:10px; margin-bottom:4px; }
.so-card {
    flex:1; border-radius:8px; padding:16px 16px 14px;
    box-shadow:0 2px 6px rgba(0,0,0,.08);
}
.so-warn  { background:#FEF7E6; border-left:5px solid #B8860B; }
.so-soft  { background:#FDF0E8; border-left:5px solid #C05000; }
.so-crit  { background:#FBE8EB; border-left:5px solid #A8192E; }
.so-badge {
    display:inline-block; font-size:9px; font-weight:700;
    border-radius:3px; padding:2px 7px; letter-spacing:.6px;
    text-transform:uppercase; margin-bottom:6px;
}
.so-badge.warn { background:#B8860B; color:#fff; }
.so-badge.soft { background:#C05000; color:#fff; }
.so-badge.crit { background:#A8192E; color:#fff; }
.so-val  { font-size:26px; font-weight:700; font-family:'IBM Plex Mono',monospace; color:#2C2C2C; margin:0; line-height:1; }
.so-sub  { font-size:11px; color:#6B5E57; margin:4px 0 0; }
.so-desc { font-size:10px; color:#8C7B72; margin:6px 0 0; font-style:italic; }

/* ── SECTION TITLE ── */
.sec { font-size:10.5px; font-weight:700; color:#A8192E; text-transform:uppercase;
       letter-spacing:1.2px; margin:20px 0 8px;
       padding-bottom:5px; border-bottom:1px solid #D9D0C7; }

/* ── TABLE override ── */
[data-testid="stDataFrame"] thead th {
    background:#EDE6DD !important; color:#2C2C2C !important;
    font-size:11px !important; font-weight:700 !important;
    text-transform:uppercase !important; letter-spacing:.4px !important;
}
[data-testid="stDataFrame"] tbody td { font-size:12px !important; color:#3A3A3A !important; }
</style>
""", unsafe_allow_html=True)

# ── KONSTANTA ────────────────────────────────────────────────────────────────
ALL_COLUMNS = [
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
NUMERIC_COLS = {
    "NOMINAL","Nilai Faktur","Saldo Awal","Movement","Saldo Akhir",
    "CURRENT","1-7 DAYS","8-30 DAYS","31-60 DAYS","61-90 DAYS",
    "91-120 DAYS","121+ DAYS","<2026",
    "OVERDUE","OVERDUE?","ACTUAL PELUNASAN","TARGET PELUNASAN",
    "DUE DATE","Qty Faktur Gantung",
}
DATE_COLS = {
    "Tanggal Faktur","Tanggal JT","Tgl Target Pelunasan System",
    "Tgl Konfirmasi","TANGGAL HARI INII","batas 2025",
}
BUCKETS = ["CURRENT","1-7 DAYS","8-30 DAYS","31-60 DAYS",
           "61-90 DAYS","91-120 DAYS","121+ DAYS","<2026"]
BUCKET_COLOR = {
    "CURRENT":    "#1A6B3C",
    "1-7 DAYS":   "#B8860B",
    "8-30 DAYS":  "#B8860B",
    "31-60 DAYS": "#C05000",
    "61-90 DAYS": "#C05000",
    "91-120 DAYS":"#A8192E",
    "121+ DAYS":  "#7A0E1E",
    "<2026":      "#8C7B72",
}

# SO Block mapping
SO_MAP = {
    "1-7 DAYS":   "WARNING SO",
    "8-30 DAYS":  "WARNING SO",
    "31-60 DAYS": "SOFT BLOCK",
    "61-90 DAYS": "SOFT BLOCK",
    "91-120 DAYS":"CRITICAL BLOCK",
    "121+ DAYS":  "CRITICAL BLOCK",
    "<2026":      "CRITICAL BLOCK",
}

# ── FORMAT ───────────────────────────────────────────────────────────────────
def M(v):
    v = float(v)
    if abs(v) >= 1_000_000_000: return f"{v/1_000_000_000:.2f}M"
    if abs(v) >= 1_000_000:     return f"{v/1_000_000:.1f}Jt"
    return f"{v:,.0f}"
def R(v): return f"{float(v):,.0f}"
def P(n,d): return f"{n/d*100:.1f}%" if d else "–"

# ── SUPABASE ─────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_sb():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

@st.cache_data(ttl=300, show_spinner=False)
def load_data():
    sb = get_sb()
    last_updated = "–"
    try:
        meta = sb.table("upload_log").select("uploaded_at,total_rows") \
                 .order("uploaded_at", desc=True).limit(1).execute()
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
        rows, page, SZ = [], 0, 1000
        while True:
            r = sb.table("os_master").select("*").range(page*SZ,(page+1)*SZ-1).execute()
            if not r.data: break
            rows.extend(r.data)
            if len(r.data) < SZ: break
            page += 1
        if not rows:
            return pd.DataFrame(), last_updated
        df = pd.DataFrame(rows)
        for c in ("id","created_at"):
            if c in df.columns: df.drop(columns=c, inplace=True)
        for col in ALL_COLUMNS:
            if col not in df.columns: df[col] = None
        df = df[ALL_COLUMNS].copy()
        for col in NUMERIC_COLS:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        for col in DATE_COLS:
            df[col] = pd.to_datetime(df[col], errors="coerce")
        return df, last_updated
    except Exception as e:
        st.error(f"Gagal ambil data: {e}")
        return pd.DataFrame(), last_updated

# ── PLOTLY BASE ───────────────────────────────────────────────────────────────
FONT = dict(family="Inter, sans-serif", size=11, color="#2C2C2C")
def plot_base(fig, h=300, margin=None):
    m = margin or dict(t=12,b=12,l=6,r=6)
    fig.update_layout(
        plot_bgcolor="#F0EBE3", paper_bgcolor="rgba(0,0,0,0)",
        font=FONT, height=h, margin=m,
        xaxis=dict(gridcolor="#DDD5CC", linecolor="#C8BFB7", tickfont_size=10),
        yaxis=dict(gridcolor="#DDD5CC", linecolor="#C8BFB7", tickfont_size=10),
        showlegend=False,
    )
    return fig

def sec(t): st.markdown(f"<p class='sec'>{t}</p>", unsafe_allow_html=True)

def kpi(col_obj, label, val, sub="", cls=""):
    with col_obj:
        st.markdown(
            f"<div class='kpi {cls}'>"
            f"<p class='kpi-lbl'>{label}</p>"
            f"<p class='kpi-val'>{val}</p>"
            f"<p class='kpi-sub'>{sub}</p>"
            f"</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    with st.spinner("Memuat data..."):
        df, last_updated = load_data()

    # ── HEADER — judul tidak terpotong ───────────────────────────────
    st.markdown(f"""
    <div class="pma-header">
      <div style="min-width:0;flex:1;margin-right:16px">
        <p class="pma-title">AR Outstanding MT — MTI NKA</p>
        <p class="pma-sub">PT Pinus Merah Abadi &nbsp;·&nbsp; FAD Team &nbsp;·&nbsp; Data via Supabase</p>
      </div>
      <span class="pma-date">{datetime.now().strftime('%d %b %Y')}</span>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.warning("Belum ada data. Jalankan **JALANKAN_UPLOAD.bat** untuk upload data.")
        return

    # ── SIDEBAR ───────────────────────────────────────────────────────
    st.sidebar.markdown("### Filter")
    def sb(label, col, src):
        opts = ["Semua"] + sorted(src[col].dropna().unique().tolist())
        return st.sidebar.selectbox(label, opts, key=f"f_{col}")

    sel_region = sb("Region",       "REGION",       df)
    d0 = df if sel_region=="Semua" else df[df["REGION"]==sel_region]
    sel_area   = sb("Nama Area",    "NAMA AREA",    d0)
    d1 = d0 if sel_area=="Semua" else d0[d0["NAMA AREA"]==sel_area]
    sel_jenis  = sb("Jenis Outlet", "JENIS OUTLET", d1)
    sel_asm    = sb("ASM",          "ASM",          d1)
    sel_rbm    = sb("RBM",          "RBM",          d1)
    sel_grp    = sb("Grouping OS",  "GROUPING OS",  d1)
    sel_bkt    = st.sidebar.multiselect("Kelompok Aging", BUCKETS, default=BUCKETS)
    st.sidebar.markdown("---")
    if st.sidebar.button("↺  Refresh Data", use_container_width=True):
        st.cache_data.clear(); st.rerun()
    st.sidebar.caption(f"Update: {last_updated}")

    # ── FILTER ────────────────────────────────────────────────────────
    dff = df.copy()
    if sel_region!="Semua": dff = dff[dff["REGION"]      ==sel_region]
    if sel_area  !="Semua": dff = dff[dff["NAMA AREA"]   ==sel_area]
    if sel_jenis !="Semua": dff = dff[dff["JENIS OUTLET"] ==sel_jenis]
    if sel_asm   !="Semua": dff = dff[dff["ASM"]         ==sel_asm]
    if sel_rbm   !="Semua": dff = dff[dff["RBM"]         ==sel_rbm]
    if sel_grp   !="Semua": dff = dff[dff["GROUPING OS"] ==sel_grp]
    if sel_bkt:              dff = dff[dff["KELOMPOK"].isin(sel_bkt)]
    if dff.empty:
        st.warning("Tidak ada data sesuai filter."); return

    # ── UPDATE BAR ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="upd-bar">
      <span>⏱ Update terakhir: <strong>{last_updated}</strong></span>
      <span>{len(dff):,} faktur ditampilkan</span>
    </div>""", unsafe_allow_html=True)

    # ── KPI UTAMA ─────────────────────────────────────────────────────
    total_nom = dff["NOMINAL"].sum()
    total_ov  = dff["OVERDUE"].sum()
    total_cur = dff["CURRENT"].sum()
    total_akt = dff["ACTUAL PELUNASAN"].sum()
    total_tgt = dff["TARGET PELUNASAN"].sum()
    total_due = dff["DUE DATE"].sum()
    total_qty = int(dff["Qty Faktur Gantung"].sum())

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    kpi(c1,"Total Outstanding", M(total_nom), f"Nilai Faktur {M(dff['Nilai Faktur'].sum())}")
    kpi(c2,"Overdue",           M(total_ov),  P(total_ov,total_nom)+" dari outstanding")
    kpi(c3,"Current",           M(total_cur), P(total_cur,total_nom)+" dari total","green")
    kpi(c4,"% Collection",      P(total_akt,total_tgt),
        f"Actual {M(total_akt)} / Target {M(total_tgt)}","gold")
    kpi(c5,"Due Date Hari Ini", M(total_due), "Nominal jatuh tempo hari ini","stone")
    kpi(c6,"Qty Faktur Gantung",f"{total_qty:,}", f"{len(dff):,} baris data","orange")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── BUCKET AGING STRIP ────────────────────────────────────────────
    bv = {b: dff[b].sum() for b in BUCKETS}
    grand = sum(bv.values())
    cells = "".join([
        f"<div class='bk-cell' style='border-top-color:{BUCKET_COLOR[b]}'>"
        f"<p class='bk-lbl'>{b}</p><p class='bk-val'>{M(bv[b])}</p></div>"
        for b in BUCKETS
    ])
    cells += (
        f"<div class='bk-cell' style='border-top-color:#2C2C2C;background:#2C2C2C'>"
        f"<p class='bk-lbl' style='color:#C8BFB7'>TOTAL</p>"
        f"<p class='bk-val' style='color:#fff'>{M(grand)}</p></div>"
    )
    st.markdown(f"<div class='bk-strip'>{cells}</div>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # SO BLOCK SECTION — informasi baru, jadi bintang utama
    # ════════════════════════════════════════════════════════════════
    sec("STATUS SO BLOCK — REKOMENDASI TINDAKAN")

    # Hitung per kategori SO
    df_ov = dff[dff["KELOMPOK"] != "CURRENT"].copy()
    df_ov["SO_KAT"] = df_ov["KELOMPOK"].map(SO_MAP)

    so_sum = df_ov.groupby("SO_KAT").agg(
        Nominal=("NOMINAL","sum"),
        Faktur=("No Faktur","count"),
        Area=("NAMA AREA","nunique"),
    ).reindex(["WARNING SO","SOFT BLOCK","CRITICAL BLOCK"]).fillna(0)

    warn_nom = so_sum.loc["WARNING SO","Nominal"]   if "WARNING SO"      in so_sum.index else 0
    soft_nom = so_sum.loc["SOFT BLOCK","Nominal"]   if "SOFT BLOCK"      in so_sum.index else 0
    crit_nom = so_sum.loc["CRITICAL BLOCK","Nominal"] if "CRITICAL BLOCK" in so_sum.index else 0
    warn_fkt = int(so_sum.loc["WARNING SO","Faktur"])    if "WARNING SO"      in so_sum.index else 0
    soft_fkt = int(so_sum.loc["SOFT BLOCK","Faktur"])    if "SOFT BLOCK"      in so_sum.index else 0
    crit_fkt = int(so_sum.loc["CRITICAL BLOCK","Faktur"]) if "CRITICAL BLOCK" in so_sum.index else 0
    warn_area= int(so_sum.loc["WARNING SO","Area"])      if "WARNING SO"      in so_sum.index else 0
    soft_area= int(so_sum.loc["SOFT BLOCK","Area"])      if "SOFT BLOCK"      in so_sum.index else 0
    crit_area= int(so_sum.loc["CRITICAL BLOCK","Area"])  if "CRITICAL BLOCK"  in so_sum.index else 0

    st.markdown(f"""
    <div class="so-wrap">
      <div class="so-card so-warn">
        <span class="so-badge warn">⚠ Warning SO</span>
        <p class="so-val">{M(warn_nom)}</p>
        <p class="so-sub">{warn_fkt:,} faktur &nbsp;·&nbsp; {warn_area} area</p>
        <p class="so-desc">Kelompok 1–7 hari & 8–30 hari — segera follow up sebelum eskalasi</p>
      </div>
      <div class="so-card so-soft">
        <span class="so-badge soft">🔶 Soft Block</span>
        <p class="so-val">{M(soft_nom)}</p>
        <p class="so-sub">{soft_fkt:,} faktur &nbsp;·&nbsp; {soft_area} area</p>
        <p class="so-desc">Kelompok 31–60 & 61–90 hari — pertimbangkan hold pengiriman baru</p>
      </div>
      <div class="so-card so-crit">
        <span class="so-badge crit">🔴 Critical Block</span>
        <p class="so-val">{M(crit_nom)}</p>
        <p class="so-sub">{crit_fkt:,} faktur &nbsp;·&nbsp; {crit_area} area</p>
        <p class="so-desc">Kelompok 91–120, 121+ hari & &lt;2026 — blokir SO, eskalasi ke manajemen</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabel TOP AREA per SO Kategori — 3 kolom berdampingan
    c_w, c_s, c_c = st.columns(3)

    def so_table(col_obj, kat, title):
        with col_obj:
            st.caption(f"**Top Area — {title}**")
            sub = df_ov[df_ov["SO_KAT"]==kat]
            if sub.empty:
                st.info("Tidak ada data"); return
            t = (sub.groupby("NAMA AREA")
                 .agg(Nominal=("NOMINAL","sum"), Faktur=("No Faktur","count"))
                 .reset_index().sort_values("Nominal",ascending=False).head(10))
            t["%"] = t["Nominal"].apply(lambda v: P(v, sub["NOMINAL"].sum()))
            t["Nominal"] = t["Nominal"].apply(M)
            t.columns = ["Nama Area","Nominal","Faktur","%"]
            st.dataframe(t, use_container_width=True, hide_index=True, height=300)

    so_table(c_w, "WARNING SO",      "⚠ Warning SO")
    so_table(c_s, "SOFT BLOCK",      "🔶 Soft Block")
    so_table(c_c, "CRITICAL BLOCK",  "🔴 Critical Block")

    # Chart: SO Block per Nama Area — stacked bar
    sec("DISTRIBUSI SO BLOCK PER NAMA AREA")
    pivot = (
        df_ov.groupby(["NAMA AREA","SO_KAT"])["NOMINAL"]
        .sum().unstack(fill_value=0).reset_index()
    )
    for k in ["WARNING SO","SOFT BLOCK","CRITICAL BLOCK"]:
        if k not in pivot.columns: pivot[k] = 0
    pivot["TOTAL"] = pivot[["WARNING SO","SOFT BLOCK","CRITICAL BLOCK"]].sum(axis=1)
    pivot = pivot.nlargest(20,"TOTAL")

    fig_so = go.Figure()
    cfg = [
        ("WARNING SO",      "#B8860B", "⚠ Warning SO"),
        ("SOFT BLOCK",      "#C05000", "🔶 Soft Block"),
        ("CRITICAL BLOCK",  "#A8192E", "🔴 Critical Block"),
    ]
    for col_key, color, name in cfg:
        if col_key in pivot.columns:
            fig_so.add_trace(go.Bar(
                name=name, x=pivot["NAMA AREA"], y=pivot[col_key],
                marker_color=color,
                text=pivot[col_key].apply(lambda v: M(v) if v > 0 else ""),
                textposition="inside", textfont=dict(size=9,color="#fff"),
            ))
    plot_base(fig_so, h=360)
    fig_so.update_layout(
        barmode="stack", showlegend=True,
        legend=dict(orientation="h", x=0, y=1.06, font_size=11),
        xaxis_tickangle=-35, yaxis_tickformat=",",
    )
    st.plotly_chart(fig_so, use_container_width=True)

    # ════════════════════════════════════════════════════════════════
    # KOMPOSISI OUTSTANDING
    # ════════════════════════════════════════════════════════════════
    sec("KOMPOSISI OUTSTANDING")
    col_a, col_b = st.columns([5,4])

    with col_a:
        grp_os = (dff[dff["NOMINAL"]>0].groupby("GROUPING OS")["NOMINAL"]
                  .sum().sort_values().reset_index())
        grp_os.columns = ["Kategori","Nominal"]
        n = len(grp_os)
        colors = [f"rgba(168,25,46,{0.3+0.7*(i/max(n-1,1)):.2f})" for i in range(n)]
        fig_h = go.Figure(go.Bar(
            x=grp_os["Nominal"], y=grp_os["Kategori"], orientation="h",
            marker_color=colors,
            text=[M(v) for v in grp_os["Nominal"]],
            textposition="outside", textfont=dict(size=10,color="#2C2C2C"),
        ))
        plot_base(fig_h, h=300)
        fig_h.update_layout(xaxis_tickformat=",")
        st.plotly_chart(fig_h, use_container_width=True)

    with col_b:
        # Donut — warna nude per bucket
        pie_labels = [b for b in BUCKETS if bv[b] > 0]
        pie_vals   = [bv[b] for b in BUCKETS if bv[b] > 0]
        pie_colors = [BUCKET_COLOR[b] for b in BUCKETS if bv[b] > 0]
        fig_pie = go.Figure(go.Pie(
            labels=pie_labels, values=pie_vals,
            marker_colors=pie_colors, hole=0.55,
            textinfo="percent", textfont_size=10,
            hovertemplate="%{label}: %{value:,.0f}<extra></extra>",
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=300, margin=dict(t=12,b=12,l=0,r=0),
            legend=dict(font_size=10, x=1.02, y=0.5, xanchor="left"),
            showlegend=True,
            annotations=[dict(
                text=f"<b>{M(grand)}</b><br><span style='font-size:9px'>Total OS</span>",
                x=0.5,y=0.5,showarrow=False,font=dict(size=13,color="#2C2C2C"),
            )],
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ════════════════════════════════════════════════════════════════
    # TABEL NAMA AREA + KATEGORI OVERDUE
    # ════════════════════════════════════════════════════════════════
    sec("OUTSTANDING PER WILAYAH & KATEGORI")
    col_c, col_d = st.columns(2)

    with col_c:
        st.caption("**Per Nama Area** — Nilai Faktur · Current · Overdue · % Curr/OD")
        t_area = (dff.groupby("NAMA AREA")
                  .agg(NF=("Nilai Faktur","sum"),Cur=("CURRENT","sum"),Ov=("OVERDUE","sum"))
                  .reset_index().sort_values("NF",ascending=False))
        t_area["% C/OD"] = t_area.apply(lambda r: P(r["Cur"],r["Cur"]+r["Ov"]),axis=1)
        for c in ["NF","Cur","Ov"]: t_area[c] = t_area[c].apply(M)
        t_area.columns = ["Nama Area","Nilai Faktur","Current","Overdue","% Curr/OD"]
        st.dataframe(t_area, use_container_width=True, hide_index=True, height=340)

    with col_d:
        st.caption("**Per Kategori Overdue**")
        t_kat = (dff[dff["NOMINAL"]>0].groupby("KATEGORI OVERDUE")
                 .agg(Nominal=("NOMINAL","sum"),Faktur=("No Faktur","count"))
                 .reset_index().sort_values("Nominal",ascending=False))
        t_kat["%"] = t_kat["Nominal"].apply(lambda v: P(v,total_nom))
        t_kat["Nominal"] = t_kat["Nominal"].apply(R)
        t_kat.columns = ["Kategori Overdue","Nominal","Jml Faktur","%"]
        st.dataframe(t_kat, use_container_width=True, hide_index=True, height=340)

    # ════════════════════════════════════════════════════════════════
    # COLLECTION — ACTUAL vs TARGET
    # ════════════════════════════════════════════════════════════════
    sec("COLLECTION — ACTUAL vs TARGET PELUNASAN")
    col_e, col_f = st.columns([5,4])

    with col_e:
        t_coll = (dff.groupby("NAMA AREA")
                  .agg(Actual=("ACTUAL PELUNASAN","sum"),Target=("TARGET PELUNASAN","sum"))
                  .reset_index())
        t_coll = t_coll[t_coll["Target"]>0].nlargest(12,"Target")
        fig_c = go.Figure()
        fig_c.add_trace(go.Bar(
            name="Target", x=t_coll["NAMA AREA"], y=t_coll["Target"],
            marker_color="#D9D0C7",
            text=[M(v) for v in t_coll["Target"]],
            textposition="outside", textfont=dict(size=9),
        ))
        fig_c.add_trace(go.Bar(
            name="Actual", x=t_coll["NAMA AREA"], y=t_coll["Actual"],
            marker_color="#A8192E",
            text=[M(v) for v in t_coll["Actual"]],
            textposition="outside", textfont=dict(size=9,color="#fff"),
        ))
        plot_base(fig_c, h=320)
        fig_c.update_layout(
            barmode="group", showlegend=True,
            legend=dict(orientation="h",x=0,y=1.08,font_size=11),
            xaxis_tickangle=-30, yaxis_tickformat=",",
        )
        st.plotly_chart(fig_c, use_container_width=True)

    with col_f:
        st.caption("**Collection Rate per ASM**")
        t_asm = (dff.groupby("ASM")
                 .agg(Actual=("ACTUAL PELUNASAN","sum"),
                      Target=("TARGET PELUNASAN","sum"),
                      OS=("NOMINAL","sum"))
                 .reset_index())
        t_asm = t_asm[t_asm["Target"]>0].sort_values("Target",ascending=False)
        t_asm["%Coll"] = t_asm.apply(lambda r: P(r["Actual"],r["Target"]),axis=1)
        for c in ["Actual","Target","OS"]: t_asm[c] = t_asm[c].apply(M)
        t_asm.columns = ["ASM","Actual","Target","Outstanding","% Coll"]
        st.dataframe(t_asm, use_container_width=True, hide_index=True, height=320)

    # ════════════════════════════════════════════════════════════════
    # BREAKDOWN OUTLET & RBM
    # ════════════════════════════════════════════════════════════════
    sec("BREAKDOWN JENIS OUTLET & RBM")
    col_g, col_h = st.columns([4,5])

    with col_g:
        t_out = (dff.groupby("JENIS OUTLET")
                 .agg(OS=("NOMINAL","sum"),OV=("OVERDUE","sum"))
                 .reset_index().sort_values("OS",ascending=False).head(12))
        t_out["%OD"] = t_out.apply(lambda r: P(r["OV"],r["OS"]),axis=1)
        for c in ["OS","OV"]: t_out[c] = t_out[c].apply(M)
        t_out.columns = ["Jenis Outlet","Outstanding","Overdue","%OD"]
        st.dataframe(t_out, use_container_width=True, hide_index=True, height=340)

    with col_h:
        t_rbm = (dff.groupby("RBM")
                 .agg(OS=("NOMINAL","sum"),OV=("OVERDUE","sum"),
                      Akt=("ACTUAL PELUNASAN","sum"),Tgt=("TARGET PELUNASAN","sum"))
                 .reset_index().sort_values("OS",ascending=False))
        t_rbm["%OD"]   = t_rbm.apply(lambda r: P(r["OV"],r["OS"]),axis=1)
        t_rbm["%Coll"] = t_rbm.apply(lambda r: P(r["Akt"],r["Tgt"]),axis=1)
        for c in ["OS","OV","Akt","Tgt"]: t_rbm[c] = t_rbm[c].apply(M)
        t_rbm.columns = ["RBM","Outstanding","Overdue","Actual Pel.","Target Pel.","%OD","%Coll"]
        st.dataframe(t_rbm, use_container_width=True, hide_index=True, height=340)

    # ════════════════════════════════════════════════════════════════
    # DETAIL FAKTUR
    # ════════════════════════════════════════════════════════════════
    ovrd_ct = int((dff["OVERDUE?"]>0).sum())
    sec(f"DETAIL FAKTUR — {ovrd_ct:,} FAKTUR OVERDUE")

    COLS = ["NAMA AREA","RBM","ASM","NAMA SALES","NAMA TOKO","No Faktur",
            "Tanggal Faktur","Tanggal JT","Nilai Faktur","Saldo Akhir",
            "KELOMPOK","OVERDUE?","GROUPING OS"]
    cols_ok = [c for c in COLS if c in dff.columns]
    tbl = dff[cols_ok].copy()
    if "Tanggal Faktur" in tbl.columns:
        tbl["Tanggal Faktur"] = tbl["Tanggal Faktur"].dt.strftime("%d %b %Y")
    if "Tanggal JT" in tbl.columns:
        tbl["Tanggal JT"] = tbl["Tanggal JT"].dt.strftime("%d %b %Y")
    for c in ["Nilai Faktur","Saldo Akhir"]:
        if c in tbl.columns: tbl[c] = tbl[c].apply(R)
    tbl.rename(columns={
        "NAMA AREA":"Nama Area","NAMA SALES":"Nama Sales","NAMA TOKO":"Nama Toko",
        "Saldo Akhir":"Sisa AR","OVERDUE?":"Hari OD","KELOMPOK":"Kelompok",
        "GROUPING OS":"Grouping OS",
    }, inplace=True)
    tbl.insert(0,"#",range(1,len(tbl)+1))

    with st.expander(f"🔽 Tampilkan {len(tbl):,} baris · OS Total: {M(total_nom)}", expanded=False):
        st.dataframe(tbl, use_container_width=True, hide_index=True, height=460)
        st.download_button(
            "⬇️ Download CSV (hasil filter)",
            data=dff[cols_ok].to_csv(index=False,sep=";",encoding="utf-8-sig").encode("utf-8-sig"),
            file_name=f"OS_MTI_NKA_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

    # ── FOOTER ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        f"<p style='text-align:center;color:#A8998F;font-size:11px;"
        f"font-family:IBM Plex Mono,monospace'>"
        f"AR OTC · PT Pinus Merah Abadi · FAD Team · "
        f"data {last_updated} · render {datetime.now().strftime('%d %b %Y %H:%M')}"
        f"</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
