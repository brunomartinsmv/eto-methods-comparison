from __future__ import annotations

import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PALETTE = {
    "blue": "#0F4D92",
    "blue_light": "#3775BA",
    "green": "#8BCF8B",
    "red": "#B64342",
    "teal": "#42949E",
    "violet": "#9A4D8E",
    "gray": "#767676",
    "gray_light": "#CFCECE",
    "ink": "#272727",
    "paper": "#F7F8FA",
}

METHOD_LABELS = {
    "et_camargo": "Camargo",
    "et_hargreaves_samani": "Hargreaves–Samani",
    "et_hargreaves_samani_corr": "Hargreaves–Samani corrected",
    "et_priestley_taylor": "Priestley–Taylor",
    "et_penman_monteith": "Penman–Monteith",
    "et_garcia_lopez": "Garcia–Lopez",
    "et_makkink": "Makkink",
    "et_mccloud": "McCloud",
    "et_turc": "Turc",
    "et_global_radiation": "Global radiation",
    "et_ivanov": "Ivanov",
    "et_jensen_heise": "Jensen–Heise",
    "et_net_radiation": "Net radiation",
    "et_radiation_temperature": "Radiation–temperature",
    "et_lungeon": "Lungeon",
    "et_stephens_stewart": "Stephens–Stewart",
    "et_hicks_hess": "Hicks–Hess",
    "et_thornthwaite": "Thornthwaite",
    "et_thornthwaite_camargo": "Thornthwaite–Camargo",
}


def apply_figure_style(*, font_size: float = 10.5, axes_linewidth: float = 0.8) -> None:
    plt.rcParams.update(
        {
            "font.family": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "font.size": font_size,
            "axes.titlesize": font_size + 1,
            "axes.labelsize": font_size,
            "xtick.labelsize": font_size - 1,
            "ytick.labelsize": font_size - 1,
            "axes.linewidth": axes_linewidth,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.labelcolor": PALETTE["ink"],
            "text.color": PALETTE["ink"],
            "xtick.color": PALETTE["gray"],
            "ytick.color": PALETTE["gray"],
            "legend.frameon": False,
            "savefig.facecolor": "white",
            "figure.facecolor": "white",
            "svg.fonttype": "none",
            "svg.hashsalt": "eto-methods-comparison",
        }
    )


def method_label(value: str) -> str:
    if value in METHOD_LABELS:
        return METHOD_LABELS[value]
    value = re.sub(r"^et_", "", value)
    return value.replace("_", " ").title()


def style_axis(ax: plt.Axes) -> None:
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=PALETTE["gray_light"], linewidth=0.6, alpha=0.55)
    ax.tick_params(length=3, width=0.7)
