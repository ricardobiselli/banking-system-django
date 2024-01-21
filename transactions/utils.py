from decimal import Decimal
import http.client
import json


def get_exchange_rate(base_currency, target_currency):
    conn = http.client.HTTPSConnection("api.fxratesapi.com")
    conn.request("GET", f"/latest?base={base_currency}")
    res = conn.getresponse()

    if res.status == 200:
        data = res.read()
        exchange_rates = json.loads(data)
        rates = exchange_rates["rates"]
        return Decimal(rates.get(target_currency, 1))
    else:
        return Decimal(1)

    conn.close()
