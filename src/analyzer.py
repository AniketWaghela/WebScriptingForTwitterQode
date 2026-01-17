import pandas as pd
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer

def calculate_sentiment(df):
    """
    Calculates sentiment polarity for each tweet using TextBlob.
    Polarity range: -1 (negative) to 1 (positive).
    """
    if df.empty or "content" not in df.columns:
        return df

    df["polarity"] = df["content"].apply(lambda text: TextBlob(str(text)).sentiment.polarity)
    return df

def generate_tfidf_vectors(df, max_features=1000):
    """
    Generates TF-IDF vectors for the tweet content.
    """
    if df.empty or "content" not in df.columns or len(df) < 2:
        return df, None

    vectorizer = TfidfVectorizer(max_features=max_features, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(df["content"])
    
    return df, vectorizer

def aggregate_signals(df):
    """
    Aggregates sentiment and engagement into a composite score per tag.
    """
    if df.empty:
        return df

    # Simple composite signal formula: sentiment * (1 + log(engagement + 1))
    import numpy as np
    df["engagement_weight"] = 1 + np.log1p(df["replies"] + df["retweets"] + df["likes"])
    df["composite_signal"] = df["polarity"] * df["engagement_weight"]
    
    summary = df.groupby("tag").agg({
        "polarity": ["mean", "std"],
        "composite_signal": "mean",
        "content": "count"
    }).reset_index()
    
    print("\nSignal Aggregation Summary:")
    print(summary)
    return summary

def visualize_signals(df):
    """
    Creates a simple sentiment distribution plot saved to disk.
    """
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    if df.empty:
        return

    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x="polarity", hue="tag", kde=True, bins=20)
    plt.title("Market Sentiment Distribution by Hashtag")
    plt.xlabel("Polarity (-1 to 1)")
    plt.ylabel("Tweet Count")
    
    output_path = "logs/sentiment_distribution.png"
    plt.savefig(output_path)
    print(f"Visualization saved to {output_path}")

if __name__ == "__main__":
    # Test data
    data = {
        "content": [
            "Nifty is reaching all time high! Very bullish.",
            "Sensex is falling, market crash alert.",
            "Trading is fun but risky."
        ]
    }
    df = pd.DataFrame(data)
    df = calculate_sentiment(df)
    print("Sentiment Analysis:")
    print(df)
    
    df, v = generate_tfidf_vectors(df)
    print("\nTF-IDF vectors generated.")
