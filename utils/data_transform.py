import pandas as pd

def transform_yfinance_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms the Yahoo Finance DataFrame to be more user-friendly.
    1. Formats Date from '2026-01-14 08:00:00+00:00' to '2026-01-14 08:00'
    2. Formats Open, High, Low, Close to 2 decimal places
    3. Formats Volume with thousand separators
    """
    if df.empty:
        return df

    # Copy to avoid SettingWithCopyWarning
    df = df.copy()

    # 0. Standardize column names to Title Case
    # This handles cases where yahooquery or files have lowercase headers (date vs Date)
    rename_map = {
        'date': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'symbol': 'Symbol',
        'adj close': 'Adj Close'
    }
    df.rename(columns=rename_map, inplace=True)

    # 1. Format Date
    if 'Date' in df.columns:
        # Convert to datetime objects first to handle various input formats safely
        df['Date'] = pd.to_datetime(df['Date'], utc=True)
        # Format to string 'YYYY-MM-DD HH:MM'
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d %H:%M')

    # 2. Format OHLC to 2 decimal places
    ohlc_cols = ['Open', 'High', 'Low', 'Close']
    for col in ohlc_cols:
        if col in df.columns:
            # Round to 2 decimals
            df[col] = df[col].round(2)

    # 3. Format Volume with thousand separators
    if 'Volume' in df.columns:
        # Ensure it's numeric before formatting
        # If it's cached as string "1,000", handle that
        if df['Volume'].dtype == object:
             # Try to clean it up just in case (remove commas)
             try:
                 df['Volume'] = df['Volume'].astype(str).str.replace(',', '').astype(float)
             except Exception:
                 pass # Leave as is if conversion fails

        # Apply formatting to numerics
        if pd.api.types.is_numeric_dtype(df['Volume']):
            df['Volume'] = df['Volume'].apply(lambda x: "{:,.0f}".format(x) if pd.notnull(x) else "")

    return df
