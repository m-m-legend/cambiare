import requests

API_URL = "https://open.er-api.com/v6/latest/{}"

SUPPORTED_CURRENCIES = ["BRL", "USD", "EUR", "JPY", "CAD"]
# Taxas de câmbio
def get_exchange_rates(base_currency):
    try:
        response = requests.get(API_URL.format(base_currency), timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get("result") != "success":
            return {}

        rates = data.get("rates", {})
        return {k: rates[k] for k in SUPPORTED_CURRENCIES if k in rates}

    except Exception:
        return {}
