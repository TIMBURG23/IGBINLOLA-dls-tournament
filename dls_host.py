import streamlit as st
import pandas as pd
import itertools
import random
import json
import os
import re
import copy
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="DLS Ultra Manager", page_icon="⚽", layout="wide", initial_sidebar_state="collapsed")

# --- CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Teko:wght@300;500;700&family=Rajdhani:wght@500;700&display=swap');

    .stApp {
        background-color: #09090b;
        background-image: radial-gradient(circle at 50% 0%, #111827 0%, transparent 80%);
        color: white;
    }
    h1, h2, h3 { font-family: 'Teko', sans-serif !important; text-transform: uppercase; margin: 0 !important; }
    .big-title {
        font-size: 5rem; font-weight: 700; text-align: center;
        background: linear-gradient(180deg, #fff 0%, #64748b 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(59, 130, 246, 0.3);
    }
    .glass-panel {
        background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05); 
        border-radius: 12px; padding: 20px; margin-bottom: 15px;
    }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background: rgba(0,0,0,0.6) !important; color: white !important; border: 1px solid #334155 !important;
    }
    .stButton > button {
        background: transparent; border: 1px solid #3b82f6; color: #3b82f6;
        font-family: 'Rajdhani', sans-serif; font-weight: 700; text-transform: uppercase; width: 100%;
    }
    .stButton > button:hover { background: #3b82f6; color: white; }
    .footer { text-align: center; padding: 20px; color: #475569; font-family: 'Rajdhani'; border-top: 1px solid #1e293b; margin-top: 50px; }
    .designer-name { color: #3b82f6; font-weight: bold; letter-spacing: 1px; }
    .club-badge { font-size: 3rem; margin-bottom: 10px; }
    .eliminated { opacity: 0.5; text-decoration: line-through; color: #ef4444 !important; }
    .drop-zone { background: linear-gradient(90deg, rgba(239,68,68,0.2) 0%, rgba(239,68,68,0.05) 100%); border: 2px solid #ef4444; }
    .safe-zone { background: linear-gradient(90deg, rgba(34,197,94,0.1) 0%, transparent 100%); border-left: 3px solid #22c55e; }
    .bye-zone { background: linear-gradient(90deg, rgba(250,204,21,0.1) 0%, transparent 100%); border-left: 3px solid #facc15; }
    .phase-badge { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; margin-left: 10px; }
    .phase-1 { background: #dc2626; color: white; }
    .phase-2 { background: #ea580c; color: white; }
    .phase-3 { background: #d97706; color: white; }
    .phase-4 { background: #ca8a04; color: white; }
    .phase-final { background: #fbbf24; color: #000; }
    .sudden-death { background: linear-gradient(90deg, #000 0%, #dc2626 50%, #000 100%); color: white; border: 2px solid #dc2626; }
    .golden-boot { color: #fbbf24; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 💾 DATABASE ---
DB_FILE = "dls_ultra_db.json"
BADGE_POOL = ["🦁", "🦅", "🐺", "🐉", "🦈", "🐍", "🐻", "🐝", "🦂", "🕷️", "⚓", "⚔️", "🛡️", "👑", "⚡", "🔥", "🌪️", "🌊", "🏰", "🚀", "💀", "👹", "👽", "🤖", "👻", "🎃", "💎", "🎯", "🎲", "🎱"]

def init_defaults():
    defaults = {
        'teams': [], 'format': 'League', 'current_round': 'Group Stage',
        'fixtures': [], 'results': {}, 'match_meta': {},
        'started': False, 'groups': {}, 'champion': None, 'active_teams': [], 
        'admin_unlock': False, 'team_badges': {}, 'news': [], 
        'legacy_stats': {}, 'team_history': {},
        'eliminated_teams': [], 'round_number': 1, 'survival_history': [],
        'battle_phase': 'Phase 1: The Purge',  # Track current phase
        'bye_team': None,  # For Phase 3: Team with bye
        'cumulative_stats': {},  # Store cumulative team points
        'cumulative_player_stats': {},  # NEW: Store cumulative player stats
        'sudden_death_round': 0,  # Track sudden death rounds
        'phase1_match_count': 2  # 2 matches each in Phase 1
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                st.session_state.teams = data.get("teams", [])
                st.session_state.format = data.get("format", "League") 
                st.session_state.current_round = data.get("current_round", "Group Stage")
                
                raw_fix = data.get("fixtures", [])
                st.session_state.fixtures = [tuple(f) for f in raw_fix] if isinstance(raw_fix, list) else []
                
                r_data = data.get("results", {})
                st.session_state.results = r_data if isinstance(r_data, dict) else {}
                
                m_data = data.get("match_meta", {})
                st.session_state.match_meta = m_data if isinstance(m_data, dict) else {}

                st.session_state.started = data.get("started", False)
                
                g_data = data.get("groups", {})
                st.session_state.groups = g_data if isinstance(g_data, dict) else {}
                
                st.session_state.champion = data.get("champion", None)
                st.session_state.active_teams = data.get("active_teams", [])
                st.session_state.team_badges = data.get("team_badges", {})
                st.session_state.news = data.get("news", [])
                st.session_state.legacy_stats = data.get("legacy_stats", {})
                st.session_state.team_history = data.get("team_history", {})
                
                # Survival-specific data
                st.session_state.eliminated_teams = data.get("eliminated_teams", [])
                st.session_state.round_number = data.get("round_number", 1)
                st.session_state.survival_history = data.get("survival_history", [])
                st.session_state.battle_phase = data.get("battle_phase", "Phase 1: The Purge")
                st.session_state.bye_team = data.get("bye_team", None)
                st.session_state.cumulative_stats = data.get("cumulative_stats", {})
                st.session_state.cumulative_player_stats = data.get("cumulative_player_stats", {})  # Load player stats
                st.session_state.sudden_death_round = data.get("sudden_death_round", 0)
                st.session_state.phase1_match_count = data.get("phase1_match_count", 2)

                for t in st.session_state.teams:
                    if t not in st.session_state.team_badges:
                        st.session_state.team_badges[t] = random.choice(BADGE_POOL)
        except: init_defaults()
    else: init_defaults()

def save_data_internal():
    """Save all data including cumulative player stats"""
    data = {
        "teams": st.session_state.teams, "format": st.session_state.format,
        "current_round": st.session_state.current_round, "fixtures": st.session_state.fixtures,
        "results": st.session_state.results, "match_meta": st.session_state.match_meta,
        "started": st.session_state.started, "groups": st.session_state.groups,
        "champion": st.session_state.champion, "active_teams": st.session_state.active_teams,
        "team_badges": st.session_state.team_badges, "news": st.session_state.news,
        "legacy_stats": st.session_state.legacy_stats, 
        "team_history": st.session_state.team_history,
        "eliminated_teams": st.session_state.eliminated_teams,
        "round_number": st.session_state.round_number,
        "survival_history": st.session_state.survival_history,
        "battle_phase": st.session_state.battle_phase,
        "bye_team": st.session_state.bye_team,
        "cumulative_stats": st.session_state.cumulative_stats,
        "cumulative_player_stats": st.session_state.cumulative_player_stats,  # Save player stats
        "sudden_death_round": st.session_state.sudden_death_round,
        "phase1_match_count": st.session_state.phase1_match_count
    }
    with open(DB_FILE, "w") as f: json.dump(data, f)

# --- 🧠 BATTLE ROYALE CORE LOGIC ---

def generate_balanced_fixtures_fixed(teams, matches_per_team):
    """Generate fixtures where EVERY team plays exactly N matches"""
    if len(teams) < 2: return []
    
    # Create a round-robin schedule
    def round_robin(teams_list):
        """Generate round-robin pairs"""
        if len(teams_list) % 2:
            teams_list.append(None)  # Add dummy for odd number
        
        n = len(teams_list)
        fixtures = []
        
        for round_num in range(n - 1):
            round_fixtures = []
            for i in range(n // 2):
                if teams_list[i] is not None and teams_list[n - 1 - i] is not None:
                    round_fixtures.append((teams_list[i], teams_list[n - 1 - i]))
            
            # Rotate for next round
            teams_list.insert(1, teams_list.pop())
            fixtures.extend(round_fixtures)
        
        return fixtures
    
    # Get all possible unique pairings
    all_possible = list(itertools.combinations(teams, 2))
    random.shuffle(all_possible)
    
    # If matches_per_team is small, use round-robin
    if matches_per_team <= len(teams) - 1:
        # Create multiple mini-rounds
        fixtures = []
        for _ in range(matches_per_team):
            round_fixtures = round_robin(teams.copy())
            # Filter out any None teams from the round-robin
            round_fixtures = [f for f in round_fixtures if f[0] is not None and f[1] is not None]
            fixtures.extend(round_fixtures)
        
        # Take only the required number of fixtures
        total_matches_needed = (len(teams) * matches_per_team) // 2
        if len(fixtures) >= total_matches_needed:
            return fixtures[:total_matches_needed]
    
    # Fallback: Use combination approach
    team_match_counts = {team: 0 for team in teams}
    fixtures = []
    available_pairs = all_possible.copy()
    
    while available_pairs and min(team_match_counts.values()) < matches_per_team:
        # Find a pair where both teams need matches
        for pair in available_pairs[:]:
            t1, t2 = pair
            if team_match_counts[t1] < matches_per_team and team_match_counts[t2] < matches_per_team:
                fixtures.append(pair)
                team_match_counts[t1] += 1
                team_match_counts[t2] += 1
                available_pairs.remove(pair)
                break
        else:
            # No suitable pair found, break
            break
    
    # If we still need more matches, try to add random ones
    if min(team_match_counts.values()) < matches_per_team:
        # Get teams that need more matches
        needy_teams = [t for t in teams if team_match_counts[t] < matches_per_team]
        
        # Try to create additional matches for needy teams
        for i in range(len(needy_teams)):
            for j in range(i + 1, len(needy_teams)):
                t1, t2 = needy_teams[i], needy_teams[j]
                if team_match_counts[t1] < matches_per_team and team_match_counts[t2] < matches_per_team:
                    # Check if this pair already exists
                    existing = False
                    for fix in fixtures:
                        if (fix[0] == t1 and fix[1] == t2) or (fix[0] == t2 and fix[1] == t1):
                            existing = True
                            break
                    
                    if not existing:
                        fixtures.append((t1, t2))
                        team_match_counts[t1] += 1
                        team_match_counts[t2] += 1
    
    return fixtures

def generate_fixtures_for_phase(teams, phase):
    """Generate fixtures based on current phase - 2 MATCHES EACH IN PHASE 1"""
    shuffled = teams.copy()
    random.shuffle(shuffled)
    
    if phase == "Phase 1: The Purge":
        # 2 matches per team for balance
        matches_per_team = 2
        
        # Generate balanced fixtures
        fixtures = generate_balanced_fixtures_fixed(shuffled, matches_per_team)
        
        return fixtures
    
    elif phase == "Phase 2: The Squeeze":
        # For 4 teams: 2 matches each (home and away against each other)
        fixtures = []
        for i in range(len(shuffled)):
            for j in range(i+1, len(shuffled)):
                fixtures.append((shuffled[i], shuffled[j]))
                fixtures.append((shuffled[j], shuffled[i]))  # Return fixture
        random.shuffle(fixtures)
        return fixtures
    
    elif phase == "Phase 3: The Standoff":
        # For 3 teams: 2nd vs 3rd in Sudden Death Semi-Final (2 legs)
        # First, determine standings
        standings = get_cumulative_standings()
        if len(standings) < 3: return []
        
        # Sort by points (highest first)
        standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
        
        leader = standings[0]['Team']
        second = standings[1]['Team']
        third = standings[2]['Team']
        
        st.session_state.bye_team = leader
        st.session_state.news.insert(0, f"👑 {leader} gets automatic BYE to Grand Final!")
        
        # 2nd vs 3rd play two legs
        return [(second, third), (third, second)]
    
    elif phase == "Phase 4: The Grand Final":
        # For 2 teams: one final match
        return [(shuffled[0], shuffled[1])]
    
    return []

def get_cumulative_standings():
    """Get current cumulative standings for all active teams"""
    standings = []
    
    # Start with cumulative stats if they exist
    cumulative = st.session_state.cumulative_stats.copy()
    
    # Add current round results
    for mid, res in st.session_state.results.items():
        try:
            if "_" in mid:
                base = mid.split('_')[0]
            else:
                base = mid
            
            if "v" in base:
                h, a = base.split('v')
            else:
                continue
        except: continue
        
        # Initialize teams in cumulative stats
        if h not in cumulative:
            cumulative[h] = {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0}
        if a not in cumulative:
            cumulative[a] = {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0}
        
        s_h, s_a = res[0], res[1]
        
        cumulative[h]['P'] += 1
        cumulative[a]['P'] += 1
        cumulative[h]['GF'] += s_h
        cumulative[h]['GA'] += s_a
        cumulative[h]['GD'] += (s_h - s_a)
        cumulative[a]['GF'] += s_a
        cumulative[a]['GA'] += s_h
        cumulative[a]['GD'] += (s_a - s_h)
        
        if s_h > s_a:
            cumulative[h]['W'] += 1
            cumulative[h]['Pts'] += 3
            cumulative[a]['L'] += 1
        elif s_a > s_h:
            cumulative[a]['W'] += 1
            cumulative[a]['Pts'] += 3
            cumulative[h]['L'] += 1
        else:
            cumulative[h]['D'] += 1
            cumulative[h]['Pts'] += 1
            cumulative[a]['D'] += 1
            cumulative[a]['Pts'] += 1
    
    # Convert to list format
    for team in st.session_state.active_teams:
        if team in cumulative:
            standings.append({
                'Team': team,
                'P': cumulative[team]['P'],
                'W': cumulative[team]['W'],
                'D': cumulative[team]['D'],
                'L': cumulative[team]['L'],
                'GF': cumulative[team]['GF'],
                'GA': cumulative[team]['GA'],
                'GD': cumulative[team]['GD'],
                'Pts': cumulative[team]['Pts']
            })
        else:
            standings.append({
                'Team': team,
                'P': 0, 'W': 0, 'D': 0, 'L': 0,
                'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0
            })
    
    return standings

def update_cumulative_player_stats():
    """Update cumulative player stats from current round results"""
    # Start with existing cumulative player stats
    player_stats = st.session_state.cumulative_player_stats.copy()
    
    # Process all matches in current round
    for mid, res in st.session_state.results.items():
        try:
            if "_" in mid:
                base = mid.split('_')[0]
            else:
                base = mid
            
            if "v" in base:
                h, a = base.split('v')
            else:
                continue
        except: continue
        
        meta = st.session_state.match_meta.get(mid, {})
        
        def process_player_string(raw_str, team, stat_type):
            if not raw_str: return
            parts = raw_str.split(',')
            for p in parts:
                p = p.strip()
                if not p: continue
                count = 1
                name = p
                m_br = re.search(r'^(.*?)\s*\((\d+)\)$', p)
                m_x = re.search(r'^(.*?)\s*[xX](\d+)$', p)
                if m_br: name = m_br.group(1); count = int(m_br.group(2))
                elif m_x: name = m_x.group(1); count = int(m_x.group(2))
                name = name.strip().title()
                
                # Create unique player ID (name + team)
                player_id = f"{name}|{team}"
                
                # Initialize player stats if not exists
                if player_id not in player_stats:
                    player_stats[player_id] = {
                        'Name': name,
                        'Team': team,
                        'G': 0, 'A': 0, 'R': 0
                    }
                
                # Add stats
                player_stats[player_id][stat_type] += count
        
        # Process goals, assists, red cards
        process_player_string(meta.get('h_s', ''), h, 'G')
        process_player_string(meta.get('a_s', ''), a, 'G')
        process_player_string(meta.get('h_a', ''), h, 'A')
        process_player_string(meta.get('a_a', ''), a, 'A')
        process_player_string(meta.get('h_r', ''), h, 'R')
        process_player_string(meta.get('a_r', ''), a, 'R')
    
    # Save back to session state
    st.session_state.cumulative_player_stats = player_stats

def get_current_player_stats():
    """Get cumulative player stats combined with current round"""
    # Start with cumulative player stats
    player_stats = st.session_state.cumulative_player_stats.copy()
    
    # Add current round results to show live updates
    for mid, res in st.session_state.results.items():
        try:
            if "_" in mid:
                base = mid.split('_')[0]
            else:
                base = mid
            
            if "v" in base:
                h, a = base.split('v')
            else:
                continue
        except: continue
        
        meta = st.session_state.match_meta.get(mid, {})
        
        def process_player_string_live(raw_str, team, stat_type):
            if not raw_str: return
            parts = raw_str.split(',')
            for p in parts:
                p = p.strip()
                if not p: continue
                count = 1
                name = p
                m_br = re.search(r'^(.*?)\s*\((\d+)\)$', p)
                m_x = re.search(r'^(.*?)\s*[xX](\d+)\)$', p)
                if m_br: name = m_br.group(1); count = int(m_br.group(2))
                elif m_x: name = m_x.group(1); count = int(m_x.group(2))
                name = name.strip().title()
                
                player_id = f"{name}|{team}"
                
                if player_id not in player_stats:
                    player_stats[player_id] = {
                        'Name': name,
                        'Team': team,
                        'G': 0, 'A': 0, 'R': 0
                    }
                
                player_stats[player_id][stat_type] += count
        
        process_player_string_live(meta.get('h_s', ''), h, 'G')
        process_player_string_live(meta.get('a_s', ''), a, 'G')
        process_player_string_live(meta.get('h_a', ''), h, 'A')
        process_player_string_live(meta.get('a_a', ''), a, 'A')
        process_player_string_live(meta.get('h_r', ''), h, 'R')
        process_player_string_live(meta.get('a_r', ''), a, 'R')
    
    return player_stats

def handle_battle_royale_elimination():
    """Execute your exact Battle Royale protocol"""
    # FIRST: Update cumulative player stats before elimination
    update_cumulative_player_stats()
    
    standings = get_cumulative_standings()
    
    # Sort by Points → GD → GF
    standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
    
    remaining = len(standings)
    
    # DETERMINE CURRENT PHASE
    if remaining >= 5:
        phase = "Phase 1: The Purge"
        elim_count = 2  # Bottom 2 teams eliminated
    elif remaining == 4:
        phase = "Phase 2: The Squeeze"
        elim_count = 1  # Bottom 1 team eliminated
    elif remaining == 3:
        phase = "Phase 3: The Standoff"
        elim_count = 0  # Special elimination handled differently
    elif remaining == 2:
        phase = "Phase 4: The Grand Final"
        elim_count = 0
    else:
        # Only 1 team left - CHAMPION!
        st.session_state.champion = standings[0]['Team']
        st.session_state.news.insert(0, f"🏆 {st.session_state.champion} is the BATTLE ROYALE CHAMPION!")
        st.session_state.battle_phase = "CHAMPION CROWNED"
        save_data_internal()
        st.rerun()
        return
    
    # Update phase if changed
    if phase != st.session_state.battle_phase:
        st.session_state.battle_phase = phase
        st.session_state.news.insert(0, f"🔁 PHASE CHANGE: {phase}")
    
    # Handle eliminations based on phase
    eliminated_this_round = []
    
    if phase == "Phase 1: The Purge":
        # Eliminate bottom 2 teams
        bottom_teams = standings[-2:]
        for team_data in bottom_teams:
            team = team_data['Team']
            if team in st.session_state.active_teams:
                st.session_state.active_teams.remove(team)
                eliminated_this_round.append(team)
                st.session_state.eliminated_teams.append({
                    'team': team,
                    'round': st.session_state.round_number,
                    'position': remaining - standings.index(team_data),
                    'phase': phase
                })
        
        if eliminated_this_round:
            st.session_state.news.insert(0, f"💀 PURGED: {', '.join(eliminated_this_round)} eliminated!")
    
    elif phase == "Phase 2: The Squeeze":
        # Eliminate bottom 1 team
        bottom_team = standings[-1]['Team']
        if bottom_team in st.session_state.active_teams:
            st.session_state.active_teams.remove(bottom_team)
            eliminated_this_round.append(bottom_team)
            st.session_state.eliminated_teams.append({
                'team': bottom_team,
                'round': st.session_state.round_number,
                'position': 4,
                'phase': phase
            })
        
        if eliminated_this_round:
            st.session_state.news.insert(0, f"💀 SQUEEZED OUT: {bottom_team} eliminated!")
    
    elif phase == "Phase 3: The Standoff":
        # Special phase: No elimination here, just generate sudden death fixtures
        # If sudden death matches are already completed, handle elimination
        if st.session_state.sudden_death_round >= 2:
            # Both sudden death matches have been played
            # Determine loser based on aggregate score
            leader = standings[0]['Team']
            second = standings[1]['Team']
            third = standings[2]['Team']
            
            # Check results of sudden death matches
            match1_id = f"{second}v{third}_0"
            match2_id = f"{third}v{second}_1"
            
            res1 = st.session_state.results.get(match1_id, [0, 0])
            res2 = st.session_state.results.get(match2_id, [0, 0])
            
            # Calculate aggregate
            second_goals = res1[0] + res2[1]  # Second's goals in both legs
            third_goals = res1[1] + res2[0]   # Third's goals in both legs
            
            if second_goals > third_goals:
                loser = third
                winner = second
            elif third_goals > second_goals:
                loser = second
                winner = third
            else:
                # Tie - use penalties if recorded
                if len(res1) > 2 and len(res2) > 2:
                    second_pens = res1[2] + res2[3]
                    third_pens = res1[3] + res2[2]
                    loser = third if second_pens > third_pens else second
                    winner = second if second_pens > third_pens else third
                else:
                    # Still tied - eliminate based on cumulative standings
                    loser = third if standings[1]['Pts'] > standings[2]['Pts'] else second
            
            # Eliminate loser
            if loser in st.session_state.active_teams:
                st.session_state.active_teams.remove(loser)
                eliminated_this_round.append(loser)
                st.session_state.eliminated_teams.append({
                    'team': loser,
                    'round': st.session_state.round_number,
                    'position': 3,
                    'phase': phase,
                    'reason': 'Lost Sudden Death Semi-Final'
                })
                st.session_state.news.insert(0, f"💀 SUDDEN DEATH: {loser} eliminated! {winner} advances to Final!")
            
            # Reset sudden death counter
            st.session_state.sudden_death_round = 0
            st.session_state.bye_team = None
    
    # Save cumulative team stats before generating new fixtures
    for team_data in standings:
        team = team_data['Team']
        if team in st.session_state.active_teams:
            if team not in st.session_state.cumulative_stats:
                st.session_state.cumulative_stats[team] = {}
            
            st.session_state.cumulative_stats[team]['P'] = team_data['P']
            st.session_state.cumulative_stats[team]['W'] = team_data['W']
            st.session_state.cumulative_stats[team]['D'] = team_data['D']
            st.session_state.cumulative_stats[team]['L'] = team_data['L']
            st.session_state.cumulative_stats[team]['GF'] = team_data['GF']
            st.session_state.cumulative_stats[team]['GA'] = team_data['GA']
            st.session_state.cumulative_stats[team]['GD'] = team_data['GD']
            st.session_state.cumulative_stats[team]['Pts'] = team_data['Pts']
    
    # Generate next round fixtures
    next_fixtures = generate_fixtures_for_phase(st.session_state.active_teams, phase)
    st.session_state.fixtures = next_fixtures
    
    # Update round info
    st.session_state.round_number += 1
    
    if phase == "Phase 3: The Standoff" and not eliminated_this_round:
        st.session_state.sudden_death_round += 1
        if st.session_state.sudden_death_round == 1:
            st.session_state.current_round = f"SUDDEN DEATH • Leg 1 • {phase}"
        else:
            st.session_state.current_round = f"SUDDEN DEATH • Leg 2 • {phase}"
    else:
        st.session_state.current_round = f"Round {st.session_state.round_number} • {phase}"
    
    # Reset match data for next round (but player stats are saved in cumulative_player_stats)
    st.session_state.results = {}
    st.session_state.match_meta = {}
    
    # Log history
    st.session_state.survival_history.append({
        'round': st.session_state.round_number - 1,
        'phase': phase,
        'remaining': len(st.session_state.active_teams),
        'eliminated': eliminated_this_round
    })
    
    save_data_internal()
    st.rerun()

if 'init' not in st.session_state:
    load_data()
    st.session_state.init = True

init_defaults()

# --- 🏆 HEADER ---
st.markdown('<div class="big-title">DLS ULTRA</div>', unsafe_allow_html=True)

# Special Battle Royale header
if "Survival" in st.session_state.format:
    st.markdown(f"""
    <div style="text-align: center; margin: 20px 0; padding: 15px; background: linear-gradient(90deg, #000 0%, #dc2626 50%, #000 100%); border-radius: 10px;">
        <h2 style="color: white; font-family: 'Teko'; margin: 0;">💀 BATTLE ROYALE PROTOCOL</h2>
        <p style="color: #fca5a5; font-family: 'Rajdhani'; margin: 5px 0 0 0;">"Survive the Cut. Trust No One."</p>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.champion:
    st.markdown(f'<div class="subtitle" style="color:#FFD700">👑 CHAMPION: {st.session_state.champion} 👑</div>', unsafe_allow_html=True)
else:
    subtitle = f"{st.session_state.current_round}"
    if "Survival" in st.session_state.format:
        phase_badge = ""
        if "Phase 1" in st.session_state.battle_phase:
            phase_badge = '<span class="phase-badge phase-1">THE PURGE (2 matches each)</span>'
        elif "Phase 2" in st.session_state.battle_phase:
            phase_badge = '<span class="phase-badge phase-2">THE SQUEEZE (2 matches each)</span>'
        elif "Phase 3" in st.session_state.battle_phase:
            phase_badge = '<span class="phase-badge phase-3">THE STANDOFF</span>'
        elif "Phase 4" in st.session_state.battle_phase:
            phase_badge = '<span class="phase-badge phase-4">GRAND FINAL</span>'
        
        subtitle = f"Round {st.session_state.round_number} • {st.session_state.battle_phase} {phase_badge}"
    
    st.markdown(f'<div class="subtitle">{subtitle}</div>', unsafe_allow_html=True)

# --- 🔒 SIDEBAR ---
with st.sidebar:
    st.markdown("### 🔐 MANAGER ACCESS")
    
    if not st.session_state.admin_unlock:
        pin = st.text_input("ENTER PIN", type="password")
        if pin == "0209": 
            st.session_state.admin_unlock = True
            st.rerun()
    
    if st.session_state.admin_unlock:
        st.success("ACCESS GRANTED")
        if st.button("🔒 LOGOUT"):
            st.session_state.admin_unlock = False
            st.rerun()

        st.markdown("---")
        if st.session_state.started and not st.session_state.champion:
            if st.button("⏩ EXECUTE ELIMINATION & NEXT ROUND"): 
                if "Survival" in st.session_state.format:
                    handle_battle_royale_elimination()
                else:
                    # Original logic for other formats
                    # ... (unchanged from previous code)
                    save_data_internal()
                    st.rerun()

        st.markdown("---")
        st.markdown("### ⚙️ TEAM EDITOR")
        new_team = st.text_input("REGISTER NEW CLUB")
        
        if st.button("ADD CLUB"):
            if new_team and new_team not in st.session_state.teams:
                st.session_state.teams.append(new_team)
                st.session_state.team_badges[new_team] = random.choice(BADGE_POOL)
                
                if st.session_state.started:
                    st.session_state.active_teams.append(new_team)
                    
                    if "Survival" in st.session_state.format:
                        # In Battle Royale, new team starts with 0 cumulative points
                        st.session_state.cumulative_stats[new_team] = {
                            'P': 0, 'W': 0, 'D': 0, 'L': 0, 
                            'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0
                        }
                        st.toast(f"💀 {new_team} enters the Battle Royale!")
                    else:
                        st.toast(f"✅ {new_team} joined!")
                
                save_data_internal()
                st.rerun()

        edit_target = st.selectbox("SELECT CLUB", ["Select..."] + st.session_state.teams)
        if edit_target != "Select...":
            c1, c2 = st.columns(2)
            if c1.button("🗑️ DELETE"):
                st.session_state.teams.remove(edit_target)
                if edit_target in st.session_state.active_teams: st.session_state.active_teams.remove(edit_target)
                save_data_internal()
                st.rerun()
            rename_val = c2.text_input("RENAME TO", value=edit_target)
            if c2.button("RENAME"):
                idx = st.session_state.teams.index(edit_target)
                st.session_state.teams[idx] = rename_val
                st.session_state.team_badges[rename_val] = st.session_state.team_badges.pop(edit_target)
                save_data_internal()
                st.rerun()

        st.markdown("---")
        st.markdown("### 💾 DATA MANAGEMENT")
        
        current_data = json.dumps({
            "teams": st.session_state.teams, "format": st.session_state.format, 
            "current_round": st.session_state.current_round, "fixtures": st.session_state.fixtures, 
            "results": st.session_state.results, "match_meta": st.session_state.match_meta, 
            "started": st.session_state.started, "groups": st.session_state.groups, 
            "champion": st.session_state.champion, "active_teams": st.session_state.active_teams, 
            "team_badges": st.session_state.team_badges, "news": st.session_state.news,
            "legacy_stats": st.session_state.legacy_stats,
            "team_history": st.session_state.team_history,
            "eliminated_teams": st.session_state.eliminated_teams,
            "round_number": st.session_state.round_number,
            "survival_history": st.session_state.survival_history,
            "battle_phase": st.session_state.battle_phase,
            "bye_team": st.session_state.bye_team,
            "cumulative_stats": st.session_state.cumulative_stats,
            "cumulative_player_stats": st.session_state.cumulative_player_stats,
            "sudden_death_round": st.session_state.sudden_death_round,
            "phase1_match_count": st.session_state.phase1_match_count
        })
        st.download_button("📥 DOWNLOAD BACKUP", data=current_data, file_name="dls_backup.json", mime="application/json")
        uploaded = st.file_uploader("📤 RESTORE BACKUP", type=['json'])
        if uploaded and st.button("⚠️ RESTORE NOW"):
            data = json.load(uploaded)
            st.session_state.teams = data["teams"]
            st.session_state.fixtures = [tuple(f) for f in data["fixtures"]] if isinstance(data["fixtures"], list) else []
            st.session_state.results = data["results"] if isinstance(data["results"], dict) else {}
            st.session_state.match_meta = data.get("match_meta", {}) if isinstance(data.get("match_meta"), dict) else {}
            st.session_state.started = data.get("started", False)
            st.session_state.groups = data.get("groups", {})
            st.session_state.current_round = data.get("current_round", "Group Stage")
            st.session_state.champion = data.get("champion", None)
            st.session_state.active_teams = data.get("active_teams", [])
            st.session_state.team_badges = data.get("team_badges", {})
            st.session_state.news = data.get("news", [])
            st.session_state.legacy_stats = data.get("legacy_stats", {})
            st.session_state.team_history = data.get("team_history", {})
            st.session_state.eliminated_teams = data.get("eliminated_teams", [])
            st.session_state.round_number = data.get("round_number", 1)
            st.session_state.survival_history = data.get("survival_history", [])
            st.session_state.battle_phase = data.get("battle_phase", "Phase 1: The Purge")
            st.session_state.bye_team = data.get("bye_team", None)
            st.session_state.cumulative_stats = data.get("cumulative_stats", {})
            st.session_state.cumulative_player_stats = data.get("cumulative_player_stats", {})
            st.session_state.sudden_death_round = data.get("sudden_death_round", 0)
            st.session_state.phase1_match_count = data.get("phase1_match_count", 2)
            save_data_internal()
            st.rerun()
        if st.button("🧨 FACTORY RESET"):
            st.session_state.clear()
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

# --- 🎮 MAIN INTERFACE ---
if not st.session_state.started:
    st.markdown(f"<div class='glass-panel' style='text-align:center'><h3>CLUBS READY: {len(st.session_state.teams)}</h3></div>", unsafe_allow_html=True)
    if st.session_state.teams:
        cols = st.columns(4)
        for i, t in enumerate(st.session_state.teams):
            b = st.session_state.team_badges.get(t, "🛡️")
            with cols[i%4]: st.markdown(f"<div class='glass-panel' style='text-align:center'><h1>{b}</h1><h3>{t}</h3></div>", unsafe_allow_html=True)

    if st.session_state.admin_unlock: 
        st.markdown("### 🏆 SELECT FORMAT")
        fmt = st.radio("", ["Home & Away League", "World Cup (Groups + Knockout)", "Classic Knockout", "Survival Mode (Battle Royale)"], horizontal=True)
        if st.button("🚀 INITIALIZE SEASON"):
            if len(st.session_state.teams) < 2: st.error("Need 2+ Teams")
            else:
                st.session_state.format = fmt
                st.session_state.current_round = "Group Stage" if "World" in fmt else ("League Phase" if "League" in fmt else ("Round 1" if "Survival" in fmt else "Knockout Round"))
                st.session_state.active_teams = st.session_state.teams.copy()
                
                if "Survival" in fmt:
                    # Initialize Battle Royale
                    st.session_state.eliminated_teams = []
                    st.session_state.round_number = 1
                    st.session_state.survival_history = []
                    st.session_state.battle_phase = "Phase 1: The Purge"
                    st.session_state.bye_team = None
                    st.session_state.cumulative_stats = {}
                    st.session_state.cumulative_player_stats = {}  # Initialize player stats
                    st.session_state.sudden_death_round = 0
                    st.session_state.phase1_match_count = 2
                    
                    # Initialize cumulative stats for all teams
                    for team in st.session_state.teams:
                        st.session_state.cumulative_stats[team] = {
                            'P': 0, 'W': 0, 'D': 0, 'L': 0, 
                            'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0
                        }
                    
                    # Generate first round fixtures
                    matches = generate_fixtures_for_phase(st.session_state.teams, "Phase 1: The Purge")
                    st.session_state.fixtures = matches
                    st.session_state.current_round = f"Round 1 • {st.session_state.battle_phase}"
                    
                    st.success(f"💀 BATTLE ROYALE INITIALIZED! 2 matches per team. Points and player stats carry over forever!")
                
                elif "League" in fmt: 
                    matches = list(itertools.permutations(st.session_state.teams, 2))
                    random.shuffle(matches)
                elif "World Cup" in fmt:
                    shuffled = st.session_state.teams.copy(); random.shuffle(shuffled); groups = {}; group_names = "ABCDEFGH"
                    for i in range(0, len(shuffled), 4): groups[group_names[i//4]] = shuffled[i:i+4]
                    st.session_state.groups = groups; matches = []
                    for g, teams in groups.items(): matches.extend(list(itertools.combinations(teams, 2)))
                elif "Knockout" in fmt:
                    shuffled = st.session_state.teams.copy(); random.shuffle(shuffled); matches = []
                    for i in range(0, len(shuffled), 2):
                        if i+1 < len(shuffled): matches.append((shuffled[i], shuffled[i+1]))
                
                if "Survival" not in fmt:
                    st.session_state.fixtures = matches
                
                st.session_state.started = True
                save_data_internal()
                st.rerun()

else:
    tab1, tab2, tab3, tab4 = st.tabs(["📊 CUMULATIVE TABLE", "⚽ MATCH CENTER", "⭐ STATS", "💀 BATTLE INFO"])

    with tab1:
        def render_battle_royale_table():
            standings = get_cumulative_standings()
            
            if not standings:
                st.info("No teams remaining")
                return
            
            # Sort by Points → GD → GF
            standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
            
            rows = []
            for idx, s in enumerate(standings):
                team = s['Team']
                badge = st.session_state.team_badges.get(team, "🛡️")
                
                # Determine row class based on position and phase
                row_class = ""
                if st.session_state.battle_phase == "Phase 1: The Purge" and idx >= len(standings) - 2:
                    row_class = "drop-zone"
                elif st.session_state.battle_phase == "Phase 2: The Squeeze" and idx == len(standings) - 1:
                    row_class = "drop-zone"
                elif st.session_state.bye_team == team:
                    row_class = "bye-zone"
                
                rows.append({
                    "#": idx + 1,
                    "Club": f"{badge} {team}",
                    "P": s['P'], "W": s['W'], "D": s['D'], "L": s['L'], 
                    "GF": s['GF'], "GA": s['GA'], "GD": s['GD'], 
                    "Pts": s['Pts']
                })
            
            if rows:
                df = pd.DataFrame(rows)
                
                # Highlight drop zone
                st.markdown(f"**Teams Alive:** {len(st.session_state.active_teams)} | **Current Phase:** {st.session_state.battle_phase}")
                
                if st.session_state.battle_phase == "Phase 1: The Purge":
                    st.warning(f"⚠️ **DROP ZONE:** Bottom 2 teams will be eliminated after this round! (2 matches each)")
                elif st.session_state.battle_phase == "Phase 2: The Squeeze":
                    st.warning(f"⚠️ **DROP ZONE:** Bottom team will be eliminated after this round! (2 matches each)")
                elif st.session_state.battle_phase == "Phase 3: The Standoff":
                    st.info(f"👑 **BYE:** {st.session_state.bye_team} gets automatic pass to Final!")
                    st.warning(f"⚔️ **SUDDEN DEATH:** 2nd vs 3rd playing elimination match!")
                
                st.dataframe(df[['#', 'Club', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']], 
                           hide_index=True, use_container_width=True,
                           column_config={
                               "#": st.column_config.NumberColumn(width="small"),
                               "Pts": st.column_config.ProgressColumn("Pts", format="%d", min_value=0, max_value=max(100, df['Pts'].max()))
                           })
                
                # Show eliminated teams
                if st.session_state.eliminated_teams:
                    with st.expander(f"☠️ Eliminated Teams ({len(st.session_state.eliminated_teams)})"):
                        elim_data = []
                        for e in st.session_state.eliminated_teams:
                            elim_data.append({
                                "Team": e['team'],
                                "Round": e['round'],
                                "Phase": e['phase'],
                                "Position": f"{e['position']}th"
                            })
                        if elim_data:
                            elim_df = pd.DataFrame(elim_data)
                            st.dataframe(elim_df, hide_index=True, use_container_width=True)

        def render_league_table():
            standings = get_cumulative_standings()
            
            if not standings:
                st.info("No teams in league")
                return
            
            standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
            
            rows = []
            for idx, s in enumerate(standings):
                team = s['Team']
                badge = st.session_state.team_badges.get(team, "🛡️")
                
                rows.append({
                    "#": idx + 1,
                    "Club": f"{badge} {team}",
                    "P": s['P'], "W": s['W'], "D": s['D'], "L": s['L'], 
                    "GF": s['GF'], "GA": s['GA'], "GD": s['GD'], 
                    "Pts": s['Pts']
                })
            
            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(df[['#', 'Club', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']], 
                           hide_index=True, use_container_width=True,
                           column_config={
                               "#": st.column_config.NumberColumn(width="small"),
                               "Pts": st.column_config.ProgressColumn("Pts", format="%d", min_value=0, max_value=max(100, df['Pts'].max()))
                           })

        if st.session_state.format == "Survival Mode (Battle Royale)":
            render_battle_royale_table()
        elif "League" in st.session_state.format:
            render_league_table()
        elif "World" in st.session_state.format and "Group" in st.session_state.current_round:
            # Render group tables...
            pass
        else:
            # Render knockout bracket...
            pass

    with tab2:
        filter_team = st.selectbox("FILTER TEAM", ["All"] + st.session_state.active_teams)
        
        for i, fix in enumerate(st.session_state.fixtures): 
            if len(fix) < 2: continue
            h, a = fix[0], fix[1]
            
            if filter_team != "All" and filter_team not in [h, a]: continue
            
            mid = f"{h}v{a}_{i}" 
            res = st.session_state.results.get(mid)
            
            # Check if this is a sudden death match
            is_sudden_death = (
                st.session_state.battle_phase == "Phase 3: The Standoff" and 
                st.session_state.sudden_death_round > 0
            )
            
            with st.container():
                panel_class = "glass-panel"
                if is_sudden_death:
                    panel_class += " sudden-death"
                
                st.markdown(f"<div class='{panel_class}'>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([4, 2, 4])
                b1 = st.session_state.team_badges.get(h, ""); b2 = st.session_state.team_badges.get(a, "")
                
                # Match header
                if is_sudden_death:
                    c1.markdown(f"<h3 style='text-align:right; color:#ff6b6b'>{h} {b1}</h3>", unsafe_allow_html=True)
                    c3.markdown(f"<h3 style='text-align:left; color:#ff6b6b'>{b2} {a}</h3>", unsafe_allow_html=True)
                    c2.markdown(f"<div style='text-align:center'><small>⚔️ SUDDEN DEATH • Leg {st.session_state.sudden_death_round}</small></div>", unsafe_allow_html=True)
                else:
                    c1.markdown(f"<h3 style='text-align:right'>{h} {b1}</h3>", unsafe_allow_html=True)
                    c3.markdown(f"<h3 style='text-align:left'>{b2} {a}</h3>", unsafe_allow_html=True)
                
                # Score display
                if res:
                    sc = f"{res[0]} - {res[1]}"
                    if len(res) > 2: sc += f"\n(P: {res[2]}-{res[3]})"
                    score_color = "#ef4444" if is_sudden_death else "#3b82f6"
                    c2.markdown(f"<h1 style='text-align:center; color:{score_color}'>{sc}</h1>", unsafe_allow_html=True)
                else: 
                    if is_sudden_death:
                        c2.markdown(f"<h1 style='text-align:center; color:#ef4444'>⚔️ VS ⚔️</h1>", unsafe_allow_html=True)
                    else:
                        c2.markdown(f"<h1 style='text-align:center; color:#64748b'>VS</h1>", unsafe_allow_html=True)
                
                # Match reporting
                if st.session_state.admin_unlock and not st.session_state.champion: 
                    with st.expander(f"📝 REPORT MATCH {i+1}"):
                        if is_sudden_death:
                            st.warning("⚔️ **SUDDEN DEATH SEMI-FINAL:** Loser is ELIMINATED!")
                        
                        ac1, ac2 = st.columns(2)
                        s1 = ac1.number_input(f"{h}", 0, 20, key=f"s1_{mid}") 
                        s2 = ac2.number_input(f"{a}", 0, 20, key=f"s2_{mid}") 
                        p1, p2 = 0, 0
                        
                        # Penalties for sudden death or non-league formats
                        if (s1 == s2 and "League" not in st.session_state.format) or is_sudden_death:
                            st.caption("Penalties (if tied)")
                            p1 = ac1.number_input(f"P {h}", 0, 20, key=f"p1_{mid}")
                            p2 = ac2.number_input(f"P {a}", 0, 20, key=f"p2_{mid}")

                        sc1, sc2 = st.columns(2)
                        prev = st.session_state.match_meta.get(mid, {})
                        gs1 = sc1.text_input("Scorers (Home)", value=prev.get('h_s',''), key=f"g1_{mid}", placeholder="Messi (2), ...")
                        gs2 = sc2.text_input("Scorers (Away)", value=prev.get('a_s',''), key=f"g2_{mid}")
                        ha = sc1.text_input("Ast H", value=prev.get('h_a',''), key=f"ah_{mid}")
                        aa = sc2.text_input("Ast A", value=prev.get('a_a',''), key=f"aa_{mid}")
                        hr = sc1.text_input("Red H", value=prev.get('h_r',''), key=f"rh_{mid}")
                        ar = sc2.text_input("Red A", value=prev.get('a_r',''), key=f"ra_{mid}")
                        
                        if st.button("CONFIRM RESULT", key=f"b_{mid}"):
                            if (s1 == s2 and "League" not in st.session_state.format) or is_sudden_death:
                                st.session_state.results[mid] = [s1, s2, p1, p2]
                            else:
                                st.session_state.results[mid] = [s1, s2]
                            
                            st.session_state.match_meta[mid] = {'h_s': gs1, 'a_s': gs2, 'h_a': ha, 'a_a': aa, 'h_r': hr, 'a_r': ar}
                            
                            # Update cumulative stats immediately
                            if h in st.session_state.cumulative_stats and a in st.session_state.cumulative_stats:
                                st.session_state.cumulative_stats[h]['P'] += 1
                                st.session_state.cumulative_stats[a]['P'] += 1
                                st.session_state.cumulative_stats[h]['GF'] += s1
                                st.session_state.cumulative_stats[h]['GA'] += s2
                                st.session_state.cumulative_stats[h]['GD'] += (s1 - s2)
                                st.session_state.cumulative_stats[a]['GF'] += s2
                                st.session_state.cumulative_stats[a]['GA'] += s1
                                st.session_state.cumulative_stats[a]['GD'] += (s2 - s1)
                                
                                if s1 > s2:
                                    st.session_state.cumulative_stats[h]['W'] += 1
                                    st.session_state.cumulative_stats[h]['Pts'] += 3
                                    st.session_state.cumulative_stats[a]['L'] += 1
                                elif s2 > s1:
                                    st.session_state.cumulative_stats[a]['W'] += 1
                                    st.session_state.cumulative_stats[a]['Pts'] += 3
                                    st.session_state.cumulative_stats[h]['L'] += 1
                                else:
                                    st.session_state.cumulative_stats[h]['D'] += 1
                                    st.session_state.cumulative_stats[h]['Pts'] += 1
                                    st.session_state.cumulative_stats[a]['D'] += 1
                                    st.session_state.cumulative_stats[a]['Pts'] += 1
                            
                            save_data_internal()
                            st.success("UPDATED")
                            st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        # Get cumulative player stats
        player_stats = get_current_player_stats()
        
        if player_stats:
            # Convert to list for display
            data = []
            for player_id, stats in player_stats.items():
                if isinstance(stats, dict):
                    data.append({
                        "Player": stats.get('Name', 'Unknown'),
                        "Club": stats.get('Team', 'Unknown'),
                        "Goals": stats.get('G', 0),
                        "Assists": stats.get('A', 0),
                        "Reds": stats.get('R', 0)
                    })
            
            if data:
                df = pd.DataFrame(data)
                
                # Show Golden Boot leader
                if not df.empty:
                    top_scorer = df.sort_values(by='Goals', ascending=False).iloc[0]
                    st.markdown(f"<div class='glass-panel' style='text-align:center'><h3>👑 GOLDEN BOOT LEADER</h3><h2 class='golden-boot'>{top_scorer['Player']} ({top_scorer['Club']}) - {top_scorer['Goals']} goals</h2></div>", unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                
                def show_stat(col, title, key, icon):
                    col.markdown(f"#### {icon} {title}")
                    if not df.empty:
                        top = df.sort_values(by=key, ascending=False).head(10).reset_index(drop=True)
                        top.index += 1
                        col.dataframe(top[['Player', 'Club', key]], use_container_width=True)
                
                show_stat(c1, "Goals", "Goals", "⚽")
                show_stat(c2, "Assists", "Assists", "👟")
                show_stat(c3, "Red Cards", "Reds", "🟥")
                
                # Show total stats
                with st.expander("📊 TOTAL TOURNAMENT STATS"):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Players", len(df))
                    col2.metric("Total Goals", int(df['Goals'].sum()))
                    col3.metric("Total Assists", int(df['Assists'].sum()))
                    col4.metric("Total Red Cards", int(df['Reds'].sum()))
            else:
                st.info("No player stats recorded yet. Report matches to see stats!")
        else:
            st.info("No player stats recorded yet. Report matches to see stats!")

    with tab4:
        if "Survival" in st.session_state.format:
            st.markdown("### 💀 BATTLE ROYALE PROTOCOL")
            
            # Protocol Rules
            with st.expander("📜 THE CORE RULES", expanded=True):
                st.markdown("""
                **1. The "Cumulative" Table**
                - Points carry over FOREVER
                - Player stats (goals, assists, reds) also carry over FOREVER
                - Win 3-0 in Round 1 → carry 3 points and +3 GD into Round 2
                - Strategy: Hoard points to stay safe from the "Drop Zone"
                
                **2. Matchmaking: Pure RNG**
                - No fixed bracket
                - After every round, all surviving teams are thrown into a hat and shuffled
                - You could play the strongest team twice in a row, or dodge them until the end
                - It is pure luck
                """)
            
            with st.expander("🩸 THE ELIMINATION PHASES"):
                st.markdown("""
                **Phase 1: The Purge (5+ Teams Alive)**
                - Bottom 2 teams eliminated EVERY ROUND
                - **2 matches per team each round**
                - Example: 8 teams → Round 1 → 7th & 8th deleted
                
                **Phase 2: The Squeeze (4 Teams Alive)**
                - Bottom 1 team eliminated per round
                - 2 matches per team (home & away)
                - You just have to be better than one other person
                
                **Phase 3: The Standoff (3 Teams Alive)**
                - **1st Place**: Gets a BYE (Automatic pass to Grand Final)
                - **2nd vs 3rd**: Play "Sudden Death" Semi-Final (2 legs)
                - Loser eliminated, Winner advances to Final
                
                **Phase 4: The Grand Final (2 Teams Alive)**
                - Final two survivors play one last match
                - Highest points total at the end wins the crown
                """)
            
            with st.expander("📊 TIE-BREAKERS (How to stay alive)"):
                st.markdown("""
                If teams are level on points near the Drop Zone:
                1. **Points** (Highest wins)
                2. **Goal Difference** (Better GD wins)
                3. **Goals For** (Most goals scored wins)
                4. **Head-to-Head** (If applicable)
                """)
            
            # Current Status
            st.markdown("### 🎯 CURRENT STATUS")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Teams Alive", len(st.session_state.active_teams))
            with col2:
                st.metric("Round", st.session_state.round_number)
            with col3:
                st.metric("Eliminated", len(st.session_state.eliminated_teams))
            with col4:
                st.metric("Phase", st.session_state.battle_phase.split(":")[0])
            
            # Show current match count info
            if st.session_state.battle_phase == "Phase 1: The Purge":
                st.info(f"📊 **Current Round:** Each team plays **2 matches** (balanced scheduling)")
            
            # News Feed
            if st.session_state.news:
                st.markdown("### 📰 BATTLE NEWS")
                for news_item in st.session_state.news[:5]:  # Show last 5 news items
                    st.markdown(f"• {news_item}")
            
            # Survival Progress
            st.markdown("### 📈 SURVIVAL PROGRESS")
            total_start = len(st.session_state.teams)
            current = len(st.session_state.active_teams)
            
            if total_start > 0:
                progress = current / total_start
                st.progress(progress, text=f"{current}/{total_start} teams remaining ({int(progress*100)}%)")
            
            # Show who's at risk
            if st.session_state.active_teams and st.session_state.battle_phase in ["Phase 1: The Purge", "Phase 2: The Squeeze"]:
                standings = get_cumulative_standings()
                standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
                
                if st.session_state.battle_phase == "Phase 1: The Purge" and len(standings) >= 5:
                    at_risk = standings[-2:]
                    st.warning(f"**DROP ZONE:** {at_risk[0]['Team']} and {at_risk[1]['Team']} are at risk of elimination!")
                elif st.session_state.battle_phase == "Phase 2: The Squeeze" and len(standings) == 4:
                    at_risk = standings[-1]
                    st.warning(f"**DROP ZONE:** {at_risk['Team']} is at risk of elimination!")
            
            # Phase 3 Special Display
            if st.session_state.battle_phase == "Phase 3: The Standoff":
                standings = get_cumulative_standings()
                standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
                
                if len(standings) == 3:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.success(f"**👑 1st: {standings[0]['Team']}**\n{standings[0]['Pts']} pts\n(AUTO BYE TO FINAL)")
                    with col2:
                        st.warning(f"**⚔️ 2nd: {standings[1]['Team']}**\n{standings[1]['Pts']} pts\n(Playing Sudden Death)")
                    with col3:
                        st.error(f"**💀 3rd: {standings[2]['Team']}**\n{standings[2]['Pts']} pts\n(Playing Sudden Death)")
        
        else:
            st.info("Battle Royale info only available in Survival Mode")

# --- FOOTER ---
st.markdown("""<div class="footer">OFFICIAL DLS TOURNAMENT ENGINE <br> WRITTEN AND DESIGNED BY <span class="designer-name">OLUWATIMILEYIN IGBINLOLA</span></div>""", unsafe_allow_html=True)
