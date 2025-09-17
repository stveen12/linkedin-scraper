import os
import time
import pickle
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ---------------- CONFIG ----------------
COOKIES_FILE = "linkedin_cookies.pkl"
DOWNLOAD_DIR = str(Path(__file__).with_name("downloads").resolve())
MAX_PROFILES = 100  # How many profiles to collect (scroll manually)
WAIT_SEC = 15
# ----------------------------------------

# Prepare download folder
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Chrome options
options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
}
options.add_experimental_option("prefs", prefs)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, WAIT_SEC)
driver.maximize_window()

# --- Open & restore cookies ---
driver.get("https://www.linkedin.com")
time.sleep(2)

if os.path.exists(COOKIES_FILE):
    with open(COOKIES_FILE, "rb") as f:
        for c in pickle.load(f):
            # Selenium requires non-None domain for add_cookie in some versions
            if "domain" in c and c["domain"]:
                driver.add_cookie(c)
            else:
                # Fallback: add current domain
                c["domain"] = ".linkedin.com"
                driver.add_cookie(c)
    driver.refresh()
    time.sleep(2)
else:
    input("No cookies yet. Log in in the opened window, then press Enter here to save cookies...")
    with open(COOKIES_FILE, "wb") as f:
        pickle.dump(driver.get_cookies(), f)
    print("Cookies saved.")

# --- GO TO MY NETWORK ---
driver.get("https://www.linkedin.com/mynetwork/")
time.sleep(5)

# Click "Show all suggestions..." button
try:
    show_all_btn = WebDriverWait(driver, WAIT_SEC).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Show all suggestions for People you may know based on your recent activity']"))
    )
    driver.execute_script("arguments[0].click();", show_all_btn)
    print("Opened 'People you may know' list...")
    time.sleep(3)
except:
    print("⚠️ Could not find 'Show all suggestions...' button. Continuing with default suggestions...")


# Scroll to load more profiles, enter after done
input(f"Scroll to load more profiles (up to {MAX_PROFILES}), then press Enter here...")


# Collect profile links
seen = set()
links = []
for a in driver.find_elements(By.CSS_SELECTOR, "a[href*='linkedin.com/in/']"):
    href = a.get_attribute("href")
    if not href:
        continue
    href = href.split("?")[0]
    if "/in/" in href and href not in seen:
        seen.add(href)
        links.append(href)

print(f"Collected {len(links)} profiles:", links[:15])  # show first few


def click_more_then_save_pdf():
    # There are typically two "More actions" buttons; pick the last visible one
    more_buttons = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//button[@aria-label='More actions']"))
    )
    # Keep only displayed
    more_buttons = [b for b in more_buttons if b.is_displayed()]
    if not more_buttons:
        raise Exception("No visible 'More actions' button found")
    more_btn = more_buttons[-1]

    # Scroll and open
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", more_btn)
    time.sleep(0.3)
    driver.execute_script("arguments[0].click();", more_btn)

    # Wait until dropdown is actually open
    wait.until(lambda d: more_btn.get_attribute("aria-expanded") == "true")

    # Find visible "Save to PDF" item (covers text or aria-label variants)
    def find_visible_pdf():
        # Prefer aria-label
        cands = driver.find_elements(By.XPATH, "//div[@aria-label='Save to PDF']")
        cands += driver.find_elements(By.XPATH, "//*[contains(text(),'Save to PDF')]")
        # Keep only visible ones
        cands = [el for el in cands if el.is_displayed()]
        return cands[0] if cands else None

    pdf_btn = WebDriverWait(driver, WAIT_SEC).until(lambda d: find_visible_pdf())
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", pdf_btn)
    time.sleep(0.2)
    driver.execute_script("arguments[0].click();", pdf_btn)

# --- Visit profiles & save PDFs ---
for i, url in enumerate(links, 1):
    try:
        driver.get(url)
        # Wait for profile header to render
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))

        click_more_then_save_pdf()
        print(f"[{i}/{len(links)}] Saved PDF for: {url}")
        time.sleep(3)  # small buffer for download to start
    except Exception as e:
        print(f"[{i}/{len(links)}] Failed on {url}: {e}")
        # Try once more (menus can be flaky)
        try:
            time.sleep(1.5)
            click_more_then_save_pdf()
            print(f"[{i}/{len(links)}] Saved PDF on retry: {url}")
            time.sleep(3)
        except Exception as e2:
            print(f"[{i}/{len(links)}] Retry failed on {url}: {e2}")

print("Done. PDFs (if any) saved to:", DOWNLOAD_DIR)
driver.quit()
