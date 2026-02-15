from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from clients.trading212 import Trading212Client
from clients.yfinance import YFinanceClient
import os
import glob
import pandas as pd
from typing import List

app = FastAPI(title="Trading Data Scraper API")

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development to avoid port issues
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Trading Scraper API is running"}

@app.post("/connect")
def connect_session():
    """
    Simulates a session connection:
    1. Runs T212 Scrape to get Cash and Report
    2. Runs YFinance Scrape to update market data
    3. Returns aggregated data (Balance, Status)
    """
    try:
        # 1. Trading212
        t212_client = Trading212Client(is_demo=False)
        cash_data = t212_client.fetch_account_cash()
        
        # Extract total value if available, else use free cash or just 0
        # cash_data example: {'free': 100, 'total': 1000, ...} 
        # We need to see actual structure, but for now we return the whole object
        
        report_file = t212_client.download_historic_data()
        
        # 2. YFinance
        yf_client = YFinanceClient()
        yf_client.get_tickers()
        
        return {
            "status": "connected",
            "balance": cash_data.get('total') if cash_data else 0, # Adjust based on actual T212 response structure
            "cash_data": cash_data,
            "message": "Connected and synced successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")

@app.post("/disconnect")
def disconnect_session():
    """
    Simulates disconnection.
    """
    return {"status": "disconnected", "message": "Session ended"}

@app.post("/scrape/t212")
def scrape_t212():
    try:
        # Check for API keys first
        import config
        key_id, secret_key = config.get_api_keys("Trading212")
        if not key_id or not secret_key:
             raise ValueError("API Keys missing")

        client = Trading212Client(is_demo=False)
        cash = client.fetch_account_cash()
        report_file = client.download_historic_data()
        
        return {"status": "success", "cash": cash, "report": report_file}
    except ValueError as e:
        # Catch missing keys or other value errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape/yfinance")
def scrape_yfinance():
    try:
        client = YFinanceClient()
        client.get_tickers()
        return {"status": "success", "message": "YFinance scrape completed"}
    except ValueError as e:
        # Catch missing/empty tickers file
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/reports")
def list_reports():
    """List all CSV reports in the root directory."""
    files = glob.glob("History Report *.csv")
    # Sort files by modification time, newest first
    files.sort(key=os.path.getmtime, reverse=True)
    return {"reports": files}

@app.get("/data/market")
def list_market_data():
    """List all market data CSVs."""
    files = glob.glob("market_data/*.csv")
    return {"files": files}

@app.get("/data/content")
def get_file_content(path: str):
    """Read specific CSV file content"""
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        from utils.data_transform import transform_yfinance_data
        df = pd.read_csv(path)
        
        # Apply clean-up for display
        df = transform_yfinance_data(df)
        
        # Convert to object type to allow None values (which map to JSON null)
        # Otherwise, pandas keeps None as NaN in float columns, breaking JSON serialization
        data = df.astype(object).where(pd.notnull(df), None).to_dict(orient="records")
        return {"filename": path, "columns": df.columns.tolist(), "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

@app.post("/shutdown")
def shutdown_server():
    """Shuts down the backend server."""
    import signal
    import threading
    
    def kill():
        # Give potential response time to flush
        import time
        time.sleep(1)
        os.kill(os.getpid(), signal.SIGTERM)
        
    threading.Thread(target=kill).start()
    return {"status": "shutdown", "message": "Backend shutting down..."}
