import http.client
import json

# Establish a connection to the API
conn = http.client.HTTPSConnection("api.fxratesapi.com")

# Send a GET request to retrieve the latest exchange rates
conn.request("GET", "/latest")

# Get the response from the API
res = conn.getresponse()

# Check if the request was successful (status code 200)
if res.status == 200:
    # Read the response data
    data = res.read()
    
    # Decode the JSON response
    exchange_rates = json.loads(data)
    
    # Access the rates dictionary containing the exchange rates
    rates = exchange_rates["rates"]
    
    # Print the exchange rates for different currencies
    for currency, rate in rates.items():
        print(f"{currency}: {rate}")
else:
    print("Failed to fetch exchange rates.")

# Close the connection
conn.close()
