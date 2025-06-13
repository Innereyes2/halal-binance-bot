import os
import time
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Connect to Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# Read bot ON/OFF status
def get_status():
    status = supabase.table("status").select("*").eq("id", 1).execute()
    return status.data[0]["running"]

# Turn bot ON or OFF
def set_status(new_state):
    supabase.table("status").update({"running": new_state}).eq("id", 1).execute()
    print("✅ Bot is now", "ON" if new_state else "OFF")

# Watch status every few seconds
def dashboard_loop():
    print("📟 Dashboard running. Watching for start/stop signal...")

    while True:
        bot_state = get_status()
        print("🤖 Bot is", "RUNNING ✅" if bot_state else "STOPPED 🛑")
        time.sleep(15)

if __name__ == "__main__":
    dashboard_loop()
