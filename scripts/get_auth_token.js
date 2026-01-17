/* 
  Twitter Auth Token Extractor (WebScript)
  
  Instructions:
  1. Login to Twitter (X) in your browser.
  2. Press F12 to open Developer Tools.
  3. Go to the 'Console' tab.
  4. Paste the code below and press Enter.
  5. Copy the result and paste it into TWITTER_AUTH_TOKEN in your .env file.
*/

(function () {
    const name = "auth_token";
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
        const token = parts.pop().split(';').shift();
        console.log("%c--- TWITTER SESSION TOKEN ---", "color: green; font-weight: bold; font-size: 16px;");
        console.log("%cToken: %c" + token, "color: blue;", "color: black; background: #eee; padding: 2px; border: 1px solid #ccc;");
        console.log("%cCopy the token above and paste it into your .env file as TWITTER_AUTH_TOKEN.", "color: gray; font-style: italic;");
    } else {
        console.error("Auth token not found. Make sure you are logged in to Twitter (x.com).");
    }
})();
