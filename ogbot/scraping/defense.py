﻿import util
from mechanize import Browser
from bs4 import BeautifulSoup
import re
import logging
from scraper import *


class Defense(Scraper):

    def get_defenses(self, planet = None):
        """
        Get defenses for the given planet
        """
        self.logger.info('Getting defense data')
        url = self.url_provider.get_page_url('defense', planet)
        self.logger.info('The defense url is ' + url)
        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")
        refs = soup.findAll("span", { "class" : "textlabel" })

        defenses = []
        for ref in refs:
            if ref.parent['class'] == ['level']:
                aux = ref.parent.text.replace('\t','')
                shipData = re.sub('  +', '', aux).encode('utf8')
                defenses.append( tuple(shipData.split('\n')) )

        defenses = map(tuple, map(scraper.sanitize, [filter(None, i) for i in defenses]))
        return defenses

    def auto_build_defenses(self, planet = None):
        """
        Build some defenses for the given planet
        """
        defense_types = [('406', '20'), ('404', '100'), ('402', '6000'), ('401', '3000')]

        self.logger.info('Auto building defenses')
        self.redirect_to_page(planet)
        for defense in defense_types:
            self.build_defense_item(defense, planet)

    def redirect_to_page(self, planet = None):
        """
        Redirect to defense page for the given planet
        """
        url = self.url_provider.get_page_url('defense', planet)
        self.logger.info("Redirecting to page %s" % url)
        self.open_url(url)

    def build_defense(self, defense, planet = None):
        """
        Build defenses for the given planet.
        defense should be a tuple where defense[0] is the defense type
        and defense[1] is the amount as string.
        defense type examples:
            401 - missile launcher
            402 - light cannon
            404 - gauss cannon
            406 - plasma
        """

        self.redirect_to_page(planet)

        try:
            self.build_defense_item(defense, planet)
        except Exception as e:
            self.logger.info('Error building defense')
            self.logger.info(e)

    def build_defense_item(self, defense, planet = None):
        self.logger.info("building %s %s on planet %s" % (defense[1], defense[0], planet.name))
        self.logger.info("Writing data to form")
        self.browser.select_form(name='form')
        self.browser.form.new_control('text','menge',{'value': defense[1]})
        self.browser.form.fixup()
        self.browser['menge'] = defense[1]
        self.browser.form.new_control('text','type',{'value':defense[0]})
        self.browser.form.fixup()
        self.browser['type'] = defense[0]
        self.browser.form.new_control('text','modus',{'value':'1'})
        self.browser.form.fixup()
        self.browser['modus'] = '1'
        self.logger.info("Submitting build defense request")
        self.submit_request()
