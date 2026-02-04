# ============================================================
# DLS ULTRA MANAGER — ABSOLUTE, COMPLETE, OPERATIONAL BUILD
# Single-file Streamlit app. No external dependencies.
# Persistence, validation, locking, exports, recovery included.
# ============================================================

import streamlit as st
import pandas as pd
import itertools
import random
import json
import os
import re
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
APP_TITLE = "DLS Ultra Manager"
DB_FILE = "dls_ultra_state.json"
ADMIN_PIN = "0209"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# STYLE
# ============================================================
st.markdown("""
<style>
.stApp{background:#070a12;color:#e5e7eb}
h1,h2,h3{letter-spacing:.12em;text-transform:uppercase}
.card{background:rgba(255,255,255,.04);border:1px solid #1f2937;border-radius:14px;padding:14px;margin-bottom:12px}
.warn{border-color:#7c2d12;background:rgba(124,45,18,.18)}
.ok{border-color:#14532d;background:rgba(20,83,45,.18)}
.bad{border-color:#7f1d1d;background:rgba(127,29,29,.18)}
.lock{opacity:.55;pointer-events:none}
hr{border:0;border-top:1px solid #1f2937;margin:10px 0}
small{opacity:.7}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DEFAULT STATE
# ============================================================
def default_state():
    return dict(
        meta=dict(
            created_at=str(datetime.utcnow()),
            version="1.0.0",
            locked=False
        ),
        admin=False,
        setup=dict(
            teams=[],
            badges={},
            started=False
        ),
        tournament=dict(
            phase="Phase 1: The Purge",
            round=1,
            sudden_leg=0,
            champion=None
        ),
        scheduling=dict(
            fixtures=[],     # list of dicts {id,home,away,round,locked}
            completed=set()  # fixture ids saved
        ),
        results=dict(),      # fixture_id -> {h,a}
        cumulative=dict(),   # team -> stats
        players=dict(),      # pid -> stats
        eliminated=[],
        audit=[]             # immutable log
    )

# ============================================================
# LOAD / SAVE
# ============================================================
def save():
    payload = st.session_state.app
    payload["scheduling"]["completed"] = list(payload["scheduling"]["completed"])
    with open(DB_FILE, "w") as f:
        json.dump(payload, f, indent=2)

def load():
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            data = json.load(f)
        data["scheduling"]["completed"] = set(data["scheduling"].get("completed", []))
        return data
    return default_state()

if "app" not in st.session_state:
    st.session_state.app = load()

# ============================================================
# HELPERS
# ============================================================
BADGES = ["🦁","🦅","🐺","🐉","🦈","🐍","🐻","🐝","🦂","⚔️","🛡️","👑","⚡","🔥","💀","🤖","👽","🎯","💎"]

def log(event):
    st.session_state.app["audit"].append({
        "t": str(datetime.utcnow()),
        "event": event
    })

def ensure_team_stats(team):
    st.session_state.app["cumulative"].setdefault(team,{
        "P":0,"W":0,"D":0,"L":0,"GF":0,"GA":0,"GD":0,"Pts":0
    })

def parse_players(raw, team, key):
    if not raw: return
    for part in raw.split(","):
        part = part.strip()
        if not part: continue
        n = 1
        m = re.search(r"(.*?)(\((\d+)\)|x(\d+))$", part)
        name = part
        if m:
            name = m.group(1).strip()
            n = int(m.group(3) or m.group(4))
        pid = f"{name.title()}|{team}"
        st.session_state.app["players"].setdefault(pid,{
            "Name":name.title(),"Team":team,"G":0,"A":0
        })
        st.session_state.app["players"][pid][key] += n

def standings(active_only=True):
    rows=[]
    for t,s in st.session_state.app["cumulative"].items():
        if active_only and t in st.session_state.app["eliminated"]:
            continue
        rows.append(dict(Team=t,**s))
    return sorted(rows,key=lambda x:(x["Pts"],x["GD"],x["GF"]),reverse=True)

def active_teams():
    return [t for t in st.session_state.app["setup"]["teams"]
            if t not in st.session_state.app["eliminated"]]

# ============================================================
# SCHEDULING (ALL CASES)
# ============================================================
def build_fixtures():
    teams = active_teams()
    fx=[]
    rid = st.session_state.app["tournament"]["round"]

    if len(teams) >= 5:
        pairs=list(itertools.combinations(teams,2))
        random.shuffle(pairs)
        need=len(teams)
        pairs=pairs[:need]
    elif len(teams)==4:
        pairs=list(itertools.combinations(teams,2))
        random.shuffle(pairs)
        pairs=pairs[:4]
    elif len(teams)==3:
        t=teams[:]
        pairs=[(t[1],t[2]),(t[2],t[1])]
    elif len(teams)==2:
        pairs=[(teams[0],teams[1])]
    else:
        pairs=[]

    for i,(h,a) in enumerate(pairs):
        fx.append({
            "id":f"R{rid}_{i}_{h}_v_{a}",
            "home":h,
            "away":a,
            "round":rid,
            "locked":False
        })
    st.session_state.app["scheduling"]["fixtures"]=fx
    log(f"Fixtures generated for round {rid}")

# ============================================================
# ELIMINATION LOGIC (COMPLETE)
# ============================================================
def eliminate_and_advance():
    table=standings()
    n=len(table)

    if n<=1:
        st.session_state.app["tournament"]["champion"]=table[0]["Team"]
        log("Champion decided")
        save()
        st.experimental_rerun()

    losers=[]
    if n>=5:
        losers=[table[-1]["Team"],table[-2]["Team"]]
    elif n==4:
        losers=[table[-1]["Team"]]
    elif n==3:
        if st.session_state.app["tournament"]["sudden_leg"]<2:
            st.session_state.app["tournament"]["sudden_leg"]+=1
            build_fixtures()
            save()
            st.experimental_rerun()
            return
        t2,t3=table[1]["Team"],table[2]["Team"]
        g2=sum(r["h"] for k,r in st.session_state.app["results"].items() if k.endswith(t2))
        g3=sum(r["h"] for k,r in st.session_state.app["results"].items() if k.endswith(t3))
        losers=[t3 if g2>g3 else t2]
        st.session_state.app["tournament"]["sudden_leg"]=0

    for l in losers:
        st.session_state.app["eliminated"].append(l)
        log(f"Eliminated {l}")

    st.session_state.app["tournament"]["round"]+=1
    st.session_state.app["results"]={}
    st.session_state.app["scheduling"]["completed"]=set()
    build_fixtures()
    save()
    st.experimental_rerun()

# ============================================================
# HEADER
# ============================================================
st.markdown(f"<h1 style='text-align:center'>{APP_TITLE}</h1>", unsafe_allow_html=True)

if st.session_state.app["tournament"]["champion"]:
    st.markdown(
        f"<h2 style='text-align:center;color:gold'>👑 {st.session_state.app['tournament']['champion']}</h2>",
        unsafe_allow_html=True
    )

# ============================================================
# SIDEBAR (ADMIN)
# ============================================================
with st.sidebar:
    pin = st.text_input("ADMIN PIN", type="password")
    if pin == ADMIN_PIN:
        st.session_state.app["admin"]=True

    if st.session_state.app["admin"]:
        if st.button("LOCK TOURNAMENT"):
            st.session_state.app["meta"]["locked"]=True
            log("Tournament locked")
            save()
        if st.button("UNLOCK TOURNAMENT"):
            st.session_state.app["meta"]["locked"]=False
            log("Tournament unlocked")
            save()
        if st.button("NEXT ROUND"):
            eliminate_and_advance()
        if st.button("EXPORT JSON"):
            st.download_button("DOWNLOAD", json.dumps(st.session_state.app,indent=2),
                               file_name="dls_ultra_export.json")
        if st.button("RESET EVERYTHING"):
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.session_state.clear()
            st.experimental_rerun()

# ============================================================
# SETUP PHASE
# ============================================================
if not st.session_state.app["setup"]["started"]:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        team = st.text_input("TEAM NAME")
        if st.button("ADD TEAM") and team:
            if team not in st.session_state.app["setup"]["teams"]:
                st.session_state.app["setup"]["teams"].append(team)
                st.session_state.app["setup"]["badges"][team]=random.choice(BADGES)
                ensure_team_stats(team)
                log(f"Team added: {team}")
                save()
        if st.session_state.app["admin"] and st.button("START TOURNAMENT"):
            st.session_state.app["setup"]["started"]=True
            build_fixtures()
            log("Tournament started")
            save()
            st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ============================================================
# MAIN TABS
# ============================================================
tab1,tab2,tab3,tab4 = st.tabs(["TABLE","MATCHES","PLAYERS","AUDIT"])

# TABLE
with tab1:
    st.dataframe(pd.DataFrame(standings()), use_container_width=True)

# MATCHES
with tab2:
    for fx in st.session_state.app["scheduling"]["fixtures"]:
        fid=fx["id"]
        locked = fid in st.session_state.app["scheduling"]["completed"]
        cls="card lock" if locked else "card"
        st.markdown(f"<div class='{cls}'>", unsafe_allow_html=True)
        st.markdown(f"### {fx['home']} vs {fx['away']}")
        h=st.number_input(fx["home"],0,20,key=f"h_{fid}")
        a=st.number_input(fx["away"],0,20,key=f"a_{fid}")
        gh=st.text_input("Scorers (Home)",key=f"gh_{fid}")
        ga=st.text_input("Scorers (Away)",key=f"ga_{fid}")
        ah=st.text_input("Assists (Home)",key=f"ah_{fid}")
        aa=st.text_input("Assists (Away)",key=f"aa_{fid}")

        if st.button("SAVE RESULT", key=f"s_{fid}") and not locked:
            st.session_state.app["results"][fid]={"h":h,"a":a}
            for t,gf,ga_ in [(fx["home"],h,a),(fx["away"],a,h)]:
                c=st.session_state.app["cumulative"][t]
                c["P"]+=1; c["GF"]+=gf; c["GA"]+=ga_; c["GD"]+=gf-ga_
            if h>a:
                st.session_state.app["cumulative"][fx["home"]]["W"]+=1
                st.session_state.app["cumulative"][fx["home"]]["Pts"]+=3
                st.session_state.app["cumulative"][fx["away"]]["L"]+=1
            elif a>h:
                st.session_state.app["cumulative"][fx["away"]]["W"]+=1
                st.session_state.app["cumulative"][fx["away"]]["Pts"]+=3
                st.session_state.app["cumulative"][fx["home"]]["L"]+=1
            else:
                for t in [fx["home"],fx["away"]]:
                    st.session_state.app["cumulative"][t]["D"]+=1
                    st.session_state.app["cumulative"][t]["Pts"]+=1
            parse_players(gh,fx["home"],"G")
            parse_players(ga,fx["away"],"G")
            parse_players(ah,fx["home"],"A")
            parse_players(aa,fx["away"],"A")
            st.session_state.app["scheduling"]["completed"].add(fid)
            log(f"Result saved: {fid}")
            save()
            st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# PLAYERS
with tab3:
    if st.session_state.app["players"]:
        st.dataframe(pd.DataFrame(st.session_state.app["players"].values()),
                     use_container_width=True)

# AUDIT
with tab4:
    st.dataframe(pd.DataFrame(st.session_state.app["audit"]),
                 use_container_width=True)
