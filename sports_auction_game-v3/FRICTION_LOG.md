# FRICTION LOG — Amazon Developer Hackathon 2026
**Project**: Universal Sports Manager AI 2026  
**Categories Targeted**: Fire TV Track & Alexa+ Track  
**Developer**: Hackathon Participant  

---

## Executive Summary
This Friction Log provides detailed, field-tested developer feedback gathered during the development of **Universal Sports Manager AI 2026**—a voice-driven multi-sport career mode game built for **Fire OS / Vega OS** and powered by an **Alexa+ Model Context Protocol (MCP) server (`2025-11-25`)**.

Our feedback focuses on three primary areas:
1. **Alexa+ Model Context Protocol (MCP) Tool Calling Latency & Schema Validation**
2. **Fire TV Webview Performance & 10-Foot Spatial Focus Trapping**
3. **Cross-Device State Synchronization between Alexa+ Background Workers and Fire OS Web Content**

---

## 1. Alexa+ MCP Server Integration Feedback

### Issue 1.1: Streamable HTTP Transport Initialization Handshake
* **Observation**: When running an MCP server implementing spec `2025-11-25` over Streamable HTTP, the initial `initialize` handshake requires a strict JSON-RPC 2.0 wrapper.
* **Friction**: The documentation does not clearly specify whether tool response schemas should wrap state updates inside the `result.content` text list or alongside top-level keys.
* **Recommendation**: Provide an official Python/Node SDK decorator (e.g., `@alexa_mcp.tool()`) that automatically handles JSON-RPC 2.0 framing and CORS headers for local testing.

### Issue 1.2: Voice Bidding & Decimal Parameter Parsing
* **Observation**: In the IPL Auction mode, users say currency values in Indian Rupees Crore (e.g., *"₹12.5 Crore"*).
* **Friction**: Natural language entity extraction sometimes converts "12.5 Crore" into raw integer `12` or string `"12.5"`.
* **Recommendation**: Add standardized voice slots for currency units (`AMAZON.CurrencyRupeesCr`, `AMAZON.CurrencyEurosM`, `AMAZON.CurrencyUSD`) in the Alexa+ Agent Skill builder.

---

## 2. Fire TV 10-Foot UI & Webview Rendering Feedback

### Issue 2.1: Spatial Focus Trapping in Glassmorphic Dashboards
* **Observation**: Fire TV remote D-Pad navigation requires clear visual focus indicators on interactive elements (`.tv-focusable`).
* **Friction**: Standard CSS `:focus` pseudo-classes can lose focus when dynamic DOM changes occur (such as switching tabs or updating bid tickers).
* **Recommendation**: Include a lightweight spatial navigation helper script (`amazon-tv-spatial-nav.js`) in the official Fire TV Web app starter template.

---

## 3. Real-Time Cross-Device Synchronization

### Recommendation
Implement an official WebSocket or Server-Sent Events (SSE) bridge between Alexa+ agent events and Fire OS app contexts to enable instant <100ms visual updates on television screens when voice commands are recognized.
