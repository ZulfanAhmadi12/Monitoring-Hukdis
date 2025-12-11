import pandas as pd
import numpy as np
from datetime import datetime
from typing import Any

# ============================================================
# 1. Fungsi parsing tanggal dari user (dipakai apa adanya)
# ============================================================
POSSIBLE_DATE_FORMATS = [
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%m-%d-%Y",
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%d/%m/%Y %H:%M:%S",
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%fZ"
]

def parse_excel_date(value):
    if value is None or pd.isna(value):
        return ""

    try:
        v = str(value).strip()
    except:
        v = value

    if v in ("", "nan", "None"):
        return ""

    # Excel date numeric
    if isinstance(value, (int, float)):
        try:
            dt = pd.to_datetime(value, unit="d", origin="1899-12-30")
            return dt.strftime("%d/%m/%Y")
        except:
            pass

    # Datetime-like
    if isinstance(value, (datetime, pd.Timestamp, np.datetime64)):
        try:
            return pd.to_datetime(value).strftime("%d/%m/%Y")
        except:
            pass

    # Try formats one by one
    for fmt in POSSIBLE_DATE_FORMATS:
        try:
            return datetime.strptime(v, fmt).strftime("%d/%m/%Y")
        except:
            continue

    # Fallback
    try:
        dt = pd.to_datetime(v, dayfirst=True, errors="raise")
        return dt.strftime("%d/%m/%Y")
    except:
        return ""


# ============================================================
# 2. Convert string dd/mm/YYYY to datetime (untuk perhitungan SLA)
# ============================================================
def to_datetime_or_none(s):
    if not s or pd.isna(s):
        return None
    try:
        return datetime.strptime(s, "%d/%m/%Y")
    except:
        return None


# ============================================================
# 3. Fungsi Hitung SLA (mengembalikan "" jika tidak dapat dihitung)
# ============================================================
def hitung_sla(tgl_awal, tgl_akhir, batas=5):
    if tgl_awal is None or tgl_akhir is None:
        return ""     # sesuai permintaan: tetap kosong
    selisih = (tgl_akhir - tgl_awal).days
    return "Melebihi SLA" if selisih > batas else "Sesuai SLA"


# ============================================================
# 2. Convert string dd/mm/YYYY to datetime (untuk perhitungan SLA)
# ============================================================
def to_dt(s):
    if not s:
        return None
    try:
        return datetime.strptime(s, "%d/%m/%Y")
    except:
        return None


# ============================================================
# MAIN FUNCTION: tentukan SLA 3 kolom
# ============================================================
def tentukan_sla(df: pd.DataFrame) -> pd.DataFrame:
    # --- Step A: standar kan tanggal menjadi dd/mm/YYYY ---
    tanggal_cols = [
        "tanggal_lha",
        "tanggal_surat_nota_rekomendasi",
        "tanggal_lembar_putusan_pejabat_pemutus",
        "tanggal_sk_putusan",
    ]
    for col in tanggal_cols:
        df[col] = df[col].apply(parse_excel_date)

    def sla_value(t1, t2):
        if t1 is None or t2 is None:
            return ""
        delta = (t2 - t1).days
        return "Melebihi SLA" if delta > 5 else "Sesuai SLA"

    # penyampaian_nota_rekomendasi
    df["penyampaian_nota_rekomendasi"] = df.apply(
        lambda r: sla_value(
            to_dt(r.get("tanggal_lha")),
            to_dt(r.get("tanggal_surat_nota_rekomendasi"))
        ),
        axis=1
    )

    # pejabat_pemutus
    df["pejabat_pemutus"] = df.apply(
        lambda r: sla_value(
            to_dt(r.get("tanggal_surat_nota_rekomendasi")),
            to_dt(r.get("tanggal_lembar_putusan_pejabat_pemutus"))
        ),
        axis=1
    )

    # sk
    df["sk"] = df.apply(
        lambda r: sla_value(
            to_dt(r.get("tanggal_lembar_putusan_pejabat_pemutus")),
            to_dt(r.get("tanggal_sk_putusan"))
        ),
        axis=1
    )

    return df

def normalize_value(v: Any) -> str:
    if v is None:
        return ""
    v = str(v).strip()
    if v in ["", "nan", "None"]:
        return ""
    return v


def detect_changes(old_row: dict, new_row: dict) -> dict:
    changes = {}
    for col in new_row:
        old_val = normalize_value(old_row.get(col))
        new_val = normalize_value(new_row.get(col))

        if old_val != new_val:
            changes[col] = {
                "before": old_val,
                "after": new_val
            }

    return changes
