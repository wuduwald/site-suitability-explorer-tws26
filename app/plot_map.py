"""
plot_map.py

Map-based visualization for site suitability.

Uses Plotly Scattergeo (NO Mapbox dependency).
"""

from __future__ import annotations

import plotly.graph_objects as go

from app.transforms import classify_suitability
from app.config import VARIABLES, STATE_NAME_LOOKUP


def plot_suitability_map(
    df,
    variable_key: str,
    week: int,
    height: int = 650,
):
    """
    Plot suitability map for a single week.

    df must include:
      - week_bin
      - site_name
      - state
      - lat
      - long
      - value column
    """

    var_cfg = VARIABLES[variable_key]
    value_col = var_cfg["column"]
    unit = var_cfg.get("unit")

    # -----------------------------
    # Filter week
    # -----------------------------
    data = df[df["week_bin"] == week].copy()
    if data.empty:
        return go.Figure()

    # -----------------------------
    # Classify suitability
    # -----------------------------
    records = []
    for _, row in data.iterrows():
        value = row.get(value_col)
        cls = classify_suitability(value)

        if cls is None:
            continue

        state_code = row.get("state")
        state_name = STATE_NAME_LOOKUP.get(state_code, state_code)

        records.append(
            {
                "site": row["site_name"],
                "state": state_name,
                "lat": float(row["latitude"]),
                "lon": float(row["longitude"]),
                "value": float(value),
                "label": cls["label"],
                "color": cls["color"],
                "size": cls["size"],
            }
        )

    if not records:
        return go.Figure()

    # -----------------------------
    # Hover text
    # -----------------------------
    value_line = f"{var_cfg['label']}: %{{customdata[2]:.2f}}"
    if unit:
        value_line += f" {unit}"

    hovertemplate = (
        "<b>%{customdata[0]}</b><br>"
        "State: %{customdata[1]}<br>"
        + value_line
        + "<br>"
        "Class: %{customdata[3]}"
        "<extra></extra>"
    )

    # -----------------------------
    # Build figure
    # -----------------------------
    fig = go.Figure()

    fig.add_trace(
        go.Scattergeo(
            lat=[r["lat"] for r in records],
            lon=[r["lon"] for r in records],
            mode="markers",
            marker=dict(
                size=[r["size"] for r in records],
                color=[r["color"] for r in records],
                opacity=0.85,
                line=dict(width=0.5, color="white"),
            ),
            customdata=[
                [r["site"], r["state"], r["value"], r["label"]]
                for r in records
            ],
            hovertemplate=hovertemplate,
        )
    )

    # -----------------------------
    # Layout
    # -----------------------------
    fig.update_layout(
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            landcolor="rgb(245,245,245)",
            showlakes=True,
            lakecolor="rgb(220,220,220)",
        ),
        margin=dict(l=0, r=0, t=40, b=0),
        height=height,
        title=dict(
            text=f"{var_cfg['label']} — Week {week}",
            x=0.5,
            xanchor="center",
        ),
        showlegend=False,
    )

    return fig
