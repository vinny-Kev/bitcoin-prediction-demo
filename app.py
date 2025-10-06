"""
🤖 Bitcoin AI Price Predictor - Demo
Predicts large Bitcoin price movements using ensemble ML models
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# Page config
st.set_page_config(
    page_title="Bitcoin AI Predictor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_URL = "https://btc-forecast-api.onrender.com"  # Your deployed Render API
FREE_PREDICTIONS = 3
CONTACT_EMAIL = "kevinroymaglaqui29@gmail.com"

# Initialize session state
if 'prediction_count' not in st.session_state:
    st.session_state.prediction_count = 0
if 'predictions_history' not in st.session_state:
    st.session_state.predictions_history = []

# Custom CSS
st.markdown("""
<style>
    .stAlert {
        margin-top: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 10px;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffecb5;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .demo-limit {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 20px 0;
        font-size: 18px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🤖 Bitcoin AI Price Predictor")
st.markdown("### Predict Large Bitcoin Price Movements with ML")

# Sidebar
with st.sidebar:
    st.image("https://cryptologos.cc/logos/bitcoin-btc-logo.png", width=100)
    st.markdown("---")
    
    # Demo counter
    remaining = FREE_PREDICTIONS - st.session_state.prediction_count
    st.markdown(f"""
    <div class="demo-limit">
        🎁 FREE DEMO<br>
        {remaining} / {FREE_PREDICTIONS} Predictions Remaining
    </div>
    """, unsafe_allow_html=True)
    
    if remaining == 0:
        st.error("⚠️ **Demo Limit Reached**")
        st.markdown(f"""
        **Want unlimited predictions?**
        
        Contact me for:
        - ✅ Unlimited API access
        - ✅ Custom integrations  
        - ✅ Enterprise solutions
        - ✅ Model customization
        
        📧 **{CONTACT_EMAIL}**
        """)
    
    st.markdown("---")
    
    # About
    st.markdown("### 📊 About")
    st.markdown("""
    This AI model predicts **large price movements** (>0.5%) 
    using an ensemble of:
    
    - 🌲 **CatBoost** (40%)
    - 🌳 **Random Forest** (30%)
    - 🧠 **LSTM Neural Network** (30%)
    
    **Features**: 20 technical indicators selected from 70+ features
    
    **Data**: Live Binance API
    """)
    
    st.markdown("---")
    st.markdown("**Built by Kevin Roy Maglaqui**")

# Check API health
def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.json()
    except:
        return None

# Get model info
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_model_info():
    try:
        response = requests.get(f"{API_URL}/model/info", timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Make prediction
def make_prediction(symbol="BTCUSDT", interval="1m"):
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json={
                "symbol": symbol,
                "interval": interval,
                "use_live_data": True
            },
            timeout=30
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Calculate model age
def get_model_age_warning():
    try:
        info = get_model_info()
        if 'metadata' in info and 'training_date' in info['metadata']:
            training_date = datetime.fromisoformat(info['metadata']['training_date'].replace('Z', '+00:00'))
            age_days = (datetime.now() - training_date.replace(tzinfo=None)).days
            
            if age_days > 7:
                return f"⚠️ **Model is {age_days} days old.** Consider retraining for best accuracy."
            elif age_days > 3:
                return f"ℹ️ Model is {age_days} days old."
            else:
                return f"✅ Model is fresh ({age_days} days old)."
        return None
    except:
        return None

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🔮 Get Prediction")
    
    # Check API status
    health = check_api_health()
    if health is None or not health.get('model_loaded', False):
        st.error("❌ **API is offline or models not loaded.** Please start the API server.")
        st.code("uvicorn prediction_api:app --reload", language="bash")
        st.stop()
    
    # Model age warning
    age_warning = get_model_age_warning()
    if age_warning:
        if "⚠️" in age_warning:
            st.warning(age_warning)
        else:
            st.info(age_warning)
    
    # Prediction button
    if st.session_state.prediction_count >= FREE_PREDICTIONS:
        st.error(f"🚫 **Demo limit reached!** Contact {CONTACT_EMAIL} for unlimited access.")
    else:
        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            predict_btn = st.button("🚀 Predict Now", use_container_width=True, type="primary")
        
        if predict_btn:
            with st.spinner("🔮 Analyzing market data..."):
                result = make_prediction()
                
                if 'error' in result:
                    st.error(f"❌ Prediction failed: {result['error']}")
                else:
                    # Increment counter
                    st.session_state.prediction_count += 1
                    st.session_state.predictions_history.append(result)
                    
                    # Display prediction
                    st.markdown("---")
                    st.markdown("### 📈 Prediction Result")
                    
                    # Prediction label
                    label_colors = {
                        "No Significant Movement": "🟡",
                        "Large Upward Movement Expected": "🟢",
                        "Large Downward Movement Expected": "🔴"
                    }
                    
                    label = result['prediction_label']
                    emoji = label_colors.get(label, "⚪")
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 30px; border-radius: 15px; color: white; text-align: center;">
                        <h1>{emoji} {label}</h1>
                        <h2>Confidence: {result['confidence']:.1%}</h2>
                        <p>Current Price: ${result['current_price']:,.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Probabilities
                    col_prob1, col_prob2, col_prob3 = st.columns(3)
                    with col_prob1:
                        st.metric(
                            "No Movement",
                            f"{result['probabilities']['no_movement']:.1%}",
                            help="Probability of no significant price change"
                        )
                    with col_prob2:
                        st.metric(
                            "Large Up ↗️",
                            f"{result['probabilities']['large_up']:.1%}",
                            help="Probability of large upward movement"
                        )
                    with col_prob3:
                        st.metric(
                            "Large Down ↘️",
                            f"{result['probabilities']['large_down']:.1%}",
                            help="Probability of large downward movement"
                        )
                    
                    # Price projection chart
                    if result.get('next_periods'):
                        st.markdown("### 📊 Projected Price Movement")
                        
                        periods = [0] + [p['period'] for p in result['next_periods']]
                        prices = [result['current_price']] + [p['estimated_price'] for p in result['next_periods']]
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=periods,
                            y=prices,
                            mode='lines+markers',
                            name='Projected Price',
                            line=dict(color='#667eea', width=3),
                            marker=dict(size=8)
                        ))
                        
                        fig.update_layout(
                            title="Expected Price Trajectory (Next 6 Periods)",
                            xaxis_title="Periods Ahead",
                            yaxis_title="Price (USD)",
                            hovermode='x unified',
                            template='plotly_dark'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Show remaining predictions
                    remaining = FREE_PREDICTIONS - st.session_state.prediction_count
                    if remaining > 0:
                        st.info(f"ℹ️ You have **{remaining} free predictions** remaining.")
                    else:
                        st.error(f"🚫 Demo limit reached! Contact **{CONTACT_EMAIL}** for unlimited access.")

with col2:
    st.markdown("### 📊 Model Stats")
    
    # Get model info
    info = get_model_info()
    
    if 'error' not in info and 'metadata' in info:
        metadata = info['metadata']
        
        st.metric("Features", info.get('feature_count', 'N/A'))
        st.metric("Sequence Length", info.get('sequence_length', 'N/A'))
        st.metric("Train Samples", metadata.get('train_samples', 'N/A'))
        st.metric("Test Samples", metadata.get('test_samples', 'N/A'))
        
        if 'test_accuracy' in metadata:
            st.metric("Test Accuracy", f"{metadata['test_accuracy']:.2%}")
        
        if 'cv_mean_accuracy' in metadata:
            st.metric("CV Accuracy (Mean)", f"{metadata['cv_mean_accuracy']:.2%}")
            st.caption(f"± {metadata.get('cv_std_accuracy', 0):.2%}")
        
        # Training date
        if 'training_date' in metadata:
            st.markdown("---")
            st.caption(f"📅 Trained: {metadata['training_date']}")
    
    # Prediction history
    if st.session_state.predictions_history:
        st.markdown("---")
        st.markdown("### 📜 History")
        
        for i, pred in enumerate(reversed(st.session_state.predictions_history[-5:])):
            label_emoji = {
                0: "🟡",
                1: "🟢",
                2: "🔴"
            }
            emoji = label_emoji.get(pred['prediction'], "⚪")
            
            st.caption(f"{emoji} {pred['timestamp'][:19]}")
            st.caption(f"   Confidence: {pred['confidence']:.1%}")

# Footer
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown("### 🌟 Features")
    st.markdown("""
    - Real-time Binance data
    - 20 technical indicators
    - Ensemble ML models
    - High-confidence predictions
    """)

with col_f2:
    st.markdown("### 📈 Use Cases")
    st.markdown("""
    - Swing trading signals
    - Risk management
    - Market sentiment analysis
    - Entry/exit timing
    """)

with col_f3:
    st.markdown("### 💼 Contact")
    st.markdown(f"""
    **Want more?**
    
    📧 {CONTACT_EMAIL}
    
    - Unlimited API access
    - Custom integrations
    - Enterprise solutions
    """)

st.markdown("---")
st.caption("⚠️ **Disclaimer**: This is an AI prediction tool for educational purposes. Not financial advice. Trade at your own risk.")
