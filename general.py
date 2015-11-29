import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging
import urlparse

class General:
    def __init__(self, browser, universe):
        self.url_provider = util.UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser

    def get_resources(self):
        self.logger.info('Getting resources data')
        url = self.url_provider.get_page_url('resources')
        res = self.browser.open(url)
        soup = BeautifulSoup(res.read())

        resources = []
        metal = int(soup.find(id='resources_metal').text.replace('.',''))
        resources.append({'metal': metal })
        crystal = int(soup.find(id='resources_crystal').text.replace('.',''))
        resources.append({'crystal': crystal })
        deuterium = int(soup.find(id='resources_deuterium').text.replace('.',''))
        resources.append({'deuterium': deuterium })
        energy = int(soup.find(id='resources_energy').text.replace('.',''))
        resources.append({'energy': energy })
        return resources

    def get_planets(self):
        self.logger.info('Getting planets')
        url = self.url_provider.get_page_url('resources')
        res = self.browser.open(url)
        soup = BeautifulSoup(res.read())
        planets = []
        current_planet = soup.find("meta", { "name" : "ogame-planet-id"})['content']
        planets.append(current_planet)
        links = soup.findAll("a", { "class" : "planetlink tooltipRight js_hideTipOnMobile" })
        planets.extend( [ urlparse.parse_qs(link['href'])['cp'][0] for link in links])
        return planets
