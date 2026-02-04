# ===============================
# DLS ULTRA MANAGER — FULL BUILD
# ===============================

import streamlit as st
import pandas as pd
import itertools
import random
import json
import os
import re

# -------------------------------
# CONFIG
# -------------------------------
st.set_page_config(
    page_title="DLS Ultra Manager",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DB_FILE = "dls_ultra_db.json"
BADGE_POOL = ["🦁","🦅","🐺","🐉","🦈","🐍","🐻","🐝","🦂","⚔️","🛡️","👑","⚡","🔥","💀","🤖","👽","🎯","💎"]

# -------------------------------
# STYLE
# -------------------------------
st.markdown("""
<style>
.stApp { background:#09090b; color:white; }
h1,h2,h3 { text-transform:uppercase; }
.glass { background:rgba(255,255,255,0.04); border:1px solid #1e293b; border-radius:12px; padding:15px; margin-bottom:12px;}
.drop { background:rgba(239,68,68,0.15); }
.bye { background:rgba(250,204,21,0.15); }
.sudden { border:2px solid #dc2626; }
</style>
""", unsafe_allow_html=True)

# -------------------------------
# STATE INIT
# -------------------------------
def defaults():
    return dict(
        teams=[],
        active_teams=[],
        eliminated=[],
        badges={},
        fixtures=[],
        results={},
        match_meta={},
        cumulative={},
        players={},
        format=None,
        started=False,
        round=1,
        phase="Phase 1: The Purge",
        sudden_leg=0,
        champion=None,
        admin=False
    )

for k,v in defaults().items():
    if k not in st.session_state:
        st.session_state[k]=v

# -------------------------------
# PERSISTENCE
# -------------------------------
def save():
    with open(DB_FILE,"w") as f:
        json.dump(dict(st.session_state),f)

def load():
    if os.path.exists(DB_FILE):
        with open(DB_FILE) as f:
            data=json.load(f)
            for k,v in data.items():
                st.session_state[k]=v

if "loaded" not in st.session_state:
    load()
    st.session_state.loaded=True

# -------------------------------
# HELPERS
# -------------------------------
def parse_players(raw, team, key):
    if not raw: return
    for part in raw.split(","):
        part=part.strip()
        if not part: continue
        n=1
        m=re.search(r"(.*?)(\((\d+)\)|x(\d+))$",part)
        name=part
        if m:
            name=m.group(1).strip()
            n=int(m.group(3) or m.group(4))
        pid=f"{name.title()}|{team}"
        st.session_state.players.setdefault(pid,{
            "Name":name.title(),"Team":team,"G":0,"A":0
        })
        st.session_state.players[pid][key]+=n

def standings():
    rows=[]
    for t in st.session_state.active_teams:
        s=st.session_state.cumulative.get(t,{
            "P":0,"W":0,"D":0,"L":0,"GF":0,"GA":0,"GD":0,"Pts":0
        })
        rows.append(dict(Team=t,**s))
    return sorted(rows,key=lambda x:(x["Pts"],x["GD"],x["GF"]),reverse=True)

def fixtures_for_phase():
    teams=st.session_state.active_teams[:]
    random.shuffle(teams)

    if len(teams)>=5:
        pairs=list(itertools.combinations(teams,2))
        random.shuffle(pairs)
        need=(len(teams)*2)//2
        return pairs[:need]

    if len(teams)==4:
        pairs=list(itertools.combinations(teams,2))
        random.shuffle(pairs)
        return pairs[:4]

    if len(teams)==3:
        return [(teams[1],teams[2]),(teams[2],teams[1])]

    if len(teams)==2:
        return [(teams[0],teams[1])]

    return []

# -------------------------------
# ELIMINATION
# -------------------------------
def eliminate():
    table=standings()
    n=len(table)

    if n<=1:
        st.session_state.champion=table[0]["Team"]
        save()
        st.experimental_rerun()

    if n>=5:
        losers=[table[-1]["Team"],table[-2]["Team"]]
    elif n==4:
        losers=[table[-1]["Team"]]
    elif n==3:
        if st.session_state.sudden_leg<2:
            st.session_state.sudden_leg+=1
            st.session_state.fixtures=fixtures_for_phase()
            save()
            st.experimental_rerun()
            return
        t2,t3=table[1]["Team"],table[2]["Team"]
        g2=sum(r[0] for k,r in st.session_state.results.items() if k.startswith(t2))
        g3=sum(r[0] for k,r in st.session_state.results.items() if k.startswith(t3))
        losers=[t3 if g2>g3 else t2]
        st.session_state.sudden_leg=0
    else:
        losers=[]

    for l in losers:
        st.session_state.active_teams.remove(l)
        st.session_state.eliminated.append(l)

    st.session_state.round+=1
    st.session_state.results={}
    st.session_state.match_meta={}
    st.session_state.fixtures=fixtures_for_phase()
    save()
    st.experimental_rerun()

# -------------------------------
# HEADER
# -------------------------------
st.markdown("<h1 style='text-align:center'>DLS ULTRA</h1>",unsafe_allow_html=True)

if st.session_state.champion:
    st.markdown(f"<h2 style='text-align:center;color:gold'>👑 {st.session_state.champion}</h2>",unsafe_allow_html=True)

# -------------------------------
# SIDEBAR
# -------------------------------
with st.sidebar:
    pin=st.text_input("ADMIN PIN",type="password")
    if pin=="0209":
        st.session_state.admin=True

    if st.session_state.admin:
        if st.button("NEXT ROUND"):
            eliminate()
        if st.button("RESET ALL"):
            st.session_state.clear()
            if os.path.exists(DB_FILE): os.remove(DB_FILE)
            st.experimental_rerun()

# -------------------------------
# SETUP
# -------------------------------
if not st.session_state.started:
    t=st.text_input("ADD TEAM")
    if st.button("ADD") and t:
        st.session_state.teams.append(t)
        st.session_state.badges[t]=random.choice(BADGE_POOL)

    if st.session_state.admin and st.button("START BATTLE ROYALE"):
        st.session_state.started=True
        st.session_state.active_teams=st.session_state.teams[:]
        for t in st.session_state.teams:
            st.session_state.cumulative[t]={"P":0,"W":0,"D":0,"L":0,"GF":0,"GA":0,"GD":0,"Pts":0}
        st.session_state.fixtures=fixtures_for_phase()
        save()
        st.experimental_rerun()

    st.stop()

# -------------------------------
# TABS
# -------------------------------
tab1,tab2,tab3=st.tabs(["TABLE","MATCHES","STATS"])

with tab1:
    df=pd.DataFrame(standings())
    st.dataframe(df,use_container_width=True)

with tab2:
    for i,(h,a) in enumerate(st.session_state.fixtures):
        mid=f"{h}v{a}_{i}"
        with st.expander(f"{h} vs {a}"):
            s1=st.number_input(h,0,20,key=f"s1{mid}")
            s2=st.number_input(a,0,20,key=f"s2{mid}")
            g1=st.text_input("Scorers H",key=f"g1{mid}")
            g2=st.text_input("Scorers A",key=f"g2{mid}")
            a1=st.text_input("Assists H",key=f"a1{mid}")
            a2=st.text_input("Assists A",key=f"a2{mid}")

            if st.button("SAVE",key=f"save{mid}"):
                st.session_state.results[mid]=[s1,s2]
                for t,gf,ga in [(h,s1,s2),(a,s2,s1)]:
                    c=st.session_state.cumulative[t]
                    c["P"]+=1; c["GF"]+=gf; c["GA"]+=ga; c["GD"]+=gf-ga
                if s1>s2:
                    st.session_state.cumulative[h]["W"]+=1; st.session_state.cumulative[h]["Pts"]+=3
                    st.session_state.cumulative[a]["L"]+=1
                elif s2>s1:
                    st.session_state.cumulative[a]["W"]+=1; st.session_state.cumulative[a]["Pts"]+=3
                    st.session_state.cumulative[h]["L"]+=1
                else:
                    for t in [h,a]:
                        st.session_state.cumulative[t]["D"]+=1
                        st.session_state.cumulative[t]["Pts"]+=1

                parse_players(g1,h,"G")
                parse_players(g2,a,"G")
                parse_players(a1,h,"A")
                parse_players(a2,a,"A")
                save()
                st.experimental_rerun()

with tab3:
    if st.session_state.players:
        st.dataframe(pd.DataFrame(st.session_state.players.values()),use_container_width=True)
