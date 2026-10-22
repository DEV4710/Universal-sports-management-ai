# 🏆 Universal Sports Manager AI (v4 Realism Engine)
> **Voice-Driven Multi-Sport Career & Auction Game for Fire TV & Alexa+**

---

## 🌟 Features

* **🏏 IPL Cricket Career Mode**: Real-time IPL Mega Auction with AI rival team owners, Lakh/Crore bidding, 14-match IPL season simulation, and live points standings.
* **⚽ Football Manager Career Mode**: Premier League & European transfer markets, 4-3-3 / 3-5-2 tactical board, 38-match league schedule, and matchday simulator.
* **🏀 NBA Draft & Free Agency**: NBA Salary Cap free agency, 82-game season simulation, and real-time team stats.
* **🤖 Alexa+ MCP Server (`2025-11-25` Spec)**: Model Context Protocol backend enabling voice bids (*"Alexa, bid ₹15 Crore on Jasprit Bumrah"*), tactical formation adjustments, and match commentary.
* **📺 Fire TV 10-Foot Dashboard**: Dark-mode TV interface optimized for Fire OS and Vega OS.

---

## 🛠️ Quick Start Guide

### 1. Start the Alexa+ MCP Backend Server
```bash
cd mcp_server
pip install fastapi uvicorn
python server.py
```
*Server runs on `http://localhost:8000`*

### 2. Launch the Fire TV Interface
Open `firetv_app/index.html` directly in any browser or Fire TV webview simulator, or host with Python:
```bash
python -m http.server 3000 --directory firetv_app
```
*Navigate to `http://localhost:3000`*

---

## 📂 Project Structure
```
sports_manager_ai_v4/
├── mcp_server/
│   ├── server.py             # FastAPI MCP Server (2025-11-25 Spec)
│   └── player_database.json  # Real-world player stats, valuations & teams
├── firetv_app/
│   ├── index.html            # 10-foot Fire TV Interface
│   ├── styles.css            # Sport-specific glassmorphism theme styles
│   └── app.js                # State sync, voice actions & live ticker
├── FRICTION_LOG.md           # Amazon Developer Feedback (+10% Score Bonus)
└── README.md                 # Documentation
```
