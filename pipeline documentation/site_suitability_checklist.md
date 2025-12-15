
# Site Suitability App – Project Checklist

## 🧱 Project Setup
- [ ] Create project root folder
- [ ] Create directory hierarchy (data/, app/, notebooks/, assets/)
- [ ] Add README.md
- [ ] Add requirements.txt

## 📁 Data Organization
- [ ] Place sites_fixed.csv in data/dimensions/
- [ ] Place weekly_master_* files in data/metrics/
- [ ] Place weekly_spatial_*_dense_ranked files in data/derived/
- [ ] Verify all datasets join cleanly on site_id

## 🔍 Data Validation
- [ ] Validate row counts per dataset
- [ ] Validate week coverage (1–53)
- [ ] Validate no missing site mappings
- [ ] Confirm variable units & ranges

## 🧠 Core Logic
- [ ] Implement data loader
- [ ] Implement time-window selection
- [ ] Implement site × week aggregation
- [ ] Implement per-week normalization
- [ ] Enforce suitability_score == 0 → always red

## 🎨 Visualization
- [ ] Define suitability colormap
- [ ] Define temperature diverging colormap
- [ ] Define humidity colormap
- [ ] Define wind colormap
- [ ] Validate visuals with screenshots

## 🧪 Colab Prototype
- [ ] Static suitability heatmap
- [ ] Static environmental heatmaps
- [ ] Add dropdowns (window / variable / display)
- [ ] Validate UX with real questions

## 🚀 App Readiness
- [ ] Refactor logic into app/ modules
- [ ] Confirm notebooks contain no business logic
- [ ] Save screenshots for documentation
- [ ] Decide on Streamlit/Dash migration
