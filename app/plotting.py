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
    site_order: list[str] | None = None,  # <-- ORDER IS PASSED IN
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
    # APPLY SITE ORDER (IF PROVIDED)
    # -----------------------------
    if site_order is not None:
        sites = [s for s in site_order if s in matrix.index]
        matrix = matrix.loc[sites]
    else:
        sites = list(matrix.index)

    weeks = list(matrix.columns)
    z = matrix.values.astype(float)

    # -----------------------------
    # FIGURE SETUP
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
    # COLOR SCALE (ACCESSIBILITY)
    # -----------------------------
    colourblind = st.session_state.get("colourblind", False)
    colorscale = get_colorscale(variable_key, colourblind)

    overlay_text_color = "white" if colourblind else "black"

    # -----------------------------
    # COLOR RANGE
    # -----------------------------
    vmin = var_cfg.get("vmin")
    vmax = var_cfg.get("vmax")
    zmid = (vmin + vmax) / 2 if (not colourblind and vmin is not None and vmax is not None) else None

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
            connectgaps=False,
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
            textfont=dict(color=overlay_text_color, size=10),
        )

    # -----------------------------
    # RANK OVERLAY (HIDE BOTTOM ZEROES)
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
                textfont=dict(color=overlay_text_color, size=11),
            )

    # -----------------------------
    # WINNER OVERLAY (SKIP ZERO-WEEKS)
    # -----------------------------
    if overlay_key == "winner":
        rank_col = var_cfg.get("rank_column")
        if rank_col and rank_col in df.columns:
            rank_matrix = build_site_week_matrix(df, rank_col).loc[sites]
            week_max = matrix.max(axis=0)

            win_x, win_y, hover_text = [], [], []

            for w in weeks:
                if np.isnan(week_max[w]) or week_max[w] <= 0:
                    continue

                for s in sites:
                    if (
                        rank_matrix.loc[s, w] == 1
                        and s in active_sites
                        and w in active_weeks
                    ):
                        win_x.append(w)
                        win_y.append(s)

                        val = matrix.loc[s, w]
                        val_str = (
                            format(val, value_format)
                            + (f" {unit}" if unit else "")
                            if not np.isnan(val)
                            else "N/A"
                        )

                        hover_text.append(
                            f"Site: {s}<br>"
                            f"Week: {w}<br>"
                            f"{var_cfg['label']}: {val_str}<br>"
                            "Rank: 1"
                        )

            if win_x:
                fig.add_trace(
                    go.Scatter(
                        x=win_x,
                        y=win_y,
                        mode="markers",
                        marker=dict(
                            size=16,
                            color="black",
                            line=dict(color="white", width=2),
                        ),
                        text=hover_text,
                        hovertemplate="%{text}<extra></extra>",
                        showlegend=False,
                    )
                )

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
        ),
        yaxis=dict(
            title="Site",
            type="category",
            categoryorder="array",
            categoryarray=sites,
            autorange="reversed",
            showgrid=False,
            zeroline=False,
        ),
    )

    return fig
