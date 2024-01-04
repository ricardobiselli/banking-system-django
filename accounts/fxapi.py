import http.client
import json

conn = http.client.HTTPSConnection("api.fxratesapi.com")
conn.request("GET", "/latest")
res = conn.getresponse()

if res.status == 200:
    data = res.read()
    exchange_rates = json.loads(data)
    rates = exchange_rates["rates"]
    for currency, rate in rates.items():
        print(f"{currency}: {rate}")
else:
    print("Failed to fetch exchange rates.")

conn.close()
