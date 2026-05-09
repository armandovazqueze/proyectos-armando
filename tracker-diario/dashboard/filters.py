from datetime import date

import pandas as pd


def apply_date_filter(df: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    if df.empty or "checkin_date" not in df.columns:
        return df
    mask = (df["checkin_date"].dt.date >= start) & (df["checkin_date"].dt.date <= end)
    return df[mask].copy()


def apply_meaningfulness_filter(df: pd.DataFrame, levels: list[int]) -> pd.DataFrame:
    if df.empty or not levels or "meaningfulness_level" not in df.columns:
        return df
    return df[df["meaningfulness_level"].isin(levels)].copy()


def apply_activity_filter(df: pd.DataFrame, activity: str) -> pd.DataFrame:
    """Keep rows where the 'activities' column contains the given name."""
    if df.empty or not activity or "activities" not in df.columns:
        return df
    mask = df["activities"].str.contains(activity, na=False, regex=False)
    return df[mask].copy()
