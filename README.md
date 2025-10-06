# ₿ Bitcoin AI Price Forecaster - Demo

**Live prediction of large Bitcoin price movements using ensemble ML models**

## 🌐 Live Demo

**URL**: https://bitcoin-prediction-demo.streamlit.app (or your deployment URL)

## ✨ Features

- 📊 **Live Bitcoin Chart** - Real-time candlestick chart with technical indicators on startup
- 💹 **Current Market Data** - 24h price, high, low, volume metrics
- 🎁 **3 Free Predictions** - Try the AI predictor!
- 🔮 **Real-time Analysis** - Live Binance data integration
- 🧠 **Ensemble AI** - CatBoost + LSTM + Random Forest (40%/30%/30%)
- � **Technical Indicators** - SMA, EMA, Bollinger Bands, RSI, MACD
- ⏱️ **Multi-Timeframe** - 1m, 5m, 15m, 1h, 4h charts
- 🎨 **Professional UI** - Clean, modern design
- ⚡ **Fast & Lightweight** - Optimized with caching

## 🆕 Latest Updates (v1.1.0)

- ✅ Live Bitcoin price chart on startup
- ✅ Real-time market data display
- ✅ Technical indicators overlay
- ✅ Improved error handling
- ✅ Browser auto-open on startup
- ✅ Model age validation alerts
- ✅ Debug mode for API troubleshooting

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

The browser will automatically open to `http://localhost:8501`

### Environment Setup

The app connects to the deployed API service:

```python
API_URL = "https://btc-forecast-api.onrender.com"  # Production
# API_URL = "http://localhost:8000"  # Local development (if running API locally)
```

## 📦 What's Inside

- **`app.py`**: Main Streamlit dashboard
- **`data_fetcher.py`**: Binance API data fetching module
- **`requirements.txt`**: Python dependencies
- **`.streamlit/config.toml`**: Streamlit configuration
- **Documentation**: API_ISSUE_NOTE.md, FIX_SUMMARY.md, LIVE_CHART_DOCS.md

## 📊 Live Chart Features

### Real-time Data Display
- Current BTC price with 24h change percentage
- 24h high, low, and trading volume
- Updates every 5 minutes (cached)

### Interactive Candlestick Chart
- Professional green/red candlestick visualization
- Timeframe selector (1m, 5m, 15m, 1h, 4h)
- Technical indicators:
  - SMA 20 (short-term trend)
  - SMA 50 (medium-term trend)  
  - Bollinger Bands (volatility)
- Hover details with OHLC data
- Responsive design

## 🎯 Demo Limitations

- **3 free predictions** per session
- Model age warnings (accuracy degrades over time)
- Contact for unlimited access & fresh model updates

## 💼 Upgrade Options

Want unlimited predictions or custom integrations?

**Contact**: kevinroymaglaqui29@gmail.com

Services available:
- ✅ Unlimited API access
- ✅ Fresh model updates with latest market data
- ✅ Custom integrations & webhooks
- ✅ Enterprise solutions
- ✅ Model customization & fine-tuning
- ✅ Private deployment options

## 🔗 Related Components

- **API Service**: Deployed on Render at `https://btc-forecast-api.onrender.com`
- **Training Pipeline**: Separate repo with ML training code
- **Data Scraper**: Binance API integration (included in `data_fetcher.py`)

## 📊 Tech Stack

- **Frontend**: Streamlit 1.32.0
- **Charts**: Plotly 5.18.0
- **Data**: Pandas 2.2.0
- **API Client**: Requests 2.31.0
- **Data Source**: Binance Public API
- **Deployment**: Streamlit Cloud (free tier)

## 🛠️ Deployment to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo: `vinny-Kev/bitcoin-prediction-demo`
4. Set main file: `app.py`
5. Deploy! 🚀

The app will auto-deploy on every push to `main` branch.

## 🐛 Troubleshooting

### Common Issues

1. **"Model age warning"** - Model may be outdated
   - Contact for fresh model updates
   - API available at: https://btc-forecast-api.onrender.com

2. **"API timeout"** - Server may be cold-starting
   - Wait 30 seconds and try again
   - First request after idle takes longer

3. **"Chart not loading"** - Data fetch issue
   - Refresh the page
   - Check Binance API status

4. **"Prediction failed"** - API error
   - See debug expander for details
   - Contact support if persistent

## 📖 Documentation

- `API_ISSUE_NOTE.md` - Known API issues and fixes
- `FIX_SUMMARY.md` - Recent bug fixes
- `LIVE_CHART_DOCS.md` - Chart feature documentation

## 🔄 Version History

- **v1.1.0** (2025-10-06): Live charts, technical indicators, improved UX
- **v1.0.0** (2025-10-04): Initial release with prediction functionality

---

**Built with ❤️ by Kevin Roy Maglaqui**  
**Repository**: https://github.com/vinny-Kev/bitcoin-prediction-demo
