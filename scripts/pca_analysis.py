from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

matplotlib.use("Agg")
import matplotlib.pyplot as plt

PCA_CANDIDATE_COLUMNS: tuple[str, ...] = (
    "tmed_c",
    "tmax_c",
    "tmin_c",
    "rh_mean_pct",
    "wind_mean_ms",
    "rad_global_mj_m2_d",
    "rad_net_mj_m2_d",
)


@dataclass(frozen=True)
class PCAResult:
    label: str
    features: list[str]
    prepared: pd.DataFrame
    scaled: np.ndarray
    scores: np.ndarray
    loadings: pd.DataFrame
    explained_variance: pd.DataFrame


def slugify_label(label: str) -> str:
    normalized = unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower().strip()
    normalized = re.sub(r"[^a-z0-9]+", "_", normalized)
    return normalized.strip("_") or "pca"


def select_pca_columns(df: pd.DataFrame) -> list[str]:
    return [column for column in PCA_CANDIDATE_COLUMNS if column in df.columns]


def prepare_pca_data(df: pd.DataFrame, columns: list[str] | None = None) -> tuple[pd.DataFrame, list[str]]:
    selected_columns = columns if columns is not None else select_pca_columns(df)
    if len(selected_columns) < 2:
        raise ValueError(
            "PCA requires at least two meteorological variables. "
            f"Available columns: {', '.join(selected_columns) if selected_columns else 'none'}"
        )

    prepared = df.loc[:, selected_columns].apply(pd.to_numeric, errors="coerce").dropna(axis=0, how="any")
    if len(prepared) < 2:
        raise ValueError(
            "PCA requires at least two complete rows after removing missing values. "
            f"Found {len(prepared)} complete rows for columns: {', '.join(selected_columns)}"
        )

    return prepared, selected_columns


def _build_loadings(pca: PCA, features: list[str]) -> pd.DataFrame:
    component_names = [f"PC{i}" for i in range(1, pca.n_components_ + 1)]
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
    return pd.DataFrame(loadings, index=features, columns=component_names).reset_index(names="variable")


def _build_explained_variance(pca: PCA) -> pd.DataFrame:
    component_names = [f"PC{i}" for i in range(1, pca.n_components_ + 1)]
    explained = pd.DataFrame(
        {
            "component": component_names,
            "explained_variance": pca.explained_variance_,
            "explained_variance_ratio": pca.explained_variance_ratio_,
        }
    )
    explained["cumulative_explained_variance_ratio"] = explained["explained_variance_ratio"].cumsum()
    return explained


def fit_pca(df: pd.DataFrame, label: str) -> PCAResult:
    prepared, features = prepare_pca_data(df)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(prepared)
    n_components = min(2, scaled.shape[0], scaled.shape[1])
    if n_components < 2:
        raise ValueError(
            "PCA biplot requires at least two components after preprocessing. "
            f"Found {scaled.shape[0]} rows and {scaled.shape[1]} features for {label}."
        )

    pca = PCA(n_components=n_components)
    scores = pca.fit_transform(scaled)
    loadings = _build_loadings(pca, features)
    explained_variance = _build_explained_variance(pca)
    return PCAResult(
        label=label,
        features=features,
        prepared=prepared,
        scaled=scaled,
        scores=scores,
        loadings=loadings,
        explained_variance=explained_variance,
    )


def _arrow_scale(scores: np.ndarray, loadings: pd.DataFrame) -> float:
    score_ranges = np.ptp(scores[:, :2], axis=0)
    score_ranges = np.where(score_ranges == 0, 1.0, score_ranges)
    loading_values = loadings.loc[:, ["PC1", "PC2"]].to_numpy()
    max_loading = np.nanmax(np.abs(loading_values))
    if not np.isfinite(max_loading) or max_loading == 0:
        return 1.0
    return 0.45 * float(np.min(score_ranges) / max_loading)


def plot_pca_biplot(result: PCAResult, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    scores = result.scores
    loadings = result.loadings
    explained = result.explained_variance
    scale = _arrow_scale(scores, loadings)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(scores[:, 0], scores[:, 1], s=18, alpha=0.55, color="#2a6f97")
    ax.axhline(0, color="0.7", linewidth=0.8)
    ax.axvline(0, color="0.7", linewidth=0.8)

    for row in loadings.itertuples(index=False):
        x = float(row.PC1) * scale
        y = float(row.PC2) * scale
        ax.arrow(0, 0, x, y, color="#bc4749", alpha=0.85, width=0.0, head_width=0.04, length_includes_head=True)
        ax.text(x * 1.08, y * 1.08, row.variable, color="#8b1e3f", fontsize=9, ha="center", va="center")

    pc1_ratio = explained.loc[explained["component"] == "PC1", "explained_variance_ratio"].iloc[0]
    pc2_ratio = explained.loc[explained["component"] == "PC2", "explained_variance_ratio"].iloc[0]
    ax.set_xlabel(f"PC1 ({pc1_ratio:.1%} of variance)")
    ax.set_ylabel(f"PC2 ({pc2_ratio:.1%} of variance)")
    ax.set_title(f"PCA biplot - {result.label}")
    ax.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close(fig)


def run_pca(df: pd.DataFrame, label: str) -> PCAResult:
    return fit_pca(df, label)


def write_pca_outputs(result: PCAResult, tables_dir: Path, figures_dir: Path) -> None:
    tables_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    slug = slugify_label(result.label)
    result.loadings.to_csv(tables_dir / f"{slug}_pca_loadings.csv", index=False)
    result.explained_variance.to_csv(tables_dir / f"{slug}_pca_explained_variance.csv", index=False)
    plot_pca_biplot(result, figures_dir / slug / f"{slug}_pca_biplot.png")
