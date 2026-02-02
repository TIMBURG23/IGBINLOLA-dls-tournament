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

# --- CSS STYLING (YOUR ORIGINAL DESIGN) ---
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
        'battle_phase': 'Phase 1: The Purge', 
        'bye_team': None, 
        'cumulative_stats': {}, 
        'cumulative_player_stats': {}, 
        'sudden_death_round': 0, 
        'phase1_match_count': 2 
    }
    for k, v in defaults.items():
        if k not in st.session_state: st.session_state[k] = v

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                for k in st.session_state.keys():
                    if k in data:
                        if k == 'fixtures': # Safe tuple load
                            st.session_state[k] = [tuple(f) for f in data.get(k, [])]
                        else:
                            st.session_state[k] = data[k]
                
                # Ensure badges
                for t in st.session_state.teams:
                    if t not in st.session_state.team_badges:
                        st.session_state.team_badges[t] = random.choice(BADGE_POOL)
        except: init_defaults()
    else: init_defaults()

def save_data_internal():
    data = {k: st.session_state[k] for k in st.session_state.keys() if k != 'init'}
    with open(DB_FILE, "w") as f: json.dump(data, f)

# --- 🛠️ CRITICAL FIX: SAFE MATCH ID PARSER ---
def safe_split_match_id(mid):
    """Safely extracts Home and Away teams even if names have 'v' in them"""
    # 1. Strip the suffix (e.g. _0)
    if "_" in mid and mid.rsplit("_", 1)[-1].isdigit():
        base = mid.rsplit("_", 1)[0]
    else:
        base = mid
        
    # 2. Check for the new SAFE separator first
    if "|vs|" in base:
        return base.split("|vs|")
        
    # 3. Fallback for old IDs: Use team list to identify the split point
    # This prevents "DC Vibez FC" from breaking the logic
    for team in st.session_state.teams:
        if base.startswith(team + "v"):
            # We found the home team at the start
            possible_away = base[len(team)+1:]
            # Verify if possible_away is also a valid team (optional but safer)
            return team, possible_away
            
    # 4. Last resort simple split (might fail for Vibez but handles legacy)
    parts = base.split('v')
    if len(parts) == 2: return parts[0], parts[1]
    return None, None

# --- 🧠 LOGIC ENGINE (RESTORED & FIXED) ---

def generate_balanced_fixtures_fixed(teams, matches_per_team):
    """Generate fixtures where EVERY team plays exactly N matches"""
    if len(teams) < 2: return []
    
    # Create tickets
    bag = []
    for t in teams:
        for _ in range(matches_per_team):
            bag.append(t)
    
    random.shuffle(bag)
    fixtures = []
    
    for attempt in range(50):
        temp_bag = bag.copy()
        temp_fixtures = []
        random.shuffle(temp_bag)
        valid = True
        
        while len(temp_bag) >= 2:
            t1 = temp_bag.pop()
            candidates = [x for x in temp_bag if x != t1]
            if not candidates:
                valid = False; break
            
            t2 = candidates[0]
            temp_bag.remove(t2)
            temp_fixtures.append((t1, t2))
            
        if valid and len(temp_bag) == 0:
            return temp_fixtures
            
    # Fallback
    return list(itertools.combinations(teams, 2))[:len(teams)*matches_per_team//2]

def generate_fixtures_for_phase(teams, phase):
    shuffled = teams.copy()
    random.shuffle(shuffled)
    
    if phase == "Phase 1: The Purge":
        return generate_balanced_fixtures_fixed(shuffled, 2) # 2 matches each
    
    elif phase == "Phase 2: The Squeeze":
        return generate_balanced_fixtures_fixed(shuffled, 2) # 2 matches each
    
    elif phase == "Phase 3: The Standoff":
        standings = get_cumulative_standings()
        standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
        if len(standings) < 3: return []
        
        leader = standings[0]['Team']
        second = standings[1]['Team']
        third = standings[2]['Team']
        
        st.session_state.bye_team = leader
        st.session_state.news.insert(0, f"👑 {leader} gets automatic BYE to Grand Final!")
        return [(second, third), (third, second)]
    
    elif phase == "Phase 4: The Grand Final":
        return [(shuffled[0], shuffled[1])]
    
    return []

def get_cumulative_standings():
    """Calculates table. Uses safe_split to fix the 'Vibez' bug."""
    standings = []
    cumulative = copy.deepcopy(st.session_state.cumulative_stats)
    
    # Ensure all active teams are in cumulative dict
    for t in st.session_state.active_teams:
        if t not in cumulative:
            cumulative[t] = {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0}

    # Add current round results
    for mid, res in st.session_state.results.items():
        h, a = safe_split_match_id(mid) # <--- THE FIX
        if not h or not a: continue
        
        if h not in cumulative: cumulative[h] = {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0}
        if a not in cumulative: cumulative[a] = {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'GD': 0, 'Pts': 0}
        
        s_h, s_a = res[0], res[1]
        
        cumulative[h]['P'] += 1; cumulative[a]['P'] += 1
        cumulative[h]['GF'] += s_h; cumulative[a]['GF'] += s_a
        cumulative[h]['GA'] += s_a; cumulative[a]['GA'] += s_h
        cumulative[h]['GD'] += (s_h - s_a); cumulative[a]['GD'] += (s_a - s_h)
        
        if s_h > s_a:
            cumulative[h]['W'] += 1; cumulative[h]['Pts'] += 3; cumulative[a]['L'] += 1
        elif s_a > s_h:
            cumulative[a]['W'] += 1; cumulative[a]['Pts'] += 3; cumulative[h]['L'] += 1
        else:
            # STRICT DRAW RULE: 1 POINT
            cumulative[h]['D'] += 1; cumulative[h]['Pts'] += 1
            cumulative[a]['D'] += 1; cumulative[a]['Pts'] += 1
    
    for team in st.session_state.active_teams:
        if team in cumulative:
            standings.append(cumulative[team] | {'Team': team})
    
    return standings

def update_cumulative_player_stats():
    player_stats = st.session_state.cumulative_player_stats.copy()
    
    for mid, res in st.session_state.results.items():
        h, a = safe_split_match_id(mid) # <--- THE FIX
        if not h or not a: continue
        
        meta = st.session_state.match_meta.get(mid, {})
        
        def process_p(raw, team, kind):
            if not raw: return
            for part in raw.split(','):
                part = part.strip()
                if not part: continue
                
                count = 1
                name = part
                m1 = re.search(r'^(.*?)\s*\((\d+)\)$', part)
                m2 = re.search(r'^(.*?)\s*[xX](\d+)$', part)
                if m1: name = m1.group(1); count = int(m1.group(2))
                elif m2: name = m2.group(1); count = int(m2.group(2))
                
                name = name.strip().title()
                pid = f"{name}|{team}"
                
                if pid not in player_stats:
                    player_stats[pid] = {'Name': name, 'Team': team, 'G':0, 'A':0, 'R':0}
                player_stats[pid][kind] += count

        process_p(meta.get('h_s'), h, 'G'); process_p(meta.get('a_s'), a, 'G')
        process_p(meta.get('h_a'), h, 'A'); process_p(meta.get('a_a'), a, 'A')
        process_p(meta.get('h_r'), h, 'R'); process_p(meta.get('a_r'), a, 'R')
        
    st.session_state.cumulative_player_stats = player_stats

def handle_battle_royale_elimination():
    update_cumulative_player_stats()
    standings = get_cumulative_standings()
    standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
    
    remaining = len(standings)
    
    if remaining >= 5:
        phase = "Phase 1: The Purge"
        drop_count = 2
    elif remaining == 4:
        phase = "Phase 2: The Squeeze"
        drop_count = 1
    elif remaining == 3:
        phase = "Phase 3: The Standoff"
        drop_count = 0
    elif remaining == 2:
        phase = "Phase 4: The Grand Final"
        drop_count = 0
    else:
        st.session_state.champion = standings[0]['Team']
        st.session_state.battle_phase = "CHAMPION CROWNED"
        save_data_internal(); st.rerun(); return

    st.session_state.battle_phase = phase
    eliminated_this_round = []

    if phase in ["Phase 1: The Purge", "Phase 2: The Squeeze"]:
        victims = standings[-drop_count:]
        for v in victims:
            t = v['Team']
            if t in st.session_state.active_teams:
                st.session_state.active_teams.remove(t)
                st.session_state.eliminated_teams.append({'team': t, 'phase': phase})
                eliminated_this_round.append(t)
        if eliminated_this_round:
            st.session_state.news.insert(0, f"💀 ELIMINATED: {', '.join(eliminated_this_round)}")

    elif phase == "Phase 3: The Standoff":
        if st.session_state.sudden_death_round >= 2:
            leader = standings[0]['Team']
            p2 = standings[1]['Team']
            p3 = standings[2]['Team']
            
            # Simple elimination: 3rd place in standings goes home
            loser = p3
            winner = p2
            
            if loser in st.session_state.active_teams:
                st.session_state.active_teams.remove(loser)
                st.session_state.eliminated_teams.append({'team': loser, 'phase': phase})
                st.session_state.news.insert(0, f"💀 SUDDEN DEATH: {loser} eliminated! {winner} advances.")
            
            st.session_state.sudden_death_round = 0
            st.session_state.bye_team = None

    # SAVE STATS to permanent storage before wiping results
    for t_data in standings:
        t = t_data['Team']
        if t in st.session_state.active_teams:
            st.session_state.cumulative_stats[t] = {k:v for k,v in t_data.items() if k != 'Team'}

    # Next Round Setup
    st.session_state.fixtures = generate_fixtures_for_phase(st.session_state.active_teams, phase)
    st.session_state.round_number += 1
    
    if phase == "Phase 3: The Standoff" and not eliminated_this_round:
        st.session_state.sudden_death_round += 1
        st.session_state.current_round = f"SUDDEN DEATH • Leg {st.session_state.sudden_death_round}"
    else:
        st.session_state.current_round = f"Round {st.session_state.round_number} • {phase}"

    st.session_state.results = {}
    st.session_state.match_meta = {}
    
    save_data_internal()
    st.rerun()

if 'init' not in st.session_state:
    load_data()
    st.session_state.init = True

init_defaults()

# --- 🏆 UI RENDERING ---
st.markdown('<div class="big-title">DLS ULTRA</div>', unsafe_allow_html=True)

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
        subtitle = f"Round {st.session_state.round_number} • {st.session_state.battle_phase}"
    st.markdown(f'<div class="subtitle">{subtitle}</div>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🔐 MANAGER ACCESS")
    if not st.session_state.admin_unlock:
        if st.text_input("ENTER PIN", type="password") == "0209":
            st.session_state.admin_unlock = True; st.rerun()
    
    if st.session_state.admin_unlock:
        st.success("ACCESS GRANTED")
        if st.button("🔒 LOGOUT"): st.session_state.admin_unlock = False; st.rerun()
        
        st.markdown("---")
        if st.session_state.started and not st.session_state.champion:
            if st.button("⏩ NEXT ROUND / ELIMINATE"):
                if "Survival" in st.session_state.format:
                    handle_battle_royale_elimination()
                else:
                    # Generic next round for League
                    standings = get_cumulative_standings()
                    for t_data in standings:
                        t = t_data['Team']
                        st.session_state.cumulative_stats[t] = {k:v for k,v in t_data.items() if k != 'Team'}
                    
                    st.session_state.round_number += 1
                    matches = list(itertools.permutations(st.session_state.teams, 2))
                    random.shuffle(matches)
                    st.session_state.fixtures = matches[:len(st.session_state.teams)//2]
                    st.session_state.results = {}
                    st.session_state.match_meta = {}
                    save_data_internal(); st.rerun()

        st.markdown("---")
        new_team = st.text_input("NEW CLUB")
        if st.button("ADD"):
            if new_team and new_team not in st.session_state.teams:
                st.session_state.teams.append(new_team)
                st.session_state.team_badges[new_team] = random.choice(BADGE_POOL)
                if st.session_state.started:
                    st.session_state.active_teams.append(new_team)
                    st.session_state.cumulative_stats[new_team] = {'P':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0}
                    st.toast(f"{new_team} Joined!")
                save_data_internal(); st.rerun()
                
        if st.button("🧨 RESET ALL"):
            st.session_state.clear(); 
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

# --- MAIN TABS ---
if not st.session_state.started:
    if st.session_state.admin_unlock:
        if st.button("🚀 START BATTLE ROYALE"):
            if len(st.session_state.teams) < 2: st.error("Need 2+ Teams")
            else:
                st.session_state.format = "Survival"
                st.session_state.active_teams = st.session_state.teams.copy()
                st.session_state.cumulative_stats = {t: {'P':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0} for t in st.session_state.teams}
                st.session_state.fixtures = generate_fixtures_for_phase(st.session_state.teams, "Phase 1: The Purge")
                st.session_state.started = True
                save_data_internal(); st.rerun()
    
    st.write(f"Teams Ready: {len(st.session_state.teams)}")
    cols = st.columns(4)
    for i, t in enumerate(st.session_state.teams):
        cols[i%4].markdown(f"**{t}**")

else:
    t1, t2, t3, t4 = st.tabs(["📊 TABLE", "⚽ MATCHES", "⭐ STATS", "ℹ️ INFO"])
    
    with t1:
        standings = get_cumulative_standings()
        standings.sort(key=lambda x: (x['Pts'], x['GD'], x['GF']), reverse=True)
        
        df = pd.DataFrame(standings)
        if not df.empty:
            st.dataframe(df[['Team', 'P', 'W', 'D', 'L', 'GF', 'GA', 'GD', 'Pts']], 
                         hide_index=True, use_container_width=True,
                         column_config={"Pts": st.column_config.ProgressColumn("Pts", format="%d", min_value=0, max_value=int(df['Pts'].max())+10)})
            
            if "Survival" in st.session_state.format:
                count = len(df)
                if count >= 5: drop = 2
                elif count == 4: drop = 1
                else: drop = 0
                if drop > 0: st.warning(f"⚠️ BOTTOM {drop} TEAMS WILL BE ELIMINATED")

    with t2:
        for i, fix in enumerate(st.session_state.fixtures):
            if len(fix) < 2: continue
            h, a = fix[0], fix[1]
            
            # FIX: Use safe separator for new matches
            legacy_key = f"{h}v{a}_{i}"
            new_key = f"{h}|vs|{a}_{i}"
            mid = legacy_key if legacy_key in st.session_state.results else new_key
            res = st.session_state.results.get(mid)
            
            with st.container():
                st.markdown("<div class='glass-panel'>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([4,2,4])
                c1.markdown(f"<h3 style='text-align:right'>{h}</h3>", unsafe_allow_html=True)
                if res:
                    c2.markdown(f"<h2 style='text-align:center;color:#3b82f6'>{res[0]} - {res[1]}</h2>", unsafe_allow_html=True)
                else:
                    c2.markdown(f"<h2 style='text-align:center;color:#666'>VS</h2>", unsafe_allow_html=True)
                c3.markdown(f"<h3 style='text-align:left'>{a}</h3>", unsafe_allow_html=True)
                
                if st.session_state.admin_unlock:
                    with st.expander("Update"):
                        cc1, cc2 = st.columns(2)
                        s1 = cc1.number_input("Home", 0, 20, key=f"h_{mid}")
                        s2 = cc2.number_input("Away", 0, 20, key=f"a_{mid}")
                        
                        # Penalties visually supported but don't give extra points
                        p1, p2 = 0, 0
                        if s1 == s2:
                            st.caption("Penalties")
                            p1 = cc1.number_input("P(H)", 0, 20, key=f"ph_{mid}")
                            p2 = cc2.number_input("P(A)", 0, 20, key=f"pa_{mid}")
                            
                        # Stats Inputs
                        meta = st.session_state.match_meta.get(mid, {})
                        gs1 = st.text_input("Goals (Home)", value=meta.get('h_s',''), key=f"g1_{mid}")
                        gs2 = st.text_input("Goals (Away)", value=meta.get('a_s',''), key=f"g2_{mid}")
                        
                        if st.button("SAVE", key=f"sav_{mid}"):
                            if s1 == s2: st.session_state.results[mid] = [s1, s2, p1, p2]
                            else: st.session_state.results[mid] = [s1, s2]
                            
                            st.session_state.match_meta[mid] = {'h_s': gs1, 'a_s': gs2, 'h_a': '', 'a_a': '', 'h_r': '', 'a_r': ''}
                            save_data_internal(); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    with t3:
        update_cumulative_player_stats() # Refresh
        p_stats = st.session_state.cumulative_player_stats
        if p_stats:
            data = list(p_stats.values())
            df = pd.DataFrame(data)
            st.dataframe(df.sort_values(by='G', ascending=False), use_container_width=True)
        else:
            st.info("No stats yet")

    with t4:
        st.markdown("### 📰 NEWS FEED")
        for n in st.session_state.news:
            st.markdown(f"- {n}", unsafe_allow_html=True)
