import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================================
# CAPCRAFT AI — NBA FRONT OFFICE DECISION INTELLIGENCE
# ==========================================================

st.set_page_config(
    page_title="CapCraft AI | NBA Roster Intelligence",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        padding: 0.5rem 0 0.25rem 0;
        border-bottom: 2px solid #E8461A;
        margin-bottom: 1.25rem;
    }
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: -0.03em;
        margin: 0;
        line-height: 1.1;
        color: #F0F2F6;
    }
    .title-accent {
        color: #E8461A;
    }
    .sub-title {
        font-size: 0.92rem;
        font-weight: 500;
        color: #8b949e;
        margin-top: 4px;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .rec-banner {
        background: linear-gradient(135deg, #1a1f2e 0%, #161b27 100%);
        border-left: 3px solid #E8461A;
        border-radius: 6px;
        padding: 14px 18px;
        margin: 12px 0 18px 0;
        font-size: 0.9rem;
        color: #c9d1d9;
        line-height: 1.6;
    }
    .rec-banner strong {
        color: #E8461A;
        font-weight: 700;
    }
    .section-label {
        font-size: 0.72rem;
        font-weight: 700;
        color: #E8461A;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 8px;
        margin-top: 4px;
    }
    .insight-card {
        background: #0d1117;
        padding: 18px;
        border-radius: 10px;
        border: 1px solid rgba(232,70,26,0.2);
        min-height: 175px;
        font-size: 0.88rem;
        line-height: 1.65;
        color: #c9d1d9;
    }
    .insight-card b {
        color: #f0f2f6;
    }
    .agent-name {
        font-size: 0.78rem;
        font-weight: 700;
        color: #E8461A;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .checklist-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 0;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        font-size: 0.87rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# CONSTANTS
# ----------------------------------------------------------
SALARY_CAP_DEFAULT = 140.5

FALLBACK_PLAYERS = [
    {"Player": "Nikola Jokic", "Team": "DEN", "Salary": 51.4},
    {"Player": "Shai Gilgeous-Alexander", "Team": "OKC", "Salary": 35.8},
    {"Player": "Luka Doncic", "Team": "DAL", "Salary": 43.0},
    {"Player": "Jayson Tatum", "Team": "BOS", "Salary": 34.9},
    {"Player": "Alex Caruso", "Team": "OKC", "Salary": 9.8},
    {"Player": "Derrick White", "Team": "BOS", "Salary": 19.5},
    {"Player": "Jalen Williams", "Team": "OKC", "Salary": 4.7},
    {"Player": "Sam Hauser", "Team": "BOS", "Salary": 2.1},
    {"Player": "Tyrese Haliburton", "Team": "IND", "Salary": 42.3},
    {"Player": "Bam Adebayo", "Team": "MIA", "Salary": 34.8},
    {"Player": "Mikal Bridges", "Team": "NYK", "Salary": 23.3},
    {"Player": "Austin Reaves", "Team": "LAL", "Salary": 12.0},
    {"Player": "Herb Jones", "Team": "NOP", "Salary": 13.0},
    {"Player": "Kevon Looney", "Team": "GSW", "Salary": 7.5},
    {"Player": "Draymond Green", "Team": "GSW", "Salary": 22.3},
    {"Player": "Stephen Curry", "Team": "GSW", "Salary": 51.9},
    {"Player": "Klay Thompson", "Team": "DAL", "Salary": 43.2},
    {"Player": "Andrew Wiggins", "Team": "GSW", "Salary": 24.3},
    {"Player": "LeBron James", "Team": "LAL", "Salary": 47.6},
    {"Player": "Anthony Davis", "Team": "LAL", "Salary": 43.2},
    {"Player": "D'Angelo Russell", "Team": "LAL", "Salary": 18.0},
    {"Player": "Rui Hachimura", "Team": "LAL", "Salary": 17.8},
    {"Player": "Jimmy Butler", "Team": "MIA", "Salary": 48.8},
    {"Player": "Tyler Herro", "Team": "MIA", "Salary": 32.6},
    {"Player": "Jrue Holiday", "Team": "BOS", "Salary": 30.0},
    {"Player": "Al Horford", "Team": "BOS", "Salary": 26.5},
    {"Player": "Kristaps Porzingis", "Team": "BOS", "Salary": 30.7},
    {"Player": "Giannis Antetokounmpo", "Team": "MIL", "Salary": 48.8},
    {"Player": "Damian Lillard", "Team": "MIL", "Salary": 45.6},
    {"Player": "Brook Lopez", "Team": "MIL", "Salary": 13.0},
    {"Player": "Bobby Portis", "Team": "MIL", "Salary": 14.0},
    {"Player": "Khris Middleton", "Team": "MIL", "Salary": 33.4},
    {"Player": "Joel Embiid", "Team": "PHI", "Salary": 51.4},
    {"Player": "Tyrese Maxey", "Team": "PHI", "Salary": 13.0},
    {"Player": "Paul George", "Team": "PHI", "Salary": 48.8},
    {"Player": "Tobias Harris", "Team": "PHI", "Salary": 39.2},
    {"Player": "Kelly Oubre Jr.", "Team": "PHI", "Salary": 13.0},
    {"Player": "Kawhi Leonard", "Team": "LAC", "Salary": 48.8},
    {"Player": "James Harden", "Team": "LAC", "Salary": 35.6},
    {"Player": "Russell Westbrook", "Team": "LAC", "Salary": 4.0},
    {"Player": "Ivica Zubac", "Team": "LAC", "Salary": 13.0},
    {"Player": "Devin Booker", "Team": "PHX", "Salary": 36.0},
    {"Player": "Kevin Durant", "Team": "PHX", "Salary": 51.2},
    {"Player": "Bradley Beal", "Team": "PHX", "Salary": 50.2},
    {"Player": "Julius Randle", "Team": "NYK", "Salary": 28.9},
    {"Player": "OG Anunoby", "Team": "NYK", "Salary": 37.0},
    {"Player": "Jalen Brunson", "Team": "NYK", "Salary": 26.0},
    {"Player": "Donte DiVincenzo", "Team": "NYK", "Salary": 9.3},
    {"Player": "Josh Hart", "Team": "NYK", "Salary": 12.9},
    {"Player": "Scottie Barnes", "Team": "TOR", "Salary": 7.0},
    {"Player": "Pascal Siakam", "Team": "IND", "Salary": 37.9},
    {"Player": "Myles Turner", "Team": "IND", "Salary": 19.9},
    {"Player": "Andrew Nembhard", "Team": "IND", "Salary": 4.5},
    {"Player": "Bennedict Mathurin", "Team": "IND", "Salary": 5.7},
    {"Player": "Victor Wembanyama", "Team": "SAS", "Salary": 12.1},
    {"Player": "Devin Vassell", "Team": "SAS", "Salary": 16.5},
    {"Player": "Keldon Johnson", "Team": "SAS", "Salary": 19.7},
    {"Player": "Chris Paul", "Team": "GSW", "Salary": 30.8},
    {"Player": "Alperen Sengun", "Team": "HOU", "Salary": 6.5},
    {"Player": "Jalen Green", "Team": "HOU", "Salary": 7.0},
    {"Player": "Fred VanVleet", "Team": "HOU", "Salary": 43.0},
    {"Player": "Chet Holmgren", "Team": "OKC", "Salary": 9.9},
    {"Player": "Josh Giddey", "Team": "OKC", "Salary": 6.6},
    {"Player": "Luguentz Dort", "Team": "OKC", "Salary": 16.0},
    {"Player": "Isaiah Hartenstein", "Team": "OKC", "Salary": 16.0},
    {"Player": "Trae Young", "Team": "ATL", "Salary": 40.1},
    {"Player": "Dejounte Murray", "Team": "ATL", "Salary": 28.0},
    {"Player": "Clint Capela", "Team": "ATL", "Salary": 22.3},
    {"Player": "De'Aaron Fox", "Team": "SAC", "Salary": 30.4},
    {"Player": "Domantas Sabonis", "Team": "SAC", "Salary": 37.9},
    {"Player": "Harrison Barnes", "Team": "SAC", "Salary": 18.0},
    {"Player": "LaMelo Ball", "Team": "CHA", "Salary": 32.6},
    {"Player": "Miles Bridges", "Team": "CHA", "Salary": 14.0},
    {"Player": "Donovan Mitchell", "Team": "CLE", "Salary": 35.6},
    {"Player": "Darius Garland", "Team": "CLE", "Salary": 33.0},
    {"Player": "Evan Mobley", "Team": "CLE", "Salary": 9.0},
    {"Player": "Jarrett Allen", "Team": "CLE", "Salary": 20.0},
    {"Player": "Anthony Edwards", "Team": "MIN", "Salary": 8.0},
    {"Player": "Karl-Anthony Towns", "Team": "NYK", "Salary": 36.0},
    {"Player": "Rudy Gobert", "Team": "MIN", "Salary": 41.0},
    {"Player": "Mike Conley", "Team": "MIN", "Salary": 22.0},
    {"Player": "Jaden McDaniels", "Team": "MIN", "Salary": 3.9},
    {"Player": "Kyrie Irving", "Team": "DAL", "Salary": 40.1},
    {"Player": "P.J. Washington", "Team": "DAL", "Salary": 16.0},
    {"Player": "Dereck Lively II", "Team": "DAL", "Salary": 4.8},
    {"Player": "Nikola Vucevic", "Team": "CHI", "Salary": 22.0},
    {"Player": "DeMar DeRozan", "Team": "SAC", "Salary": 28.0},
    {"Player": "Zach LaVine", "Team": "CHI", "Salary": 43.9},
    {"Player": "Jaren Jackson Jr.", "Team": "MEM", "Salary": 32.6},
    {"Player": "Ja Morant", "Team": "MEM", "Salary": 33.5},
    {"Player": "Desmond Bane", "Team": "MEM", "Salary": 22.3},
    {"Player": "Nikola Jovic", "Team": "MIA", "Salary": 4.0},
    {"Player": "Naz Reid", "Team": "MIN", "Salary": 14.0},
    {"Player": "Tre Jones", "Team": "SAS", "Salary": 7.0},
    {"Player": "Immanuel Quickley", "Team": "TOR", "Salary": 14.0},
    {"Player": "RJ Barrett", "Team": "TOR", "Salary": 23.7},
]

PLAYER_OVERRIDES = {
    "Nikola Jokic": (8.8, 29.5),
    "Luka Doncic": (8.2, 35.5),
    "Shai Gilgeous-Alexander": (7.9, 32.1),
    "Jayson Tatum": (6.0, 28.3),
    "Alex Caruso": (3.8, 13.2),
    "Derrick White": (4.2, 18.5),
    "Jalen Williams": (3.1, 23.0),
    "Sam Hauser": (1.1, 13.0),
    "Tyrese Haliburton": (5.4, 27.2),
    "Bam Adebayo": (3.9, 24.0),
    "Mikal Bridges": (2.2, 20.5),
    "Herb Jones": (3.0, 14.8),
    "Victor Wembanyama": (7.2, 24.0),
    "Anthony Edwards": (5.8, 31.0),
    "Giannis Antetokounmpo": (9.0, 33.0),
    "Joel Embiid": (7.5, 31.5),
    "Stephen Curry": (7.0, 29.0),
    "LeBron James": (5.2, 27.5),
    "Kevin Durant": (6.5, 30.0),
    "Donovan Mitchell": (4.5, 29.0),
    "Tyrese Maxey": (4.8, 26.5),
    "Jalen Brunson": (4.6, 27.0),
    "OG Anunoby": (3.5, 18.5),
    "Scottie Barnes": (2.8, 22.5),
    "Evan Mobley": (2.9, 17.0),
    "Chet Holmgren": (3.5, 20.0),
    "Josh Giddey": (1.8, 22.0),
    "Alperen Sengun": (2.6, 22.5),
    "Jalen Green": (1.8, 26.5),
    "LaMelo Ball": (3.2, 27.5),
    "De'Aaron Fox": (3.0, 27.0),
    "Trae Young": (2.5, 33.5),
    "Pascal Siakam": (3.6, 24.0),
    "Domantas Sabonis": (3.4, 23.5),
    "Jaren Jackson Jr.": (3.8, 20.0),
    "Ja Morant": (4.0, 28.5),
    "Darius Garland": (2.5, 26.0),
    "Karl-Anthony Towns": (2.0, 27.5),
    "Kyrie Irving": (4.2, 29.0),
    "Damian Lillard": (3.8, 31.0),
    "Bradley Beal": (0.5, 28.0),
    "Jimmy Butler": (4.0, 23.5),
    "Kawhi Leonard": (4.8, 24.5),
    "Rudy Gobert": (3.0, 13.0),
    "Draymond Green": (4.5, 13.5),
    "Naz Reid": (2.2, 17.0),
    "Jaden McDaniels": (2.5, 14.5),
    "Immanuel Quickley": (1.9, 22.0),
    "Josh Hart": (2.0, 16.5),
    "Donte DiVincenzo": (1.8, 16.0),
}


# ----------------------------------------------------------
# DATA PIPELINE
# ----------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def load_market_data():
    url = "https://raw.githubusercontent.com/erikgregorywebb/datasets/master/nba-salaries.csv"

    def stable_noise(name):
        seed = sum(ord(c) * (i + 1) for i, c in enumerate(str(name))) % 1000
        return (seed / 1000) - 0.5

    def build_analytics(df):
        df["Noise"] = df["Player"].apply(stable_noise)
        df["BPM"] = (
            0.10 * df["Salary"]
            + 1.8 * df["Noise"]
            + np.where(df["Salary"] < 5, 1.0, 0)
            - np.where(df["Salary"] > 38, 0.6, 0)
        ).clip(-2.5, 9.5).round(1)
        df["USG_Pct"] = (
            13.5 + 0.37 * df["Salary"] + 5.0 * df["Noise"]
        ).clip(10.0, 36.0).round(1)
        for player, (bpm, usg) in PLAYER_OVERRIDES.items():
            mask = df["Player"] == player
            if mask.any():
                df.loc[mask, "BPM"] = bpm
                df.loc[mask, "USG_Pct"] = usg
        df["Value_Index"] = (df["BPM"] / np.sqrt(df["Salary"].clip(lower=1.5))).round(3)

        def assign_role(row):
            if row["Salary"] >= 38:
                return "Franchise Star"
            if row["USG_Pct"] >= 26:
                return "Primary Creator"
            if row["BPM"] >= 2.5:
                return "Two-Way Connector"
            if row["Salary"] <= 8:
                return "Value Rotation"
            return "Rotation Asset"

        df["Role"] = df.apply(assign_role, axis=1)
        df = df.drop(columns=["Noise"])
        return df.sort_values("Value_Index", ascending=False).reset_index(drop=True)

    try:
        df = pd.read_csv(url)
        df.columns = [c.strip() for c in df.columns]
        rename_map = {"name": "Player", "player": "Player", "salary": "Salary", "team": "Team"}
        df = df.rename(columns=rename_map)
        if not {"Player", "Team", "Salary"}.issubset(df.columns):
            raise ValueError("Schema mismatch")
        df = df[["Player", "Team", "Salary"]].copy()
        df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")
        df = df.dropna(subset=["Player", "Team", "Salary"])

        # Normalize team names: full names, historical franchises, and relocations -> 3-letter codes.
        # Covers every value found in the public CSV, including defunct/relocated teams and junk entries.
        TEAM_NORM = {
            # Current franchises
            "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN",
            "Charlotte Hornets": "CHA", "Charlotte Bobcats": "CHA",
            "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
            "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
            "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
            "LA Clippers": "LAC", "Los Angeles Clippers": "LAC",
            "LA Lakers": "LAL", "Los Angeles Lakers": "LAL",
            "Memphis Grizzlies": "MEM", "Miami Heat": "MIA", "Milwaukee Bucks": "MIL",
            "Minnesota Timberwolves": "MIN", "New Orleans Pelicans": "NOP",
            "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC", "Orlando Magic": "ORL",
            "Philadelphia 76ers": "PHI", "Philadelphia Sixers": "PHI",
            "Phoenix Suns": "PHX", "Portland Trail Blazers": "POR",
            "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS",
            "Toronto Raptors": "TOR", "Utah Jazz": "UTA", "Washington Wizards": "WAS",
            # Historical / relocated franchises
            "New Jersey Nets": "BKN",
            "Seattle SuperSonics": "OKC",
            "Vancouver Grizzlies": "MEM",
            "New Orleans Hornets": "NOP",
            "NO/Oklahoma City Hornets": "NOP",
            "NO/Oklahoma City\r\n Hornets": "NOP",
            # Already-correct abbreviations (passthrough)
            "ATL": "ATL", "BOS": "BOS", "BKN": "BKN", "NJN": "BKN",
            "CHA": "CHA", "CHI": "CHI", "CLE": "CLE", "DAL": "DAL",
            "DEN": "DEN", "DET": "DET", "GSW": "GSW", "HOU": "HOU",
            "IND": "IND", "LAC": "LAC", "LAL": "LAL", "MEM": "MEM",
            "MIA": "MIA", "MIL": "MIL", "MIN": "MIN", "NOP": "NOP",
            "NOH": "NOP", "SEA": "OKC", "NYK": "NYK", "OKC": "OKC",
            "ORL": "ORL", "PHI": "PHI", "PHX": "PHX", "POR": "POR",
            "SAC": "SAC", "SAS": "SAS", "TOR": "TOR", "UTA": "UTA", "WAS": "WAS",
        }
        df["Team"] = df["Team"].str.strip().map(TEAM_NORM)
        # Drop rows whose team didn't match any known franchise (overseas clubs, nulls, junk)
        df = df.dropna(subset=["Team"])
        df = df.drop_duplicates(subset=["Player"], keep="first")
        if df["Salary"].max() > 1_000_000:
            df["Salary"] = df["Salary"] / 1_000_000
        df["Salary"] = df["Salary"].clip(lower=0.8).round(2)
        # Augment with fallback entries not in CSV
        fb_df = pd.DataFrame(FALLBACK_PLAYERS)
        existing = set(df["Player"].str.strip().tolist())
        new_entries = fb_df[~fb_df["Player"].isin(existing)]
        df = pd.concat([df, new_entries], ignore_index=True)
        df = df.drop_duplicates(subset=["Player"], keep="first")
        return build_analytics(df)
    except Exception:
        df = pd.DataFrame(FALLBACK_PLAYERS)
        return build_analytics(df)


df_market = load_market_data()


# ----------------------------------------------------------
# METRIC CALCULATIONS
# ----------------------------------------------------------
def compute_metrics(roster, cap_benchmark):
    if roster is None or roster.empty:
        return {}
    player_count = len(roster)
    total_salary = float(roster["Salary"].sum())
    avg_bpm = float(roster["BPM"].mean()) if player_count else 0.0
    total_bpm = float(roster["BPM"].sum())
    total_usg = float(roster["USG_Pct"].sum())
    cap_delta = cap_benchmark - total_salary
    high_usage = roster[roster["USG_Pct"] >= 28]
    creator_overlap = len(high_usage)
    lineup_value = total_bpm / np.sqrt(total_salary) if total_salary > 0 else 0.0
    cap_status = "UNDER CAP" if cap_delta >= 0 else "OVER CAP"
    cap_detail = (
        f"${cap_delta:.1f}M flexibility" if cap_delta >= 0
        else f"${abs(cap_delta):.1f}M over benchmark"
    )
    payroll_conc = (
        float(roster["Salary"].max()) / total_salary if total_salary > 0 else 0.0
    )
    # Risk score 0–100
    risk = 0
    if cap_delta < 0:
        risk += min(30, int(abs(cap_delta) / cap_benchmark * 100))
    if creator_overlap >= 3:
        risk += 20
    elif creator_overlap == 0:
        risk += 10
    if payroll_conc > 0.35:
        risk += 20
    if avg_bpm < 1.0:
        risk += 15
    low_value_count = len(roster[roster["Value_Index"] < 0.3])
    risk += min(15, low_value_count * 5)
    risk = min(100, max(0, risk))
    risk_label = "Low Risk" if risk <= 33 else "Moderate Risk" if risk <= 66 else "High Risk"
    # Composite strategy score
    comp = (
        2.5 * lineup_value
        + 0.8 * avg_bpm
        + (10 if cap_delta >= 0 else -5)
        + (5 if creator_overlap in [1, 2] else -5)
        - 0.25 * risk
    )
    return {
        "player_count": player_count,
        "total_salary": total_salary,
        "avg_bpm": avg_bpm,
        "total_bpm": total_bpm,
        "total_usg": total_usg,
        "cap_delta": cap_delta,
        "creator_overlap": creator_overlap,
        "lineup_value": lineup_value,
        "cap_status": cap_status,
        "cap_detail": cap_detail,
        "payroll_conc": payroll_conc,
        "risk": risk,
        "risk_label": risk_label,
        "comp_score": comp,
    }


# ----------------------------------------------------------
# LINEUP BUILDERS
# ----------------------------------------------------------
def build_star_heavy(team_pool, market_pool, cap_bench, min_bpm, max_sal, positive_only):
    pool = df_market.copy()
    if positive_only:
        pool = pool[pool["BPM"] > 0]
    pool = pool[pool["Salary"] <= max_sal]
    pool = pool[pool["BPM"] >= min_bpm]
    franchise = pool[pool["Team"] == team_pool].sort_values("BPM", ascending=False).head(2)
    others = pool[pool["Team"] != team_pool].sort_values("BPM", ascending=False)
    used = set(franchise["Player"].tolist())
    filler = others[~others["Player"].isin(used)].head(3)
    combined = pd.concat([franchise, filler]).drop_duplicates("Player").head(5)
    return combined.reset_index(drop=True)


def build_balanced(team_pool, market_pool, cap_bench, min_bpm, max_sal, positive_only):
    pool = df_market.copy()
    if positive_only:
        pool = pool[pool["BPM"] > 0]
    pool = pool[(pool["Salary"] <= max_sal) & (pool["BPM"] >= min_bpm)]
    candidates = pool[pool["USG_Pct"].between(14, 27)].sort_values(
        ["BPM", "Value_Index"], ascending=False
    )
    return candidates.head(5).reset_index(drop=True)


def build_moneyball(team_pool, market_pool, cap_bench, min_bpm, max_sal, positive_only):
    pool = df_market.copy()
    if positive_only:
        pool = pool[pool["BPM"] > 0]
    pool = pool[(pool["Salary"] <= min(22, max_sal)) & (pool["BPM"] >= max(1.0, min_bpm))]
    candidates = pool.sort_values("Value_Index", ascending=False)
    return candidates.head(5).reset_index(drop=True)


def build_roster_by_strategy(strategy, selected_team, cap_bench, min_bpm, max_sal, positive_only):
    team_pool = df_market[df_market["Team"] == selected_team].copy()
    market_pool = df_market[df_market["Team"] != selected_team].copy()
    if strategy == "Star-Heavy Build":
        return build_star_heavy(selected_team, market_pool, cap_bench, min_bpm, max_sal, positive_only)
    elif strategy == "Balanced Synergy Build":
        return build_balanced(selected_team, market_pool, cap_bench, min_bpm, max_sal, positive_only)
    elif strategy == "Moneyball Yield Build":
        return build_moneyball(selected_team, market_pool, cap_bench, min_bpm, max_sal, positive_only)
    return pd.DataFrame()


# ----------------------------------------------------------
# SESSION STATE INIT
# ----------------------------------------------------------
if "manual_players" not in st.session_state:
    st.session_state.manual_players = []
if "trade_applied" not in st.session_state:
    st.session_state.trade_applied = False
if "trade_roster" not in st.session_state:
    st.session_state.trade_roster = None
if "compare_players" not in st.session_state:
    st.session_state.compare_players = []

# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏀 CapCraft AI")
    st.markdown('<div class="section-label">Roster Engineering Console</div>', unsafe_allow_html=True)
    st.divider()

    unique_teams = sorted(df_market["Team"].dropna().unique().tolist())
    default_idx = unique_teams.index("BOS") if "BOS" in unique_teams else 0
    selected_team = st.selectbox("Target Franchise", options=unique_teams, index=default_idx)

    st.divider()
    st.markdown('<div class="section-label">Lineup Strategy</div>', unsafe_allow_html=True)

    strategy_option = st.radio(
        "Optimization Blueprint",
        options=["Star-Heavy Build", "Balanced Synergy Build", "Moneyball Yield Build", "Manual Override"]
    )

    st.divider()
    st.markdown('<div class="section-label">Scenario Controls</div>', unsafe_allow_html=True)

    cap_benchmark = st.slider(
        "Salary Cap Benchmark ($M)",
        min_value=100, max_value=220,
        value=int(SALARY_CAP_DEFAULT),
        step=1
    )
    min_bpm_filter = st.slider("Minimum BPM Threshold", min_value=-2.5, max_value=5.0, value=0.0, step=0.1)
    max_sal_filter = st.slider("Max Player Salary ($M)", min_value=5, max_value=60, value=55, step=1)
    max_creator_overlap = st.slider("Max Acceptable Creator Overlap", min_value=0, max_value=5, value=2, step=1)
    positive_bpm_only = st.toggle("Show only positive-BPM players", value=False)

    st.divider()
    compare_all = st.checkbox("Compare all strategies")

# ----------------------------------------------------------
# MANUAL OVERRIDE BUILDER
# ----------------------------------------------------------
if strategy_option == "Manual Override":
    team_pool_df = df_market[df_market["Team"] == selected_team]
    default_manual = team_pool_df.sort_values("BPM", ascending=False)["Player"].head(5).tolist()
    if not st.session_state.manual_players:
        st.session_state.manual_players = default_manual

    all_players_list = df_market["Player"].tolist()
    selected_manual = st.sidebar.multiselect(
        "Select exactly five players",
        options=all_players_list,
        default=st.session_state.manual_players,
        key="manual_select"
    )
    st.session_state.manual_players = selected_manual
    roster = df_market[df_market["Player"].isin(selected_manual)].drop_duplicates("Player").copy()
else:
    roster = build_roster_by_strategy(
        strategy_option, selected_team, cap_benchmark,
        min_bpm_filter, max_sal_filter, positive_bpm_only
    )

# Apply trade if active
if st.session_state.trade_applied and st.session_state.trade_roster is not None:
    roster = st.session_state.trade_roster.copy()

roster = roster.drop_duplicates("Player").reset_index(drop=True)
metrics = compute_metrics(roster, cap_benchmark)

# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------
st.markdown(
    '<div class="main-header">'
    '<div class="main-title">🏀 Cap<span class="title-accent">Craft</span> AI</div>'
    '<div class="sub-title">NBA Front Office Decision Intelligence · Payroll Architecture · Production-Per-Dollar Analysis</div>'
    '</div>',
    unsafe_allow_html=True
)

st.caption(
    "Interactive roster construction scenarios combining payroll discipline, production proxies, and role-balance analysis. "
    "BPM and Usage% are deterministic analytical proxies for hackathon demonstration only."
)


# ----------------------------------------------------------
# DYNAMIC RECOMMENDATION BANNER
# ----------------------------------------------------------
def generate_recommendation(metrics, strategy, roster):
    if not metrics or metrics.get("player_count", 0) != 5:
        return None
    s = metrics
    m = compute_metrics(build_roster_by_strategy("Moneyball Yield Build", selected_team, cap_benchmark, min_bpm_filter, max_sal_filter, positive_bpm_only), cap_benchmark)
    b = compute_metrics(build_roster_by_strategy("Balanced Synergy Build", selected_team, cap_benchmark, min_bpm_filter, max_sal_filter, positive_bpm_only), cap_benchmark)
    sh = compute_metrics(build_roster_by_strategy("Star-Heavy Build", selected_team, cap_benchmark, min_bpm_filter, max_sal_filter, positive_bpm_only), cap_benchmark)
    scores = {
        "Star-Heavy Build": sh.get("comp_score", 0) if sh else 0,
        "Balanced Synergy Build": b.get("comp_score", 0) if b else 0,
        "Moneyball Yield Build": m.get("comp_score", 0) if m else 0,
    }
    best = max(scores, key=scores.get)
    risk_label = s.get("risk_label", "")
    lv = s.get("lineup_value", 0)
    co = s.get("creator_overlap", 0)
    cap_d = s.get("cap_delta", 0)
    strength = (
        "strong payroll efficiency" if s.get("cap_delta", 0) >= 0 and lv > 1.5 else
        "high-ceiling star production" if s.get("avg_bpm", 0) > 4.5 else
        "balanced role distribution" if co == 2 else
        "cap-compliant construction"
    )
    tradeoff = (
        "elevated creator overlap risk" if co >= 3 else
        f"payroll overage of ${abs(cap_d):.1f}M" if cap_d < 0 else
        "limited franchise star upside" if s.get("avg_bpm", 0) < 3.0 else
        "compressed cap flexibility"
    )
    return f"<b>Recommendation:</b> The current <b>{strategy}</b> scenario demonstrates <b>{strength}</b>, though it carries <b>{tradeoff}</b>. Composite Score: <b>{s.get('comp_score', 0):.1f}</b> — Best overall strategy based on scenario filters: <b>{best}</b>."


rec_html = generate_recommendation(metrics, strategy_option, roster)
if rec_html:
    st.markdown(f'<div class="rec-banner">{rec_html}</div>', unsafe_allow_html=True)

# ----------------------------------------------------------
# TABS
# ----------------------------------------------------------
tab_exec, tab_analytics, tab_trade, tab_compare, tab_method = st.tabs([
    "Executive Summary", "Roster Analytics", "Trade Simulator", "Player Comparison", "Methodology"
])


# ============================================================
# TAB 1: EXECUTIVE SUMMARY
# ============================================================
with tab_exec:
    player_count = metrics.get("player_count", 0)
    total_salary = metrics.get("total_salary", 0)
    avg_bpm = metrics.get("avg_bpm", 0)
    cap_delta = metrics.get("cap_delta", 0)
    lineup_value = metrics.get("lineup_value", 0)
    creator_overlap = metrics.get("creator_overlap", 0)
    risk = metrics.get("risk", 0)
    risk_label = metrics.get("risk_label", "N/A")
    payroll_conc = metrics.get("payroll_conc", 0)

    # Metric cards
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    with m1:
        st.metric("Five-Man Payroll", f"${total_salary:.1f}M",
                  delta=metrics.get("cap_detail", ""),
                  delta_color="normal" if cap_delta >= 0 else "inverse")
    with m2:
        st.metric("Cap Flexibility", f"${cap_delta:+.1f}M",
                  delta="Under cap" if cap_delta >= 0 else "Over cap",
                  delta_color="normal" if cap_delta >= 0 else "inverse")
    with m3:
        st.metric("Avg Impact (BPM)", f"{avg_bpm:.2f}",
                  help="Deterministic analytical proxy for hackathon demonstration.")
    with m4:
        st.metric("Lineup Value Score", f"{lineup_value:.2f}",
                  help="Total BPM adjusted for payroll scale.")
    with m5:
        co_label = "Healthy" if creator_overlap in [1, 2] else ("Shortage" if creator_overlap == 0 else "Friction")
        st.metric("Creator Overlap", f"{creator_overlap}",
                  delta=co_label,
                  delta_color="normal" if creator_overlap in [1, 2] else "inverse")
    with m6:
        st.metric("Roster Risk Score", f"{risk}/100",
                  delta=risk_label,
                  delta_color="normal" if risk <= 33 else "off" if risk <= 66 else "inverse")

    # Status banner
    if player_count != 5:
        st.warning(f"Select exactly five players for a complete evaluation. Currently: {player_count} selected.")
    elif cap_delta < 0:
        st.error(f"Cap Alert: This lineup is ${abs(cap_delta):.1f}M above the illustrative ${cap_benchmark:.1f}M benchmark.")
    else:
        st.success(f"Roster clears the illustrative cap benchmark with ${cap_delta:.1f}M in remaining cap flexibility.")

    st.divider()

    # Gauge + Table
    col_left, col_right = st.columns([1, 1.7])

    with col_left:
        st.markdown('<div class="section-label">Cap Utilization</div>', unsafe_allow_html=True)
        gauge_max = max(cap_benchmark * 1.3, total_salary * 1.15)
        gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=total_salary,
            delta={"reference": cap_benchmark, "valueformat": ".1f", "suffix": "M"},
            number={"prefix": "$", "suffix": "M", "valueformat": ".1f"},
            title={"text": "Five-Man Payroll vs. Cap"},
            gauge={
                "axis": {"range": [0, gauge_max], "tickformat": "$,.0f"},
                "bar": {"color": "#E8461A" if cap_delta < 0 else "#4C78A8", "thickness": 0.3},
                "steps": [
                    {"range": [0, cap_benchmark * 0.85], "color": "#0d1117"},
                    {"range": [cap_benchmark * 0.85, cap_benchmark], "color": "#1a2a1a"},
                    {"range": [cap_benchmark, gauge_max], "color": "#2a1a1a"},
                ],
                "threshold": {
                    "line": {"color": "#E8461A", "width": 3},
                    "thickness": 0.75,
                    "value": cap_benchmark
                }
            }
        ))
        gauge.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=60, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c9d1d9")
        )
        st.plotly_chart(gauge, width="stretch")
        st.caption(f"Illustrative cap benchmark: ${cap_benchmark:.1f}M")

    with col_right:
        st.markdown('<div class="section-label">Roster Asset Ledger</div>', unsafe_allow_html=True)
        if not roster.empty:
            display_roster = roster[["Player", "Role", "Team", "Salary", "BPM", "USG_Pct", "Value_Index"]].sort_values("Value_Index", ascending=False)
            max_vi = max(1.0, float(display_roster["Value_Index"].max()))
            st.dataframe(
                display_roster,
                width="stretch",
                hide_index=True,
                column_config={
                    "Salary": st.column_config.NumberColumn("Salary ($M)", format="$%.1fM"),
                    "BPM": st.column_config.NumberColumn("Impact (BPM)", format="%.1f"),
                    "USG_Pct": st.column_config.NumberColumn("Usage %", format="%.1f%%"),
                    "Value_Index": st.column_config.ProgressColumn(
                        "Value Index", format="%.3f", min_value=0, max_value=max_vi
                    )
                }
            )
        else:
            st.info("No roster data to display.")

    st.divider()

    # Roster Health Checklist
    st.markdown('<div class="section-label">Roster Health Checklist</div>', unsafe_allow_html=True)
    hc1, hc2, hc3 = st.columns(3)

    with hc1:
        if cap_delta >= 0:
            st.success(f"✅ Cap Compliance — Under by ${cap_delta:.1f}M")
        else:
            st.error(f"❌ Cap Compliance — Over by ${abs(cap_delta):.1f}M")

        if creator_overlap in [1, 2]:
            st.success(f"✅ Creator Balance — {creator_overlap} primary creator(s)")
        elif creator_overlap == 0:
            st.warning(f"⚠️ Creator Balance — No high-usage initiator detected")
        else:
            st.error(f"❌ Creator Balance — {creator_overlap} creators causing role friction")

    with hc2:
        if avg_bpm >= 2.5:
            st.success(f"✅ Lineup Impact — Avg BPM {avg_bpm:.2f} (Above threshold)")
        elif avg_bpm >= 1.0:
            st.warning(f"⚠️ Lineup Impact — Avg BPM {avg_bpm:.2f} (Watch)")
        else:
            st.error(f"❌ Lineup Impact — Avg BPM {avg_bpm:.2f} (Below average)")

        if payroll_conc <= 0.35:
            st.success(f"✅ Payroll Distribution — Top contract at {payroll_conc:.0%}")
        else:
            st.warning(f"⚠️ Payroll Concentration — Top contract at {payroll_conc:.0%}")

    with hc3:
        avg_vi = float(roster["Value_Index"].mean()) if not roster.empty else 0
        if avg_vi >= 0.5:
            st.success(f"✅ Value Efficiency — Avg Value Index {avg_vi:.3f}")
        elif avg_vi >= 0.3:
            st.warning(f"⚠️ Value Efficiency — Avg Value Index {avg_vi:.3f}")
        else:
            st.error(f"❌ Value Efficiency — Avg Value Index {avg_vi:.3f}")

        if risk <= 33:
            st.success(f"✅ Risk Score — {risk}/100 ({risk_label})")
        elif risk <= 66:
            st.warning(f"⚠️ Risk Score — {risk}/100 ({risk_label})")
        else:
            st.error(f"❌ Risk Score — {risk}/100 ({risk_label})")

    st.markdown('<div class="section-label" style="margin-top:8px;">Overall Risk</div>', unsafe_allow_html=True)
    st.progress(risk / 100, text=f"{risk_label} — {risk}/100")

    # Strategy Comparison
    if compare_all:
        st.divider()
        with st.expander("Strategy Comparison Matrix", expanded=True):
            st.markdown('<div class="section-label">All-Strategy Decision Matrix</div>', unsafe_allow_html=True)
            strategies = ["Star-Heavy Build", "Balanced Synergy Build", "Moneyball Yield Build"]
            rows = []
            for s in strategies:
                r = build_roster_by_strategy(s, selected_team, cap_benchmark, min_bpm_filter, max_sal_filter, positive_bpm_only)
                m = compute_metrics(r, cap_benchmark)
                if m:
                    rows.append({
                        "Strategy": s,
                        "Payroll ($M)": f"${m['total_salary']:.1f}M",
                        "Cap Delta": f"${m['cap_delta']:+.1f}M",
                        "Avg BPM": round(m["avg_bpm"], 2),
                        "Lineup Value": round(m["lineup_value"], 2),
                        "Creator Overlap": m["creator_overlap"],
                        "Payroll Conc.": f"{m['payroll_conc']:.0%}",
                        "Risk Score": m["risk"],
                        "Composite Score": round(m["comp_score"], 1),
                    })
            if rows:
                comp_df = pd.DataFrame(rows)
                best_comp = comp_df.loc[comp_df["Composite Score"].idxmax(), "Strategy"]
                st.dataframe(comp_df, width="stretch", hide_index=True)
                st.success(f"Best composite strategy based on current filters: **{best_comp}**")

    # Front Office Committee
    st.divider()
    st.markdown('<div class="section-label">Virtual Front Office Committee</div>', unsafe_allow_html=True)

    if player_count == 5 and not roster.empty:
        top_value = roster.sort_values("Value_Index", ascending=False).iloc[0]
        highest_paid = roster.sort_values("Salary", ascending=False).iloc[0]
        lowest_impact = roster.sort_values("BPM").iloc[0]
        total_usg = metrics.get("total_usg", 0)

        if creator_overlap <= 1:
            arch_verdict = "Low creator density — the lineup may need an additional late-clock initiator or a secondary ball-handler capable of generating quality shots."
        elif creator_overlap == 2:
            arch_verdict = "Balanced creator architecture. Two primary engines can stagger possessions and run pick-and-roll actions without excessive role conflict."
        else:
            arch_verdict = "Creator friction detected. Multiple players commanding high possession share may produce offensive role redundancy and late-shot-clock inefficiency."

        scout_text = (
            f"Top production-per-dollar asset: <b>{top_value['Player']}</b> — "
            f"Value Index <b>{top_value['Value_Index']:.3f}</b>, "
            f"{top_value['BPM']:.1f} BPM proxy at ${top_value['Salary']:.1f}M. "
            f"Lowest-impact contract: <b>{lowest_impact['Player']}</b> at "
            f"{lowest_impact['BPM']:.1f} BPM — monitor for rotation optimization."
        )

        cap_text = (
            f"Scenario status: <b>{metrics.get('cap_status', '')}</b>. "
            f"Five-man spend: <b>${total_salary:.1f}M</b> vs. ${cap_benchmark:.1f}M benchmark. "
            f"Largest commitment: <b>{highest_paid['Player']}</b> at ${highest_paid['Salary']:.1f}M "
            f"({payroll_conc:.0%} of lineup payroll). "
            f"{'Structure preserves cap room for mid-level exceptions.' if cap_delta >= 0 else 'Salary shedding or exception-based roster moves required to achieve compliance.'}"
        )

        arch_text = (
            f"Combined usage proxy: <b>{total_usg:.1f}%</b> across five players. "
            f"High-usage creators (USG ≥ 28%): <b>{creator_overlap}</b>. "
            f"Payroll concentration index: <b>{payroll_conc:.0%}</b>. {arch_verdict}"
        )

        a1, a2, a3 = st.columns(3)
        with a1:
            st.markdown(f'<div class="insight-card"><div class="agent-name">🕵️ Pro Data Scout</div>{scout_text}</div>', unsafe_allow_html=True)
        with a2:
            st.markdown(f'<div class="insight-card"><div class="agent-name">💼 Cap Manager</div>{cap_text}</div>', unsafe_allow_html=True)
        with a3:
            st.markdown(f'<div class="insight-card"><div class="agent-name">📐 Roster Architect</div>{arch_text}</div>', unsafe_allow_html=True)
    else:
        st.info("Select exactly five players to activate the Front Office Committee evaluation.")


# ============================================================
# TAB 2: ROSTER ANALYTICS
# ============================================================
with tab_analytics:
    st.markdown('<div class="section-label">Analytical Filters</div>', unsafe_allow_html=True)

    fa1, fa2, fa3 = st.columns([1.2, 1.5, 1])
    with fa1:
        available_roles = ["All"] + sorted(df_market["Role"].unique().tolist())
        role_filter = st.selectbox("Role Filter", available_roles)
    with fa2:
        sal_range = st.slider("Salary Range ($M)", 0.0, 60.0, (0.0, 60.0), 0.5)
    with fa3:
        pos_bpm_tab = st.toggle("Positive BPM only", value=False, key="tab2_pos_bpm")

    view_df = df_market.copy()
    if role_filter != "All":
        view_df = view_df[view_df["Role"] == role_filter]
    view_df = view_df[view_df["Salary"].between(sal_range[0], sal_range[1])]
    if pos_bpm_tab:
        view_df = view_df[view_df["BPM"] > 0]

    st.divider()

    if roster.empty:
        st.info("No roster selected. Charts will display full market data.")
        chart_df = view_df.head(30)
    else:
        chart_df = roster.copy()

    # Scatter: Salary vs BPM
    st.markdown('<div class="section-label">Financial Commitment vs. On-Court Impact Proxy</div>', unsafe_allow_html=True)

    if not chart_df.empty:
        avg_sal_line = float(chart_df["Salary"].mean())
        fig_scatter = px.scatter(
            chart_df,
            x="Salary",
            y="BPM",
            size="USG_Pct",
            color="Role",
            text="Player",
            hover_data={
                "Team": True,
                "Salary": ":.1fM",
                "BPM": ":.1f",
                "USG_Pct": ":.1f%%",
                "Value_Index": ":.3f"
            },
            labels={
                "Salary": "Salary Commitment ($M)",
                "BPM": "On-Court Impact Proxy (BPM)",
                "USG_Pct": "Usage Rate (%)"
            },
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_scatter.add_vline(x=avg_sal_line, line_dash="dot", line_color="#8b949e",
                               annotation_text=f"Avg Salary ${avg_sal_line:.1f}M",
                               annotation_font_color="#8b949e")
        fig_scatter.add_hline(y=0, line_dash="dash", line_color="#555",
                               annotation_text="League-average impact baseline")
        fig_scatter.update_traces(textposition="top center",
                                   marker=dict(line=dict(width=1, color="white"), opacity=0.9))
        fig_scatter.update_layout(
            height=480,
            legend_title_text="Archetype",
            margin=dict(l=10, r=10, t=30, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,17,23,1)",
            font=dict(color="#c9d1d9"),
            xaxis=dict(gridcolor="#21262d"),
            yaxis=dict(gridcolor="#21262d"),
        )
        st.plotly_chart(fig_scatter, width="stretch")
        st.caption("BPM and Usage % are deterministic analytical proxies for hackathon demonstration.")

    st.divider()

    # Value Index Bar + Payroll Allocation side by side
    col_v1, col_v2 = st.columns(2)

    with col_v1:
        st.markdown('<div class="section-label">Value Index Ranking</div>', unsafe_allow_html=True)
        if not chart_df.empty:
            vi_df = chart_df.sort_values("Value_Index", ascending=True).tail(10)
            fig_vi = px.bar(
                vi_df,
                x="Value_Index",
                y="Player",
                orientation="h",
                color="Value_Index",
                color_continuous_scale=["#21262d", "#E8461A"],
                labels={"Value_Index": "Value Index", "Player": ""},
                text="Value_Index"
            )
            fig_vi.update_traces(texttemplate="%{text:.3f}", textposition="outside")
            fig_vi.update_layout(
                height=380,
                showlegend=False,
                coloraxis_showscale=False,
                margin=dict(l=10, r=50, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(13,17,23,1)",
                font=dict(color="#c9d1d9"),
                xaxis=dict(gridcolor="#21262d"),
                yaxis=dict(gridcolor="#21262d"),
            )
            st.plotly_chart(fig_vi, width="stretch")

    with col_v2:
        st.markdown('<div class="section-label">Payroll Allocation</div>', unsafe_allow_html=True)
        if not chart_df.empty:
            pay_df = chart_df.sort_values("Salary", ascending=True)
            fig_pay = px.bar(
                pay_df,
                x="Salary",
                y="Player",
                orientation="h",
                color="Role",
                labels={"Salary": "Salary ($M)", "Player": ""},
                text="Salary",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_pay.update_traces(texttemplate="$%{text:.1f}M", textposition="outside")
            fig_pay.update_layout(
                height=380,
                legend_title_text="Archetype",
                margin=dict(l=10, r=70, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(13,17,23,1)",
                font=dict(color="#c9d1d9"),
                xaxis=dict(gridcolor="#21262d"),
                yaxis=dict(gridcolor="#21262d"),
            )
            st.plotly_chart(fig_pay, width="stretch")

    st.divider()

    # Full market table
    st.markdown('<div class="section-label">Full Market Player Pool</div>', unsafe_allow_html=True)
    st.caption(f"Showing {len(view_df)} players matching current filters.")
    if not view_df.empty:
        disp_df = view_df[["Player", "Team", "Role", "Salary", "BPM", "USG_Pct", "Value_Index"]].copy()
        disp_max_vi = max(1.0, float(disp_df["Value_Index"].max()))
        st.dataframe(
            disp_df,
            width="stretch",
            hide_index=True,
            column_config={
                "Salary": st.column_config.NumberColumn("Salary ($M)", format="$%.1fM"),
                "BPM": st.column_config.NumberColumn("Impact (BPM)", format="%.1f"),
                "USG_Pct": st.column_config.NumberColumn("Usage %", format="%.1f%%"),
                "Value_Index": st.column_config.ProgressColumn(
                    "Value Index", format="%.3f", min_value=0, max_value=disp_max_vi
                )
            }
        )
    else:
        st.info("No players match the current filter combination.")


# ============================================================
# TAB 3: TRADE SIMULATOR
# ============================================================
with tab_trade:
    st.markdown('<div class="section-label">Trade Scenario Simulator</div>', unsafe_allow_html=True)
    st.caption("Evaluate the payroll and production impact of swapping a roster player for a market acquisition target.")

    if roster.empty or len(roster) < 1:
        st.info("Build a roster in the sidebar to enable Trade Simulator.")
    else:
        tc1, tc2 = st.columns(2)

        with tc1:
            st.markdown("**Remove from lineup:**")
            out_player = st.selectbox(
                "Select player to trade away",
                options=roster["Player"].tolist(),
                key="trade_out"
            )

        available_market = df_market[~df_market["Player"].isin(roster["Player"].tolist())].copy()

        with tc2:
            st.markdown("**Bring in from market:**")
            if available_market.empty:
                st.warning("No market players available.")
                in_player = None
            else:
                in_player = st.selectbox(
                    "Select acquisition target",
                    options=available_market.sort_values("Value_Index", ascending=False)["Player"].tolist(),
                    key="trade_in"
                )

        st.divider()

        if in_player and out_player:
            bt1, bt2, bt3 = st.columns([1, 1, 1])
            preview_clicked = bt1.button("Preview Trade Scenario", type="secondary")
            apply_clicked = bt2.button("Apply Trade to Scenario", type="primary")
            reset_clicked = bt3.button("Reset Applied Trade")

            if reset_clicked:
                st.session_state.trade_applied = False
                st.session_state.trade_roster = None
                st.rerun()

            if preview_clicked or apply_clicked:
                before_roster = roster.copy()
                after_roster = roster[roster["Player"] != out_player].copy()
                new_player_row = df_market[df_market["Player"] == in_player]
                after_roster = pd.concat([after_roster, new_player_row], ignore_index=True).drop_duplicates("Player")

                before_m = compute_metrics(before_roster, cap_benchmark)
                after_m = compute_metrics(after_roster, cap_benchmark)

                if before_m and after_m:
                    delta_bpm = after_m["avg_bpm"] - before_m["avg_bpm"]
                    delta_pay = after_m["total_salary"] - before_m["total_salary"]
                    delta_lv = after_m["lineup_value"] - before_m["lineup_value"]
                    delta_risk = after_m["risk"] - before_m["risk"]
                    delta_comp = after_m["comp_score"] - before_m["comp_score"]

                    st.markdown('<div class="section-label">Trade Impact Analysis</div>', unsafe_allow_html=True)
                    st.markdown(f"**{out_player}** → **{in_player}**")

                    cmp_cols = st.columns(5)
                    cmp_cols[0].metric("Payroll Δ", f"${delta_pay:+.1f}M",
                                       delta_color="inverse" if delta_pay > 0 else "normal")
                    cmp_cols[1].metric("Avg BPM Δ", f"{delta_bpm:+.2f}",
                                       delta_color="normal" if delta_bpm > 0 else "inverse")
                    cmp_cols[2].metric("Lineup Value Δ", f"{delta_lv:+.2f}",
                                       delta_color="normal" if delta_lv > 0 else "inverse")
                    cmp_cols[3].metric("Risk Δ", f"{delta_risk:+.0f}",
                                       delta_color="inverse" if delta_risk > 0 else "normal")
                    cmp_cols[4].metric("Composite Score Δ", f"{delta_comp:+.1f}",
                                       delta_color="normal" if delta_comp > 0 else "inverse")

                    # Before vs After table
                    compare_rows = []
                    for col, label in [
                        ("total_salary", "Total Payroll ($M)"),
                        ("cap_delta", "Cap Flexibility ($M)"),
                        ("avg_bpm", "Avg BPM"),
                        ("lineup_value", "Lineup Value Score"),
                        ("total_usg", "Total Usage Proxy"),
                        ("creator_overlap", "Creator Overlap"),
                        ("payroll_conc", "Payroll Concentration"),
                        ("risk", "Risk Score"),
                    ]:
                        bv = before_m.get(col, 0)
                        av = after_m.get(col, 0)
                        compare_rows.append({"Metric": label, "Before Trade": round(bv, 2), "After Trade": round(av, 2), "Δ": round(av - bv, 2)})
                    cmp_df = pd.DataFrame(compare_rows)
                    st.dataframe(cmp_df, width="stretch", hide_index=True)

                    if delta_comp > 0:
                        st.success(f"Trade Recommendation: **APPROVE** — Composite score improves by {delta_comp:+.1f} points. This acquisition strengthens the roster construction scenario.")
                    else:
                        st.error(f"Trade Recommendation: **REJECT** — Composite score decreases by {abs(delta_comp):.1f} points. This trade weakens the overall scenario.")

                    if apply_clicked:
                        st.session_state.trade_applied = True
                        st.session_state.trade_roster = after_roster.reset_index(drop=True)
                        st.success(f"Trade applied: {out_player} out, {in_player} in. Dashboard has been updated.")
                        st.rerun()

        if st.session_state.trade_applied:
            st.info("A trade has been applied to the current scenario. Click 'Reset Applied Trade' to revert.")


# ============================================================
# TAB 4: PLAYER COMPARISON
# ============================================================
with tab_compare:
    st.markdown('<div class="section-label">Player Comparison Tool</div>', unsafe_allow_html=True)
    st.caption("Select 2–5 players to compare across salary, production proxy, and value metrics.")

    all_players_sorted = df_market.sort_values("Value_Index", ascending=False)["Player"].tolist()

    default_compare = []
    if not roster.empty:
        default_compare = roster.sort_values("Value_Index", ascending=False)["Player"].head(3).tolist()
    if not st.session_state.compare_players:
        st.session_state.compare_players = default_compare

    selected_compare = st.multiselect(
        "Select players to compare (2–5)",
        options=all_players_sorted,
        default=st.session_state.compare_players,
        key="compare_select"
    )
    st.session_state.compare_players = selected_compare

    if len(selected_compare) < 2:
        st.warning("Select at least 2 players to enable comparison.")
    elif len(selected_compare) > 5:
        st.warning("Limit comparison to 5 players for clarity.")
    else:
        cmp_df = df_market[df_market["Player"].isin(selected_compare)].copy()
        cmp_display = cmp_df[["Player", "Team", "Role", "Salary", "BPM", "USG_Pct", "Value_Index"]].sort_values("Value_Index", ascending=False)

        st.divider()
        max_vi_cmp = max(1.0, float(cmp_display["Value_Index"].max()))
        st.dataframe(
            cmp_display,
            width="stretch",
            hide_index=True,
            column_config={
                "Salary": st.column_config.NumberColumn("Salary ($M)", format="$%.1fM"),
                "BPM": st.column_config.NumberColumn("Impact (BPM)", format="%.1f"),
                "USG_Pct": st.column_config.NumberColumn("Usage %", format="%.1f%%"),
                "Value_Index": st.column_config.ProgressColumn(
                    "Value Index", format="%.3f", min_value=0, max_value=max_vi_cmp
                )
            }
        )

        st.divider()
        st.markdown('<div class="section-label">Side-by-Side Metric Comparison</div>', unsafe_allow_html=True)

        melted = cmp_df.melt(
            id_vars=["Player"],
            value_vars=["Salary", "BPM", "Value_Index"],
            var_name="Metric",
            value_name="Value"
        )
        metric_labels = {"Salary": "Salary ($M)", "BPM": "BPM Proxy", "Value_Index": "Value Index"}
        melted["Metric"] = melted["Metric"].map(metric_labels)

        fig_cmp = px.bar(
            melted,
            x="Metric",
            y="Value",
            color="Player",
            barmode="group",
            labels={"Value": "Value", "Metric": ""},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_cmp.update_layout(
            height=420,
            legend_title_text="Player",
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(13,17,23,1)",
            font=dict(color="#c9d1d9"),
            xaxis=dict(gridcolor="#21262d"),
            yaxis=dict(gridcolor="#21262d"),
        )
        st.plotly_chart(fig_cmp, width="stretch")


# ============================================================
# TAB 5: METHODOLOGY
# ============================================================
with tab_method:
    st.markdown('<div class="section-label">Methodology & Caveats</div>', unsafe_allow_html=True)

    st.markdown("""
### Data Sources
**Salary data** is sourced from a public CSV file maintained on GitHub
([erikgregorywebb/datasets](https://github.com/erikgregorywebb/datasets)).
Salaries are expressed in millions of dollars. The dataset reflects a historical snapshot and is not a live NBA salary feed.
If the CSV is unavailable, the app automatically falls back to a curated set of ~90 representative players.

---

### Analytical Proxies

**BPM (Box Plus/Minus) Proxy**
BPM values in CapCraft AI are **deterministic analytical proxies** computed from salary tiers and
a stable player-name-derived noise function. They are **not** official NBA Box Plus/Minus statistics.

- Salary has a moderate positive correlation with production, but the proxy deliberately introduces
  underpriced and overpaid outliers to create realistic decision-support scenarios.
- Hand-tuned overrides are applied to 50+ recognizable players to improve demo realism.
- Range: approximately −2.5 to +9.5.

**Usage Rate (USG%) Proxy**
Usage% values are also deterministic proxies reflecting offensive possession share estimates,
derived from salary level and the same stable noise function.
They are **not** official NBA Synergy or play-by-play tracking statistics.

- Range: approximately 10% to 36%.

---

### Cap Benchmark

The salary-cap figure is an **illustrative benchmark** configurable between $100M and $220M.
It does **not** represent the official NBA salary cap, luxury tax line, first apron, or second apron.
CBA rules, team exceptions, player option structures, and contract incentives are not modeled.

---

### Derived Metrics

| Metric | Formula |
|---|---|
| Value Index | BPM / √(max(Salary, 1.5)) |
| Lineup Value Score | Total BPM / √(Total Salary) |
| Payroll Concentration | Highest Salary / Total Lineup Salary |
| Roster Risk Score | Composite of cap overage, creator overlap, payroll concentration, low BPM, low-value contracts (0–100) |
| Composite Strategy Score | Rewards lineup value, avg BPM, cap compliance, creator balance, low risk |

---

### Intended Use

CapCraft AI is a **hackathon decision-support prototype** designed for rapid roster scenario exploration.

It is **not**:
- Official NBA cap or contract advice
- A CBA-compliant roster construction tool
- A replacement for proprietary sports analytics platforms
- An official NBA projection or tracking system

All scenario outputs should be interpreted as illustrative decision-support tools, not actionable front-office guidance.
""")

# ----------------------------------------------------------
# FOOTER
# ----------------------------------------------------------
st.divider()
st.caption(
    "CapCraft AI · Hackathon Prototype · Public salary data from erikgregorywebb/datasets · "
    "BPM and Usage% are deterministic analytical proxies for demonstration only · "
    "Not official NBA cap, CBA, or contract advice."
)