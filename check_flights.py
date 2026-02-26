import json
import os
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# =========================
# Load configuration
# =========================

with open("config.json") as f:
    config = json.load(f)

route = config["routes"][0]

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
ALERT_EMAIL = os.environ.get("ALERT_EMAIL")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

print("=== Airfare tracker run ===")
print(f"Route: {route['from']} -> {route['to']}")
print(f"Dates: {route['depart_date']} to {route['return_date']}")
print(f"Nonstop only: {route.get('nonstop_only', True)}")

# =========================
# Validate environment
# =========================

if not SERPAPI_KEY:
    raise Exception("Missing SERPAPI_KEY secret")

# =========================
# Query SerpAPI
# =========================

url = "https://serpapi.com/search.json"

params = {
    "engine": "google_flights",
    "type": 1,  # round trip
    "departure_id": route["from"],
    "arrival_id": route["to"],
    "outbound_date": route["depart_date"],
    "return_date": route["return_date"],
    "currency": "USD",
    "hl": "en",
    "gl": "us",
    "deep_search": "true",
    "api_key": SERPAPI_KEY
}

# Nonstop filter
if route.get("nonstop_only", True):
    params["stops"] = 1

response = requests.get(url, params=params)

print(f"HTTP status: {response.status_code}")

data = response.json()

if "error" in data:
    raise Exception(f"SerpAPI error: {data['error']}")

# =========================
# Extract price
# =========================

def extract_price(value):
    if isinstance(value, int):
        return value

    if isinstance(value, str):
        digits = "".join(c for c in value if c.isdigit())
        return int(digits) if digits else None

    return None

flights = []

if "best_flights" in data:
    flights.extend(data["best_flights"])

if "other_flights" in data:
    flights.extend(data["other_flights"])

if not flights:
    raise Exception("No flights found")

prices = []

for flight in flights:
    price = extract_price(flight.get("price"))
    if price:
        prices.append(price)

if not prices:
    raise Exception("No valid prices found")

price = min(prices)

print(f"✅ Cheapest price found: ${price}")

# =========================
# Log price history
# =========================

log_line = f"{datetime.now().isoformat()} - ${price}\n"

with open("price_log.txt", "a") as f:
    f.write(log_line)

print("Price logged")

# =========================
# Email alert function
# =========================

def send_email(subject, body):

    if not ALERT_EMAIL or not GMAIL_APP_PASSWORD:
        print("Email secrets not configured. Skipping email.")
        return

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = ALERT_EMAIL
    msg["To"] = ALERT_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(ALERT_EMAIL, GMAIL_APP_PASSWORD)
        server.send_message(msg)

    print("✅ Email alert sent")

# =========================
# Alert logic
# =========================

if price <= route["alert_price"]:

    subject = f"Flight Alert: {route['from']} ⇄ {route['to']} is ${price}"

    if price <= route["priority_price"]:
        subject = f"🔥 BUY NOW: {route['from']} ⇄ {route['to']} is ${price}"

    body = f"""
Flight Deal Found!

Route: {route['from']} ⇄ {route['to']}
Dates: {route['depart_date']} to {route['return_date']}
Nonstop: {route.get('nonstop_only', True)}
Price: ${price}

Check flights:
https://www.google.com/travel/flights
"""

    send_email(subject, body)

else:
    print(f"No alert. Price ${price} above threshold ${route['alert_price']}")

print("=== Tracker complete ===")
