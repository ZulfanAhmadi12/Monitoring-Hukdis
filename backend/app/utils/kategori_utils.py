# backend/app/utils/kategori_utils.py

import json
import re
try:
    from backend.app.utils.logger import log_event
except ModuleNotFoundError:
    from app.utils.logger import log_event


# ======================================================================
# 1. SANITIZING + VALIDATION
# ======================================================================

VALID_TRUE = {"terpenuhi", "yes", "ya", "y", "1", "true", "ok"}
VALID_FALSE = {"tidak terpenuhi", "tidak", "no", "n", "0", "false"}

REQUIRED_COLS = ["kewenangan", "kesengajaan", "financial", "fraud"]


def sanitize_value(value, nomor_lha, pn, col):
    """Normalize messy inputs: whitespace, uppercase, synonyms, etc."""

    if value is None:
        raise ValueError(f"Baris nomor_lha={nomor_lha}, pn={pn}: kolom '{col}' kosong")

    v = str(value).strip().lower()
    v = re.sub(r"\s+", " ", v)  # collapse multiple whitespaces

    # Map to canonical values
    if v in VALID_TRUE:
        return "terpenuhi"

    if v in VALID_FALSE:
        return "tidak terpenuhi"

    # INVALID
    raise ValueError(
        f"Baris nomor_lha={nomor_lha}, pn={pn}: "
        f"nilai '{value}' pada kolom '{col}' tidak valid. "
        f"Gunakan 'terpenuhi' atau 'tidak terpenuhi'."
    )


# ======================================================================
# 2. LOAD RULES FROM JSON
# ======================================================================

def load_rules():
    import os
    rules_path = os.path.join(os.path.dirname(__file__), "..", "config", "kategori_rules.json")

    with open(rules_path, "r", encoding="utf-8") as f:
        return json.load(f)


RULES = load_rules()   # loaded once on import


# ======================================================================
# 3. CHECK RULE OVERLAP (at import time)
# ======================================================================

def check_rule_overlap():
    """Ensure two rules do not represent the same combination."""
    seen = {}

    for idx, rule in enumerate(RULES):
        sig = (
            rule.get("kewenangan"),
            rule.get("kesengajaan"),
            rule.get("financial"),
            rule.get("fraud"),
        )
        if sig in seen:
            raise ValueError(
                f"Rule overlap detected between rule #{seen[sig]} and rule #{idx}, "
                f"signature={sig}"
            )
        seen[sig] = idx

check_rule_overlap()


# ======================================================================
# 4. MAIN FUNCTION: DETERMINE CATEGORY
# ======================================================================

def penentuan_kategori_pelanggaran(row: dict):
    nomor_lha = row.get("nomor_lha", "?")
    pn = row.get("pn", "?")

    sanitized = {}

    # 1. SANITASI semua kolom wajib
    for col in REQUIRED_COLS:
        sanitized_value = sanitize_value(row.get(col), nomor_lha, pn, col)
        sanitized[col] = sanitized_value

    # 2. CARI KATEGORI BERDASARKAN RULE JSON
    matches = []
    for rule in RULES:
        ok = True
        for col in REQUIRED_COLS:
            if sanitized[col] != rule[col]:
                ok = False
                break
        if ok:
            matches.append(rule["kategori"])

    # 3. HASIL KATEGORI
    if len(matches) == 1:
        return {
            "kategori": matches[0],
            "sanitized": sanitized
        }

    if len(matches) == 0:
        msg = (
            f"Tidak ada rule cocok untuk nomor_lha={nomor_lha}, pn={pn}: "
            f"(kew={sanitized['kewenangan']}, kes={sanitized['kesengajaan']}, "
            f"fin={sanitized['financial']}, fraud={sanitized['fraud']})"
        )
        log_event("error", msg)
        raise ValueError(msg)

    msg = f"Ambiguous rule match untuk nomor_lha={nomor_lha}, pn={pn}: {matches}"
    log_event("error", msg)
    raise ValueError(msg)


