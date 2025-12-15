
# Site Suitability Interactive Heatmap App – Context

## Goal
Build an interactive decision-support heatmap tool to explore site suitability
by week, variable, and historical window using human-readable site names.

## Core Concepts
- Heatmaps are the primary visual metaphor
- Variable-specific color semantics matter
- Suitability is relative per week
- suitability_score == 0 is always a hard no-go
- sites_fixed.csv is authoritative for site identity

## User Controls
- Data Window: 2018–2024 | Last 4 years | 2024 only
- Variable: Suitability | Temperature | Humidity | Wind
- Cell Display: Rank | Raw value | Suitability | Blank

## Data Architecture
### Dimensions
- sites_fixed.csv (site_id, site_name, lat, long, metadata)

### Metrics (Raw)
- weekly_master_2024.csv
- weekly_master_last4y.csv
- weekly_master_full_2018_2024.csv

### Derived (Decision Surfaces)
- weekly_spatial_2024_dense_ranked.csv
- weekly_spatial_last4y_dense_ranked.csv
- weekly_spatial_full_history_dense_ranked.csv

### Excluded from App
- layer1_*
- weekly_summary_*
- layer2_*

## Visualization Rules
- Suitability: traffic-light, relative per week, zero pinned red
- Temperature: blue → beige/green → red
- Humidity/Wind: neutral → warning → red

## Status
- Project scoped as app-like tool
- File hierarchy designed
- No core code written yet
- Next step: data_loader.py

## Tooling
- Built initially in Google Colab
- Logic separated from notebooks
- Planned migration to Streamlit or Dash
