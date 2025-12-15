from typing import Optional, Dict, Any

def format_prompt_from_template(input : Dict[str, Any])-> str:
    """
    This function prepares the prompt for BI Narrator LLM based on the analytics results. 
    """
    system_prompt = input["prompt_input"]["system_prompt"]
    audience = input["prompt_input"]["audience"]
    tone = input["prompt_input"]["tone"]
    analytics_result = input["analytics_result"]

    meta = analytics_result["meta"]
    kpis = analytics_result["kpis"]
    peaks = analytics_result["peaks"]
    contrib = analytics_result["contributions"]
    # describe = analytics_result["metric_describe"]
    time_series = analytics_result["time_series"]

    # Safety formatters

    def fmt_pct(x):
        return "N/A" if x is None else f"{x * 100:.2f}%"
    
    def fmt_float(x):
        return "N/A" if x is None else f"{x:.2f}"
    
    # # Distribution block 
    # if describe:
    #     distribution_summary = (
    #         f"Count: {int(describe['count'])}\n"
    #         f"Mean: {describe['mean']:.2f}\n"
    #         f"Median: {describe['median']:.2f}\n"
    #         f"Std Dev: {describe['std']:.2f}\n"
    #         f"Min: {describe['min']:.2f}\n"
    #         f"25th Percentile: {describe['p25']:.2f}\n"
    #         f"75th Percentile: {describe['p75']:.2f}\n"
    #         f"Max: {describe['max']:.2f}"
    #     )
    # else:
    #     distribution_summary = "No distribution statistics available."

    # time series block
    ts_sample = time_series[-12:] if len(time_series) > 12 else time_series

    ts_lines = {
        f"{row.get('period_end')} | "
        f"sum={row['metric_sum']:.2f}, mean={row['metric_mean']:.2f}, n={row['n_records']}"
        for row in ts_sample
    }

    time_series_block = "\n".join(ts_lines) if ts_lines else "No time series data."

    # Contribution Block

    if contrib["available"]:
        top = "\n".join(
            [f"#{c['rank']} {c['category']} → {c['metric_sum']:.2f} ({c['metric_share_pct']:.1f}%)"
             for c in contrib["top_contributors"]]
        )
        bottom = "\n".join(
            [f"#{c['rank']} {c['category']} → {c['metric_sum']:.2f} ({c['metric_share_pct']:.1f}%)"
             for c in contrib["bottom_draggers"]]
        )
        contribution_block = f"Top Contributors:\n{top}\n\nBottom Draggers:\n{bottom}"
    else:
        contribution_block = "No category breakdown available."

    # Peaks

    max_period = peaks["max_period"]
    min_period = peaks["min_period"]

    max_period_txt = f"{max_period['period_end']} → {max_period['metric_sum']:.2f}" if max_period else "N/A"
    min_period_txt = f"{min_period['period_end']} → {min_period['metric_sum']:.2f}" if min_period else "N/A"

    # Final output format
    return system_prompt.format(
        metric_name=meta["metric_col"],
        audience=audience,
        tone=tone,
        date_col=meta["date_col"],
        category_col=meta["category_col"] or "None",
        freq=meta["freq"],
        date_range=f"{meta['date_min']} to {meta['date_max']}",
        num_periods=kpis["num_periods"],
        total_metric=fmt_float(kpis["total_metric"]),
        overall_growth_pct=fmt_pct(kpis["overall_growth_pct"]),
        trend_direction=kpis["trend_direction"],
        volatility_score=fmt_float(kpis["volatility_score"]),
        # distribution_summary=distribution_summary,
        time_series_block=time_series_block,
        contribution_block=contribution_block,
        max_period=max_period_txt,
        min_period=min_period_txt,
    )