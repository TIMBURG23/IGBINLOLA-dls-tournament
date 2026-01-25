import streamlit as st
import pandas as pd
import numpy as np
import itertools
import random
import json
import os
import time
import re

# --- CONFIGURATION ---
st.set_page_config(
    page_title="DLS26 Tournaments", 
    page_icon="⚽", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- 💎 NEXT-GEN CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Teko:wght@300;500;700&family=Rajdhani:wght@500;700&display=swap');

    .stApp {
        background-color: #09090b;
        background-image: radial-gradient(circle at 50% 0%, #111827 0%, transparent 80%), url("https://www.transparenttextures.com/patterns/cubes.png");
        color: white;
    }
    
    h1, h2, h3 { 
        font-family: 'Teko', sans-serif !important; 
        text-transform: uppercase; 
        margin: 0 !important; 
    }
    
    .big-title {
        font-size: 5rem; 
        font-weight: 700; 
        text-align: center;
        background: linear-gradient(180deg, #fff 0%, #64748b 100%);
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(59, 130, 246, 0.3);
    }
    
    .subtitle { 
        font-family: 'Rajdhani', sans-serif; 
        color: #3b82f6; 
        text-align: center; 
        letter-spacing: 4px; 
        margin-bottom: 30px; 
        font-weight: bold; 
    }
    
    .glass-panel {
        background: rgba(255, 255, 255, 0.03); 
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05); 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 15px;
    }
    
    /* NEWS TICKER STYLE */
    .news-ticker {
        background: rgba(59, 130, 246, 0.1); 
        border-left: 4px solid #3b82f6; 
        padding: 10px; 
        margin-bottom: 20px;
        font-family: 'Rajdhani'; 
        font-size: 1.1rem; 
        color: #93c5fd;
    }

    .club-badge { 
        font-size: 3rem; 
        margin-bottom: 10px; 
        filter: drop-shadow(0 0 10px rgba(255,255,255,0.2)); 
    }
    
    .club-name { 
        font-family: 'Teko', sans-serif; 
        font-size: 1.5rem; 
        color: #e2e8f0; 
        letter-spacing: 1px; 
    }

    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background: rgba(0,0,0,0.6) !important; 
        color: white !important; 
        border: 1px solid #334155 !important; 
        border-radius: 6px;
    }
    
    .stButton > button {
        background: transparent; 
        border: 1px solid #3b82f6; 
        color: #3b82f6;
        font-family: 'Rajdhani', sans-serif; 
        font-weight: 700; 
        text-transform: uppercase; 
        transition: 0.3s; 
        width: 100%;
    }
    
    .stButton > button:hover { 
        background: #3b82f6; 
        color: white; 
        box-shadow: 0 0 15px rgba(59, 130, 246, 0.6); 
    }
    
    .footer { 
        text-align: center; 
        padding: 20px; 
        color: #475569; 
        font-family: 'Rajdhani'; 
        border-top: 1px solid #1e293b; 
        margin-top: 50px; 
    }
    
    .designer-name { 
        color: #3b82f6; 
        font-weight: bold; 
        letter-spacing: 1px; 
    }
</style>
""", unsafe_allow_html=True)

# --- 💾 DATABASE LOGIC ---
DB_FILE = "dls_ultra_db.json"
BADGE_POOL = ["🦁", "🦅", "🐺", "🐉", "🦈", "🐍", "🐻", "🐝", "🦂", "🕷️", "⚓", "⚔️", "🛡️", "👑", "⚡", "🔥", "🌪️", "🌊", "🏰", "🚀", "💀", "👹", "👽", "🤖", "👻", "🎃", "💎", "🎯", "🎲", "🎱"]

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                data = json.load(f)
                st.session_state.teams = data.get("teams", [])
                st.session_state.format = data.get("format", "League") 
                st.session_state.current_round = data.get("current_round", "Group Stage")
                st.session_state.fixtures = [tuple(f) for f in data.get("fixtures", [])]
                st.session_state.results = data.get("results", {})
                st.session_state.team_stats = data.get("team_stats", {})
                st.session_state.player_stats = data.get("player_stats", {}) 
                st.session_state.started = data.get("started", False)
                st.session_state.groups = data.get("groups", {}) 
                st.session_state.champion = data.get("champion", None)
                st.session_state.active_teams = data.get("active_teams", [])
                st.session_state.team_badges = data.get("team_badges", {})
                st.session_state.news = data.get("news", ["Welcome to the Season!"])
                
                # Integrity Check: Assign badges to teams that missed them
                for team in st.session_state.teams:
                    if team not in st.session_state.team_badges:
                        st.session_state.team_badges[team] = random.choice(BADGE_POOL)
                    # Init form if missing
                    if team in st.session_state.team_stats and 'Form' not in st.session_state.team_stats[team]:
                        st.session_state.team_stats[team]['Form'] = []
        except: 
            init_defaults()
    else: 
        init_defaults()

def init_defaults():
    defaults = {
        'teams': [], 'format': 'League', 'current_round': 'Group Stage',
        'fixtures': [], 'results': {}, 'team_stats': {}, 'player_stats': {}, 
        'started': False, 'groups': {}, 'champion': None, 'active_teams': [], 
        'is_admin': False, 'team_badges': {}, 'news': ["Welcome to the Season!"]
    }
    for k, v in defaults.items():
        if k not in st.session_state: 
            st.session_state[k] = v

def save_data():
    data = {
        "teams": st.session_state.teams, 
        "format": st.session_state.format, 
        "current_round": st.session_state.current_round,
        "fixtures": st.session_state.fixtures, 
        "results": st.session_state.results,
        "team_stats": st.session_state.team_stats, 
        "player_stats": st.session_state.player_stats,
        "started": st.session_state.started, 
        "groups": st.session_state.groups, 
        "champion": st.session_state.champion, 
        "active_teams": st.session_state.active_teams,
        "team_badges": st.session_state.team_badges,
        "news": st.session_state.news
    }
    with open(DB_FILE, "w") as f: 
        json.dump(data, f)

def add_news(msg):
    """Adds a headline to the ticker"""
    st.session_state.news.insert(0, f"📢 {msg}")
    # Keep only last 5 headlines
    if len(st.session_state.news) > 5: 
        st.session_state.news.pop()

# --- 🧠 PROGRESSION LOGIC ---
def check_round_complete():
    if not st.session_state.fixtures: 
        return False
    for h, a in st.session_state.fixtures:
        mid = f"{h}v{a}"
        if mid not in st.session_state.results: 
            return False
    return True

def advance_round():
    # === SURVIVAL MODE LOGIC ===
    if "Survival" in st.session_state.format:
        data = []
        for t in st.session_state.active_teams:
            if t in st.session_state.team_stats: 
                data.append(st.session_state.team_stats[t] | {'Club': t})
        
        df = pd.DataFrame(data).sort_values(by=['Pts', 'GD', 'GF'], ascending=False)
        
        # Check Winner
        if len(st.session_state.active_teams) <= 2:
            st.session_state.champion = df.iloc[0]['Club']
            add_news(f"CHAMPION CROWNED: {st.session_state.champion} wins the Survival Mode!")
            st.balloons()
            save_data()
            st.rerun()
            return

        # Eliminate Teams
        drop_count = 2 if len(st.session_state.active_teams) > 4 else 1
        eliminated = df.tail(drop_count)['Club'].tolist()
        
        for team in eliminated:
            st.session_state.active_teams.remove(team)
            add_news(f"ELIMINATED: {team} has been dropped from the league!")
            st.toast(f"☠️ {team} ELIMINATED!")

        # Setup Next Round
        remaining = st.session_state.active_teams.copy()
        
        if len(remaining) == 3:
            # Special Semi-Final Logic (1st gets Bye)
            data_rem = []
            for t in remaining: 
                data_rem.append(st.session_state.team_stats[t] | {'Club': t})
            df_rem = pd.DataFrame(data_rem).sort_values(by=['Pts', 'GD', 'GF'], ascending=False)
            
            leader = df_rem.iloc[0]['Club']
            p2 = df_rem.iloc[1]['Club']
            p3 = df_rem.iloc[2]['Club']
            
            st.session_state.current_round = f"SEMI-FINAL (BYE: {leader})"
            st.session_state.fixtures = [(p2, p3)]
            
        elif len(remaining) == 2:
            st.session_state.current_round = "THE FINAL DUEL"
            st.session_state.fixtures = [(remaining[0], remaining[1])]
            
        else:
            random.shuffle(remaining)
            new_fixtures = []
            for i in range(0, len(remaining), 2):
                if i+1 < len(remaining): 
                    new_fixtures.append((remaining[i], remaining[i+1]))
            st.session_state.fixtures = new_fixtures
            st.session_state.current_round = f"Round of {len(remaining)}"
            
        st.session_state.results = {}

    # === WORLD CUP LOGIC ===
    elif st.session_state.current_round == "Group Stage":
        qualified = []
        for g, teams in st.session_state.groups.items():
            g_data = []
            for t in teams:
                if t in st.session_state.team_stats: 
                    g_data.append(st.session_state.team_stats[t] | {'Club': t})
            df = pd.DataFrame(g_data).sort_values(by=['Pts', 'GD', 'GF'], ascending=False)
            if len(df) >= 2: 
                qualified.append(df.iloc[0]['Club'])
                qualified.append(df.iloc[1]['Club'])
        
        if len(qualified) < 2: 
            st.error("Not enough teams to advance!")
            return
        
        random.shuffle(qualified)
        new_fixtures = []
        for i in range(0, len(qualified), 2):
            if i+1 < len(qualified): 
                new_fixtures.append((qualified[i], qualified[i+1]))
        
        st.session_state.fixtures = new_fixtures
        st.session_state.results = {}
        st.session_state.current_round = "Knockout Stage"
        add_news("Knockout Stage Begins! Top teams advance.")

    # === STANDARD KNOCKOUT LOGIC ===
    else:
        winners = []
        for h, a in st.session_state.fixtures:
            mid = f"{h}v{a}"
            res = st.session_state.results.get(mid) # Format: [h, a, pen_h, pen_a]
            
            # Check Penalties first
            if len(res) > 2 and (res[2] > 0 or res[3] > 0):
                if res[2] > res[3]: winners.append(h)
                else: winners.append(a)
            # Regular Score
            elif res[0] > res[1]: 
                winners.append(h)
            elif res[1] > res[0]: 
                winners.append(a)
            # Draw Fallback (Random)
            else:
                winners.append(random.choice([h, a]))
        
        if len(winners) == 1:
            st.session_state.champion = winners[0]
            add_news(f"🏆 {winners[0]} is the CHAMPION!")
            st.balloons()
        else:
            new_fixtures = []
            for i in range(0, len(winners), 2):
                if i+1 < len(winners): 
                    new_fixtures.append((winners[i], winners[i+1]))
            st.session_state.fixtures = new_fixtures
            st.session_state.results = {}
            
            if len(winners) == 2: 
                st.session_state.current_round = "GRAND FINAL"
            elif len(winners) == 4: 
                st.session_state.current_round = "SEMI FINALS"
            
            add_news(f"{st.session_state.current_round} Generated!")

    save_data()
    st.rerun()

# --- 🧠 SMART PARSER ---
def parse_and_update_stats(raw_input, stat_type, team_name):
    """Parses 'Messi (2), Ronaldo' strings"""
    if not raw_input or raw_input.strip() == "": return
    
    entries = raw_input.split(',')
    for entry in entries:
        entry = entry.strip()
        if not entry: continue
        
        count = 1
        clean_name = entry
        
        # Regex for Name (N) or Name xN
        match_bracket = re.search(r'^(.*?)\s*\((\d+)\)$', entry)
        match_multiplier = re.search(r'^(.*?)\s*[xX](\d+)$', entry)
        
        if match_bracket:
            clean_name = match_bracket.group(1)
            count = int(match_bracket.group(2))
        elif match_multiplier:
            clean_name = match_multiplier.group(1)
            count = int(match_multiplier.group(2))
            
        clean_name = clean_name.strip().title()
        
        for _ in range(count):
            if clean_name not in st.session_state.player_stats:
                st.session_state.player_stats[clean_name] = {"G": 0, "A": 0, "R": 0, "Team": team_name}
            # Update team just in case
            st.session_state.player_stats[clean_name]["Team"] = team_name
            st.session_state.player_stats[clean_name][stat_type] += 1

# --- INIT ---
if 'init' not in st.session_state:
    load_data()
    st.session_state.init = True

# --- 🏆 HEADER ---
st.markdown('<div class="big-title">DLS ULTRA</div>', unsafe_allow_html=True)
if st.session_state.champion:
    st.markdown(f'<div class="subtitle" style="color:#FFD700">👑 CHAMPION: {st.session_state.champion} 👑</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="subtitle">{st.session_state.current_round} /// V8.0</div>', unsafe_allow_html=True)

# --- NEWS TICKER ---
if st.session_state.started:
    if st.session_state.news:
        news_html = " &nbsp;&nbsp;&bull;&nbsp;&nbsp; ".join(st.session_state.news)
        st.markdown(f"<div class='news-ticker'>📰 BREAKING: {news_html}</div>", unsafe_allow_html=True)

# --- 🔒 SIDEBAR (ADMIN) ---
with st.sidebar:
    st.markdown("### 🔐 Oluwatimileyin and Bob ACCESS")
    pin = st.text_input("ENTER PIN", type="password")
    
    if pin == "0209": 
        st.session_state.is_admin = True
        st.success("ACCESS GRANTED")
    else: 
        st.session_state.is_admin = False

    if st.session_state.is_admin:
        st.markdown("---")
        # Round Progression Controls
        if st.session_state.started and not st.session_state.champion:
            if check_round_complete():
                st.success("✅ ROUND COMPLETE")
                if st.button("⏩ GENERATE NEXT ROUND"): 
                    advance_round()
            else: 
                st.info("Finish matches to advance.")

        st.markdown("---")
        st.markdown("### ⚙️ TEAM EDITOR")
        
        # Add Team
        new_team = st.text_input("REGISTER NEW CLUB")
        if st.button("ADD CLUB"):
            if new_team and new_team not in st.session_state.teams:
                st.session_state.teams.append(new_team)
                st.session_state.team_badges[new_team] = random.choice(BADGE_POOL)
                st.session_state.team_stats[new_team] = {'P':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0, 'Form':[]}
                save_data()
                st.rerun()

        # Edit/Delete Team
        edit_target = st.selectbox("SELECT CLUB", ["Select..."] + st.session_state.teams)
        if edit_target != "Select...":
            c1, c2 = st.columns(2)
            if c1.button("🗑️ DELETE"):
                st.session_state.teams.remove(edit_target)
                if edit_target in st.session_state.team_stats: 
                    del st.session_state.team_stats[edit_target]
                save_data()
                st.rerun()
            
            rename_val = c2.text_input("RENAME TO", value=edit_target)
            if c2.button("RENAME"):
                idx = st.session_state.teams.index(edit_target)
                st.session_state.teams[idx] = rename_val
                st.session_state.team_stats[rename_val] = st.session_state.team_stats.pop(edit_target)
                st.session_state.team_badges[rename_val] = st.session_state.team_badges.pop(edit_target)
                save_data()
                st.rerun()

        # Backup System
        st.markdown("---")
        st.markdown("### 💾 BACKUP")
        current_data = json.dumps({
            "teams": st.session_state.teams, "format": st.session_state.format, 
            "current_round": st.session_state.current_round, "fixtures": st.session_state.fixtures, 
            "results": st.session_state.results, "team_stats": st.session_state.team_stats, 
            "player_stats": st.session_state.player_stats, "started": st.session_state.started, 
            "groups": st.session_state.groups, "champion": st.session_state.champion, 
            "active_teams": st.session_state.active_teams, "team_badges": st.session_state.team_badges,
            "news": st.session_state.news
        })
        st.download_button("📥 DOWNLOAD SAVE", data=current_data, file_name="dls_backup.json", mime="application/json")
        
        uploaded = st.file_uploader("📤 RESTORE SAVE", type=['json'])
        if uploaded and st.button("⚠️ RESTORE"):
            data = json.load(uploaded)
            st.session_state.teams = data["teams"]
            st.session_state.fixtures = [tuple(f) for f in data["fixtures"]]
            st.session_state.results = data["results"]
            st.session_state.team_stats = data["team_stats"]
            st.session_state.player_stats = data.get("player_stats", {})
            st.session_state.started = data.get("started", False)
            st.session_state.groups = data.get("groups", {})
            st.session_state.current_round = data.get("current_round", "Group Stage")
            st.session_state.champion = data.get("champion", None)
            st.session_state.active_teams = data.get("active_teams", [])
            st.session_state.team_badges = data.get("team_badges", {})
            st.session_state.news = data.get("news", [])
            save_data()
            st.rerun()
        
        if st.button("🧨 FACTORY RESET"):
            st.session_state.clear()
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.rerun()

# --- 🎮 MAIN INTERFACE ---
if not st.session_state.started:
    # LOBBY SCREEN
    st.markdown(f"<div class='glass-panel' style='text-align:center'><h3>CLUBS READY: {len(st.session_state.teams)}</h3></div>", unsafe_allow_html=True)
    
    if st.session_state.teams:
        cols = st.columns(4)
        for i, team in enumerate(st.session_state.teams):
            badge = st.session_state.team_badges.get(team, "🛡️")
            with cols[i%4]:
                st.markdown(f"""
                <div class='glass-panel' style='text-align:center;'>
                    <div class='club-badge'>{badge}</div>
                    <div class='club-name'>{team}</div>
                </div>
                """, unsafe_allow_html=True)

    if st.session_state.is_admin:
        st.markdown("### 🏆 SELECT FORMAT")
        fmt = st.radio("", ["Home & Away League", "World Cup (Groups + Knockout)", "Classic Knockout", "Survival Mode (Battle Royale)"], horizontal=True)
        
        if st.button("🚀 INITIALIZE SEASON"):
            if len(st.session_state.teams) < 2: 
                st.error("Need 2+ Teams")
            else:
                st.session_state.format = fmt
                st.session_state.current_round = "Group Stage" if "World" in fmt else ("League Phase" if "League" in fmt else ("Round 1" if "Survival" in fmt else "Knockout Round"))
                st.session_state.active_teams = st.session_state.teams.copy() # For Survival Mode
                
                # GENERATE FIXTURES
                if "League" in fmt:
                    matches = list(itertools.permutations(st.session_state.teams, 2))
                    random.shuffle(matches)
                    st.session_state.fixtures = matches
                
                elif "World Cup" in fmt:
                    shuffled = st.session_state.teams.copy()
                    random.shuffle(shuffled)
                    groups = {}
                    group_names = "ABCDEFGH"
                    for i in range(0, len(shuffled), 4):
                        g_name = group_names[i//4]
                        groups[g_name] = shuffled[i:i+4]
                    st.session_state.groups = groups
                    matches = []
                    for g, teams in groups.items(): 
                        matches.extend(list(itertools.combinations(teams, 2)))
                    st.session_state.fixtures = matches
                
                elif "Survival" in fmt:
                    shuffled = st.session_state.teams.copy()
                    random.shuffle(shuffled)
                    matches = []
                    for i in range(0, len(shuffled), 2):
                        if i+1 < len(shuffled): 
                            matches.append((shuffled[i], shuffled[i+1]))
                    st.session_state.fixtures = matches
                
                elif "Knockout" in fmt:
                    shuffled = st.session_state.teams.copy()
                    random.shuffle(shuffled)
                    matches = []
                    for i in range(0, len(shuffled), 2):
                        if i+1 < len(shuffled): 
                            matches.append((shuffled[i], shuffled[i+1]))
                    st.session_state.fixtures = matches

                st.session_state.started = True
                
                # Init stats
                for t in st.session_state.teams: 
                    st.session_state.team_stats[t] = {'P':0,'W':0,'D':0,'L':0,'GF':0,'GA':0,'GD':0,'Pts':0, 'Form':[]}
                
                add_news("Season Initialized!")
                save_data()
                st.rerun()

else:
    # LIVE TOURNAMENT SCREEN
    if st.session_state.champion:
        st.markdown(f"""
        <div style="text-align:center; margin-top:50px;">
            <h1 style="font-size:8rem; color:#FFD700; text-shadow:0 0 50px #FFD700;">🏆</h1>
            <h1 style="font-size:4rem;">{st.session_state.champion}</h1>
            <h3 style="color:#94a3b8;">TOURNAMENT CHAMPION</h3>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
    else:
        tab1, tab2, tab3 = st.tabs(["📊 STANDINGS", "⚽ MATCH CENTER", "⭐ STATS"])

        # HELPER FOR TABLE RENDER
        def render_table(teams_list):
            data = []
            for t in teams_list:
                if t in st.session_state.team_stats:
                    stats = st.session_state.team_stats[t]
                    # Form Icons
                    form_str = "".join([f"{'✅' if x=='W' else ('❌' if x=='L' else '➖')}" for x in stats.get('Form', [])[-5:]])
                    data.append(stats | {'Club': t, 'Form': form_str})
            
            if data:
                df = pd.DataFrame(data).sort_values(by=['Pts', 'GD', 'GF'], ascending=False).reset_index(drop=True)
                df.index += 1
                st.dataframe(df[['Club','P','W','D','L','GF','GA','GD','Pts','Form']], use_container_width=True)

        # TAB 1: TABLES
        with tab1:
            if "Survival" in st.session_state.format:
                st.markdown("### 💀 SURVIVAL TABLE (BOTTOM TEAMS ELIMINATED)")
                render_table(st.session_state.active_teams)
                st.caption("⚠️ The bottom teams in this table will be deleted when the round ends!")

            elif "League" in st.session_state.format:
                st.markdown("### 🇪🇺 LEAGUE TABLE")
                render_table(st.session_state.teams)

            elif "World Cup" in st.session_state.format and st.session_state.current_round == "Group Stage":
                for g_name, teams in st.session_state.groups.items():
                    st.markdown(f"#### GROUP {g_name}")
                    render_table(teams)

            else:
                # Bracket View for Knockouts
                st.markdown(f"### 🥊 {st.session_state.current_round}")
                for h, a in st.session_state.fixtures:
                    mid = f"{h}v{a}"
                    res = st.session_state.results.get(mid)
                    
                    score = f"{res[0]} - {res[1]}" if res else "VS"
                    if res and len(res) > 2: # Has penalties
                        score += f" ({res[2]}-{res[3]} P)"
                        
                    b1 = st.session_state.team_badges.get(h, "🛡️")
                    b2 = st.session_state.team_badges.get(a, "🛡️")
                    
                    st.markdown(f"""
                    <div class="glass-panel" style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:1.5rem; text-align:right; width:40%;">{h} {b1}</span>
                        <span style="font-family:'Teko'; font-size:2rem; background:#1e293b; padding:0 20px; border-radius:10px;">{score}</span>
                        <span style="font-size:1.5rem; text-align:left; width:40%;">{b2} {a}</span>
                    </div>
                    """, unsafe_allow_html=True)

        # TAB 2: MATCH CENTER
        with tab2:
            filter_team = st.selectbox("FILTER TEAM", ["All"] + st.session_state.teams)
            matches_shown = 0
            for i, (h, a) in enumerate(st.session_state.fixtures):
                if filter_team != "All" and filter_team not in [h, a]: continue
                matches_shown += 1
                if matches_shown > 50: break
                mid = f"{h}v{a}"
                res = st.session_state.results.get(mid)
                
                with st.container():
                    st.markdown(f"<div style='margin-top:20px; border-top:1px solid #333; padding-top:10px;'></div>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([3, 2, 3])
                    c1.markdown(f"<h3 style='text-align:right'>{h}</h3>", unsafe_allow_html=True)
                    
                    score_txt = "VS"
                    if res:
                        score_txt = f"{res[0]} - {res[1]}"
                        if len(res) > 2: score_txt += f" (P: {res[2]}-{res[3]})"
                    
                    c2.markdown(f"<h2 style='text-align:center; color:{'#3b82f6' if res else '#64748b'}'>{score_txt}</h2>", unsafe_allow_html=True)
                    c3.markdown(f"<h3 style='text-align:left'>{a}</h3>", unsafe_allow_html=True)

                    if st.session_state.is_admin and not st.session_state.champion:
                        with st.expander(f"📝 EDIT MATCH"):
                            ic1, ic2 = st.columns(2)
                            nh = ic1.number_input(f"{h}", 0, 20, key=f"s_h_{mid}")
                            na = ic2.number_input(f"{a}", 0, 20, key=f"s_a_{mid}")
                            
                            # PENALTY LOGIC
                            is_knockout = "Survival" in st.session_state.format or "Knockout" in st.session_state.format or st.session_state.current_round != "Group Stage"
                            
                            if "League" not in st.session_state.format and is_knockout and nh == na:
                                st.caption("🤝 DRAW! ENTER PENALTY SCORE:")
                                pc1, pc2 = st.columns(2)
                                ph = pc1.number_input(f"Pens {h}", 0, 20, key=f"p_h_{mid}")
                                pa = pc2.number_input(f"Pens {a}", 0, 20, key=f"p_a_{mid}")
                            else:
                                ph, pa = 0, 0

                            st.caption("Stats: 'Haaland (2), KDB'")
                            sc1, sc2 = st.columns(2)
                            h_s = sc1.text_input(f"Scorers", key=f"g_h_{mid}")
                            a_s = sc2.text_input(f"Scorers", key=f"g_a_{mid}")
                            h_a = sc1.text_input(f"Assists", key=f"a_h_{mid}")
                            a_a = sc2.text_input(f"Assists", key=f"a_a_{mid}")
                            h_r = sc1.text_input(f"Reds", key=f"r_h_{mid}")
                            a_r = sc2.text_input(f"Reds", key=f"r_a_{mid}")

                            if st.button("CONFIRM", key=f"btn_{mid}"):
                                # Save Result
                                if nh == na and is_knockout and "League" not in st.session_state.format:
                                    st.session_state.results[mid] = [nh, na, ph, pa]
                                    winner = h if ph > pa else a
                                    add_news(f"{winner} wins on penalties ({ph}-{pa}) against {a if winner==h else h}!")
                                else:
                                    st.session_state.results[mid] = [nh, na]
                                    if nh > na: add_news(f"{h} beats {a} ({nh}-{na})")
                                    elif na > nh: add_news(f"{a} beats {h} ({na}-{nh})")

                                # Update Table Stats
                                t1 = st.session_state.team_stats[h]
                                t2 = st.session_state.team_stats[a]
                                
                                t1['P']+=1; t1['GF']+=nh; t1['GA']+=na; t1['GD']+=(nh-na)
                                t2['P']+=1; t2['GF']+=na; t2['GA']+=nh; t2['GD']+=(na-nh)
                                
                                # Points & Form
                                if nh > na: 
                                    t1['W']+=1; t1['Pts']+=3; t2['L']+=1
                                    t1['Form'].append('W'); t2['Form'].append('L')
                                elif na > nh: 
                                    t2['W']+=1; t2['Pts']+=3; t1['L']+=1
                                    t2['Form'].append('W'); t1['Form'].append('L')
                                else: 
                                    t1['D']+=1; t1['Pts']+=1; t2['D']+=1; t2['Pts']+=1
                                    t1['Form'].append('D'); t2['Form'].append('D')

                                # Update Player Stats
                                parse_and_update_stats(h_s, "G", h)
                                parse_and_update_stats(a_s, "G", a)
                                parse_and_update_stats(h_a, "A", h)
                                parse_and_update_stats(a_a, "A", a)
                                parse_and_update_stats(h_r, "R", h)
                                parse_and_update_stats(a_r, "R", a)
                                
                                save_data()
                                st.success("SAVED")
                                st.rerun()

        # TAB 3: PLAYER STATS
        with tab3:
            st.markdown("### ⭐ HALL OF FAME")
            if st.session_state.player_stats:
                p_data = []
                for name, stats in st.session_state.player_stats.items(): 
                    p_data.append({'Name': name} | stats)
                
                pdf = pd.DataFrame(p_data)
                
                c1, c2, c3 = st.columns(3)
                
                c1.markdown("#### ⚽ GOALS")
                c1.dataframe(pdf.sort_values("G", ascending=False).head(10)[['Name','Team','G']], use_container_width=True)
                
                c2.markdown("#### 👟 ASSISTS")
                c2.dataframe(pdf.sort_values("A", ascending=False).head(10)[['Name','Team','A']], use_container_width=True)
                
                c3.markdown("#### 🟥 RED CARDS")
                c3.dataframe(pdf.sort_values("R", ascending=False).head(10)[['Name','Team','R']], use_container_width=True)
            else:
                st.info("No stats recorded yet.")

# --- FOOTER ---
st.markdown("""
<div class="footer">
   DLS26 TOURNAMENT <br> 
    WRITTEN AND DESIGNED BY <span class="designer-name">OLUWATIMILEYIN IGBINLOLA</span>
</div>
""", unsafe_allow_html=True)
