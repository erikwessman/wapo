import os
import re
import time
import traceback
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FFOptions
from selenium.webdriver.firefox.service import Service as FFService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _get_firefox_driver(geckodriver_path: str):
    options = FFOptions()
    options.log.level = "trace"
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    service = FFService(executable_path=geckodriver_path)
    return webdriver.Firefox(options=options, service=service)


def _get_chrome_driver(chrome_bin_path: str, chromedriver_path: str):
    chrome_options = ChromeOptions()
    chrome_options.binary_location = chrome_bin_path
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    chrome_service = ChromeService(executable_path=chromedriver_path)
    return webdriver.Chrome(service=chrome_service, options=chrome_options)


def _get_driver():
    environment = os.getenv("WAPO_ENVIRONMENT")

    if environment == "devel":
        geckodriver_path = os.getenv("GECKODRIVER_PATH")
        return _get_firefox_driver(geckodriver_path)
    elif environment == "prod":
        chrome_bin_path = os.environ.get("GOOGLE_CHROME_BIN")
        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
        return _get_chrome_driver(chrome_bin_path, chromedriver_path)
    else:
        raise ValueError("Can't get webdriver, no environment set")


def get_wapo_url(day: str = None) -> str:
    """
    Retrieves the URL of the latest Washington Post crossword puzzle.

    Parameters:
    - day (str, optional): The specific day for which the crossword URL is needed. Defaults to None, which fetches the latest crossword puzzle.

    Returns:
    - str: The URL of the specified day's crossword puzzle.

    Raises:
    - WebDriverException: If there are issues in controlling the browser through WebDriver.
    - TimeoutException: If the expected elements do not appear within the given time.
    """
    driver = _get_driver()

    try:
        driver.get("https://www.washingtonpost.com/crossword-puzzles/daily/")

        wait = WebDriverWait(driver, 10)

        btn_accept_cookies = wait.until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        btn_accept_cookies.click()

        driver.execute_script("""
            var leaderboardWrapper = document.getElementById('leaderboard-wrapper');
            if (leaderboardWrapper) {
                leaderboardWrapper.remove();
            }
        """)

        crossword_frame = wait.until(
            EC.element_to_be_clickable((By.ID, "iframe-xword"))
        )
        driver.switch_to.frame(crossword_frame)

        item_latest_crossword = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "puzzle-link"))
        )
        item_latest_crossword.click()

        btn_footer = wait.until(EC.element_to_be_clickable((By.ID, "footer-btn")))
        btn_footer.click()

        # Wait for things to load
        time.sleep(2)

        btn_invite = wait.until(
            EC.element_to_be_clickable((By.CLASS_NAME, "nav-social-play-invite-icon"))
        )
        btn_invite.click()

        textarea_invite_link = wait.until(
            EC.presence_of_element_located((By.ID, "social-link"))
        )
        return textarea_invite_link.get_attribute("value")

    finally:
        driver.quit()


def get_puzzle_time(url: str) -> int:
    """
    Retrieves the time taken to complete a crossword puzzle from a given URL.

    If the webdriver cannot get the puzzle time it raises a ValueError

    Parameters:
    - url (str): The URL of the crossword puzzle.

    Returns:
    - int: The completion time of the puzzle in seconds.
    """
    driver = _get_driver()

    try:
        driver.get(url)

        wait = WebDriverWait(driver, 10)

        btn_accept_cookies = wait.until(
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        btn_accept_cookies.click()

        crossword_frame = wait.until(
            EC.element_to_be_clickable((By.ID, "iframe-xword"))
        )
        driver.switch_to.frame(crossword_frame)

        bla = wait.until(
            EC.visibility_of_element_located((By.CLASS_NAME, "modal-title"))
        )

        print("here")

        print(bla)

        print(bla.text)

        time_str = wait.until(
            EC.visibility_of_element_located((By.ID, "clock_str"))
        )  # returns "X minutes and Y seconds"

        minutes = re.search(r"(\d+)\s+minutes?", time_str.text)
        seconds = re.search(r"(\d+)\s+seconds?", time_str.text)

        minutes = int(minutes.group(1)) if minutes else 0
        seconds = int(seconds.group(1)) if seconds else 0

        return int(minutes) * 60 + int(seconds)

    except Exception as error:
        print(f"Error type: {type(error)}, Error: {error}, Trace: {traceback.format_exc()}")
        raise

    finally:
        driver.quit()
