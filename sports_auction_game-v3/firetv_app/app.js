/* ==========================================================================
   SPORTS MANAGER AI 2026 - FIRE TV & ALEXA+ APPLICATION SCRIPT
   ========================================================================== */

const MCP_ENDPOINT = 'http://localhost:8000';

let state = {
    sport: 'cricket',
    manager_name: 'Coach Alexa',
    difficulty: 'Tactical AI (Hard)',
    selected_team: null,
    squad: [],
    auction_pool: [],
    current_lot_index: 0,
    current_bid: 2.0,
    highest_bidder: 'Base Price',
    bidding_logs: [],
    current_matchday: 1,
    total_matchdays: 14,
    match_active: false,
    standings: []
};

// Database copy
const SPORTS_DATA = {
    cricket: {
        title: "IPL CRICKET MEGA AUCTION",
        currency: "₹",
        unit: "Cr",
        total_matchdays: 14,
        teams: [
            { id: "rcb", name: "Royal Challengers Alexa", budget: 100.0, rating: 88 },
            { id: "mi", name: "Mumbai AI", budget: 95.0, rating: 91 },
            { id: "csk", name: "Chennai Super Kings", budget: 90.0, rating: 90 },
            { id: "kkr", name: "Kolkata Knight Riders", budget: 98.0, rating: 87 }
        ],
        players: [
            { id: "c1", name: "Jasprit Bumrah", role: "Fast Bowler", rating: 96, base_price: 2.0, icon: "⚡" },
            { id: "c2", name: "Virat Kohli", role: "Top-Order Batter", rating: 95, base_price: 2.0, icon: "👑" },
            { id: "c3", name: "Heinrich Klaasen", role: "Wicketkeeper Batter", rating: 92, base_price: 2.0, icon: "💥" },
            { id: "c4", name: "Rashid Khan", role: "Leg-Spin All-Rounder", rating: 94, base_price: 2.0, icon: "🌀" }
        ]
    },
    football: {
        title: "PREMIER LEAGUE & CHAMPIONS CUP",
        currency: "€",
        unit: "M",
        total_matchdays: 38,
        teams: [
            { id: "mci", name: "Manchester City", budget: 220.0, rating: 92 },
            { id: "rma", name: "Real Madrid", budget: 250.0, rating: 94 },
            { id: "ars", name: "Arsenal Alexa FC", budget: 180.0, rating: 89 },
            { id: "bar", name: "FC Barcelona", budget: 160.0, rating: 90 }
        ],
        players: [
            { id: "f1", name: "Erling Haaland", role: "Striker (ST)", rating: 94, base_price: 150.0, icon: "🤖" },
            { id: "f2", name: "Jude Bellingham", role: "Central Midfielder", rating: 93, base_price: 140.0, icon: "🌟" },
            { id: "f3", name: "Kylian Mbappé", role: "Left Winger", rating: 95, base_price: 180.0, icon: "⚡" },
            { id: "f4", name: "Lamine Yamal", role: "Right Winger", rating: 89, base_price: 110.0, icon: "💎" }
        ]
    },
    basketball: {
        title: "NBA DRAFT & FREE AGENCY",
        currency: "$",
        unit: "M",
        total_matchdays: 82,
        teams: [
            { id: "lal", name: "LA Lakers", budget: 140.0, rating: 89 },
            { id: "bos", name: "Boston Celtics", budget: 145.0, rating: 93 },
            { id: "gsw", name: "Golden State Warriors", budget: 150.0, rating: 88 },
            { id: "dal", name: "Dallas Mavericks", budget: 135.0, rating: 90 }
        ],
        players: [
            { id: "b1", name: "Victor Wembanyama", role: "Center (C)", rating: 93, base_price: 30.0, icon: "👽" },
            { id: "b2", name: "Luka Dončić", role: "Point Guard (PG)", rating: 94, base_price: 38.0, icon: "🪄" },
            { id: "b3", name: "Shai Gilgeous-Alexander", role: "Shooting Guard", rating: 92, base_price: 35.0, icon: "🎯" }
        ]
    }
};

document.addEventListener('DOMContentLoaded', () => {
    console.log("Sports Manager AI 2026 Engine Ready.");
    checkMCPConnection();
});

// NAVIGATION
function navigateTo(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    const target = document.getElementById(screenId);
    if (target) target.classList.add('active');
}

// SPORT SELECT
function selectSport(sportKey) {
    state.sport = sportKey;
    const data = SPORTS_DATA[sportKey];
    state.total_matchdays = data.total_matchdays;
    state.auction_pool = [...data.players];

    document.getElementById('team-select-title').innerText = `SELECT YOUR ${data.title} CLUB`;
    renderTeamSelectionGrid();
    navigateTo('screen-team-select');
}

function renderTeamSelectionGrid() {
    const grid = document.getElementById('team-cards-list');
    grid.innerHTML = '';
    const teams = SPORTS_DATA[state.sport].teams;
    state.selected_team = teams[0];

    teams.forEach((t, index) => {
        const card = document.createElement('div');
        card.className = `team-option-card tv-focusable ${index === 0 ? 'selected' : ''}`;
        card.innerHTML = `
            <h3>${t.name}</h3>
            <p>Rating: <strong>${t.rating} OVERALL</strong></p>
            <p>Budget: <strong>${SPORTS_DATA[state.sport].currency}${t.budget} ${SPORTS_DATA[state.sport].unit}</strong></p>
        `;
        card.onclick = () => {
            document.querySelectorAll('.team-option-card').forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            state.selected_team = t;
        };
        grid.appendChild(card);
    });
}

function confirmTeamSetup() {
    const mgrName = document.getElementById('manager-name-input').value;
    if (mgrName) state.manager_name = mgrName;

    // Build Initial Standings
    const teams = SPORTS_DATA[state.sport].teams;
    state.standings = teams.map(t => ({
        team: t.name, played: 0, won: 0, lost: 0, pts: 0
    }));

    // Update Hub Displays
    document.getElementById('hub-manager-name').innerText = state.manager_name;
    document.getElementById('hub-team-name').innerText = state.selected_team.name;
    document.getElementById('hub-budget-val').innerText = `${SPORTS_DATA[state.sport].currency}${state.selected_team.budget} ${SPORTS_DATA[state.sport].unit}`;
    document.getElementById('hub-total-matchdays').innerText = state.total_matchdays;

    document.getElementById('fix-home-name').innerText = state.selected_team.name;
    const awayOpp = teams.find(t => t.name !== state.selected_team.name) || teams[1];
    document.getElementById('fix-away-name').innerText = awayOpp.name;

    // Initialize Acquisition Spotlight
    setupAcquisitionStage();
    renderTacticalPitch();
    renderStandingsTable();

    navigateTo('screen-hub');
    showVoiceBanner(`Career initialized for ${state.manager_name} managing ${state.selected_team.name}!`);
}

// HUB TABS
function showHubTab(tabId) {
    document.querySelectorAll('.hub-tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

    const targetTab = document.getElementById(tabId);
    if (targetTab) targetTab.classList.add('active');

    const btn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tabId));
    if (btn) btn.classList.add('active');
}

// ACQUISITION / AUCTION
function setupAcquisitionStage() {
    if (state.auction_pool.length === 0) return;
    const currPlayer = state.auction_pool[state.current_lot_index];

    document.getElementById('acq-player-name').innerText = currPlayer.name;
    document.getElementById('acq-player-role').innerText = `${currPlayer.role} • ${SPORTS_DATA[state.sport].title}`;
    document.getElementById('acq-player-avatar').innerText = currPlayer.icon;
    document.getElementById('acq-stat-rating').innerText = currPlayer.rating;

    state.current_bid = currPlayer.base_price;
    state.highest_bidder = "Base Price";

    document.getElementById('acq-curr-bid').innerText = `${SPORTS_DATA[state.sport].currency}${state.current_bid} ${SPORTS_DATA[state.sport].unit}`;
    document.getElementById('acq-curr-bidder').innerText = state.highest_bidder;
}

function placeVoiceBid(increment) {
    const newBid = Math.round((state.current_bid + increment) * 10) / 10;
    if (newBid > state.selected_team.budget) {
        showVoiceBanner("Bid rejected: Insufficient club budget!");
        return;
    }

    state.current_bid = newBid;
    state.highest_bidder = state.selected_team.name;

    document.getElementById('acq-curr-bid').innerText = `${SPORTS_DATA[state.sport].currency}${state.current_bid} ${SPORTS_DATA[state.sport].unit}`;
    document.getElementById('acq-curr-bidder').innerText = state.highest_bidder;

    addBidLog(`🗣️ ${state.manager_name} bid ${SPORTS_DATA[state.sport].currency}${newBid} ${SPORTS_DATA[state.sport].unit}`);

    // AI Counter Bid
    setTimeout(() => {
        if (Math.random() > 0.3) {
            const aiCounter = Math.round((newBid + 0.5) * 10) / 10;
            state.current_bid = aiCounter;
            state.highest_bidder = "Mumbai AI Rival";
            document.getElementById('acq-curr-bid').innerText = `${SPORTS_DATA[state.sport].currency}${aiCounter} ${SPORTS_DATA[state.sport].unit}`;
            document.getElementById('acq-curr-bidder').innerText = state.highest_bidder;
            addBidLog(`🤖 Mumbai AI countered with ${SPORTS_DATA[state.sport].currency}${aiCounter} ${SPORTS_DATA[state.sport].unit}`);
            showVoiceBanner(`AI Rival outbid you with ${SPORTS_DATA[state.sport].currency}${aiCounter}!`);
        }
    }, 1200);
}

function addBidLog(msg) {
    const container = document.getElementById('bidding-logs-container');
    const entry = document.createElement('p');
    entry.className = 'log-entry';
    entry.innerText = msg;
    container.prepend(entry);
}

function signCurrentPlayer() {
    if (state.highest_bidder !== state.selected_team.name) {
        showVoiceBanner("You do not hold the highest bid!");
        return;
    }

    const player = state.auction_pool[state.current_lot_index];
    state.selected_team.budget -= state.current_bid;
    state.selected_team.budget = Math.round(state.selected_team.budget * 10) / 10;
    state.squad.push(player);

    document.getElementById('hub-budget-val').innerText = `${SPORTS_DATA[state.sport].currency}${state.selected_team.budget} ${SPORTS_DATA[state.sport].unit}`;
    showVoiceBanner(`🎉 SOLD! ${player.name} signed to ${state.selected_team.name}!`);
    addBidLog(`✨ OFFICIAL: ${player.name} signed for ${SPORTS_DATA[state.sport].currency}${state.current_bid} ${SPORTS_DATA[state.sport].unit}`);

    renderTacticalPitch();
}

// TACTICS
function renderTacticalPitch() {
    const field = document.getElementById('tactical-field');
    field.innerHTML = '';

    const roster = document.getElementById('squad-list-container');
    roster.innerHTML = '';

    if (state.squad.length === 0) {
        field.innerHTML = `<p style="color:#a0aec0; text-align:center;">No squad players signed yet. Head to Market/Auction to acquire players!</p>`;
        return;
    }

    state.squad.forEach((p, idx) => {
        const node = document.createElement('div');
        node.style.cssText = `background: rgba(0,255,136,0.2); border: 2px solid #00ff88; padding: 10px 16px; border-radius: 20px; font-weight:800; text-align:center; color:#fff;`;
        node.innerHTML = `${p.icon} ${p.name}<br><small style="color:#00e5ff">${p.role}</small>`;
        field.appendChild(node);

        const card = document.createElement('div');
        card.className = 'roster-card';
        card.innerHTML = `<span>${p.icon} <strong>${p.name}</strong> (${p.role})</span><span style="color:#ffd700">RATING ${p.rating}</span>`;
        roster.appendChild(card);
    });
}

// MATCH SIMULATOR
function startMatchSimulation() {
    if (state.match_active) return;
    state.match_active = true;

    const commBox = document.getElementById('match-commentary-box');
    commBox.innerHTML = '';

    document.getElementById('sim-home-name').innerText = state.selected_team.name;
    document.getElementById('sim-away-name').innerText = "Mumbai AI";

    let mins = 0;
    let homeScore = 0;
    let awayScore = 0;

    const timer = setInterval(() => {
        mins += 15;
        document.getElementById('sim-match-time').innerText = `${mins}'`;

        if (Math.random() > 0.6) {
            homeScore += 1;
            document.getElementById('sim-home-score').innerText = homeScore;
            addCommentary(`⚽ GOAL! ${state.selected_team.name} scores in the ${mins}' minute!`);
        } else if (Math.random() > 0.7) {
            awayScore += 1;
            document.getElementById('sim-away-score').innerText = awayScore;
            addCommentary(`🚨 GOAL! Mumbai AI scores in the ${mins}' minute!`);
        } else {
            addCommentary(`⏱️ ${mins}' - Solid tactical play in midfield.`);
        }

        if (mins >= 90) {
            clearInterval(timer);
            state.match_active = false;
            document.getElementById('sim-match-status').innerText = "FULL TIME";
            addCommentary(`🏆 FULL TIME RESULT: ${state.selected_team.name} ${homeScore} - ${awayScore} Mumbai AI`);

            // Update Standings
            const userTeam = state.standings.find(s => s.team === state.selected_team.name);
            if (userTeam) {
                userTeam.played += 1;
                if (homeScore > awayScore) { userTeam.won += 1; userTeam.pts += 3; }
                else if (homeScore === awayScore) { userTeam.pts += 1; }
                else { userTeam.lost += 1; }
            }
            renderStandingsTable();
        }
    }, 1000);
}

function addCommentary(line) {
    const box = document.getElementById('match-commentary-box');
    const p = document.createElement('p');
    p.className = 'comm-line';
    p.innerText = line;
    box.prepend(p);
}

function sendVoiceTacticalCommand(mentality) {
    showVoiceBanner(`Tactics set to: ${mentality} Mentality via Alexa+ Voice`);
    addCommentary(`🗣️ VOICE COMMAND EXECUTION: Team shifted to ${mentality} mentality.`);
}

// STANDINGS
function renderStandingsTable() {
    const tbody = document.getElementById('standings-tbody');
    tbody.innerHTML = '';

    state.standings.sort((a,b) => b.pts - a.pts).forEach((s, idx) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>#${idx + 1}</td>
            <td><strong>${s.team}</strong></td>
            <td>${s.played}</td>
            <td>${s.won}</td>
            <td>${s.lost}</td>
            <td><strong style="color:#00ff88">${s.pts} PTS</strong></td>
        `;
        tbody.appendChild(tr);
    });
}

function showVoiceBanner(msg) {
    document.getElementById('voice-status-text').innerText = msg;
}

function checkMCPConnection() {
    fetch(`${MCP_ENDPOINT}/state`)
        .then(res => res.json())
        .then(data => {
            console.log("Connected to local MCP Server:", data);
        })
        .catch(() => {
            console.log("MCP Server offline or standalone browser mode active.");
        });
}
