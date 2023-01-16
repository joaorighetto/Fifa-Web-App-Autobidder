import configparser
import re
import requests
from bs4 import BeautifulSoup
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from util import sclick
from time import time
import json


class Bot:

    def __init__(self, driver):

        self.driver = driver
        self.config = configparser.ConfigParser()
        self.config.read("settings.ini")
        self.player_id_dict = self.config.get("Data", "player_id_dict")
        self.player_price_dict = self.config.get("Data", "player_price_dict")

        # Stats
        self.user_players_won = self.config.getint("Statistics", "players_won")
        self.user_players_lost = self.config.getint("Statistics", "players_lost")
        self.user_players_sold = self.config.getint("Statistics", "players_sold")
        self.user_coins = self.config.getint("Statistics", "current_coins")
        self.user_projected_profit = self.config.getfloat("Statistics", "projected_profit")
        self.total_cycles = self.config.getint("Statistics", "total_cycles")
        self.user_searches_made = self.config.getint("Statistics", "searches_made")
        self.user_bids_made = self.config.getint("Statistics", "bids_made")
        self.last_price_update_time = self.config.getfloat("Statistics", "last_price_update_time")

        # Round variables

        self.round_number = 0
        self.bids_made_this_round = 0
        self.requests_made_this_round = 0
        self.players_won_this_round = 0
        self.players_lost_this_round = 0
        self.projected_profit_this_round = 0

        # Misc
        self.header = {'User-Agent': 'Mozilla/5.0'}

    def run(self):

        self.navigate_to_market()
        curr_time = time()

        while True:
            self.round_number += 1
            print("Round: ", self.round_number)
            if curr_time - self.last_price_update_time > 3600:
                self.get_player_ids()
                self.get_player_prices()
                self.config.set('Statistics', 'last_price_update_time', f'{curr_time}')
                with open('../data/settings.ini', 'w') as configfile:
                    self.config.write(configfile)
            self.buy_loop()

    def navigate_to_market(self):
        self.driver.get("https://www.ea.com/fifa/ultimate-team/web-app/")

        transfer = WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "icon-transfer"))
        )
        transfer.click()

        self.wait_for_shield_invisibility()

        search_market_box = self.driver.find_element(By.CLASS_NAME, "ut-tile-transfer-market")
        search_market_box.click()
        sleep(.2)

    def buy_loop(self):
        for name, price in json.loads(self.player_price_dict).items():
            sleep(2.5)
            search_price = str(int(price) - int(self.config['Settings']['margin']))
            name_box = self.driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
                                                          "div/div[2]/div/div[1]/div[1]/div[1]/div/div[1]/input")
            sclick(name_box)
            name_box.send_keys(name)
            select_player = WebDriverWait(self.driver, 2).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btn-text"))
            )
            sclick(select_player)
            max_value_box = self.driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
                                                               "div/div[2]/div/div[1]/div[2]/div[6]/div[2]/input")
            sclick(max_value_box)
            max_value_box.send_keys(search_price)
            max_value_box.send_keys(Keys.ENTER)
            # Click search
            sclick(self.driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/"
                                                      "div/div[2]/div/div[2]/button[2]"))
            self.requests_made_this_round += 1
            self.bid(name, price)

    def bid(self, player_name, sell_value):
        sleep(.5)
        player_list = self.driver.find_elements(By.CSS_SELECTOR, ".listFUTItem")
        if len(player_list) > 0:
            for player in player_list:  # <li> in <ul>
                self.wait_for_shield_invisibility()
                WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(player)
                        )
                sclick(player)
                buy_now = self.driver.find_element(By.CLASS_NAME, "buyButton")
                sclick(buy_now)
                self.bids_made_this_round += 1

                buy_confirm = self.driver.find_element(By.XPATH, "/html/body/div[4]/section/div/div/button[1]")
                sclick(buy_confirm)

                try:
                    bid_won = WebDriverWait(self.driver, 2.5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "li.listFUTItem.has-auction-data.selected.won"))
                    )
                except TimeoutException:
                    bid_won = None
                    self.players_lost_this_round += 1
                    print("Bid failed")

                if bid_won:
                    bid_value = self.driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/section[2]/div/div/div[2]/div[1]/div[2]/div/span[2]").text
                    self.players_won_this_round += 1
                    bid_value = re.sub(r",", "", bid_value)
                    print("-" * 40)
                    print(f"{player_name} bid won: {bid_value}")

                    sclick(self.driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                                              "section[2]/div/div/div[2]/div[2]/div[1]/button"))  # list on the transfer market

                    self.wait_for_shield_invisibility()

                    max_value_box = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                                              "section[2]/div/div/div[2]/div[2]/div[2]/div[3]/div[2]/input"))
                        )
                    sclick(max_value_box)
                    max_value_box.send_keys(Keys.BACK_SPACE)
                    sleep(0.2)
                    max_value_box.send_keys(sell_value)
                    sleep(0.2)

                    min_value_box = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                                              "section[2]/div/div/div[2]/div[2]/div[2]/div[2]/div[2]/input"))
                        )
                    sclick(min_value_box)
                    min_value_box.send_keys(Keys.BACK_SPACE)
                    sleep(0.2)
                    min_value_box.send_keys(sell_value - 100)
                    sleep(0.2)

                    sclick(self.driver.find_element(By.XPATH, "/html/body/main/section/section/div[2]/div/div/"
                                                              "section[2]/div/div/div[2]/div[2]/div[2]/button"))  # confirm list on market

                    print(f"{player_name} listed for: {sell_value}")
                    print("-" * 40)
                    self.wait_for_shield_invisibility()

                    self.projected_profit_this_round += sell_value * 0.95 - float(bid_value)
                    sclick(self.driver.find_element(By.CSS_SELECTOR, ".ut-navigation-button-control"))  # go back
                else:
                    self.wait_for_shield_invisibility()
                    continue
        else:
            self.wait_for_shield_invisibility()
            sclick(self.driver.find_element(By.CSS_SELECTOR, ".ut-navigation-button-control"))  # go back

    def get_player_ids(self):
        id_dict = {}
        url = self.config['Settings']['futbin_filter_url']
        r = requests.get(url, headers=self.header)
        soup = BeautifulSoup(r.content, "html.parser")
        for player_img in soup.find_all("img", {"class": "player_img"}):
            key = player_img.get('alt')  # extract player name from 'alt' attribute
            player_name = re.sub(r"\s\d*$", "", key)  # clean player's name from rating
            player_id = player_img.get("data-original")  # this is the attribute where we can find the player ID
            player_id = re.search(r"/\d*\.", player_id).group(0)
            id_dict[f"{player_name}"] = player_id.strip("/.")
        self.config.set("Data", "player_id_dict", json.dumps(id_dict))
        with open("../data/settings.ini", "w") as configfile:
            self.config.write(configfile)

    def get_player_prices(self):
        print("-" * 50)
        print("Fetching prices...")
        base_url = "https://www.futbin.com/23/playerPrices/?player="
        price_dict = {}
        for name, id_ in json.loads(self.player_id_dict).items():
            sleep(0.5)
            url = base_url + id_
            print(url)
            r = requests.get(url, headers=self.header)
            data = r.json()

            price = str(data[id_]['prices']['pc']['LCPrice'])
            price = re.sub(r",", "", price)

            if price != "0":
                price_dict[name] = int(price)
            else:
                price_dict[name] = None

        lowest_price = min(price_dict.values())
        print(f"Lowest price found: {lowest_price}")
        print("Prices successfully loaded.")
        self.last_price_update_time = time()
        print("-" * 50)
        self.config.set("Data", "player_price_dict", json.dumps(price_dict))
        with open("../data/settings.ini", "w") as configfile:
            self.config.write(configfile)

    def wait_for_shield_invisibility(self):
        WebDriverWait(self.driver, 30).until(
            EC.invisibility_of_element_located(
                (By.CLASS_NAME, 'ut-click-shield'))
        )
        sleep(0.1)
