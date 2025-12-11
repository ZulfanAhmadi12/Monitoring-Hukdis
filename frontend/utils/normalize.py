import pandas as pd

def normalize(val):
    if pd.isna(val):
        return ""
    v = str(val).strip()
    if v.lower() in ["none", "nan", "null"]:
        return ""
    return v
