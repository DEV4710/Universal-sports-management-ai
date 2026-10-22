# Universal Sports Manager AI 2026 🏆
**The Ultimate Voice-Driven Living Room Sports Career Engine for Fire TV & Alexa+**

Official Submission for **Build, Ship, Shape: Amazon Developer Hackathon 2026**  
*Target Tracks*: **Fire TV Track** ($25,000 Top Prize) & **Alexa+ Track** ($25,000 Top Prize)

---

## 🌟 Overview

**Universal Sports Manager AI 2026** brings the depth and excitement of modern sports career games (**FC 27 / NBA 2K / Football Manager / IPL Auction Simulators**) into the living room. By pairing **Fire TV's 10-foot big-screen visuals** with an **Alexa+ Model Context Protocol (MCP) server**, players can manage clubs, bid in auctions, negotiate transfers, set tactical pitch formations, and simulate entire seasons using natural voice commands and remote controls.

---

## 🎮 Key Features & Game Modes

### 🏏 1. IPL Cricket Career Mode
* **Live Mega Auction**: Bid against AI rival franchise owners (*"Alexa, bid ₹15 Crore on Jasprit Bumrah"*).
* **14-Match IPL Season**: Simulate league fixtures with ball-by-ball commentary, Orange & Purple Cap leaderboards, and Playoff finals.

### ⚽ 2. Football Manager Career Mode
* **Transfer Window & Scouting**: Negotiate release clauses and transfer fees for stars like Erling Haaland, Jude Bellingham, and Kylian Mbappé.
* **Tactical Pitch Board**: Drag and set 4-3-3, 4-2-3-1, or 3-5-2 pitch tactics with live mentality switches (*"Alexa, go All-Out Attack"*).
* **38-Match League & European Champions Cup**: Full league simulation with real-time match events.

### 🏀 3. NBA Franchise Career Mode
* **NBA Draft & Free Agency**: Pick top draft prospects (Victor Wembanyama, Cooper Flagg) and manage team salary caps.
* **82-Game Season & NBA Playoffs**: Track conference standings and playoff brackets.

---

## 🛠️ Architecture & Tech Stack

```
   ┌────────────────────────┐             ┌───────────────────────────────────┐
   │   Alexa+ Voice AI      │  JSON-RPC   │   FastAPI MCP Server              │
   │   (Agent Skill / MCP)  │────────────>│   (server.py)                     │
   └────────────────────────┘  HTTP/2025  │   - State Engine                  │
                                          │   - AI Rival Logic                │
                                          └─────────────────┬─────────────────┘
                                                            │ REST / Local WS
                                                            ▼
                                          ┌───────────────────────────────────┐
                                          │   Fire TV Big-Screen UI           │
                                          │   (index.html / app.js)           │
                                          │   - Glassmorphism Broadcast UI    │
                                          │   - Tactical Pitch Visualizer     │
                                          │   - Live Match Simulator Engine   │
                                          └───────────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Run the Alexa+ MCP Server Backend
```bash
cd mcp_server
pip install fastapi uvicorn
python server.py
```
*Server starts at `http://localhost:8000` exposing official MCP endpoints (`/mcp`).*

### 2. Launch the Fire TV Dashboard Frontend
Open `firetv_app/index.html` in any web browser or Fire OS / Vega OS webview simulator.

---

## 📄 Friction Log Included
See `FRICTION_LOG.md` for detailed developer feedback regarding MCP schema validation, Fire OS webview performance, and cross-device sync. Submitting this feedback grants **up to a 10% bonus** on the final judging score!
