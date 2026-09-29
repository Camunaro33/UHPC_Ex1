# -*- coding: utf-8 -*-
"""
bfup_ex1.py – noyau de calcul et de tracé de l'exemple 1 (§8)
Élément composé BFUP armé – béton armé : résistance à la flexion (ELU) et aptitude au service (ELS).

Cours « Structures existantes – Examen et interventions (bases) », Applications p. 38-40.
Unités internes : N, mm, MPa.
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
from matplotlib.gridspec import GridSpec

B = 1000.0  # largeur de référence [mm] (calculs par mètre)

plt.rcParams.update({
    "font.size": 9, "axes.titlesize": 10, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False,
})

C_CONC, C_UHPC, C_STEEL, C_COMP, C_TENS, C_NA = "0.85", "0.55", "k", "#b2182b", "#2166ac", "#d6604d"


# ----------------------------------------------------------------------------
# Utilitaires
# ----------------------------------------------------------------------------
def bar_area(phi, s):
    """Aire d'armature par mètre [mm²/m] pour Ø phi [mm] tous les s [mm]."""
    return np.pi * phi**2 / 4.0 * B / s


def trap(f, y):
    return float(np.sum(0.5 * (f[1:] + f[:-1]) * np.diff(y)))


def bisect(f, a, b, tol=1e-7, nmax=300):
    fa, fb = f(a), f(b)
    if fa * fb > 0:
        raise ValueError("Pas de changement de signe dans l'intervalle")
    for _ in range(nmax):
        m = 0.5 * (a + b)
        fm = f(m)
        if abs(b - a) < tol:
            break
        if fa * fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return 0.5 * (a + b)


def input_box(ax, items, title="Données d'entrée"):
    ax.axis("off")
    ax.set_title(title, loc="left")
    txt = "\n".join(f"{k:<14s} {v}" for k, v in items)
    ax.text(0.0, 0.98, txt, va="top", ha="left", family="monospace",
            fontsize=7.8, transform=ax.transAxes)


def table(ax, cols, rows, title, summary=None):
    ax.axis("off")
    ax.set_title(title, loc="left")
    t = ax.table(cellText=rows, colLabels=cols, loc="upper center",
                 cellLoc="center", bbox=[0, 0.38 if summary else 0.0, 1, 0.62 if summary else 1])
    t.auto_set_font_size(False)
    t.set_fontsize(7.8)
    for (r, c), cell in t.get_celld().items():
        cell.set_linewidth(0.4)
        if r == 0:
            cell.set_text_props(weight="bold")
            cell.set_facecolor("0.93")
    if summary:
        ax.text(0.0, 0.33, "\n".join(summary), va="top", ha="left", fontsize=8,
                family="monospace", transform=ax.transAxes)


def draw_layered_section(ax, h_c, h_U, bars, x_na=None, title="Section (b = 1 m)"):
    w = 1.0
    ax.add_patch(Rectangle((0, 0), w, h_c, fc=C_CONC, ec="k", hatch="///", lw=0.8))
    ax.add_patch(Rectangle((0, h_c), w, h_U, fc=C_UHPC, ec="k", lw=0.8))
    ax.text(w / 2, h_c + h_U / 2, "BFUP armé", ha="center", va="center", fontsize=8,
            color="w", weight="bold", bbox=dict(fc=C_UHPC, ec="none", pad=0.5))
    ax.text(w / 2, h_c * 0.12, "béton armé", ha="center", fontsize=8,
            bbox=dict(fc=C_CONC, ec="none", pad=0.5))
    for y, lab in bars:
        xs = np.linspace(0.08, 0.92, 7) * w
        ax.plot(xs, [y] * len(xs), "o", color=C_STEEL, ms=3.5)
        ax.text(w + 0.04, y, lab, va="center", fontsize=7.5)
    # cotes
    ax.annotate("", (-0.12, 0), (-0.12, h_c), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(-0.15, h_c / 2, f"h_c={h_c:.0f}", rotation=90, ha="right", va="center", fontsize=7.5)
    ax.annotate("", (-0.12, h_c), (-0.12, h_c + h_U), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(-0.15, h_c + h_U / 2, f"h_U={h_U:.0f}", rotation=90, ha="right", va="center", fontsize=7.5)
    if x_na is not None:
        ax.axhline(x_na, color=C_NA, ls="--", lw=1)
        ax.text(w / 2, x_na + 3, f"axe neutre x = {x_na:.1f} mm", color=C_NA, ha="center", fontsize=7.5,
                bbox=dict(fc="w", ec="none", pad=0.5))
    ax.set_xlim(-0.45, w + 0.75)
    ax.set_ylim(-8, h_c + h_U + 12)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.set_ylabel("y depuis la fibre inférieure [mm]")
    ax.set_title(title)


def draw_strain(ax, y_ref, eps_ref, x, y_top, marks, title="Déformations"):
    """Profil linéaire : eps(y_ref) = eps_ref [‰], eps(x) = 0."""
    k = eps_ref / (y_ref - x)
    y = np.array([0.0, y_top])
    e = k * (y - x)
    ax.fill_betweenx([0, x], 0, [e[0], 0], color=C_COMP, alpha=0.25)
    ax.fill_betweenx([x, y_top], 0, [0, e[1]], color=C_TENS, alpha=0.25)
    ax.plot(e, y, "k", lw=1)
    ax.axvline(0, color="k", lw=0.6)
    ax.axhline(x, color=C_NA, ls="--", lw=1)
    for yy, lab in marks:
        ev = k * (yy - x)
        ax.plot(ev, yy, "o", color="k", ms=3)
        ax.text(ev, yy, f"  {lab} = {ev:.2f}‰", va="center",
                ha="left" if ev >= 0 else "right", fontsize=7.5)
    lim = 1.25 * max(abs(e).max(), 1e-9)
    ax.set_xlim(-lim * 1.6, lim * 1.9)
    ax.set_ylim(-8, y_top + 12)
    ax.set_xlabel("ε [‰]  (traction +)")
    ax.set_yticklabels([])
    ax.set_title(title)
    return k


def draw_stress(ax, continua, bar_notes, x, y_top, title="Contraintes (béton, BFUP)"):
    """continua : liste de (y_array, sigma_array, couleur, label)."""
    smax = 1.0
    for y, s, c, lab in continua:
        ax.fill_betweenx(y, 0, s, color=c, alpha=0.45, lw=0)
        ax.plot(s, y, color=c, lw=1)
        i = np.argmax(np.abs(s))
        ax.text(s[i], y[i], f" {lab}: {s[i]:.1f} MPa", fontsize=7.5, va="center",
                ha="left" if s[i] >= 0 else "right")
        smax = max(smax, np.abs(s).max())
    ax.axvline(0, color="k", lw=0.6)
    ax.axhline(x, color=C_NA, ls="--", lw=1)
    for yy, txt in bar_notes:
        ax.plot(0, yy, "o", color=C_STEEL, ms=3)
        ax.text(0.03 * smax, yy - 4, txt, fontsize=7, va="top")
    ax.set_xlim(-2.3 * smax, 2.3 * smax)
    ax.set_ylim(-8, y_top + 12)
    ax.set_xlabel("σ [MPa]")
    ax.set_yticklabels([])
    ax.set_title(title)


def draw_forces(ax, forces, y_top, unit="kN/m", title="Forces internes"):
    """forces : liste de (label, F, y). F>0 traction."""
    Fm = max(abs(F) for _, F, _ in forces)
    seen = {}
    for lab, F, y in forces:
        n = seen.get(round(y), 0)
        seen[round(y)] = n + 1
        c = C_TENS if F > 0 else C_COMP
        ax.annotate("", xy=(F, y), xytext=(0, y),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=1.8, shrinkA=0, shrinkB=0))
        ax.text(F, y + (9 * n if n else -9) if y > 100 else y, f" {lab} = {F:.1f}", color=c, fontsize=7.5,
                ha="left" if F > 0 else "right", va="bottom" if (n or y <= 100) else "top")
    ax.axvline(0, color="k", lw=0.6)
    ax.set_xlim(-1.9 * Fm, 1.9 * Fm)
    ax.set_ylim(-8, y_top + 12)
    ax.set_xlabel(f"F [{unit}]")
    ax.set_yticklabels([])
    ax.set_title(title)


def new_fig(title):
    fig = plt.figure(figsize=(17, 9.5))
    fig.suptitle(title, fontsize=12, weight="bold", x=0.01, ha="left")
    gs = GridSpec(2, 4, figure=fig, height_ratios=[1.15, 1], hspace=0.35, wspace=0.28,
                  left=0.05, right=0.98, top=0.91, bottom=0.05)
    return fig, gs


# ============================================================================
# EXEMPLE 1 – §8 : Élément composé BFUP armé – béton armé
# ============================================================================
def ex1_inputs():
    return dict(
        h_c=180.0, d_sc=180.0, phi_sc=18.0, s_sc=150.0, f_sk=450.0, f_ck=30.0,
        h_U=40.0, phi_sU=8.0, s_sU=50.0, f_Utk=10.0, f_sUk=500.0,
        eps_U_uls=5.0, eps_cu=3.5,                     # [‰] contrôle de la déformation du béton
        M_d=160.0, gamma_M=1.20,                       # [kNm/m], [-]
        m_ser=115.0, eps_U_ser=1.0,                    # [kNm/m], [‰] critère ELS (fibre sup. BFUP)
        E_U=50000.0, E_s=210000.0, E_c=35000.0,        # [MPa]
        d_sc_ser_corrige=171.0,                        # d_sc utilisé dans le tableau ELS du corrigé
    )


def ex1_sls_state(p, A_sU, A_sc, d_sc, x):
    """État de section à l'ELS pour eps_U,ser imposé à la fibre supérieure, axe neutre x."""
    h_top = p["h_c"] + p["h_U"]
    d_sU = p["h_c"] + p["h_U"] / 2
    k = p["eps_U_ser"] / 1000 / (h_top - x)
    eps = lambda y: k * (y - x)
    yU = np.linspace(p["h_c"], h_top, 401)
    sU = np.minimum(p["E_U"] * eps(yU), p["f_Utk"])          # BFUP bilinéaire (écrouissage ~ palier)
    F_U, M_U = trap(sU, yU) * B, trap(sU * yU, yU) * B
    s_sU = np.clip(p["E_s"] * eps(d_sU), -p["f_sUk"], p["f_sUk"])
    s_sc = np.clip(p["E_s"] * eps(d_sc), -p["f_sk"], p["f_sk"])
    s_cb = p["E_c"] * eps(0.0)                              # béton linéaire, traction négligée
    F_c = 0.5 * s_cb * x * B
    comp = [  # nom, eps[‰], sigma, F[kN/m], bras y[mm], m[kNm/m]
        ("BFUP", eps(h_top) * 1e3, float(sU.max()), F_U / 1e3, M_U / F_U, M_U / 1e6),
        ("A_s,U", eps(d_sU) * 1e3, s_sU, A_sU * s_sU / 1e3, d_sU, A_sU * s_sU * d_sU / 1e6),
        ("A_s,ct", eps(d_sc) * 1e3, s_sc, A_sc * s_sc / 1e3, d_sc, A_sc * s_sc * d_sc / 1e6),
        ("Béton", eps(0) * 1e3, s_cb, F_c / 1e3, x / 3, F_c * x / 3 / 1e6),
    ]
    sumF = sum(c[3] for c in comp)
    m = sum(c[5] for c in comp)
    return dict(comp=comp, sumF=sumF, m=m, x=x, eps_int=eps(p["h_c"]) * 1e3,
                eps=eps, sU=(yU, sU), s_cb=s_cb)


def ex1_compute(p=None):
    p = ex1_inputs() if p is None else {**ex1_inputs(), **p}
    A_sc = bar_area(p["phi_sc"], p["s_sc"])
    A_sU = bar_area(p["phi_sU"], p["s_sU"])
    h_top = p["h_c"] + p["h_U"]
    d_sU = d_U = p["h_c"] + p["h_U"] / 2

    # 1) Dalle en BA seule
    mR0 = 0.9 * p["d_sc"] * A_sc * p["f_sk"] / 1e6

    # 2) Calcul plastique de la section composée
    F_U = p["f_Utk"] * p["h_U"] * B / 1e3
    F_sU = A_sU * p["f_sUk"] / 1e3
    F_sc = A_sc * p["f_sk"] / 1e3
    F_c = F_U + F_sU + F_sc
    x = F_c * 1e3 / (0.85 * B * p["f_ck"])
    z_c = 0.85 * x / 2
    uls_rows = [
        ("BFUP", p["h_U"] * B, p["f_Utk"], F_U, d_U),
        ("A_s,U", A_sU, p["f_sUk"], F_sU, d_sU),
        ("A_s,ct", A_sc, p["f_sk"], F_sc, p["d_sc"]),
        ("Béton", 0.85 * x * B, -p["f_ck"], -F_c, z_c),
    ]
    mR1 = sum(F * d for *_, F, d in uls_rows) / 1e3
    eps_c = -p["eps_U_uls"] * x / (h_top - x)

    # 3) Sécurité structurale
    mRd = mR1 / p["gamma_M"]

    # 4) ELS – axe neutre par itération (équilibre), deux variantes
    f = lambda xx, d: ex1_sls_state(p, A_sU, A_sc, d, xx)["sumF"]
    x_ser = bisect(lambda xx: f(xx, p["d_sc"]), 20, p["h_c"] - 1)
    sls = ex1_sls_state(p, A_sU, A_sc, p["d_sc"], x_ser)
    x_ser_c = bisect(lambda xx: f(xx, p["d_sc_ser_corrige"]), 20, p["h_c"] - 1)
    sls_c = ex1_sls_state(p, A_sU, A_sc, p["d_sc_ser_corrige"], x_ser_c)

    return dict(p=p, A_sc=A_sc, A_sU=A_sU, d_sU=d_sU, mR0=mR0, uls_rows=uls_rows, F_c=F_c, x=x,
                mR1=mR1, eps_c=eps_c, mRd=mRd, sls=sls, sls_c=sls_c, f_res=f)


