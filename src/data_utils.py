"""
Utility functions for loading and cleaning the Himalayan Expeditions dataset.
"""
from pathlib import Path
import pandas as pd


def load_raw_data(data_dir: str | Path) -> dict[str, pd.DataFrame]:
    """Load the four main CSV files from data/raw/. Returns a dict keyed by table name."""
    data_dir = Path(data_dir)
    tables = ["exped", "members", "peaks", "refer"]
    return {
        name: pd.read_csv(data_dir / f"{name}.csv",
                          low_memory=False, encoding='latin1')
        for name in tables
    }


def clean_expeditions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the expeditions table.
    - Imputes NaN in success1–success4 as False.
    - Drops rows without a valid year (pre-1900 or null).
    - Lowercases the peakid for consistent joining.
    """
    df = df.copy()
    for col in ["success1", "success2", "success3", "success4"]:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)
    df = df.dropna(subset=["year"])
    df["year"] = df["year"].astype(int)
    df = df[df["year"] >= 1900]
    df["peakid"] = df["peakid"].str.strip().str.upper()
    return df


def clean_members(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the members table.
    - Imputes NaN in msuccess as False.
    - Creates full_name from fname + lname.
    - Strips and title-cases citizen field.
    """
    df = df.copy()
    if "msuccess" in df.columns:
        df["msuccess"] = df["msuccess"].fillna(False).astype(bool)
    if "death" in df.columns:
        df["death"] = df["death"].fillna("N")
    df["full_name"] = (
        df.get("fname", pd.Series("", index=df.index)).fillna("").str.strip()
        + " "
        + df.get("lname", pd.Series("", index=df.index)).fillna("").str.strip()
    ).str.strip()
    if "citizen" in df.columns:
        df["citizen"] = df["citizen"].str.strip().str.title()
    df["peakid"] = df["peakid"].str.strip().str.upper()
    return df


def clean_peaks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the peaks table.
    - Strips and title-cases pkname.
    - Uppercases peakid for consistent joining.
    """
    df = df.copy()
    df["pkname"] = df["pkname"].str.strip().str.title()
    df["peakid"] = df["peakid"].str.strip().str.upper()
    return df


def merge_master(exped: pd.DataFrame, peaks: pd.DataFrame) -> pd.DataFrame:
    """
    Join expeditions with peak metadata via peakid.
    Returns a flat DataFrame ready for temporal and regional analysis.
    """
    return exped.merge(
        peaks[["peakid", "pkname", "heightm", "himal", "pstatus"]],
        on="peakid",
        how="left",
    )
