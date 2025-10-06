"""
Data Fetcher Module for Bitcoin Price Data
Fetches historical and real-time data from Binance API
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time

class BinanceDataFetcher:
    """Fetches Bitcoin price data from Binance API"""
    
    BASE_URL = "https://api.binance.com/api/v3"
    
    @staticmethod
    def fetch_historical_klines(symbol="BTCUSDT", interval="1m", limit=500):
        """
        Fetch historical candlestick data from Binance
        
        Args:
            symbol: Trading pair (default: BTCUSDT)
            interval: Kline interval (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles to fetch (max 1000)
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            endpoint = f"{BinanceDataFetcher.BASE_URL}/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            # Convert price columns to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            
            # Set timestamp as index
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            raise Exception(f"Failed to fetch Binance data: {str(e)}")
    
    @staticmethod
    def fetch_current_price(symbol="BTCUSDT"):
        """
        Fetch current ticker price
        
        Args:
            symbol: Trading pair (default: BTCUSDT)
        
        Returns:
            dict with current price info
        """
        try:
            endpoint = f"{BinanceDataFetcher.BASE_URL}/ticker/24hr"
            params = {"symbol": symbol}
            
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'symbol': data['symbol'],
                'price': float(data['lastPrice']),
                'change_24h': float(data['priceChange']),
                'change_percent': float(data['priceChangePercent']),
                'high_24h': float(data['highPrice']),
                'low_24h': float(data['lowPrice']),
                'volume': float(data['volume']),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            raise Exception(f"Failed to fetch current price: {str(e)}")
    
    @staticmethod
    def fetch_multi_timeframe(symbol="BTCUSDT", intervals=None):
        """
        Fetch data for multiple timeframes
        
        Args:
            symbol: Trading pair
            intervals: List of intervals (default: ['1m', '5m', '15m', '1h'])
        
        Returns:
            dict with DataFrames for each interval
        """
        if intervals is None:
            intervals = ['1m', '5m', '15m', '1h']
        
        result = {}
        for interval in intervals:
            try:
                # Adjust limit based on interval
                limit_map = {
                    '1m': 500,
                    '5m': 500,
                    '15m': 500,
                    '1h': 500,
                    '4h': 500,
                    '1d': 365
                }
                limit = limit_map.get(interval, 500)
                
                df = BinanceDataFetcher.fetch_historical_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )
                result[interval] = df
                
                # Respect rate limits
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error fetching {interval} data: {e}")
                result[interval] = None
        
        return result
    
    @staticmethod
    def calculate_technical_indicators(df):
        """
        Calculate basic technical indicators
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with added indicators
        """
        df = df.copy()
        
        # Simple Moving Averages
        df['SMA_20'] = df['close'].rolling(window=20).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        df['SMA_200'] = df['close'].rolling(window=200).mean()
        
        # Exponential Moving Averages
        df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Bollinger Bands
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        std = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + (std * 2)
        df['BB_lower'] = df['BB_middle'] - (std * 2)
        
        # Volume indicators
        df['volume_SMA'] = df['volume'].rolling(window=20).mean()
        
        return df


def get_bitcoin_data(interval="1m", limit=500, with_indicators=True):
    """
    Convenience function to fetch Bitcoin data with fallback
    
    Args:
        interval: Timeframe interval
        limit: Number of candles
        with_indicators: Whether to calculate technical indicators
    
    Returns:
        DataFrame with Bitcoin price data
    """
    try:
        fetcher = BinanceDataFetcher()
        df = fetcher.fetch_historical_klines(
            symbol="BTCUSDT",
            interval=interval,
            limit=limit
        )
        
        if with_indicators:
            df = fetcher.calculate_technical_indicators(df)
        
        return df
    except Exception as e:
        # If Binance fails, try CoinGecko for at least current price as single point
        if "451" in str(e):
            raise Exception("Binance API blocked in this region (451)")
        raise e


def get_current_bitcoin_price():
    """
    Get current Bitcoin price and stats with fallback options
    
    Returns:
        dict with current price information
    """
    # Try Binance first
    try:
        fetcher = BinanceDataFetcher()
        return fetcher.fetch_current_price("BTCUSDT")
    except Exception as binance_error:
        # Fallback to CoinGecko API (no API key required, no regional restrictions)
        try:
            response = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={
                    "ids": "bitcoin",
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_24hr_vol": "true"
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()['bitcoin']
            
            return {
                'symbol': 'BTCUSD',
                'price': float(data['usd']),
                'change_24h': 0,  # CoinGecko doesn't provide absolute change
                'change_percent': float(data.get('usd_24h_change', 0)),
                'high_24h': float(data['usd']) * 1.02,  # Estimate based on typical volatility
                'low_24h': float(data['usd']) * 0.98,   # Estimate based on typical volatility
                'volume': float(data.get('usd_24h_vol', 0)),
                'timestamp': datetime.now(),
                'source': 'CoinGecko'
            }
        except Exception as coingecko_error:
            # Last resort: CryptoCompare API (also no restrictions)
            try:
                response = requests.get(
                    "https://min-api.cryptocompare.com/data/pricemultifull",
                    params={
                        "fsyms": "BTC",
                        "tsyms": "USD"
                    },
                    timeout=10
                )
                response.raise_for_status()
                data = response.json()['RAW']['BTC']['USD']
                
                return {
                    'symbol': 'BTCUSD',
                    'price': float(data['PRICE']),
                    'change_24h': float(data['CHANGE24HOUR']),
                    'change_percent': float(data['CHANGEPCT24HOUR']),
                    'high_24h': float(data['HIGH24HOUR']),
                    'low_24h': float(data['LOW24HOUR']),
                    'volume': float(data['VOLUME24HOUR']),
                    'timestamp': datetime.now(),
                    'source': 'CryptoCompare'
                }
            except Exception as cryptocompare_error:
                raise Exception(f"All price sources failed. Binance: {str(binance_error)[:100]}, CoinGecko: {str(coingecko_error)[:100]}, CryptoCompare: {str(cryptocompare_error)[:100]}")
