"""an interactive salary dashboard using the team's final selection flag."""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Salary Benchmark Dashboard", page_icon="💼", layout="wide")
st.title("Salary Benchmark by Position Level")
st.caption("Singapore IT job postings · Advertised monthly salary midpoints (SGD)")

# 1. Load only the columns this page needs. A file change invalidates the cache.
DATA_PATH = Path(__file__).resolve().parent / "jobs_clean.csv"


@st.cache_data
def load_data(path, modified_time):
    data = pd.read_csv(path, usecols=[
        "metadata_jobPostId", "position_level", "it_job_category",
        "salary_midpoint", "salary_analysis_ready"
    ])
    if data["salary_analysis_ready"].isna().any() or not data["salary_analysis_ready"].isin([True, False]).all():
        raise ValueError("The salary_analysis_ready column must contain only True or False.")
    return data


try:
    all_jobs = load_data(str(DATA_PATH), DATA_PATH.stat().st_mtime_ns)
except (OSError, ValueError) as error:
    st.error(f"Could not load the team dataset: {error}")
    st.stop()

# 2. Apply the final cleaning flag before calculating any salary statistics.
salary = all_jobs.loc[all_jobs["salary_analysis_ready"].eq(True)].copy()
st.caption(
    f"{len(all_jobs):,} IT postings · {len(salary):,} analysis-ready · "
    f"{len(all_jobs) - len(salary):,} excluded for review"
)

# 3. Combine job-function and position-level filters before all summaries.
category = st.selectbox("IT job category", ["All IT categories"] + sorted(salary["it_job_category"].dropna().unique().tolist()))
category_data = salary if category == "All IT categories" else salary.loc[salary["it_job_category"].eq(category)]
level_options = sorted(salary["position_level"].dropna().unique().tolist())
levels = st.multiselect("Position levels", level_options, default=level_options,
                        help="Select one or more levels to compare. Clear the selection to start again.")
if not levels:
    st.info("Select at least one position level to display the analysis.")
    st.stop()
selected = category_data.loc[category_data["position_level"].isin(levels)]
if selected.empty:
    st.info("No analysis-ready records match this selection.")
    st.stop()

summary = selected.groupby("position_level").agg(
    posting_count=("metadata_jobPostId", "nunique"),
    median_midpoint=("salary_midpoint", "median"),
    q1_midpoint=("salary_midpoint", lambda v: v.quantile(0.25)),
    q3_midpoint=("salary_midpoint", lambda v: v.quantile(0.75)),
).reset_index().sort_values("median_midpoint", ascending=False)

# 4. Show the sample size and one main salary measure.
left, middle, right = st.columns(3)
left.metric("Selected postings", f"{len(selected):,}")
middle.metric("Median monthly midpoint", f"SGD {selected['salary_midpoint'].median():,.2f}")
right.metric("Position levels", selected["position_level"].nunique())

st.subheader("Median salary by position level")
st.caption("Hover over a bar for the posting count and middle 50% range (Q1–Q3).")
chart_data = summary.loc[summary["posting_count"].ge(5)]
if len(chart_data) < len(summary):
    st.info("The chart omits levels with fewer than five selected postings. Their counts remain in the table.")
fig = px.bar(
    chart_data.sort_values("median_midpoint"), x="median_midpoint", y="position_level",
    orientation="h", custom_data=["posting_count", "q1_midpoint", "q3_midpoint"],
    labels={"median_midpoint": "Median monthly midpoint (SGD)", "position_level": "Position level"},
)
fig.update_traces(
    marker_color="#007F78",
    hovertemplate="%{y}<br>Median: SGD %{x:,.2f}<br>Postings: %{customdata[0]:,}<br>Q1–Q3: SGD %{customdata[1]:,.2f}–%{customdata[2]:,.2f}<extra></extra>",
)
fig.update_layout(height=500, margin=dict(l=0, r=20, t=15, b=0), xaxis_tickformat=",.0f")
st.plotly_chart(fig, use_container_width=True)

# 5. Count every selected posting in a salary bin; no sampling is used.
st.subheader("Salary midpoint distribution")
st.caption("Each bar counts postings in a salary interval. Both filters above apply to this chart.")
bin_width = st.select_slider("Salary interval width (SGD)", options=[250, 500, 1000, 2000], value=500)
values = selected["salary_midpoint"]
start = np.floor(values.min() / bin_width) * bin_width
end = (np.floor(values.max() / bin_width) + 1) * bin_width
edges = np.arange(start, end + bin_width / 2, bin_width)
counts, edges = np.histogram(values, bins=edges)
distribution = pd.DataFrame({
    "bin_center": (edges[:-1] + edges[1:]) / 2,
    "postings": counts,
    "interval": [f"SGD {low:,.0f} to < {high:,.0f}" for low, high in zip(edges[:-1], edges[1:])],
})
assert int(distribution["postings"].sum()) == len(selected)
dist_fig = px.bar(distribution, x="bin_center", y="postings", custom_data=["interval"],
                  labels={"bin_center": "Monthly salary midpoint (SGD)", "postings": "Job postings"})
dist_fig.update_traces(marker_color="#315C78", width=bin_width * 0.95,
                       hovertemplate="%{customdata[0]}<br>Postings: %{y:,}<extra></extra>")
dist_fig.add_vline(x=values.median(), line_dash="dash", line_color="#007F78",
                   annotation_text=f"Median: SGD {values.median():,.2f}", annotation_position="top right")
dist_fig.update_layout(height=420, margin=dict(l=0, r=20, t=40, b=0), xaxis_tickformat=",.0f")
st.plotly_chart(dist_fig, use_container_width=True)
st.caption(f"All {int(counts.sum()):,} selected postings are included. The dashed line marks their median.")

st.subheader("Salary summary")
table = summary.copy()
table.loc[table["posting_count"].lt(5), ["median_midpoint", "q1_midpoint", "q3_midpoint"]] = float("nan")
table = table.rename(columns={
    "position_level": "Position level", "posting_count": "Postings",
    "median_midpoint": "Median midpoint (SGD)", "q1_midpoint": "Q1 midpoint (SGD)",
    "q3_midpoint": "Q3 midpoint (SGD)"
})
st.dataframe(table.round(2), hide_index=True, use_container_width=True)
st.caption("Q1–Q3 is the middle 50% of posting midpoints, not the advertised minimum–maximum interval.")
with st.expander("How records are selected"):
    st.write(
        "Only salary_analysis_ready=True records are used: valid Monthly salaries, "
        "Within range under the category × position-level IQR rule, and all option B checks passed. "
        "B requires minimum ≥ SGD 1,000, maximum ≤ SGD 25,000, band width ≤ SGD 10,000, "
        "and maximum/minimum ≤ 3. Original salary values remain unchanged."
    )
    st.write(
        "These are advertised salary midpoints, not actual employee pay. "
        "Position-level comparisons also reflect differences in job functions. "
        "Use the category filter to inspect those differences."
    )
