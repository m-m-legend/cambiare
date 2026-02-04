from flask import Flask, render_template, request
from services.exchange_service import get_exchange_rates
from services.investment_service import best_stock_sectors

app = Flask(__name__)

CURRENCIES = ["BRL", "USD", "EUR", "JPY", "CAD"]

@app.route("/", methods=["GET", "POST"])
def index():
    base = request.form.get("base", "USD")
    target = request.form.get("target", "BRL")
    amount = float(request.form.get("amount", 1))

    rates = get_exchange_rates(base)
    converted_value = None

    if rates and target in rates:
        converted_value = round(amount * rates[target], 2)
        


    return render_template(
        "index.html",
        currencies=CURRENCIES,
        base=base,
        target=target,
        amount=amount,
        rates=rates,
        converted_value=converted_value,
        sectors=best_stock_sectors()
    )

if __name__ == "__main__":
    app.run(debug=True)

