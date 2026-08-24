import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Setting Page Configuration
st.set_page_config(
    page_title="IBNR Explorer - Actuarial Toolkit",
    page_icon="📊",
    layout="wide"
)

st.title("📊 IBNR Explorer: Actuarial Reserving Toolkit")
st.markdown("**TIRA Compliance & Non-Life Reserving Dashboard**")
st.markdown("---")

# 1. Sidebar - Data Input Section
st.sidebar.header("📁 Data Options")
uploaded_file = st.sidebar.file_uploader("Upload Claims CSV File", type=["csv"])

# Load Dataset Safely
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("Custom Dataset Loaded!")
else:
    try:
        df = pd.read_csv("claims_data.csv")
        st.sidebar.info("Using Default Tanzanian Motor Claims Dataset")
    except Exception as e:
        st.error("File la 'claims_data.csv' halipatikani. Hakikisha lipo kwenye folder moja na app.py!")
        st.stop()

# 2. Data Processing Pipeline
df['AccidentDate'] = pd.to_datetime(df['AccidentDate'])
df['PaymentDate'] = pd.to_datetime(df['PaymentDate'])
df['AccidentYear'] = df['AccidentDate'].dt.year
df['PaymentYear'] = df['PaymentDate'].dt.year
df['DevYear'] = df['PaymentYear'] - df['AccidentYear']
df = df[df['DevYear'] >= 0]

# 3. Build Cumulative Triangle
incremental_triangle = df.pivot_table(
    index='AccidentYear',
    columns='DevYear',
    values='PaidAmount',
    aggfunc='sum'
).fillna(0)
cumulative_triangle = incremental_triangle.cumsum(axis=1)

# 4. Calculate Weighted Link Ratios
num_dev_years = cumulative_triangle.shape[1]
weighted_link_ratios = {}
for dev_year in range(num_dev_years - 1):
    current_losses = cumulative_triangle.iloc[:(num_dev_years - dev_year - 1), dev_year]
    next_losses = cumulative_triangle.iloc[:(num_dev_years - dev_year - 1), dev_year + 1]
    if current_losses.sum() > 0:
        weighted_factor = next_losses.sum() / current_losses.sum()
    else:
        weighted_factor = 1.0
    weighted_link_ratios[f'Dev {dev_year}-{dev_year+1}'] = weighted_factor

# Sidebar Inputs for Assumptions
st.sidebar.markdown("---")
st.sidebar.header("⚙️ Actuarial Assumptions")
tail_factor = st.sidebar.number_input("Tail Factor (Dev Ultimate):", min_value=1.0000, value=1.0000, step=0.005, format="%.4f")

# 5. Calculate CDFs & Reserves (FIXED VECTOR LENGTH MISMATCH HERE)
factors = list(weighted_link_ratios.values()) + [tail_factor]

# Compute cumulative factors starting from each dev step to ultimate
cdfs_by_dev = [np.prod(factors[i:]) for i in range(len(factors))]

latest_paid = []
ay_cdfs = []
cols = cumulative_triangle.columns.tolist()
num_rows = len(cumulative_triangle)

for i, ay in enumerate(cumulative_triangle.index):
    # Determine dev column index corresponding to diagonal
    col_idx = min(num_rows - 1 - i, len(cols) - 1)
    col_name = cols[col_idx]
    
    # Extract Latest Diagonal Value
    latest_paid.append(cumulative_triangle.loc[ay, col_name])
    
    # Select appropriate CDF matching column position
    if col_idx < len(cdfs_by_dev):
        ay_cdfs.append(cdfs_by_dev[col_idx])
    else:
        ay_cdfs.append(1.0)

# Build Dataframe safely with guaranteed equal array lengths
summary_df = pd.DataFrame({
    'Accident Year': cumulative_triangle.index,
    'Latest Paid (TZS)': latest_paid,
    'CDF': ay_cdfs
})

summary_df['Ultimate Loss (TZS)'] = summary_df['Latest Paid (TZS)'] * summary_df['CDF']
summary_df['IBNR Reserve (TZS)'] = summary_df['Ultimate Loss (TZS)'] - summary_df['Latest Paid (TZS)']

total_paid = summary_df['Latest Paid (TZS)'].sum()
total_ultimate = summary_df['Ultimate Loss (TZS)'].sum()
total_ibnr = summary_df['IBNR Reserve (TZS)'].sum()

# --- DASHBOARD LAYOUT ---

# Top KPI Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Cumulative Paid", f"TZS {total_paid:,.0f}")
col2.metric("Total Ultimate Loss", f"TZS {total_ultimate:,.0f}")
col3.metric("Required IBNR Reserve", f"TZS {total_ibnr:,.0f}", delta=f"{((total_ibnr/total_paid)*100):.1f}% Loading" if total_paid > 0 else "0%")

st.markdown("---")

# Main Dashboard Tabs
tab1, tab2, tab3 = st.tabs(["📊 Loss Triangle", "📈 Link Ratios", "📋 IBNR Reserve Summary"])

with tab1:
    st.subheader("Cumulative Paid Loss Triangle (TZS)")
    st.dataframe(cumulative_triangle.style.format("{:,.0f}"), use_container_width=True)
    
    # Loss Development Plot
    st.subheader("Claims Development Curves")
    plot_df = cumulative_triangle.reset_index().melt(id_vars='AccidentYear', var_name='DevYear', value_name='PaidAmount')
    fig = px.line(plot_df, x='DevYear', y='PaidAmount', color='AccidentYear', markers=True, title="Cumulative Paid Losses by Development Year")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Weighted Average Link Ratios (Age-to-Age)")
    lr_df = pd.DataFrame(list(weighted_link_ratios.items()), columns=['Development Period', 'Link Ratio (LDF)'])
    st.table(lr_df.style.format({'Link Ratio (LDF)': '{:.4f}'}))

with tab3:
    st.subheader("IBNR Reserving Summary")
    st.dataframe(
        summary_df.style.format({
            'Latest Paid (TZS)': '{:,.0f}',
            'CDF': '{:.4f}',
            'Ultimate Loss (TZS)': '{:,.0f}',
            'IBNR Reserve (TZS)': '{:,.0f}'
        }), use_container_width=True
    )