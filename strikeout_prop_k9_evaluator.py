
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

def calculate_weighted_stats(k9_rhb, k9_lhb, bb_rhb, bb_lhb, percent_rhb, percent_lhb):
    weighted_k9 = (k9_rhb * percent_rhb) + (k9_lhb * percent_lhb)
    weighted_bb = (bb_rhb * percent_rhb) + (bb_lhb * percent_lhb)
    k_bb = (weighted_k9 / 9) - weighted_bb  # convert K/9 to K% approximation
    return round(weighted_k9, 2), round(weighted_bb, 4), round(k_bb, 4)

def evaluate_metric(value, thresholds):
    if value >= thresholds['over']:
        return "Over"
    elif thresholds['neutral_low'] <= value <= thresholds['neutral_high']:
        return "Neutral"
    else:
        return "Under"

st.title("Strikeout Prop Evaluator (Full Trifecta with K/9)")

st.markdown("""
Enter pitcher data and matchup to calculate strikeout prop lean:
""")

pitcher_hand = st.selectbox("Pitcher Throws", ["RHP", "LHP"])
rhb = st.number_input("Number of Right-handed Batters", min_value=0, max_value=9, value=5)
lhb = st.number_input("Number of Left-handed Batters", min_value=0, max_value=9, value=2)
sh = st.number_input("Number of Switch-hitters", min_value=0, max_value=9, value=2)

k9_rhb = st.number_input("K/9 vs RHB", min_value=0.0, max_value=20.0, value=9.0)
k9_lhb = st.number_input("K/9 vs LHB", min_value=0.0, max_value=20.0, value=7.5)
bb_rhb = st.number_input("BB% vs RHB (as decimal)", min_value=0.0, max_value=1.0, value=0.05)
bb_lhb = st.number_input("BB% vs LHB (as decimal)", min_value=0.0, max_value=1.0, value=0.10)

ip = st.number_input("Innings Pitched", min_value=0.1, max_value=100.0, value=22.2)
tbf = st.number_input("Total Batters Faced", min_value=1.0, max_value=500.0, value=87.0)

if st.button("Evaluate"):
    percent_rhb, percent_lhb = calculate_handedness_counts(rhb, lhb, sh, pitcher_hand)
    weighted_k9, weighted_bb, k_bb = calculate_weighted_stats(k9_rhb, k9_lhb, bb_rhb, bb_lhb, percent_rhb, percent_lhb)

    batters_per_inning = tbf / ip if ip > 0 else 0

    # Trifecta evaluations
    results = {
        "K/9": evaluate_metric(weighted_k9, {"over": 9.5, "neutral_low": 7.5, "neutral_high": 9.4}),
        "K-BB%": evaluate_metric(k_bb, {"over": 0.15, "neutral_low": 0.10, "neutral_high": 0.14}),
        "Batters/Inning": evaluate_metric(batters_per_inning, {"over": 0, "neutral_low": 3.9, "neutral_high": 4.2}) if batters_per_inning <= 3.8 else "Under"
    }

    st.subheader("Results")
    st.write(f"Weighted K/9: {weighted_k9:.1f} → {results['K/9']}")
    st.write(f"K-BB% (approx): {k_bb * 100:.1f}% → {results['K-BB%']}")
    st.write(f"Batters per Inning: {batters_per_inning:.2f} → {results['Batters/Inning']}")

    over = sum(1 for v in results.values() if v == "Over")
    neutral = sum(1 for v in results.values() if v == "Neutral")
    under = sum(1 for v in results.values() if v == "Under")

    st.markdown("---")
    st.write(f"✅ Matches for OVER: {over}")
    st.write(f"➖ Matches for NEUTRAL: {neutral}")
    st.write(f"⛔ Matches for UNDER: {under}")
