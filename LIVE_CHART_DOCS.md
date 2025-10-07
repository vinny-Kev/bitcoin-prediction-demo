# Live Chart Feature - Documentation

## Overview
The app now displays a **live Bitcoin price chart on startup** with real-time data from Binance API, eliminating the need to wait for predictions to see market data.

## New Features Added

### 1. **Data Fetcher Module** (`data_fetcher.py`)

A comprehensive module for fetching Bitcoin market data:

#### Features:
- ✅ **Historical candlestick data** (OHLCV)
- ✅ **Current price & 24h statistics**
- ✅ **Technical indicators** (SMA, EMA, MACD, RSI, Bollinger Bands)
- ✅ **Multi-timeframe support** (1m, 5m, 15m, 1h, 4h, 1d)
- ✅ **Rate limit handling**
- ✅ **Error handling with clear messages**

#### Key Functions:
```python
# Fetch historical data
df = get_bitcoin_data(interval="5m", limit=200, with_indicators=True)

# Get current price
price_data = get_current_bitcoin_price()
```

### 2. **Live Chart on Startup**

The main page now shows:

#### **Current Price Metrics** (4 columns)
- Current Price with 24h change percentage
- 24h High price
- 24h Low price  
- 24h Trading volume

#### **Interactive Candlestick Chart**
- **Timeframe selector**: Choose between 1m, 5m, 15m, 1h, 4h
- **Candlestick visualization**: Green (up) / Red (down)
- **Technical indicators**:
  - SMA 20 (blue line)
  - SMA 50 (orange line)
  - Bollinger Bands (purple dashed lines with shaded area)
- **Real-time updates**: Data cached for 5 minutes
- **Hover details**: Unified hover mode showing all values

### 3. **Professional Styling**

- Modern candlestick colors (green/red)
- Clean white background
- Responsive design
- Professional chart layout
- No slider (cleaner look)

## Data Source

**Binance Public API**
- Endpoint: `https://api.binance.com/api/v3`
- Rate limits respected with automatic delays
- Reliable and fast

## Technical Indicators Included

1. **Simple Moving Averages (SMA)**
   - SMA 20: Short-term trend
   - SMA 50: Medium-term trend
   - SMA 200: Long-term trend (available with more data)

2. **Exponential Moving Averages (EMA)**
   - EMA 12: Fast moving average
   - EMA 26: Slow moving average

3. **MACD (Moving Average Convergence Divergence)**
   - MACD line
   - Signal line

4. **RSI (Relative Strength Index)**
   - 14-period RSI
   - Overbought/oversold indicator

5. **Bollinger Bands**
   - Upper band (mean + 2 std dev)
   - Middle band (20-period SMA)
   - Lower band (mean - 2 std dev)

6. **Volume Analysis**
   - Trading volume
   - 20-period volume SMA

## Caching Strategy

- **Chart data**: Cached for 5 minutes (`ttl=300`)
- **Model info**: Cached for 1 hour (`ttl=3600`)
- Reduces API calls and improves performance
- Fresh data on timeframe changes

## User Experience Improvements

### Before:
❌ Empty screen on startup
❌ Must click predict to see any data
❌ No market context

### After:
✅ **Instant visual feedback** - Chart loads immediately
✅ **Market context** - See current price and trends
✅ **Interactive exploration** - Change timeframes
✅ **Professional appearance** - Looks like a real trading app
✅ **Educational value** - Technical indicators visible

## Error Handling

The module handles:
- Connection errors
- Timeout errors  
- Invalid responses
- Missing data
- Rate limit errors

All errors show user-friendly messages.

## Performance

- **Initial load**: ~2-3 seconds
- **Timeframe change**: ~1-2 seconds
- **Cached reload**: Instant
- **Chart rendering**: Smooth with Plotly

## Future Enhancements (Optional)

Possible additions:
1. **Real-time streaming** - WebSocket for live updates
2. **More indicators** - Fibonacci, Ichimoku, etc.
3. **Drawing tools** - Support/resistance lines
4. **Volume chart** - Separate volume subplot
5. **Comparison view** - Multiple cryptocurrencies
6. **Export data** - Download CSV of historical data

## Integration with Predictions

The chart provides context for predictions:
- Users see current trend before predicting
- Can compare prediction with actual chart patterns
- Better understanding of model decisions
- More confidence in the system

## Files Modified

1. **data_fetcher.py** (NEW)
   - Complete data fetching module
   - 250+ lines of well-documented code

2. **app.py**
   - Added import for data_fetcher
   - Added chart creation functions
   - Integrated live chart in main content
   - Added timeframe selector

3. **requirements.txt** (No changes needed)
   - All required packages already present

## Testing Checklist

- [x] Chart loads on app startup
- [x] Current price displays correctly
- [x] Timeframe selector works
- [x] Technical indicators visible
- [x] Candlesticks render properly
- [x] Hover interactions work
- [x] Error handling works
- [x] Mobile responsive
- [x] Performance acceptable

## Contact

- Developer: Kevin Roy Maglaqui
- Email: kevinroymaglaqui29@gmail.com
- Repo: https://github.com/vinny-Kev/bitcoin-prediction-demo
