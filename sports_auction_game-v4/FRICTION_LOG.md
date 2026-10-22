# Amazon Developer Hackathon 2026 - Friction Log & Feedback
**Project**: Universal Sports Manager AI (v4 Realism Engine)
**Track Focus**: Fire TV + Alexa+ Integration

---

## 🚀 Overview & Developer Journey
We built an ambitious, multi-device **Universal Sports Manager Career Engine** combining **Alexa+** (backend Model Context Protocol server over FastAPI) and **Fire TV** (10-foot webview interface designed for Fire OS and Vega OS). The application spans **IPL Cricket Mega Auctions**, **Premier League Transfer Markets**, and **NBA Salary Cap Drafts**.

Below are critical technical observations, friction points, and recommendations identified during developer integration.

---

## 🛠️ Key Friction Points & Recommendations

### 1. Multi-Sport MCP Tool Schema State Synchronization
* **Friction**: Synchronizing real-time voice bids across multiple distinct sports rulesets (Cricket IPL Lakh/Crore vs. Football Millions vs. NBA Cap Space) required custom state machine schemas. When voice commands like *"Alexa, bid ₹15 Crore on Jasprit Bumrah"* are issued, parsing regional currency units and mapping them to dynamic AI rival bids exposed a lack of native sport-specific schema primitives in standard MCP tool templates.
* **Recommendation**: Introduce pre-built Amazon Developer SDK intent templates for voice-driven auction events, live bidding timers, and currency formatting.

### 2. Fire TV Webview CORS & Local Server Communication
* **Friction**: When testing the Fire TV UI (`index.html`) communicating with a local MCP server (`http://localhost:8000/mcp`), strict CORS policies on Fire OS and Vega OS webview instances caused silent connection drops unless explicit middleware headers (`Access-Control-Allow-Origin: *`) were configured on both sides.
* **Recommendation**: Include default CORS configurations and local webview debug logging flags in official Fire TV React Native and HTML5 starter kits.

### 3. Real-Time AI Rival State Latency
* **Friction**: In a fast-paced live auction room, simulating multiple AI team owners evaluating player market valuations and counter-bidding in under 500ms required careful async handler management in Python FastAPI.
* **Recommendation**: Offer native Amazon Bedrock or AgentCore streaming event bus integration guidelines specifically for low-latency multi-agent gaming scenarios.

---

## 🏆 Scoring Bonus Claim
This Friction Log provides actionable engineering feedback for Amazon Developer teams and claims the **+10% score bonus** for the Hackathon judging process.
