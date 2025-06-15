import os
import random
import time
import json
import shutil
import threading
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

ACCOUNTS_FILE = "accounts.json"
BASE_VIDEO_FOLDER = "C:/InstagramBot/Videos"
CONFIG_FILE = "browser_config.json"

def get_browser_preference():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                if config.get('browser'):
                    use_saved = input(f"Found saved browser preference: {config['browser']}. Use it? (y/n): ").lower()
                    if use_saved == 'y':
                        return config['browser']
        except:
            pass

    print("\nAvailable browsers:")
    print("1. Chrome")
    print("2. Firefox")
    print("3. Edge")
    
    while True:
        choice = input("\nSelect your browser (1-3): ").strip()
        if choice == "1":
            browser = "chrome"
            break
        elif choice == "2":
            browser = "firefox"
            break
        elif choice == "3":
            browser = "edge"
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

    save_pref = input("\nSave this browser preference for future use? (y/n): ").lower()
    if save_pref == 'y':
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'browser': browser}, f)
    
    return browser

def get_browser_driver(browser_name, proxy=None):
    browser_name = browser_name.lower()
    print(f"Starting {browser_name} browser...")
    
    try:
        if browser_name == "chrome":
            options = ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            if proxy:
                options.add_argument(f"--proxy-server={proxy}")
            
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            
        elif browser_name == "firefox":
            options = FirefoxOptions()
            if proxy:
                # Firefox proxy setup is different
                pass
            
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=options)
            driver.maximize_window()
            
        elif browser_name == "edge":
            options = EdgeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            if proxy:
                options.add_argument(f"--proxy-server={proxy}")
            
            service = EdgeService(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=options)
            
        else:
            print(f"Unsupported browser: {browser_name}. Defaulting to Chrome.")
            return get_browser_driver("chrome", proxy)

        # Add stealth settings
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        print(f"{browser_name.capitalize()} browser started successfully!")
        return driver
        
    except Exception as e:
        print(f"Error starting {browser_name}: {str(e)}")
        print("Trying Chrome as fallback...")
        if browser_name != "chrome":
            return get_browser_driver("chrome", proxy)
        else:
            print("Failed to start any browser. Please check your browser installation.")
            raise

def login(driver, username, password):
    try:
        print(f"[{username}] Navigating to Instagram login...")
        driver.get("https://www.instagram.com/accounts/login/")
        
        # Wait for page to load
        wait = WebDriverWait(driver, 20)
        
        # Accept cookies if present
        try:
            cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Allow')]")))
            cookie_button.click()
            time.sleep(2)
        except:
            pass
        
        # Find and fill username
        print(f"[{username}] Entering credentials...")
        username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_input = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        
        # Clear fields and enter credentials
        username_input.clear()
        time.sleep(1)
        username_input.send_keys(username)
        time.sleep(1)
        
        password_input.clear()
        time.sleep(1)
        password_input.send_keys(password)
        time.sleep(2)
        
        # Submit login
        password_input.send_keys(Keys.RETURN)
        
        # Wait for login to complete
        try:
            # Wait for home page or main feed
            wait.until(EC.any_of(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@aria-label, 'Home')]")),
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/')]//div[contains(@aria-label, 'Home')]")),
                EC.presence_of_element_located((By.XPATH, "//svg[@aria-label='Home']"))
            ))
            print(f"[{username}] Logged in successfully!")
            time.sleep(3)
            
            # Dismiss any post-login popups
            dismiss_popups(driver)
            
        except Exception as e:
            print(f"[{username}] Login may have failed or requires additional verification: {str(e)}")
            # Check if we're on the main page anyway
            if "instagram.com" in driver.current_url and "login" not in driver.current_url:
                print(f"[{username}] Appears to be logged in despite error.")
            else:
                raise
                
    except Exception as e:
        print(f"[{username}] Login failed: {str(e)}")
        print(f"[{username}] Current URL: {driver.current_url}")
        raise

def dismiss_popups(driver):
    """Dismiss various Instagram popups"""
    popup_selectors = [
        "//button[contains(text(), 'Not Now')]",
        "//button[contains(text(), 'Cancel')]",
        "//button[contains(text(), 'Dismiss')]",
        "//button[contains(text(), 'Use App')]",
        "//button[contains(text(), 'OK')]",
        "//button[contains(text(), 'Save Info')]",
        "//button[contains(text(), 'Turn on Notifications')]"
    ]
    
    for selector in popup_selectors:
        try:
            popup = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, selector)))
            popup.click()
            print(f"Dismissed popup")
            time.sleep(1)
        except:
            continue
    
    # Try pressing escape as well
    try:
        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        time.sleep(1)
    except:
        pass

def pick_video(folder):
    """Pick a random video from the folder"""
    if not os.path.exists(folder):
        print(f"Video folder does not exist: {folder}")
        return None
        
    files = [f for f in os.listdir(folder) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
    if not files:
        print(f"No video files found in: {folder}")
        return None
        
    selected_file = random.choice(files)
    full_path = os.path.join(folder, selected_file)
    print(f"Selected video: {selected_file}")
    return full_path

def upload_video(driver, video_path, caption, username):
    """Upload a video to Instagram"""
    try:
        print(f"[{username}] Starting video upload...")
        driver.get("https://www.instagram.com/")
        time.sleep(5)
        dismiss_popups(driver)

        # Find and click the "New post" button
        try:
            # Try multiple selectors for the new post button
            new_post_selectors = [
                "//div[@role='menuitem']//*[name()='svg' and @aria-label='New post']",
                "//div[contains(@aria-label, 'New post')]",
                "//a[contains(@href, '/create/')]",
                "//*[contains(text(), 'Create')]"
            ]
            
            new_post_button = None
            for selector in new_post_selectors:
                try:
                    new_post_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if not new_post_button:
                raise Exception("Could not find 'New post' button")
                
            new_post_button.click()
            print(f"[{username}] Clicked 'New post' button")
            time.sleep(3)
            
        except Exception as e:
            print(f"[{username}] Error clicking New post button: {e}")
            return False

        # Upload the file
        try:
            # Look for file input
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
            )
            file_input.send_keys(video_path)
            print(f"[{username}] File uploaded")
            time.sleep(7)  # Wait for upload to process
            
        except Exception as e:
            print(f"[{username}] Error uploading file: {e}")
            return False

        # Click Next buttons
        try:
            # First Next button (after upload)
            next_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Next")]'))
            )
            next_button.click()
            print(f"[{username}] Clicked first Next button")
            time.sleep(3)
            
            # Second Next button (after editing)
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Next")]'))
            )
            next_button.click()
            print(f"[{username}] Clicked second Next button")
            time.sleep(3)
            
        except Exception as e:
            print(f"[{username}] Error with Next buttons: {e}")
            # Continue anyway, might still work

        # Add caption and share
        try:
            # Find caption textarea
            caption_area = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//textarea[@aria-label="Write a caption..."]'))
            )
            caption_area.clear()
            caption_area.send_keys(caption)
            print(f"[{username}] Added caption")
            time.sleep(2)
            
            # Click Share button
            share_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Share")]'))
            )
            share_button.click()
            print(f"[{username}] Post shared successfully!")
            time.sleep(5)
            return True
            
        except Exception as e:
            print(f"[{username}] Error adding caption or sharing: {e}")
            return False
            
    except Exception as e:
        print(f"[{username}] Upload failed: {e}")
        return False

def run_account(account, browser):
    username = account["username"]
    password = account["password"]
    videos_per_day = account.get("videos_per_day", 1)
    proxy = account.get("proxy")
    min_delay = account.get("min_delay", 45)
    max_delay = account.get("max_delay", 300)
    start_offset = account.get("start_offset", 0)

    video_folder = os.path.join(BASE_VIDEO_FOLDER, username, "ToUpload")
    posted_folder = os.path.join(BASE_VIDEO_FOLDER, username, "Posted")
    
    # Create directories if they don't exist
    os.makedirs(video_folder, exist_ok=True)
    os.makedirs(posted_folder, exist_ok=True)

    print(f"[{username}] Starting in {start_offset} seconds...")
    time.sleep(start_offset)

    driver = None
    try:
        driver = get_browser_driver(browser, proxy)
        login(driver, username, password)
        
        for i in range(videos_per_day):
            print(f"[{username}] Processing video {i+1}/{videos_per_day}")
            
            video_path = pick_video(video_folder)
            if not video_path:
                print(f"[{username}] No videos available for upload.")
                break
                
            # Generate random caption
            captions = [
                "Fresh content! 🔥 #reel #viral",
                "Daily drop! 📱 #content #upload",
                "Grind mode activated 💪 #hustle #auto",
                "New post alert! 🚨 #fresh #content",
                "Keeping it real 💯 #authentic #daily"
            ]
            caption = random.choice(captions)
            
            # Attempt upload
            success = upload_video(driver, video_path, caption, username)
            
            if success:
                # Move video to posted folder
                try:
                    posted_path = os.path.join(posted_folder, os.path.basename(video_path))
                    shutil.move(video_path, posted_path)
                    print(f"[{username}] Video moved to posted folder")
                except Exception as e:
                    print(f"[{username}] Error moving video: {e}")
                
                # Wait before next post
                if i < videos_per_day - 1:  # Don't wait after the last video
                    wait_time = random.randint(min_delay, max_delay)
                    print(f"[{username}] Waiting {wait_time} seconds before next post...")
                    time.sleep(wait_time)
            else:
                print(f"[{username}] Upload failed, skipping to next video")
                
    except KeyboardInterrupt:
        print(f"\n[{username}] Gracefully shutting down...")
    except Exception as e:
        print(f"[{username}] ERROR: {e}")
    finally:
        if driver:
            try:
                driver.quit()
                print(f"[{username}] Browser closed.")
            except:
                pass
        print(f"[{username}] Session finished.")

def main():
    try:
        print("=" * 50)
        print("Welcome to Instagram Bot v2.0!")
        print("=" * 50)
        
        # Check if accounts file exists
        if not os.path.exists(ACCOUNTS_FILE):
            print(f"Error: {ACCOUNTS_FILE} not found!")
            print("Please create an accounts.json file with your account details.")
            return
        
        browser = get_browser_preference()
        print(f"Selected browser: {browser}")
        
        with open(ACCOUNTS_FILE, "r") as f:
            accounts = json.load(f)
        
        if not accounts:
            print("No accounts found in accounts.json!")
            return
            
        print(f"Found {len(accounts)} account(s) to process.")
        
        # Run accounts in separate threads
        threads = []
        for i, account in enumerate(accounts):
            print(f"Starting thread for account: {account['username']}")
            t = threading.Thread(target=run_account, args=(account, browser))
            threads.append(t)
            t.start()
            
            # Small delay between starting threads
            if i < len(accounts) - 1:
                time.sleep(5)

        # Wait for all threads to complete
        for t in threads:
            t.join()
            
        print("All accounts finished processing!")
        
    except KeyboardInterrupt:
        print("\nShutting down all threads...")
        sys.exit(0)
    except Exception as e:
        print(f"Main error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()