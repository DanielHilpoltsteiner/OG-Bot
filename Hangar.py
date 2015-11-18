from OgameUtil import UrlProvider
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging


class Hangar:
    def __init__(self, browser, universe):
        self.urlProvider = UrlProvider(universe)
        self.logger = logging.getLogger('ogame-bot')
        self.browser = browser

    def GetShips(self):
        self.logger.info('Getting shipyard data')
        url = self.urlProvider.GetPageUrl('shipyard')
        res = self.browser.open(url)
        soup = BeautifulSoup(res.read())
        refs = soup.findAll("span", { "class" : "textlabel" })

        ships = []
        for ref in refs:
            if ref.parent['class'] == ['level']:
                aux = ref.parent.text.replace('\t','')
                shipData = re.sub('  +', '', aux).encode('utf8')
                ships.append( tuple(shipData.split('\n')) )

        ships = map(tuple, map(sanitize, [filter(None, i) for i in ships]))
        return ships

def sanitize(t):
    for i in t:
        try:
            yield int(i)
        except ValueError:
            yield i
