import streamlit as st
import pandas as pd
from datetime import datetime
import math

# ============================================================================
# BACKWARD COMPATIBILITY HELPER FUNCTION
# ============================================================================

def safe_rerun():
    """
    Helper function to handle Streamlit rerun compatibility.
    Tries st.rerun() first (newer versions), falls back to st.experimental_rerun() (older versions).
    """
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()


# ============================================================================
# CUSTOM CSS STYLING - Deep Burgundy (#5B0E14) & Golden Sand (#F1E194)
# ============================================================================

def apply_custom_css():
    st.markdown("""
    <style>
    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #5B0E14 0%, #3a0909 100%);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #F1E194 !important;
        font-family: 'Arial Black', sans-serif;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #F1E194 0%, #d4c77a 100%);
        color: #5B0E14;
        font-weight: bold;
        border: 2px solid #5B0E14;
        border-radius: 8px;
        padding: 10px 24px;
        font-size: 16px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #d4c77a 0%, #F1E194 100%);
        box-shadow: 0 4px 8px rgba(241, 225, 148, 0.4);
        transform: translateY(-2px);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: rgba(241, 225, 148, 0.1);
        color: #F1E194;
        border: 2px solid #F1E194;
        border-radius: 6px;
    }
    
    /* Dataframes */
    .stDataFrame {
        background-color: rgba(241, 225, 148, 0.05);
        border: 2px solid #F1E194;
        border-radius: 8px;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: rgba(241, 225, 148, 0.15);
        color: #F1E194 !important;
        border: 1px solid #F1E194;
        border-radius: 6px;
        font-weight: bold;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #F1E194 !important;
        font-size: 28px !important;
        font-weight: bold !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #F1E194 !important;
        opacity: 0.8;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #5B0E14 0%, #2a0606 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: #F1E194 !important;
    }
    
    /* Success/Info/Warning boxes */
    .stSuccess, .stInfo, .stWarning {
        background-color: rgba(241, 225, 148, 0.1);
        border: 2px solid #F1E194;
        color: #F1E194;
    }
    
    /* Dividers */
    hr {
        border-color: #F1E194;
        opacity: 0.5;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    if 'tournament_started' not in st.session_state:
        st.session_state.tournament_started = False
    if 'players' not in st.session_state:
        st.session_state.players = []
    if 'tournament_type' not in st.session_state:
        st.session_state.tournament_type = None
    if 'current_round' not in st.session_state:
        st.session_state.current_round = 1
    if 'matches' not in st.session_state:
        st.session_state.matches = []
    if 'standings' not in st.session_state:
        st.session_state.standings = pd.DataFrame()
    if 'match_history' not in st.session_state:
        st.session_state.match_history = []
    if 'eliminated_players' not in st.session_state:
        st.session_state.eliminated_players = []
    if 'tournament_complete' not in st.session_state:
        st.session_state.tournament_complete = False


# ============================================================================
# PLAYER MANAGEMENT
# ============================================================================

def add_player(name, rating):
    """Add a new player to the tournament"""
    if name and name not in [p['name'] for p in st.session_state.players]:
        st.session_state.players.append({
            'name': name,
            'rating': rating,
            'wins': 0,
            'losses': 0,
            'points': 0,
            'buchholz': 0,
            'active': True
        })
        return True
    return False


def remove_player(name):
    """Remove a player from the tournament"""
    st.session_state.players = [p for p in st.session_state.players if p['name'] != name]


# ============================================================================
# TOURNAMENT LOGIC - SWISS SYSTEM
# ============================================================================

def generate_swiss_pairings():
    """Generate pairings for Swiss system tournament"""
    active_players = [p for p in st.session_state.players if p['active']]
    
    # Sort by points (descending), then by rating (descending)
    sorted_players = sorted(active_players, key=lambda x: (-x['points'], -x['rating']))
    
    matches = []
    paired = set()
    
    for i, player in enumerate(sorted_players):
        if player['name'] in paired:
            continue
            
        # Try to find an opponent with similar points
        for j in range(i + 1, len(sorted_players)):
            opponent = sorted_players[j]
            if opponent['name'] not in paired:
                matches.append({
                    'player1': player['name'],
                    'player2': opponent['name'],
                    'result': None,
                    'round': st.session_state.current_round
                })
                paired.add(player['name'])
                paired.add(opponent['name'])
                break
    
    # Handle bye if odd number of players
    if len(active_players) % 2 == 1:
        unpaired = [p for p in sorted_players if p['name'] not in paired][0]
        matches.append({
            'player1': unpaired['name'],
            'player2': 'BYE',
            'result': '1-0',
            'round': st.session_state.current_round
        })
    
    return matches


# ============================================================================
# TOURNAMENT LOGIC - SINGLE ELIMINATION
# ============================================================================

def generate_elimination_bracket():
    """Generate bracket for single elimination tournament"""
    active_players = [p for p in st.session_state.players if p['active']]
    
    # Sort by rating for seeding
    sorted_players = sorted(active_players, key=lambda x: -x['rating'])
    
    # Calculate number of rounds needed
    num_players = len(sorted_players)
    num_rounds = math.ceil(math.log2(num_players))
    bracket_size = 2 ** num_rounds
    
    # Add byes if needed
    num_byes = bracket_size - num_players
    
    matches = []
    
    # First round pairings (seeded)
    for i in range(bracket_size // 2):
        if i < num_byes:
            # Top seeds get byes
            matches.append({
                'player1': sorted_players[i]['name'],
                'player2': 'BYE',
                'result': '1-0',
                'round': 1
            })
        else:
            # Regular matches
            player1_idx = i
            player2_idx = num_players - 1 - (i - num_byes)
            matches.append({
                'player1': sorted_players[player1_idx]['name'],
                'player2': sorted_players[player2_idx]['name'],
                'result': None,
                'round': 1
            })
    
    return matches


def generate_next_elimination_round():
    """Generate next round of elimination bracket based on previous results"""
    # Get winners from current round
    current_round_matches = [m for m in st.session_state.match_history 
                            if m['round'] == st.session_state.current_round]
    
    winners = []
    for match in current_round_matches:
        if match['result'] == '1-0':
            winners.append(match['player1'])
        elif match['result'] == '0-1':
            winners.append(match['player2'])
    
    # If only one winner, tournament is complete
    if len(winners) <= 1:
        st.session_state.tournament_complete = True
        return []
    
    # Generate next round matches
    next_round_matches = []
    for i in range(0, len(winners), 2):
        if i + 1 < len(winners):
            next_round_matches.append({
                'player1': winners[i],
                'player2': winners[i + 1],
                'result': None,
                'round': st.session_state.current_round + 1
            })
        else:
            # Odd number of winners gets a bye
            next_round_matches.append({
                'player1': winners[i],
                'player2': 'BYE',
                'result': '1-0',
                'round': st.session_state.current_round + 1
            })
    
    return next_round_matches


# ============================================================================
# MATCH RESULTS PROCESSING
# ============================================================================

def update_match_result(match_idx, result):
    """Update the result of a match"""
    match = st.session_state.matches[match_idx]
    match['result'] = result
    
    # Update player statistics
    player1 = next((p for p in st.session_state.players if p['name'] == match['player1']), None)
    player2 = next((p for p in st.session_state.players if p['name'] == match['player2']), None)
    
    if result == '1-0':
        if player1:
            player1['wins'] += 1
            player1['points'] += 1
        if player2 and match['player2'] != 'BYE':
            player2['losses'] += 1
    elif result == '0-1':
        if player1:
            player1['losses'] += 1
        if player2:
            player2['wins'] += 1
            player2['points'] += 1
    elif result == '0.5-0.5':
        if player1:
            player1['points'] += 0.5
        if player2:
            player2['points'] += 0.5


def finalize_round():
    """Finalize current round and prepare for next round"""
    # Move matches to history
    st.session_state.match_history.extend(st.session_state.matches)
    
    if st.session_state.tournament_type == 'elimination':
        # Eliminate losers
        for match in st.session_state.matches:
            if match['result'] == '0-1' and match['player1'] != 'BYE':
                player = next((p for p in st.session_state.players if p['name'] == match['player1']), None)
                if player:
                    player['active'] = False
                    st.session_state.eliminated_players.append(match['player1'])
            elif match['result'] == '1-0' and match['player2'] != 'BYE':
                player = next((p for p in st.session_state.players if p['name'] == match['player2']), None)
                if player:
                    player['active'] = False
                    st.session_state.eliminated_players.append(match['player2'])
        
        # Generate next round
        next_matches = generate_next_elimination_round()
        st.session_state.matches = next_matches
        
        if not st.session_state.tournament_complete:
            st.session_state.current_round += 1
    else:
        # Swiss system - generate next round
        st.session_state.current_round += 1
        st.session_state.matches = generate_swiss_pairings()
    
    update_standings()


# ============================================================================
# STANDINGS CALCULATION
# ============================================================================

def update_standings():
    """Update tournament standings"""
    standings_data = []
    
    for player in st.session_state.players:
        standings_data.append({
            'Player': player['name'],
            'Rating': player['rating'],
            'Points': player['points'],
            'Wins': player['wins'],
            'Losses': player['losses'],
            'Status': 'Active' if player['active'] else 'Eliminated'
        })
    
    df = pd.DataFrame(standings_data)
    df = df.sort_values('Points', ascending=False).reset_index(drop=True)
    df.index += 1
    
    st.session_state.standings = df


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_tournament_setup():
    """Render tournament setup interface"""
    st.title("🏆 DLS Ultra Manager")
    st.subheader("Tournament Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        tournament_type = st.selectbox(
            "Tournament Type",
            ["Swiss System", "Single Elimination"]
        )
        st.session_state.tournament_type = tournament_type.lower().replace(" ", "_")
    
    with col2:
        st.metric("Registered Players", len(st.session_state.players))
    
    st.markdown("---")
    
    # Player registration
    st.subheader("Add Players")
    col1, col2, col3 = st.columns([3, 2, 1])
    
    with col1:
        player_name = st.text_input("Player Name", key="player_name_input")
    
    with col2:
        player_rating = st.number_input("Rating", min_value=0, max_value=3000, value=1500, key="player_rating_input")
    
    with col3:
        st.write("")
        st.write("")
        if st.button("➕ Add Player"):
            if add_player(player_name, player_rating):
                st.success(f"Added {player_name}")
                safe_rerun()
            else:
                st.error("Invalid or duplicate player name")
    
    # Display current players
    if st.session_state.players:
        st.subheader("Current Players")
        
        players_df = pd.DataFrame([
            {
                'Name': p['name'],
                'Rating': p['rating']
            } for p in st.session_state.players
        ])
        
        st.dataframe(players_df, use_container_width=True)
        
        # Remove player
        player_to_remove = st.selectbox(
            "Remove Player",
            [""] + [p['name'] for p in st.session_state.players]
        )
        
        if player_to_remove and st.button("🗑️ Remove Selected Player"):
            remove_player(player_to_remove)
            st.success(f"Removed {player_to_remove}")
            safe_rerun()
    
    st.markdown("---")
    
    # Start tournament
    if len(st.session_state.players) >= 2:
        if st.button("🎯 Start Tournament", type="primary"):
            if st.session_state.tournament_type == 'swiss_system':
                st.session_state.matches = generate_swiss_pairings()
            else:
                st.session_state.matches = generate_elimination_bracket()
            
            st.session_state.tournament_started = True
            update_standings()
            safe_rerun()
    else:
        st.info("Add at least 2 players to start the tournament")


def render_tournament_manager():
    """Render active tournament interface"""
    st.title("🏆 DLS Ultra Manager")
    
    # Tournament header
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tournament Type", 
                 "Swiss System" if st.session_state.tournament_type == 'swiss_system' else "Elimination")
    
    with col2:
        st.metric("Current Round", st.session_state.current_round)
    
    with col3:
        active_count = sum(1 for p in st.session_state.players if p['active'])
        st.metric("Active Players", active_count)
    
    st.markdown("---")
    
    # Check if tournament is complete
    if st.session_state.tournament_complete:
        st.success("🎊 Tournament Complete!")
        
        winner = [p for p in st.session_state.players if p['active']][0]
        st.balloons()
        
        st.markdown(f"### 👑 Champion: {winner['name']}")
        st.markdown(f"**Rating:** {winner['rating']}")
        
        st.markdown("---")
        
        if st.button("🔄 Reset Tournament"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            safe_rerun()
        
        return
    
    # Current round matches
    if st.session_state.matches:
        st.subheader(f"Round {st.session_state.current_round} Matches")
        
        all_matches_complete = all(m['result'] is not None for m in st.session_state.matches)
        
        for idx, match in enumerate(st.session_state.matches):
            # NOTE: Removed 'key' parameter for backward compatibility
            with st.expander(f"Match {idx + 1}: {match['player1']} vs {match['player2']}", 
                           expanded=(match['result'] is None)):
                
                if match['player2'] == 'BYE':
                    st.info(f"{match['player1']} receives a BYE (automatic win)")
                else:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**{match['player1']}**")
                        player1 = next(p for p in st.session_state.players if p['name'] == match['player1'])
                        st.write(f"Rating: {player1['rating']}")
                    
                    with col2:
                        if match['result'] is None:
                            result = st.selectbox(
                                "Result",
                                ["Not Played", "1-0", "0-1", "0.5-0.5"],
                                key=f"match_result_{idx}"
                            )
                            
                            if result != "Not Played":
                                if st.button("✅ Confirm Result", key=f"confirm_{idx}"):
                                    update_match_result(idx, result)
                                    safe_rerun()
                        else:
                            st.success(f"Result: {match['result']}")
                    
                    with col3:
                        st.write(f"**{match['player2']}**")
                        player2 = next(p for p in st.session_state.players if p['name'] == match['player2'])
                        st.write(f"Rating: {player2['rating']}")
        
        st.markdown("---")
        
        # Next round button
        if all_matches_complete:
            button_label = "Execute Elimination / Next Round" if st.session_state.tournament_type == 'elimination' else "⏭️ Next Round"
            
            if st.button(button_label, type="primary"):
                finalize_round()
                safe_rerun()
        else:
            st.info("Complete all matches to proceed to the next round")
    
    # Standings
    st.markdown("---")
    st.subheader("📊 Current Standings")
    
    if not st.session_state.standings.empty:
        st.dataframe(st.session_state.standings, use_container_width=True)
    
    # Match history
    if st.session_state.match_history:
        # NOTE: Removed 'key' parameter for backward compatibility
        with st.expander("📜 Match History"):
            for round_num in range(1, st.session_state.current_round):
                st.markdown(f"**Round {round_num}**")
                round_matches = [m for m in st.session_state.match_history if m['round'] == round_num]
                
                for match in round_matches:
                    st.write(f"{match['player1']} vs {match['player2']} → {match['result']}")
                
                st.markdown("---")
    
    # Eliminated players (for elimination tournaments)
    if st.session_state.tournament_type == 'elimination' and st.session_state.eliminated_players:
        # NOTE: Removed 'key' parameter for backward compatibility
        with st.expander("❌ Eliminated Players"):
            for player in st.session_state.eliminated_players:
                st.write(f"• {player}")
    
    # Reset button
    st.markdown("---")
    if st.button("🔄 Reset Tournament"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        safe_rerun()


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    st.set_page_config(
        page_title="DLS Ultra Manager",
        page_icon="🏆",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    apply_custom_css()
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/5B0E14/F1E194?text=DLS+Ultra", use_container_width=True)
        st.markdown("---")
        
        st.markdown("### ℹ️ About")
        st.markdown("""
        **DLS Ultra Manager** is a comprehensive tournament management system supporting:
        
        - 🇨🇭 Swiss System
        - 🏅 Single Elimination
        
        Track ratings, standings, and match history with ease!
        """)
        
        st.markdown("---")
        st.markdown("*Powered by Streamlit*")
        st.markdown(f"*{datetime.now().strftime('%Y-%m-%d')}*")
    
    # Main content
    if not st.session_state.tournament_started:
        render_tournament_setup()
    else:
        render_tournament_manager()


if __name__ == "__main__":
    main()
