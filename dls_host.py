<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DLS Ultra Manager - Battle Royale</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Teko:wght@300;500;700&family=Rajdhani:wght@500;700&display=swap');

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background-color: #09090b;
            background-image: radial-gradient(circle at 50% 0%, #111827 0%, transparent 80%);
            color: white;
            font-family: 'Rajdhani', sans-serif;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        h1, h2, h3 {
            font-family: 'Teko', sans-serif;
            text-transform: uppercase;
            margin: 0;
        }

        .big-title {
            font-size: 4rem;
            font-weight: 700;
            text-align: center;
            background: linear-gradient(180deg, #fff 0%, #64748b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(59, 130, 246, 0.3);
            margin-bottom: 20px;
        }

        .glass-panel {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            backdrop-filter: blur(10px);
        }

        .phase-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-left: 10px;
        }

        .phase-1 { background: #dc2626; color: white; }
        .phase-2 { background: #ea580c; color: white; }
        .phase-3 { background: #d97706; color: white; }
        .phase-4 { background: #ca8a04; color: white; }

        .drop-zone {
            background: linear-gradient(90deg, rgba(239,68,68,0.2) 0%, rgba(239,68,68,0.05) 100%);
            border: 2px solid #ef4444;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            border-bottom: 1px solid #334155;
            padding-bottom: 10px;
        }

        .tab {
            padding: 10px 20px;
            background: transparent;
            border: 1px solid #3b82f6;
            color: #3b82f6;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
        }

        .tab:hover {
            background: #3b82f6;
            color: white;
        }

        .tab.active {
            background: #3b82f6;
            color: white;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }

        th {
            background: rgba(59, 130, 246, 0.1);
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #3b82f6;
            font-family: 'Teko', sans-serif;
            font-size: 1.2rem;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #334155;
        }

        tr:hover {
            background: rgba(255, 255, 255, 0.05);
        }

        .progress-bar {
            width: 100%;
            height: 10px;
            background: #1e293b;
            border-radius: 5px;
            overflow: hidden;
            margin: 10px 0;
        }

        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            border-radius: 5px;
            transition: width 0.3s ease;
        }

        .btn {
            background: transparent;
            border: 1px solid #3b82f6;
            color: #3b82f6;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Rajdhani', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
            margin: 5px;
            transition: all 0.3s;
        }

        .btn:hover {
            background: #3b82f6;
            color: white;
        }

        .btn-danger {
            border-color: #ef4444;
            color: #ef4444;
        }

        .btn-danger:hover {
            background: #ef4444;
            color: white;
        }

        .input-group {
            margin: 10px 0;
        }

        input, select {
            width: 100%;
            padding: 10px;
            background: rgba(0,0,0,0.6);
            color: white;
            border: 1px solid #334155;
            border-radius: 6px;
            margin: 5px 0;
        }

        .team-badge {
            font-size: 1.5rem;
            margin-right: 10px;
        }

        .match-card {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
        }

        .match-score {
            font-size: 2rem;
            font-weight: bold;
            color: #3b82f6;
            min-width: 100px;
            text-align: center;
        }

        @media (max-width: 768px) {
            .big-title {
                font-size: 2.5rem;
            }
            
            .tabs {
                flex-wrap: wrap;
            }
            
            .tab {
                flex: 1;
                min-width: 120px;
                text-align: center;
            }
            
            table {
                font-size: 0.9rem;
            }
            
            th, td {
                padding: 8px 4px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="big-title">DLS ULTRA</h1>
        
        <div id="battleRoyaleHeader" class="glass-panel" style="text-align: center; display: none;">
            <h2 style="color: white; margin: 0;">💀 BATTLE ROYALE PROTOCOL</h2>
            <p style="color: #fca5a5; margin: 5px 0 0 0;">"Survive the Cut. Trust No One."</p>
        </div>
        
        <div id="championDisplay" class="glass-panel" style="text-align: center; color:#FFD700; display: none;">
            <h2>👑 CHAMPION: <span id="championName"></span> 👑</h2>
        </div>
        
        <div id="roundInfo" class="glass-panel" style="text-align: center;">
            <h2 id="currentRound">Round 1 • Phase 1: The Purge</h2>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('standings')">📊 STANDINGS</button>
            <button class="tab" onclick="showTab('matches')">⚽ MATCH CENTER</button>
            <button class="tab" onclick="showTab('stats')">⭐ STATS</button>
            <button class="tab" onclick="showTab('info')">💀 BATTLE INFO</button>
        </div>

        <!-- TAB 1: STANDINGS -->
        <div id="standings" class="tab-content active">
            <div class="glass-panel">
                <h3>💀 SURVIVAL ARENA • <span id="teamsAlive">8</span> Teams Alive</h3>
                <div id="dropZoneWarning" style="color: #ef4444; margin: 10px 0; padding: 10px; background: rgba(239,68,68,0.1); border-radius: 6px;">
                    ⚠️ <strong>DROP ZONE:</strong> Bottom 2 teams will be eliminated after this round!
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Club</th>
                            <th>P</th>
                            <th>W</th>
                            <th>D</th>
                            <th>L</th>
                            <th>GF</th>
                            <th>GA</th>
                            <th>GD</th>
                            <th>Pts</th>
                        </tr>
                    </thead>
                    <tbody id="standingsTable">
                        <!-- Table will be populated by JavaScript -->
                    </tbody>
                </table>
                
                <div id="eliminatedSection" style="margin-top: 20px; display: none;">
                    <h4>☠️ Eliminated Teams</h4>
                    <div id="eliminatedList"></div>
                </div>
            </div>
        </div>

        <!-- TAB 2: MATCH CENTER -->
        <div id="matches" class="tab-content">
            <div class="glass-panel">
                <h3>⚽ MATCH CENTER</h3>
                <div class="input-group">
                    <select id="teamFilter" onchange="filterMatches()">
                        <option value="all">All Teams</option>
                    </select>
                </div>
                <div id="matchesList">
                    <!-- Matches will be populated by JavaScript -->
                </div>
            </div>
        </div>

        <!-- TAB 3: STATS -->
        <div id="stats" class="tab-content">
            <div class="glass-panel">
                <h3>⭐ PLAYER STATS</h3>
                <div id="goldenBoot" class="glass-panel" style="text-align: center;">
                    <h3>👑 GOLDEN BOOT LEADER</h3>
                    <h2 id="topScorer" style="color: #fbbf24;">No goals recorded yet</h2>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                    <div>
                        <h4>⚽ Top Scorers</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Player</th>
                                    <th>Club</th>
                                    <th>Goals</th>
                                </tr>
                            </thead>
                            <tbody id="goalsTable">
                                <tr><td colspan="3" style="text-align: center;">No goals recorded yet</td></tr>
                            </tbody>
                        </table>
                    </div>
                    
                    <div>
                        <h4>👟 Top Assists</h4>
                        <table>
                            <thead>
                                <tr>
                                    <th>Player</th>
                                    <th>Club</th>
                                    <th>Assists</th>
                                </tr>
                            </thead>
                            <tbody id="assistsTable">
                                <tr><td colspan="3" style="text-align: center;">No assists recorded yet</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 4: BATTLE INFO -->
        <div id="info" class="tab-content">
            <div class="glass-panel">
                <h3>💀 BATTLE ROYALE PROTOCOL</h3>
                
                <div style="margin: 20px 0;">
                    <button class="btn" onclick="toggleSection('rules')">📜 THE CORE RULES</button>
                    <button class="btn" onclick="toggleSection('phases')">🩸 ELIMINATION PHASES</button>
                    <button class="btn" onclick="toggleSection('tiebreakers')">📊 TIE-BREAKERS</button>
                </div>
                
                <div id="rules" class="section-content" style="display: block;">
                    <h4>📜 THE CORE RULES</h4>
                    <ul style="margin-left: 20px; line-height: 1.6;">
                        <li><strong>The "Cumulative" Table:</strong> Points carry over FOREVER</li>
                        <li><strong>Matchmaking: Pure RNG:</strong> No fixed bracket, random pairing every round</li>
                        <li><strong>Strategy:</strong> Hoard points to stay safe from the "Drop Zone"</li>
                    </ul>
                </div>
                
                <div id="phases" class="section-content" style="display: none;">
                    <h4>🩸 THE ELIMINATION PHASES</h4>
                    <ul style="margin-left: 20px; line-height: 1.6;">
                        <li><strong>Phase 1: The Purge (5+ Teams):</strong> Bottom 2 eliminated every round (2 matches each)</li>
                        <li><strong>Phase 2: The Squeeze (4 Teams):</strong> Bottom 1 eliminated per round</li>
                        <li><strong>Phase 3: The Standoff (3 Teams):</strong> 1st gets bye, 2nd vs 3rd sudden death</li>
                        <li><strong>Phase 4: Grand Final (2 Teams):</strong> One match for the crown</li>
                    </ul>
                </div>
                
                <div id="tiebreakers" class="section-content" style="display: none;">
                    <h4>📊 TIE-BREAKERS</h4>
                    <ol style="margin-left: 20px; line-height: 1.6;">
                        <li><strong>Points</strong> (Highest wins)</li>
                        <li><strong>Goal Difference</strong> (Better GD wins)</li>
                        <li><strong>Goals For</strong> (Most goals scored wins)</li>
                    </ol>
                </div>
                
                <div style="margin-top: 30px;">
                    <h4>🎯 CURRENT STATUS</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin: 20px 0;">
                        <div class="glass-panel" style="text-align: center;">
                            <h3 id="statusTeams">8</h3>
                            <p>Teams Alive</p>
                        </div>
                        <div class="glass-panel" style="text-align: center;">
                            <h3 id="statusRound">1</h3>
                            <p>Round</p>
                        </div>
                        <div class="glass-panel" style="text-align: center;">
                            <h3 id="statusEliminated">0</h3>
                            <p>Eliminated</p>
                        </div>
                        <div class="glass-panel" style="text-align: center;">
                            <h3 id="statusPhase">Purge</h3>
                            <p>Phase</p>
                        </div>
                    </div>
                    
                    <h4>📈 SURVIVAL PROGRESS</h4>
                    <div class="progress-bar">
                        <div id="progressFill" class="progress-fill" style="width: 100%"></div>
                    </div>
                    <p style="text-align: center;"><span id="progressText">8/8 teams remaining (100%)</span></p>
                </div>
            </div>
        </div>

        <!-- ADMIN PANEL (Initially Hidden) -->
        <div id="adminPanel" class="glass-panel" style="margin-top: 30px; display: none;">
            <h3>🔐 ADMIN PANEL</h3>
            
            <div class="input-group">
                <input type="password" id="adminPin" placeholder="Enter PIN (0209)">
                <button class="btn" onclick="toggleAdmin()">UNLOCK</button>
            </div>
            
            <div id="adminControls" style="display: none;">
                <div style="margin: 20px 0;">
                    <button class="btn" onclick="nextRound()">⏩ NEXT ROUND</button>
                    <button class="btn" onclick="resetTournament()">🧨 RESET</button>
                </div>
                
                <h4>⚙️ TEAM MANAGEMENT</h4>
                <div class="input-group">
                    <input type="text" id="newTeam" placeholder="New team name">
                    <button class="btn" onclick="addTeam()">ADD TEAM</button>
                </div>
                
                <div id="teamList" style="margin-top: 20px;"></div>
            </div>
        </div>

        <div style="text-align: center; padding: 20px; color: #475569; border-top: 1px solid #1e293b; margin-top: 50px;">
            OFFICIAL DLS TOURNAMENT ENGINE<br>
            WRITTEN AND DESIGNED BY <span style="color: #3b82f6; font-weight: bold;">OLUWATIMILEYIN IGBINLOLA</span>
        </div>
    </div>

    <script>
        // ========== DATA STORAGE ==========
        let tournamentData = {
            teams: ['Barcelona', 'Real Madrid', 'Manchester City', 'Liverpool', 'Bayern Munich', 'PSG', 'Chelsea', 'Juventus'],
            badges: ['🦁', '🦅', '🐺', '🐉', '🦈', '🐍', '🐻', '🐝'],
            activeTeams: ['Barcelona', 'Real Madrid', 'Manchester City', 'Liverpool', 'Bayern Munich', 'PSG', 'Chelsea', 'Juventus'],
            eliminatedTeams: [],
            round: 1,
            phase: 'Phase 1: The Purge',
            champion: null,
            cumulativeStats: {},
            playerStats: {},
            fixtures: [],
            results: {},
            isBattleRoyale: true
        };

        // Initialize data on load
        function initializeData() {
            // Load from localStorage if available
            const saved = localStorage.getItem('dlsUltraData');
            if (saved) {
                tournamentData = JSON.parse(saved);
            } else {
                // Initialize cumulative stats
                tournamentData.teams.forEach(team => {
                    tournamentData.cumulativeStats[team] = {
                        P: 0, W: 0, D: 0, L: 0,
                        GF: 0, GA: 0, GD: 0, Pts: 0
                    };
                });
                
                // Generate first round fixtures
                generateFixtures();
                saveData();
            }
            
            updateDisplay();
        }

        // Save data to localStorage
        function saveData() {
            localStorage.setItem('dlsUltraData', JSON.stringify(tournamentData));
        }

        // ========== DISPLAY FUNCTIONS ==========
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Remove active class from all tab buttons
            document.querySelectorAll('.tab').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            
            // Activate corresponding button
            event.target.classList.add('active');
            
            // Update tab content
            updateTabContent(tabName);
        }

        function updateTabContent(tabName) {
            switch(tabName) {
                case 'standings':
                    updateStandings();
                    break;
                case 'matches':
                    updateMatches();
                    break;
                case 'stats':
                    updateStats();
                    break;
                case 'info':
                    updateInfo();
                    break;
            }
        }

        function updateDisplay() {
            // Update header
            if (tournamentData.isBattleRoyale) {
                document.getElementById('battleRoyaleHeader').style.display = 'block';
            }
            
            // Update champion display
            if (tournamentData.champion) {
                document.getElementById('championDisplay').style.display = 'block';
                document.getElementById('championName').textContent = tournamentData.champion;
            } else {
                document.getElementById('championDisplay').style.display = 'none';
            }
            
            // Update round info
            document.getElementById('currentRound').textContent = 
                `Round ${tournamentData.round} • ${tournamentData.phase}`;
            
            // Update all tabs
            updateStandings();
            updateMatches();
            updateStats();
            updateInfo();
            
            // Update filter dropdown
            updateTeamFilter();
        }

        // ========== STANDINGS TAB ==========
        function updateStandings() {
            const tableBody = document.getElementById('standingsTable');
            const teamsAlive = document.getElementById('teamsAlive');
            const dropZoneWarning = document.getElementById('dropZoneWarning');
            
            // Clear table
            tableBody.innerHTML = '';
            
            // Get standings data
            const standings = [];
            tournamentData.activeTeams.forEach(team => {
                if (tournamentData.cumulativeStats[team]) {
                    standings.push({
                        team: team,
                        ...tournamentData.cumulativeStats[team]
                    });
                }
            });
            
            // Sort by Points → GD → GF
            standings.sort((a, b) => {
                if (b.Pts !== a.Pts) return b.Pts - a.Pts;
                if (b.GD !== a.GD) return b.GD - a.GD;
                return b.GF - a.GF;
            });
            
            // Update teams alive count
            teamsAlive.textContent = tournamentData.activeTeams.length;
            
            // Update drop zone warning
            if (tournamentData.phase === 'Phase 1: The Purge' && tournamentData.activeTeams.length >= 5) {
                dropZoneWarning.innerHTML = '⚠️ <strong>DROP ZONE:</strong> Bottom 2 teams will be eliminated after this round!';
                dropZoneWarning.style.display = 'block';
            } else if (tournamentData.phase === 'Phase 2: The Squeeze') {
                dropZoneWarning.innerHTML = '⚠️ <strong>DROP ZONE:</strong> Bottom team will be eliminated after this round!';
                dropZoneWarning.style.display = 'block';
            } else {
                dropZoneWarning.style.display = 'none';
            }
            
            // Populate table
            standings.forEach((teamData, index) => {
                const row = document.createElement('tr');
                
                // Determine if team is in drop zone
                const isDropZone = (tournamentData.phase === 'Phase 1: The Purge' && index >= standings.length - 2) ||
                                   (tournamentData.phase === 'Phase 2: The Squeeze' && index === standings.length - 1);
                
                if (isDropZone) {
                    row.classList.add('drop-zone');
                }
                
                const badgeIndex = tournamentData.teams.indexOf(teamData.team);
                const badge = badgeIndex >= 0 ? tournamentData.badges[badgeIndex] : '🛡️';
                
                row.innerHTML = `
                    <td>${index + 1}</td>
                    <td><span class="team-badge">${badge}</span> ${teamData.team}</td>
                    <td>${teamData.P}</td>
                    <td>${teamData.W}</td>
                    <td>${teamData.D}</td>
                    <td>${teamData.L}</td>
                    <td>${teamData.GF}</td>
                    <td>${teamData.GA}</td>
                    <td>${teamData.GD}</td>
                    <td><strong>${teamData.Pts}</strong></td>
                `;
                
                tableBody.appendChild(row);
            });
            
            // Update eliminated teams section
            updateEliminatedTeams();
        }

        function updateEliminatedTeams() {
            const eliminatedSection = document.getElementById('eliminatedSection');
            const eliminatedList = document.getElementById('eliminatedList');
            
            if (tournamentData.eliminatedTeams.length > 0) {
                eliminatedSection.style.display = 'block';
                eliminatedList.innerHTML = tournamentData.eliminatedTeams
                    .map(team => `<div style="padding: 5px; color: #ef4444;">💀 ${team}</div>`)
                    .join('');
            } else {
                eliminatedSection.style.display = 'none';
            }
        }

        // ========== MATCHES TAB ==========
        function updateMatches() {
            const matchesList = document.getElementById('matchesList');
            
            if (tournamentData.fixtures.length === 0) {
                matchesList.innerHTML = '<div class="glass-panel" style="text-align: center;">No matches scheduled for this round.</div>';
                return;
            }
            
            matchesList.innerHTML = '';
            
            tournamentData.fixtures.forEach((fixture, index) => {
                const [home, away] = fixture;
                const matchId = `${home}_${away}_${index}`;
                const result = tournamentData.results[matchId] || null;
                
                const matchCard = document.createElement('div');
                matchCard.className = 'match-card glass-panel';
                
                const homeBadgeIndex = tournamentData.teams.indexOf(home);
                const awayBadgeIndex = tournamentData.teams.indexOf(away);
                const homeBadge = homeBadgeIndex >= 0 ? tournamentData.badges[homeBadgeIndex] : '🛡️';
                const awayBadge = awayBadgeIndex >= 0 ? tournamentData.badges[awayBadgeIndex] : '🛡️';
                
                matchCard.innerHTML = `
                    <div style="flex: 1; text-align: right;">
                        <h3>${home} ${homeBadge}</h3>
                    </div>
                    <div class="match-score">
                        ${result ? `${result[0]} - ${result[1]}` : 'VS'}
                    </div>
                    <div style="flex: 1; text-align: left;">
                        <h3>${awayBadge} ${away}</h3>
                    </div>
                `;
                
                matchesList.appendChild(matchCard);
            });
        }

        function updateTeamFilter() {
            const filter = document.getElementById('teamFilter');
            filter.innerHTML = '<option value="all">All Teams</option>';
            
            tournamentData.activeTeams.forEach(team => {
                const option = document.createElement('option');
                option.value = team;
                option.textContent = team;
                filter.appendChild(option);
            });
        }

        function filterMatches() {
            const selectedTeam = document.getElementById('teamFilter').value;
            const matches = document.querySelectorAll('.match-card');
            
            matches.forEach(match => {
                if (selectedTeam === 'all') {
                    match.style.display = 'flex';
                } else {
                    const matchText = match.textContent;
                    if (matchText.includes(selectedTeam)) {
                        match.style.display = 'flex';
                    } else {
                        match.style.display = 'none';
                    }
                }
            });
        }

        // ========== STATS TAB ==========
        function updateStats() {
            // Process player stats from results
            const playerStats = {};
            
            // Collect stats from all results
            Object.entries(tournamentData.results).forEach(([matchId, score]) => {
                // Extract teams from matchId
                const parts = matchId.split('_');
                const home = parts[0];
                const away = parts[1];
                
                // In a real app, you'd parse actual player stats here
                // For demo, we'll create some sample stats
                if (Math.random() > 0.5) {
                    const homeScorer = `Player${Math.floor(Math.random() * 10)}`;
                    const playerId = `${homeScorer}|${home}`;
                    
                    if (!playerStats[playerId]) {
                        playerStats[playerId] = { name: homeScorer, team: home, G: 0, A: 0, R: 0 };
                    }
                    playerStats[playerId].G += Math.floor(Math.random() * 3) + 1;
                }
            });
            
            // Convert to array and sort
            const statsArray = Object.values(playerStats);
            const topScorers = [...statsArray].sort((a, b) => b.G - a.G);
            const topAssists = [...statsArray].sort((a, b) => b.A - a.A);
            
            // Update Golden Boot
            const goldenBoot = document.getElementById('topScorer');
            if (topScorers.length > 0) {
                goldenBoot.innerHTML = `${topScorers[0].name} (${topScorers[0].team}) - ${topScorers[0].G} goals`;
                goldenBoot.style.color = '#fbbf24';
            } else {
                goldenBoot.textContent = 'No goals recorded yet';
                goldenBoot.style.color = 'white';
            }
            
            // Update goals table
            const goalsTable = document.getElementById('goalsTable');
            goalsTable.innerHTML = '';
            
            if (topScorers.length > 0) {
                topScorers.slice(0, 5).forEach(player => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${player.name}</td>
                        <td>${player.team}</td>
                        <td><strong>${player.G}</strong></td>
                    `;
                    goalsTable.appendChild(row);
                });
            } else {
                goalsTable.innerHTML = '<tr><td colspan="3" style="text-align: center;">No goals recorded yet</td></tr>';
            }
            
            // Update assists table
            const assistsTable = document.getElementById('assistsTable');
            assistsTable.innerHTML = '';
            
            if (topAssists.length > 0) {
                topAssists.slice(0, 5).forEach(player => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${player.name}</td>
                        <td>${player.team}</td>
                        <td><strong>${player.A}</strong></td>
                    `;
                    assistsTable.appendChild(row);
                });
            } else {
                assistsTable.innerHTML = '<tr><td colspan="3" style="text-align: center;">No assists recorded yet</td></tr>';
            }
        }

        // ========== INFO TAB ==========
        function updateInfo() {
            // Update status cards
            document.getElementById('statusTeams').textContent = tournamentData.activeTeams.length;
            document.getElementById('statusRound').textContent = tournamentData.round;
            document.getElementById('statusEliminated').textContent = tournamentData.eliminatedTeams.length;
            document.getElementById('statusPhase').textContent = tournamentData.phase.split(':')[1]?.trim() || tournamentData.phase;
            
            // Update progress bar
            const totalTeams = tournamentData.teams.length;
            const remainingTeams = tournamentData.activeTeams.length;
            const progress = (remainingTeams / totalTeams) * 100;
            
            document.getElementById('progressFill').style.width = `${progress}%`;
            document.getElementById('progressText').textContent = 
                `${remainingTeams}/${totalTeams} teams remaining (${Math.round(progress)}%)`;
        }

        function toggleSection(sectionId) {
            // Hide all sections
            document.querySelectorAll('.section-content').forEach(section => {
                section.style.display = 'none';
            });
            
            // Show selected section
            document.getElementById(sectionId).style.display = 'block';
        }

        // ========== TOURNAMENT LOGIC ==========
        function generateFixtures() {
            const teams = [...tournamentData.activeTeams];
            const fixtures = [];
            
            // Shuffle teams
            for (let i = teams.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [teams[i], teams[j]] = [teams[j], teams[i]];
            }
            
            // Create pairs (2 matches each for Phase 1)
            for (let i = 0; i < teams.length; i += 2) {
                if (i + 1 < teams.length) {
                    fixtures.push([teams[i], teams[i + 1]]);
                    
                    // Add return fixture for Phase 1
                    if (tournamentData.phase === 'Phase 1: The Purge') {
                        fixtures.push([teams[i + 1], teams[i]]);
                    }
                }
            }
            
            tournamentData.fixtures = fixtures;
            tournamentData.results = {};
        }

        function simulateRound() {
            // Simulate results for all fixtures
            tournamentData.fixtures.forEach((fixture, index) => {
                const [home, away] = fixture;
                const matchId = `${home}_${away}_${index}`;
                
                if (!tournamentData.results[matchId]) {
                    // Generate random scores
                    const homeScore = Math.floor(Math.random() * 5);
                    const awayScore = Math.floor(Math.random() * 5);
                    
                    tournamentData.results[matchId] = [homeScore, awayScore];
                    
                    // Update cumulative stats
                    updateTeamStats(home, away, homeScore, awayScore);
                }
            });
            
            saveData();
            updateDisplay();
        }

        function updateTeamStats(home, away, homeScore, awayScore) {
            // Initialize if needed
            if (!tournamentData.cumulativeStats[home]) {
                tournamentData.cumulativeStats[home] = { P: 0, W: 0, D: 0, L: 0, GF: 0, GA: 0, GD: 0, Pts: 0 };
            }
            if (!tournamentData.cumulativeStats[away]) {
                tournamentData.cumulativeStats[away] = { P: 0, W: 0, D: 0, L: 0, GF: 0, GA: 0, GD: 0, Pts: 0 };
            }
            
            // Update home team stats
            tournamentData.cumulativeStats[home].P += 1;
            tournamentData.cumulativeStats[home].GF += homeScore;
            tournamentData.cumulativeStats[home].GA += awayScore;
            tournamentData.cumulativeStats[home].GD += (homeScore - awayScore);
            
            // Update away team stats
            tournamentData.cumulativeStats[away].P += 1;
            tournamentData.cumulativeStats[away].GF += awayScore;
            tournamentData.cumulativeStats[away].GA += homeScore;
            tournamentData.cumulativeStats[away].GD += (awayScore - homeScore);
            
            // Update wins/losses/draws
            if (homeScore > awayScore) {
                tournamentData.cumulativeStats[home].W += 1;
                tournamentData.cumulativeStats[home].Pts += 3;
                tournamentData.cumulativeStats[away].L += 1;
            } else if (awayScore > homeScore) {
                tournamentData.cumulativeStats[away].W += 1;
                tournamentData.cumulativeStats[away].Pts += 3;
                tournamentData.cumulativeStats[home].L += 1;
            } else {
                tournamentData.cumulativeStats[home].D += 1;
                tournamentData.cumulativeStats[home].Pts += 1;
                tournamentData.cumulativeStats[away].D += 1;
                tournamentData.cumulativeStats[away].Pts += 1;
            }
        }

        function nextRound() {
            // First simulate current round if not already done
            if (Object.keys(tournamentData.results).length === 0) {
                simulateRound();
            }
            
            // Determine phase and handle eliminations
            const activeCount = tournamentData.activeTeams.length;
            
            if (activeCount >= 5) {
                // Phase 1: Eliminate bottom 2
                tournamentData.phase = 'Phase 1: The Purge';
                eliminateBottomTeams(2);
            } else if (activeCount === 4) {
                // Phase 2: Eliminate bottom 1
                tournamentData.phase = 'Phase 2: The Squeeze';
                eliminateBottomTeams(1);
            } else if (activeCount === 3) {
                // Phase 3: Sudden Death setup
                tournamentData.phase = 'Phase 3: The Standoff';
                setupSuddenDeath();
            } else if (activeCount === 2) {
                // Phase 4: Grand Final
                tournamentData.phase = 'Phase 4: The Grand Final';
                // One more round then determine champion
            } else if (activeCount === 1) {
                // Champion!
                tournamentData.champion = tournamentData.activeTeams[0];
                tournamentData.phase = 'CHAMPION CROWNED';
            }
            
            // Increment round
            tournamentData.round += 1;
            
            // Generate new fixtures
            generateFixtures();
            
            saveData();
            updateDisplay();
            
            alert(`Round ${tournamentData.round - 1} completed! Moving to ${tournamentData.phase}`);
        }

        function eliminateBottomTeams(count) {
            // Get current standings
            const standings = tournamentData.activeTeams.map(team => ({
                team,
                ...tournamentData.cumulativeStats[team]
            }));
            
            // Sort by Points → GD → GF
            standings.sort((a, b) => {
                if (b.Pts !== a.Pts) return b.Pts - a.Pts;
                if (b.GD !== a.GD) return b.GD - a.GD;
                return b.GF - a.GF;
            });
            
            // Eliminate bottom teams
            const eliminated = standings.slice(-count);
            eliminated.forEach(teamData => {
                const index = tournamentData.activeTeams.indexOf(teamData.team);
                if (index > -1) {
                    tournamentData.activeTeams.splice(index, 1);
                    tournamentData.eliminatedTeams.push(teamData.team);
                }
            });
        }

        function setupSuddenDeath() {
            // In Phase 3, only 2nd vs 3rd play
            const standings = tournamentData.activeTeams.map(team => ({
                team,
                ...tournamentData.cumulativeStats[team]
            }));
            
            standings.sort((a, b) => {
                if (b.Pts !== a.Pts) return b.Pts - a.Pts;
                if (b.GD !== a.GD) return b.GD - a.GD;
                return b.GF - a.GF;
            });
            
            // 1st gets bye, 2nd vs 3rd play
            tournamentData.fixtures = [
                [standings[1].team, standings[2].team],
                [standings[2].team, standings[1].team]  // Return leg
            ];
        }

        // ========== ADMIN FUNCTIONS ==========
        function toggleAdmin() {
            const pin = document.getElementById('adminPin').value;
            if (pin === '0209') {
                document.getElementById('adminControls').style.display = 'block';
                document.getElementById('adminPanel').style.borderColor = '#10b981';
                updateTeamList();
            } else {
                alert('Incorrect PIN');
            }
        }

        function updateTeamList() {
            const teamList = document.getElementById('teamList');
            teamList.innerHTML = '';
            
            tournamentData.teams.forEach(team => {
                const div = document.createElement('div');
                div.className = 'glass-panel';
                div.style.margin = '10px 0';
                div.innerHTML = `
                    ${team} 
                    <button class="btn btn-danger" onclick="removeTeam('${team}')" style="float: right;">REMOVE</button>
                `;
                teamList.appendChild(div);
            });
        }

        function addTeam() {
            const newTeam = document.getElementById('newTeam').value.trim();
            if (newTeam && !tournamentData.teams.includes(newTeam)) {
                tournamentData.teams.push(newTeam);
                tournamentData.badges.push('🛡️');
                tournamentData.activeTeams.push(newTeam);
                tournamentData.cumulativeStats[newTeam] = {
                    P: 0, W: 0, D: 0, L: 0,
                    GF: 0, GA: 0, GD: 0, Pts: 0
                };
                
                document.getElementById('newTeam').value = '';
                saveData();
                updateTeamList();
                updateDisplay();
                alert(`${newTeam} added to tournament!`);
            }
        }

        function removeTeam(team) {
            if (confirm(`Remove ${team} from tournament?`)) {
                const index = tournamentData.teams.indexOf(team);
                if (index > -1) {
                    tournamentData.teams.splice(index, 1);
                    tournamentData.badges.splice(index, 1);
                    
                    const activeIndex = tournamentData.activeTeams.indexOf(team);
                    if (activeIndex > -1) {
                        tournamentData.activeTeams.splice(activeIndex, 1);
                    }
                    
                    delete tournamentData.cumulativeStats[team];
                    saveData();
                    updateTeamList();
                    updateDisplay();
                }
            }
        }

        function resetTournament() {
            if (confirm('Reset entire tournament? All data will be lost!')) {
                localStorage.removeItem('dlsUltraData');
                location.reload();
            }
        }

        // ========== INITIALIZATION ==========
        window.onload = function() {
            initializeData();
            
            // Show admin panel if URL has admin parameter
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.has('admin')) {
                document.getElementById('adminPanel').style.display = 'block';
            }
        };
    </script>
</body>
</html>
