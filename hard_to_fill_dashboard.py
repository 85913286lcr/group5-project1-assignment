"""Notebook 4: an interactive dashboard for Business Objective 1 — hard-to-fill IT job categories."""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Hard-to-Fill IT Categories", page_icon="🎯", layout="wide")
st.title("Which IT Job Categories Are High-Demand and Hard to Fill?")
st.caption("Singapore IT job postings · Demand, applicant scarcity, and open-posting backlog by category")

# 1. Load only the columns this page needs. A file change invalidates the cache.
DATA_PATH = Path(__file__).resolve().parent / "jobs_clean.csv"
REQUIRED_COLUMNS = [
    "metadata_jobPostId", "it_job_category", "numberOfVacancies",
    "metadata_totalNumberJobApplication", "metadata_repostCount",
    "status_jobStatus", "average_salary", "minimumYearsExperience",
]


@st.cache_data
def load_data(path, modified_time):
    data = pd.read_csv(path, usecols=REQUIRED_COLUMNS)
    if data["it_job_category"].isna().any():
        raise ValueError("The it_job_category column must not contain missing values.")
    return data


try:
    jobs = load_data(str(DATA_PATH), DATA_PATH.stat().st_mtime_ns)
except (OSError, ValueError) as error:
    st.error(f"Could not load the team dataset: {error}")
    st.stop()

st.caption(f"{len(jobs):,} IT postings across {jobs['it_job_category'].nunique()} categories")


# 2. Recompute the same per-category signals as the notebook: demand, scarcity, backlog, pay.
def rank_score(s, ascending):
    r = s.rank(ascending=ascending, method="average")
    return (r - 1) / (len(s) - 1) * 100 if len(s) > 1 else pd.Series(50.0, index=s.index)


category_metrics = jobs.groupby("it_job_category").agg(
    job_postings=("metadata_jobPostId", "count"),
    total_vacancies=("numberOfVacancies", "sum"),
    total_applications=("metadata_totalNumberJobApplication", "sum"),
    avg_repost=("metadata_repostCount", "mean"),
    pct_open=("status_jobStatus", lambda s: (s == "Open").mean() * 100),
    median_salary=("average_salary", "median"),
    avg_years_exp=("minimumYearsExperience", "mean"),
).reset_index()

category_metrics["applicants_per_vacancy"] = (
    category_metrics["total_applications"] / category_metrics["total_vacancies"]
)
category_metrics["demand_score"] = rank_score(category_metrics["job_postings"], ascending=True)
category_metrics["scarcity_score"] = rank_score(category_metrics["applicants_per_vacancy"], ascending=False)
category_metrics["open_score"] = rank_score(category_metrics["pct_open"], ascending=True)
category_metrics["pay_score"] = rank_score(category_metrics["median_salary"], ascending=True)

# 3. Let the viewer pick which categories to compare before any chart or index is drawn.
category_options = sorted(category_metrics["it_job_category"].tolist())
categories = st.multiselect("IT job categories", category_options, default=category_options,
                             help="Select one or more categories to compare. Clear the selection to start again.")
if not categories:
    st.info("Select at least one IT job category to display the analysis.")
    st.stop()
selected = category_metrics.loc[category_metrics["it_job_category"].isin(categories)].copy()

# 4. Default weighting is equal (1/3 each), matching the notebook. Let the viewer tilt it instead.
st.subheader("Hard-to-fill index weighting")
st.caption("The notebook weights demand, scarcity, and backlog equally. Adjust the sliders to explore other priorities.")
w1, w2, w3 = st.columns(3)
demand_w = w1.slider("Demand weight", 0.0, 1.0, 1.0, 0.1)
scarcity_w = w2.slider("Scarcity weight", 0.0, 1.0, 1.0, 0.1)
backlog_w = w3.slider("Backlog weight", 0.0, 1.0, 1.0, 0.1)
weight_sum = demand_w + scarcity_w + backlog_w
if weight_sum == 0:
    st.info("Set at least one weight above zero to compute the index.")
    st.stop()
selected["hard_to_fill_index"] = (
    selected["demand_score"] * demand_w + selected["scarcity_score"] * scarcity_w + selected["open_score"] * backlog_w
) / weight_sum
selected = selected.sort_values("hard_to_fill_index", ascending=False)

# 5. Flag priority categories relative to the current selection, not a fixed constant.
PRIORITY_THRESHOLD = 66.7
priority_categories = set(selected.loc[selected["hard_to_fill_index"].ge(PRIORITY_THRESHOLD), "it_job_category"])

left, middle, right = st.columns(3)
left.metric("Categories compared", len(selected))
top_row = selected.iloc[0]
middle.metric("Highest hard-to-fill index", top_row["it_job_category"], f"{top_row['hard_to_fill_index']:.0f} / 100")
right.metric("Total postings", f"{int(selected['job_postings'].sum()):,}")

st.subheader("Hard-to-fill ranking")
st.caption(f"Hover for the underlying signals. Categories at or above {PRIORITY_THRESHOLD:.0f} are flagged as priority.")
bar_order = selected.sort_values("hard_to_fill_index")
fig = px.bar(
    bar_order, x="hard_to_fill_index", y="it_job_category", orientation="h",
    custom_data=["job_postings", "applicants_per_vacancy", "pct_open", "median_salary"],
    labels={"hard_to_fill_index": "Hard-to-fill index (0-100)", "it_job_category": "IT job category"},
)
fig.update_traces(
    marker_color=["#eb6834" if c in priority_categories else "#2a78d6" for c in bar_order["it_job_category"]],
    hovertemplate=(
        "%{y}<br>Hard-to-fill index: %{x:.0f}<br>Postings: %{customdata[0]:,}<br>"
        "Applicants/vacancy: %{customdata[1]:.2f}<br>Open: %{customdata[2]:.1f}%<br>"
        "Median salary: SGD %{customdata[3]:,.0f}<extra></extra>"
    ),
)
fig.update_layout(height=450, margin=dict(l=0, r=20, t=15, b=0), xaxis_range=[0, 100])
st.plotly_chart(fig, use_container_width=True)

st.subheader("Demand vs. scarcity landscape")
st.caption("Bubble size is the number of postings. The dashed lines mark the median rank (50) on each axis.")
scatter_fig = px.scatter(
    selected, x="scarcity_score", y="demand_score", size="job_postings", text="it_job_category",
    custom_data=["job_postings", "applicants_per_vacancy", "pct_open"],
    labels={"scarcity_score": "Scarcity score (higher = fewer applicants per vacancy)",
            "demand_score": "Demand score (higher = more postings)"},
    color=selected["it_job_category"].isin(priority_categories).map({True: "Priority", False: "Other"}),
    color_discrete_map={"Priority": "#eb6834", "Other": "#2a78d6"},
)
scatter_fig.update_traces(
    textposition="top center",
    hovertemplate=(
        "Postings: %{customdata[0]:,}<br>Applicants/vacancy: %{customdata[1]:.2f}<br>"
        "Open: %{customdata[2]:.1f}%<extra></extra>"
    ),
)
scatter_fig.add_hline(y=50, line_dash="dash", line_color="#c3c2b7")
scatter_fig.add_vline(x=50, line_dash="dash", line_color="#c3c2b7")
scatter_fig.update_layout(height=500, margin=dict(l=0, r=20, t=15, b=0), legend_title_text="")
st.plotly_chart(scatter_fig, use_container_width=True)

st.subheader("Category summary")
table = selected[[
    "it_job_category", "job_postings", "total_vacancies", "applicants_per_vacancy", "pct_open",
    "avg_repost", "median_salary", "avg_years_exp", "hard_to_fill_index",
]].rename(columns={
    "it_job_category": "IT job category", "job_postings": "Postings", "total_vacancies": "Vacancies",
    "applicants_per_vacancy": "Applicants/vacancy", "pct_open": "Open (%)", "avg_repost": "Avg. reposts",
    "median_salary": "Median salary (SGD)", "avg_years_exp": "Avg. years experience",
    "hard_to_fill_index": "Hard-to-fill index",
})
st.dataframe(table.round(2), hide_index=True, use_container_width=True)

with st.expander("How the hard-to-fill index is calculated"):
    st.write(
        "Each category's demand (posting count), scarcity (applicants per vacancy, inverted), and backlog "
        "(% of postings still Open) is converted to a 0-100 rank across the selected categories, then combined "
        "using the weights above. The notebook's default is an equal 1/3 weighting of all three."
    )
    st.write(
        "Median salary and average reposts are shown as supporting context only — they are not part of the "
        "index. `pay_score` (salary rank) instead feeds Objective 2's pay-gap analysis."
    )
    st.write(
        "\"Other IT\" is a catch-all label rather than a specific specialism, so its large posting volume can "
        "overstate how hard-to-fill it really is relative to the named categories."
    )
