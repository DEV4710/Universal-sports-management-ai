const API_URL = "http://localhost:8000";

let currentSport = "cricket";
let currentData = null;

async function fetchState() {
  try {
    const res = await fetch(`${API_URL}/state`);
    const data = await res.json();
    currentData = data;
    renderUI(data);
  } catch (err) {
    console.log("MCP Server polling offline or standalone mode.", err);
  }
}

function switchSport(sport) {
  currentSport = sport;
  document.querySelectorAll('.sport-btn').forEach(btn => btn.classList.remove('active'));
  document.getElementById(`btn-${sport}`).classList.add('active');

  // Trigger MCP switch
  callMCP("select_sport_and_mode", { sport: sport });
}

async function callMCP(toolName, args) {
  try {
    const res = await fetch(`${API_URL}/mcp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        id: Date.now(),
        method: 'tools/call',
        params: { name: toolName, arguments: args }
      })
    });
    const result = await res.json();
    fetchState();
  } catch (err) {
    console.error("MCP Call error:", err);
  }
}

function triggerAction(type) {
  if (type === 'bid') {
    if (!currentData || !currentData.available_players.length) return;
    const player = currentData.available_players[0];
    const amount = currentSport === 'cricket' ? 5.0 : currentSport === 'football' ? 120.0 : 15.0;
    callMCP("execute_player_acquisition", {
      player_name: player.name,
      offer_amount: amount,
      action_type: currentSport === 'cricket' ? 'bid' : currentSport === 'football' ? 'negotiate' : 'draft_pick'
    });
  } else if (type === 'sim_match') {
    callMCP("simulate_full_match", { opponent_team: "Global Stars XI" });
  }
}

function renderUI(data) {
  const state = data.state;
  const players = data.available_players;

  // Top Nav
  document.getElementById('ui-team-name').innerText = state.user_team_name;
  document.getElementById('ui-budget').innerText = `${state.currency_symbol}${state.budget.toFixed(1)}${state.currency_unit}`;

  // Market
  const marketTitle = document.getElementById('market-title');
  if (state.active_sport === 'cricket') marketTitle.innerText = "🔥 IPL LIVE AUCTION STAGE";
  else if (state.active_sport === 'football') marketTitle.innerText = "⚽ FOOTBALL TRANSFER WINDOW";
  else marketTitle.innerText = "🏀 NBA DRAFT WAR ROOM";

  if (players && players.length > 0) {
    const topP = players[0];
    document.getElementById('p-avatar').innerText = state.active_sport === 'cricket' ? '🏏' : state.active_sport === 'football' ? '⚽' : '🏀';
    document.getElementById('p-name').innerText = topP.name;
    document.getElementById('p-role').innerText = `${topP.role} • Rating: ${topP.rating}`;
    document.getElementById('p-price').innerText = `${state.currency_symbol}${topP.base_price_cr || topP.market_value_m || topP.salary_m}${state.currency_unit}`;
    
    // Pool list
    const poolEl = document.getElementById('pool-list');
    poolEl.innerHTML = players.map(p => `
      <div class="pool-item">
        <div>
          <div class="pool-item-name">${p.name}</div>
          <div class="pool-item-role">${p.role}</div>
        </div>
        <div class="pool-item-val">${state.currency_symbol}${p.base_price_cr || p.market_value_m || p.salary_m}${state.currency_unit}</div>
      </div>
    `).join('');
  }

  // Squad Pitch
  document.getElementById('ui-formation').innerText = state.tactics.formation;
  document.getElementById('ui-style').innerText = state.tactics.style;
  const squadGrid = document.getElementById('squad-grid');
  if (state.user_roster && state.user_roster.length > 0) {
    squadGrid.innerHTML = state.user_roster.map(p => `<div class="squad-chip">⭐ ${p.name} (${p.role})</div>`).join('');
  } else {
    squadGrid.innerHTML = `<div class="empty-squad-msg">No players signed yet. Use Alexa+ Voice commands to bid or sign players!</div>`;
  }

  // Facilities
  document.getElementById('ui-stadium').innerText = `${state.club_facilities.stadium_capacity.toLocaleString()} Seats`;
  document.getElementById('ui-training').innerText = state.club_facilities.training_level;
  document.getElementById('ui-youth').innerText = state.club_facilities.youth_academy;
  document.getElementById('ui-morale').innerText = state.club_facilities.morale;

  // Logs
  const logEl = document.getElementById('voice-logs');
  logEl.innerHTML = state.recent_logs.slice().reverse().map(l => `<div class="log-entry">${l}</div>`).join('');
}

// Poll state every 2s
setInterval(fetchState, 2000);
fetchState();
