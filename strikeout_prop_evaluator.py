
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

    return percent_rhb, percent_lhb

def calculate_weighted_stats(k_rhb, k_lhb, bb_rhb, bb_lhb, percent_rhb, percent_lhb):
    weighted_k = (k_rhb * percent_rhb) + (k_lhb * percent_lhb)
    weighted_bb = (bb_rhb * percent_rhb) + (bb_lhb * percent_lhb)
    k_bb = weighted_k - weighted_bb
    return round(weighted_k, 4), round(weighted_bb, 4), round(k_bb, 4)

def evaluate_metric(value, thresholds):
    if value >= thresholds['over']:
        return "Over"
    elif thresholds['neutral_low'] <= value <= thresholds['neutral_high']:
        return "Neutral"
    else:
        return "Under"

st.title("Strikeout Prop Evaluator (Full Trifecta)")

st.markdown("""
Enter pitcher data and matchup to calculate strikeout prop lean:
""")

pitcher_hand = st.selectbox("Pitcher Throws", ["RHP", "LHP"])
rhb = st.number_input("Number of Right-handed Batters", min_value=0, max_value=9, value=5)
lhb = st.number_input("Number of Left-handed Batters", min_value=0, max_value=9, value=2)
sh = st.number_input("Number of Switch-hitters", min_value=0, max_value=9, value=2)

k_rhb = st.number_input("K% vs RHB (e.g. 0.30 for 30%)", min_value=0.0, max_value=1.0, value=0.30)
k_lhb = st.number_input("K% vs LHB", min_value=0.0, max_value=1.0, value=0.20)
bb_rhb = st.number_input("BB% vs RHB", min_value=0.0, max_value=1.0, value=0.05)
bb_lhb = st.number_input("BB% vs LHB", min_value=0.0, max_value=1.0, value=0.10)

strikeouts = st.number_input("Total Strikeouts", min_value=0.0, max_value=100.0, value=18.0)
ip = st.number_input("Innings Pitched", min_value=0.1, max_value=100.0, value=22.2)
tbf = st.number_input("Total Batters Faced", min_value=1.0, max_value=500.0, value=87.0)

if st.button("Evaluate"):
    percent_rhb, percent_lhb = calculate_handedness_counts(rhb, lhb, sh, pitcher_hand)
    weighted_k, weighted_bb, k_bb = calculate_weighted_stats(k_rhb, k_lhb, bb_rhb, bb_lhb, percent_rhb, percent_lhb)

    k9 = (strikeouts / ip) * 9
    batters_per_inning = tbf / ip if ip > 0 else 0

    # Trifecta evaluations
    results = {
        "K%": evaluate_metric(weighted_k, {"over": 0.25, "neutral_low": 0.22, "neutral_high": 0.24}),
        "K/9": evaluate_metric(k9, {"over": 9.5, "neutral_low": 7.5, "neutral_high": 9.4}),
        "K-BB%": evaluate_metric(k_bb, {"over": 0.15, "neutral_low": 0.10, "neutral_high": 0.14}),
        "Batters/Inning": evaluate_metric(batters_per_inning, {"over": 0, "neutral_low": 3.9, "neutral_high": 4.2}) if batters_per_inning <= 3.8 else "Under"
    }

    st.subheader("Results")
    st.write(f"Weighted K%: {weighted_k * 100:.1f}% → {results['K%']}")
    st.write(f"K/9: {k9:.1f} → {results['K/9']}")
    st.write(f"K-BB%: {k_bb * 100:.1f}% → {results['K-BB%']}")
    st.write(f"Batters per Inning: {batters_per_inning:.2f} → {results['Batters/Inning']}")

    over = sum(1 for v in results.values() if v == "Over")
    neutral = sum(1 for v in results.values() if v == "Neutral")
    under = sum(1 for v in results.values() if v == "Under")

    st.markdown("---")
    st.write(f"✅ Matches for OVER: {over}")
    st.write(f"➖ Matches for NEUTRAL: {neutral}")
    st.write(f"⛔ Matches for UNDER: {under}")
