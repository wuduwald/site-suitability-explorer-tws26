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
    # BASE HOVER (value only)
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
    # HEATMAP
    # -----------------------------
    fig.add_trace(
        go.Heatmap(
            z=z,
            x=weeks,
            y=sites,
            colorscale=var_cfg.get("colorscale", "rdylgn"),
            zmin=var_cfg.get("vmin"),
            zmax=var_cfg.get("vmax"),
            colorbar=dict(title=colorbar_title) if show_colorbar else None,
            hovertemplate=base_hovertemplate,
        )
    )

    # -----------------------------
    # VALUE OVERLAY
    # -----------------------------
    if overlay_key == "value":
        text = []
        for site in sites:
            row = []
            for week in weeks:
                val = matrix.loc[site, week]
                row.append("" if np.isnan(val) else format(val, value_format))
            text.append(row)

        fig.update_traces(
            text=text,
            texttemplate="%{text}",
            textfont=dict(color="black", size=10),
        )

    # -----------------------------
    # RANK OVERLAY (text + hover)
    # -----------------------------
    if overlay_key == "rank":
        rank_col = var_cfg.get("rank_column")

        if rank_col and rank_col in df.columns:
            rank_matrix = build_site_week_matrix(df, rank_col)

            # ---- cell text
            text = []
            for site in sites:
                row = []
                for week in weeks:
                    r = rank_matrix.loc[site, week]
                    row.append("" if np.isnan(r) else str(int(r)))
                text.append(row)

            fig.update_traces(
                text=text,
                texttemplate="%{text}",
                textfont=dict(color="black", size=11),
            )

            # ---- hover (value + rank)
            hover_text = []
            for site in sites:
                row = []
                for week in weeks:
                    val = matrix.loc[site, week]
                    rank = rank_matrix.loc[site, week]

                    val_str = (
                        format(val, value_format) + (f" {unit}" if unit else "")
                        if not np.isnan(val)
                        else "N/A"
                    )

                    rank_str = str(int(rank)) if not np.isnan(rank) else "N/A"

                    row.append(
                        f"Site: {site}<br>"
                        f"Week: {week}<br>"
                        f"{var_cfg['label']}: {val_str}<br>"
                        f"Rank: {rank_str}"
                    )
                hover_text.append(row)

            fig.update_traces(
                hovertemplate="%{customdata}<extra></extra>",
                customdata=hover_text,
            )

    # -----------------------------
    # WINNER OVERLAY (markers + hover)
    # -----------------------------
    if overlay_key == "winner":
        rank_col = var_cfg.get("rank_column")

        if rank_col and rank_col in df.columns:
            rank_matrix = build_site_week_matrix(df, rank_col)

            win_x, win_y, hover_text = [], [], []

            for week in weeks:
                winners = rank_matrix[week][rank_matrix[week] == 1].index
                for site in winners:
                    if site in active_sites and week in active_weeks:
                        win_x.append(week)
                        win_y.append(site)

                        val = matrix.loc[site, week]
                        val_str = (
                            format(val, value_format) + (f" {unit}" if unit else "")
                            if not np.isnan(val)
                            else "N/A"
                        )

                        hover_text.append(
                            f"Site: {site}<br>"
                            f"Week: {week}<br>"
                            f"{var_cfg['label']}: {val_str}<br>"
                            "Rank: 1"
                        )

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
                    name="",
                )
            )

    # -----------------------------
    # FOCUS MASK
    # -----------------------------
    shapes = []

    for i, site in enumerate(sites):
        for j, week in enumerate(weeks):
            if site not in active_sites or week not in active_weeks:
                shapes.append(
                    dict(
                        type="rect",
                        x0=week - 0.5,
                        x1=week + 0.5,
                        y0=i - 0.5,
                        y1=i + 0.5,
                        fillcolor="rgba(120,120,120,0.75)",
                        line=dict(width=0),
                        layer="above",
                    )
                )

    # -----------------------------
    # TITLE + LAYOUT
    # -----------------------------
    subtitle = var_cfg.get("description", "")
    if dataset_label:
        subtitle = f"{subtitle} — {dataset_label}"

    fig.update_layout(
        title=dict(
            text=(
                f"{var_cfg['label']}<br>"
                f"<span style='font-size:14px; color:#666;'>"
                f"{subtitle}"
                f"</span>"
            ),
            x=0.5,
            xanchor="center",
            yanchor="top",
        ),
        height=fig_height,
        autosize=False,
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
            showgrid=False,
            zeroline=False,
        ),
        yaxis_autorange="reversed",
        margin=dict(l=180, r=40, t=90, b=40),
        shapes=shapes,
    )

    return fig
