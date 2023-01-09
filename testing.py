from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from time import sleep, time
import requests
import re
import json
import os

H = {'User-Agent': 'Mozilla/5.0'}


def wait_for_shield_invisibility(driver_):

    WebDriverWait(driver_, 30).until(
        EC.invisibility_of_element_located(
            (By.CLASS_NAME, 'ut-click-shield'))
    )
    sleep(0.1)


def sclick(target):
    sleep(0.3)
    target.click()
    sleep(0.3)


def navigate_to_market():
    transfer = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "icon-transfer"))
    )
    transfer.click()

    wait_for_shield_invisibility(driver)

    search_market_box = driver.find_element(By.CLASS_NAME, "ut-tile-transfer-market")
    search_market_box.click()

    # max_value_box = driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
    #                                               "div/div[2]/div/div[1]/div[2]/div[6]/div[2]/input")

    # target_price = "2800"
    # sclick(max_value_box)
    # max_value_box.send_keys(target_price)
    # max_value_box.send_keys(Keys.ENTER)

    sleep(0.2)


def buy_loop():
    # Set player name and max value to search
    target_profit = 600
    loop_profit = 0
    with open("prices.txt", "r") as prices:
        for line in prices:
            players_prices_dict = json.loads(line)
    for name, price in players_prices_dict.items():
        sleep(2.5)
        target_price = str(price - target_profit)
        name_box = driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
                                                 "div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/input")
        sclick(name_box)
        name_box.send_keys(name)
        try:
            select_player = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, "btn-text"))
            )
            sclick(select_player)
        except TimeoutException:
            name_box.send_keys(Keys.BACK_SPACE)
            sleep(0.1)
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
        sleep(0.5)
        # Click search
        driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
                                      "div/div[2]/div/div[2]/button[2]").click()
        try:
            WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".listFUTItem"))
            )
            loop_profit += bid_and_sell(price, name)
        except TimeoutException:
            driver.find_element(By.CSS_SELECTOR, ".ut-navigation-button-control").click()  # go back

    return loop_profit


def bid_and_sell(sell_value, player_name):
    profit = 0
    player_list = driver.find_elements(By.CSS_SELECTOR, ".listFUTItem")
    for player in player_list:  # <li> in <ul>
        wait_for_shield_invisibility(driver)
        player.click()
        sleep(0.2)
        driver.find_element(By.CLASS_NAME, "buyButton").click()  # buy now
        sleep(0.2)
        driver.find_element(By.XPATH, "/html/body/div[4]/section/div/div/button[1]").click()  # confirm
        sleep(0.2)
        try:
            bid_won = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li.listFUTItem.has-auction-data.selected.won"))
            )
        except TimeoutException:
            bid_won = None
            print("Bid failed")
        if bid_won:
            bid_value = driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                                      "section[1]/div/ul/li[1]/div/div[2]/div[2]/span[2]").text
            bid_value = re.sub(r",", "", bid_value)
            print("-" * 40)
            print(f"{player_name} bid won: {bid_value}")

            driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                          "section[2]/div/div/div[2]/div[2]/div[1]/button").click()  # list on the transfer market

            wait_for_shield_invisibility(driver)

            max_value_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                                      "section[2]/div/div/div[2]/div[2]/div[2]/div[3]/div[2]/input"))
                )

            max_value_box.click()
            sleep(0.2)
            max_value_box.send_keys(Keys.BACK_SPACE)
            sleep(0.2)
            max_value_box.send_keys(sell_value)
            sleep(0.2)

            min_value_box = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                                      "section[2]/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/input"))
                )
            min_value_box.click()
            sleep(0.2)
            min_value_box.send_keys(Keys.BACK_SPACE)
            sleep(0.2)
            min_value_box.send_keys(sell_value - 100)
            sleep(0.2)

            driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                          "section[2]/div/div/div[2]/div[2]/div[2]/button").click()  # confirm list on market
            print(f"{player_name} listed for: {sell_value}")
            print("-" * 40)
            wait_for_shield_invisibility(driver)

            profit += sell_value * 0.95 - float(bid_value)
            driver.find_element(By.CSS_SELECTOR, ".ut-navigation-button-control").click()  # go back
            return profit
        else:
            wait_for_shield_invisibility(driver)
            driver.find_element(By.CSS_SELECTOR, ".ut-navigation-button-control").click()  # go back
            return profit


def get_player_ids():
    ids_dict = {}
    url = "https://www.futbin.com/players?page=1&order=asc&player_rating=84-84&pos_type=all&sort=pc_price&version=gold_rare"
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
    print("-" * 100)
    print("Fetching prices...")
    base_url = "https://www.futbin.com/23/playerPrices/?player="
    prices = {}
    for name, id_ in get_player_ids().items():
        sleep(0.5)
        url = base_url + id_
        print(url)
        r = requests.get(url, headers=H)
        data = r.json()
        price = str(data[id_]['prices']['pc']['LCPrice'])
        price = re.sub(r",", "", price)
        if price != "0":
            prices[name] = int(price)

    lowest_price = min(prices.values())
    print(lowest_price)
    with open("prices.txt", "w+") as file:
        file.truncate(0)
        file.write(json.dumps(prices))
    print("Prices successfully loaded.")
    print("-" * 100)


service = Service(r"C:\Program Files (x86)\chromedriver.exe")
options = Options()
options.add_argument(r"--user-data-dir=C:\Users\Joao Marcos\AppData\Local\Google\Chrome\User Data")
options.add_argument("--profile-directory=Profile 1")


driver = webdriver.Chrome(service=service, options=options)
driver.get("https://www.ea.com/fifa/ultimate-team/web-app/")

total_profit = 0
round_count = 0
navigate_to_market()
while True:
    round_count += 1
    last_time_modified = os.path.getmtime("prices.txt")
    if time() - last_time_modified > 1600:
        get_players_prices()
    round_profit = buy_loop()
    if round_profit > 0:
        total_profit += round_profit
        print("$", total_profit, "- Round:", round_count)
