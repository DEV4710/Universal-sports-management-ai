import json
import random
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Alexa+ Ultimate Sports Manager MCP Server", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "player_database.json")

def load_db():
    with open(DB_PATH, "r") as f:
        return json.load(f)

# Global Game State
game_state = {
    "active_sport": "cricket",
    "mode": "IPL Auction",
    "user_team_name": "Royal Challengers Alexa",
    "budget": 100.0, # Currency unit depends on sport (Cr for Cricket, €M for Football, $M for Basketball)
    "currency_symbol": "₹",
    "currency_unit": "Cr",
    "club_facilities": {"stadium_capacity": 50000, "training_level": "Tier 3", "youth_academy": "Tier 2", "morale": "High"},
    "tactics": {"formation": "4-3-3", "style": "Balanced Attack", "captain": "Auto"},
    "current_target": None,
    "user_roster": [],
    "recent_logs": ["Game Session initialized. Select Cricket IPL Auction, Football Transfer Window, or NBA Draft to begin."]
}

def update_currency():
    if game_state["active_sport"] == "cricket":
        game_state["currency_symbol"] = "₹"
        game_state["currency_unit"] = "Cr"
        game_state["mode"] = "IPL Auction"
        if game_state["budget"] > 200: game_state["budget"] = 100.0
    elif game_state["active_sport"] == "football":
        game_state["currency_symbol"] = "€"
        game_state["currency_unit"] = "M"
        game_state["mode"] = "Transfer Window"
        if game_state["budget"] < 150: game_state["budget"] = 250.0
    elif game_state["active_sport"] == "basketball":
        game_state["currency_symbol"] = "$"
        game_state["currency_unit"] = "M"
        game_state["mode"] = "NBA Draft & Free Agency"
        if game_state["budget"] > 200 or game_state["budget"] < 80: game_state["budget"] = 140.0

@app.post("/mcp")
async def handle_mcp(request: Request):
    body = await request.json()
    method = body.get("method")
    req_id = body.get("id")

    if method == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2025-11-25",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "Alexa+ Ultimate Sports Manager MCP", "version": "2.0.0"}
            }
        })

    elif method == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "select_sport_and_mode",
                        "description": "Switch between Cricket (IPL Auction), Football (Transfer Window), and Basketball (NBA Draft).",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "sport": {"type": "string", "enum": ["cricket", "football", "basketball"]},
                                "user_team_name": {"type": "string"}
                            },
                            "required": ["sport"]
                        }
                    },
                    {
                        "name": "execute_player_acquisition",
                        "description": "Place a bid in Cricket Auction, submit a transfer offer in Football, or select a rookie pick in NBA Draft.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "player_name": {"type": "string"},
                                "offer_amount": {"type": "number"},
                                "action_type": {"type": "string", "enum": ["bid", "negotiate", "draft_pick"]}
                            },
                            "required": ["player_name"]
                        }
                    },
                    {
                        "name": "set_squad_tactics",
                        "description": "Set team formation, tactical playing style, and team leadership.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "formation": {"type": "string"},
                                "style": {"type": "string"},
                                "captain": {"type": "string"}
                            }
                        }
                    },
                    {
                        "name": "manage_club_finances",
                        "description": "Upgrade stadium facilities, youth academy, or boost team morale.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "upgrade_type": {"type": "string", "enum": ["stadium", "training", "youth_academy", "morale_boost"]},
                                "investment_amount": {"type": "number"}
                            },
                            "required": ["upgrade_type"]
                        }
                    },
                    {
                        "name": "simulate_full_match",
                        "description": "Simulate a live career/manager match with real-time commentary, score progression, and stats.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "opponent_team": {"type": "string"}
                            }
                        }
                    }
                ]
            }
        })

    elif method == "tools/call":
        tool_name = body.get("params", {}).get("name")
        args = body.get("params", {}).get("arguments", {})
        db = load_db()

        if tool_name == "select_sport_and_mode":
            sport = args.get("sport", "cricket").lower()
            game_state["active_sport"] = sport
            if args.get("user_team_name"):
                game_state["user_team_name"] = args.get("user_team_name")
            update_currency()
            game_state["user_roster"] = []
            log_msg = f"Switched to {sport.upper()} ({game_state['mode']}). Team: {game_state['user_team_name']}."
            game_state["recent_logs"].append(log_msg)

            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps({"status": "success", "message": log_msg, "state": game_state, "available_players": db[sport]["players"]})}]
                }
            })

        elif tool_name == "execute_player_acquisition":
            sport = game_state["active_sport"]
            player_name = args.get("player_name")
            offer = args.get("offer_amount", 5.0)
            action = args.get("action_type", "bid")

            # Find player
            player = next((p for p in db[sport]["players"] if player_name.lower() in p["name"].lower()), None)
            if not player:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps({"status": "error", "message": f"Player '{player_name}' not found in {sport} database."})}]}
                })

            if offer > game_state["budget"]:
                msg = f"Insufficient budget! Offer {game_state['currency_symbol']}{offer}{game_state['currency_unit']} exceeds remaining budget {game_state['currency_symbol']}{game_state['budget']:.1f}{game_state['currency_unit']}."
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": json.dumps({"status": "error", "message": msg, "state": game_state})}]}
                })

            # Acquire player
            game_state["budget"] -= offer
            player["status"] = f"Signed by {game_state['user_team_name']}"
            game_state["user_roster"].append(player)
            
            if sport == "cricket":
                res_msg = f"SOLD! {player['name']} ({player['role']}) acquired by {game_state['user_team_name']} for {game_state['currency_symbol']}{offer}{game_state['currency_unit']} in the IPL Auction!"
            elif sport == "football":
                res_msg = f"TRANSFER COMPLETED! {player['name']} signs for {game_state['user_team_name']} for {game_state['currency_symbol']}{offer}{game_state['currency_unit']}!"
            else:
                res_msg = f"DRAFT SELECTION! With their pick, {game_state['user_team_name']} selects {player['name']} ({player['role']})!"

            game_state["recent_logs"].append(res_msg)

            return JSONResponse({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps({"status": "success", "message": res_msg, "state": game_state, "signed_player": player})}]
                }
            })

        elif tool_name == "set_squad_tactics":
            if args.get("formation"): game_state["tactics"]["formation"] = args.get("formation")
            if args.get("style"): game_state["tactics"]["style"] = args.get("style")
            if args.get("captain"): game_state["tactics"]["captain"] = args.get("captain")
            msg = f"Tactics updated: Formation {game_state['tactics']['formation']}, Style: {game_state['tactics']['style']}."
            game_state["recent_logs"].append(msg)
            return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps({"status": "success", "message": msg, "state": game_state})}]}})

        elif tool_name == "manage_club_finances":
            upg = args.get("upgrade_type")
            cost = args.get("investment_amount", 10.0)
            if cost > game_state["budget"]:
                return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps({"status": "error", "message": "Insufficient club funds."})}]}})
            game_state["budget"] -= cost
            if upg == "stadium": game_state["club_facilities"]["stadium_capacity"] += 10000
            elif upg == "training": game_state["club_facilities"]["training_level"] = "Tier 5 Elite"
            elif upg == "youth_academy": game_state["club_facilities"]["youth_academy"] = "Tier 5 World Class"
            elif upg == "morale_boost": game_state["club_facilities"]["morale"] = "Ecstatic (100%)"
            msg = f"Club Facility Upgrade: {upg.replace('_', ' ').title()} upgraded for {game_state['currency_symbol']}{cost}{game_state['currency_unit']}."
            game_state["recent_logs"].append(msg)
            return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps({"status": "success", "message": msg, "state": game_state})}]}})

        elif tool_name == "simulate_full_match":
            opp = args.get("opponent_team", "Rival Champions")
            sport = game_state["active_sport"]
            if sport == "cricket":
                user_score = f"{random.randint(170, 225)}/{random.randint(3, 8)} (20.0 ov)"
                opp_score = f"{random.randint(150, 210)}/{random.randint(5, 10)} (19.4 ov)"
                win = int(user_score.split('/')[0]) > int(opp_score.split('/')[0])
                commentary = f"MATCH RESULT: {game_state['user_team_name']} ({user_score}) {'DEFEATED' if win else 'LOST TO'} {opp} ({opp_score}) in a thrilling IPL finish! Player of the match performance powered by voice tactical changes."
            elif sport == "football":
                u_g, o_g = random.randint(1, 4), random.randint(0, 3)
                win = u_g > o_g
                commentary = f"FULL TIME: {game_state['user_team_name']} {u_g} - {o_g} {opp}. Tactical style '{game_state['tactics']['style']}' dominated midfield possession!"
            else:
                u_pts, o_pts = random.randint(102, 128), random.randint(95, 120)
                win = u_pts > o_pts
                commentary = f"FINAL SCORE: {game_state['user_team_name']} {u_pts} - {o_pts} {opp}. Clutch 4th quarter performance secures the victory!"
            
            game_state["recent_logs"].append(commentary)
            return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps({"status": "success", "message": commentary, "state": game_state, "match_outcome": "WIN" if win else "LOSS"})}]}})

@app.get("/state")
async def get_state():
    db = load_db()
    return {
        "state": game_state,
        "available_players": db[game_state["active_sport"]]["players"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
