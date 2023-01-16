from util import create_driver
from bot import Bot


driver = create_driver()
bot = Bot(driver)

bot.run()
