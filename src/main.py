import concurrent.futures
import logging
import os

# Configure logging
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/main.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from scraper import TwitterScraper
from processor import clean_data, save_to_parquet
from analyzer import calculate_sentiment, generate_tfidf_vectors, aggregate_signals, visualize_signals

def process_hashtag(tag, limit=50):
    """Worker function to scrape a single hashtag."""
    scraper = TwitterScraper()
    try:
        if not scraper.start_driver(headless=True):
            return []
            
        if not scraper.login():
            logger.error(f"Login failed for hashtag process {tag}")
            return []
            
        raw_data = scraper.scrape_hashtag(tag, limit=limit)
        return raw_data
    except Exception as e:
        logger.error(f"Error processing {tag}: {e}")
        return []
    finally:
        scraper.close_driver()

def main():
    hashtags = ["#nifty50", "#sensex", "#intraday", "#banknifty"]
    
    # Check credentials before starting
    from scraper import TwitterScraper as TS
    test = TS()
    if not test.auth_token and (not test.username or not test.password):
        logger.error("="*50)
        logger.error("MISSING CREDENTIALS: Set TWITTER_AUTH_TOKEN OR (TWITTER_USER and TWITTER_PASS) in .env")
        logger.error("="*50)
        return

    all_raw_data = []
    logger.info(f"Starting concurrent scraping for: {hashtags}")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_tag = {executor.submit(process_hashtag, tag, 20): tag for tag in hashtags}
        for future in concurrent.futures.as_completed(future_to_tag):
            tag = future_to_tag[future]
            try:
                data = future.result()
                all_raw_data.extend(data)
                logger.info(f"Finished {tag}: gathered {len(data)} tweets.")
            except Exception as e:
                logger.error(f"Tag {tag} error: {e}")

    if all_raw_data:
        logger.info("--- Pipeline: Processing & Analysis ---")
        df = clean_data(all_raw_data)
        df = calculate_sentiment(df)
        summary_df = aggregate_signals(df)
        visualize_signals(df)
        df, _ = generate_tfidf_vectors(df)
        save_to_parquet(df, "market_intelligence.parquet")
        
        logger.info(f"Successfully processed {len(df)} total unique tweets.")
    else:
        logger.error("No data collected. Verify login status and internet.")

if __name__ == "__main__":
    main()
