"""Kalkulator EWS rule-based (dipindah dari notebook CELL 10, tanpa ubah logika)."""

def s_rr(x):
    if x <= 8: return 3
    if x <= 11: return 1
    if x <= 20: return 0
    if x <= 24: return 2
    return 3

def s_spo2(x):
    if x <= 91: return 3
    if x <= 93: return 2
    if x <= 95: return 1
    return 0

def s_temp(x):
    if x <= 35.0: return 3
    if x <= 36.0: return 1
    if x <= 38.0: return 0
    if x <= 39.0: return 1
    return 2

def s_sys(x):
    if x <= 90: return 3
    if x <= 100: return 2
    if x <= 110: return 1
    if x <= 219: return 0
    return 3

def s_hr(x):
    if x <= 40: return 3
    if x <= 50: return 1
    if x <= 90: return 0
    if x <= 110: return 1
    if x <= 130: return 2
    return 3

def s_conscious(avpu=None, gcs=None):
    if gcs is not None:
        return 0 if gcs == 15 else 3
    return 0 if (avpu or "A").upper() == "A" else 3

def ews(v):
    parts = {
        "RR": s_rr(v["RR"]),
        "SpO2": s_spo2(v["SPO2"]),
        "O2": 0 if v.get("O2", "air").lower() == "air" else 2,
        "Temp": s_temp(v["T"]),
        "SYS": s_sys(v["SYS"]),
        "HR": s_hr(v["HR"]),
        "Conscious": s_conscious(v.get("AVPU"), v.get("GCS")),
    }
    total = sum(parts.values())
    single3 = any(s == 3 for s in parts.values())
    if total >= 7:
        band, advice = "HIGH", "Tim emergency segera (resus)."
    elif total >= 5:
        band, advice = "MEDIUM", "Review medis segera."
    elif total >= 3 or single3:
        band, advice = "LOW-MEDIUM", "Perawat senior menilai; pertimbangkan eskalasi."
    else:
        band, advice = "LOW", "Pemantauan rutin."
    return total, band, parts, advice
