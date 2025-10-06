"""
Kevin Roy V. Maglaqui
2025 - 10 - 04
Bitcoin AI Price Forecaster - Demo
Predicts large Bitcoin price movements using ensemble ML models
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from data_fetcher import get_bitcoin_data, get_current_bitcoin_price

# Page config
st.set_page_config(
    page_title="Bitcoin AI Forecast",
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

# API Functions - Define early so they can be used anywhere
def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.Timeout:
        return {"error": "API timeout - server may be slow or unavailable"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API - check your internet connection"}
    except Exception as e:
        return {"error": f"API health check failed: {str(e)}"}

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_model_info():
    try:
        response = requests.get(f"{API_URL}/model/info", timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "API timeout while fetching model info"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API"}
    except Exception as e:
        return {"error": f"Failed to get model info: {str(e)}"}

def make_prediction(symbol="BTCUSDT", interval="1m"):
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json={
                "symbol": symbol,
                "interval": interval,
                "use_live_data": True
            },
            timeout=45
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "Prediction timeout - API is taking too long to respond"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API for prediction"}
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error: {e.response.status_code} - {e.response.text}"}
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

def get_model_age_warning():
    try:
        info = get_model_info()
        if 'metadata' in info and 'training_date' in info['metadata']:
            training_date_str = info['metadata']['training_date']
            
            # Handle format like "20251006_112413"
            if '_' in training_date_str and len(training_date_str) == 15:
                date_part = training_date_str[:8]  # 20251006
                time_part = training_date_str[9:]  # 112413
                training_date = datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S")
            else:
                # Try ISO format
                training_date = datetime.fromisoformat(training_date_str.replace('Z', '+00:00'))
                training_date = training_date.replace(tzinfo=None)
            
            age_days = (datetime.now() - training_date).days
            
            if age_days > 14:
                return f"**Model is {age_days} days old.** For optimal performance with current market conditions, contact {CONTACT_EMAIL} to update the model with fresh market data. The API is available at {API_URL}"
            elif age_days > 7:
                return f"**Model is {age_days} days old.** Consider updating for enhanced accuracy with recent market patterns."
            elif age_days > 3:
                return f"Model is {age_days} days old - performing well with current data."
            else:
                return f"Model is fresh ({age_days} days old) - optimal performance expected."
        return "Model age information unavailable."
    except Exception as e:
        return f"Unable to verify model freshness. Contact support for current model status."

# Chart creation functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_chart_data(interval="5m", limit=200):
    """Fetch data for the startup chart"""
    try:
        df = get_bitcoin_data(interval=interval, limit=limit, with_indicators=True)
        return df
    except Exception as e:
        st.error(f"Failed to fetch chart data: {str(e)}")
        return None

def create_price_chart(df, show_indicators=True):
    """Create an interactive price chart with technical indicators"""
    fig = go.Figure()
    
    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='BTC Price',
        increasing_line_color='#10b981',
        decreasing_line_color='#ef4444'
    ))
    
    if show_indicators and 'SMA_20' in df.columns:
        # Add moving averages
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA_20'],
            mode='lines',
            name='SMA 20',
            line=dict(color='#3b82f6', width=1.5),
            opacity=0.7
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA_50'],
            mode='lines',
            name='SMA 50',
            line=dict(color='#f59e0b', width=1.5),
            opacity=0.7
        ))
        
        # Add Bollinger Bands
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['BB_upper'],
            mode='lines',
            name='BB Upper',
            line=dict(color='#8b5cf6', width=1, dash='dash'),
            opacity=0.5
        ))
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['BB_lower'],
            mode='lines',
            name='BB Lower',
            line=dict(color='#8b5cf6', width=1, dash='dash'),
            opacity=0.5,
            fill='tonexty',
            fillcolor='rgba(139, 92, 246, 0.1)'
        ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Bitcoin Price Chart (Real-time Binance Data)',
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title='Time',
        yaxis_title='Price (USD)',
        template='plotly_white',
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#374151', size=12),
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

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
    
    # API Status Check
    st.markdown("### API Status")
    api_status = check_api_health()
    if api_status and "error" not in api_status and api_status.get('status') == 'healthy':
        st.success("**API Connected** ✓")
        st.caption(f"Models Loaded: {'Yes' if api_status.get('model_loaded') else 'No'}")
    elif api_status and "error" in api_status:
        st.error(f"**API Error**")
        st.caption(api_status['error'])
    else:
        st.warning("**API Status Unknown**")
    
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

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # Live Bitcoin Price Chart (shown on startup)
    st.markdown("### Live Bitcoin Market Data")
    
    # Fetch and display current price
    try:
        current_data = get_current_bitcoin_price()
        
        col_price1, col_price2, col_price3, col_price4 = st.columns(4)
        with col_price1:
            st.metric(
                "Current Price",
                f"${current_data['price']:,.2f}",
                delta=f"{current_data['change_percent']:.2f}%"
            )
        with col_price2:
            st.metric("24h High", f"${current_data['high_24h']:,.2f}")
        with col_price3:
            st.metric("24h Low", f"${current_data['low_24h']:,.2f}")
        with col_price4:
            st.metric("24h Volume", f"{current_data['volume']:,.0f} BTC")
    except Exception as e:
        st.warning(f"Unable to fetch current price: {str(e)}")
    
    # Interactive chart with timeframe selector
    chart_interval = st.selectbox(
        "Select Timeframe",
        options=["1m", "5m", "15m", "1h", "4h"],
        index=1,  # Default to 5m
        help="Choose the candlestick timeframe"
    )
    
    # Fetch and display chart
    with st.spinner("Loading chart data..."):
        chart_data = fetch_chart_data(interval=chart_interval, limit=200)
        
        if chart_data is not None and not chart_data.empty:
            chart = create_price_chart(chart_data, show_indicators=True)
            st.plotly_chart(chart, use_container_width=True)
        else:
            st.error("Failed to load chart data. Please refresh the page.")
    
    st.markdown("---")
    
    st.markdown("### Generate Prediction")
    
    # Check API status
    health = check_api_health()
    
    # Debug info - can be removed later
    with st.expander("🔍 API Connection Status (Debug Info)"):
        st.write(f"**API URL:** {API_URL}")
        st.write(f"**Health Check Response:**")
        st.json(health)
        
        # Test additional endpoints
        if st.button("Test Model Info Endpoint"):
            model_info = get_model_info()
            st.json(model_info)
    
    if health is None:
        st.error("**API Service Unavailable** - No response from API server.")
        st.info(f"Attempting to connect to: {API_URL}")
        st.stop()
    elif "error" in health:
        st.error(f"**API Error:** {health['error']}")
        st.info(f"API URL: {API_URL}")
        st.stop()
    elif not health.get('model_loaded', False):
        st.warning("**Models Not Loaded** - API is running but models are not ready.")
        st.info("Please wait for models to load or check API server logs.")
        st.stop()
    
    # Model age warning
    age_warning = get_model_age_warning()
    if age_warning:
        # Safely check the warning type without parsing integers
        if "contact" in age_warning.lower():
            # Critical warning - model is old, contact needed
            st.markdown(f"""
            <div class="warning-box">
                <strong>Model Status:</strong> {age_warning}
            </div>
            """, unsafe_allow_html=True)
        elif "Consider updating" in age_warning or "old" in age_warning.lower():
            # Warning - model needs updating soon
            st.warning(f"**Model Status:** {age_warning}")
        else:
            # Info - model is fresh
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
                    
                    # Provide helpful troubleshooting information
                    with st.expander("🔧 Troubleshooting Information"):
                        st.markdown("""
                        **Common API Issues:**
                        
                        1. **Server Error (500)**: The API encountered an internal error
                           - This may be due to data processing issues
                           - The model may need fresh data
                           - Contact support for assistance
                        
                        2. **Timeout**: The API is taking too long to respond
                           - The server may be cold-starting (first request after idle)
                           - Try again in a few moments
                        
                        3. **Connection Error**: Cannot reach the API
                           - Check your internet connection
                           - Verify API is running
                        
                        **Contact Information:**
                        - Email: kevinroymaglaqui29@gmail.com
                        - API URL: https://btc-forecast-api.onrender.com
                        
                        For immediate assistance with model updates or API issues, please reach out.
                        """)
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
