from datetime import datetime
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from bs4 import BeautifulSoup
import requests
import re
import json

H = {'User-Agent': 'Mozilla/5.0'}


def sclick(target):
    time.sleep(0.1)
    target.click()
    time.sleep(0.2)


def navigate_to_market():
    transfer = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "icon-transfer"))
    )
    transfer.click()

    search_market_box = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "ut-tile-transfer-market"))
    )
    search_market_box.click()

    time.sleep(0.2)


def buy_loop():
    # Set player name and max value to search
    target_profit = 300
    with open("prices.txt", "r") as prices:
        for line in prices:
            players_prices_dict = json.loads(line)
    for name, price in players_prices_dict.items():
        target_price = "2100"  # str(price * 0.95 - target_profit)
        name_box = driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
                                                 "div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/input")
        sclick(name_box)
        name_box.send_keys(name)
        select_player = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CLASS_NAME, "btn-text"))
        )
        sclick(select_player)

        max_value_box = driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
                                                      "div/div[2]/div/div[1]/div[2]/div[6]/div[2]/input")
        sclick(max_value_box)
        max_value_box.send_keys(target_price)
        max_value_box.send_keys(Keys.ENTER)
        time.sleep(1)
        bid_and_sell(price, name)


def bid_and_sell(sell_value, player_name):
    # Click search
    profit = 0
    driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
                                  "div/div[2]/div/div[2]/button[2]").click()
    try:
        WebDriverWait(driver, 1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".listFUTItem"))
        )

        player_list = driver.find_elements(By.CSS_SELECTOR, ".listFUTItem")
        for player in player_list:  # <li> in <ul>
            time.sleep(0.1)
            player.click()
            time.sleep(0.1)
            driver.find_element(By.CLASS_NAME, "buyButton").click()  # buy now
            time.sleep(0.1)
            driver.find_element(By.XPATH, "/html/body/div[4]/section/div/div/button[1]").click()  # confirm
            try:
                bid_won = WebDriverWait(driver, 0.7).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".listFUTItem.won"))
                )
                if bid_won:
                    time.sleep(0.2)
                    bid_value = driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                                              "section[1]/div/ul/li[1]/div/div[2]/div[2]/span[2]").text
                    bid_value = re.sub(r",", "", bid_value)
                    print(f"{player_name} bid won: {bid_value}")
                    driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                                  "section[2]/div/div/div[2]/div[2]/div[1]/button").click()  # list on the transfer market
                    time.sleep(0.5)
                    max_value_box = driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                                                  "section[2]/div/div/div[2]/div[2]/div[2]/div[3]/div[2]/input")  # max value
                    min_value_box = driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                                                  "section[2]/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/input")
                    max_value_box.click()
                    time.sleep(0.2)
                    max_value_box.send_keys(Keys.BACK_SPACE)
                    time.sleep(0.2)
                    max_value_box.send_keys(sell_value)
                    time.sleep(0.2)
                    min_value_box.click()
                    time.sleep(0.2)
                    min_value_box.send_keys(Keys.BACK_SPACE)
                    time.sleep(0.2)
                    min_value_box.send_keys(sell_value - 100)
                    time.sleep(0.2)

                    driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                                  "section[2]/div/div/div[2]/div[2]/div[2]/button").click()  # list on market
                    print(f"{player_name} listed for: {sell_value}")
                    time.sleep(0.2)
                    if bid_value:
                        profit += sell_value * 0.95 - float(bid_value)
                        print(f"Expected profit: {profit}")

            except TimeoutException:
                print("Bid failed")

    except TimeoutException:
        print(f"{player_name} not found")

    finally:
        time.sleep(0.1)
        driver.find_element(By.CSS_SELECTOR, ".ut-navigation-button-control").click()  # go back


def get_player_ids():
    ids_dict = {}
    url = "https://www.futbin.com/players?page=1&player_rating=84-84&pos_type=all&sort=ps_price&order=asc&version=gold"
    r = requests.get(url, headers=H)
    soup = BeautifulSoup(r.content, "html.parser")
    for player_img in soup.find_all("img", {"class": "player_img"}):
        key = player_img.get('alt')  # extract player name from 'alt' attribute
        new_key = re.sub(r"\s\d*$", "", key)  # clean player's name from rating
        value = player_img.get("data-original")  # this is where we can find the player ID
        new_value = re.search(r"/\d*\.", value).group(0)
        ids_dict[f"{new_key}"] = new_value.strip("/.")
    return ids_dict


def get_players_prices():
    print("Fetching prices...")
    base_url = "https://www.futbin.com/23/playerPrices/?player="
    prices = {}
    for name, id_ in get_player_ids().items():
        time.sleep(1)
        url = base_url + id_
        r = requests.get(url, headers=H)
        data = r.json()
        price = data[id_]['prices']['pc']['LCPrice']
        price = re.sub(r",", "", price)
        prices[name] = int(price)
    with open("prices.txt", "w") as file:
        file.truncate(0)
        file.write(json.dumps(prices))
    print("Prices successfully fetched.")


last_modified_time = os.path.getmtime("prices.txt")
if time.time() - last_modified_time > 1800:
    get_players_prices()
service = Service(r"C:\Program Files (x86)\chromedriver.exe")
options = Options()
options.add_argument(r"--user-data-dir=C:\Users\Joao Marcos\AppData\Local\Google\Chrome\User Data")
options.add_argument("--profile-directory=Profile 1")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.ea.com/fifa/ultimate-team/web-app/")

navigate_to_market()
while True:
    buy_loop()
