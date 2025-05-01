
import streamlit as st

# Utility functions
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

# Inputs
pitcher_hand = st.selectbox("Pitcher Throws", ["RHP", "LHP"])
rhb = st.number_input("Number of Right-handed Batters", min_value=0, max_value=9, value=5)
lhb = st.number_input("Number of Left-handed Batters", min_value=0, max_value=9, value=2)
sh = st.number_input("Number of Switch-hitters", min_value=0, max_value=9, value=2)

k_rhb = st.number_input("K% vs RHB", min_value=0.0, max_value=1.0, value=0.30)
k9_rhb = st.number_input("K/9 vs RHB", value=9.5)
bb_rhb = st.number_input("BB% vs RHB", min_value=0.0, max_value=1.0, value=0.05)
tbf_rhb = st.number_input("TBF vs RHB", value=50.0)
ip_rhb = st.number_input("IP vs RHB", value=15.0)
babip_rhb = st.number_input("BABIP vs RHB", value=0.280)
xfip_rhb = st.number_input("xFIP vs RHB", value=3.5)
fip_rhb = st.number_input("FIP vs RHB", value=3.3)

k_lhb = st.number_input("K% vs LHB", min_value=0.0, max_value=1.0, value=0.20)
k9_lhb = st.number_input("K/9 vs LHB", value=7.2)
bb_lhb = st.number_input("BB% vs LHB", min_value=0.0, max_value=1.0, value=0.10)
tbf_lhb = st.number_input("TBF vs LHB", value=37.0)
ip_lhb = st.number_input("IP vs LHB", value=10.0)
babip_lhb = st.number_input("BABIP vs LHB", value=0.260)
xfip_lhb = st.number_input("xFIP vs LHB", value=4.0)
fip_lhb = st.number_input("FIP vs LHB", value=3.6)

k_rank = st.number_input("Team K Rank", min_value=1, max_value=30, value=7)
k_avg_season = st.number_input("Season Avg Ks/Game", value=8.4)
k_avg_last3 = st.number_input("Last 3 Games Avg Ks", value=9.3)
k_last_game = st.number_input("Last Game Ks", value=11.0)
k_home = st.number_input("Home Avg Ks/Game", value=8.0)
k_away = st.number_input("Away Avg Ks/Game", value=8.7)
is_home = st.radio("Is today's game at home?", ["Yes", "No"])
k_home_away = k_home if is_home == "Yes" else k_away
pitching_outs_line = st.number_input("Optional: Pitching Outs Line (e.g. 17.5 for 5.2 IP)", min_value=0.0, value=0.0)

era = st.number_input("ERA", min_value=0.0, value=4.50)
hits_line = st.number_input("Hits Allowed Line", min_value=0.0, value=5.5)
k_line = st.number_input("Pitcher's K Line", value=5.5)

if st.button("Analyze"):
    eff_rhb, eff_lhb, percent_rhb, percent_lhb = calculate_handedness_counts(rhb, lhb, sh, pitcher_hand)
    bpi_rhb = tbf_rhb / ip_rhb
    bpi_lhb = tbf_lhb / ip_lhb
    avg_bpi = (bpi_rhb * percent_rhb) + (bpi_lhb * percent_lhb)

    if pitching_outs_line > 0:
        projected_ip = pitching_outs_line / 3.0
        ip_source = f"📘 From sportsbook line ({pitching_outs_line} outs)"
    else:
        projected_ip = 24.0 / avg_bpi
        ip_source = "🧮 Auto-estimated from BPI"

    total_tbf = projected_ip * avg_bpi
    weighted_k_pct = (k_rhb * percent_rhb) + (k_lhb * percent_lhb)
    expected_ks = weighted_k_pct * total_tbf

    kbb_rhb = k_rhb - bb_rhb
    kbb_lhb = k_lhb - bb_lhb
    xfip_fip_rhb_diff = xfip_rhb - fip_rhb
    xfip_fip_lhb_diff = xfip_lhb - fip_lhb

    results = {
        "K% vs RHB": evaluate_metric(k_rhb, {"over": 0.25, "neutral_low": 0.22, "neutral_high": 0.24}),
        "K% vs LHB": evaluate_metric(k_lhb, {"over": 0.25, "neutral_low": 0.22, "neutral_high": 0.24}),
        "K/9 vs RHB": evaluate_metric(k9_rhb, {"over": 9.5, "neutral_low": 7.5, "neutral_high": 9.4}),
        "K/9 vs LHB": evaluate_metric(k9_lhb, {"over": 9.5, "neutral_low": 7.5, "neutral_high": 9.4}),
        "K-BB% vs RHB": evaluate_metric(kbb_rhb, {"over": 0.15, "neutral_low": 0.10, "neutral_high": 0.14}),
        "K-BB% vs LHB": evaluate_metric(kbb_lhb, {"over": 0.15, "neutral_low": 0.10, "neutral_high": 0.14}),
        "Batters/Inning vs RHB": evaluate_metric(bpi_rhb, {"over": 0, "neutral_low": 3.9, "neutral_high": 4.2}) if bpi_rhb <= 3.8 else "Under",
        "Batters/Inning vs LHB": evaluate_metric(bpi_lhb, {"over": 0, "neutral_low": 3.9, "neutral_high": 4.2}) if bpi_lhb <= 3.8 else "Under",
        "Team K Rank": evaluate_metric(-k_rank, {"over": -8, "neutral_low": -20, "neutral_high": -9}),
        "Season Avg Ks/Game": evaluate_metric(k_avg_season, {"over": 8.3, "neutral_low": 7.5, "neutral_high": 8.2}),
        "Last 3 Games Avg Ks": evaluate_metric(k_avg_last3, {"over": 9.0, "neutral_low": 7.0, "neutral_high": 8.9}),
        "Last Game Ks": evaluate_metric(k_last_game, {"over": 10, "neutral_low": 7, "neutral_high": 9}),
        "Home/Away Avg Ks/Game": evaluate_metric(k_home_away, {"over": 8.5, "neutral_low": 7.5, "neutral_high": 8.4}),
        "BABIP vs RHB": evaluate_metric(babip_rhb, {"over": 0.270, "neutral_low": 0.230, "neutral_high": 0.269}),
        "BABIP vs LHB": evaluate_metric(babip_lhb, {"over": 0.270, "neutral_low": 0.230, "neutral_high": 0.269}),
        "xFIP - FIP vs RHB": evaluate_metric(xfip_fip_rhb_diff, {"over": 0.0, "neutral_low": -0.3, "neutral_high": 0.3}),
        "xFIP - FIP vs LHB": evaluate_metric(xfip_fip_lhb_diff, {"over": 0.0, "neutral_low": -0.3, "neutral_high": 0.3})
    }

    st.subheader("Results (17-Metric Evaluation)")
    for label, verdict in results.items():
        st.write(f"{label}: {verdict}")

    over = sum(1 for v in results.values() if v == "Over")
    neutral = sum(1 for v in results.values() if v == "Neutral")
    under = sum(1 for v in results.values() if v == "Under")

    # Add ERA and Hits Line signal into decision-making
    context_signal = ""
    if era > 4.5 and hits_line > 5.5:
        under += 1
        context_signal = "⚠️ High ERA and Hits Line added to UNDER count"
    elif era < 3.5 and hits_line < 5.0:
        over += 1
        context_signal = "✅ Low ERA and Hits Line added to OVER count"
    else:
        context_signal = "➕ ERA and Hits Line had no major impact"

    if over >= 9:
        decision = "✅ Bet OVER K"
    elif under >= 9:
        decision = "⛔ Bet UNDER K"
    else:
        decision = "⚠️ No clear edge — Don't Touch"

    st.markdown("---")
    st.write(f"📊 Weighted K%: {weighted_k_pct:.2%}")
    st.write(f"📈 Expected Ks: {expected_ks:.2f}")
    st.write(f"🎯 K Line: {k_line}")
    st.write(f"🧮 Projected IP: {projected_ip:.2f} ({ip_source})")
    st.write(f"📎 Based on avg BPI: {avg_bpi:.2f}")
    st.markdown("---")
    st.subheader(f"Final Verdict: {decision}")
    st.write(context_signal)
    if expected_ks > k_line:
        st.write("📈 Model sees value on OVER")
    elif expected_ks < k_line:
        st.write("📉 Model sees value on UNDER")
    else:
        st.write("➖ Model is right on the line — no value edge")

    st.markdown("---")
    st.subheader("📌 Context Signals")
    st.write(f"ERA: {era:.2f} | Hits Allowed Line: {hits_line:.1f}")

if st.button("Clear"):
    st.experimental_rerun()
