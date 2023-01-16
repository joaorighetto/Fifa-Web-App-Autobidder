from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from time import sleep


def create_driver():
    service = Service(r"../chromedriver.exe")
    options = Options()
    options.add_argument(r"--user-data-dir=C:\Users\Joao Marcos\AppData\Local\Google\Chrome\User Data")
    options.add_argument("--profile-directory=Profile 1")
    return webdriver.Chrome(service=service, options=options)


def sclick(target: WebElement):
    sleep(0.3)
    target.click()
    sleep(0.3)
