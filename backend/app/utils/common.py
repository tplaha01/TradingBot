def clamp(x: float, lo: float=-1.0, hi: float=1.0) -> float:
    return max(lo, min(hi, x))
