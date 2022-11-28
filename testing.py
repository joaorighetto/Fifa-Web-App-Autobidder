import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

service = Service(r"C:\Program Files (x86)\chromedriver.exe")
options = Options()
options.add_argument(r"--user-data-dir=C:\Users\Joao Marcos\AppData\Local\Google\Chrome\User Data") 
options.add_argument("--profile-directory=Profile 1")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.ea.com/fifa/ultimate-team/web-app/")

try:

    transfer = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "icon-transfer"))
    )
    transfer.click()

    search_market_box = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ut-tile-transfer-market"))
    )
    search_market_box.click()

    time.sleep(0.33)
    # quality
    driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
                                  "div/div[2]/div/div[1]/div[1]/div[2]/div/div").click()
    time.sleep(0.33)
    # gold
    driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
                                  "div/div[2]/div/div[1]/div[1]/div[2]/div/ul/li[4]").click()
    time.sleep(0.33)
    # rarity
    driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
                                  "div/div[2]/div/div[1]/div[1]/div[3]/div/div").click()
    time.sleep(0.33)
    # common
    driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
                                  "div/div[2]/div/div[1]/div[1]/div[3]/div/ul/li[2]").click()
    time.sleep(0.33)

    # filters
    max_buy_now = driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
                                                "div/div[2]/div/div[1]/div[2]/div[6]/div[2]/input")
    max_buy_now.click()
    max_buy_now.send_keys("400")
    time.sleep(0.33)

    # search
    driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
                                  "div/div[2]/div/div[2]/button[2]").click()

    WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "paginated-item-list"))
        )
    time.sleep(1)
    player_list = driver.find_elements(By.CSS_SELECTOR, ".listFUTItem")
    try:
        for player in player_list:  # <li> in <ul>
            time.sleep(0.2)
            player.click()
            time.sleep(0.5)
            driver.find_element(By.CLASS_NAME, "buyButton").click()  # buy now
            time.sleep(0.5)
            driver.find_element(By.XPATH, "/html/body/div[4]/section/div/div/button[1]").click()  # confirm
            time.sleep(0.5)
            try:
                driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                              "section[2]/div/div/div[2]/div[3]/button[8]").click()
            except selenium.common.exceptions.NoSuchElementException as e:
                print(e)
            finally:
                continue
    except Exception as e:
        print("for loop:", e)
    finally:
        driver.find_element(By.XPATH, "/html/body/main/section/section/div[1]/button[1]").click()  # go back
    # TODO restart loop

except Exception as e:
    print("general exception: ", e)
