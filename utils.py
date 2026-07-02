"""
utils.py
Core pandas / data-analysis functions for the AI Excel Assistant.
Kept separate from app.py so the logic is easy to unit-test and reuse.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression


# ---------------------------------------------------------------------------
# 1. DUPLICATES
# ---------------------------------------------------------------------------
def find_duplicates(df: pd.DataFrame, subset_cols=None):
    """
    Returns a DataFrame of duplicate rows.
    If subset_cols is None, checks duplicates across all columns.
    """
    subset_cols = subset_cols if subset_cols else None
    dup_mask = df.duplicated(subset=subset_cols, keep=False)
    duplicates = df[dup_mask].sort_values(by=subset_cols if subset_cols else df.columns.tolist())
    return duplicates


# ---------------------------------------------------------------------------
# 2. MISSING VALUES
# ---------------------------------------------------------------------------
def missing_value_report(df: pd.DataFrame):
    """
    Returns a summary DataFrame: column, missing count, missing %.
    """
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df) * 100).round(2)
    report = pd.DataFrame({
        "Column": df.columns,
        "Missing Values": missing_count.values,
        "Missing %": missing_pct.values,
        "Data Type": df.dtypes.astype(str).values
    })
    report = report[report["Missing Values"] > 0].sort_values("Missing Values", ascending=False)
    return report.reset_index(drop=True)


# ---------------------------------------------------------------------------
# 3. PIVOT TABLE
# ---------------------------------------------------------------------------
def generate_pivot(df: pd.DataFrame, index_col, columns_col, values_col, aggfunc="sum"):
    """
    Wraps pandas.pivot_table with sensible error handling.
    """
    pivot = pd.pivot_table(
        df,
        index=index_col,
        columns=columns_col if columns_col else None,
        values=values_col,
        aggfunc=aggfunc,
        fill_value=0
    )
    return pivot


# ---------------------------------------------------------------------------
# 4. CHARTS
# ---------------------------------------------------------------------------
def create_chart(df: pd.DataFrame, chart_type: str, x_col: str, y_col: str, color_col=None):
    """
    Returns a plotly figure object based on chart_type.
    """
    chart_type = chart_type.lower()
    if chart_type == "bar":
        fig = px.bar(df, x=x_col, y=y_col, color=color_col, template="plotly_white")
    elif chart_type == "line":
        fig = px.line(df, x=x_col, y=y_col, color=color_col, template="plotly_white")
    elif chart_type == "scatter":
        fig = px.scatter(df, x=x_col, y=y_col, color=color_col, template="plotly_white")
    elif chart_type == "pie":
        fig = px.pie(df, names=x_col, values=y_col, template="plotly_white")
    elif chart_type == "histogram":
        fig = px.histogram(df, x=x_col, template="plotly_white")
    else:
        fig = px.bar(df, x=x_col, y=y_col, template="plotly_white")

    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=13),
    )
    return fig


# ---------------------------------------------------------------------------
# 5. SALES PREDICTION (simple linear regression forecast)
# ---------------------------------------------------------------------------
def predict_sales(df: pd.DataFrame, date_col: str, sales_col: str, periods: int = 30):
    """
    Fits a simple linear regression on time (ordinal day number) vs sales
    and forecasts `periods` future days. Good enough for a portfolio demo
    (not meant to be production-grade forecasting).
    Returns: history_df, forecast_df, plotly figure
    """
    work = df[[date_col, sales_col]].dropna().copy()
    work[date_col] = pd.to_datetime(work[date_col])
    work = work.sort_values(date_col)

    # Aggregate multiple rows per day if needed
    work = work.groupby(date_col, as_index=False)[sales_col].sum()

    work["day_num"] = (work[date_col] - work[date_col].min()).dt.days
    X = work[["day_num"]].values
    y = work[sales_col].values

    model = LinearRegression()
    model.fit(X, y)

    last_day = work["day_num"].max()
    future_days = np.arange(last_day + 1, last_day + periods + 1).reshape(-1, 1)
    future_preds = model.predict(future_days)
    future_preds = np.maximum(future_preds, 0)  # sales can't be negative

    future_dates = [work[date_col].max() + pd.Timedelta(days=int(d - last_day)) for d in future_days.flatten()]
    forecast_df = pd.DataFrame({date_col: future_dates, sales_col: future_preds, "Type": "Forecast"})
    history_df = work[[date_col, sales_col]].copy()
    history_df["Type"] = "Actual"

    combined = pd.concat([history_df, forecast_df], ignore_index=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history_df[date_col], y=history_df[sales_col],
        mode="lines+markers", name="Actual Sales", line=dict(color="#4F8BF9")
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df[date_col], y=forecast_df[sales_col],
        mode="lines+markers", name="Forecasted Sales",
        line=dict(color="#FF6B6B", dash="dash")
    ))
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    r2 = model.score(X, y)
    return history_df, forecast_df, fig, r2


# ---------------------------------------------------------------------------
# 6. QUICK DATA PROFILE (used to give the LLM context about the sheet)
# ---------------------------------------------------------------------------
def profile_dataframe(df: pd.DataFrame, max_cols=25):
    cols = df.columns.tolist()[:max_cols]
    profile = {
        "n_rows": len(df),
        "n_cols": len(df.columns),
        "columns": cols,
        "dtypes": {c: str(df[c].dtype) for c in cols},
        "sample_rows": df.head(3).to_dict(orient="records"),
    }
    return profile
