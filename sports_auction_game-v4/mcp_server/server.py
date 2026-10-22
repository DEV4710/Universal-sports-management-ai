"""
Universal Sports Manager AI (v4 Engine)
Model Context Protocol (MCP) Server - Streamable HTTP Spec 2025-11-25
"""

import json
import random
import os
from typing import Dict, Any, List
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Alexa+ Universal Sports Manager AI MCP Server", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Database
DB_PATH = os.path.join(os.path.dirname(__file__), "player_database.json")
with open(DB_PATH, "r") as f:
    SPORTS_DB = json.load(f)

# Global Session State
GAME_STATE: Dict[str, Any] = {
    "sport": "cricket",
    "selected_team_id": "rcb",
    "user_manager_name": "Manager Alexa",
    "currency_symbol": "₹",
    "currency_unit": "Cr",
    "user_budget": 100.0,
    "user_roster": [],
    "teams": [],
    "auction_pool": [],
    "current_player_index": 0,
    "current_player": None,
    "current_bid": 0.0,
    "highest_bidder_id": None,
    "highest_bidder_name": "Base Price",
    "auction_status": "waiting", # waiting, active, sold, passed, finished
    "auction_logs": [],
    "formation": "4-3-3 Attacking",
    "tactics": "Balanced",
    "league_standings": [],
    "match_day": 1,
    "total_match_days": 10,
    "last_match_result": None
}

def init_game_session(sport: str, user_team_id: str, manager_name: str):
    global GAME_STATE
    sport_data = SPORTS_DB.get(sport, SPORTS_DB["cricket"])
    
    GAME_STATE["sport"] = sport
    GAME_STATE["currency_symbol"] = sport_data["currency"]
    GAME_STATE["currency_unit"] = sport_data["unit"]
    GAME_STATE["user_manager_name"] = manager_name or "Manager Alexa"
    GAME_STATE["user_roster"] = []
    GAME_STATE["auction_logs"] = []
    GAME_STATE["current_player_index"] = 0
    GAME_STATE["match_day"] = 1
    
    # Clone teams
    teams = json.loads(json.dumps(sport_data["teams"]))
    for t in teams:
        t["roster"] = []
        t["points"] = 0
        t["played"] = 0
        t["won"] = 0
        t["lost"] = 0
        if t["id"] == user_team_id:
            t["is_user"] = True
            GAME_STATE["selected_team_id"] = user_team_id
            GAME_STATE["user_budget"] = t["budget"]
        else:
            t["is_user"] = False
            
    GAME_STATE["teams"] = teams
    GAME_STATE["auction_pool"] = json.loads(json.dumps(sport_data["players"]))
    
    # Set default formations
    if sport == "cricket":
        GAME_STATE["formation"] = "Balanced XI (5 Bat / 2 AR / 4 Bowl)"
        GAME_STATE["total_match_days"] = 14
    elif sport == "football":
        GAME_STATE["formation"] = "4-3-3 Attacking"
        GAME_STATE["total_match_days"] = 38
    else:
        GAME_STATE["formation"] = "Pace & Space (1-2-2)"
        GAME_STATE["total_match_days"] = 82
        
    _load_current_lot()
    _recalculate_standings()
    
def _load_current_lot():
    idx = GAME_STATE["current_player_index"]
    pool = GAME_STATE["auction_pool"]
    if idx < len(pool):
        p = pool[idx]
        GAME_STATE["current_player"] = p
        GAME_STATE["current_bid"] = p["base_price"]
        GAME_STATE["highest_bidder_id"] = None
        GAME_STATE["highest_bidder_name"] = "Base Price"
        GAME_STATE["auction_status"] = "active"
        symbol = GAME_STATE["currency_symbol"]
        unit = GAME_STATE["currency_unit"]
        GAME_STATE["auction_logs"].insert(0, f"📢 LOT #{idx+1}: {p['name']} ({p['role']}, OVR {p['rating']}) is on the block! Base Price: {symbol}{p['base_price']}{unit}.")
    else:
        GAME_STATE["current_player"] = None
        GAME_STATE["auction_status"] = "finished"
        GAME_STATE["auction_logs"].insert(0, "🏆 AUCTION CONCLUDED! All players have been processed. Prepare for Season Matchday 1!")

def _recalculate_standings():
    # Sort teams by points, then rating sum
    sorted_teams = sorted(GAME_STATE["teams"], key=lambda t: (t["points"], sum(p.get("rating", 80) for p in t["roster"])), reverse=True)
    GAME_STATE["league_standings"] = sorted_teams

@app.get("/")
def root():
    return {"status": "ok", "service": "Alexa+ Sports Manager AI Engine v4"}

@app.get("/api/state")
def get_state():
    return GAME_STATE

@app.post("/mcp")
async def handle_mcp(request: Request):
    body = await request.json()
    method = body.get("method")
    rpc_id = body.get("id", 1)

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "protocolVersion": "2025-11-25",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "Alexa+ Universal Sports Manager AI", "version": "4.0.0"}
            }
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "tools": [
                    {
                        "name": "start_career_session",
                        "description": "Start a new realistic Career Mode session for Cricket, Football, or Basketball.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "sport": {"type": "string", "enum": ["cricket", "football", "basketball"]},
                                "user_team_id": {"type": "string"},
                                "manager_name": {"type": "string"}
                            },
                            "required": ["sport", "user_team_id"]
                        }
                    },
                    {
                        "name": "place_user_bid",
                        "description": "Place a competitive voice bid on the current auction player lot.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "bid_amount": {"type": "number"}
                            }
                        }
                    },
                    {
                        "name": "trigger_ai_bid_step",
                        "description": "Simulate rival AI teams bidding on the current lot based on their valuations.",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "finalize_current_lot",
                        "description": "Knock down/sell the current lot to the highest bidder and advance automatically to the next player.",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "set_tactics",
                        "description": "Adjust team tactical formation and match mindset via voice.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "formation": {"type": "string"},
                                "tactics": {"type": "string"}
                            }
                        }
                    },
                    {
                        "name": "simulate_match_day",
                        "description": "Simulate the current season matchday with dynamic sport-isolated algorithm.",
                        "inputSchema": {"type": "object", "properties": {}}
                    }
                ]
            }
        }

    elif method == "tools/call":
        params = body.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        symbol = GAME_STATE["currency_symbol"]
        unit = GAME_STATE["currency_unit"]

        if tool_name == "start_career_session":
            sport = args.get("sport", "cricket")
            team_id = args.get("user_team_id", "rcb")
            mgr = args.get("manager_name", "Manager Alexa")
            init_game_session(sport, team_id, mgr)
            return _mcp_response(rpc_id, f"Career Mode initialized for {sport.upper()}! Selected team: {team_id.upper()}. Bidding is open.")

        elif tool_name == "place_user_bid":
            if GAME_STATE["auction_status"] != "active" or not GAME_STATE["current_player"]:
                return _mcp_response(rpc_id, "Auction is not currently active for bidding.")
            
            p = GAME_STATE["current_player"]
            curr_bid = GAME_STATE["current_bid"]
            user_bid = args.get("bid_amount", round(curr_bid + 0.5, 2))
            
            # Find user team
            user_team = next((t for t in GAME_STATE["teams"] if t["is_user"]), None)
            if not user_team or user_bid > user_team["budget"]:
                return _mcp_response(rpc_id, f"Insufficient budget! Your remaining budget is {symbol}{user_team['budget'] if user_team else 0}{unit}.")
            
            if user_bid <= curr_bid and GAME_STATE["highest_bidder_id"] is not None:
                user_bid = round(curr_bid + (0.5 if GAME_STATE['sport']=='cricket' else 5.0), 2)
                
            GAME_STATE["current_bid"] = user_bid
            GAME_STATE["highest_bidder_id"] = user_team["id"]
            GAME_STATE["highest_bidder_name"] = user_team["name"]
            
            GAME_STATE["auction_logs"].insert(0, f"🙋♂️ {user_team['name']} placed a bid of {symbol}{user_bid}{unit} on {p['name']}!")
            
            # Automatically trigger AI reaction
            _process_ai_bidding()
            
            return _mcp_response(rpc_id, f"Bid registered at {symbol}{user_bid}{unit}! Current highest bidder: {GAME_STATE['highest_bidder_name']}.")

        elif tool_name == "trigger_ai_bid_step":
            _process_ai_bidding()
            return _mcp_response(rpc_id, f"AI teams evaluated lot. Highest bidder: {GAME_STATE['highest_bidder_name']} at {symbol}{GAME_STATE['current_bid']}{unit}.")

        elif tool_name == "finalize_current_lot":
            _sell_or_pass_current_lot()
            return _mcp_response(rpc_id, "Lot finalized. Advanced to next lot.")

        elif tool_name == "set_tactics":
            if "formation" in args:
                GAME_STATE["formation"] = args["formation"]
            if "tactics" in args:
                GAME_STATE["tactics"] = args["tactics"]
            return _mcp_response(rpc_id, f"Tactics updated to {GAME_STATE['formation']} ({GAME_STATE['tactics']}).")

        elif tool_name == "simulate_match_day":
            msg = _simulate_full_matchday()
            return _mcp_response(rpc_id, msg)

    return _mcp_response(rpc_id, "Unknown MCP tool call.", error=True)

def _process_ai_bidding():
    if GAME_STATE["auction_status"] != "active" or not GAME_STATE["current_player"]:
        return
    
    p = GAME_STATE["current_player"]
    curr_bid = GAME_STATE["current_bid"]
    val = p.get("valuation", p["base_price"] * 2)
    symbol = GAME_STATE["currency_symbol"]
    unit = GAME_STATE["currency_unit"]

    # Filter AI teams with budget and valuation margin
    ai_teams = [t for t in GAME_STATE["teams"] if not t["is_user"] and t["budget"] >= curr_bid + 0.5]
    
    # Filter AI teams that value this player higher than current bid
    willing_teams = [t for t in ai_teams if curr_bid < val * random.uniform(0.85, 1.15)]
    
    if willing_teams and GAME_STATE["highest_bidder_id"] != willing_teams[0]["id"]:
        buyer = random.choice(willing_teams)
        increment = 0.5 if GAME_STATE["sport"] == "cricket" else (5.0 if GAME_STATE["sport"] == "football" else 2.0)
        new_bid = round(curr_bid + increment, 2)
        
        if new_bid <= buyer["budget"]:
            GAME_STATE["current_bid"] = new_bid
            GAME_STATE["highest_bidder_id"] = buyer["id"]
            GAME_STATE["highest_bidder_name"] = buyer["name"]
            GAME_STATE["auction_logs"].insert(0, f"🤖 {buyer['name']} countered with {symbol}{new_bid}{unit} for {p['name']}!")

def _sell_or_pass_current_lot():
    p = GAME_STATE["current_player"]
    if not p:
        return
    
    symbol = GAME_STATE["currency_symbol"]
    unit = GAME_STATE["currency_unit"]
    bidder_id = GAME_STATE["highest_bidder_id"]
    final_price = GAME_STATE["current_bid"]
    
    if bidder_id:
        # Find winning team
        winner = next((t for t in GAME_STATE["teams"] if t["id"] == bidder_id), None)
        if winner:
            winner["budget"] = round(winner["budget"] - final_price, 2)
            winner["roster"].append(p)
            if winner["is_user"]:
                GAME_STATE["user_budget"] = winner["budget"]
                GAME_STATE["user_roster"].append(p)
            GAME_STATE["auction_logs"].insert(0, f"🎉 SOLD! {p['name']} goes to {winner['name']} for {symbol}{final_price}{unit}!")
    else:
        GAME_STATE["auction_logs"].insert(0, f"❌ UNSOLD! {p['name']} passed without any bids.")
        
    # Advance lot index
    GAME_STATE["current_player_index"] += 1
    _load_current_lot()

def _simulate_full_matchday():
    sport = GAME_STATE["sport"]
    teams = GAME_STATE["teams"]
    day = GAME_STATE["match_day"]
    
    user_team = next((t for t in teams if t["is_user"]), teams[0])
    ai_teams = [t for t in teams if not t["is_user"]]
    opponent = random.choice(ai_teams)
    
    user_rating = sum(p.get("rating", 80) for p in user_team["roster"]) or 85
    opp_rating = sum(p.get("rating", 80) for p in opponent["roster"]) or 85
    
    # Tactical boost
    if GAME_STATE["tactics"] == "Aggressive":
        user_rating += 3
    elif GAME_STATE["tactics"] == "Counter / Defensive":
        user_rating += 2

    # Win probability calculation
    prob = user_rating / (user_rating + opp_rating)
    user_won = random.random() < prob
    
    user_team["played"] += 1
    opponent["played"] += 1
    
    if sport == "cricket":
        if user_won:
            user_score = f"{random.randint(180, 220)}/4"
            opp_score = f"{random.randint(140, 179)}/9"
            user_team["points"] += 2
            user_team["won"] += 1
            opponent["lost"] += 1
            result_txt = f"VICTORY! {user_team['name']} ({user_score}) defeated {opponent['name']} ({opp_score}) by {random.randint(15, 45)} runs!"
        else:
            user_score = f"{random.randint(140, 165)}/8"
            opp_score = f"{random.randint(166, 175)}/3"
            opponent["points"] += 2
            opponent["won"] += 1
            user_team["lost"] += 1
            result_txt = f"DEFEAT! {opponent['name']} ({opp_score}) defeated {user_team['name']} ({user_score}) by 7 wickets."
            
    elif sport == "football":
        u_goals = random.randint(2, 4) if user_won else random.randint(0, 1)
        o_goals = random.randint(0, 1) if user_won else random.randint(2, 3)
        if u_goals > o_goals:
            user_team["points"] += 3
            user_team["won"] += 1
            opponent["lost"] += 1
            result_txt = f"VICTORY! {user_team['name']} {u_goals} - {o_goals} {opponent['name']}!"
        elif u_goals == o_goals:
            user_team["points"] += 1
            opponent["points"] += 1
            result_txt = f"DRAW! {user_team['name']} {u_goals} - {o_goals} {opponent['name']}."
        else:
            opponent["points"] += 3
            opponent["won"] += 1
            user_team["lost"] += 1
            result_txt = f"DEFEAT! {user_team['name']} {u_goals} - {o_goals} {opponent['name']}."
            
    else: # Basketball
        u_pts = random.randint(110, 128) if user_won else random.randint(95, 108)
        o_pts = random.randint(95, 108) if user_won else random.randint(110, 125)
        if user_won:
            user_team["points"] += 2
            user_team["won"] += 1
            opponent["lost"] += 1
            result_txt = f"VICTORY! {user_team['name']} {u_pts} - {o_pts} {opponent['name']}!"
        else:
            opponent["points"] += 2
            opponent["won"] += 1
            user_team["lost"] += 1
            result_txt = f"DEFEAT! {user_team['name']} {u_pts} - {o_pts} {opponent['name']}!"

    GAME_STATE["match_day"] += 1
    GAME_STATE["last_match_result"] = result_txt
    _recalculate_standings()
    return f"Matchday {day} Concluded: {result_txt}"

def _mcp_response(rpc_id: int, text: str, error: bool = False):
    return {
        "jsonrpc": "2.0",
        "id": rpc_id,
        "result": {
            "content": [{"type": "text", "text": text}],
            "isError": error
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
