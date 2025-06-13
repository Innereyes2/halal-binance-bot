import os
import requests
from dotenv import load_dotenv

load_dotenv()

def send_whatsapp(message):
    account_sid = os.getenv("WHATSAPP_TWILIO_SID")
    auth_token = os.getenv("WHATSAPP_TWILIO_AUTH")
    from_number = os.getenv("WHATSAPP_FROM")
    to_number = os.getenv("WHATSAPP_TO")

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = {
        "From": from_number,
        "To": to_number,
        "Body": message,
    }

    response = requests.post(url, data=data, auth=(account_sid, auth_token))
    print("WhatsApp response:", response.status_code, response.text)
