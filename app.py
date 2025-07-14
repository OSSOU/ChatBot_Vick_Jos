from flask import Flask, request
from twilio.rest import Client
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Twilio credentials
TWILIO_SID = os.getenv("US7e41847863430e319b5ace709fbd3c29")
TWILIO_TOKEN = os.getenv("a5f7e1f03a99af49601b42915662d696")
client = Client(TWILIO_SID, TWILIO_TOKEN)

# API-Football credentials
API_KEY = os.getenv("RAPIDAPI_KEY")
API_HOST = os.getenv("RAPIDAPI_HOST")

HEADERS = {
    "X-RapidAPI-Key": API_KEY,
    "X-RapidAPI-Host": API_HOST
}

# WhatsApp sandbox number
WHATSAPP_FROM = "whatsapp:+14155238886"  # Twilio sandbox number

def get_team_score(team_name):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    params = {
        "live": "all"
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        return "⚠️ Unable to fetch live data at the moment."

    data = response.json().get("response", [])
    
    for match in data:
        teams = match['teams']
        if team_name.lower() in teams['home']['name'].lower() or team_name.lower() in teams['away']['name'].lower():
            home = teams['home']['name']
            away = teams['away']['name']
            goals_home = match['goals']['home']
            goals_away = match['goals']['away']
            status = match['fixture']['status']['long']
            return f"⚽ {home} {goals_home} - {goals_away} {away} ({status})"
    
    return f"ℹ️ No live match found for '{team_name.title()}'."

@app.route("/webhook", methods=["POST"])
def webhook():
    user_msg = request.form.get("Body")
    from_number = request.form.get("From")

    if not user_msg:
        return "No message received.", 200

    # Example: "score PSG"
    if user_msg.lower().startswith("score "):
        team = user_msg[6:].strip()
        response_msg = get_team_score(team)
    else:
        response_msg = "👋 Welcome! Send: score <team name> to get live score.\nExample: score Barcelona"

    # Send response via Twilio
    client.messages.create(
        body=response_msg,
        from_=WHATSAPP_FROM,
        to=from_number
    )

    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
