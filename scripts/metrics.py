from __future__ import annotations

import numpy as np
import pandas as pd


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) == 0:
        return float("nan")
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) == 0:
        return float("nan")
    return float(np.mean(np.abs(y_true - y_pred)))


def mbe(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) == 0:
        return float("nan")
    return float(np.mean(y_pred - y_true))


def pearson_r(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) < 2:
        return float("nan")
    if np.std(y_true, ddof=1) == 0 or np.std(y_pred, ddof=1) == 0:
        return float("nan")
    corr = np.corrcoef(y_true, y_pred)[0, 1]
    if not np.isfinite(corr):
        return float("nan")
    return float(corr)


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    corr = pearson_r(y_true, y_pred)
    if not np.isfinite(corr):
        return float("nan")
    return float(corr**2)


def willmott_d(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    if len(y_true) == 0:
        return float("nan")
    y_mean = np.mean(y_true)
    denom = np.sum((np.abs(y_pred - y_mean) + np.abs(y_true - y_mean)) ** 2)
    if denom == 0:
        return float("nan")
    return float(1 - np.sum((y_pred - y_true) ** 2) / denom)


def confidence_c(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    r = pearson_r(y_true, y_pred)
    d = willmott_d(y_true, y_pred)
    if not np.isfinite(r) or not np.isfinite(d):
        return float("nan")
    return float(r * d)


def classify_confidence(c: float) -> str:
    if not np.isfinite(c):
        return ""
    if c > 0.85:
        return "Excellent"
    if c > 0.75:
        return "Very Good"
    if c > 0.65:
        return "Good"
    if c > 0.60:
        return "Average"
    if c > 0.50:
        return "Poor"
    if c > 0.40:
        return "Bad"
    return "Very Poor"


def compute_metrics(df: pd.DataFrame, ref_col: str, method_cols: list[str]) -> pd.DataFrame:
    rows = []

    for col in method_cols:
        ref = df[ref_col].to_numpy()
        series = df[col].to_numpy()
        mask = np.isfinite(ref) & np.isfinite(series)
        ref = ref[mask]
        series = series[mask]
        c = confidence_c(ref, series)
        rows.append(
            {
                "method": col,
                "rmse": rmse(ref, series),
                "mae": mae(ref, series),
                "mbe": mbe(ref, series),
                "r": pearson_r(ref, series),
                "r2": r2_score(ref, series),
                "willmott_d": willmott_d(ref, series),
                "c": c,
                "classification": classify_confidence(c),
            }
        )

    return pd.DataFrame(rows)
