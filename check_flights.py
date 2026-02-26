import json
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Load config
with open("config.json") as f:
    config = json.load(f)

EMAIL = config["email"]
route = config["routes"][0]

# Simulated price check (we'll upgrade this to live pricing next)
price = random.randint(180, 420)

# Log price
log_entry = f"{datetime.now().isoformat()} - ${price}\n"
with open("price_log.txt", "a") as f:
    f.write(log_entry)

print(f"Current price: ${price}")

# Send alert if below threshold
if price <= route["alert_price"]:

    subject = f"Flight Alert: PHL ⇄ CHS now ${price}"

    if price <= route["priority_price"]:
        subject = f"🔥 BUY NOW: PHL ⇄ CHS ${price}"

    body = f"""
Flight Deal Found!

Route: {route['from']} ⇄ {route['to']}
Dates: {route['depart_date']} to {route['return_date']}
Nonstop: Yes
Price: ${price}

Check Google Flights immediately.
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    print("Alert triggered")
