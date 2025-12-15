import numpy as np
import plotly.graph_objects as go

from app.transforms import build_site_week_matrix
from app.config import VARIABLES


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

    matrix = build_site_week_matrix(df, value_col)

    sites = list(matrix.index)
    weeks = list(matrix.columns)

    z = matrix.values

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
    # HEATMAP (LOCKED)
    # -----------------------------
    fig.add_trace(
        go.Heatmap(
            z=z,
            x=weeks,
            y=sites,
            colorscale=var_cfg.get("colorscale", "RdYlGn"),
            zmin=var_cfg.get("vmin"),
            zmax=var_cfg.get("vmax"),
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
    # RANK OVERLAY
    # -----------------------------
    if overlay_key == "rank":
        rank_col = var_cfg.get("rank_column")
        if rank_col and rank_col in df.columns:
            rank_matrix = build_site_week_matrix(df, rank_col)

            fig.update_traces(
                text=[
                    [
                        "" if np.isnan(rank_matrix.loc[s, w])
                        else str(int(rank_matrix.loc[s, w]))
                        for w in weeks
                    ]
                    for s in sites
                ],
                texttemplate="%{text}",
                textfont=dict(color="black", size=11),
            )

    # -----------------------------
    # WINNER OVERLAY (LOCKED AXIS)
    # -----------------------------
    if overlay_key == "winner":
        rank_col = var_cfg.get("rank_column")
        if rank_col and rank_col in df.columns:
            rank_matrix = build_site_week_matrix(df, rank_col)

            win_x, win_y, hover_text = [], [], []

            for w in weeks:
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

            fig.add_trace(
                go.Scatter(
                    x=win_x,
                    y=win_y,
                    yaxis="y",  # CRITICAL
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
    # TITLE + LAYOUT (FULLY LOCKED)
    # -----------------------------
    subtitle = var_cfg.get("description", "")
    if dataset_label:
        subtitle = f"{subtitle} — {dataset_label}"

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
            automargin=False,          # 🔒 KEY FIX
            ticklabelposition="outside",
            showgrid=False,
            zeroline=False,
        ),
        shapes=shapes,
    )

    return fig
