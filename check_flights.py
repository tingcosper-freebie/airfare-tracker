import json
import requests
import os
import smtplib
from email.mime.text import MIMEText

def send_email(subject: str, body: str):
    to_email = os.environ.get("ALERT_EMAIL")
    app_pw = os.environ.get("GMAIL_APP_PASSWORD")

    if not to_email or not app_pw:
        print("Email secrets not set; skipping email.")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = to_email
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(to_email, app_pw)
        smtp.send_message(msg)

    print("✅ Email sent")
    if price <= route["alert_price"]:
    subject = f"Flight Alert: {route['from']} ⇄ {route['to']} is ${price}"
        if price <= route["priority_price"]:
            subject = f"🔥 BUY NOW: {route['from']} ⇄ {route['to']} is ${price}"

    body = f"""Deal found!

Route: {route['from']} ⇄ {route['to']}
Dates: {route['depart_date']} to {route['return_date']}
Nonstop: {route.get('nonstop_only', True)}
Price: ${price}

Open Google Flights:
https://www.google.com/travel/flights
"""
    send_email(subject, body)
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
