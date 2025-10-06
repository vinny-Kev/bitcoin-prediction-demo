"""
Kevin Roy V. Maglaqui
2025 - 10 - 04
Bitcoin AI Price Predictor - Demo
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
    page_icon="₿",
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
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .warning-box {
        background-color: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
        border-left: 4px solid #f59e0b;
    }
    .demo-limit {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        padding: 18px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 20px 0;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .professional-header {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        padding: 30px;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    .model-status {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin: 16px 0;
        border-left: 4px solid #3b82f6;
    }
    .contact-professional {
        background: #1f2937;
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="professional-header">
    <h1>₿ Bitcoin AI Price Predictor</h1>
    <h3>Machine Learning Forecasting System</h3>
    <p>Predict significant Bitcoin price movements using advanced ensemble models</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Bitcoin.svg/1024px-Bitcoin.svg.png?20140331024207", width=100)
    st.markdown("---")
    
    # Demo counter
    remaining = FREE_PREDICTIONS - st.session_state.prediction_count
    st.markdown(f"""
    <div class="demo-limit">
        FREE DEMO ACCESS<br>
        {remaining} / {FREE_PREDICTIONS} Predictions Remaining
    </div>
    """, unsafe_allow_html=True)
    
    if remaining == 0:
        st.error("**Demo Limit Reached**")
        st.markdown(f"""
        <div class="contact-professional">
        <strong>Upgrade for Full Access</strong><br><br>
        
        Professional services available:
        • Unlimited API access<br>
        • Custom integrations<br>  
        • Enterprise solutions<br>
        • Model customization<br><br>
        
        <strong>Contact: {CONTACT_EMAIL}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # About
    st.markdown("### About the Model")
    st.markdown("""
    This AI system predicts **significant price movements** (>0.5%) 
    using an ensemble approach:
    
    • **CatBoost Algorithm** (40% weight)
    • **Random Forest** (30% weight)  
    • **LSTM Neural Network** (30% weight)
    
    **Technical Features**: 20 optimized indicators from 70+ analyzed
    
    **Data Source**: Real-time Binance API
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

# Calculate model age and provide professional validation messaging
def get_model_age_warning():
    try:
        info = get_model_info()
        if 'metadata' in info and 'training_date' in info['metadata']:
            training_date = datetime.fromisoformat(info['metadata']['training_date'].replace('Z', '+00:00'))
            age_days = (datetime.now() - training_date.replace(tzinfo=None)).days
            
            if age_days > 14:
                return f"**Model is {age_days} days old.** For optimal performance with current market conditions, contact {CONTACT_EMAIL} to update the model with fresh market data. The API is available at {API_URL}"
            elif age_days > 7:
                return f"**Model is {age_days} days old.** Consider updating for enhanced accuracy with recent market patterns."
            elif age_days > 3:
                return f"Model is {age_days} days old - performing well with current data."
            else:
                return f"Model is fresh ({age_days} days old) - optimal performance expected."
        return "Model age information unavailable."
    except:
        return "Unable to verify model freshness. Contact support for current model status."

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Generate Prediction")
    
    # Check API status
    health = check_api_health()
    if health is None or not health.get('model_loaded', False):
        st.error("**API Service Unavailable** - Models not loaded. Please verify the API server is running.")
        st.code("uvicorn prediction_api:app --reload", language="bash")
        st.stop()
    
    # Model age warning
    age_warning = get_model_age_warning()
    if age_warning:
        if "contact" in age_warning.lower() or "days old" in age_warning and int(age_warning.split()[2]) > 14:
            st.markdown(f"""
            <div class="warning-box">
                <strong>Model Status:</strong> {age_warning}
            </div>
            """, unsafe_allow_html=True)
        elif "Consider updating" in age_warning:
            st.warning(f"**Model Status:** {age_warning}")
        else:
            st.markdown(f"""
            <div class="model-status">
                <strong>Model Status:</strong> {age_warning}
            </div>
            """, unsafe_allow_html=True)
    
    # Prediction button
    if st.session_state.prediction_count >= FREE_PREDICTIONS:
        st.error(f"**Demo limit reached.** Contact {CONTACT_EMAIL} for unlimited access and fresh model updates.")
    else:
        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            predict_btn = st.button("Generate Prediction", use_container_width=True, type="primary")
        
        if predict_btn:
            with st.spinner("Analyzing market data and generating prediction..."):
                result = make_prediction()
                
                if 'error' in result:
                    st.error(f"**Prediction failed:** {result['error']}")
                else:
                    # Increment counter
                    st.session_state.prediction_count += 1
                    st.session_state.predictions_history.append(result)
                    
                    # Display prediction
                    st.markdown("---")
                    st.markdown("### Prediction Results")
                    
                    # Prediction label
                    label_indicators = {
                        "No Significant Movement": "◯",
                        "Large Upward Movement Expected": "▲",
                        "Large Downward Movement Expected": "▼"
                    }
                    
                    label = result['prediction_label']
                    indicator = label_indicators.get(label, "●")
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                                padding: 32px; border-radius: 16px; color: white; text-align: center;
                                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);">
                        <h1>{indicator} {label}</h1>
                        <h2>Confidence Level: {result['confidence']:.1%}</h2>
                        <p style="font-size: 18px;">Current BTC Price: ${result['current_price']:,.2f}</p>
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
                            "Large Upward",
                            f"{result['probabilities']['large_up']:.1%}",
                            help="Probability of large upward movement"
                        )
                    with col_prob3:
                        st.metric(
                            "Large Downward",
                            f"{result['probabilities']['large_down']:.1%}",
                            help="Probability of large downward movement"
                        )
                    
                    # Price projection chart
                    if result.get('next_periods'):
                        st.markdown("### Projected Price Movement")
                        
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
                            template='plotly_white',
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#374151')
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Show remaining predictions
                    remaining = FREE_PREDICTIONS - st.session_state.prediction_count
                    if remaining > 0:
                        st.info(f"You have **{remaining} free predictions** remaining in this demo session.")
                    else:
                        st.error(f"**Demo limit reached.** Contact **{CONTACT_EMAIL}** for unlimited access and model updates.")

with col2:
    st.markdown("### Model Performance")
    
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
            st.caption(f"Last Trained: {metadata['training_date']}")
    
    # Prediction history
    if st.session_state.predictions_history:
        st.markdown("---")
        st.markdown("### Recent History")
        
        for i, pred in enumerate(reversed(st.session_state.predictions_history[-5:])):
            label_indicators = {
                0: "⚫",
                1: "�", 
                2: "🔴"
            }
            indicator = label_indicators.get(pred['prediction'], "⚪")
            
            st.caption(f"{indicator} {pred['timestamp'][:19]}")
            st.caption(f"   Confidence: {pred['confidence']:.1%}")

# Footer
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown("### Key Features")
    st.markdown("""
    - Real-time Binance data integration
    - 20 optimized technical indicators
    - Ensemble machine learning models
    - High-confidence prediction system
    """)

with col_f2:
    st.markdown("### Applications")
    st.markdown("""
    - Swing trading signal generation
    - Risk management planning
    - Market sentiment analysis
    - Strategic entry/exit timing
    """)

with col_f3:
    st.markdown("### Professional Services")
    st.markdown(f"""
    **Upgrade Options Available**
    
    Contact: {CONTACT_EMAIL}
    
    - Unlimited API access
    - Custom model integrations
    - Enterprise-grade solutions
    - Real-time model updates
    """)

st.markdown("---")
st.caption("**Disclaimer**: This is an AI prediction tool for educational and research purposes. Not financial advice. Trade responsibly and at your own risk.")
