import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================================
# CAPCRAFT AI — NBA FRONT OFFICE ROSTER OPTIMIZER
# ==========================================================

st.set_page_config(
    page_title="CapCraft AI | NBA Roster Optimizer",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------
SALARY_CAP_2026 = 140.5
APRONS_NOTE = "Illustrative cap model using a $140.5M salary-cap benchmark."

st.markdown("""
<style>
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    .sub-title {
        color: #8b949e;
        font-size: 1.05rem;
        margin-top: -8px;
        margin-bottom: 18px;
    }
    .section-label {
        font-size: 0.85rem;
        font-weight: 700;
        color: #8b949e;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .insight-card {
        padding: 16px;
        border-radius: 12px;
        border: 1px solid rgba(128,128,128,0.25);
        min-height: 165px;
    }
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------
# DATA PIPELINE
# ----------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def load_market_data():
    url = "https://raw.githubusercontent.com/erikgregorywebb/datasets/master/nba-salaries.csv"

    fallback_players = [
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
    ]

    try:
        df = pd.read_csv(url)
        df.columns = [column.strip() for column in df.columns]

        rename_map = {
            "name": "Player",
            "player": "Player",
            "salary": "Salary",
            "team": "Team"
        }
        df = df.rename(columns=rename_map)

        required_columns = {"Player", "Team", "Salary"}
        if not required_columns.issubset(df.columns):
            raise ValueError("CSV schema does not contain expected columns.")

        df = df[["Player", "Team", "Salary"]].copy()
        df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")
        df = df.dropna(subset=["Player", "Team", "Salary"])
        df = df.drop_duplicates(subset=["Player"], keep="first")

        if df["Salary"].max() > 1_000_000:
            df["Salary"] = df["Salary"] / 1_000_000

        df["Salary"] = df["Salary"].clip(lower=0.8).round(2)

    except Exception:
        df = pd.DataFrame(fallback_players)

    # Deterministic proxy engine:
    # Uses salary tiers + player-name stable seed to avoid a fake perfect salary/BPM relationship.
    def stable_noise(name):
        return ((sum(ord(char) for char in str(name)) % 100) / 100) - 0.5

    df["Noise"] = df["Player"].apply(stable_noise)

    # Production proxy: elite salaries trend upward, but variance creates underpriced/overpriced assets.
    df["BPM"] = (
        0.11 * df["Salary"]
        + 1.6 * df["Noise"]
        + np.where(df["Salary"] < 6, 1.2, 0)
        - np.where(df["Salary"] > 35, 0.8, 0)
    ).clip(-2.5, 9.5).round(1)

    # Usage proxy: reflects offensive role but deliberately does not equal salary.
    df["USG_Pct"] = (
        13
        + 0.38 * df["Salary"]
        + 5.5 * df["Noise"]
    ).clip(10.0, 36.0).round(1)

    # Hand-tuned showcase players for demo credibility.
    overrides = {
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
    }

    for player, values in overrides.items():
        if player in df["Player"].values:
            df.loc[df["Player"] == player, ["BPM", "USG_Pct"]] = values

    # Value Index avoids rewarding minimum-salary noise too aggressively.
    df["Value_Index"] = (
        df["BPM"] / np.sqrt(df["Salary"].clip(lower=1.5))
    ).round(3)

    def assign_role(row):
        if row["Salary"] >= 35:
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


df_market = load_market_data()

# ----------------------------------------------------------
# HEADER
# ----------------------------------------------------------
st.markdown('<div class="main-title">🏀 CapCraft AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Front Office Decision Intelligence · Salary Cap Discipline · On-Court Value Modeling</div>',
    unsafe_allow_html=True
)

st.caption(
    "Hackathon prototype using public salary data and deterministic BPM / Usage proxies. "
    "Designed for fast, reliable executive scenario analysis."
)

# ----------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------
with st.sidebar:
    st.header("Roster Engineering")

    unique_teams = sorted(df_market["Team"].dropna().unique().tolist())
    default_index = unique_teams.index("BOS") if "BOS" in unique_teams else 0

    selected_team = st.selectbox(
        "Target Franchise",
        options=unique_teams,
        index=default_index
    )

    st.divider()
    st.subheader("Lineup Strategy")

    strategy_option = st.radio(
        "Optimization Blueprint",
        options=[
            "Star-Heavy Build",
            "Balanced Synergy Build",
            "Moneyball Yield Build",
            "Manual Override"
        ]
    )

    st.caption("Each blueprint produces a five-player roster scenario.")

team_pool = df_market[df_market["Team"] == selected_team].copy()
market_pool = df_market[df_market["Team"] != selected_team].copy()

# ----------------------------------------------------------
# LINEUP ENGINE
# ----------------------------------------------------------
def build_star_heavy_lineup():
    franchise_stars = team_pool.sort_values("BPM", ascending=False).head(2)
    market_stars = market_pool.sort_values("BPM", ascending=False).head(3)
    return pd.concat([franchise_stars, market_stars]).drop_duplicates("Player").head(5)


def build_balanced_lineup():
    candidates = df_market[
        df_market["USG_Pct"].between(14, 27)
    ].sort_values(["BPM", "Value_Index"], ascending=False)

    return candidates.head(5)


def build_moneyball_lineup():
    candidates = df_market[
        (df_market["Salary"] <= 22) &
        (df_market["BPM"] >= 1.0)
    ].sort_values("Value_Index", ascending=False)

    return candidates.head(5)


if strategy_option == "Star-Heavy Build":
    roster = build_star_heavy_lineup()

elif strategy_option == "Balanced Synergy Build":
    roster = build_balanced_lineup()

elif strategy_option == "Moneyball Yield Build":
    roster = build_moneyball_lineup()

else:
    default_players = team_pool.sort_values("BPM", ascending=False)["Player"].head(5).tolist()
    selected_players = st.sidebar.multiselect(
        "Select exactly five players",
        options=df_market["Player"].tolist(),
        default=default_players
    )
    roster = df_market[df_market["Player"].isin(selected_players)].copy()

roster = roster.drop_duplicates("Player").copy()

# ----------------------------------------------------------
# METRICS ENGINE
# ----------------------------------------------------------
player_count = len(roster)
total_salary = roster["Salary"].sum()
avg_bpm = roster["BPM"].mean() if player_count else 0
total_usg = roster["USG_Pct"].sum()
cap_delta = SALARY_CAP_2026 - total_salary

high_usage_players = roster[roster["USG_Pct"] >= 28]
creator_overlap = len(high_usage_players)

lineup_value = (
    roster["BPM"].sum() / np.sqrt(total_salary)
    if total_salary > 0 else 0
)

cap_status = "UNDER CAP" if cap_delta >= 0 else "OVER CAP"
cap_status_detail = (
    f"${cap_delta:.1f}M flexibility"
    if cap_delta >= 0
    else f"${abs(cap_delta):.1f}M over benchmark"
)

# ----------------------------------------------------------
# EXECUTIVE SUMMARY
# ----------------------------------------------------------
st.divider()
st.markdown('<div class="section-label">Executive Decision Summary</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "Five-Man Payroll",
        f"${total_salary:.1f}M",
        delta=cap_status_detail,
        delta_color="normal" if cap_delta >= 0 else "inverse"
    )

with m2:
    st.metric(
        "Average Impact",
        f"{avg_bpm:.2f} BPM",
        help="BPM proxy estimates relative impact per 100 possessions."
    )

with m3:
    st.metric(
        "Lineup Value Score",
        f"{lineup_value:.2f}",
        help="Total production adjusted for payroll scale. Higher is better."
    )

with m4:
    st.metric(
        "Creator Overlap",
        f"{creator_overlap} high-usage players",
        delta="Healthy" if creator_overlap <= 2 else "Potential friction",
        delta_color="normal" if creator_overlap <= 2 else "inverse"
    )

if player_count != 5:
    st.warning(f"Current configuration has {player_count} players. Select exactly five for a complete front-office evaluation.")
elif cap_delta < 0:
    st.error(f"Cap alert: this lineup is {abs(cap_delta):.1f}M above the illustrative ${SALARY_CAP_2026:.1f}M benchmark.")
else:
    st.success(f"Roster clears the illustrative cap benchmark with ${cap_delta:.1f}M in remaining flexibility.")

# ----------------------------------------------------------
# CAP UTILIZATION + TABLE
# ----------------------------------------------------------
st.divider()
left, right = st.columns([1, 1.65])

with left:
    st.markdown('<div class="section-label">Cap Utilization</div>', unsafe_allow_html=True)

    gauge_max = max(SALARY_CAP_2026 * 1.25, total_salary * 1.1)

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=total_salary,
        number={"prefix": "$", "suffix": "M"},
        title={"text": "Five-Man Payroll"},
        gauge={
            "axis": {"range": [0, gauge_max]},
            "bar": {"color": "#4C78A8"},
            "steps": [
                {"range": [0, SALARY_CAP_2026], "color": "#E8F3EC"},
                {"range": [SALARY_CAP_2026, gauge_max], "color": "#FCE8E6"},
            ],
            "threshold": {
                "line": {"color": "#D62728", "width": 4},
                "thickness": 0.75,
                "value": SALARY_CAP_2026
            }
        }
    ))

    gauge.update_layout(
        height=310,
        margin=dict(l=20, r=20, t=55, b=10)
    )

    st.plotly_chart(gauge, width="stretch")
    st.caption(APRONS_NOTE)

with right:
    st.markdown('<div class="section-label">Roster Asset Ledger</div>', unsafe_allow_html=True)

    display_roster = roster[
        ["Player", "Role", "Team", "Salary", "BPM", "USG_Pct", "Value_Index"]
    ].sort_values("Value_Index", ascending=False)

    st.dataframe(
        display_roster,
        width="stretch",
        hide_index=True,
        column_config={
            "Salary": st.column_config.NumberColumn("Salary ($M)", format="$%.1fM"),
            "BPM": st.column_config.NumberColumn("Impact (BPM)", format="%.1f"),
            "USG_Pct": st.column_config.NumberColumn("Usage %", format="%.1f%%"),
            "Value_Index": st.column_config.ProgressColumn(
                "Value Index",
                format="%.3f",
                min_value=0,
                max_value=max(1.0, float(display_roster["Value_Index"].max()))
            )
        }
    )

# ----------------------------------------------------------
# VISUAL ANALYTICS
# ----------------------------------------------------------
st.divider()
st.markdown('<div class="section-label">Financial Cost vs. On-Court Impact</div>', unsafe_allow_html=True)

if not roster.empty:
    fig = px.scatter(
        roster,
        x="Salary",
        y="BPM",
        size="USG_Pct",
        color="Role",
        text="Player",
        hover_data={
            "Team": True,
            "Salary": ":.1f",
            "BPM": ":.1f",
            "USG_Pct": ":.1f",
            "Value_Index": ":.3f"
        },
        labels={
            "Salary": "Salary Commitment ($M)",
            "BPM": "On-Court Impact Proxy (BPM)",
            "USG_Pct": "Usage Rate (%)"
        }
    )

    fig.add_vline(
        x=total_salary / max(player_count, 1),
        line_dash="dot",
        annotation_text="Roster Avg Salary"
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray",
        annotation_text="League-average impact"
    )

    fig.update_traces(
        textposition="top center",
        marker=dict(line=dict(width=1, color="white"))
    )

    fig.update_layout(
        height=500,
        legend_title_text="Archetype",
        margin=dict(l=10, r=10, t=25, b=10)
    )

    st.plotly_chart(fig, width="stretch")

# ----------------------------------------------------------
# FRONT OFFICE COMMITTEE
# ----------------------------------------------------------
st.divider()
st.markdown('<div class="section-label">Virtual Front Office Committee</div>', unsafe_allow_html=True)

if player_count == 5:
    top_value = roster.sort_values("Value_Index", ascending=False).iloc[0]
    highest_paid = roster.sort_values("Salary", ascending=False).iloc[0]

    if creator_overlap <= 1:
        architect_verdict = "Low creator overlap. The group may need another reliable late-clock initiator."
    elif creator_overlap == 2:
        architect_verdict = "Healthy creator balance. Two primary engines can stagger possessions without excessive redundancy."
    else:
        architect_verdict = "High creator overlap. Multiple players require major possession share, creating possible offensive-role friction."

    scout_text = (
        f"**Best efficiency asset: {top_value['Player']}**  \n"
        f"Value Index: **{top_value['Value_Index']:.3f}**  \n\n"
        f"This player produces {top_value['BPM']:.1f} BPM proxy impact at "
        f"${top_value['Salary']:.1f}M, making them the strongest production-per-payroll asset in this scenario."
    )

    cap_text = (
        f"**Cap position: {cap_status}**  \n"
        f"Five-man spend: **${total_salary:.1f}M**  \n\n"
        f"The largest commitment is {highest_paid['Player']} at "
        f"${highest_paid['Salary']:.1f}M. "
        f"{'The structure preserves flexibility.' if cap_delta >= 0 else 'The structure requires salary shedding or exception-based roster planning.'}"
    )

    architect_text = (
        f"**Usage architecture: {total_usg:.1f}% combined proxy usage**  \n"
        f"High-usage creators: **{creator_overlap}**  \n\n"
        f"{architect_verdict}"
    )

    a1, a2, a3 = st.columns(3)

    with a1:
        st.markdown('<div class="insight-card">🕵️ <b>Pro Data Scout</b><br><br>' + scout_text + '</div>', unsafe_allow_html=True)

    with a2:
        st.markdown('<div class="insight-card">💼 <b>Cap Manager</b><br><br>' + cap_text + '</div>', unsafe_allow_html=True)

    with a3:
        st.markdown('<div class="insight-card">📐 <b>Roster Architect</b><br><br>' + architect_text + '</div>', unsafe_allow_html=True)

else:
    st.info("Select exactly five players to unlock the automated Scout, Cap Manager, and Roster Architect evaluations.")

# ----------------------------------------------------------
# FOOTER
# ----------------------------------------------------------
st.divider()
st.caption(
    "CapCraft AI is a hackathon decision-support prototype. Salary data is sourced from a public CSV; "
    "BPM and usage values are deterministic analytical proxies for demonstration purposes."
)