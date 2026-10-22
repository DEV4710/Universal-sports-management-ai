import json
import random
import os
from typing import Dict, Any, List
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Alexa+ Universal Sports Manager MCP Server", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load master database
DB_PATH = os.path.join(os.path.dirname(__file__), "player_database.json")
with open(DB_PATH, "r") as f:
    MASTER_DB = json.load(f)

# Global Manager Game State
game_state = {
    "sport": "cricket",  # cricket, football, basketball
    "manager_name": "Coach Alexa",
    "selected_team": {
        "id": "rcb",
        "name": "Royal Challengers Alexa",
        "budget": 100.0,
        "currency": "₹",
        "unit": "Cr"
    },
    "phase": "title",  # title, setup, hub, acquisition, tactics, match, standings
    "season": 2026,
    "current_matchday": 1,
    "total_matchdays": 14,
    "squad": [],
    "tactics": {
        "formation": "4-3-3",
        "mentality": "Attacking",
        "captain": "Virat Kohli",
        "bowling_order": "Pace Heavy"
    },
    "league_standings": [],
    "acquisition": {
        "active": False,
        "current_item": None,
        "current_bid": 0.0,
        "highest_bidder": "None",
        "logs": []
    },
    "live_match": {
        "home_team": "Royal Challengers Alexa",
        "away_team": "Mumbai AI",
        "home_score": 0,
        "away_score": 0,
        "time_elapsed": "00:00",
        "status": "Not Started",
        "commentary_feed": []
    }
}

@app.get("/")
def read_root():
    return {"status": "online", "system": "Alexa+ MCP Server 2026", "mcp_version": "2025-11-25"}

@app.get("/state")
def get_state():
    return game_state

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    payload = await request.json()
    method = payload.get("method")
    req_id = payload.get("id", 1)

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2025-11-25",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "Alexa+ Universal Sports Manager MCP Engine",
                    "version": "3.0.0"
                }
            }
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "init_career_mode",
                        "description": "Initialize career mode for Cricket, Football, or Basketball.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "sport": {"type": "string", "enum": ["cricket", "football", "basketball"]},
                                "manager_name": {"type": "string"},
                                "team_id": {"type": "string"}
                            },
                            "required": ["sport", "manager_name", "team_id"]
                        }
                    },
                    {
                        "name": "voice_auction_bid",
                        "description": "Place a natural voice bid in the IPL Cricket Mega Auction or Transfer Window.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "bid_amount": {"type": "number", "description": "Bid value in Cr or Millions"}
                            },
                            "required": ["bid_amount"]
                        }
                    },
                    {
                        "name": "set_tactics",
                        "description": "Set team tactics, formation, or playstyle via voice commands.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "formation": {"type": "string"},
                                "mentality": {"type": "string"}
                            }
                        }
                    },
                    {
                        "name": "simulate_match",
                        "description": "Simulate the current league fixture with AI voice commentary and real-time tactical events.",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
            }
        }

    elif method == "tools/call":
        params = payload.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "init_career_mode":
            sport = args.get("sport", "cricket")
            team_id = args.get("team_id", "rcb")
            manager_name = args.get("manager_name", "Manager Alexa")

            sport_data = MASTER_DB.get(sport, MASTER_DB["cricket"])
            team = next((t for t in sport_data["teams"] if t["id"] == team_id), sport_data["teams"][0])

            game_state["sport"] = sport
            game_state["manager_name"] = manager_name
            game_state["selected_team"] = {
                "id": team["id"],
                "name": team["name"],
                "budget": team.get("budget_cr") or team.get("budget_m") or 100.0,
                "currency": "₹" if sport == "cricket" else "€" if sport == "football" else "$",
                "unit": "Cr" if sport == "cricket" else "M"
            }
            game_state["phase"] = "hub"
            game_state["current_matchday"] = 1
            game_state["total_matchdays"] = 14 if sport == "cricket" else 38 if sport == "football" else 82

            # Initialize Standings
            game_state["league_standings"] = [
                {"team": t["name"], "played": 0, "won": 0, "lost": 0, "drawn": 0, "points": 0, "rating": t["rating"]}
                for t in sport_data["teams"]
            ]

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{
                        "type": "text",
                        "text": f"Career initialized for {manager_name} managing {team['name']} in {sport.upper()} mode."
                    }],
                    "state": game_state
                }
            }

        elif tool_name == "voice_auction_bid":
            bid_amt = args.get("bid_amount", 5.0)
            acq = game_state["acquisition"]
            curr_bid = acq["current_bid"]

            if bid_amt <= curr_bid:
                res_text = f"Bid ₹{bid_amt} rejected. Must exceed current highest bid of ₹{curr_bid}."
            elif bid_amt > game_state["selected_team"]["budget"]:
                res_text = f"Bid rejected! Insufficient club transfer budget."
            else:
                acq["current_bid"] = bid_amt
                acq["highest_bidder"] = game_state["selected_team"]["name"]
                acq["logs"].insert(0, f"🗣️ {game_state['manager_name']} placed bid: {game_state['selected_team']['currency']}{bid_amt}{game_state['selected_team']['unit']}")

                # AI Counter Bid Chance
                if random.random() > 0.3:
                    ai_team = random.choice(["Mumbai AI", "Real Madrid AI", "Boston AI"])
                    counter = round(bid_amt + random.choice([0.5, 1.0, 2.0]), 1)
                    acq["current_bid"] = counter
                    acq["highest_bidder"] = ai_team
                    acq["logs"].insert(0, f"🤖 {ai_team} outbid with {game_state['selected_team']['currency']}{counter}{game_state['selected_team']['unit']}!")
                    res_text = f"Bid placed, but {ai_team} countered with {counter}!"
                else:
                    res_text = f"Highest bid belongs to {game_state['selected_team']['name']} at {bid_amt}!"

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": res_text}],
                    "state": game_state
                }
            }

        elif tool_name == "set_tactics":
            form = args.get("formation", "4-3-3")
            ment = args.get("mentality", "Attacking")
            game_state["tactics"]["formation"] = form
            game_state["tactics"]["mentality"] = ment

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Tactics updated: {form} | {ment} mentality."}],
                    "state": game_state
                }
            }

        elif tool_name == "simulate_match":
            sport = game_state["sport"]
            team_name = game_state["selected_team"]["name"]
            opp = random.choice([t["team"] for t in game_state["league_standings"] if t["team"] != team_name])

            if sport == "cricket":
                user_score = f"{random.randint(160, 220)}/{random.randint(3, 8)}"
                opp_score = f"{random.randint(150, 215)}/{random.randint(4, 9)}"
                winner = team_name if int(user_score.split("/")[0]) > int(opp_score.split("/")[0]) else opp
            elif sport == "football":
                user_goals = random.randint(0, 4)
                opp_goals = random.randint(0, 3)
                user_score, opp_score = user_goals, opp_goals
                winner = team_name if user_goals > opp_goals else opp if opp_goals > user_goals else "Draw"
            else:
                user_score = random.randint(98, 128)
                opp_score = random.randint(95, 125)
                winner = team_name if user_score > opp_score else opp

            game_state["current_matchday"] += 1
            game_state["live_match"] = {
                "home_team": team_name,
                "away_team": opp,
                "home_score": user_score,
                "away_score": opp_score,
                "status": f"Full Time - {winner} Victory!",
                "commentary_feed": [
                    f"FULL TIME! {team_name} ({user_score}) vs {opp} ({opp_score}).",
                    f"Tactical adjustment: {game_state['tactics']['mentality']} style proved effective.",
                    f"Key Player MVP performance awarded!"
                ]
            }

            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Match completed: {team_name} {user_score} - {opp_score} {opp}"}],
                    "state": game_state
                }
            }

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
