# -*- coding: utf-8 -*-
"""
Applet Streamlit – Exemple 1 (§8)
Élément composé BFUP armé – béton armé : résistance à la flexion (ELU) et aptitude au service (ELS)

Lancer localement :  streamlit run app.py
"""
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

import bfup_ex1 as core

st.set_page_config(page_title="BFUP armé – béton armé | Ex. 1", layout="wide")

D = core.ex1_inputs()

# ----------------------------------------------------------------------------
# Entrées
# ----------------------------------------------------------------------------
with st.sidebar:
    st.header("Données d'entrée")
    st.caption("Valeurs par défaut : énoncé du cours (p. 38).")

    st.subheader("Dalle existante (béton armé)")
    h_c = st.number_input("h_c = d_sc [mm]", 80.0, 500.0, D["h_c"], 5.0)
    phi_sc = st.number_input("Ø A_s,ct [mm]", 6.0, 40.0, D["phi_sc"], 1.0)
    s_sc = st.number_input("Espacement s_ct [mm]", 50.0, 400.0, D["s_sc"], 10.0)
    f_sk = st.number_input("f_sk [MPa]", 200.0, 700.0, D["f_sk"], 10.0)
    f_ck = st.number_input("f_ck (actualisée) [MPa]", 10.0, 100.0, D["f_ck"], 1.0)

    st.subheader("Couche de BFUP armé")
    h_U = st.number_input("h_U [mm]", 10.0, 150.0, D["h_U"], 5.0)
    phi_sU = st.number_input("Ø A_s,U [mm]", 4.0, 32.0, D["phi_sU"], 1.0)
    s_sU = st.number_input("Espacement s_U [mm]", 25.0, 300.0, D["s_sU"], 5.0)
    f_Utk = st.number_input("f_Utk [MPa]", 0.0, 20.0, D["f_Utk"], 0.5)
    f_sUk = st.number_input("f_sUk [MPa]", 200.0, 700.0, D["f_sUk"], 10.0)

    st.subheader("Actions et sécurité (ELU)")
    M_d = st.number_input("M_d [kNm/m]", 0.0, 1000.0, D["M_d"], 5.0)
    gamma_M = st.number_input("γ_M [-]", 1.0, 2.0, D["gamma_M"], 0.05,
                              help="L'énoncé donne 1.20 ; le corrigé calcule avec 1.30.")
    eps_U_uls = st.number_input("ε_U à l'ELU [‰]", 1.0, 20.0, D["eps_U_uls"], 0.5)
    eps_cu = st.number_input("ε_cu [‰]", 2.0, 5.0, D["eps_cu"], 0.1)

    st.subheader("Aptitude au service (ELS)")
    m_ser = st.number_input("m_ser [kNm/m]", 0.0, 1000.0, D["m_ser"], 5.0)
    eps_U_ser = st.number_input("ε_U,ser (fibre sup.) [‰]", 0.1, 5.0, D["eps_U_ser"], 0.1)
    E_U = st.number_input("E_U [MPa]", 20000.0, 70000.0, D["E_U"], 1000.0)
    E_s = st.number_input("E_s [MPa]", 180000.0, 220000.0, D["E_s"], 1000.0)
    E_c = st.number_input("E_c [MPa]", 15000.0, 50000.0, D["E_c"], 1000.0)
    corr = st.checkbox("Reproduire le tableau ELS du corrigé (d_sc = 171 mm)", value=False)

p = dict(h_c=h_c, d_sc=h_c, phi_sc=phi_sc, s_sc=s_sc, f_sk=f_sk, f_ck=f_ck,
         h_U=h_U, phi_sU=phi_sU, s_sU=s_sU, f_Utk=f_Utk, f_sUk=f_sUk,
         eps_U_uls=eps_U_uls, eps_cu=eps_cu, M_d=M_d, gamma_M=gamma_M,
         m_ser=m_ser, eps_U_ser=eps_U_ser, E_U=E_U, E_s=E_s, E_c=E_c,
         d_sc_ser_corrige=171.0 if corr else h_c)

try:
    r = core.ex1_compute(p)
except ValueError:
    st.error("L'itération sur l'axe neutre à l'ELS n'a pas convergé pour ces données "
             "(pas d'équilibre avec 20 mm < x < h_c). Vérifier les entrées.")
    st.stop()

p = r["p"]
s = r["sls_c"] if corr else r["sls"]
h_top = p["h_c"] + p["h_U"]

# ----------------------------------------------------------------------------
# En-tête et indicateurs
# ----------------------------------------------------------------------------
st.title("Élément composé BFUP armé – béton armé")
st.markdown("Résistance à la flexion à l'ELU (calcul plastique) et aptitude au service à l'ELS · "
            "*Cours « Structures existantes », §8, p. 38-40*")

ok_uls = r["mRd"] >= p["M_d"]
ok_sls = s["m"] >= p["m_ser"]
GEQ_U = r"\geq" if ok_uls else "<"
GEQ_S = r"\geq" if ok_sls else "<"
c1, c2, c3, c4 = st.columns(4)
c1.metric("m_R,0 – dalle BA seule", f"{r['mR0']:.1f} kNm/m")
c2.metric("m_R,1 – section composée", f"{r['mR1']:.1f} kNm/m", f"+{(r['mR1']/r['mR0']-1)*100:.0f} % vs m_R,0")
c3.metric("m_Rd = m_R,1 / γ_M", f"{r['mRd']:.1f} kNm/m",
          f"M_d/m_Rd = {p['M_d']/r['mRd']:.2f} – {'OK' if ok_uls else 'NON'}",
          delta_color="normal" if ok_uls else "inverse", delta_arrow="off")
c4.metric(f"m(ε_U = {p['eps_U_ser']:g}‰) – ELS", f"{s['m']:.1f} kNm/m",
          f"m_ser/m = {p['m_ser']/s['m']:.2f} – {'OK' if ok_sls else 'NON'}",
          delta_color="normal" if ok_sls else "inverse", delta_arrow="off")

# Contrôles de validité du calcul plastique
x = r["x"]
k_uls = p["eps_U_uls"] / (h_top - x)
eps_sU_uls, eps_sc_uls = k_uls * (r["d_sU"] - x), k_uls * (p["d_sc"] - x)
warn = []
if 0.85 * x > p["h_c"]:
    warn.append("La zone comprimée (0.85·x) dépasse la dalle en béton : le modèle n'est plus valable.")
if eps_sc_uls < p["f_sk"] / p["E_s"] * 1e3:
    warn.append(f"A_s,ct ne plastifie pas à l'ELU (ε = {eps_sc_uls:.2f}‰ < {p['f_sk']/p['E_s']*1e3:.2f}‰).")
if eps_sU_uls < p["f_sUk"] / p["E_s"] * 1e3:
    warn.append(f"A_s,U ne plastifie pas à l'ELU (ε = {eps_sU_uls:.2f}‰ < {p['f_sUk']/p['E_s']*1e3:.2f}‰).")
if abs(r["eps_c"]) > p["eps_cu"]:
    warn.append(f"ε_c = {r['eps_c']:.2f}‰ dépasse ε_cu = {p['eps_cu']}‰ : rupture du béton avant ε_U imposé.")
for w in warn:
    st.warning(w)


# ----------------------------------------------------------------------------
# Figures
# ----------------------------------------------------------------------------
def bars_def():
    return [(r["d_sU"], f"A_s,U Ø{p['phi_sU']:.0f}/{p['s_sU']:.0f}\n= {r['A_sU']:.0f} mm²/m"),
            (p["d_sc"], f"A_s,ct Ø{p['phi_sc']:.0f}/{p['s_sc']:.0f}\n= {r['A_sc']:.0f} mm²/m")]


def fig_uls():
    fig, ax = plt.subplots(1, 4, figsize=(17, 5.2), gridspec_kw=dict(wspace=0.3))
    core.draw_layered_section(ax[0], p["h_c"], p["h_U"], bars_def(), x)
    core.draw_strain(ax[1], h_top, p["eps_U_uls"], x, h_top,
                     [(h_top, "ε_U"), (r["d_sU"], "ε_sU"), (p["d_sc"], "ε_sc"), (0, "ε_c")],
                     title=f"Déformations (ε_U = {p['eps_U_uls']:g}‰)")
    core.draw_stress(ax[2],
                     [(np.array([p["h_c"], h_top]), np.array([p["f_Utk"]] * 2), core.C_TENS, "f_Utk"),
                      (np.array([0, 0.85 * x]), np.array([-p["f_ck"]] * 2), core.C_COMP, "f_ck (0.85x)")],
                     [(r["d_sU"], f"f_sUk={p['f_sUk']:.0f}"), (p["d_sc"], f"f_sk={p['f_sk']:.0f}")],
                     x, h_top, title="Contraintes (plastifiées)")
    core.draw_forces(ax[3], [(n, F, d) for n, A, fk, F, d in r["uls_rows"]], h_top)
    fig.subplots_adjust(left=0.05, right=0.98, top=0.9, bottom=0.12)
    return fig


def fig_sls():
    fig, ax = plt.subplots(1, 4, figsize=(17, 5.2), gridspec_kw=dict(wspace=0.3))
    d_sc = p["d_sc_ser_corrige"]
    bars = [bars_def()[0], (d_sc, bars_def()[1][1])]
    core.draw_layered_section(ax[0], p["h_c"], p["h_U"], bars, s["x"])
    core.draw_strain(ax[1], h_top, p["eps_U_ser"], s["x"], h_top,
                     [(h_top, "ε_U"), (r["d_sU"], "ε_sU"), (p["h_c"], "ε_int"), (0, "ε_c")],
                     title="Déformations (ELS)")
    yU, sU = s["sU"]
    core.draw_stress(ax[2], [(yU, sU, core.C_TENS, "BFUP"),
                             (np.array([0, s["x"]]), np.array([s["s_cb"], 0]), core.C_COMP, "béton")],
                     [(r["d_sU"], f"σ_sU={s['comp'][1][2]:.1f}"), (d_sc, f"σ_sc={s['comp'][2][2]:.1f}")],
                     s["x"], h_top, title="Contraintes (ELS)")
    core.draw_forces(ax[3], [(c[0], c[3], c[4]) for c in s["comp"]], h_top)
    fig.subplots_adjust(left=0.05, right=0.98, top=0.9, bottom=0.12)
    return fig


def show(fig, name):
    st.pyplot(fig, width="stretch")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=160)
    plt.close(fig)
    st.download_button(f"Télécharger la figure (PNG)", buf.getvalue(), file_name=name, mime="image/png")



def fmt_table(df, fmts):
    """Formate un tableau en texte (cases vides pour la ligne Σ)."""
    out = df.copy().astype(object)
    for c, f in fmts.items():
        out[c] = [("" if (v is None or (isinstance(v, float) and np.isnan(v))) else f.format(round(v, 6) + 0.0)) for v in df[c]]
    return out

tab1, tab2, tab3, tab4 = st.tabs(["ELU – résistance (1–3)", "ELS – aptitude au service (4)",
                                  "Étude paramétrique", "Hypothèses et notes"])

# ----------------------------------------------------------------------------
with tab1:
    show(fig_uls(), "ex1_ELU.png")
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown("**Calcul plastique – tous les éléments tendus plastifiés**")
        df = pd.DataFrame([(n, A, fk, F, d, F * d / 1e3) for n, A, fk, F, d in r["uls_rows"]],
                          columns=["Élément", "A [mm²/m]", "f_k [MPa]", "F [kN/m]", "d_i [mm]", "m [kNm/m]"])
        df.loc[len(df)] = ["Σ", np.nan, np.nan, df["F [kN/m]"].sum(), np.nan, df["m [kNm/m]"].sum()]
        st.dataframe(fmt_table(df, {c: "{:.1f}" for c in df.columns[1:]}), hide_index=True, width="stretch")
    with right:
        st.markdown("**1) Dalle en béton armé seule**")
        st.latex(rf"m_{{R,0}} = 0.9\,d_{{sc}}\,A_{{sc}}\,f_{{sk}} = 0.9\cdot{p['d_sc']:.0f}\cdot{r['A_sc']:.0f}"
                 rf"\cdot{p['f_sk']:.0f} = {r['mR0']:.1f}\ \mathrm{{kNm/m}}")
        st.markdown("**2) Section composée**")
        st.latex(rf"0.85\,x\cdot 1000\cdot f_{{ck}} = \textstyle\sum F_t = {r['F_c']:.0f}\ \mathrm{{kN/m}}"
                 rf"\ \Rightarrow\ x = {x:.1f}\ \mathrm{{mm}}")
        st.latex(rf"m_{{R,1}} = \textstyle\sum F_i d_i = {r['mR1']:.1f}\ \mathrm{{kNm/m}}")
        st.latex(rf"\varepsilon_c = -\varepsilon_U\,\frac{{x}}{{h_c+h_U-x}} = {r['eps_c']:.2f}\,‰"
                 rf"\ {'>' if abs(r['eps_c']) <= p['eps_cu'] else '<'}\ -{p['eps_cu']}\,‰")
        st.markdown("**3) Sécurité structurale**")
        st.latex(rf"m_{{Rd}} = \frac{{m_{{R,1}}}}{{\gamma_M}} = \frac{{{r['mR1']:.1f}}}{{{p['gamma_M']:.2f}}}"
                 rf" = {r['mRd']:.1f}\ {GEQ_U}\ M_d = {p['M_d']:.0f}\ \mathrm{{kNm/m}}")
        (st.success if ok_uls else st.error)(
            "Sécurité structurale vérifiée." if ok_uls else "Sécurité structurale NON vérifiée.")

# ----------------------------------------------------------------------------
with tab2:
    show(fig_sls(), "ex1_ELS.png")
    left, right = st.columns([1.1, 1])
    with left:
        st.markdown(f"**Analyse en section – ε_U = {p['eps_U_ser']:g}‰ à la fibre supérieure du BFUP**")
        df = pd.DataFrame([c for c in s["comp"]],
                          columns=["Élément", "ε [‰]", "σ [MPa]", "F [kN/m]", "y [mm]", "m [kNm/m]"])
        df.loc[len(df)] = ["Σ", np.nan, np.nan, s["sumF"], np.nan, s["m"]]
        st.dataframe(fmt_table(df, {"ε [‰]": "{:.3f}", "σ [MPa]": "{:.1f}", "F [kN/m]": "{:.1f}",
                                     "y [mm]": "{:.1f}", "m [kNm/m]": "{:.1f}"}),
                     hide_index=True, width="stretch")
        eU_el = p["f_Utk"] / p["E_U"] * 1e3
        st.caption(f"ε_U,elast = {eU_el:.2f}‰ ; ε à l'interface = {s['eps_int']:.2f}‰ → "
                   + ("BFUP entièrement écrouissant." if s["eps_int"] > eU_el else "BFUP partiellement élastique."))
    with right:
        st.latex(rf"x = {s['x']:.1f}\ \mathrm{{mm}}\quad(\text{{itération sur }}\textstyle\sum F = 0)")
        st.latex(rf"m(\varepsilon_U={p['eps_U_ser']:g}\,‰) = {s['m']:.1f}\ {GEQ_S}"
                 rf"\ m_{{ser}} = {p['m_ser']:.0f}\ \mathrm{{kNm/m}}")
        (st.success if ok_sls else st.error)(
            "Aptitude au service vérifiée." if ok_sls else "Aptitude au service NON vérifiée.")
        fig, ax = plt.subplots(figsize=(5.5, 3.2))
        xs = np.linspace(20, p["h_c"] - 1, 200)
        ax.plot(xs, [r["f_res"](xx, p["d_sc_ser_corrige"]) for xx in xs], color=core.C_TENS)
        ax.axhline(0, color="k", lw=0.6)
        ax.plot(s["x"], 0, "o", color=core.C_NA)
        ax.set_xlabel("x [mm]")
        ax.set_ylabel("ΣF [kN/m]")
        ax.set_title("Équilibre en fonction de l'axe neutre")
        fig.tight_layout()
        st.pyplot(fig, width="stretch")
        plt.close(fig)

# ----------------------------------------------------------------------------
with tab3:
    PARAMS = {
        "h_U – épaisseur BFUP [mm]": ("h_U", 10.0, 100.0),
        "f_Utk – traction BFUP [MPa]": ("f_Utk", 0.0, 16.0),
        "s_U – espacement A_s,U [mm]": ("s_sU", 30.0, 200.0),
        "Ø A_s,U [mm]": ("phi_sU", 6.0, 20.0),
        "f_ck – béton existant [MPa]": ("f_ck", 15.0, 60.0),
        "h_c – dalle existante [mm]": ("h_c", 120.0, 300.0),
    }
    a, b = st.columns([1, 2])
    with a:
        lab = st.selectbox("Paramètre", list(PARAMS))
        key, lo, hi = PARAMS[lab]
        rng = st.slider("Plage", lo, hi, (lo, hi))
    vals = np.linspace(rng[0], rng[1], 31)
    out = []
    for v in vals:
        q = dict(p)
        q[key] = v
        if key == "h_c":
            q["d_sc"] = v
            if not corr:
                q["d_sc_ser_corrige"] = v
        try:
            rr = core.ex1_compute(q)
            ss = rr["sls_c"] if corr else rr["sls"]
            out.append((v, rr["mR1"], rr["mRd"], ss["m"], rr["x"], rr["eps_c"]))
        except ValueError:
            out.append((v, np.nan, np.nan, np.nan, np.nan, np.nan))
    o = np.array(out, dtype=float)
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.plot(o[:, 0], o[:, 1], color=core.C_TENS, label="m_R,1 (caract.)")
    ax.plot(o[:, 0], o[:, 2], color=core.C_TENS, ls="--", label="m_Rd = m_R,1/γ_M")
    ax.plot(o[:, 0], o[:, 3], color="0.35", label=f"m(ε_U = {p['eps_U_ser']:g}‰) – ELS")
    ax.axhline(p["M_d"], color=core.C_COMP, lw=0.9, label="M_d")
    ax.axhline(p["m_ser"], color=core.C_COMP, lw=0.9, ls=":", label="m_ser")
    ax.axvline(p[key], color="0.6", ls=":", lw=0.9)
    ax.set_xlabel(lab)
    ax.set_ylabel("m [kNm/m]")
    ax.legend(frameon=False, fontsize=8, ncol=3)
    fig.tight_layout()
    with b:
        st.pyplot(fig, width="stretch")
    plt.close(fig)
    bad = o[np.abs(o[:, 5]) > p["eps_cu"], 0]
    if bad.size:
        st.info(f"|ε_c| > ε_cu pour {lab.split(' ')[0]} ∈ [{bad.min():.1f} ; {bad.max():.1f}] : "
                "le calcul plastique surestime alors la résistance.")
    st.download_button("Télécharger les résultats (CSV)",
                       pd.DataFrame(o, columns=[key, "mR1", "mRd", "m_ELS", "x_ELU", "eps_c"]).to_csv(index=False),
                       file_name=f"ex1_parametrique_{key}.csv", mime="text/csv")

# ----------------------------------------------------------------------------
with tab4:
    st.markdown(f"""
**Modèle (calcul plastique, ELU)**
- Tous les éléments tendus (BFUP, A_s,U, A_s,ct) sont plastifiés ; le BFUP travaille à f_Utk sur toute son épaisseur.
- Béton comprimé : bloc rectangulaire f_ck sur 0.85·x ; résistance du béton en traction négligée.
- Moments calculés par rapport à la fibre inférieure ; le BFUP et A_s,U agissent à mi-hauteur de la couche.
- Contrôle : ε_c à la fibre inférieure pour ε_U = {p['eps_U_uls']:g}‰ imposé à la fibre supérieure.

**Modèle (ELS)**
- ε_U,ser imposé à la fibre supérieure ; BFUP bilinéaire (E_U puis palier f_Utk), aciers élastiques-plastiques,
  béton linéaire (E_c) ; axe neutre obtenu par itération sur ΣF = 0.

**Écarts relevés dans le corrigé du cours**
- Point 3 : le corrigé divise par 1.30 (→ 208.8 kNm/m) alors que l'énoncé donne γ_M = 1.20 (→ 226.4 kNm/m).
- « Presque 70 % » compare m_Rd(γ = 1.30) à m_R,0 ; en valeurs caractéristiques, le gain est de +120 %.
- Tableau ELS : A_s,ct placé à d = 171 mm au lieu de 180 mm. Avec d = 180 mm : x = 81.3 mm, m = 139.2 kNm/m
  (corrigé : 80.5 mm, 134 kNm/m). La case « Reproduire le tableau ELS du corrigé » applique d = 171 mm.
""")
