import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.preprocessing import (
    standardize_date_column,
    resample_to_weekly,
    merge_dataframes_on_date,
    handle_missing_values,
    scale_features,
    preprocess_pipeline,
)


def test_standardize_date_column():
    df = pd.DataFrame({
        "date": ["2024-01-01", "2024-01-03", "2024-01-02"],
        "oil": [70, 72, 71]
    })

    result = standardize_date_column(df)

    assert pd.api.types.is_datetime64_any_dtype(result["date"])
    assert result.iloc[0]["date"] == pd.Timestamp("2024-01-01")
    assert len(result) == 3


def test_resample_to_weekly():
    df = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=10, freq="D"),
        "oil": [70, 71, 72, 73, 74, 75, 76, 77, 78, 79]
    })

    result = resample_to_weekly(df, method="mean")

    assert "date" in result.columns
    assert "oil" in result.columns
    assert len(result) >= 2


def test_merge_dataframes_on_date():
    df1 = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-07", "2024-01-14"]),
        "oil": [72, 75]
    })

    df2 = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-07", "2024-01-14"]),
        "freight": [1200, 1250]
    })

    result = merge_dataframes_on_date([df1, df2])

    assert "oil" in result.columns
    assert "freight" in result.columns
    assert len(result) == 2


def test_handle_missing_values():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-07", "2024-01-14", "2024-01-21"]),
        "oil": [72, None, 76],
        "freight": [1200, 1250, None]
    })

    result = handle_missing_values(df, fill_method="ffill_bfill")

    assert result.isnull().sum().sum() == 0


def test_scale_features():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2024-01-07", "2024-01-14", "2024-01-21"]),
        "oil": [70, 75, 80],
        "freight": [1000, 1200, 1400]
    })

    scaled_df, scaler = scale_features(df)

    assert "oil" in scaled_df.columns
    assert "freight" in scaled_df.columns
    assert scaler is not None


def test_preprocess_pipeline():
    df1 = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=14, freq="D"),
        "oil": range(70, 84)
    })

    df2 = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=14, freq="D"),
        "freight": range(1000, 1014)
    })

    processed_df, scaler = preprocess_pipeline([df1, df2])

    assert "date" in processed_df.columns
    assert "oil" in processed_df.columns
    assert "freight" in processed_df.columns
    assert processed_df.isnull().sum().sum() == 0
    assert scaler is not None