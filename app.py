"""
Kevin Roy V. Maglaqui
2025 - 10 - 06
Bitcoin AI Price Forecaster - Demo
Predicts large Bitcoin price movements using ensemble ML models
Version: 1.1.0 - Added live charts and improved error handling
"""

import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
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
if 'api_wake_log' not in st.session_state:
    st.session_state.api_wake_log = []
if 'last_wake_attempt' not in st.session_state:
    st.session_state.last_wake_attempt = None
if 'wake_cooldown' not in st.session_state:
    st.session_state.wake_cooldown = 60  # seconds between manual wake attempts


# API Functions - Define early so they can be used anywhere
def get_api_headers():
    """Get headers with API key if available"""
    headers = {"Content-Type": "application/json"}
    if st.session_state.api_key:
        headers["Authorization"] = f"Bearer {st.session_state.api_key}"
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

def wake_api(max_retries: int = 3, base_delay: float = 2.0):
    """Attempt to wake the Render free-tier API by pinging /health multiple times.

    Returns a dict with status and log entries.
    """
    now = time.time()
    # Throttle wake attempts
    if st.session_state.last_wake_attempt and (now - st.session_state.last_wake_attempt) < st.session_state.wake_cooldown:
        remaining = int(st.session_state.wake_cooldown - (now - st.session_state.last_wake_attempt))
        return {"status": "cooldown", "message": f"Please wait {remaining}s before trying again."}

    st.session_state.last_wake_attempt = now
    log = []
    for attempt in range(1, max_retries + 1):
        try:
            start = time.time()
            timeout = 5 + attempt * 3  # progressively longer
            r = requests.get(f"{API_URL}/health", timeout=timeout)
            elapsed = time.time() - start
            if r.status_code == 200:
                data = r.json()
                log.append(f"Attempt {attempt}: ✅ 200 OK in {elapsed:.2f}s (model_loaded={data.get('model_loaded')})")
                st.session_state.api_wake_log = log
                return {"status": "awake", "log": log, "model_loaded": data.get('model_loaded')}
            else:
                log.append(f"Attempt {attempt}: ⚠️ {r.status_code} {r.text[:60]}")
        except requests.exceptions.Timeout:
            log.append(f"Attempt {attempt}: ⏱️ Timeout after {timeout}s")
        except Exception as e:
            log.append(f"Attempt {attempt}: ❌ Error: {str(e)[:70]}")
        # Backoff before next attempt (non-blocking perspective; small sleep acceptable)
        time.sleep(base_delay * attempt)
    st.session_state.api_wake_log = log
    return {"status": "failed", "log": log}

def get_usage_info():
    """Get current API usage information"""
    try:
        headers = {}
        if st.session_state.api_key:
            headers["Authorization"] = f"Bearer {st.session_state.api_key}"
        response = requests.get(f"{API_URL}/api-keys/usage", headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
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

def make_prediction(symbol="BTCUSDT", interval="1m", use_v1_1=True):
    try:
        headers = get_api_headers()
        
        # Use v1.1 endpoint for enriched response, fallback to v1.0 if it fails
        endpoint = "/v1.1/predict" if use_v1_1 else "/predict"
        
        response = requests.post(
            f"{API_URL}{endpoint}",
            json={
                "symbol": symbol,
                "interval": interval,
                "use_live_data": True
            },
            headers=headers,
            timeout=45
        )
        
        # If v1.1 fails with validation error, try v1.0 fallback
        if response.status_code == 500 and use_v1_1 and 'validation error' in response.text.lower():
            st.warning("⚠️ v1.1 endpoint has a bug, falling back to v1.0...")
            return make_prediction(symbol, interval, use_v1_1=False)
        
        # Check if this was a guest request (no API key)
        # Backend increments guest usage automatically, so we track it here too
        if not st.session_state.api_key:
            # Only increment on success or rate limit (403)
            if response.status_code in [200, 403]:
                st.session_state.guest_usage_count += 1
        
        response.raise_for_status()
        result = response.json()
        
        # Refresh usage info after successful prediction
        if st.session_state.api_key:
            updated_usage = get_usage_info()
            if updated_usage:
                st.session_state.usage_info = updated_usage
        
        return result
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            error_data = e.response.json() if e.response.headers.get('content-type') == 'application/json' else {}
            return {"error": error_data.get('detail', 'Rate limit exceeded'), "rate_limit": True}
        elif e.response.status_code == 403:
            error_data = e.response.json() if e.response.headers.get('content-type') == 'application/json' else {}
            error_msg = error_data.get('detail', 'Access denied')
            # Check if it's guest limit or auth error
            if 'Free trial limit' in error_msg or 'free predictions' in error_msg.lower():
                st.session_state.guest_usage_count = 3  # Sync guest count
                return {"error": error_msg, "guest_limit": True}
            return {"error": error_msg, "auth_error": True}
        elif e.response.status_code == 401:
            return {"error": "Invalid API key", "auth_error": True}
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
    if prediction_result:
        # Determine color and name based on prediction
        suggestion = prediction_result.get('suggestion', {})
        action = suggestion.get('action', None)
        
        if action == 'BUY':
            pred_color = '#10b981'  # Green
            pred_name = '▲ AI Prediction: BUY Signal'
            pred_symbol = 'triangle-up'
        elif action == 'SELL':
            pred_color = '#ef4444'  # Red
            pred_name = '▼ AI Prediction: SELL Signal'
            pred_symbol = 'triangle-down'
        elif action == 'HOLD':
            pred_color = '#f59e0b'  # Orange
            pred_name = '◯ AI Prediction: HOLD'
            pred_symbol = 'diamond'
        else:
            # Fallback to legacy prediction_label
            pred_label = prediction_result.get('prediction_label', '')
            if 'Upward' in pred_label:
                pred_color = '#10b981'
                pred_name = '▲ AI Prediction: Upward'
                pred_symbol = 'triangle-up'
            elif 'Downward' in pred_label:
                pred_color = '#ef4444'
                pred_name = '▼ AI Prediction: Downward'
                pred_symbol = 'triangle-down'
            else:
                pred_color = '#6b7280'
                pred_name = '◯ AI Prediction: Neutral'
                pred_symbol = 'circle'
        
        # Build hover text
        hover_extra = f"<br>Confidence: {prediction_result.get('confidence', 0):.1%}"
        if suggestion:
            hover_extra += f"<br>Action: {action} ({suggestion.get('conviction', 'N/A')})"
            hover_extra += f"<br>Risk: {suggestion.get('risk_level', 'N/A')}"
        trend = prediction_result.get('trend', {})
        if trend:
            hover_extra += f"<br>Trend: {trend.get('short_term', 'N/A')} / {trend.get('long_term', 'N/A')}"
        
        # Check if we have next_periods for full overlay
        if 'next_periods' in prediction_result:
            # FULL OVERLAY WITH PROJECTION LINE
            current_price = prediction_result['current_price']
            last_time = df.index[-1]
            
            # Calculate average time interval
            if len(df) >= 2:
                time_intervals = [(df.index[i] - df.index[i-1]) for i in range(1, min(6, len(df)))]
                avg_interval = sum(time_intervals, timedelta(0)) / len(time_intervals)
            else:
                avg_interval = timedelta(minutes=5)
            
            # Get the last closing price from the chart
            last_chart_price = float(df['close'].iloc[-1])
            
            # Create prediction line starting from the last chart point
            prediction_times = [last_time]
            prediction_prices = [last_chart_price]
            
            # Add predicted future points
            for period in prediction_result['next_periods']:
                future_time = last_time + (avg_interval * period['period'])
                prediction_times.append(future_time)
                prediction_prices.append(period['estimated_price'])
            
            # Add prediction line
            fig.add_trace(go.Scatter(
                x=prediction_times,
                y=prediction_prices,
                mode='lines+markers',
                name=pred_name,
                line=dict(color=pred_color, width=3, dash='dash'),
                marker=dict(size=10, symbol='star', color=pred_color),
                opacity=0.9,
                hovertemplate=f'<b>Predicted Price</b><br>$%{{y:,.2f}}<br>%{{x}}{hover_extra}<extra></extra>'
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
                fillcolor=f'rgba({"16, 185, 129" if pred_color == "#10b981" else "239, 68, 68" if pred_color == "#ef4444" else "245, 158, 11" if pred_color == "#f59e0b" else "107, 114, 128"}, 0.1)',
                showlegend=False,
                hoverinfo='skip'
            ))
        else:
            # SIMPLE OVERLAY - Just show marker at current price point
            last_time = df.index[-1]
            last_price = float(df['close'].iloc[-1])
            
            # Add a single marker showing the prediction
            fig.add_trace(go.Scatter(
                x=[last_time],
                y=[last_price],
                mode='markers',
                name=pred_name,
                marker=dict(
                    size=20,
                    symbol=pred_symbol,
                    color=pred_color,
                    line=dict(width=2, color='white')
                ),
                opacity=0.9,
                hovertemplate=f'<b>AI Prediction</b><br>${{y:,.2f}}<br>{{x}}{hover_extra}<extra></extra>'
            ))
            
            # Add annotation
            fig.add_annotation(
                x=last_time,
                y=last_price,
                text=f"{pred_name.split(':')[1].strip()}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=pred_color,
                ax=50,
                ay=-40,
                bgcolor=pred_color,
                font=dict(color='white', size=12),
                bordercolor='white',
                borderwidth=2,
                borderpad=4,
                opacity=0.9
            )
    
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
⚠️ **PROJECT IN DEVELOPMENT** - This AI system uses advanced meta-learning techniques and is continuously improving. 
**Take all forecasts with a grain of salt** - use predictions as one of many factors in your analysis, not as definitive 
trading signals. Always conduct your own research and never invest more than you can afford to lose.
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

    # Wake API helper (for cold starts on free tier)
    with st.expander("🚀 Wake / Restart API Helper", expanded=False):
        st.caption("Free-tier hosting can spin down when idle. Use this to 'warm' the API.")
        col_w1, col_w2 = st.columns([1,1])
        with col_w1:
            wake_clicked = st.button("🔄 Wake API", use_container_width=True)
        with col_w2:
            if st.button("🧹 Clear Log", use_container_width=True):
                st.session_state.api_wake_log = []
        if wake_clicked:
            with st.spinner("Pinging service to wake it up..."):
                wake_result = wake_api()
                status = wake_result.get('status')
                if status == 'awake':
                    st.success("API is awake and responding ✅")
                elif status == 'cooldown':
                    st.info(wake_result.get('message'))
                else:
                    st.warning("Wake attempts finished without success. The service may still be starting.")
        if st.session_state.api_wake_log:
            st.code("\n".join(st.session_state.api_wake_log), language="text")
        st.caption("Tip: First response after a cold start can take 20-60s. Multiple progressive pings help.")
    
    st.markdown("---")
    
    # API Key & Usage Section
    st.markdown("### 🔑 API Access")
    
    # Show current status
    if st.session_state.api_key:
        st.success("✅ API Key Active")
        # Get and display usage info
        usage = get_usage_info()
        if usage:
            user_type = usage.get('user_type', 'authenticated')
            
            if user_type == 'admin':
                # Admin user - unlimited access
                name = usage.get('name', 'Admin')
                st.success(f"🌟 **{name}**")
                st.info("**Unlimited Access** - No rate limits")
            elif user_type == 'authenticated':
                # Regular authenticated user with rate limits
                name = usage.get('name', 'User')
                rate_limit = usage.get('rate_limit', 'N/A')
                calls_remaining = usage.get('calls_remaining', 0)
                
                st.info(f"👤 **{name}**")
                st.caption(f"Limit: {rate_limit}")
                st.metric("Calls Available", f"{calls_remaining} calls/min")
            else:
                # Other special access
                st.info("🌟 **Premium Access**")
        
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
            **Hosting isn't free!** You've used all 3 free predictions.
            
            **Don't have an API key?**  
            📧 Email **kevinroymaglaqui29@gmail.com** with:
            - Your name
            - Your email
            - Use case (optional)
            
            I'll send you an API key for continued access!
            
            **Already have a key?** Enter it below 👇
            """)
        
        # API Key input
        with st.expander("🔐 Enter API Key" if guest_used < guest_limit else "🔐 Enter API Key (Required)", expanded=guest_used >= guest_limit):
            api_key_input = st.text_input(
                "API Key",
                type="password",
                placeholder="btc_xxxxxxxxxxxxx",
                help="Request your API key by emailing kevinroymaglaqui29@gmail.com"
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
                if st.button("� Request Key", use_container_width=True):
                    st.info("""
                    **Email:** kevinroymaglaqui29@gmail.com
                    
                    **Subject:** API Key Request - Bitcoin AI
                    
                    **Include:** Your name and email
                    """)
    
    st.markdown("---")
    
    # About
    st.markdown("### About the Model")
    st.info("🚧 **Status:** In Active Development")
    st.markdown("""
    This AI system predicts **significant price movements** (>0.2%) 
    using a **meta-learning stacked ensemble**:
    
    **Base Models:**
    • **CatBoost** (50% weight)
    • **Random Forest** (25% weight)  
    • **Logistic Regression** (25% weight)
    
    **Meta-Learner**: Combines base predictions for optimal accuracy
    
    **Technical Features**: 20 optimized indicators analyzed
    
    **Data Source**: Real-time Binance API
    
    ⚠️ **Note**: Models are continuously updated. 
    Always verify predictions against multiple sources.
    """)
    
    st.markdown("---")
    st.markdown("**Built by Kevin Roy Maglaqui**")

# Main content - NEW CLEAN LAYOUT
main_col, sidebar_col = st.columns([3, 1])

with main_col:
    # PREDICTION SECTION - FIRST THING USERS SEE
    st.markdown("## 🎯 Generate AI Prediction")
    
    # Check API status
    health = check_api_health()
    
    if health is None:
        st.error("**API Service Unavailable**")
    elif "error" in health:
        st.error(f"**API Error:** {health['error']}")
    elif not health.get('model_loaded', False):
        st.warning("**Models Not Loaded** - Please wait...")
    else:
        # Model age check - simplified
        age_warning = get_model_age_warning()
        if age_warning and ("contact" in age_warning.lower() or "Consider updating" in age_warning):
            st.info(f"ℹ️ {age_warning}")
        
        # Check if user can make predictions
        can_predict = True
        guest_message = ""
        
        if not st.session_state.api_key and st.session_state.guest_usage_count >= 3:
            can_predict = False
            guest_message = "🚫 Free trial exhausted (3/3 used)"
        elif not st.session_state.api_key:
            guest_message = f"👤 Guest: {st.session_state.guest_usage_count}/3 free"
        
        # Layout for button and message
        btn_col1, btn_col2 = st.columns([1, 2])
        
        with btn_col1:
            predict_btn = st.button(
                "🔮 Predict", 
                use_container_width=True, 
                type="primary",
                disabled=not can_predict
            )
        
        with btn_col2:
            if guest_message:
                if can_predict:
                    st.caption(guest_message)
                else:
                    st.error(guest_message)
                    st.caption("👉 Enter API key in sidebar")
        
        if predict_btn:
            with st.spinner("🤖 Analyzing market data..."):
                result = make_prediction()
                
                if 'error' in result:
                    if result.get('guest_limit') or result.get('auth_error'):
                        st.error(f"🔑 {result['error']}")
                        st.info("📧 Email **kevinroymaglaqui29@gmail.com** for API key")
                    elif result.get('rate_limit'):
                        st.error(f"⏱️ {result['error']}")
                    else:
                        st.error(f"❌ {result['error']}")
                else:
                    # Store prediction
                    st.session_state.predictions_history.append(result)
                    st.session_state.latest_prediction = result
                    
                    st.markdown("---")
                    
                    # Check if v1.1 enriched
                    has_enriched = 'suggestion' in result and 'trend' in result
                    
                    if has_enriched:
                        suggestion = result.get('suggestion', {})
                        trend = result.get('trend', {})
                        tags = result.get('tags', [])
                        
                        # Determine color
                        action = suggestion.get('action', 'HOLD')
                        if action == 'BUY':
                            card_gradient = "linear-gradient(135deg, #10b981 0%, #059669 100%)"
                            indicator = "🟢"
                        elif action == 'SELL':
                            card_gradient = "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)"
                            indicator = "🔴"
                        else:
                            card_gradient = "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
                            indicator = "🟡"
                        
                        # Clean prediction card
                        st.markdown(f"""
                        <div style="background: {card_gradient}; 
                                    padding: 30px; border-radius: 16px; color: white; text-align: center;
                                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);">
                            <h1 style="margin: 0;">{indicator} {action}</h1>
                            <h3 style="margin: 12px 0;">Confidence: {result['confidence']:.1%} | Conviction: {suggestion.get('conviction', 'N/A')}</h3>
                            <p style="font-size: 20px; margin: 8px 0;">Current Price: ${result['current_price']:,.2f}</p>
                            <p style="font-size: 14px; opacity: 0.9; margin: 4px 0;">
                                Trend: {trend.get('short_term', 'N/A')} (short) • {trend.get('long_term', 'N/A')} (long) • {trend.get('strength', 'N/A')}
                            </p>
                            <p style="font-size: 12px; opacity: 0.8;">Risk: {suggestion.get('risk_level', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Tags
                        if tags:
                            st.markdown("<br>", unsafe_allow_html=True)
                            tag_html = " ".join([f'<span style="background: #3b82f6; color: white; padding: 6px 14px; border-radius: 12px; font-size: 12px; margin: 3px; display: inline-block;">{tag}</span>' for tag in tags])
                            st.markdown(f'<div style="text-align: center;">{tag_html}</div>', unsafe_allow_html=True)
                        
                        # Probabilities - compact
                        st.markdown("<br>", unsafe_allow_html=True)
                        prob_col1, prob_col2, prob_col3 = st.columns(3)
                        with prob_col1:
                            st.metric("No Move", f"{result['probabilities'].get('no_movement', 0):.0%}")
                        with prob_col2:
                            st.metric("⬆ Up", f"{result['probabilities'].get('large_up', 0):.0%}")
                        with prob_col3:
                            st.metric("⬇ Down", f"{result['probabilities'].get('large_down', 0):.0%}")
                        
                        # Reasoning - collapsible
                        with st.expander("💡 View AI Reasoning", expanded=False):
                            reasoning = suggestion.get('reasoning', [])
                            if reasoning:
                                for i, reason in enumerate(reasoning, 1):
                                    st.markdown(f"{i}. {reason}")
                            
                            # Score breakdown
                            st.markdown("---")
                            st.markdown("**Score Breakdown:**")
                            breakdown = suggestion.get('score_breakdown', {})
                            col_s1, col_s2, col_s3 = st.columns(3)
                            with col_s1:
                                st.metric("Confidence", f"{breakdown.get('confidence_boost', 0):.2f}")
                            with col_s2:
                                st.metric("Trend", f"{breakdown.get('trend_score', 0):.2f}")
                            with col_s3:
                                st.metric("Total", f"{breakdown.get('total_score', 0):.2f}")
                    
                    else:
                        # v1.0 fallback
                        label = result['prediction_label']
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #1f2937 0%, #374151 100%); 
                                    padding: 30px; border-radius: 16px; color: white; text-align: center;
                                    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);">
                            <h1>{label}</h1>
                            <h3>Confidence: {result['confidence']:.1%}</h3>
                            <p style="font-size: 20px;">Price: ${result['current_price']:,.2f}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.success("✅ Prediction generated! Scroll down to see it overlaid on the live chart.")
    
    # CHART SECTION - BELOW PREDICTION
    st.markdown("---")
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
        st.info("💡 **The AI prediction feature below still works!**")
    
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
                prediction_to_show = None
                if st.session_state.latest_prediction:
                    # Check if we have full overlay data (next_periods) or just simple marker
                    has_full_overlay = 'next_periods' in st.session_state.latest_prediction
                    overlay_type = "with projection line" if has_full_overlay else "with prediction marker"
                    checkbox_label = f"Show AI Prediction Overlay ({overlay_type})"
                    
                    show_prediction = st.checkbox(checkbox_label, 
                                                  value=True,  # Always default True
                                                  help="Display the latest AI prediction on the chart",
                                                  key="prediction_overlay_toggle")
                    if show_prediction:
                        prediction_to_show = st.session_state.latest_prediction
                
                # Create chart with or without prediction overlay
                chart = create_price_chart(chart_data, show_indicators=True, 
                                          data_source=chart_source, 
                                          prediction_result=prediction_to_show)
                st.plotly_chart(chart, use_container_width=True)
            else:
                st.error(f"⚠️ **Unable to load chart data**")
                st.caption(f"Error: {status[:200]}")
                st.info("💡 The AI prediction feature above still works!")
    else:
        st.info("💡 **Chart temporarily unavailable** - Use the AI Prediction feature below to get forecasts!")

with sidebar_col:
    # COMPACT METADATA BOX - Right side
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); 
                padding: 20px; border-radius: 12px; color: white;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); margin-bottom: 20px;">
        <h4 style="margin: 0 0 12px 0;">📊 Model Metadata</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Refresh button
    if st.button("🔄 Refresh Model Info", key="refresh_model_info"):
        get_model_info.clear()
        st.rerun()
    
    # Get model info
    info = get_model_info()
    
    # DEBUG: Show what we're getting
    with st.expander("🔍 Debug: Raw API Response", expanded=False):
        st.json(info)
    
    if 'error' not in info:
        # Extract metrics
        metadata = info.get('metadata', {})
        performance = info.get('performance', metadata.get('performance', {}))
        
        # Model Architecture
        has_meta_learner = info.get('has_meta_learner', metadata.get('has_meta_learner', False))
        use_stacking = info.get('use_stacking', metadata.get('use_stacking', False))
        
        # DEBUG
        st.caption(f"🐛 has_meta_learner: {has_meta_learner}, use_stacking: {use_stacking}")
        
        if has_meta_learner or use_stacking:
            st.markdown("**🧠 Stacked Ensemble + Meta-Learner**")
            st.caption("_Base models → Meta-learner → Final prediction_")
            st.markdown("---")
        
        # Ensemble Weights - check both top level and metadata
        ensemble_weights = info.get('ensemble_weights', metadata.get('ensemble_weights', {}))
        
        # DEBUG
        st.caption(f"🐛 ensemble_weights: {ensemble_weights}")
        
        st.markdown("**Base Model Weights:**")
        
        if ensemble_weights:
            catboost_weight = ensemble_weights.get('catboost', 0.5) * 100
            rf_weight = ensemble_weights.get('rf', 0.25) * 100
            logistic_weight = ensemble_weights.get('logistic', 0.25) * 100
            
            st.caption(f"• CatBoost: {catboost_weight:.0f}%")
            st.caption(f"• Random Forest: {rf_weight:.0f}%")
            st.caption(f"• Logistic Regression: {logistic_weight:.0f}%")
        else:
            # Fallback to defaults
            st.caption("• CatBoost: 50%")
            st.caption("• Random Forest: 25%")
            st.caption("• Logistic Regression: 25%")
        
        st.markdown("---")
        
        # Training Metrics
        st.markdown("**Training Metrics:**")
        test_accuracy = performance.get('test_accuracy', metadata.get('performance', {}).get('test', {}).get('accuracy', None))
        if test_accuracy:
            st.caption(f"Accuracy: {test_accuracy:.1%}")
        
        # Extract precision and recall
        nested_perf = metadata.get('performance', {}).get('test', {})
        if nested_perf:
            precision = nested_perf.get('precision_macro')
            recall = nested_perf.get('recall_macro')
            
            if precision:
                st.caption(f"Precision: {precision:.1%}")
            if recall:
                st.caption(f"Recall: {recall:.1%}")
        
        st.markdown("---")
        
        # Testing Performance
        st.markdown("**Testing Accuracy:**")
        test_f1 = performance.get('test_f1', metadata.get('performance', {}).get('test', {}).get('f1_macro', None))
        if test_f1:
            st.caption(f"F1 Score: {test_f1:.3f}")
        
        test_roc = performance.get('test_roc_auc', metadata.get('performance', {}).get('test', {}).get('roc_auc_ovr', None))
        if test_roc:
            st.caption(f"ROC AUC: {test_roc:.3f}")
        
        st.markdown("---")
        st.caption(f"🔢 Features: {info.get('feature_count', info.get('n_features', 20))}")
        
        # Training date
        training_date = info.get('training_date', metadata.get('training_date', None))
        if training_date:
            st.caption(f"📅 {training_date[:10]}")
    else:
        st.error("Model info unavailable")
    
    st.markdown("---")
    
    # Technical Indicators List
    st.markdown("**Technical Indicators:**")
    indicators = [
        "SMA (7, 14, 21, 50)",
        "EMA (12, 26)",
        "RSI (14)",
        "MACD",
        "Bollinger Bands",
        "ATR",
        "ADX",
        "Volume Ratio",
        "ROC",
        "+ Price derivatives"
    ]
    for indicator in indicators:
        st.caption(f"• {indicator}")
    
    st.markdown("---")
    
    # User Warning Box
    st.markdown("""
    <div style="background: #fef3c7; border: 2px solid #f59e0b; 
                padding: 16px; border-radius: 8px; margin-bottom: 16px;">
        <strong style="color: #92400e;">⚠️ Development Notice</strong>
        <p style="color: #78350f; font-size: 12px; margin: 8px 0 0 0;">
            This is a demo. Models may occasionally malfunction. 
            Take predictions with caution - not financial advice!
        </p>
    </div>
    """, unsafe_allow_html=True)

# Demo message and API integration info at the bottom
st.markdown("---")
demo_col1, demo_col2 = st.columns(2)

with demo_col1:
    st.markdown("""
    <div style="background: #1f2937; color: white; padding: 20px; border-radius: 12px; height: 100%;">
        <h4>🎯 About This Demo</h4>
        <p style="font-size: 14px; margin: 8px 0;">
            Demo of my Bitcoin AI forecasting API built with ensemble machine learning.
        </p>
        <p style="font-size: 14px; margin: 8px 0;">
            <strong>Want to integrate this into your systems?</strong>
        </p>
        <p style="font-size: 13px; color: #9ca3af;">
            📧 <strong>kevinroymaglaqui29@gmail.com</strong><br>
            🌐 API: <code>btc-forecast-api.onrender.com</code>
        </p>
    </div>
    """, unsafe_allow_html=True)

with demo_col2:
    st.markdown("""
    <div style="background: #fef3c7; border: 2px solid #f59e0b; padding: 20px; border-radius: 12px; height: 100%;">
        <h4 style="color: #92400e;">⚠️ Important Disclaimer</h4>
        <p style="font-size: 13px; color: #78350f; margin: 8px 0;">
            <strong>Development status:</strong> Models may malfunction.<br>
            <strong>Not financial advice:</strong> Use predictions as ONE data point.<br>
            <strong>Trade responsibly:</strong> Only invest what you can afford to lose.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("Built by Kevin Roy Maglaqui | Bitcoin AI Price Predictor v1.1")
