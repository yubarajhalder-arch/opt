import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Portfolio Analyzer", layout="wide")

st.title("📊 Simple Portfolio Analyzer — Streamlit App")
st.markdown("""
Upload or edit your asset allocation table, then view weighted metrics, charts and a projection of portfolio value.

Assumptions:
- "Reward (%)" is treated as expected annual return (compounded yearly) for projection.
- "% INVESTED" should sum to 100. If not, the app will normalize the weights before projection.
""")

# Default portfolio data (from the image provided)
def get_default_df():
    data = {
        "ASSET CLASS": [
            "BANK FIXED DEPOSIT", "GOVERNMENT BONDS", "TREASURY BILL", "GOLD ETF",
            "LARGE CAP MUTUAL FUNDS", "CORPORATE BONDS", "PPF", "REAL ESTATE",
            "NIFTY 50", "LIQUID FUND"
        ],
        "RISK (%)": [2, 3, 1, 5, 6, 4, 8, 5, 10, 1],
        "REWARD (%)": [5, 6, 4, 8, 10, 7, 8, 9, 15, 3],
        "TIME(YRS)": [2, 3, 1, 3, 3, 2, 5, 4, 1, 1],
        "% INVESTED": [10, 15, 10, 10, 10, 10, 10, 10, 5, 10]
    }
    df = pd.DataFrame(data)
    return df

# Sidebar inputs
st.sidebar.header("Inputs & Settings")
initial_investment = st.sidebar.number_input("Initial investment (₹)", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
projection_years = st.sidebar.slider("Projection years", min_value=1, max_value=50, value=10)
show_individual_projection = st.sidebar.checkbox("Show individual asset projections", value=True)
normalize_weights = st.sidebar.checkbox("Normalize % INVESTED to sum 100", value=True)

uploaded_file = st.sidebar.file_uploader("Upload CSV with columns: ASSET CLASS, RISK (%), REWARD (%), TIME(YRS), % INVESTED", type=["csv"]) 

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.sidebar.error(f"Error reading CSV: {e}")
        df = get_default_df()
else:
    df = get_default_df()

# Allow user to edit table
st.subheader("Portfolio table (editable)")
edited_df = st.data_editor(df, num_rows="dynamic")

# Basic validation and normalization
if "% INVESTED" not in edited_df.columns:
    st.error("Please include a '% INVESTED' column in the table.")
    st.stop()

weights = edited_df["% INVESTED"].fillna(0).astype(float)
if normalize_weights:
    total = weights.sum()
    if total == 0:
        st.warning("Total % INVESTED is 0. Please enter weights.")
    else:
        weights = weights / total * 100
else:
    total = weights.sum()

# calculate weighted metrics
risk = edited_df["RISK (%)"].astype(float)
reward = edited_df["REWARD (%)"].astype(float)
time = edited_df["TIME(YRS)"].astype(float)
weights_fraction = weights / 100.0

weighted_risk = (risk * weights_fraction).sum()
weighted_reward = (reward * weights_fraction).sum()
weighted_time = (time * weights_fraction).sum()

col1, col2, col3 = st.columns(3)
col1.metric("Weighted Risk (%)", f"{weighted_risk:.2f}")
col2.metric("Weighted Reward (%)", f"{weighted_reward:.2f}")
col3.metric("Weighted Time (yrs)", f"{weighted_time:.2f}")

# Show allocation pie chart
st.subheader("Allocation & asset-level metrics")
alloc_df = edited_df.copy()
alloc_df["% INVESTED (normalized)"] = weights

c1, c2 = st.columns([1,2])
with c1:
    st.write("% Invested (table)")
    st.dataframe(alloc_df.style.format({"% INVESTED (normalized)": "{:.2f}"}), height=300)

with c2:
    fig_pie = px.pie(alloc_df, names="ASSET CLASS", values="% INVESTED (normalized)", title="Portfolio Allocation")
    st.plotly_chart(fig_pie, use_container_width=True)

# Bar charts for risk and reward
br1, br2 = st.columns(2)
with br1:
    fig_risk = px.bar(alloc_df, x="ASSET CLASS", y="RISK (%)", title="Risk (%) by Asset", text_auto=True)
    fig_risk.update_layout(xaxis_tickangle=-45, height=350)
    st.plotly_chart(fig_risk, use_container_width=True)
with br2:
    fig_reward = px.bar(alloc_df, x="ASSET CLASS", y="REWARD (%)", title="Reward (%) by Asset", text_auto=True)
    fig_reward.update_layout(xaxis_tickangle=-45, height=350)
    st.plotly_chart(fig_reward, use_container_width=True)

# Projection section
st.subheader("Projection")
st.write("This projection uses each asset's REWARD (%) as the annual expected return and the % INVESTED as the initial allocation.")

# If weights were normalized, use weights_fraction accordingly
weights_frac = weights_fraction.values
rewards_pct = reward.values / 100.0

# Portfolio-level projection using weighted average return
portfolio_annual_return = weighted_reward / 100.0
years = np.arange(0, projection_years + 1)
portfolio_values = initial_investment * (1 + portfolio_annual_return) ** years

proj_df = pd.DataFrame({"Year": years, "Portfolio Value": portfolio_values})

st.line_chart(proj_df.rename(columns={"Year": "index"}).set_index("index"))

st.write(f"Initial investment: ₹{initial_investment:,.2f}")
st.write(f"Portfolio annual expected return (weighted average): {portfolio_annual_return*100:.2f}%")
st.write(f"Value after {projection_years} years (weighted-average compounding): ₹{portfolio_values[-1]:,.2f}")

# Optional: show individual asset projections
if show_individual_projection:
    st.subheader("Individual asset projections (based on their REWARD %)")
    indiv_vals = {}
    for idx, row in alloc_df.iterrows():
        weight_pct = weights_frac[idx] if idx < len(weights_frac) else 0
        alloc_amount = initial_investment * weight_pct
        r = row["REWARD (%)"] / 100.0
        vals = alloc_amount * (1 + r) ** years
        indiv_vals[row["ASSET CLASS"]] = vals
    indiv_proj_df = pd.DataFrame(indiv_vals, index=years)
    st.dataframe(indiv_proj_df.head(15))

    # stacked area chart using plotly
    indiv_long = indiv_proj_df.reset_index().melt(id_vars=["index"], var_name="Asset", value_name="Value")
    indiv_long.rename(columns={"index":"Year"}, inplace=True)
    fig_area = px.area(indiv_long, x="Year", y="Value", color="Asset", title="Individual Asset Projections (stacked)")
    st.plotly_chart(fig_area, use_container_width=True)

# Download options
st.subheader("Download")
csv = alloc_df.to_csv(index=False).encode("utf-8")
st.download_button("Download allocation as CSV", data=csv, file_name="allocation.csv", mime="text/csv")

# Save projection to CSV for users who want to download it
proj_csv = proj_df.to_csv(index=False).encode("utf-8")
st.download_button("Download portfolio projection (years) as CSV", data=proj_csv, file_name="portfolio_projection.csv", mime="text/csv")

st.markdown("---")
st.write("How to use: edit the table or upload your CSV, tweak inputs from the sidebar and then download results.\n\nIf you want enhancements (Monte Carlo, risk-adjusted returns, inflation, or monthly contributions), tell me what you'd like next!")
