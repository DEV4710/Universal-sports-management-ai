// UNIVERSAL SPORTS MANAGER AI (v4 Realism Engine)
const API_BASE = "http://localhost:8000";

let currentSport = "cricket";
let currentStage = "auctionStage";

document.addEventListener("DOMContentLoaded", () => {
  fetchGameState();
  setInterval(fetchGameState, 2500); // Poll for live voice state updates
});

async function fetchGameState() {
  try {
    const res = await fetch(`${API_BASE}/api/state`);
    const state = await res.json();
    renderState(state);
  } catch (err) {
    console.warn("MCP Server offline or loading...", err);
  }
}

function renderState(state) {
  // Update Header / Sport Theme
  document.body.className = `theme-${state.sport}`;
  currentSport = state.sport;

  // User Club Info
  const userTeam = state.teams.find(t => t.is_user) || { name: "User Club", budget: 100 };
  document.getElementById("userTeamTitle").textContent = userTeam.name.toUpperCase();
  document.getElementById("managerName").textContent = `Manager: ${state.user_manager_name}`;
  document.getElementById("userBudgetValue").textContent = `${state.currency_symbol}${userTeam.budget} ${state.currency_unit}`;

  // League Standings Table
  document.getElementById("leagueTitle").textContent = `${state.sport.toUpperCase()} LEAGUE STANDINGS`;
  document.getElementById("matchdayBadge").textContent = `MD ${state.match_day}/${state.total_match_days}`;
  
  const standingsBody = document.getElementById("standingsBody");
  standingsBody.innerHTML = "";
  state.league_standings.forEach((team, idx) => {
    const tr = document.createElement("tr");
    if (team.is_user) tr.className = "user-row";
    tr.innerHTML = `
      <td>${idx + 1}</td>
      <td>${team.name}</td>
      <td>${team.played}</td>
      <td>${team.won}</td>
      <td>${team.lost}</td>
      <td><strong>${team.points}</strong></td>
    `;
    standingsBody.appendChild(tr);
  });

  // Current Lot Stage
  const player = state.current_player;
  if (player && state.auction_status === "active") {
    document.getElementById("lotNumber").textContent = `LOT #${state.current_player_index + 1}`;
    document.getElementById("playerRole").textContent = player.role.toUpperCase();
    document.getElementById("playerName").textContent = player.name;
    document.getElementById("playerStats").textContent = player.stats;
    document.getElementById("playerRating").textContent = player.rating;
    document.getElementById("playerValuation").textContent = `${state.currency_symbol}${player.valuation} ${state.currency_unit}`;
    
    document.getElementById("currentBidPrice").textContent = `${state.currency_symbol}${state.current_bid} ${state.currency_unit}`;
    document.getElementById("highestBidderName").textContent = state.highest_bidder_name;
    
    // Avatar emoji by sport
    const avatar = state.sport === "cricket" ? "🏏" : (state.sport === "football" ? "⚽" : "🏀");
    document.getElementById("playerAvatar").textContent = avatar;
  } else if (state.auction_status === "finished") {
    document.getElementById("playerName").textContent = "Auction Concluded!";
    document.getElementById("playerStats").textContent = "All lots have been processed for the upcoming season.";
  }

  // Logs
  const logStream = document.getElementById("auctionLogStream");
  logStream.innerHTML = "";
  state.auction_logs.forEach(log => {
    const item = document.createElement("div");
    item.className = "log-item";
    item.textContent = log;
    logStream.appendChild(item);
  });

  // Match Simulator
  document.getElementById("matchSportTag").textContent = `${state.sport.toUpperCase()} MATCH DAY`;
  if (state.last_match_result) {
    document.getElementById("matchResultBanner").textContent = state.last_match_result;
  }

  // Squad / Tactical Board
  document.getElementById("formationText").textContent = state.formation;
  const rosterList = document.getElementById("rosterList");
  rosterList.innerHTML = "";
  if (userTeam.roster && userTeam.roster.length > 0) {
    userTeam.roster.forEach(p => {
      const item = document.createElement("div");
      item.className = "roster-item";
      item.innerHTML = `<span><strong>${p.name}</strong> (${p.role})</span><span>OVR ${p.rating}</span>`;
      rosterList.appendChild(item);
    });
  } else {
    rosterList.innerHTML = `<p style="color:#8b949e; grid-column:span 2;">No players acquired yet. Win player bids in the Auction stage!</p>`;
  }
}

// ACTION HANDLERS
async function switchSportMode(sport) {
  const teamMap = { cricket: "rcb", football: "rca", basketball: "lak" };
  await callMcpTool("start_career_session", {
    sport: sport,
    user_team_id: teamMap[sport],
    manager_name: "Manager Alexa"
  });
  
  document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
  event.target.classList.add("active");
  fetchGameState();
}

function showStage(stageId) {
  document.querySelectorAll(".stage-container").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".toggle-btn").forEach(btn => btn.classList.remove("active"));
  
  document.getElementById(stageId).classList.add("active");
  event.target.classList.add("active");
  currentStage = stageId;
}

async function userPlaceBid() {
  await callMcpTool("place_user_bid", {});
  fetchGameState();
}

async function triggerAiBidStep() {
  await callMcpTool("trigger_ai_bid_step", {});
  fetchGameState();
}

async function finalizeLot() {
  await callMcpTool("finalize_current_lot", {});
  fetchGameState();
}

async function simulateMatchDay() {
  await callMcpTool("simulate_match_day", {});
  fetchGameState();
}

async function updateTactics() {
  const tactics = document.getElementById("tacticsSelect").value;
  await callMcpTool("set_tactics", { tactics: tactics });
  fetchGameState();
}

async function callMcpTool(name, args) {
  try {
    await fetch(`${API_BASE}/mcp`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: Date.now(),
        method: "tools/call",
        params: { name: name, arguments: args }
      })
    });
  } catch (err) {
    console.error("Tool execution failed:", err);
  }
}
