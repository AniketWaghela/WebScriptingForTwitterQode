import pandas as pd
import os

def clean_data(raw_data_list):
    """
    Converts list of dicts to DataFrame, deduplicates, and normalizes.
    """
    if not raw_data_list:
        return pd.DataFrame()

    df = pd.DataFrame(raw_data_list)

    # 1. Deduplicate based on content
    df = df.drop_duplicates(subset=["content"])

    # 2. Normalize timestamp to UTC datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # 3. Text cleaning: remove newlines and extra spaces
    df["content"] = df["content"].str.replace(r"\s+", " ", regex=True).str.strip()

    # Ensure columns exist
    cols = ["timestamp", "user", "content", "tag", "replies", "retweets", "likes", "mentions", "hashtags"]
    for col in cols:
        if col not in df.columns:
            df[col] = 0 if col in ["replies", "retweets", "likes"] else ""

    return df[cols]

def save_to_parquet(df, filename="market_data.parquet"):
    """
    Saves DataFrame to Parquet format in the data/ folder.
    Appends if file exists (using a simple logic for this task).
    """
    if df.empty:
        print("Empty DataFrame, nothing to save.")
        return

    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    filepath = os.path.join(data_dir, filename)

    if os.path.exists(filepath):
        # Read existing data and append
        existing_df = pd.read_parquet(filepath)
        df = pd.concat([existing_df, df]).drop_duplicates(subset=["content"])

    df.to_parquet(filepath, engine="pyarrow", index=False)
    print(f"Data saved to {filepath}. Total rows: {len(df)}")

if __name__ == "__main__":
    # Test dummy data
    test_data = [
        {"user": "test_user", "timestamp": "2024-01-01T12:00:00Z", "content": "Nifty is going up!!!", "tag": "#nifty50"},
        {"user": "test_user", "timestamp": "2024-01-01T12:00:00Z", "content": "Nifty is going up!!!", "tag": "#nifty50"}, # Duplicate
    ]
    cleaned = clean_data(test_data)
    print("Cleaned Data:")
    print(cleaned)
    save_to_parquet(cleaned, "test.parquet")
