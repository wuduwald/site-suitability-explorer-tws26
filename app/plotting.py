import numpy as np
import plotly.graph_objects as go
import streamlit as st

from app.transforms import build_site_week_matrix
from app.config import VARIABLES, get_colorscale


def plot_heatmap(
    df,
    variable_key: str,
    overlay_key: str,
    active_weeks: set,
    active_sites: set,
    show_colorbar: bool = True,
    dataset_label: str | None = None,
):
    var_cfg = VARIABLES[variable_key]

    value_col = var_cfg["column"]
    unit = var_cfg.get("unit")
    value_format = var_cfg.get("value_format", ".2f")

    # -----------------------------
    # BUILD MATRIX
    # -----------------------------
    matrix = build_site_week_matrix(df, value_col)

    # -----------------------------
    # DERIVE SITE ORDER (STATE → SITE)
    # -----------------------------
    site_meta = df[["site_name", "state"]].drop_duplicates()

    if active_sites:
        site_meta = site_meta[site_meta["site_name"].isin(active_sites)]

    if "state" in site_meta.columns:
        site_meta = site_meta.sort_values(["state", "site_name"])
    else:
        site_meta = site_meta.sort_values("site_name")

    ordered_sites = site_meta["site_name"].tolist()

    matrix = matrix.loc[ordered_sites]

    sites = ordered_sites
    weeks = list(matrix.columns)

    # 🔑 FIX 1: mask NaNs explicitly
    z = np.ma.masked_invalid(matrix.values)

    # -----------------------------
    # FIGURE HEIGHT
    # -----------------------------
    fig_height = max(400, len(sites) * 22)
    fig = go.Figure()

    # -----------------------------
    # COLORBAR TITLE
    # -----------------------------
    colorbar_title = (
        f'{var_cfg["label"]} ({unit})'
        if unit and show_colorbar
        else var_cfg["label"]
    )

    # -----------------------------
    # BASE HOVER
    # -----------------------------
    hover_value = (
        f"%{{z:{value_format}}} {unit}"
        if unit
        else f"%{{z:{value_format}}}"
    )

    base_hovertemplate = (
        "Site: %{y}<br>"
        "Week: %{x}<br>"
        f"{var_cfg['label']}: {hover_value}"
        "<extra></extra>"
    )

    # -----------------------------
    # COLOR SCALE (ACCESSIBILITY-AWARE)
    # -----------------------------
    colorscale = get_colorscale(
        variable_key=variable_key,
        colourblind_mode=st.session_state.get("colourblind", False),
    )

    # -----------------------------
    # COLOR RANGE + MIDPOINT
    # -----------------------------
    vmin = var_cfg.get("vmin")
    vmax = var_cfg.get("vmax")

    zmid = None
    if vmin is not None and vmax is not None:
        zmid = (vmin + vmax) / 2

    # -----------------------------
    # HEATMAP
    # -----------------------------
    fig.add_trace(
        go.Heatmap(
            z=z,
            x=weeks,
            y=sites,
            colorscale=colorscale,
            zmin=vmin,
            zmax=vmax,
            zmid=zmid,
            connectgaps=False,  # 🔑 FIX 2: prevent colour extrapolation
            hovertemplate=base_hovertemplate,
            colorbar=dict(
                title=colorbar_title,
                thickness=16,
                len=0.9,
            ) if show_colorbar else None,
        )
    )

    # -----------------------------
    # VALUE OVERLAY
    # -----------------------------
    if overlay_key == "value":
        fig.update_traces(
            text=[
                [
                    "" if np.isnan(matrix.loc[s, w])
                    else format(matrix.loc[s, w], value_format)
                    for w in weeks
                ]
                for s in sites
            ],
            texttemplate="%{text}",
            textfont=dict(color="black", size=10),
        )

    # -----------------------------
    # RANK OVERLAY (HIDE BOTTOM-RANK ZEROS)
    # -----------------------------
    if overlay_key == "rank":
        rank_col = var_cfg.get("rank_column")
        if rank_col and rank_col in df.columns:
            rank_matrix = build_site_week_matrix(df, rank_col).loc[sites]
            worst_rank_per_week = rank_matrix.max(axis=0)

            fig.update_traces(
                text=[
                    [
                        ""
                        if (
                            np.isnan(rank_matrix.loc[s, w])
                            or (
                                rank_matrix.loc[s, w] == worst_rank_per_week[w]
                                and (
                                    np.isnan(matrix.loc[s, w])
                                    or matrix.loc[s, w] <= 0
                                )
                            )
                        )
                        else str(int(rank_matrix.loc[s, w]))
                        for w in weeks
                    ]
                    for s in sites
                ],
                texttemplate="%{text}",
                textfont=dict(color="black", size=11),
            )

    # -----------------------------
    # FOCUS MASK
    # -----------------------------
    shapes = [
        dict(
            type="rect",
            x0=w - 0.5,
            x1=w + 0.5,
            y0=i - 0.5,
            y1=i + 0.5,
            fillcolor="rgba(120,120,120,0.75)",
            line=dict(width=0),
            layer="above",
        )
        for i, s in enumerate(sites)
        for w in weeks
        if s not in active_sites or w not in active_weeks
    ]

    # -----------------------------
    # TITLE + LAYOUT
    # -----------------------------
    subtitle = var_cfg.get("description", "")

    time_window = var_cfg.get("time_window")
    if time_window:
        subtitle += f" (data from {time_window})"

    if unit:
        subtitle += f" [{unit}]"

    if dataset_label:
        subtitle += f" — {dataset_label}"

    fig.update_layout(
        showlegend=False,
        height=fig_height,
        autosize=False,
        margin=dict(l=160, r=60, t=90, b=40),
        title=dict(
            text=(
                f"{var_cfg['label']}<br>"
                f"<span style='font-size:14px; color:#666;'>"
                f"{subtitle}"
                f"</span>"
            ),
            x=0.5,
            xanchor="center",
        ),
        xaxis=dict(
            title="Week",
            showgrid=False,
            zeroline=False,
            domain=[0.0, 1.0],
        ),
        yaxis=dict(
            title="Site",
            type="category",
            categoryorder="array",
            categoryarray=sites,
            autorange="reversed",
            automargin=False,
            ticklabelposition="outside",
            showgrid=False,
            zeroline=False,
        ),
        shapes=shapes,
    )

    return fig
