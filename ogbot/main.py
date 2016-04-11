import re
import logging
import sys

from bot import OgameBot
from config import Config

from scraping import authentication

# setting up logger
logger = logging.getLogger('OGBot')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info('Starting the bot')

config = Config(sys.argv)

auth_client = authentication.AuthenticationProvider(config)
browser = auth_client.get_browser()

bot = OgameBot(browser, config)

switcher = {
    'overview' : bot.overview,
    'explore' : bot.explore,
    'attack_inactive_planets' : bot.attack_inactive_planets,
    'auto_build_defenses' : bot.auto_build_defenses,
    'auto_build_defenses_to_planet' : bot.auto_build_defenses_to_planet,
    'transport_resources_to_planet' : bot.transport_resources_to_planet
}

logger.info("Bot running on %s mode" % config.mode)
switcher.get(config.mode)()
logger.info("Quiting bot")
