# ✅ dashboard.py — Flask control dashboard
import os
from flask import Flask, request, render_template_string
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Halal Bot Dashboard</title>
  <style>
    body { background-color: black; color: white; font-family: Arial; text-align: center; padding: 50px; }
    button { font-size: 16px; padding: 10px 20px; margin: 10px; }
    table { margin: 20px auto; border-collapse: collapse; }
    th, td { border: 1px solid white; padding: 8px 16px; }
  </style>
</head>
<body>
  <h1>🤖 Halal Binance Bot Dashboard</h1>
  <p>Status: <strong style="color: yellow">{{ status }}</strong></p>
  <form method="post">
    <button name="action" value="start">Start Bot</button>
    <button name="action" value="stop">Stop Bot</button>
  </form>

  <h2>📈 Open Trades</h2>
  <table>
    <tr><th>Symbol</th><th>Price</th><th>Quantity</th></tr>
    {% for trade in trades %}
      <tr><td>{{ trade.symbol }}</td><td>{{ trade.price }}</td><td>{{ trade.quantity }}</td></tr>
    {% endfor %}
  </table>
</body>
</html>
"""

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "start":
            supabase.table("status").update({"running": True}).eq("id", 1).execute()
        elif action == "stop":
            supabase.table("status").update({"running": False}).eq("id", 1).execute()

    running = supabase.table("status").select("*").eq("id", 1).execute().data[0]["running"]
    trades = supabase.table("trades").select("symbol, price, quantity").order("id", desc=True).limit(10).execute().data
    return render_template_string(HTML, status="RUNNING ✅" if running else "STOPPED 🚩", trades=trades)

def start_dashboard_server():
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    start_dashboard_server()
