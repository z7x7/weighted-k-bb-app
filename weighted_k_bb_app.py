
import streamlit as st

def calculate_weighted_stats(k_rhb, k_lhb, bb_rhb, bb_lhb, percent_rhb, percent_lhb):
    weighted_k = (k_rhb * percent_rhb) + (k_lhb * percent_lhb)
    weighted_bb = (bb_rhb * percent_rhb) + (bb_lhb * percent_lhb)
    k_bb = weighted_k - weighted_bb
    return round(weighted_k, 4), round(weighted_bb, 4), round(k_bb, 4)

st.title("Weighted K% and BB% Calculator")

st.markdown("""
Enter pitcher stats by handedness and the opponent's lineup split:
""")

k_rhb = st.number_input("K% vs RHB (e.g. 0.30 for 30%)", min_value=0.0, max_value=1.0, value=0.30)
k_lhb = st.number_input("K% vs LHB", min_value=0.0, max_value=1.0, value=0.20)
bb_rhb = st.number_input("BB% vs RHB", min_value=0.0, max_value=1.0, value=0.05)
bb_lhb = st.number_input("BB% vs LHB", min_value=0.0, max_value=1.0, value=0.10)

percent_rhb = st.number_input("% RHB in lineup (e.g. 0.40)", min_value=0.0, max_value=1.0, value=0.333)
percent_lhb = st.number_input("% LHB in lineup (e.g. 0.60)", min_value=0.0, max_value=1.0, value=0.667)

if st.button("Calculate"):
    weighted_k, weighted_bb, k_bb = calculate_weighted_stats(k_rhb, k_lhb, bb_rhb, bb_lhb, percent_rhb, percent_lhb)

    st.subheader("Results")
    st.write(f"Weighted K%: {weighted_k * 100:.1f}%")
    st.write(f"Weighted BB%: {weighted_bb * 100:.1f}%")
    st.write(f"K-BB%: {k_bb * 100:.1f}%")

    if weighted_k >= 0.25:
        st.success("K% Verdict: OVER")
    elif 0.22 <= weighted_k <= 0.24:
        st.warning("K% Verdict: NEUTRAL")
    else:
        st.error("K% Verdict: UNDER")

    if k_bb >= 0.15:
        st.success("K-BB% Verdict: OVER")
    elif 0.10 <= k_bb < 0.15:
        st.warning("K-BB% Verdict: NEUTRAL")
    else:
        st.error("K-BB% Verdict: UNDER")
