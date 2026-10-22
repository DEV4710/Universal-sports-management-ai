# Universal Sports Manager AI: Alexa+ & Fire TV (FC / NBA / IPL)

> **Amazon Developer Hackathon 2026 Submission**  
> *Target Tracks: Alexa+ Track & Fire TV Track*

Universal Sports Manager AI transforms your living room television into an interactive, multi-sport management and drafting game. Combining **Alexa+ AI Agent Skills / MCP (`2025-11-25`)** with a **10-foot Fire TV UI (Fire OS & Vega OS)**, players can experience **IPL Cricket Auctions**, **Premier League Football Transfer Windows**, and **NBA Draft War Rooms** using natural voice commands.

---

## 🌟 Key Features Across All 3 Sports

1. **🏏 Cricket (IPL Live Auction)**:
   * Real-time voice bidding against AI rival club owners.
   * Big-screen TV auction stage displaying player ratings, career statistics, and live bid logs.

2. **⚽ Football (FC 27 Transfer Window)**:
   * Negotiate player transfers (Erling Haaland, Jude Bellingham, Kylian Mbappé), release clauses, and weekly wages via voice.
   * Interactive 4-3-3 squad builder pitch and tactical formation overlay.

3. **🏀 Basketball (NBA Draft & Free Agency)**:
   * Select rookie draft picks (Victor Wembanyama, Cooper Flagg) or sign free agents in the NBA Draft War Room.
   * Manage salary cap space and 5-on-5 court lineups.

4. **🏰 Club Management & Facilities**:
   * Expand stadium capacity, upgrade training complexes, invest in youth academies, and boost team morale.

5. **🎙️ Real-Time Match Simulation Engine**:
   * Simulate full matches with AI-generated voice commentary based on your tactical choices.

---

## 🏗️ Architecture

```
┌─────────────────────────┐               ┌─────────────────────────────────┐
│     Fire TV Display     │               │        Alexa+ AI Agent          │
│   (Fire OS / Vega OS)   │               │     Model Context Protocol      │
│                         │               │          (MCP 2025-11-25)       │
│  • 10-Foot Big Screen   │  JSON-RPC 2.0 │  • Voice Bidding Engine         │
│  • Squad & Pitch UI     │ <───────────> │  • Transfer Negotiator          │
│  • Auction & Draft Stage│   HTTP / WS   │  • Tactical Match Simulator     │
│  • Facility Management  │               │  • Player Database (JSON)       │
└─────────────────────────┘               └─────────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Launch the Alexa+ MCP Server
```bash
cd mcp_server
python3 -m venv venv && source venv/bin/activate
pip install fastapi uvicorn
python3 server.py
```
*MCP Server runs on `http://localhost:8000/mcp`.*

### 2. Launch the Fire TV App
Open `firetv_app/index.html` in any browser or load it directly into the Fire TV Webview / Simulator.

---

## 📁 Repository Structure
```
sports_manager_ai_v2/
├── mcp_server/
│   ├── server.py               # FastAPi MCP (2025-11-25) JSON-RPC 2.0 Endpoint
│   └── player_database.json    # Multi-Sport Database (Cricket, Football, Basketball)
├── firetv_app/
│   ├── index.html              # Fire TV 10-foot Big Screen Dashboard
│   ├── styles.css              # Dark Glassmorphism TV CSS
│   └── app.js                  # Client State & MCP Polling Logic
├── FRICTION_LOG.md             # Developer Feedback for Amazon Engineering (+10% Bonus)
└── README.md                   # Hackathon Documentation & Video Script
```
