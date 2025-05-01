
import streamlit as st

def calculate_handedness_counts(rhb, lhb, sh, pitcher_hand):
    if pitcher_hand == 'RHP':
        effective_rhb = rhb
        effective_lhb = lhb + sh
    else:
        effective_rhb = rhb + sh
        effective_lhb = lhb

    total = effective_rhb + effective_lhb
    percent_rhb = effective_rhb / total
    percent_lhb = effective_lhb / total

    return effective_rhb, effective_lhb, percent_rhb, percent_lhb

def evaluate_metric(value, thresholds):
    if value >= thresholds['over']:
        return "Over"
    elif thresholds['neutral_low'] <= value <= thresholds['neutral_high']:
        return "Neutral"
    else:
        return "Under"

st.title("Strikeout Prop Diagnostic (Full 13-Trifecta Analyzer)")

pitcher_hand = st.selectbox("Pitcher Throws", ["RHP", "LHP"])
rhb = st.number_input("Number of Right-handed Batters", min_value=0, max_value=9, value=5)
lhb = st.number_input("Number of Left-handed Batters", min_value=0, max_value=9, value=2)
sh = st.number_input("Number of Switch-hitters", min_value=0, max_value=9, value=2)

st.subheader("Pitcher vs RHB")
k_rhb = st.number_input("K% vs RHB (e.g. 0.30 = 30%)", min_value=0.0, max_value=1.0, value=0.30)
k9_rhb = st.number_input("K/9 vs RHB", min_value=0.0, max_value=20.0, value=9.5)
bb_rhb = st.number_input("BB% vs RHB", min_value=0.0, max_value=1.0, value=0.05)
tbf_rhb = st.number_input("TBF vs RHB", min_value=1.0, value=50.0)
ip_rhb = st.number_input("IP vs RHB", min_value=0.1, value=15.0)

st.subheader("Pitcher vs LHB")
k_lhb = st.number_input("K% vs LHB", min_value=0.0, max_value=1.0, value=0.20)
k9_lhb = st.number_input("K/9 vs LHB", min_value=0.0, max_value=20.0, value=7.2)
bb_lhb = st.number_input("BB% vs LHB", min_value=0.0, max_value=1.0, value=0.10)
tbf_lhb = st.number_input("TBF vs LHB", min_value=1.0, value=37.0)
ip_lhb = st.number_input("IP vs LHB", min_value=0.1, value=10.0)

st.subheader("Opponent K Profile")
k_rank = st.number_input("Team K Rank (1 = most strikeouts)", min_value=1, max_value=30, value=7)
k_avg_season = st.number_input("Season Avg Ks/Game", min_value=0.0, value=8.4)
k_avg_last3 = st.number_input("Last 3 Games Avg Ks", min_value=0.0, value=9.3)
k_last_game = st.number_input("Last Game Ks", min_value=0.0, value=11.0)
k_home_away = st.number_input("Home/Away Avg Ks/Game", min_value=0.0, value=8.7)

if st.button("Analyze"):
    eff_rhb, eff_lhb, percent_rhb, percent_lhb = calculate_handedness_counts(rhb, lhb, sh, pitcher_hand)

    bpi_rhb = tbf_rhb / ip_rhb
    bpi_lhb = tbf_lhb / ip_lhb
    kbb_rhb = k_rhb - bb_rhb
    kbb_lhb = k_lhb - bb_lhb

    results = {
        "K% vs RHB": evaluate_metric(k_rhb, {"over": 0.25, "neutral_low": 0.22, "neutral_high": 0.24}),
        "K% vs LHB": evaluate_metric(k_lhb, {"over": 0.25, "neutral_low": 0.22, "neutral_high": 0.24}),
        "K/9 vs RHB": evaluate_metric(k9_rhb, {"over": 9.5, "neutral_low": 7.5, "neutral_high": 9.4}),
        "K/9 vs LHB": evaluate_metric(k9_lhb, {"over": 9.5, "neutral_low": 7.5, "neutral_high": 9.4}),
        "K-BB% vs RHB": evaluate_metric(kbb_rhb, {"over": 0.15, "neutral_low": 0.10, "neutral_high": 0.14}),
        "K-BB% vs LHB": evaluate_metric(kbb_lhb, {"over": 0.15, "neutral_low": 0.10, "neutral_high": 0.14}),
        "Batters/Inning vs RHB": evaluate_metric(bpi_rhb, {"over": 0, "neutral_low": 3.9, "neutral_high": 4.2}) if bpi_rhb <= 3.8 else "Under",
        "Batters/Inning vs LHB": evaluate_metric(bpi_lhb, {"over": 0, "neutral_low": 3.9, "neutral_high": 4.2}) if bpi_lhb <= 3.8 else "Under",
        "Team K Rank": evaluate_metric(k_rank, {"over": 8, "neutral_low": 9, "neutral_high": 20}),
        "Season Avg Ks/Game": evaluate_metric(k_avg_season, {"over": 8.3, "neutral_low": 7.5, "neutral_high": 8.2}),
        "Last 3 Games Avg Ks": evaluate_metric(k_avg_last3, {"over": 9.0, "neutral_low": 7.0, "neutral_high": 8.9}),
        "Last Game Ks": evaluate_metric(k_last_game, {"over": 10, "neutral_low": 7, "neutral_high": 9}),
        "Home/Away Avg Ks/Game": evaluate_metric(k_home_away, {"over": 8.5, "neutral_low": 7.5, "neutral_high": 8.4})
    }

    st.subheader("Results (13-Trifecta)")
    for label, verdict in results.items():
        st.write(f"{label}: {verdict}")

    over = sum(1 for v in results.values() if v == "Over")
    neutral = sum(1 for v in results.values() if v == "Neutral")
    under = sum(1 for v in results.values() if v == "Under")

    if over >= 7:
        decision = "✅ Bet OVER K"
    elif under >= 7:
        decision = "⛔ Bet UNDER K"
    else:
        decision = "⚠️ No clear edge — Don't Touch"

    st.markdown("---")
    st.write(f"🧠 Pitcher Throws: {pitcher_hand}")
    st.write(f"📊 LHB: {eff_lhb}, RHB: {eff_rhb}")
    st.markdown("---")
    st.write(f"✅ Matches for OVER: {over}")
    st.write(f"➖ Matches for NEUTRAL: {neutral}")
    st.write(f"⛔ Matches for UNDER: {under}")
    st.markdown("---")
    st.subheader(f"Final Verdict: {decision}")
