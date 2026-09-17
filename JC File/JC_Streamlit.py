import pandas as pd
import plotly.express as px
import plotly.graph_objects as gg
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Experience Premium & Salary Dashboard",
    page_icon="📊",
    layout="wide",
)


# 2. Data Loading & Cleaning Function
@st.cache_data
def load_data():
    df = pd.read_csv("jobs_clean.csv")
    df_clean = df.dropna(
        subset=["minimumYearsExperience", "average_salary"]
    ).copy()
    df_clean["minimumYearsExperience"] = df_clean[
        "minimumYearsExperience"
    ].astype(int)
    return df_clean


df = load_data()

# Sidebar Filters
st.sidebar.header("Filter Options")
max_exp = st.sidebar.slider("Max Experience (Years)", 5, 20, 15)

selected_position = st.sidebar.multiselect(
    "Position Levels",
    options=df["positionLevels"].dropna().unique(),
    default=df["positionLevels"].dropna().unique(),
)

selected_category = st.sidebar.multiselect(
    "IT Job Category",
    options=df["it_job_category"].dropna().unique(),
    default=df["it_job_category"].dropna().unique(),
)

# Apply filters
filtered_df = df[
    (df["minimumYearsExperience"] <= max_exp)
    & (df["positionLevels"].isin(selected_position))
    & (df["it_job_category"].isin(selected_category))
]

# st.title
st.title("📊 Experience Premium & Salary Breakdown Dashboard")
st.markdown("Analyze how required years of experience impact salary growth.")

# 3. Aggregations
grouped = (
    filtered_df.groupby("minimumYearsExperience")
    .agg(
        job_count=("average_salary", "count"),
        avg_salary=("average_salary", "mean"),
        median_salary=("average_salary", "median"),
    )
    .reset_index()
)

grouped["avg_sgd_change"] = grouped["avg_salary"].diff()
grouped["avg_pct_change"] = grouped["avg_salary"].pct_change() * 100
grouped["median_sgd_change"] = grouped["median_salary"].diff()
grouped["median_pct_change"] = grouped["median_salary"].pct_change() * 100

# 4. Top Key Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Jobs Filtered", f"{len(filtered_df):,}")
col2.metric("Overall Avg Salary", f"SGD {filtered_df['average_salary'].mean():,.2f}")
col3.metric("Overall Median Salary", f"SGD {filtered_df['average_salary'].median():,.2f}")
col4.metric("Avg Premium (1 Yr vs 0)", f"SGD {grouped.loc[grouped['minimumYearsExperience']==1, 'avg_sgd_change'].values[0]:,.2f}" if 1 in grouped['minimumYearsExperience'].values else "N/A")

st.markdown("---")

# 5. Charts Section
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Salary Trend by Minimum Experience")
    fig_line = gg.Figure()
    fig_line.add_trace(
        gg.Scatter(
            x=grouped["minimumYearsExperience"],
            y=grouped["avg_salary"],
            mode="lines+markers",
            name="Average Salary",
        )
    )
    fig_line.add_trace(
        gg.Scatter(
            x=grouped["minimumYearsExperience"],
            y=grouped["median_salary"],
            mode="lines+markers",
            name="Median Salary",
        )
    )
    fig_line.update_layout(
        xaxis_title="Minimum Years of Experience",
        yaxis_title="Salary (SGD)",
        hovermode="x unified",
    )
    st.plotly_chart(fig_line, use_container_width=True)

with chart_col2:
    st.subheader("YoY Percentage Salary Premium")
    fig_bar = px.bar(
        grouped,
        x="minimumYearsExperience",
        y="avg_pct_change",
        labels={
            "minimumYearsExperience": "Years of Experience",
            "avg_pct_change": "Average Salary % Increase",
        },
        color="avg_pct_change",
        color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# 6. Detailed Table
st.subheader("📋 Experience Premium Table")

table_display = pd.DataFrame({
    "Minimum Experience": grouped["minimumYearsExperience"].apply(
        lambda x: f"{x} Year{'s' if x != 1 else ''}"
    ),
    "Job Count": grouped["job_count"].apply(lambda x: f"{x:,}"),
    "Average Salary": grouped["avg_salary"].apply(lambda x: f"SGD {x:,.2f}"),
    "Avg Change vs Prior Year": grouped.apply(
        lambda r: (
            "-"
            if pd.isna(r["avg_sgd_change"])
            else f"+SGD {r['avg_sgd_change']:,.2f} (+{r['avg_pct_change']:.2f}%)"
        ),
        axis=1,
    ),
    "Median Salary": grouped["median_salary"].apply(lambda x: f"SGD {x:,.2f}"),
    "Median Change vs Prior Year": grouped.apply(
        lambda r: (
            "-"
            if pd.isna(r["median_sgd_change"])
            else f"{'+' if r['median_sgd_change'] >= 0 else '-'}SGD {abs(r['median_sgd_change']):,.2f} ({'+' if r['median_pct_change'] >= 0 else ''}{r['median_pct_change']:.2f}%)"
        ),
        axis=1,
    ),
})

st.dataframe(table_display, use_container_width=True)