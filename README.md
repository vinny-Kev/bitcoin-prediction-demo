# 🤖 Bitcoin AI Price Predictor - Demo

**Live prediction of large Bitcoin price movements using ensemble ML models**

## 🌐 Live Demo

**URL**: TBD (Streamlit Cloud)

## ✨ Features

- 🎁 **3 Free Predictions** - Try it out!
- 🔮 **Real-time Analysis** - Live Binance data
- 🧠 **Ensemble AI** - CatBoost + LSTM + Random Forest
- 📊 **Visual Predictions** - Price projections & confidence scores
- ⚡ **Fast & Lightweight** - Just UI, no heavy ML dependencies

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Environment Setup

The app connects to the API service. Update `API_URL` in `app.py`:

```python
API_URL = "https://your-render-api.onrender.com"  # Production
# API_URL = "http://localhost:8000"  # Local development
```

## 📦 What's Inside

- **`app.py`**: Streamlit dashboard (lightweight, API calls only)
- **`requirements.txt`**: Minimal dependencies (no ML libraries!)

## 🎯 Demo Limitations

- **3 free predictions** per session
- Model age warnings (accuracy degrades over time)
- Contact for unlimited access

## 💼 Upgrade Options

Want unlimited predictions or custom integrations?

**Contact**: kevinroymaglaqui29@gmail.com

- ✅ Unlimited API access
- ✅ Custom integrations
- ✅ Enterprise solutions
- ✅ Model customization

## 🔗 Related Repos

- **API Service**: [bitcoin-api-service](../bitcoin-api-service) (Render deployment)
- **Training Pipeline**: [money-printer](../money-printer) (local only, heavy)

## 📊 Tech Stack

- **Frontend**: Streamlit
- **Charts**: Plotly
- **API Client**: Requests
- **Deployment**: Streamlit Cloud (free tier)

## 🛠️ Deployment to Streamlit Cloud

1. Push this folder to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Select `app.py` as main file
5. Deploy! 🚀

---

**Built with ❤️ by Kevin Roy Maglaqui**
