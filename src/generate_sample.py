import pandas as pd
import os
from datetime import datetime, timedelta
import random

def generate_mock_data():
    """
    Generates realistic market-related tweet data for demonstration.
    """
    hashtags = ["#nifty50", "#sensex", "#intraday", "#banknifty", "#stockmarketindia"]
    users = ["MarketManiac", "TraderJoe", "EquityExpert", "NiftyNinja", "SensexSage", "OptionOrbit"]
    
    bullish_phrases = [
        "Nifty looks extremely strong today! Bull run ahead.",
        "Sensex touching new highs. Great time to be an investor.",
        "Strong breakout in BankNifty. Bullish momentum is real.",
        "Market sentiment is very positive after the recent news.",
        "Accumulating Nifty at these levels. Bullish!",
        "Intraday long positions paying off well. Market is on fire."
    ]
    
    bearish_phrases = [
        "Sensex showing signs of weakness. Reversal imminent?",
        "Avoid long positions today, market looks bearish.",
        "Huge sell-off in BankNifty. Stay cautious.",
        "Global cues are negative, expect a gap down opening.",
        "Profit booking at higher levels. Bearish trend started.",
        "Market is overbought, waiting for a correction."
    ]
    
    neutral_phrases = [
        "Market moving sideways today. No clear trend.",
        "Watching #nifty50 closely for direction.",
        "Consolidation continue in the market. Wait and watch.",
        "Standard morning update: indices opening flat.",
        "Trading within a range. Intraday players be careful."
    ]
    
    data = []
    base_time = datetime.utcnow()
    
    for _ in range(250): # Generate 250 sample tweets
        tag = random.choice(hashtags)
        user = random.choice(users)
        sentiment_type = random.choice(["bullish", "bearish", "neutral"])
        
        if sentiment_type == "bullish":
            content = random.choice(bullish_phrases)
        elif sentiment_type == "bearish":
            content = random.choice(bearish_phrases)
        else:
            content = random.choice(neutral_phrases)
            
        # Add a random date within last 24h
        time = base_time - timedelta(minutes=random.randint(0, 1440))
        
        data.append({
            "user": user,
            "timestamp": time.isoformat() + "Z",
            "content": content,
            "tag": tag,
            "replies": random.randint(0, 50),
            "retweets": random.randint(0, 100),
            "likes": random.randint(0, 500)
        })
        
    return data

if __name__ == "__main__":
    from processor import clean_data, save_to_parquet
    from analyzer import calculate_sentiment, aggregate_signals, visualize_signals, generate_tfidf_vectors
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SampleGenerator")

    logger.info("Generating mock data for showcase...")
    raw_data = generate_mock_data()
    
    logger.info("Processing data...")
    df = clean_data(raw_data)
    
    logger.info("Analyzing sentiment...")
    df = calculate_sentiment(df)
    
    logger.info("Aggregating signals...")
    summary_df = aggregate_signals(df)
    
    logger.info("Visualizing signals...")
    visualize_signals(df)
    
    logger.info("Saving to Parquet...")
    save_to_parquet(df, "sample_market_data.parquet")
    
    logger.info("Success! Sample data saved to data/sample_market_data.parquet")
    logger.info("Visualization saved to logs/sentiment_distribution.png")
    print("\nSample Data Head:")
    print(df.head())
