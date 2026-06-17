from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pymongo
import re
import requests
import speech_recognition as sr
import pyttsx3
from typing import Dict, List
from datetime import datetime

app = FastAPI()

# CORS setup for front-end communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup 
client = pymongo.MongoClient("mongodb://localhost:27017/")  
db = client["cricket_db"]
collection = db["matches"]

# API keys 
CRICKETDATA_API_KEY = "8fe507eb-2181-469a-9918-398ee5bdc951"  # Get from https://cricketdata.org/
GNEWS_API_KEY = "8f213ca8739338b90b68c09571d81649d515c595f72cdf39548f6bf4f9b10bd6"  # Get from https://gnews.io/

# Speech setup
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

class QueryRequest(BaseModel):
    query: str
    lang: str = "en"

# Entity Extraction from Query
def extract_entities(query: str) -> Dict:
    date_pattern = r"\d{4}-\d{2}-\d{2}|\d{4}/\d{2}/\d{2}"
    date = re.search(date_pattern, query)
    teams = []
    players = []
    # Common cricket teams
    for team in ["India", "Australia", "New Zealand", "South Africa", "England", "West Indies", "Pakistan", "Sri Lanka"]:
        if team.lower() in query.lower():
            teams.append(team)
    # Player name regex (simplified: capitalize words)
    player_pattern = r"[A-Z][a-z]+ [A-Z][a-z]+"
    players = re.findall(player_pattern, query)
    return {
        "date": date.group().replace("/", "-") if date else None,
        "teams": teams,
        "players": players
    }

# Fetch CricketData API
async def fetch_cricketdata_api(team1: str, team2: str = None, date: str = None) -> Dict:
    try:
        url = "https://api.cricapi.com/v1/matches"
        params = {"apikey": CRICKETDATA_API_KEY}
        if team1:
            params["team1"] = team1
        if team2:
            params["team2"] = team2
        if date:
            params["date"] = date
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"CricketData API error: {str(e)}"}

# Fetch Google News API
async def fetch_news_api(team1: str, team2: str = None) -> str:
    try:
        url = "https://gnews.io/api/v4/search"
        query = f"{team1} vs {team2} cricket" if team2 else f"{team1} cricket"
        params = {"q": query, "token": GNEWS_API_KEY, "lang": "en", "max": 3}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        news_summary = "\n".join([article["title"] for article in data.get("articles", [])])
        return news_summary or "No recent news found."
    except Exception as e:
        return f"News fetch error: {str(e)}"

# Fetch Wikipedia API
async def fetch_wikipedia_api(query: str) -> str:
    try:
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": query,
            "prop": "extracts",
            "exintro": True,
            "explaintext": True
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        page = next(iter(data["query"]["pages"].values()), {})
        return page.get("extract", "No Wikipedia info found.")
    except Exception as e:
        return f"Wikipedia fetch error: {str(e)}"

# Main Query Processing Endpoint
@app.post("/query")
async def process_query(request: QueryRequest):
    query = request.query
    lang = request.lang
    entities = extract_entities(query)

    response = {}

    # Query MongoDB for match data
    mongo_query = {}
    if entities["date"]:
        mongo_query["date"] = entities["date"]
    if entities["teams"]:
        mongo_query["teams"] = {"$all": entities["teams"]}
    if entities["players"]:
        mongo_query["top_performers.name"] = {"$in": entities["players"]}

    match_data = collection.find_one(mongo_query)
    if match_data:
        response["match_summary"] = {
            "winner": match_data.get("winner", "Unknown"),
            "venue": match_data.get("venue", "Unknown"),
            "runs": match_data.get("runs_total", {}),
            "wickets": match_data.get("wickets", {}),
            "top_performers": match_data.get("top_performers", [])
        }
    else:
        response["match_summary"] = "No match data found in database."

    # Fetch real-time match data from CricketData API
    if entities["teams"]:
        team1 = entities["teams"][0]
        team2 = entities["teams"][1] if len(entities["teams"]) > 1 else None
        api_data = await fetch_cricketdata_api(team1, team2, entities["date"])
        if "error" not in api_data:
            response["live_data"] = api_data.get("data", "No live data available.")

    # Fetch news
    if entities["teams"]:
        team1 = entities["teams"][0]
        team2 = entities["teams"][1] if len(entities["teams"]) > 1 else None
        response["news"] = await fetch_news_api(team1, team2)

    # Fetch Wikipedia info for players or teams
    if entities["players"]:
        response["player_info"] = await fetch_wikipedia_api(entities["players"][0])
    elif entities["teams"]:
        response["team_info"] = await fetch_wikipedia_api(entities["teams"][0])

    # Visualization
    if "plot" in query.lower() or "graph" in query.lower():
        if "ipl" in query.lower():
            # Aggregate IPL data from MongoDB
            ipl_matches = collection.find({"match_type": "IPL"}).limit(3)
            players, runs = [], []
            for match in ipl_matches:
                for performer in match.get("top_performers", []):
                    if performer["name"] not in players:
                        players.append(performer["name"])
                        runs.append(performer.get("runs", 0))
            response["visualization"] = {
                "type": "bar",
                "data": {
                    "labels": players[:3],
                    "values": runs[:3]
                }
            }
        elif "win-loss" in query.lower() and entities["teams"]:
            # Aggregate win-loss ratio from MongoDB
            years = [str(y) for y in range(2018, 2024)]
            team1, team2 = entities["teams"][0], entities["teams"][1] if len(entities["teams"]) > 1 else None
            team1_ratios, team2_ratios = [], []
            for year in years:
                matches = collection.find({"date": {"$regex": f"^{year}"}, "teams": {"$in": [team1]}})
                wins, total = 0, 0
                for match in matches:
                    total += 1
                    if match["winner"] == team1:
                        wins += 1
                team1_ratios.append(wins / total if total else 0)
                if team2:
                    matches = collection.find({"date": {"$regex": f"^{year}"}, "teams": {"$in": [team2]}})
                    wins, total = 0, 0
                    for match in matches:
                        total += 1
                        if match["winner"] == team2:
                            wins += 1
                    team2_ratios.append(wins / total if total else 0)
            response["visualization"] = {
                "type": "line",
                "data": {
                    "labels": years,
                    "team1": team1_ratios,
                    "team2": team2_ratios if team2 else []
                }
            }

    return {"response": response, "lang": lang}

# Voice Input Endpoint
@app.post("/voice")
async def process_voice(request: QueryRequest):
    try:
        with sr.Microphone() as source:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio, language="ta-IN" if request.lang == "ta" else "en-US")
            return await process_query(QueryRequest(query=text, lang=request.lang))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Voice recognition error: {str(e)}")

# Text-to-Speech Endpoint
@app.post("/tts")
async def text_to_speech(request: QueryRequest):
    try:
        tts_engine.setProperty("voice", "tamil" if request.lang == "ta" else "english")
        tts_engine.say(request.query)
        tts_engine.runAndWait()
        return {"status": "Speech generated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)