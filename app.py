"""
Kevin Roy V. Maglaqui
2025 - 10 - 06
Bitcoin AI Price Forecaster - Demo
Predicts large Bitcoin price movements using ensemble ML models
Version: 1.1.0 - Added live charts and improved error handling
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
CONTACT_EMAIL = "kevinroymaglaqui29@gmail.com"

# Initialize session state
if 'predictions_history' not in st.session_state:
    st.session_state.predictions_history = []
if 'latest_prediction' not in st.session_state:
    st.session_state.latest_prediction = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'guest_usage_count' not in st.session_state:
    st.session_state.guest_usage_count = 0
if 'usage_info' not in st.session_state:
    st.session_state.usage_info = None

# API Functions - Define early so they can be used anywhere
def get_api_headers():
    """Get headers with API key if available"""
    headers = {"Content-Type": "application/json"}
    if st.session_state.api_key:
        headers["X-API-Key"] = st.session_state.api_key
    return headers

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

def get_usage_info():
    """Get current API usage information"""
    try:
        headers = get_api_headers()
        response = requests.get(f"{API_URL}/usage", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

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
        headers = get_api_headers()
        response = requests.post(
            f"{API_URL}/predict",
            json={
                "symbol": symbol,
                "interval": interval,
                "use_live_data": True
            },
            headers=headers,
            timeout=45
        )
        
        # Update usage info from response headers
        if 'X-RateLimit-Remaining' in response.headers:
            st.session_state.usage_info = {
                'remaining': int(response.headers.get('X-RateLimit-Remaining', 0)),
                'limit': int(response.headers.get('X-RateLimit-Limit', 0)),
                'reset': response.headers.get('X-RateLimit-Reset', '')
            }
        
        # Track guest usage
        if not st.session_state.api_key:
            st.session_state.guest_usage_count += 1
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return {"error": "Rate limit exceeded", "rate_limit": True}
        elif e.response.status_code == 403:
            return {"error": "Invalid or expired API key", "auth_error": True}
        return {"error": f"HTTP error: {e.response.status_code} - {e.response.text}"}
    except requests.exceptions.Timeout:
        return {"error": "Prediction timeout - API is taking too long to respond"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to API for prediction"}
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
def fetch_chart_data(interval="5m", limit=60):
    """Fetch data for the startup chart"""
    try:
        df = get_bitcoin_data(interval=interval, limit=limit, with_indicators=True)
        return df, "success"
    except Exception as e:
        error_msg = str(e)
        return None, error_msg

def create_price_chart(df, show_indicators=True, data_source="Binance", prediction_result=None):
    """Create an interactive price chart with technical indicators and optional prediction overlay"""
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
    
    # Add prediction overlay if provided
    if prediction_result and 'next_periods' in prediction_result:
        current_price = prediction_result['current_price']
        last_time = df.index[-1]
        
        # Calculate average time interval from the chart data
        if len(df) >= 2:
            time_intervals = [(df.index[i] - df.index[i-1]) for i in range(1, min(6, len(df)))]
            avg_interval = sum(time_intervals, timedelta(0)) / len(time_intervals)
        else:
            avg_interval = timedelta(minutes=5)
        
        # Get the last closing price from the chart
        last_chart_price = float(df['close'].iloc[-1])
        
        # Create prediction line starting from the last chart point
        prediction_times = [last_time]
        prediction_prices = [last_chart_price]  # Start from last chart price
        
        # Add predicted future points
        for period in prediction_result['next_periods']:
            future_time = last_time + (avg_interval * period['period'])
            prediction_times.append(future_time)
            prediction_prices.append(period['estimated_price'])
        
        # Determine color based on prediction
        pred_label = prediction_result.get('prediction_label', '')
        if 'Upward' in pred_label:
            pred_color = '#10b981'  # Green
            pred_name = '▲ AI Prediction: Upward'
        elif 'Downward' in pred_label:
            pred_color = '#ef4444'  # Red
            pred_name = '▼ AI Prediction: Downward'
        else:
            pred_color = '#6b7280'  # Gray
            pred_name = '◯ AI Prediction: Neutral'
        
        # Add prediction line
        fig.add_trace(go.Scatter(
            x=prediction_times,
            y=prediction_prices,
            mode='lines+markers',
            name=pred_name,
            line=dict(color=pred_color, width=3, dash='dash'),
            marker=dict(size=10, symbol='star', color=pred_color),
            opacity=0.9,
            hovertemplate='<b>Predicted Price</b><br>$%{y:,.2f}<br>%{x}<extra></extra>'
        ))
        
        # Add confidence band
        confidence = prediction_result.get('confidence', 0)
        upper_band = [p * (1 + (1 - confidence) * 0.02) for p in prediction_prices]
        lower_band = [p * (1 - (1 - confidence) * 0.02) for p in prediction_prices]
        
        fig.add_trace(go.Scatter(
            x=prediction_times,
            y=upper_band,
            mode='lines',
            name='Confidence Upper',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=prediction_times,
            y=lower_band,
            mode='lines',
            name='Confidence Lower',
            line=dict(width=0),
            fill='tonexty',
            fillcolor=f'rgba({"16, 185, 129" if "Upward" in pred_label else "239, 68, 68" if "Downward" in pred_label else "107, 114, 128"}, 0.1)',
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Dynamic title based on data source
    chart_title = f'Bitcoin Price Chart - Live Data ({data_source})'
    if prediction_result:
        chart_title += ' with AI Prediction Overlay'
    
    # Update layout
    fig.update_layout(
        title={
            'text': chart_title,
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

# Development Disclaimer
st.warning("""
⚠️ **PROJECT IN DEVELOPMENT** - This AI system is still under active development. Some ensemble models may 
occasionally malfunction or produce unexpected results. **Take all forecasts with a grain of salt** - use predictions 
as one of many factors in your analysis, not as definitive trading signals. Always conduct your own research and 
never invest more than you can afford to lose.
""")

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
    
    # API Key & Usage Section
    st.markdown("### 🔑 API Access")
    
    # Show current status
    if st.session_state.api_key:
        st.success("✅ API Key Active")
        # Get and display usage info
        usage = get_usage_info()
        if usage:
            if usage.get('tier') == 'admin':
                st.info("🌟 **Admin Access** - Unlimited usage")
            else:
                remaining = usage.get('calls_remaining', 0)
                limit = usage.get('rate_limit', 0)
                st.metric("Requests Remaining", f"{remaining}/{limit} per min")
        
        if st.button("🔄 Change API Key"):
            st.session_state.api_key = None
            st.rerun()
    else:
        # Guest mode
        guest_used = st.session_state.guest_usage_count
        guest_limit = 3
        
        st.warning(f"👤 **Guest Mode**: {guest_used}/{guest_limit} free predictions used")
        
        if guest_used >= guest_limit:
            st.error("🚫 **Trial Expired**")
            st.markdown("""
            Hosting isn't free! Get your API key to continue:
            
            **Have an API key?** Enter it below for unlimited access!
            """)
        
        # API Key input
        with st.expander("🔐 Enter API Key" if guest_used < guest_limit else "🔐 Enter API Key (Required)", expanded=guest_used >= guest_limit):
            api_key_input = st.text_input(
                "API Key",
                type="password",
                placeholder="Enter your API key here",
                help="Get your API key from the admin"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Activate", use_container_width=True, disabled=not api_key_input):
                    st.session_state.api_key = api_key_input.strip()
                    # Verify the key
                    usage = get_usage_info()
                    if usage:
                        st.success("API key activated!")
                        st.rerun()
                    else:
                        st.error("Invalid API key")
                        st.session_state.api_key = None
            
            with col2:
                if st.button("📋 Copy Admin Key", use_container_width=True):
                    st.info("Contact: kevinroymaglaqui29@gmail.com for admin key")
    
    st.markdown("---")
    
    # About
    st.markdown("### About the Model")
    st.info("🚧 **Status:** In Active Development")
    st.markdown("""
    This AI system predicts **significant price movements** (>0.5%) 
    using an ensemble approach:
    
    • **CatBoost Algorithm** (40% weight)
    • **Random Forest** (30% weight)  
    • **Logistic Regression** (30% weight)
    
    **Technical Features**: 70 optimized indicators analyzed
    
    **Data Source**: Real-time API
    
    ⚠️ **Note**: Some models may occasionally malfunction. 
    Always verify predictions against multiple sources.
    """)
    
    st.markdown("---")
    st.markdown("**Built by Kevin Roy Maglaqui**")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    # Generate Prediction Section - MOVED UP TOP
    st.markdown("### 🎯 Generate AI Prediction")
    
    # Check API status
    health = check_api_health()
    
    if health is None:
        st.error("**API Service Unavailable** - No response from API server.")
        st.info(f"Attempting to connect to: {API_URL}")
    elif "error" in health:
        st.error(f"**API Error:** {health['error']}")
        st.info(f"API URL: {API_URL}")
    elif not health.get('model_loaded', False):
        st.warning("**Models Not Loaded** - API is running but models are not ready.")
        st.info("Please wait for models to load or check API server logs.")
    else:
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
        
        # Check if user can make predictions
        can_predict = True
        if not st.session_state.api_key and st.session_state.guest_usage_count >= 3:
            can_predict = False
            st.error("""
            🚫 **Free trial exhausted** - You've used all 3 free predictions!
            
            **Hosting isn't free!** Please enter your API key in the sidebar to continue.
            
            👉 Check the sidebar for API key input.
            """)
        
        # Prediction button
        predict_btn = st.button(
            "🔮 Generate Prediction", 
            use_container_width=True, 
            type="primary",
            disabled=not can_predict
        )
        
        if predict_btn:
            with st.spinner("🤖 Analyzing market data and generating prediction..."):
                result = make_prediction()
                
                if 'error' in result:
                    # Handle rate limit errors
                    if result.get('rate_limit'):
                        st.error("""
                        ⏱️ **Rate Limit Exceeded**
                        
                        You've made too many requests. Please wait a moment or enter your API key for higher limits.
                        """)
                        st.info("💡 Get an API key in the sidebar for unlimited access!")
                    
                    # Handle auth errors
                    elif result.get('auth_error'):
                        st.error("""
                        🔑 **Authentication Error**
                        
                        Your API key is invalid or expired. Please check your key in the sidebar.
                        """)
                        st.session_state.api_key = None
                        if st.button("🔄 Update API Key"):
                            st.rerun()
                    
                    else:
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
                    # Store prediction
                    st.session_state.predictions_history.append(result)
                    # Store latest prediction for chart overlay
                    st.session_state.latest_prediction = result
                    
                    # Display prediction
                    st.markdown("---")
                    st.markdown("### ✨ Prediction Results")
                    
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
                        st.markdown("### 📈 Projected Price Movement")
                        
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
                    
                    st.success("💡 **Tip:** Scroll down to see the prediction overlay on the live chart!")
    
    st.markdown("---")
    
    # Live Bitcoin Price Chart (shown on startup)
    st.markdown("### 📊 Live Bitcoin Market Data")
    
    # Fetch and display current price (with multiple fallback sources)
    price_available = False
    data_source = "Unknown"
    try:
        with st.spinner("Fetching current Bitcoin price..."):
            current_data = get_current_bitcoin_price()
            data_source = current_data.get('source', 'Binance')
        
        # Show data source
        if data_source != 'Binance':
            st.info(f"📊 **Data Source:** {data_source} (Binance unavailable in this region)")
        
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
        price_available = True
    except Exception as e:
        error_msg = str(e)
        st.error(f"⚠️ **Unable to fetch Bitcoin price data**")
        st.caption(f"Error: {error_msg[:200]}")
        st.info("💡 **The AI prediction feature below still works!** It uses your deployed API server for predictions.")
    
    # Interactive chart with timeframe selector (only show if we can fetch data)
    if price_available:
        chart_interval = st.selectbox(
            "Select Timeframe",
            options=["1m", "5m", "15m", "1h", "4h"],
            index=1,  # Default to 5m
            help="Choose the candlestick timeframe"
        )
        
        # Fetch and display chart
        with st.spinner("Loading chart data..."):
            chart_data, status = fetch_chart_data(interval=chart_interval, limit=60)
            
            if chart_data is not None and not chart_data.empty:
                # Determine data source from error message or default to Binance
                chart_source = "CryptoCompare" if "CryptoCompare" in status or "Binance" in status else "Binance"
                if "CryptoCompare" in status:
                    st.info("📊 **Chart Data:** Using CryptoCompare (Binance unavailable in this region)")
                
                # Show toggle for prediction overlay if prediction exists
                show_prediction = False
                if st.session_state.latest_prediction:
                    show_prediction = st.checkbox("Show AI Prediction Overlay", value=True, 
                                                  help="Display the latest AI prediction on the chart")
                
                # Create chart with or without prediction overlay
                prediction_to_show = st.session_state.latest_prediction if show_prediction else None
                chart = create_price_chart(chart_data, show_indicators=True, 
                                          data_source=chart_source, 
                                          prediction_result=prediction_to_show)
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.error(f"⚠️ **Unable to load chart data**")
                st.caption(f"Error: {status[:200]}")
                st.info("💡 The AI prediction feature above still works!")
    else:
        st.info("💡 **Chart temporarily unavailable** - Use the AI Prediction feature above to get forecasts!")

with col2:
    st.markdown("### Model Performance")
    
    # Get model info
    info = get_model_info()
    
    if 'error' not in info:
        # Extract metrics - they can be at root level or nested in metadata
        metadata = info.get('metadata', {})
        performance = info.get('performance', metadata.get('performance', {}))
        
        # Basic model info
        st.metric("Features", info.get('feature_count', info.get('n_features', 'N/A')))
        st.metric("Sequence Length", info.get('sequence_length', 'N/A'))
        
        # Training info
        training_date = info.get('training_date', metadata.get('training_date', None))
        if training_date:
            st.caption(f"📅 Trained: {training_date}")
        
        st.markdown("---")
        st.markdown("**Test Performance**")
        
        # Extract accuracy from performance dict or direct metadata
        test_accuracy = performance.get('test_accuracy', metadata.get('performance', {}).get('test', {}).get('accuracy', None))
        if test_accuracy:
            st.metric("Accuracy", f"{test_accuracy:.2%}")
        
        # Extract F1 score
        test_f1 = performance.get('test_f1', metadata.get('performance', {}).get('test', {}).get('f1_macro', None))
        if test_f1:
            st.metric("F1 Score", f"{test_f1:.3f}")
        
        # Extract ROC AUC
        test_roc = performance.get('test_roc_auc', metadata.get('performance', {}).get('test', {}).get('roc_auc_ovr', None))
        if test_roc:
            st.metric("ROC AUC", f"{test_roc:.3f}")
        
        # Extract precision and recall from nested performance
        nested_perf = metadata.get('performance', {}).get('test', {})
        if nested_perf:
            precision = nested_perf.get('precision_macro')
            recall = nested_perf.get('recall_macro')
            
            if precision:
                st.metric("Precision", f"{precision:.3f}")
            if recall:
                st.metric("Recall", f"{recall:.3f}")
        
        # Show overfitting analysis if available
        overfitting = metadata.get('performance', {}).get('overfitting_analysis', {})
        if overfitting:
            st.markdown("---")
            st.markdown("**Model Analysis**")
            acc_gap = overfitting.get('train_test_accuracy_gap')
            if acc_gap:
                st.caption(f"🔍 Accuracy Gap: {acc_gap:.2%}")
                if acc_gap < 0.10:
                    st.caption("✅ Low overfitting")
                elif acc_gap < 0.20:
                    st.caption("⚠️ Moderate overfitting")
                else:
                    st.caption("❌ High overfitting")
    
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
col_f1, col_f2 = st.columns(2)

with col_f1:
    st.markdown("### Key Features")
    st.markdown("""
    - Real-time market data integration
    - 20 optimized technical indicators
    - Ensemble machine learning models
    - High-confidence prediction system
    - Interactive chart with AI overlay
    """)

with col_f2:
    st.markdown("### Applications")
    st.markdown("""
    - Swing trading signal generation
    - Risk management planning
    - Market sentiment analysis
    - Strategic entry/exit timing
    - Educational ML demonstration
    """)

st.markdown("---")
st.error("""
**⚠️ IMPORTANT DISCLAIMER** 

This is an experimental AI prediction tool for educational and research purposes only. The system is **still in development** 
and individual ensemble models may malfunction or produce inaccurate predictions. 

**Take all forecasts with a grain of salt:**
- Not financial advice or trading recommendations
- Predictions should be ONE factor among many in your analysis
- Past performance does not guarantee future results
- Cryptocurrency markets are highly volatile and unpredictable
- Always do your own research (DYOR)
- Never invest more than you can afford to lose
- Trade responsibly and at your own risk

The creators assume no liability for any trading decisions made based on these predictions.
""")
