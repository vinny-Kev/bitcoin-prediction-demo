# Changelog

All notable changes to the Bitcoin AI Price Predictor project.

## [1.1.0] - 2025-10-08

### ✨ Added
- **Clean UI Layout**: Prediction button moved to top, 3:1 column layout
- **Smart Prediction Overlay**: Works with or without `next_periods` data
  - Full mode: Projection line with confidence bands
  - Simple mode: Color-coded marker with annotation
- **Compact Metadata Box**: Red sidebar with model info, ensemble weights, metrics
- **v1.1 API Support**: BUY/SELL/HOLD suggestions, trend analysis, risk levels
- **Auto-fallback**: v1.1 → v1.0 if backend has validation errors

### 🎨 Changed
- Moved prediction section above chart for better UX
- Consolidated all model metadata into right sidebar
- Removed prediction history from main view (kept in session state)
- Simplified footer with just contact info and disclaimer

### 🗑️ Removed
- Duplicate prediction sections
- Debug code and expanders
- Unused imports (`pandas`, `json` from app.py)
- Test files (`test_app.py`, `app_backup.py`)
- Moved documentation to `/docs` folder

### 🐛 Fixed
- Prediction overlay now works without `next_periods` field
- Chart overlay checkbox always functional
- Better error handling for API responses

### 📁 Project Organization
- Created `/docs` folder for documentation
- Cleaned up root directory (7 essential files only)
- Updated README with clear structure

---

## [1.0.0] - 2025-10-06

### Initial Release
- Streamlit web application
- FastAPI backend integration
- Live Bitcoin price charts
- Multi-source data fallbacks (Binance → CryptoCompare → CoinGecko)
- API key authentication system
- Guest mode (3 free predictions)
- Ensemble ML predictions (CatBoost, Random Forest, Logistic Regression)
