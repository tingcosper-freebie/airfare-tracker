import json
import requests
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

with open("config.json") as f:
    config = json.load(f)

route = config["routes"][0]
EMAIL = config["email"]

url = "https://serpapi.com/search.json"

params = {
    "engine": "google_flights",
    "departure_id": route["from"],
    "arrival_id": route["to"],
    "outbound_date": route["depart_date"],
    "return_date": route["return_date"],
    "currency": "USD",
    "hl": "en",
    "api_key": SERPAPI_KEY
}

response = requests.get(url, params=params)
data = response.json()

price = None

if "best_flights" in data and len(data["best_flights"]) > 0:
    price = data["best_flights"][0]["price"]

if not price:
    print("No price found")
    exit()

log_entry = f"{datetime.now().isoformat()} - ${price}\n"

with open("price_log.txt", "a") as f:
    f.write(log_entry)

print(f"Live price: ${price}")

if price <= route["alert_price"]:

    subject = f"Flight Alert: PHL ⇄ CHS now ${price}"

    if price <= route["priority_price"]:
        subject = f"🔥 BUY NOW: PHL ⇄ CHS ${price}"

    body = f"""
Live Flight Deal Found!

Route: {route['from']} ⇄ {route['to']}
Dates: {route['depart_date']} to {route['return_date']}
Price: ${price}

https://www.google.com/travel/flights
"""

    print(subject)
