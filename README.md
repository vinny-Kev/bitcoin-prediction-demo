# ₿ Bitcoin AI Price Predictor# ₿ Bitcoin AI Price Forecaster - Demo



A professional Bitcoin price prediction web app powered by ensemble machine learning models.**Live prediction of large Bitcoin price movements using ensemble ML models**



## 🚀 Live Demo## 🌐 Live Demo



**Streamlit Cloud:** [Your deployment URL here]**URL**: https://bitcoin-prediction-demo.streamlit.app



## ✨ Features## ✨ Features



- **AI Predictions**: Ensemble ML models (CatBoost 40%, Random Forest 30%, Logistic Regression 30%)- 📊 **Live Bitcoin Chart** - Real-time candlestick chart with technical indicators on startup

- **Live Charts**: Real-time Bitcoin price data with technical indicators- 💹 **Current Market Data** - 24h price, high, low, volume metrics

- **Prediction Overlay**: Visual prediction markers and projection lines on chart- 🎁 **3 Free Predictions** - Try the AI predictor!

- **API Integration**: FastAPI backend with authentication and rate limiting- 🔮 **Real-time Analysis** - Live Binance data integration

- **Guest Mode**: 3 free predictions, then API key required- 🧠 **Ensemble AI** - CatBoost + LSTM + Random Forest (40%/30%/30%)

- **v1.1 Enriched**: BUY/SELL/HOLD suggestions, trend analysis, conviction scores, risk levels- � **Technical Indicators** - SMA, EMA, Bollinger Bands, RSI, MACD

- ⏱️ **Multi-Timeframe** - 1m, 5m, 15m, 1h, 4h charts

## 📁 Project Structure- 🎨 **Professional UI** - Clean, modern design

- ⚡ **Fast & Lightweight** - Optimized with caching

```

bitcoin-streamlit-demo/## 🆕 Latest Updates (v1.1.0)

├── app.py              # Main Streamlit application

├── data_fetcher.py     # Bitcoin data fetching with fallbacks- ✅ Live Bitcoin price chart on startup

├── requirements.txt    # Python dependencies- ✅ Real-time market data display

├── runtime.txt         # Python version for Streamlit Cloud- ✅ Technical indicators overlay

├── .streamlit/         # Streamlit config- ✅ Improved error handling

│   └── config.toml- ✅ Browser auto-open on startup

└── docs/               # Documentation files- ✅ Model age validation alerts

```- ✅ Debug mode for API troubleshooting



## 🛠️ Tech Stack## 🚀 Quick Start



- **Frontend**: Streamlit 1.32.0### Local Development

- **Charts**: Plotly 5.18.0

- **Backend API**: FastAPI (deployed on Render)```bash

- **Data Sources**: Binance → CryptoCompare → CoinGecko (fallback chain)# Install dependencies

- **ML Models**: CatBoost, Random Forest, Logistic Regression (70 features)pip install -r requirements.txt



## 📦 Installation# Run the app

streamlit run app.py

### Local Development```



1. **Clone the repository**The browser will automatically open to `http://localhost:8501`

```bash

git clone https://github.com/vinny-Kev/bitcoin-prediction-demo.git### Environment Setup

cd bitcoin-prediction-demo

```The app connects to the deployed API service:



2. **Install dependencies**```python

```bashAPI_URL = "https://btc-forecast-api.onrender.com"  # Production

pip install -r requirements.txt# API_URL = "http://localhost:8000"  # Local development (if running API locally)

``````



3. **Run the app**## 📦 What's Inside

```bash

streamlit run app.py- **`app.py`**: Main Streamlit dashboard

```- **`data_fetcher.py`**: Binance API data fetching module

- **`requirements.txt`**: Python dependencies

The app will open at `http://localhost:8501`- **`.streamlit/config.toml`**: Streamlit configuration

- **Documentation**: API_ISSUE_NOTE.md, FIX_SUMMARY.md, LIVE_CHART_DOCS.md

### Deployment to Streamlit Cloud

## 📊 Live Chart Features

1. Push code to GitHub

2. Go to [share.streamlit.io](https://share.streamlit.io)### Real-time Data Display

3. Connect your repository- Current BTC price with 24h change percentage

4. Deploy!- 24h high, low, and trading volume

- Updates every 5 minutes (cached)

## 🔑 API Key

### Interactive Candlestick Chart

**Guest Mode**: 3 free predictions  - Professional green/red candlestick visualization

**Authenticated**: Rate-limited predictions (3/min)  - Timeframe selector (1m, 5m, 15m, 1h, 4h)

**Admin**: Unlimited access- Technical indicators:

  - SMA 20 (short-term trend)

**Get an API Key**: Email [kevinroymaglaqui29@gmail.com](mailto:kevinroymaglaqui29@gmail.com)  - SMA 50 (medium-term trend)  

  - Bollinger Bands (volatility)

## 📊 How It Works- Hover details with OHLC data

- Responsive design

1. **User clicks "Predict"** → App fetches live Bitcoin data

2. **Sends to backend API** → Ensemble models analyze 70 technical indicators## 🎯 Demo Limitations

3. **Returns prediction** → BUY/SELL/HOLD with confidence, trend, and risk

4. **Chart overlay** → Visual marker or projection line shows prediction- **3 free predictions** per session

- Model age warnings (accuracy degrades over time)

## 🎨 UI Layout- Contact for unlimited access & fresh model updates



```## 💼 Upgrade Options

┌──────────────────────────────────────┬────────────┐

│ 🎯 PREDICTION BUTTON (Top!)         │  METADATA  │Want unlimited predictions or custom integrations?

│   → Color-coded results              │    BOX     │

│   → Probabilities & reasoning        │            │**Contact**: kevinroymaglaqui29@gmail.com

├──────────────────────────────────────┤  • Weights │

│ 📊 LIVE CHART                        │  • Metrics │Services available:

│   → Candlestick + indicators         │  • Warning │- ✅ Unlimited API access

│   → Prediction overlay               │            │- ✅ Fresh model updates with latest market data

└──────────────────────────────────────┴────────────┘- ✅ Custom integrations & webhooks

```- ✅ Enterprise solutions

- ✅ Model customization & fine-tuning

## 🚨 Disclaimer- ✅ Private deployment options



⚠️ **This is a demo project in active development**## 🔗 Related Components



- Models may occasionally malfunction- **API Service**: Deployed on Render at `https://btc-forecast-api.onrender.com`

- **NOT financial advice**- **Training Pipeline**: Separate repo with ML training code

- Use predictions as ONE data point among many- **Data Scraper**: Binance API integration (included in `data_fetcher.py`)

- Never invest more than you can afford to lose

- Always do your own research (DYOR)## 📊 Tech Stack



## 📧 Contact- **Frontend**: Streamlit 1.32.0

- **Charts**: Plotly 5.18.0

**Kevin Roy V. Maglaqui**  - **Data**: Pandas 2.2.0

Email: [kevinroymaglaqui29@gmail.com](mailto:kevinroymaglaqui29@gmail.com)  - **API Client**: Requests 2.31.0

API: `btc-forecast-api.onrender.com`- **Data Source**: Binance Public API

- **Deployment**: Streamlit Cloud (free tier)

---

## 🛠️ Deployment to Streamlit Cloud

**Version**: 1.1.0  

**Last Updated**: October 8, 20251. Push this repo to GitHub

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
