"""
Minimal test version to diagnose Streamlit Cloud startup issue
"""

import streamlit as st

st.set_page_config(
    page_title="Test",
    page_icon="₿",
    layout="wide"
)

st.title("Test App - If you see this, it works!")
st.write("This is a minimal test to verify Streamlit Cloud can start the app.")

try:
    import requests
    st.success("✅ requests imported successfully")
except Exception as e:
    st.error(f"❌ requests import failed: {e}")

try:
    import pandas as pd
    st.success("✅ pandas imported successfully")
except Exception as e:
    st.error(f"❌ pandas import failed: {e}")

try:
    import plotly.graph_objects as go
    st.success("✅ plotly imported successfully")
except Exception as e:
    st.error(f"❌ plotly import failed: {e}")

try:
    from data_fetcher import get_bitcoin_data
    st.success("✅ data_fetcher imported successfully")
except Exception as e:
    st.error(f"❌ data_fetcher import failed: {e}")

st.info("If all checks passed, the issue is in app.py logic, not imports.")
