import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import streamlit as st

from app.data_loader import load_with_sites
from app.plotting import plot_heatmap
from app.transforms import mean_per_site
from app.config import DATASETS, VARIABLES, APP_DEFAULTS, COLORBLIND_MODE_DEFAULT


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Site Suitability Explorer",
    layout="wide",
)


# -----------------------------
# SIDEBAR CONTROLS
# -----------------------------
st.sidebar.header("Controls")

# -----------------------------
# ACCESSIBILITY
# -----------------------------
st.session_state.setdefault("colourblind", COLORBLIND_MODE_DEFAULT)

st.sidebar.toggle(
    "Bruno-Mode 😎",
    key="colourblind",
    help="Provides Mr. Ando with a colourblind friendly palette."
)

# -----------------------------
# DATASET
# -----------------------------
dataset_key = st.sidebar.selectbox(
    "Dataset",
    options=list(DATASETS.keys()),
    index=list(DATASETS.keys()).index(APP_DEFAULTS["dataset"]),
)

# -----------------------------
# VARIABLE
# -----------------------------
variable_key = st.sidebar.selectbox(
    "Variable",
    options=list(VARIABLES.keys()),
    index=list(VARIABLES.keys()).index(APP_DEFAULTS["variable"]),
)

var_cfg = VARIABLES[variable_key]

# -----------------------------
# OVERLAY (SMART / VARIABLE-AWARE)
# -----------------------------
overlay_options = ["none"]

if var_cfg.get("allow_value_overlay", False):
    overlay_options.append("value")

if var_cfg.get("allow_rank_overlay", False):
    overlay_options.append("rank")

if var_cfg.get("allow_winner_strip", False):
    overlay_options.append("winner")

default_overlay = (
    var_cfg.get("default_overlay")
    if var_cfg.get("default_overlay") in overlay_options
    else overlay_options[0]
)

overlay_key = st.sidebar.selectbox(
    "Overlay",
    options=overlay_options,
    index=overlay_options.index(default_overlay),
)

# -----------------------------
# COLORBAR
# -----------------------------
show_colorbar = st.sidebar.checkbox(
    "Show colorbar",
    value=APP_DEFAULTS.get("show_colorbar", True),
)


# -----------------------------
# LOAD DATA (CACHED)
# -----------------------------
@st.cache_data
def load_data(dataset_key):
    return load_with_sites(
        kind="spatial",
        window=dataset_key,
    )

df = load_data(dataset_key)


# -----------------------------
# FOCUS CONTROLS
# -----------------------------
weeks_min = int(df["week_bin"].min())
weeks_max = int(df["week_bin"].max())

week_range = st.sidebar.slider(
    "Weeks",
    min_value=weeks_min,
    max_value=weeks_max,
    value=(weeks_min, weeks_max),
)

active_weeks = set(range(week_range[0], week_range[1] + 1))

all_sites = sorted(df["site_name"].unique())

selected_sites = st.sidebar.multiselect(
    "Sites",
    options=["ALL"] + all_sites,
    default=["ALL"],
)


# -----------------------------
# SITE ORDERING / PRIORITISATION
# -----------------------------
st.sidebar.subheader("Site prioritisation")

sort_mode = st.sidebar.radio(
    "Order sites by",
    options=["Alphabetical", "Mean suitability"],
    index=0,
)

summary_df = None

if sort_mode == "Mean suitability":
    top_n = st.sidebar.slider(
        "Show top N sites",
        min_value=5,
        max_value=min(50, len(all_sites)),
        value=20,
        step=5,
    )

    scores = mean_per_site(
        df=df,
        value_col=var_cfg["column"],
        weeks=active_weeks,
    ).head(top_n)

    active_sites = set(scores.index)

    # -----------------------------
    # BUILD SUMMARY TABLE
    # -----------------------------
    summary_df = (
        df[df["site_name"].isin(scores.index)]
        .loc[df["week_bin"].isin(active_weeks)]
        .groupby("site_name")[var_cfg["column"]]
        .agg(
            mean="mean",
            weeks="count",
        )
        .reset_index()
        .sort_values("mean", ascending=False)
    )

    summary_df["mean"] = summary_df["mean"].round(3)

else:
    if "ALL" in selected_sites or len(selected_sites) == 0:
        active_sites = set(all_sites)
    else:
        active_sites = set(selected_sites)


# -----------------------------
# PLOT
# -----------------------------
fig = plot_heatmap(
    df=df,
    variable_key=variable_key,
    overlay_key=overlay_key,
    active_weeks=active_weeks,
    active_sites=active_sites,
    show_colorbar=show_colorbar,
    dataset_label=DATASETS[dataset_key]["label"],
)

st.plotly_chart(fig, use_container_width=True)


# -----------------------------
# SUMMARY TABLE + EXPORT
# -----------------------------
if summary_df is not None:
    st.subheader("Top sites by mean suitability")

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label="Download summary (CSV)",
        data=summary_df.to_csv(index=False),
        file_name=f"top_sites_{dataset_key}_weeks_{week_range[0]}_{week_range[1]}.csv",
        mime="text/csv",
    )


# -----------------------------
# FOOTER / STAMP
# -----------------------------
st.sidebar.markdown("---")

st.sidebar.markdown(
    """
    <small>
    <b>Site Suitability Explorer</b><br>
    Version 1.0<br>
    Data: ERA5 (weekly aggregates)<br>
    Suitability: precomputed, config-driven<br>
    Author: Henry Tyson
    </small>
    """,
    unsafe_allow_html=True,
)
