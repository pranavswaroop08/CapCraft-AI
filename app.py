import streamlit as st
import pandas as pd
import plotly.express as px
from nba_api.stats.endpoints import leaguedashplayerstats

st.set_page_config(
    page_title="CapCraft AI | Front Office Optimizer",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)
SALARY_CAP_2026=140.5

@st.cache_data(ttl=3600)
def load_market_data():
    try:
        player_stats=leaguedashplayerstats.LeagueDashPlayerStats(
            season='2025-26',
            per_mode_detailed="PerGame",
            season_type_all_star='Regular Season')
        raw_df = player_stats.get_data_frames()[0]
        final_df=raw_df[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'MIN', 'PTS', 'REB', 'AST', 'USG_PCT']].copy()
        final_df.columns = ['Player', 'Team', 'MPG', 'PPG', 'RPG', 'APG', 'USG_Pct']
        final_df['USG_Pct'] = (final_df['USG_Pct'] * 100).round(1)
        salary_url = "https://raw.githubusercontent.com/erikgregorywebb/datasets/master/nba-salaries.csv"
        salary_df = pd.read_csv(salary_url)
        salary_df.columns = [col.strip() for col in salary_df.columns]
        salary_df = salary_df.rename(columns={'name': 'Player', 'salary': 'Salary'})
        if salary_df['Salary'].max() > 1000000:
            salary_df['Salary'] = (salary_df['Salary'] / 1_000_000).round(2)
        merged_df = pd.merge(final_df, salary_df[['Player', 'Salary']], on='Player', how='inner')
        merged_df['$/Pos'] = (merged_df['Salary'] / merged_df['USG_Pct']).round(2)
        merged_df['BPM'] = ((merged_df['PPG'] * 0.4) + (merged_df['RPG'] * 0.2) + (merged_df['APG'] * 0.3) - 3.5).round(1)
        merged_df['Value_Index'] = (merged_df['BPM'] / merged_df['Salary']).round(3)        
        def assign_role(row):
            if row['Salary'] > 30.0 and row['USG_Pct'] > 25.0: return "Superstar"
            elif row['PPG'] > 12.0 and row['USG_Pct'] > 20.0: return "Scoring Option"
            elif row['Salary'] < 8.0 and row['BPM'] > 1.0: return "Rookie / Value Contract"
            else: return "Rotation Asset"
        merged_df['Role'] = merged_df.apply(assign_role, axis=1)
        return merged_df.drop_duplicates(subset=['Player']).sort_values(by="Value_Index", ascending=False)
    except Exception as e:
        st.sidebar.warning(f"Using baseline data profile matrix. Error context: {e}")
        fallback = pd.DataFrame([
            {"Player": "Nikola Jokic", "Team": "DEN", "Role": "Superstar", "MPG": 34.0, "PPG": 26.4, "RPG": 12.4, "APG": 9.0, "USG_Pct": 29.5, "Salary": 51.4, "BPM": 8.5, "Value_Index": 0.165},
            {"Player": "Shai Gilgeous-Alexander", "Team": "OKC", "Role": "Superstar", "MPG": 34.5, "PPG": 30.1, "RPG": 5.5, "APG": 6.2, "USG_Pct": 32.1, "Salary": 35.8, "BPM": 7.8, "Value_Index": 0.218},
            {"Player": "Alex Caruso", "Team": "OKC", "Role": "Rotation Asset", "MPG": 28.7, "PPG": 10.1, "RPG": 3.8, "APG": 3.5, "USG_Pct": 13.2, "Salary": 9.8, "BPM": 3.8, "Value_Index": 0.388}
        ])
        return fallback      