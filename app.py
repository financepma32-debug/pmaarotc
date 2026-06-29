"""
AR OTC Dashboard — Outstanding MT MTI NKA
PT Pinus Merah Abadi | FAD Team
Fix: judul tidak terpotong, layout full-width, warna lebih hidup & cerah
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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family:'Inter',sans-serif; }

[data-testid="stAppViewContainer"] { background:#F2EDE6; }
[data-testid="stSidebar"]          { background:#FFFFFF; border-right:1px solid #DDD5CC; }
[data-testid="stSidebar"] *        { font-size:13px; color:#1E1E1E; }

/* ════ FIX LAYOUT — konten tidak mengecil di tengah ════ */
.block-container {
    padding: 0.8rem 1.6rem 2rem !important;
    max-width: 100% !important;
}

/* ════ HEADER ════ */
.pma-header {
    background: linear-gradient(120deg, #C8192E 0%, #8C0A1C 100%);
    border-radius: 10px;
    padding: 14px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 14px;
    box-shadow: 0 4px 14px rgba(180,15,40,.28);
    box-sizing: border-box;
    width: 100%;
}
.pma-hl { flex:1; min-width:0; }
.pma-title {
    color:#fff; font-size:18px; font-weight:700; margin:0;
    line-height:1.3; white-space:normal; word-break:break-word;
}
.pma-sub { color:rgba(255,255,255,.68); font-size:11px; margin:3px 0 0; }
.pma-date {
    color:#fff; font-size:12px; font-weight:600;
    background:rgba(255,255,255,.18); border-radius:6px;
    padding:6px 14px; font-family:'IBM Plex Mono',monospace;
    white-space:nowrap; flex-shrink:0;
}

/* ════ UPDATE BAR ════ */
.upd-bar {
    background:#EAE2D8; border-radius:6px; padding:7px 14px;
    font-size:11px; color:#6B5E57;
    display:flex; justify-content:space-between; margin-bottom:14px;
}

/* ════ KPI CARDS ════ */
.kpi {
    background:#fff; border-radius:8px; padding:14px 12px 12px;
    border-left:4px solid #C8192E;
    box-shadow:0 1px 4px rgba(0,0,0,.07); min-height:84px;
}
.kpi.green  { border-left-color:#0F9D58; }
.kpi.gold   { border-left-color:#E8A000; }
.kpi.orange { border-left-color:#E65C00; }
.kpi.stone  { border-left-color:#7B6E66; }
.kpi-lbl { font-size:9.5px; font-weight:700; color:#8C7B72; text-transform:uppercase; letter-spacing:.9px; margin:0; }
.kpi-val { font-size:21px; font-weight:700; color:#1E1E1E; font-family:'IBM Plex Mono',monospace; margin:5px 0 2px; line-height:1; }
.kpi-sub { font-size:10px; color:#A0908A; margin:0; }

/* ════ BUCKET STRIP ════ */
.bk-strip { display:flex; gap:5px; margin-bottom:18px; }
.bk-cell {
    flex:1; background:#fff; border-radius:6px; padding:9px 6px;
    text-align:center; border-top:3px solid #DDD5CC;
    box-shadow:0 1px 3px rgba(0,0,0,.06);
}
.bk-lbl { font-size:8.5px; font-weight:700; color:#8C7B72; text-transform:uppercase; letter-spacing:.4px; margin:0; }
.bk-val { font-size:12.5px; font-weight:700; color:#1E1E1E; font-family:'IBM Plex Mono',monospace; margin:3px 0 0; }

/* ════ SO BLOCK CARDS ════ */
.so-wrap { display:flex; gap:12px; margin-bottom:6px; }
.so-card { flex:1; border-radius:10px; padding:18px 18px 15px; box-shadow:0 2px 8px rgba(0,0,0,.09); }
.so-warn { background:#FFFBF0; border-left:5px solid #F5A623; }
.so-soft { background:#FFF4EE; border-left:5px solid #E65C00; }
.so-crit { background:#FFF0F2; border-left:5px solid #C8192E; }
.so-badge {
    display:inline-block; font-size:9px; font-weight:700; border-radius:4px;
    padding:3px 8px; letter-spacing:.6px; text-transform:uppercase; margin-bottom:8px;
}
.so-badge.warn { background:#F5A623; color:#fff; }
.so-badge.soft { background:#E65C00; color:#fff; }
.so-badge.crit { background:#C8192E; color:#fff; }
.so-val  { font-size:28px; font-weight:700; font-family:'IBM Plex Mono',monospace; color:#1E1E1E; margin:0; line-height:1.1; }
.so-sub  { font-size:11.5px; color:#6B5E57; margin:5px 0 0; }
.so-desc { font-size:10px; color:#9A8A82; margin:7px 0 0; font-style:italic; }

/* ════ SECTION TITLE ════ */
.sec {
    font-size:10.5px; font-weight:700; color:#C8192E; text-transform:uppercase;
    letter-spacing:1.2px; margin:22px 0 8px;
    padding-bottom:6px; border-bottom:1.5px solid #DDD5CC;
}

/* ════ TABLE ════ */
[data-testid="stDataFrame"] thead th {
    background:#EDE5DC !important; color:#1E1E1E !important;
    font-size:11px !important; font-weight:700 !important;
    text-transform:uppercase !important; letter-spacing:.4px !important;
}
[data-testid="stDataFrame"] tbody td { font-size:12px !important; color:#333 !important; }
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

# ── Warna cerah & hidup — bukan kusam ───────────────────────────────────────
BUCKET_COLOR = {
    "CURRENT":    "#0F9D58",   # hijau Google
    "1-7 DAYS":   "#F5A623",   # amber cerah
    "8-30 DAYS":  "#F5A623",
    "31-60 DAYS": "#E65C00",   # oranye tua
    "61-90 DAYS": "#E65C00",
    "91-120 DAYS":"#C8192E",   # merah PMA
    "121+ DAYS":  "#8C0A1C",   # merah tua
    "<2026":      "#6B6B6B",   # abu
}
# SO Block warna cerah
SO_COLORS = {
    "WARNING SO":     "#F5A623",
    "SOFT BLOCK":     "#E65C00",
    "CRITICAL BLOCK": "#C8192E",
}
SO_MAP = {
    "1-7 DAYS":"WARNING SO","8-30 DAYS":"WARNING SO",
    "31-60 DAYS":"SOFT BLOCK","61-90 DAYS":"SOFT BLOCK",
    "91-120 DAYS":"CRITICAL BLOCK","121+ DAYS":"CRITICAL BLOCK","<2026":"CRITICAL BLOCK",
}

# Palet chart — hidup, beragam, tidak kusam
CHART_PALETTE = [
    "#C8192E","#F5A623","#0F9D58","#1A73E8",
    "#9B27AF","#E65C00","#00897B","#E91E8C",
    "#546E7A","#6D4C41",
]

# ── FORMAT ───────────────────────────────────────────────────────────────────
def M(v):
    v = float(v)
    if abs(v)>=1_000_000_000: return f"{v/1_000_000_000:.2f}M"
    if abs(v)>=1_000_000:     return f"{v/1_000_000:.1f}Jt"
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
        for col in ALL_COLUMNS:
            if col not in df.columns: df[col]=None
        df = df[ALL_COLUMNS].copy()
        for col in NUMERIC_COLS:
            df[col] = pd.to_numeric(df[col],errors="coerce").fillna(0)
        for col in DATE_COLS:
            df[col] = pd.to_datetime(df[col],errors="coerce")
        return df, last_updated
    except Exception as e:
        st.error(f"Gagal ambil data: {e}")
        return pd.DataFrame(), last_updated

# ── PLOTLY BASE ───────────────────────────────────────────────────────────────
FONT = dict(family="Inter,sans-serif", size=11, color="#1E1E1E")
def plot_base(fig, h=300, margin=None):
    m = margin or dict(t=14,b=10,l=6,r=6)
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="rgba(0,0,0,0)",
        font=FONT, height=h, margin=m,
        xaxis=dict(gridcolor="#EDE5DC", linecolor="#D0C8BF", tickfont_size=10),
        yaxis=dict(gridcolor="#EDE5DC", linecolor="#D0C8BF", tickfont_size=10),
        showlegend=False,
    )
    return fig

def sec(t): st.markdown(f"<p class='sec'>{t}</p>", unsafe_allow_html=True)

def dl_btn(df_export, filename, label="⬇️ Download CSV"):
    """Tombol download CSV kecil, konsisten di semua section."""
    csv = df_export.to_csv(index=False, sep=";", encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(label, data=csv,
                       file_name=f"{filename}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                       mime="text/csv", use_container_width=True)

def kpi(co, label, val, sub="", cls=""):
    with co:
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

    # ── HEADER — tidak terpotong ──────────────────────────────────
    st.markdown(f"""
    <div class="pma-header">
      <div class="pma-hl">
        <p class="pma-title">AR Outstanding MT — MTI NKA</p>
        <p class="pma-sub">PT Pinus Merah Abadi &nbsp;·&nbsp; FAD Team</p>
      </div>
      <span class="pma-date">{datetime.now().strftime('%d %b %Y')}</span>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.warning("Belum ada data. Jalankan **JALANKAN_UPLOAD.bat** untuk upload data.")
        return

    # ── SIDEBAR ───────────────────────────────────────────────────
    st.sidebar.markdown("### Filter")
    def sb_sel(label, col, src):
        opts = ["Semua"] + sorted(src[col].dropna().unique().tolist())
        return st.sidebar.selectbox(label, opts, key=f"f_{col}")

    sel_region = sb_sel("Region",       "REGION",       df)
    d0 = df if sel_region=="Semua" else df[df["REGION"]==sel_region]
    sel_area   = sb_sel("Nama Area",    "NAMA AREA",    d0)
    d1 = d0 if sel_area=="Semua" else d0[d0["NAMA AREA"]==sel_area]
    sel_jenis  = sb_sel("Jenis Outlet", "JENIS OUTLET", d1)
    sel_asm    = sb_sel("ASM",          "ASM",          d1)
    sel_rbm    = sb_sel("RBM",          "RBM",          d1)
    sel_grp    = sb_sel("Grouping OS",  "GROUPING OS",  d1)
    sel_bkt    = st.sidebar.multiselect("Kelompok Aging", BUCKETS, default=BUCKETS)
    st.sidebar.markdown("---")
    if st.sidebar.button("↺  Refresh Data", use_container_width=True):
        st.cache_data.clear(); st.rerun()
    st.sidebar.caption(f"Update: {last_updated}")

    # ── APPLY FILTER ──────────────────────────────────────────────
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

    # ── UPDATE BAR ────────────────────────────────────────────────
    st.markdown(f"""
    <div class="upd-bar">
      <span>⏱ Update terakhir: <strong>{last_updated}</strong></span>
      <span>{len(dff):,} faktur ditampilkan</span>
    </div>""", unsafe_allow_html=True)

    # ── KPI UTAMA ─────────────────────────────────────────────────
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

    # ── BUCKET STRIP ──────────────────────────────────────────────
    bv = {b: dff[b].sum() for b in BUCKETS}
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

    # ════════════════════════════════════════════════════════════════
    # SO BLOCK
    # ════════════════════════════════════════════════════════════════
    sec("STATUS SO BLOCK — REKOMENDASI TINDAKAN")

    df_ov = dff[dff["KELOMPOK"]!="CURRENT"].copy()
    df_ov["SO_KAT"] = df_ov["KELOMPOK"].map(SO_MAP)

    def so_kpi(k):
        sub = df_ov[df_ov["SO_KAT"]==k]
        return sub["NOMINAL"].sum(), len(sub), sub["NAMA AREA"].nunique()

    wn, wf, wa = so_kpi("WARNING SO")
    sn, sf, sa = so_kpi("SOFT BLOCK")
    cn, cf, ca = so_kpi("CRITICAL BLOCK")

    st.markdown(f"""
    <div class="so-wrap">
      <div class="so-card so-warn">
        <span class="so-badge warn">⚠ Warning SO</span>
        <p class="so-val">{M(wn)}</p>
        <p class="so-sub">{wf:,} faktur &nbsp;·&nbsp; {wa} area</p>
        <p class="so-desc">1–7 hari & 8–30 hari — segera follow up sebelum eskalasi</p>
      </div>
      <div class="so-card so-soft">
        <span class="so-badge soft">🔶 Soft Block</span>
        <p class="so-val">{M(sn)}</p>
        <p class="so-sub">{sf:,} faktur &nbsp;·&nbsp; {sa} area</p>
        <p class="so-desc">31–60 & 61–90 hari — pertimbangkan hold pengiriman baru</p>
      </div>
      <div class="so-card so-crit">
        <span class="so-badge crit">🔴 Critical Block</span>
        <p class="so-val">{M(cn)}</p>
        <p class="so-sub">{cf:,} faktur &nbsp;·&nbsp; {ca} area</p>
        <p class="so-desc">91–120, 121+ hari & &lt;2026 — blokir SO, eskalasi manajemen</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Tabel top area per SO
    cw, cs, cc = st.columns(3)
    def so_tbl(co, kat, title):
        with co:
            st.caption(f"**Top Area — {title}**")
            sub = df_ov[df_ov["SO_KAT"]==kat]
            if sub.empty: st.info("Tidak ada data"); return
            t = (sub.groupby("NAMA AREA")
                 .agg(Nominal=("NOMINAL","sum"),Faktur=("No Faktur","count"))
                 .reset_index().sort_values("Nominal",ascending=False).head(10))
            t["%"] = t["Nominal"].apply(lambda v: P(v,sub["NOMINAL"].sum()))
            t["Nominal"] = t["Nominal"].apply(M)
            t.columns = ["Nama Area","Nominal","Faktur","%"]
            st.dataframe(t, use_container_width=True, hide_index=True, height=300)

    so_tbl(cw,"WARNING SO",     "⚠ Warning SO")
    so_tbl(cs,"SOFT BLOCK",     "🔶 Soft Block")
    so_tbl(cc,"CRITICAL BLOCK", "🔴 Critical Block")

    # Download SO Block lengkap
    df_so_dl = df_ov[["NAMA AREA","RBM","ASM","No Faktur","NAMA TOKO",
                       "NOMINAL","KELOMPOK","SO_KAT","OVERDUE?"]].copy()
    df_so_dl.columns = ["Nama Area","RBM","ASM","No Faktur","Nama Toko",
                        "Nominal","Kelompok","SO Kategori","Hari OD"]
    dl_btn(df_so_dl, "SO_BLOCK_DETAIL", "⬇️ Download SO Block Detail (semua kategori)")

    # Stacked bar SO Block per area — warna cerah
    sec("DISTRIBUSI SO BLOCK PER NAMA AREA")
    pivot = (df_ov.groupby(["NAMA AREA","SO_KAT"])["NOMINAL"]
             .sum().unstack(fill_value=0).reset_index())
    for k in ["WARNING SO","SOFT BLOCK","CRITICAL BLOCK"]:
        if k not in pivot.columns: pivot[k]=0
    pivot["TOTAL"] = pivot[["WARNING SO","SOFT BLOCK","CRITICAL BLOCK"]].sum(axis=1)
    pivot = pivot.nlargest(10,"TOTAL")

    fig_so = go.Figure()
    so_cfg = [
        ("CRITICAL BLOCK","#C8192E","🔴 Critical Block"),
        ("SOFT BLOCK",    "#E65C00","🔶 Soft Block"),
        ("WARNING SO",    "#F5A623","⚠ Warning SO"),
    ]
    for col_key,color,name in so_cfg:
        if col_key in pivot.columns:
            fig_so.add_trace(go.Bar(
                name=name, x=pivot["NAMA AREA"], y=pivot[col_key],
                marker_color=color,
                text=pivot[col_key].apply(lambda v: M(v) if v>0 else ""),
                textposition="inside", textfont=dict(size=9,color="#fff"),
            ))
    plot_base(fig_so, h=360)
    fig_so.update_layout(
        barmode="stack", showlegend=True,
        legend=dict(orientation="h",x=0,y=1.06,font_size=11),
        xaxis_tickangle=-35, yaxis_tickformat=",",
    )
    st.plotly_chart(fig_so, use_container_width=True)

    # ════════════════════════════════════════════════════════════════
    # KOMPOSISI OUTSTANDING
    # ════════════════════════════════════════════════════════════════
    sec("KOMPOSISI OUTSTANDING")
    ca2, cb2 = st.columns([5,4])

    with ca2:
        grp_os = (dff[dff["NOMINAL"]>0].groupby("GROUPING OS")["NOMINAL"]
                  .sum().sort_values().reset_index())
        grp_os.columns = ["Kategori","Nominal"]
        colors_h = CHART_PALETTE[:len(grp_os)]
        fig_h = go.Figure(go.Bar(
            x=grp_os["Nominal"], y=grp_os["Kategori"], orientation="h",
            marker_color=colors_h,
            text=[M(v) for v in grp_os["Nominal"]],
            textposition="outside", textfont=dict(size=10,color="#1E1E1E"),
        ))
        plot_base(fig_h, h=300)
        fig_h.update_layout(xaxis_tickformat=",")
        st.plotly_chart(fig_h, use_container_width=True)

    with cb2:
        pie_labels = [b for b in BUCKETS if bv[b]>0]
        pie_vals   = [bv[b] for b in BUCKETS if bv[b]>0]
        pie_colors = [BUCKET_COLOR[b] for b in BUCKETS if bv[b]>0]
        fig_pie = go.Figure(go.Pie(
            labels=pie_labels, values=pie_vals,
            marker_colors=pie_colors, hole=0.55,
            textinfo="percent", textfont_size=11,
            hovertemplate="%{label}: %{value:,.0f}<extra></extra>",
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=300, margin=dict(t=12,b=12,l=0,r=0),
            legend=dict(font_size=10,x=1.01,y=0.5,xanchor="left"),
            showlegend=True,
            annotations=[dict(
                text=f"<b>{M(grand)}</b><br><span style='font-size:9px'>Total OS</span>",
                x=0.5,y=0.5,showarrow=False,font=dict(size=14,color="#1E1E1E"),
            )],
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ════════════════════════════════════════════════════════════════
    # TABEL WILAYAH & KATEGORI
    # ════════════════════════════════════════════════════════════════
    sec("OUTSTANDING PER WILAYAH & KATEGORI")
    cc2, cd2 = st.columns(2)

    with cc2:
        st.caption("**Per Nama Area** — Nilai Faktur · Current · Overdue · % Curr/OD")
        t_area = (dff.groupby("NAMA AREA")
                  .agg(NF=("Nilai Faktur","sum"),Cur=("CURRENT","sum"),Ov=("OVERDUE","sum"))
                  .reset_index().sort_values("NF",ascending=False))
        t_area["% C/OD"] = t_area.apply(lambda r: P(r["Cur"],r["Cur"]+r["Ov"]),axis=1)
        for c in ["NF","Cur","Ov"]: t_area[c]=t_area[c].apply(M)
        t_area.columns = ["Nama Area","Nilai Faktur","Current","Overdue","% Curr/OD"]
        st.dataframe(t_area, use_container_width=True, hide_index=True, height=340)

    with cd2:
        st.caption("**Per Kategori Overdue**")
        t_kat = (dff[dff["NOMINAL"]>0].groupby("KATEGORI OVERDUE")
                 .agg(Nominal=("NOMINAL","sum"),Faktur=("No Faktur","count"))
                 .reset_index().sort_values("Nominal",ascending=False))
        t_kat["%"] = t_kat["Nominal"].apply(lambda v: P(v,total_nom))
        t_kat["Nominal"] = t_kat["Nominal"].apply(R)
        t_kat.columns = ["Kategori Overdue","Nominal","Jml Faktur","%"]
        st.dataframe(t_kat, use_container_width=True, hide_index=True, height=340)

    # Download: per area & per kategori
    dw1, dw2 = st.columns(2)
    with dw1:
        t_area_dl = (dff.groupby("NAMA AREA")
                     .agg(NF=("Nilai Faktur","sum"),Cur=("CURRENT","sum"),Ov=("OVERDUE","sum"))
                     .reset_index().sort_values("NF",ascending=False))
        t_area_dl.columns = ["Nama Area","Nilai Faktur","Current","Overdue"]
        dl_btn(t_area_dl, "OUTSTANDING_PER_AREA")
    with dw2:
        t_kat_dl = (dff[dff["NOMINAL"]>0].groupby("KATEGORI OVERDUE")
                    .agg(Nominal=("NOMINAL","sum"),Faktur=("No Faktur","count"))
                    .reset_index().sort_values("Nominal",ascending=False))
        t_kat_dl.columns = ["Kategori Overdue","Nominal","Jml Faktur"]
        dl_btn(t_kat_dl, "OUTSTANDING_PER_KATEGORI")

    # ════════════════════════════════════════════════════════════════
    # COLLECTION
    # ════════════════════════════════════════════════════════════════
    sec("COLLECTION — ACTUAL vs TARGET PELUNASAN")
    ce2, cf2 = st.columns([5,4])

    with ce2:
        t_coll = (dff.groupby("NAMA AREA")
                  .agg(Actual=("ACTUAL PELUNASAN","sum"),Target=("TARGET PELUNASAN","sum"))
                  .reset_index())
        t_coll = t_coll[t_coll["Target"]>0].nlargest(12,"Target")
        fig_c = go.Figure()
        fig_c.add_trace(go.Bar(
            name="Target", x=t_coll["NAMA AREA"], y=t_coll["Target"],
            marker_color="#D0C8BE",
            text=[M(v) for v in t_coll["Target"]],
            textposition="outside", textfont=dict(size=9,color="#555"),
        ))
        fig_c.add_trace(go.Bar(
            name="Actual", x=t_coll["NAMA AREA"], y=t_coll["Actual"],
            marker_color="#C8192E",
            text=[M(v) for v in t_coll["Actual"]],
            textposition="outside", textfont=dict(size=9,color="#C8192E"),
        ))
        plot_base(fig_c, h=340)
        fig_c.update_layout(
            barmode="group", showlegend=True,
            legend=dict(orientation="h",x=0,y=1.08,font_size=11),
            xaxis_tickangle=-30, yaxis_tickformat=",",
        )
        st.plotly_chart(fig_c, use_container_width=True)

    with cf2:
        st.caption("**Collection Rate per ASM**")
        t_asm = (dff.groupby("ASM")
                 .agg(Actual=("ACTUAL PELUNASAN","sum"),
                      Target=("TARGET PELUNASAN","sum"),
                      OS=("NOMINAL","sum"))
                 .reset_index())
        t_asm = t_asm[t_asm["Target"]>0].sort_values("Target",ascending=False)
        t_asm["%Coll"] = t_asm.apply(lambda r: P(r["Actual"],r["Target"]),axis=1)
        for c in ["Actual","Target","OS"]: t_asm[c]=t_asm[c].apply(M)
        t_asm.columns = ["ASM","Actual","Target","Outstanding","% Coll"]
        st.dataframe(t_asm, use_container_width=True, hide_index=True, height=340)

    # Download collection
    dc1, dc2 = st.columns(2)
    with dc1:
        t_coll_dl = (dff.groupby("NAMA AREA")
                     .agg(Actual=("ACTUAL PELUNASAN","sum"),Target=("TARGET PELUNASAN","sum"))
                     .reset_index())
        t_coll_dl["%Coll"] = t_coll_dl.apply(lambda r: P(r["Actual"],r["Target"]),axis=1)
        t_coll_dl.columns = ["Nama Area","Actual Pelunasan","Target Pelunasan","% Collection"]
        dl_btn(t_coll_dl, "COLLECTION_PER_AREA")
    with dc2:
        t_asm_dl = (dff.groupby("ASM")
                    .agg(Actual=("ACTUAL PELUNASAN","sum"),Target=("TARGET PELUNASAN","sum"),
                         OS=("NOMINAL","sum"))
                    .reset_index())
        t_asm_dl["%Coll"] = t_asm_dl.apply(lambda r: P(r["Actual"],r["Target"]),axis=1)
        t_asm_dl.columns = ["ASM","Actual","Target","Outstanding","% Coll"]
        dl_btn(t_asm_dl, "COLLECTION_PER_ASM")

    # ════════════════════════════════════════════════════════════════
    # BREAKDOWN OUTLET & RBM
    # ════════════════════════════════════════════════════════════════
    sec("BREAKDOWN JENIS OUTLET & RBM")
    cg2, ch2 = st.columns([4,5])

    with cg2:
        t_out = (dff.groupby("JENIS OUTLET")
                 .agg(OS=("NOMINAL","sum"),OV=("OVERDUE","sum"))
                 .reset_index().sort_values("OS",ascending=False).head(12))
        t_out["%OD"] = t_out.apply(lambda r: P(r["OV"],r["OS"]),axis=1)
        for c in ["OS","OV"]: t_out[c]=t_out[c].apply(M)
        t_out.columns = ["Jenis Outlet","Outstanding","Overdue","%OD"]
        st.dataframe(t_out, use_container_width=True, hide_index=True, height=340)

    with ch2:
        t_rbm = (dff.groupby("RBM")
                 .agg(OS=("NOMINAL","sum"),OV=("OVERDUE","sum"),
                      Akt=("ACTUAL PELUNASAN","sum"),Tgt=("TARGET PELUNASAN","sum"))
                 .reset_index().sort_values("OS",ascending=False))
        t_rbm["%OD"]   = t_rbm.apply(lambda r: P(r["OV"],r["OS"]),axis=1)
        t_rbm["%Coll"] = t_rbm.apply(lambda r: P(r["Akt"],r["Tgt"]),axis=1)
        for c in ["OS","OV","Akt","Tgt"]: t_rbm[c]=t_rbm[c].apply(M)
        t_rbm.columns = ["RBM","Outstanding","Overdue","Actual Pel.","Target Pel.","%OD","%Coll"]
        st.dataframe(t_rbm, use_container_width=True, hide_index=True, height=340)

    # Download outlet & RBM
    do1, do2 = st.columns(2)
    with do1:
        t_out_dl = (dff.groupby("JENIS OUTLET")
                    .agg(OS=("NOMINAL","sum"),OV=("OVERDUE","sum"))
                    .reset_index().sort_values("OS",ascending=False))
        t_out_dl["%OD"] = t_out_dl.apply(lambda r: P(r["OV"],r["OS"]),axis=1)
        t_out_dl.columns = ["Jenis Outlet","Outstanding","Overdue","%OD"]
        dl_btn(t_out_dl, "BREAKDOWN_OUTLET")
    with do2:
        t_rbm_dl = (dff.groupby("RBM")
                    .agg(OS=("NOMINAL","sum"),OV=("OVERDUE","sum"),
                         Akt=("ACTUAL PELUNASAN","sum"),Tgt=("TARGET PELUNASAN","sum"))
                    .reset_index())
        t_rbm_dl["%OD"]   = t_rbm_dl.apply(lambda r: P(r["OV"],r["OS"]),axis=1)
        t_rbm_dl["%Coll"] = t_rbm_dl.apply(lambda r: P(r["Akt"],r["Tgt"]),axis=1)
        t_rbm_dl.columns = ["RBM","Outstanding","Overdue","Actual Pel.","Target Pel.","%OD","%Coll"]
        dl_btn(t_rbm_dl, "BREAKDOWN_RBM")

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
        if c in tbl.columns: tbl[c]=tbl[c].apply(R)
    tbl.rename(columns={
        "NAMA AREA":"Nama Area","NAMA SALES":"Nama Sales","NAMA TOKO":"Nama Toko",
        "Saldo Akhir":"Sisa AR","OVERDUE?":"Hari OD","KELOMPOK":"Kelompok",
        "GROUPING OS":"Grouping OS",
    },inplace=True)
    tbl.insert(0,"#",range(1,len(tbl)+1))

    with st.expander(f"🔽 Tampilkan {len(tbl):,} baris · OS Total: {M(total_nom)}",expanded=False):
        st.dataframe(tbl, use_container_width=True, hide_index=True, height=460)
        st.download_button(
            "⬇️ Download CSV (hasil filter)",
            data=dff[cols_ok].to_csv(index=False,sep=";",encoding="utf-8-sig").encode("utf-8-sig"),
            file_name=f"OS_MTI_NKA_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.markdown(
        f"<p style='text-align:center;color:#A0908A;font-size:11px;"
        f"font-family:IBM Plex Mono,monospace'>"
        f"AR OTC · PT Pinus Merah Abadi · FAD Team · "
        f"data {last_updated} · render {datetime.now().strftime('%d %b %Y %H:%M')}"
        f"</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
