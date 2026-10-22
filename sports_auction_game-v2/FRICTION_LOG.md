# Amazon Developer Hackathon 2026: Friction Log & Product Feedback

**Developer/Team:** Universal Sports Manager AI
**Project:** Alexa+ & Fire TV Cross-Device Sports Manager (Cricket IPL, Football Transfer, NBA Draft)
**Target Tracks:** Fire TV Track & Alexa+ Track

---

## Executive Summary
Building a multi-device voice application that connects a self-hosted Model Context Protocol (MCP) server running on Alexa+ with a 10-foot Fire TV UI revealed key friction points across schema validation, CORS setup in Fire OS Webview environments, and state synchronization latency. Submitting this friction log provides direct feedback for Amazon's developer platform teams.

---

## Top Friction Points & Suggestions

### 1. Alexa+ MCP Specification (`2025-11-25`) Tool Argument Coercion
* **Issue**: When passing numeric parameters (such as bid amounts or budget offers e.g. `12.5` or `180`), the current Alexa+ Agent Skill parser occasionally coerces float values into raw strings (e.g. `"12.5"`).
* **Workaround**: We implemented strict type checking and string-to-float fallback parsing inside the FastAPI JSON-RPC handler in `server.py`.
* **Recommendation**: Enhance the Alexa+ MCP client library to strictly enforce OpenAPI `type: "number"` definitions before payload dispatch.

### 2. Fire OS Webview CORS & Local Loopback Latency
* **Issue**: When testing the Fire TV web application on Fire OS / Vega OS simulators pointing to a local loopback MCP endpoint (`http://localhost:8000`), aggressive origin restrictions in Webview required explicit wildcards (`CORSMiddleware`).
* **Recommendation**: Include a pre-configured local development CORS template in the official Amazon Fire TV React Native & Web SDK starter repositories.

### 3. Multi-Device Real-Time State Synchronization
* **Issue**: When an Alexa+ voice tool call updates the game state (e.g., executing an IPL bid or an NBA draft pick), sending the state update back to the Fire TV interface over HTTP polling created a ~1.5s visual lag between spoken confirmation and visual rendering.
* **Workaround**: Implemented 2000ms polling with optimistic UI rendering on the Fire TV app.
* **Recommendation**: Introduce native WebSockets or SSE (Server-Sent Events) support within the official Alexa+ MCP SDK to stream real-time state changes directly to Fire TV webviews.

---

## Positive Highlights
* **MCP Streamable HTTP Standard**: The 2025-11-25 MCP spec over Streamable HTTP makes it exceptionally easy to host custom AI tools using standard Python FastAPI servers.
* **Fire TV 10-Foot Design System**: CSS backdrop-filters and flexbox layouts render smoothly at 60 FPS on Vega OS and Fire OS simulators.
