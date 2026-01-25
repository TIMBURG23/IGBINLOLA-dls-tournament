import streamlit as st
import pandas as pd
import itertools
import random
import json
import os
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="DLS Tournament Week", page_icon="🛡️", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0b141a; color: #e9edef; }
    h1 { color: #25d366; text-align: center; font-family: 'Arial Black', sans-serif; }
    
    /* LIVE BADGE */
    .live-badge {
        background-color: #ff4b4b; color: white; padding: 5px 10px; 
        border-radius: 5px; font-weight: bold; font-size: 0.8em;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* SCORE CARDS */
    .score-box {
        background-color: #202c33; padding: 10px; border-radius: 8px;
        text-align: center; font-size: 1.5em; font-weight: bold; color: #fff;
    }
    .stNumberInput input { background-color: #2a3942; color: white; border: 1px solid #25d366; }
</style>
""", unsafe_allow_html=True)

# --- 💾 THE BRAIN (DATABASE) ---
DB_FILE = "tournament_db.json"

def load_data():
    """Loads data from the local file if it exists"""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            st.session_state.teams = data.get("teams", [])
            st.session_state.tournament_started = data.get("tournament_started", False)
            st.session_state.results = data.get("results", {})
            st.session_state.fixtures = [tuple(f) for f in data.get("fixtures", [])]
    else:
        init_defaults()

def init_defaults():
    if 'teams' not in st.session_state: st.session_state.teams = []
    if 'fixtures' not in st.session_state: st.session_state.fixtures = []
    if 'results' not in st.session_state: st.session_state.results = {}
    if 'tournament_started' not in st.session_state: st.session_state.tournament_started = False

def save_data():
    """Saves current state to local file"""
    data = {
        "teams": st.session_state.teams,
        "fixtures": st.session_state.fixtures,
        "results": st.session_state.results,
        "tournament_started": st.session_state.tournament_started
    }
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# Initialize Session State
if 'data_loaded' not in st.session_state:
    load_data()
    st.session_state.data_loaded = True
if 'is_admin' not in st.session_state: st.session_state.is_admin = False

# --- 🔒 HOST CONTROL PANEL (SIDEBAR) ---
with st.sidebar:
    st.header("🔒 Host Login")
    pin = st.text_input("Host PIN", type="password")
    
    # YOUR SECRET PIN (Change this!)
    if pin == "1234": 
        st.session_state.is_admin = True
        st.success("✅ HOST UNLOCKED")
    else:
        st.session_state.is_admin = False
        st.info("👀 Viewer Mode")

    st.markdown("---")
    
    # --- ADMIN TOOLS ---
    if st.session_state.is_admin:
        st.subheader("🛠️ Setup Teams")
        new_team = st.text_input("Add Team Name")
        if st.button("Add Team"):
            if new_team and new_team not in st.session_state.teams:
                st.session_state.teams.append(new_team)
                save_data()
                st.success(f"Added {new_team}")
                time.sleep(0.5)
                st.rerun()
        
        st.markdown("---")
        
        # --- 💾 SAFEGUARD: BACKUP SYSTEM ---
        st.subheader("💾 Week-Long Safety")
        st.info("Download a backup every day to be safe!")
        
        # 1. DOWNLOAD BUTTON
        current_data = json.dumps({
            "teams": st.session_state.teams,
            "fixtures": st.session_state.fixtures,
            "results": st.session_state.results,
            "tournament_started": st.session_state.tournament_started
        })
        st.download_button(
            label="📥 Download Backup File",
            data=current_data,
            file_name="dls_backup.json",
            mime="application/json"
        )
        
        # 2. RESTORE BUTTON
        uploaded_backup = st.file_uploader("📤 Restore from Backup", type=['json'])
        if uploaded_backup is not None:
            if st.button("⚠️ RESTORE NOW"):
                data = json.load(uploaded_backup)
                st.session_state.teams = data["teams"]
                st.session_state.fixtures = [tuple(f) for f in data["fixtures"]]
                st.session_state.results = data["results"]
                st.session_state.tournament_started = data["tournament_started"]
                save_data() # Save the restored data to disk
                st.success("Tournament Restored!")
                time.sleep(1)
                st.rerun()

        st.markdown("---")
        if st.button("🧨 RESET EVERYTHING", type="primary"):
            st.session_state.clear()
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            st.rerun()

# --- MAIN PAGE ---
st.title("🛡️ DLS Tournament Live")

if st.session_state.tournament_started:
    st.markdown('<span class="live-badge">● LIVE WEEK</span>', unsafe_allow_html=True)
else:
    st.markdown("Waiting for Host to start...")

# 1. SETUP PHASE (Host Only)
if not st.session_state.tournament_started:
    if st.session_state.is_admin:
        st.info(f"Teams Ready: {len(st.session_state.teams)}")
        if st.button("🚀 LAUNCH TOURNAMENT"):
            if len(st.session_state.teams) < 2:
                st.error("Need more teams!")
            else:
                matches = list(itertools.combinations(st.session_state.teams, 2))
                random.shuffle(matches)
                st.session_state.fixtures = matches 
                st.session_state.tournament_started = True
                save_data()
                st.rerun()
    else:
        st.write("### Registered Teams:")
        for t in st.session_state.teams:
            st.caption(f"⚽ {t}")

# 2. LIVE TOURNAMENT
else:
    tab_standings, tab_matches = st.tabs(["🏆 Live Table", "⚽ Matches"])
    
    with tab_standings:
        # Calculate Table Live
        data = {t: {'P':0, 'W':0, 'D':0, 'L':0, 'GF':0, 'GA':0, 'GD':0, 'Pts':0} for t in st.session_state.teams}
        
        for i, (h, a) in enumerate(st.session_state.fixtures):
            mid = f"m_{i}"
            if mid in st.session_state.results:
                s_h, s_a = st.session_state.results[mid]
                data[h]['P']+=1; data[a]['P']+=1
                data[h]['GF']+=s_h; data[h]['GA']+=s_a; data[h]['GD']+=(s_h-s_a)
                data[a]['GF']+=s_a; data[a]['GA']+=s_h; data[a]['GD']+=(s_a-s_h)
                
                if s_h > s_a:
                    data[h]['W']+=1; data[h]['Pts']+=3; data[a]['L']+=1
                elif s_a > s_h:
                    data[a]['W']+=1; data[a]['Pts']+=3; data[h]['L']+=1
                else:
                    data[h]['D']+=1; data[h]['Pts']+=1; data[a]['D']+=1; data[a]['Pts']+=1

        df = pd.DataFrame.from_dict(data, orient='index')
        df = df.sort_values(by=['Pts', 'GD', 'GF'], ascending=False)
        st.dataframe(df, use_container_width=True)

    with tab_matches:
        filter_team = st.selectbox("Search Team", ["All"] + st.session_state.teams)
        
        count = 0
        for i, (home, away) in enumerate(st.session_state.fixtures):
            if filter_team == "All" or filter_team == home or filter_team == away:
                count += 1
                if count > 50: break
                
                mid = f"m_{i}"
                res = st.session_state.results.get(mid, [0, 0])
                
                with st.container():
                    c1, c2, c3, c4, c5 = st.columns([3, 1, 0.5, 1, 3])
                    c1.markdown(f"<div style='text-align:right; font-weight:bold; margin-top:10px'>{home}</div>", unsafe_allow_html=True)
                    c3.markdown("<div style='text-align:center; margin-top:10px'>-</div>", unsafe_allow_html=True)
                    c5.markdown(f"<div style='text-align:left; font-weight:bold; margin-top:10px'>{away}</div>", unsafe_allow_html=True)
                    
                    if st.session_state.is_admin:
                        # HOST: Can Edit
                        s_h = c2.number_input("H", 0, 20, res[0], key=f"{mid}_h", label_visibility="collapsed")
                        s_a = c4.number_input("A", 0, 20, res[1], key=f"{mid}_a", label_visibility="collapsed")
                        
                        if s_h != res[0] or s_a != res[1]:
                            st.session_state.results[mid] = [s_h, s_a]
                            save_data()
                            st.toast(f"Updated: {home} vs {away}")
                    else:
                        # VIEWER: Read Only
                        c2.markdown(f"<div class='score-box'>{res[0]}</div>", unsafe_allow_html=True)
                        c4.markdown(f"<div class='score-box'>{res[1]}</div>", unsafe_allow_html=True)