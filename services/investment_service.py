import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")
BASE_URL = "https://finnhub.io/api/v1/quote"

SECTOR_ETFS = {
    "Technology": "XLK",
    "Energy": "XLE",
    "Healthcare": "XLV",
    "Financial Services": "XLF",
    "Consumer Cyclical": "XLY",
    "Consumer Defensive": "XLP",
    "Industrials": "XLI",
    "Basic Materials": "XLB",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Communication Services": "XLC"
}

TRANSLATION = {
    "Technology": "Tecnologia",
    "Energy": "Energia",
    "Healthcare": "Saúde",
    "Financial Services": "Financeiro",
    "Consumer Cyclical": "Consumo Cíclico",
    "Consumer Defensive": "Consumo Básico",
    "Industrials": "Indústria",
    "Basic Materials": "Commodities",
    "Utilities": "Utilidades Públicas",
    "Real Estate": "Imobiliário",
    "Communication Services": "Comunicações"
}

CACHE_TTL = 60 * 60  


MARKET_INDICES = {
    "S&P 500": "SPY",
    "Nasdaq": "QQQ",
    "Ibovespa": "EWZ",
    "Dow Jones": "DIA",
    "FTSE 100": "EWU"
}

_cache_indices = {"data": None, "timestamp": 0}

def get_market_indices():
    """Busca a performance das principais bolsas do mundo"""
    now = time.time()
    if _cache_indices["data"] and now - _cache_indices["timestamp"] < CACHE_TTL:
        return _cache_indices["data"]

    results = []
    for name, ticker in MARKET_INDICES.items():
        data = _fetch_etf_performance(name, ticker) 
        if data:
            results.append(data)
        time.sleep(0.1)

    _cache_indices["data"] = results
    _cache_indices["timestamp"] = now
    return results

def get_all_sector_performance():
    """Retorna TODOS os setores, ordenados do melhor para o pior"""
    data = get_sector_performance_cached()
    
    # Ordenamos usando uma função lambda que trata o "N/A" caso o fallback esteja ativo
    ranked = sorted(data, key=lambda x: x["performance"] if isinstance(x["performance"], (int, float)) else -999, reverse=True)

    final_data = []
    for item in ranked:
        perf = item["performance"]
        # Só tenta arredondar se for número
        display_perf = f"{round(perf, 2)}%" if isinstance(perf, (int, float)) else perf
        
        final_data.append({
            "sector": item["sector"],
            "performance": display_perf,
            "raw_perf": perf 
        })

    return final_data

_cache = {"data": None, "timestamp": 0}

def _fetch_etf_performance(sector_name, ticker):
    """Busca o preço atual e calcula a variação percentual do dia"""
    try:
        params = {"symbol": ticker, "token": API_KEY}
        r = requests.get(BASE_URL, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
        
        change_percent = data.get("dp", 0)
        
        return {
            "sector": TRANSLATION.get(sector_name, sector_name),
            "performance": change_percent,
            "raw_sector": sector_name
        }
    except Exception as e:
        print(f"Erro ao buscar {ticker}: {e}")
        return None

def get_sector_performance_cached():
    now = time.time()
    if _cache["data"] and now - _cache["timestamp"] < CACHE_TTL:
        return _cache["data"]

    results = []
    # Rate limit de 60/min
    for sector, ticker in SECTOR_ETFS.items():
        data = _fetch_etf_performance(sector, ticker)
        if data:
            results.append(data)
        time.sleep(0.1) 

    if not results:
        return fallback_sectors()

    _cache["data"] = results
    _cache["timestamp"] = now
    return results

def best_stock_sectors():
    """Retorna o top 4 sem estragar o cache"""
    data = get_sector_performance_cached()
    
    # Ordena com segurança
    ranked = sorted(data, key=lambda x: x["performance"] if isinstance(x["performance"], (int, float)) else -999, reverse=True)

    result = []
    for item in ranked[:4]:
        perf = item["performance"]
        display_perf = f"{round(perf, 2)}%" if isinstance(perf, (int, float)) else perf
        
        result.append({
            "sector": item["sector"],
            "performance": display_perf,
            "raw_sector": item.get("raw_sector", "")
        })
        
    return result

def fallback_sectors():
    return [
        {"sector": "Tecnologia", "performance": "N/A", "raw_sector": "Technology"},
        {"sector": "Energia", "performance": "N/A", "raw_sector": "Energy"},
        {"sector": "Saúde", "performance": "N/A", "raw_sector": "Healthcare"},
        {"sector": "Financeiro", "performance": "N/A", "raw_sector": "Financial Services"},
    ]