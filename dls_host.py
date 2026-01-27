import streamlit as st
import pandas as pd
import itertools
import random
import json
import os
import re

# --- CONFIGURATION ---
st.set_page_config(page_title="DLS Ultra Manager", page_icon="⚽", layout="wide", initial_sidebar_state="collapsed")

# --- CSS STYLING (Classic Dark) ---
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
        'is_admin': False, 'team_badges': {}, 'news': []
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
                st.session_state.fixtures = [tuple(f) for f in data.get("fixtures", [])]
                st.session_state.results = data.get("results", {}) 
                st.session_state.match_meta = data.get("match_meta", {}) 
                st.session_state.started = data.get("started", False)
                st.session_state.groups = data.get("groups", {}) 
                st.session_state.champion = data.get("champion", None)
                st.session_state.active_teams = data.get("active_teams", [])
                st.session_state.team_badges = data.get("team_badges", {})
                st.session_state.news = data.get("news", [])
                
                for t in st.session_state.teams:
                    if t not in st.session_state.team_badges:
                        st.session_state.team_badges[t] = random.choice(BADGE_POOL)
        except: init_defaults()
    else: init_defaults()

def save_data():
    data = {
        "teams": st.session_state.teams, "format": st.session_state.format,
        "current_round": st.session_state.current_round, "fixtures": st.session_state.fixtures,
        "results": st.session_state.results, "match_meta": st.session_state.match_meta,
        "started": st.session_state.started, "groups": st.session_state.groups,
        "champion": st.session_state.champion, "active_teams": st.session_state.active_teams,
        "team_badges": st.session_state.team_badges, "news": st.session_state.news
    }
    with open(DB_FILE, "w") as f: json.dump(data, f)

# --- 🧠 RECALCULATION ENGINE (PURE) ---
def recalculate_stats():
    # 1. Reset everything to clean slate
    t_stats = {t: {'P':0, 'W':0, 'D':0, 'L':0, 'GF':0, 'GA':0, 'GD':0, 'Pts':0, 'Form': []} for t in st.session_state.teams}
    p_stats = {} 

    # 2. Replay history strictly from Saved Matches
    for mid, res in st.session_state.results.items():
        try:
            h, a = mid.split('v')
        except: continue
        
        if h not in t_stats or a not in t_stats: continue 

        s_h, s_a = res[0], res[1]
        
        # Team Stats
        t_stats[h]['P'] += 1; t_stats[a]['P'] += 1
        t_stats[h]['GF'] += s_h; t_stats[h]['GA'] += s_a; t_stats[h]['GD'] += (s_h - s_a)
        t_stats[a]['GF'] += s_a; t_stats[a]['GA'] += s_h; t_stats[a]['GD'] += (s_a - s_h)

        if s_h > s_a:
            t_stats[h]['W'] += 1; t_stats[h]['Pts'] += 3; t_stats[a]['L'] += 1
            t_stats[h]['Form'].append('W'); t_stats[a]['Form'].append('L')
        elif s_a > s_h:
            t_stats[a]['W'] += 1; t_stats[a]['Pts'] += 3; t_stats[h]['L'] += 1
            t_stats[a]['Form'].append('W'); t_stats[h]['Form'].append('L')
        else:
            t_stats[h]['D'] += 1; t_stats[h]['Pts'] += 1; t_stats[a]['D'] += 1; t_stats[a]['Pts'] += 1
            t_stats[h]['Form'].append('D'); t_stats[a]['Form'].append('D')

        # Player Stats (From Reports)
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
                uid = (name, team)
                if uid not in p_stats: p_stats[uid] = {'G':0, 'A':0, 'R':0}
                p_stats[uid][stat_type] += count

        process_player_string(meta.get('h_s', ''), h, 'G')
        process_player_string(meta.get('a_s', ''), a, 'G')
        process_player_string(meta.get('h_a', ''), h, 'A')
        process_player_string(meta.get('a_a', ''), a, 'A')
        process_player_string(meta.get('h_r', ''), h, 'R')
        process_player_string(meta.get('a_r', ''), a, 'R')

    return t_stats, p_stats

if 'init' not in st.session_state:
    load_data()
    st.session_state.init = True

init_defaults()
current_team_stats, current_player_stats = recalculate_stats()

# --- 🏆 HEADER ---
st.markdown('<div class="big-title">DLS ULTRA</div>', unsafe_allow_html=True)
if st.session_state.champion:
    st.markdown(f'<div class="subtitle" style="color:#FFD700">👑 CHAMPION: {st.session_state.champion} 👑</div>', unsafe_allow_html=True)
else:
    st.markdown(f'<div class="subtitle">{st.session_state.current_round} /// V12.0</div>', unsafe_allow_html=True)

# --- 🔒 SIDEBAR ---
with st.sidebar:
    st.markdown("### 🔐 MANAGER ACCESS")
    pin = st.text_input("ENTER PIN", type="password")
    
    if pin == "0209": 
        st.session_state.is_admin = True
        st.success("ACCESS GRANTED")
    else: 
        st.session_state.is_admin = False

    if st.session_state.is_admin:
        st.markdown("---")
        if st.session_state.started and not st.session_state.champion:
            if st.button("⏩ GENERATE NEXT ROUND"): 
                if "Survival" in st.session_state.format:
                    data = []
                    for t in st.session_state.active_teams:
                        if t in current_team_stats: data.append(current_team_stats[t] | {'Team': t})
                    df = pd.DataFrame(data).sort_values(by=['Pts', 'GD'], ascending=False)
                    if len(df) <= 2: 
                        st.session_state.champion = df.iloc[0]['Team']
                    else:
                        drop = 2 if len(df) > 4 else 1
                        elim = df.tail(drop)['Team'].tolist()
                        for e in elim: 
                            if e in st.session_state.active_teams: st.session_state.active_teams.remove(e)
                        rem = st.session_state.active_teams.copy()
                        random.shuffle(rem)
                        nxt = []
                        if len(rem) == 3:
                            d3 = [current_team_stats[t] | {'Team': t} for t in rem]
                            df3 = pd.DataFrame(d3).sort_values(by=['Pts', 'GD'], ascending=False)
                            leader = df3.iloc[0]['Team']
                            nxt = [(df3.iloc[1]['Team'], df3.iloc[2]['Team'])]
                            st.session_state.current_round = f"SEMI (Bye: {leader})"
                        elif len(rem) == 2:
                            nxt = [(rem[0], rem[1])]
                            st.session_state.current_round = "FINAL"
                        else:
                            for i in range(0, len(rem), 2):
                                if i+1 < len(rem): nxt.append((rem[i], rem[i+1]))
                            st.session_state.current_round = f"Round of {len(rem)}"
                        st.session_state.fixtures = nxt; st.session_state.results = {}; st.session_state.match_meta = {}
                        save_data(); st.rerun()
                else: 
                    wins = []
                    for h, a in st.session_state.fixtures:
                        mid = f"{h}v{a}"
                        r = st.session_state.results.get(mid)
                        if not r: wins.append(random.choice([h, a]))
                        else:
                            if r[0] > r[1]: wins.append(h)
                            elif r[1] > r[0]: wins.append(a)
                            elif len(r)>2 and r[2]>r[3]: wins.append(h)
                            else: wins.append(a)
                    if len(wins) == 1: st.session_state.champion = wins[0]
                    else:
                        nxt = []
                        for i in range(0, len(wins), 2):
                            if i+1 < len(wins): nxt.append((wins[i], wins[i+1]))
                        st.session_state.fixtures = nxt; st.session_state.results = {}; st.session_state.match_meta = {}
                        st.session_state.current_round = "NEXT ROUND"
                    save_data(); st.rerun()

        st.markdown("---")
        st.markdown("### ⚙️ TEAM EDITOR")
        new_team = st.text_input("REGISTER NEW CLUB")
        if st.button("ADD CLUB"):
            if new_team and new_team not in st.session_state.teams:
                st.session_state.teams.append(new_team)
                st.session_state.team_badges[new_team] = random.choice(BADGE_POOL)
                save_data(); st.rerun()

        edit_target = st.selectbox("SELECT CLUB", ["Select..."] + st.session_state.teams)
        if edit_target != "Select...":
            c1, c2 = st.columns(2)
            if c1.button("🗑️ DELETE"):
                st.session_state.teams.remove(edit_target)
                save_data(); st.rerun()
            rename_val = c2.text_input("RENAME TO", value=edit_target)
            if c2.button("RENAME"):
                idx = st.session_state.teams.index(edit_target)
                st.session_state.teams[idx] = rename_val
                st.session_state.team_badges[rename_val] = st.session_state.team_badges.pop(edit_target)
                save_data(); st.rerun()

        st.markdown("---")
        st.markdown("### 💾 DATA MANAGEMENT")
        current_data = json.dumps({
            "teams": st.session_state.teams, "format": st.session_state.format, 
            "current_round": st.session_state.current_round, "fixtures": st.session_state.fixtures, 
            "results": st.session_state.results, "match_meta": st.session_state.match_meta, 
            "started": st.session_state.started, "groups": st.session_state.groups, 
            "champion": st.session_state.champion, "active_teams": st.session_state.active_teams, 
            "team_badges": st.session_state.team_badges, "news": st.session_state.news
        })
        st.download_button("📥 DOWNLOAD BACKUP", data=current_data, file_name="dls_backup.json", mime="application/json")
        uploaded = st.file_uploader("📤 RESTORE BACKUP", type=['json'])
        if uploaded and st.button("⚠️ RESTORE NOW"):
            data = json.load(uploaded)
            st.session_state.teams = data["teams"]
            st.session_state.fixtures = [tuple(f) for f in data["fixtures"]]
            st.session_state.results = data["results"]
            st.session_state.match_meta = data.get("match_meta", {})
            st.session_state.started = data.get("started", False)
            st.session_state.groups = data.get("groups", {})
            st.session_state.current_round = data.get("current_round", "Group Stage")
            st.session_state.champion = data.get("champion", None)
            st.session_state.active_teams = data.get("active_teams", [])
            st.session_state.team_badges = data.get("team_badges", {})
            st.session_state.news = data.get("news", [])
            save_data(); st.rerun()
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

    if st.session_state.is_admin:
        st.markdown("### 🏆 SELECT FORMAT")
        fmt = st.radio("", ["Home & Away League", "World Cup (Groups + Knockout)", "Classic Knockout", "Survival Mode (Battle Royale)"], horizontal=True)
        if st.button("🚀 INITIALIZE SEASON"):
            if len(st.session_state.teams) < 2: st.error("Need 2+ Teams")
            else:
                st.session_state.format = fmt
                st.session_state.current_round = "Group Stage" if "World" in fmt else ("League Phase" if "League" in fmt else ("Round 1" if "Survival" in fmt else "Knockout Round"))
                st.session_state.active_teams = st.session_state.teams.copy()
                if "League" in fmt: matches = list(itertools.permutations(st.session_state.teams, 2)); random.shuffle(matches)
                elif "World Cup" in fmt:
                    shuffled = st.session_state.teams.copy(); random.shuffle(shuffled); groups = {}; group_names = "ABCDEFGH"
                    for i in range(0, len(shuffled), 4): groups[group_names[i//4]] = shuffled[i:i+4]
                    st.session_state.groups = groups; matches = []
                    for g, teams in groups.items(): matches.extend(list(itertools.combinations(teams, 2)))
                elif "Survival" in fmt:
                    shuffled = st.session_state.teams.copy(); random.shuffle(shuffled); matches = []
                    for i in range(0, len(shuffled), 2):
                        if i+1 < len(shuffled): matches.append((shuffled[i], shuffled[i+1]))
                elif "Knockout" in fmt:
                    shuffled = st.session_state.teams.copy(); random.shuffle(shuffled); matches = []
                    for i in range(0, len(shuffled), 2):
                        if i+1 < len(shuffled): matches.append((shuffled[i], shuffled[i+1]))
                st.session_state.fixtures = matches
                st.session_state.started = True
                save_data(); st.rerun()

else:
    tab1, tab2, tab3 = st.tabs(["📊 STANDINGS", "⚽ MATCH CENTER", "⭐ STATS"])

    with tab1:
        def render_table(team_list):
            rows = []
            for t in team_list:
                if t in current_team_stats:
                    s = current_team_stats[t]
                    form_viz = "".join(["✅" if x=='W' else "🟥" if x=='L' else "⬜" for x in s['Form'][-5:]])
                    badge = st.session_state.team_badges.get(t, "🛡️")
                    rows.append({"Club": f"{badge} {t}", "P": s['P'], "W": s['W'], "D": s['D'], "L": s['L'], "GF": s['GF'], "GA": s['GA'], "GD": s['GD'], "Pts": s['Pts'], "Form": form_viz})
            if rows:
                df = pd.DataFrame(rows).sort_values(by=['Pts', 'GD', 'GF'], ascending=False)
                max_pts = int(max(df['Pts'].max(), 15))
                st.dataframe(df, hide_index=True, use_container_width=True, column_config={"Pts": st.column_config.ProgressColumn("Pts", format="%d", min_value=0, max_value=max_pts)})

        if "Survival" in st.session_state.format:
            st.markdown("### 💀 SURVIVAL ZONE"); render_table(st.session_state.active_teams)
        elif "League" in st.session_state.format:
            st.markdown("### 🌍 LEAGUE TABLE"); render_table(st.session_state.teams)
        elif "World" in st.session_state.format and "Group" in st.session_state.current_round:
            for g, t in st.session_state.groups.items(): st.markdown(f"#### {g}"); render_table(t)
        else:
            st.markdown("### 🥊 BRACKET")
            for h, a in st.session_state.fixtures:
                mid = f"{h}v{a}"; res = st.session_state.results.get(mid)
                sc = f"{res[0]} - {res[1]}" if res else "VS"
                if res and len(res)>2: sc += f" (P: {res[2]}-{res[3]})"
                st.markdown(f"<div class='glass-panel' style='display:flex; justify-content:space-between'><b>{h}</b> <b>{sc}</b> <b>{a}</b></div>", unsafe_allow_html=True)

    with tab2:
        filter_team = st.selectbox("FILTER TEAM", ["All"] + st.session_state.teams)
        for h, a in st.session_state.fixtures:
            if filter_team != "All" and filter_team not in [h, a]: continue
            mid = f"{h}v{a}"; res = st.session_state.results.get(mid)
            
            with st.container():
                st.markdown(f"<div class='glass-panel'>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns([4, 2, 4])
                b1 = st.session_state.team_badges.get(h, ""); b2 = st.session_state.team_badges.get(a, "")
                c1.markdown(f"<h3 style='text-align:right'>{h} {b1}</h3>", unsafe_allow_html=True)
                if res:
                    sc = f"{res[0]} - {res[1]}"
                    if len(res) > 2: sc += f"\n(P: {res[2]}-{res[3]})"
                    c2.markdown(f"<h1 style='text-align:center; color:#3b82f6'>{sc}</h1>", unsafe_allow_html=True)
                else: c2.markdown(f"<h1 style='text-align:center; color:#64748b'>VS</h1>", unsafe_allow_html=True)
                c3.markdown(f"<h3 style='text-align:left'>{b2} {a}</h3>", unsafe_allow_html=True)
                
                if st.session_state.is_admin and not st.session_state.champion:
                    with st.expander("📝 REPORT"):
                        ac1, ac2 = st.columns(2)
                        s1 = ac1.number_input(f"{h}", 0, 20, key=f"s1_{mid}")
                        s2 = ac2.number_input(f"{a}", 0, 20, key=f"s2_{mid}")
                        p1, p2 = 0, 0
                        if s1 == s2 and "League" not in st.session_state.format:
                            st.caption("Penalties")
                            p1 = ac1.number_input(f"P {h}", 0, 20, key=f"p1_{mid}")
                            p2 = ac2.number_input(f"P {a}", 0, 20, key=f"p2_{mid}")

                        sc1, sc2 = st.columns(2)
                        # PRE-FILL existing data if available to avoid typing again
                        prev = st.session_state.match_meta.get(mid, {})
                        
                        gs1 = sc1.text_input("Scorers (Home)", value=prev.get('h_s',''), key=f"g1_{mid}", placeholder="Messi (2), ...")
                        gs2 = sc2.text_input("Scorers (Away)", value=prev.get('a_s',''), key=f"g2_{mid}")
                        
                        ha = sc1.text_input("Ast H", value=prev.get('h_a',''), key=f"ah_{mid}")
                        aa = sc2.text_input("Ast A", value=prev.get('a_a',''), key=f"aa_{mid}")
                        hr = sc1.text_input("Red H", value=prev.get('h_r',''), key=f"rh_{mid}")
                        ar = sc2.text_input("Red A", value=prev.get('a_r',''), key=f"ra_{mid}")
                        
                        if st.button("CONFIRM RESULT", key=f"b_{mid}"):
                            if s1 == s2 and "League" not in st.session_state.format:
                                st.session_state.results[mid] = [s1, s2, p1, p2]
                            else:
                                st.session_state.results[mid] = [s1, s2]
                            
                            st.session_state.match_meta[mid] = {
                                'h_s': gs1, 'a_s': gs2,
                                'h_a': ha, 'a_a': aa, 'h_r': hr, 'a_r': ar
                            }
                            save_data(); st.success("UPDATED"); st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        if current_player_stats:
            data = []
            for (name, team), s in current_player_stats.items():
                data.append({"Player": name, "Club": team, "Goals": s['G'], "Assists": s['A'], "Reds": s['R']})
            df = pd.DataFrame(data)
            c1, c2, c3 = st.columns(3)
            def show_stat(col, title, key):
                col.markdown(f"#### {title}")
                if not df.empty:
                    top = df.sort_values(by=key, ascending=False).head(10).reset_index(drop=True)
                    top.index += 1
                    col.dataframe(top[['Player', 'Club', key]], use_container_width=True)
            show_stat(c1, "⚽ Goals", "Goals"); show_stat(c2, "👟 Assists", "Assists"); show_stat(c3, "🟥 Reds", "Reds")
        else: st.info("No Goals Recorded Yet")

# --- FOOTER ---
st.markdown("""<div class="footer">OFFICIAL DLS TOURNAMENT ENGINE <br> WRITTEN AND DESIGNED BY <span class="designer-name">OLUWATIMILEYIN IGBINLOLA</span></div>""", unsafe_allow_html=True)
