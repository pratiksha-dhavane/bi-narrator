import numpy as np
import pandas as pd
from typing import Optional, Dict, Any

def prepare_dataframe(data: pd.DataFrame, 
                      date_col: str, 
                      metric_col: str, 
                      category_col: Optional[str] = None) -> pd.DataFrame:
    """
    Returns a cleaned df with standardized column names:
    - 'date'
    - 'metric'
    - optional 'category'
    Rows with invalid date or metric are dropped.
    """

    col_list = [date_col, metric_col] + ([category_col] if category_col else [])
    df = data[col_list].copy()

    df["date"] = pd.to_datetime(df[date_col], errors="coerce")
    df["metric"] = pd.to_numeric(df[metric_col], errors="coerce")

    if category_col:
        df['category'] = df[category_col].astype(str)

    df = df.dropna(subset=[date_col, metric_col])

    keep_cols = ["date", "metric"] + (["category"] if category_col else [])

    return df[keep_cols]

def aggregate_over_time(data: pd.DataFrame,
                        freq='ME'       # "D", "W", "M", "Q"
                        ) -> pd.DataFrame:
    """
    Aggregates metric over time at given frequency.
    Returns a df with: date, metric_sum, metric_mean, n_records
    """

    if data.empty:
        return pd.DataFrame(columns=["date", "metric_sum", "metric_mean", "n_records"])
    
    grouped_df = ( 
        data
        .groupby(pd.Grouper(key="date",freq=freq))["metric"]
        .agg(["sum","mean","count"])
        .reset_index()
        .rename(columns={
            "sum" : "metric_sum",
            "mean" : "metric_mean",
            "count" : "n_records"
        }) 
                  )
    
    grouped_df = grouped_df.dropna(subset=["date"])
    return grouped_df

def compute_kpis_and_peaks(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes high-level KPIs and peak/trough periods.
    Returns dict with 'kpis' and 'peaks'.
    """

    if data.empty:
        return {
            "kpis": {
                "total_metric": 0.0,
                "overall_growth_pct": None,
                "trend_direction": "flat",
                "num_periods": 0,
                "volatility_score": None,
            },
            "peaks": {
                "max_period": None,
                "min_period": None,
            },
        }
    
    total_metric = float(data["metric_sum"].sum())
    num_periods = int(len(data))

    # overall growth from first to last period
    first = data["metric_sum"].iloc[0]
    last = data["metric_sum"].iloc[-1]
    
    if first == 0 or num_periods < 2:
        overall_growth_pct = None

    else:
        overall_growth_pct = (last - first) / abs(first)

    # Trend direction with small tolerance band
    trend_direction = "flat"
    if overall_growth_pct is not None:
        if overall_growth_pct > 0.05:
            trend_direction = "up"
        elif overall_growth_pct < -0.05:
            trend_direction = "down"

    # Volatility: std dev of period-over-period % change
    metric_series = data['metric_sum'].astype(float)
    pct_changes = metric_series.pct_change().dropna()
    volatility_score = float(pct_changes.std()) if len(pct_changes) > 0 else None

    # Peaks
    max_idx = metric_series.idxmax()
    min_idx = metric_series.idxmin()

    max_row = data.loc[max_idx]
    min_row = data.loc[min_idx]

    peaks = {
        "max_period" : {
            "period_end" : max_row["date"].date().isoformat(),
            "metric_sum" : float(max_row["metric_sum"]),
        },
        "min_period" : {
            "period_end" : min_row["date"].date().isoformat(),
            "metric_sum" : float(min_row["metric_sum"]),
        }
    }

    kpis = {
        "total_metric": total_metric,
        "overall_growth_pct": overall_growth_pct,
        "trend_direction": trend_direction,
        "num_periods": num_periods,
        "volatility_score": volatility_score,
    }

    return {"kpis": kpis, "peaks": peaks}

def compute_contributions(
        data : pd.DataFrame,
        total_metric : float,
        top_n : int = 5,
        bottom_n : int = 3,
) -> Dict[str, Any]:
    """
    Computes top and bottom categories by metric_sum.
    Expects df to have 'category' column.
    """

    if "category" not in data.columns or total_metric == 0 or data.empty:
        return {
            "available": False,
            "top_contributors": [],
            "bottom_draggers": [],
        }
    
    agg = (
        data.groupby("category")["metric"]
        .sum()
        .reset_index()
        .rename(columns={"metric": "metric_sum"})
    )

    agg["metric_share_pct"] = ( agg["metric_sum"] / total_metric ) * 100

    agg_sorted = agg.sort_values("metric_sum", ascending=False)

    top = agg_sorted.head(top_n).copy()
    top["rank"] = range(1, len(top) + 1)

    bottom = agg_sorted.sort_values("metric_sum", ascending=True).head(bottom_n).copy()
    bottom["rank"] = range(1, len(bottom) + 1)

    def to_records(df_part):
        return [
            {
                "category" : row["category"],
                "metric_sum" : float(row["metric_sum"]),
                "metric_share_pct" : float(row["metric_share_pct"]),
                "rank" : int(row["rank"])
            }
        for _, row in df_part.iterrows()
        ]
    
    return {
        "available": True,
        "top_contributors": to_records(top),
        "bottom_draggers": to_records(bottom),        
    }

def run_analytics(
        data : pd.DataFrame,
        date_col : str,
        metric_col : str,
        category_col : Optional[str] = None,
        freq : str = "ME"
) -> Dict[str, Any]:
    """
    Full analytics pipeline:
    - clean + standardize
    - aggregate over time
    - compute KPIs + peaks
    - compute contributions
    - assemble analytics_result dict
    """

    # 1. Prepare DF
    df_clean = prepare_dataframe(data, date_col, metric_col, category_col)

    if df_clean.empty:
        raise ValueError("No valid rows after cleaning (date/metric parsing failed).")

    # 2. time aggregation
    time_agg = aggregate_over_time(df_clean)  

    # # 3. Global metric description
    # metric_describe = compute_metric_describe(df_clean)

    # 4. KPIs + Peaks
    kpi_peaks = compute_kpis_and_peaks(time_agg)
    kpis = kpi_peaks["kpis"]
    peaks = kpi_peaks["peaks"]

    # 5. Contributions
    contributions = compute_contributions(df_clean, total_metric=kpis["total_metric"])

    # 6. Meta
    meta = {
        "n_rows": int(len(df_clean)),
        "n_columns": int(data.shape[1]),
        "metric_col": metric_col,
        "date_col": date_col,
        "category_col": category_col,
        "freq": freq,
        "date_min": df_clean["date"].min().date().isoformat(),
        "date_max": df_clean["date"].max().date().isoformat(),
    }

    # 7. Time series as records (JSON-serializable)
    time_series_records = [
        {
            "period_end": row["date"].date().isoformat(),
            "metric_sum": float(row["metric_sum"]),
            "metric_mean": float(row["metric_mean"]),
            "n_records": int(row["n_records"]),
        }
        for _, row in time_agg.iterrows()
    ]

    analytics_result = {
        "meta": meta,
        "kpis": kpis,
        # "metric_describe": metric_describe,
        "time_series": time_series_records,
        "peaks": peaks,
        "contributions": contributions,
    }

    return analytics_result