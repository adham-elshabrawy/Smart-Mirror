import os
import requests
from flask import Flask, jsonify, request
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Set a secret key for Flask sessions
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallbackSecretKey")

# SportsDB API key from environment
SPORTSDB_API_KEY = os.getenv("SPORTSDb_API_KEY")

# Base endpoint for TheSportsDB
BASE_URL = "https://www.thesportsdb.com/api/v1/json/"

@app.route('/')
def index():
    """
    Home route.
    Returns a simple welcome message and instructions.
    """
    return (
        "Welcome to the Sports API Integration!<br>"
        "Use /league/<league_id>/events to see upcoming events for a league.<br>"
        "Use /team/<team_id>/events to see upcoming events for a team."
    )

@app.route('/league/<league_id>/events')
def league_events(league_id):
    """
    Fetch upcoming events for a given league.
    Example leagues: 
    - English Premier League (id=4328)
    - NBA (id=4387), etc.
    """
    url = f"{BASE_URL}{SPORTSDB_API_KEY}/eventsnextleague.php?id={league_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch league events"}), 500
    
    data = response.json()
    events = data.get('events', [])
    
    # Create a simplified response
    event_list = []
    for event in events:
        event_list.append({
            "event": event["strEvent"],
            "date": event["dateEvent"],
            "time": event["strTime"],
            "homeTeam": event["strHomeTeam"],
            "awayTeam": event["strAwayTeam"]
        })
    
    return jsonify({"league_id": league_id, "upcoming_events": event_list})

@app.route('/team/<team_id>/events')
def team_events(team_id):
    """
    Fetch upcoming events for a given team.
    Example teams:
    - Manchester United (id=133612), 
    - Golden State Warriors (id=134873), etc.
    """
    url = f"{BASE_URL}{SPORTSDB_API_KEY}/eventsnext.php?id={team_id}"
    response = requests.get(url)
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch team events"}), 500
    
    data = response.json()
    events = data.get('events', [])
    
    # Create a simplified response
    event_list = []
    for event in events:
        event_list.append({
            "event": event["strEvent"],
            "date": event["dateEvent"],
            "time": event["strTime"],
            "homeTeam": event["strHomeTeam"],
            "awayTeam": event["strAwayTeam"]
        })
    
    return jsonify({"team_id": team_id, "upcoming_events": event_list})

@app.route('/search/team')
def search_team():
    """
    Search for a team by name.
    e.g. /search/team?name=Warriors
    """
    query = request.args.get('name', '')
    if not query:
        return jsonify({"error": "Missing 'name' query parameter"}), 400
    
    url = f"{BASE_URL}{SPORTSDB_API_KEY}/searchteams.php?t={query}"
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to search teams"}), 500
    
    data = response.json()
    teams = data.get("teams", [])
    
    # Return basic info for each team found
    results = []
    for team in teams:
        results.append({
            "teamName": team["strTeam"],
            "teamID": team["idTeam"],
            "league": team["strLeague"],
            "stadium": team["strStadium"]
        })
    
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
