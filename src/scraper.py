import logging
import random
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv, find_dotenv

# Configure logging
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TwitterScraper:
    def __init__(self):
        self.driver = None
        env_file = find_dotenv()
        if env_file:
            load_dotenv(env_file)
            logger.info(f"Loaded environment from {env_file}")
        else:
            load_dotenv() 
            
        self.username = os.getenv("TWITTER_USER")
        self.password = os.getenv("TWITTER_PASS")
        self.auth_token = os.getenv("TWITTER_AUTH_TOKEN")

    def start_driver(self, headless=False):
        """Initializes the Chrome WebDriver."""
        paths_to_add = [r"C:\Windows\System32\WindowsPowerShell\v1.0", r"C:\Windows\System32"]
        for p in paths_to_add:
            if os.path.exists(p) and p not in os.environ["PATH"]:
                os.environ["PATH"] += os.pathsep + p
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            self.driver.implicitly_wait(5)
            logger.info("WebDriver initialized.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            return False

    def login(self):
        """Logs into Twitter using session token or username/password."""
        if self.auth_token:
            logger.info("Using session-based authentication (auth_token).")
            return self._login_with_token()
        
        if not self.username or not self.password:
            logger.error("Credentials missing in .env (and no auth_token found)")
            return False

        return self._login_with_ui()

    def _login_with_token(self):
        """Bypasses UI login by injecting auth_token cookie."""
        try:
            # Must visit the domain first to set cookies
            self.driver.get("https://twitter.com")
            time.sleep(2)
            
            # Add the auth_token cookie
            cookie = {
                'name': 'auth_token',
                'value': self.auth_token,
                'domain': '.twitter.com',
                'path': '/',
                'secure': True
            }
            self.driver.add_cookie(cookie)
            logger.info("Auth token cookie injected.")
            
            # Refresh to apply the cookie
            self.driver.refresh()
            time.sleep(5)
            
            if "login" in self.driver.current_url.lower():
                logger.warning("Session token appears invalid (redirected back to login).")
                if self.username and self.password:
                    logger.info("Attempting UI-based fallback.")
                    return self._login_with_ui()
                return False
            
            logger.info("Session-based login successful.")
            return True
        except Exception as e:
            logger.error(f"Token injection failed: {e}")
            return False

    def _login_with_ui(self):
        """Standard UI-based login flow."""
        logger.info("Logging into Twitter via UI...")
        self.driver.get("https://twitter.com/i/flow/login")
        wait = WebDriverWait(self.driver, 25)

        try:
            # Step 1: Username
            u_field = wait.until(EC.presence_of_element_located((By.NAME, "text")))
            u_field.send_keys(self.username)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))).click()
            
            # Step 2: Verification Screen OR Password Screen
            time.sleep(3)
            text_fields = self.driver.find_elements(By.NAME, "text")
            if text_fields and text_fields[0].is_displayed():
                logger.info("Secondary verification detected. Using username/email as response.")
                text_fields[0].send_keys(self.username)
                wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))).click()
                time.sleep(2)

            # Step 3: Password
            p_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
            p_field.send_keys(self.password)
            wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']"))).click()
            
            time.sleep(8)
            if "login" in self.driver.current_url.lower():
                logger.error("UI-based login failed. Check credentials or account status.")
                return False
            
            logger.info("UI-based login successful.")
            return True
        except Exception as e:
            logger.error(f"UI-based login failed: {e}")
            return False

    def scrape_hashtag(self, tag, limit=50):
        """Scrapes hashtags with resiliency."""
        cleaned_tag = tag.replace("#", "%23")
        url = f"https://twitter.com/search?q={cleaned_tag}&src=typed_query&f=live"
        logger.info(f"Scraping {tag}...")
        self.driver.get(url)
        time.sleep(5)

        tweets_data = []
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while len(tweets_data) < limit:
            articles = self.driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
            for article in articles:
                if len(tweets_data) >= limit: break
                try:
                    text_els = article.find_elements(By.XPATH, ".//div[@data-testid='tweetText']")
                    if not text_els: continue
                    text = text_els[0].text
                    
                    user = article.find_element(By.XPATH, ".//div[@data-testid='User-Name']").text.split("\n")[0]
                    timestamp = article.find_element(By.XPATH, ".//time").get_attribute("datetime")
                    
                    tweet_info = {
                        "user": user, "timestamp": timestamp, "content": text, "tag": tag,
                        "replies": 0, "retweets": 0, "likes": 0, "mentions": "", "hashtags": ""
                    }
                    if not any(t["content"] == text for t in tweets_data):
                        tweets_data.append(tweet_info)
                        logger.info(f"[{tag}] Scraped {len(tweets_data)}/{limit}")
                except: continue

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3, 5))
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height: break
            last_height = new_height

        return tweets_data

    def close_driver(self):
        if self.driver: self.driver.quit()
