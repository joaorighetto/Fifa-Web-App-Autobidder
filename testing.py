# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import requests
import re
import json

H = {'User-Agent': 'Mozilla/5.0'}

# def navigate_to_market():
#     transfer = WebDriverWait(driver, 60).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "icon-transfer"))
#     )
#     transfer.click()
#
#     search_market_box = WebDriverWait(driver, 5).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "ut-tile-transfer-market"))
#     )
#     search_market_box.click()
#
#     time.sleep(0.5)
#
#
# def set_filters():
#     # quality
#     driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
#                                   "div/div[2]/div/div[1]/div[1]/div[2]/div/div").click()
#     time.sleep(0.5)
#     # gold
#     driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
#                                   "div/div[2]/div/div[1]/div[1]/div[2]/div/ul/li[4]").click()
#     time.sleep(0.5)
#     # rarity
#     driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
#                                   "div/div[2]/div/div[1]/div[1]/div[3]/div/div").click()
#     time.sleep(0.5)
#     # common
#     driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
#                                   "div/div[2]/div/div[1]/div[1]/div[3]/div/ul/li[2]").click()
#     time.sleep(0.5)
#
#     # filters
#     max_buy_now = driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
#                                                 "div/div[2]/div/div[1]/div[2]/div[6]/div[2]/input")
#     max_buy_now.click()
#     max_buy_now.send_keys("400")
#     time.sleep(0.5)
#
#
# def buy_loop(plus_or_minus):
#     # search
#     driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
#                                   "div/div[2]/div/div[2]/button[2]").click()
#
#     WebDriverWait(driver, 2).until(
#             EC.presence_of_element_located((By.CLASS_NAME, "paginated-item-list"))
#         )
#     time.sleep(0.2)
#     player_list = driver.find_elements(By.CSS_SELECTOR, ".listFUTItem")
#     time.sleep(0.1)
#
#     for player in player_list:  # <li> in <ul>
#         time.sleep(0.25)
#         player.click()
#         time.sleep(0.1)
#         driver.find_element(By.CLASS_NAME, "buyButton").click()  # buy now
#         time.sleep(0.1)
#         driver.find_element(By.XPATH, "/html/body/div[4]/section/div/div/button[1]").click()  # confirm
#         try:
#             bid_won = WebDriverWait(driver, 0.7).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, ".listFUTItem.won"))
#             )
#             if bid_won:
#                 print("bid won")
#                 driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
#                                               "section[2]/div/div/div[2]/div[2]/div[1]/button").click()  # list on the transfer market
#                 time.sleep(0.2)
#                 max_value = driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
#                                                           "section[2]/div/div/div[2]/div[2]/div[2]/div[3]/div[2]/input")  # max value
#                 max_value.click()
#                 time.sleep(0.2)
#                 max_value.send_keys("1")  # set max value to minimum possible
#                 time.sleep(0.2)
#                 raise_min_value = driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
#                                                                 "section[2]/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/button[2]")  # raise min value by 4 increments
#                 raise_min_value.click()  # 1
#                 time.sleep(0.1)
#                 raise_min_value.click()  # 2
#                 time.sleep(0.1)
#                 raise_min_value.click()  # 3
#                 time.sleep(0.1)
#                 raise_min_value.click()  # 4
#                 time.sleep(0.1)
#                 driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
#                                               "section[2]/div/div/div[2]/div[2]/div[2]/button").click()  # list on market
#                 time.sleep(0.1)
#         except Exception as e:
#             print("bid failed", type(e))
#
#     time.sleep(0.5)
#     driver.find_element(By.XPATH, "/html/body/main/section/section/div[1]/button[1]").click()  # go back
#     time.sleep(1.5)
#     WebDriverWait(driver, 2).until(
#         EC.presence_of_element_located((By.XPATH, "/html/body/main/section/section/div[2]/div/div[2]/"
#                                                   "div/div[1]/div[2]/div[2]/div[2]/button[2]"))
#     )
#
#     if plus_or_minus in range(0, 3):
#         time.sleep(0.25)
#         driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div[2]/"
#                                       "div/div[1]/div[2]/div[2]/div[2]/button[2]").click()  # this will click plus button in bid value so we are able to refresh players properly
#         print("plus")
#     else:
#         time.sleep(0.25)
#         driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div[2]/"
#                                       "div/div[1]/div[2]/div[2]/div[2]/button[1]").click()  # this will click minus
#         print("minus")


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
    print(ids_dict)
    return ids_dict


def get_players_prices():
    base_url = "https://www.futbin.com/23/playerPrices/?player="
    prices = {}
    for name, id_ in get_player_ids().items():
        time.sleep(1)
        url = base_url + id_
        r = requests.get(url, headers=H)
        data = r.json()
        prices[name] = data[id_]['prices']['pc']['LCPrice']
    print(prices)
    return prices


# service = Service(r"C:\Program Files (x86)\chromedriver.exe")
# options = Options()
# options.add_argument(r"--user-data-dir=C:\Users\Joao Marcos\AppData\Local\Google\Chrome\User Data")
# options.add_argument("--profile-directory=Profile 1")
# options.add_experimental_option("detach", True)
#
# driver = webdriver.Chrome(service=service, options=options)
# driver.get("https://www.ea.com/fifa/ultimate-team/web-app/")
#
# navigate_to_market()
# set_filters()
# x = 0
# while True:
#     buy_loop(x)
#     x += 1
#     if x == 6:
#         x = 0
#     print("x = ", x
get_players_prices()
