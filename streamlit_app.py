
import io, json, os, numpy as np, pandas as pd, matplotlib.pyplot as plt
import streamlit as st

# Reuse bundle code
from evelution.calibration.mappings import load_mapping, LinearMap, LogisticMap, PHMap
from evelution.export.methods import export_methods_md
from evelution.data.instruments import parse_nta_csv, parse_trps_csv, parse_flow_csv, export_standard
from evelution.compliance.evtrack import score as evtrack_score
from evelution.physics.electrostatics import delta_pKa_from_surface_potential, fraction_protonated, debye_length_nm

st.set_page_config(page_title="EVelution — Micelle Genesis", layout="wide")
theme_choice = st.sidebar.selectbox('Theme', ['Minimal','Classic'], index=0)
if theme_choice=='Minimal':
    st.markdown(open('content/themes/minimal.css','r').read(), unsafe_allow_html=True)

# --- Styling (simple, inline CSS) ---
st.markdown('''
<style>
  .evelution-hero { 
    padding: 28px 24px; border-radius: 18px; 
    background: radial-gradient(1200px 600px at 20% 10%, rgba(124,189,255,0.25), rgba(255,255,255,0));
    border: 1px solid rgba(120,120,180,0.25);
  }
  .muted {color: #57606a;}
  .pill {display:inline-block;padding:4px 10px;border-radius:999px;background:#eef2ff;border:1px solid #c7d2fe;font-size:12px;color:#3730a3;margin-right:6px;}
  .cta {font-weight:600;padding:8px 14px;border-radius:10px;border:1px solid #cbd5e1;background:#f1f5f9;}
</style>
''', unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("EVelution")
user_id = st.sidebar.text_input("User ID", "trial")
if "entered" not in st.session_state:
    st.session_state.entered = False

# ----------- FIRST SLIDE: MICELLE GENESIS -----------
st.markdown('<div class="ev-hero">', unsafe_allow_html=True)
st.markdown("### Micelle Genesis")
st.markdown('<div class="ev-muted">Start here: surfactants self‑assemble. Surface potential (Ψ) bends chemistry near the membrane.</div>', unsafe_allow_html=True)

colA, colB = st.columns([2,3])

with colA:
    st.markdown('<span class="ev-pill">concept</span> critical micelle concentration (CMC)', unsafe_allow_html=True)
    conc = st.slider("Total surfactant concentration (mM)", 0.0, 20.0, 6.0, 0.1)
    cmc  = st.slider("CMC (mM)", 0.0, 10.0, 5.0, 0.1)
    st.markdown('<span class="ev-pill">electrostatics</span> Ψ and screening', unsafe_allow_html=True)
    psi_mV = st.slider("Surface potential Ψ (mV)", -150, 150, -40, step=5)
    ionic  = st.slider("Ionic strength (M)", 0.00, 0.50, 0.15, 0.01)
    z = st.selectbox("Probe charge change z", [-2,-1,1,2], index=2)
    pKa_bulk = st.number_input("Indicator pKa (bulk)", value=7.0, step=0.1)

    # quick metrics
    dpk = delta_pKa_from_surface_potential(psi_mV/1000.0, float(z))
    pKa_app = pKa_bulk + dpk
    lamD = debye_length_nm(float(ionic))
    st.metric("ΔpKa (surface − bulk)", f"{dpk:+.2f}")
    st.metric("Debye length (nm)", f"{lamD:.1f}")

    go = st.button("Continue → Enter Sandbox", use_container_width=True)
    if go:
        st.session_state.entered = True

def draw_micelle(ax, center=(0,0), radius=1.0, heads=28, psi_mV=-40):
    # color by sign of Ψ
    c = "#5B8DEF" if psi_mV<=0 else "#C26DFF"
    theta = np.linspace(0, 2*np.pi, heads, endpoint=False)
    x = center[0] + radius*np.cos(theta)
    y = center[1] + radius*np.sin(theta)
    # heads
    ax.scatter(x, y, s=30, edgecolors=c, facecolors="white", linewidths=1.5, zorder=3)
    # tails (inward lines)
    for xi, yi, th in zip(x, y, theta):
        ax.plot([xi, center[0]+0.25*np.cos(th)], [yi, center[1]+0.25*np.sin(th)], color=c, lw=1.2, alpha=0.9, zorder=2)
    # outline
    circ = plt.Circle(center, radius, fill=False, color=c, lw=1.0, alpha=0.7)
    ax.add_artist(circ)

with colB:
    fig, ax = plt.subplots(figsize=(6.2,4.0), dpi=200)
    ax.set_aspect('equal')
    ax.axis("off")
    if conc <= cmc + 1e-9:
        # monomers scattered
        rng = np.random.default_rng(42)
        pts = rng.uniform(-2.6, 2.6, size=(80,2))
        color = "#5B8DEF" if psi_mV<=0 else "#C26DFF"
        ax.scatter(pts[:,0], pts[:,1], s=18, edgecolors=color, facecolors="white", linewidths=1.2, alpha=0.9)
        ax.text(-2.6, 2.6, "Below CMC → monomers", fontsize=10, color="#334155")
    else:
        # one primary micelle, optionally a couple satellites
        draw_micelle(ax, (0,0), 1.5, heads=36, psi_mV=psi_mV)
        if conc > 1.5*cmc:
            draw_micelle(ax, (2.3,1.2), 0.9, heads=20, psi_mV=psi_mV)
            draw_micelle(ax, (-2.1,-1.4), 0.8, heads=18, psi_mV=psi_mV)
        ax.text(-2.6, 2.6, "Above CMC → micelles", fontsize=10, color="#334155")
    st.pyplot(fig, clear_figure=True)

    # Titration curves
    pH = np.linspace(3, 11, 400)
    frac_bulk = 1.0/(1.0 + 10**(pH - pKa_bulk))
    frac_app  = 1.0/(1.0 + 10**(pH - pKa_app))
    fig2, ax2 = plt.subplots(figsize=(6.2,2.6), dpi=200)
    ax2.plot(pH, frac_bulk, label="bulk", lw=2)
    ax2.plot(pH, frac_app,  label="near Ψ surface", lw=2)
    ax2.set_xlabel("pH"); ax2.set_ylabel("fraction protonated")
    ax2.legend(frameon=False)
    st.pyplot(fig2, clear_figure=True)

st.markdown('</div>', unsafe_allow_html=True)

# Gate the rest of the app behind the first slide
if not st.session_state.entered:
    st.stop()

# ----------- SANDBOX (calibrated sliders + explain-why) -----------
st.header("Sandbox — Calibrated Story & Explain‑Why")
c1, c2, c3, c4 = st.columns(4)

def load_or_default(var, unit, xmin, xmax, invert=False):
    p = f"content/calibrations/{user_id}/{var}.json"
    if os.path.exists(p):
        return load_mapping(p)
    return LinearMap(unit=unit, xmin=xmin, xmax=xmax, invert=invert)

m_o2   = load_or_default("E_O2", "%O2", 0.0, 21.0)
m_atp  = load_or_default("I_ATP", "mM", 0.0, 5.0)
m_ros  = load_or_default("I_ROS", "AU", 0.0, 10.0)
m_escrt= load_or_default("S_ESCRT", "AU", 0.0, 1.0)

with c1:
    u_o2 = st.number_input(f"O2 ({m_o2.unit})", value=float(getattr(m_o2, "xmin", 0.0)))
    n_o2 = m_o2.to01(u_o2)
    st.caption(f"map: {m_o2.__class__.__name__}")
with c2:
    u_atp = st.number_input(f"ATP ({m_atp.unit})", value=float(getattr(m_atp, "xmin", 0.0)))
    n_atp = m_atp.to01(u_atp)
    st.caption(f"map: {m_atp.__class__.__name__}")
with c3:
    u_ros = st.number_input(f"ROS ({m_ros.unit})", value=float(getattr(m_ros, "xmin", 0.0)))
    n_ros = m_ros.to01(u_ros)
    st.caption(f"map: {m_ros.__class__.__name__}")
with c4:
    u_es  = st.number_input(f"ESCRT ({m_escrt.unit})", value=float(getattr(m_escrt, "xmin", 0.0)))
    n_es  = m_escrt.to01(u_es)
    st.caption(f"map: {m_escrt.__class__.__name__}")

# Explain-Why chart (demo)
gS = 1.0/(1.0 + np.exp(-6*(n_es-0.5)))
gW = 0.6*n_atp + 0.4*(1.0-n_ros)
stress = 1.0 + 0.25*(0.5 - n_o2)
parts = {"log g_S": np.log(gS+1e-9), "log g_W": np.log(gW+1e-9), "log λ(O2)": np.log(stress+1e-9)}

figE, axE = plt.subplots(figsize=(4,2.5), dpi=200)
axE.bar(list(parts.keys()), list(parts.values()))
axE.set_ylabel("log contribution")
axE.set_title("Explain‑Why: log r = log r_T + log g_S + log g_W + Σ log λ_s")
st.pyplot(figE, clear_figure=True)

with st.expander("Exact mappings used"):
    st.write(f"O2 → {m_o2.__class__.__name__}")
    st.write(f"ATP → {m_atp.__class__.__name__}")
    st.write(f"ROS → {m_ros.__class__.__name__}")
    st.write(f"ESCRT → {m_escrt.__class__.__name__}")

st.divider()

# ----------- Shared environment demo -----------
st.subheader("Shared environment (demo)")
t = np.arange(0, 10, 1.0)
flux = {"CellA": np.sin(t/3)+1.5, "CellB": np.cos(t/4)+1.2, "CellC": 0.4+0*t}
fig2, ax2 = plt.subplots(figsize=(6,3), dpi=200)
ax2.stackplot(t, np.row_stack([flux[k] for k in flux.keys()]), labels=list(flux.keys()))
ax2.legend(fontsize=8, ncol=3, frameon=False)
ax2.set_xlabel("time"); ax2.set_ylabel("EV flux")
st.pyplot(fig2, clear_figure=True)

# ----------- Per-cell A/B/C dashboard -----------
st.subheader("Per‑cell snapshot compare (demo)")
t = np.arange(0, 12, 1.0)
A = {"time":t, "rate":0.5+0.1*np.sin(t), "W":0.6+0.1*np.cos(t/2), "S":0.5+0.05*np.sin(t/3)}
B = {"time":t, "rate":0.7+0.1*np.sin(t+0.2), "W":0.65+0.1*np.cos(t/2), "S":0.55+0.05*np.sin(t/3)}
C = {"time":t, "rate":0.4+0.1*np.sin(t-0.1), "W":0.5+0.1*np.cos(t/2), "S":0.45+0.05*np.sin(t/3)}

fig3, (ax31, ax32) = plt.subplots(nrows=2, figsize=(6,5), dpi=200)
for k, snap in {"A":A,"B":B,"C":C}.items():
    ax31.plot(snap["time"], snap["rate"], label=f"{k} rate")
ax31.set_ylabel("EV rate"); ax31.legend(fontsize=8, ncol=3, frameon=False)
def pchg(a,b): 
    a=float(a); b=float(b); 
    return 100.0*(b-a)/(abs(a) if abs(a)>1e-9 else 1.0)
metrics = ["rate","W","S"]
valsB = [pchg(A[m][-1], B[m][-1]) for m in metrics]
valsC = [pchg(A[m][-1], C[m][-1]) for m in metrics]
x = np.arange(len(metrics)); width=0.35
ax32.bar(x, valsB, width, label="A→B"); ax32.bar(x+width, valsC, width, label="A→C")
ax32.axhline(0, color="#999", lw=0.5); ax32.set_xticks(x+width/2); ax32.set_xticklabels(metrics)
ax32.set_ylabel("% change"); ax32.legend(frameon=False, fontsize=8)
st.pyplot(fig3, clear_figure=True)

st.divider()

# ----------- Imports & QC -----------
st.subheader("Instrument imports → standardized CSV + QC")
kind = st.selectbox("Instrument kind", ["NTA","TRPS","FLOW"])
up = st.file_uploader("Upload CSV", type=["csv"])
if up is not None:
    tmp = f"/tmp/_import_{kind.lower()}.csv"
    with open(tmp, "wb") as f: f.write(up.read())
    if kind=="NTA": df = parse_nta_csv(tmp)
    elif kind=="TRPS": df = parse_trps_csv(tmp)
    else: df = parse_flow_csv(tmp)
    st.dataframe(df.head(20))
    csv_buf = io.StringIO(); df.to_csv(csv_buf, index=False)
    st.download_button("Download standardized CSV", csv_buf.getvalue(), file_name="standardized.csv", mime="text/csv")
    qc = {
        "rows": int(df.shape[0]),
        "n_outliers": int(df.get("flag_outlier", pd.Series([False])).sum() if "flag_outlier" in df.columns else 0),
        "n_below_lod": int(df.get("flag_below_lod", pd.Series([False])).sum() if "flag_below_lod" in df.columns else 0),
        "n_below_loq": int(df.get("flag_below_loq", pd.Series([False])).sum() if "flag_below_loq" in df.columns else 0),
        "instrument_types": [kind]
    }
    st.json(qc)
    st.download_button("Download QC JSON", json.dumps(qc, indent=2), file_name="qc.json", mime="application/json")

st.divider()

# ----------- EV-TRACK-like scoring -----------
st.subheader("EV‑TRACK-like checklist")
meta = st.text_area("Paste metadata JSON (or leave blank to use trial template)", height=160, value=json.dumps({
    "sample_matrix":"plasma",
    "anticoagulant":"EDTA",
    "processing_time":"45 min to spin",
    "freeze_thaw_count": 0,
    "isolation_method":"SEC after TFF",
    "characterization_methods":["TEM","NTA","WB(tetraspanins)"],
    "markers_reported":["CD9","CD63","CD81","TSG101","ALIX"],
    "instrument_settings":"NTA camera 14; TRPS NP200",
    "calibration_standards":"200 nm polystyrene beads",
    "negative_controls":"blank buffer SEC fractions",
    "data_availability":"zenodo:DOI-TBD",
    "software_versions":"EVelution trial bundle"
}, indent=2))
try:
    md = json.loads(meta)
    sc = evtrack_score(md)
    st.metric("Checklist score", f"{sc['score']} / {sc['total']}")
    with st.expander("Details"):
        st.write("Present:", sc["present"])
        st.write("Missing:", sc["missing"])
    st.download_button("Download score JSON", json.dumps(sc, indent=2), file_name="evtrack_score.json")
except Exception as e:
    st.warning(f"Metadata JSON parse error: {e}")

st.divider()

# ----------- Methods exporter -----------
st.subheader("Methods (Markdown)")
if st.button("Generate Methods.md"):
    p = export_methods_md()
    try:
        with open(p, "r") as f: md = f.read()
        st.code(md, language="markdown")
        st.download_button("Download Methods.md", md, file_name="methods.md")
    except Exception as e:
        st.error(str(e))

st.caption("Prototype: swap the demo formulas with your full model hooks when ready.")
