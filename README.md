# Market Intelligence Scraper

A robust, concurrent Twitter scraper and sentiment analyzer for market intelligence.

## 🚀 Final Project Showcase

This project now supports **Session-based Authentication**, which is much more robust than traditional automated login.

### 🛠️ Configuration (Required)

1.  **Get your Session Token**:
    - Open [twitter.com](https://twitter.com) in your browser and log in.
    - Press `F12` to open Developer Tools, then click the **Console** tab.
    - Paste the content of `scripts/get_auth_token.js` into the console and press Enter.
    - Copy the generated `auth_token`.
2.  **Update `.env`**:
    - Open the `.env` file.
    - Paste your token like this: `TWITTER_AUTH_TOKEN=your_token_here`.
    - *(Alternatively, you can provide `TWITTER_USER` and `TWITTER_PASS`, but the token is more reliable).*

### 🏃 How to Run
```powershell
python src/main.py
```

### 📁 Output
- **Logs**: `logs/main.log` (Scraping progress)
- **Data**: `data/market_intelligence.parquet` (Consolidated dataset)
- **Viz**: `logs/sentiment_distribution.png` (Analysis results)

---

### 🔍 Features
- **Concurrent Scraping**: Processes multiple hashtags in parallel.
- **Resilient Pipeline**: Handles dynamic Twitter UI changes and verification prompts.
- **Sentiment Analysis**: Uses TextBlob to gauge market mood.
- **Smart Indexing**: Generates TF-IDF vectors for deep signal analysis.
- **Data Deduplication**: Ensures clean, high-quality data storage.
