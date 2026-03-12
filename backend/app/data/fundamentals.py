import requests
from ..config import get_settings

settings = get_settings()
FMP_KEY = settings.FMP_KEY

def get_fundamentals(symbol: str):
    """Fetch basic fundamental ratios from FMP free endpoints."""
    if not FMP_KEY:
        # fallback defaults
        return {
            "revenue_growth": 0.1,
            "gross_margin": 0.4,
            "oper_margin": 0.25,
            "debt_to_equity": 1.0,
            "pe": 25.0,
        }

    try:
        # 1️⃣ ratios (margins, leverage)
        ratios_url = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{symbol.upper()}?apikey={FMP_KEY}"
        ratios = requests.get(ratios_url, timeout=10).json()
        r = ratios[0] if isinstance(ratios, list) and ratios else {}

        # 2️⃣ profile (P/E)
        prof_url = f"https://financialmodelingprep.com/api/v3/profile/{symbol.upper()}?apikey={FMP_KEY}"
        prof = requests.get(prof_url, timeout=10).json()
        p = prof[0] if isinstance(prof, list) and prof else {}

        return {
            "revenue_growth": float(r.get("revenueGrowthTTM", 0.05)),
            "gross_margin": float(r.get("grossProfitMarginTTM", 0.35)),
            "oper_margin": float(r.get("operatingProfitMarginTTM", 0.2)),
            "debt_to_equity": float(r.get("debtEquityRatioTTM", 1.0)),
            "pe": float(p.get("pe", 20.0)),
        }

    except Exception as e:
        print("⚠️ FMP fetch exception:", e)
        return {
            "revenue_growth": 0.05,
            "gross_margin": 0.35,
            "oper_margin": 0.2,
            "debt_to_equity": 1.0,
            "pe": 20.0,
        }
