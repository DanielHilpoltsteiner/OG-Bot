from bs4 import BeautifulSoup
import re
from general import General
from scraper import Item, ItemAction, Scraper
from enum import Enum

class ResearchTypes(Enum):
    EnergyTech                      = "113",
    LaserTech                       = "120",
    IonTech                         = "121",
    HyperspaceTech                  = "114",
    PlasmaTech                      = "122",
    CombustionDrive                 = "115",
    ImpulseDrive                    = "117",
    HyperspaceDrive                 = "118",
    EspionageTech                   = "106",
    ComputerTech                    = "108",
    AstroPhysics                    = "124",
    IntergalacticResearchNetwork    = "123",
    GravitonResearch                = "199",
    WeaponTech                      = "109",
    ShieldTech                      = "110",
    ArmourTech                      = "111"

RESEARCH_DATA = {
    "113": ResearchItem("113", "Energy Technology"),
    "120": ResearchItem("120", "Laser Technology"),
    "121": ResearchItem("121", "Ion Technology"),
    "114": ResearchItem("114", "Hyperspace Technology"),
    "122": ResearchItem("122", "Plasma Technology"),
    "115": ResearchItem("115", "Combustion Drive"),
    "117": ResearchItem("117", "Impulse Drive"),
    "118": ResearchItem("118", "Hyperspace Drive"),
    "106": ResearchItem("106", "Espionage Technology"),
    "108": ResearchItem("108", "Computer Technology"),
    "124": ResearchItem("124", "Astro Physics"),
    "123": ResearchItem("123", "Intergalactic Research Network"),
    "199": ResearchItem("199", "Graviton Research"),
    "109": ResearchItem("109", "Weapon Technology"),
    "110": ResearchItem("110", "Shield Technology"),
    "111": ResearchItem("111", "Armour Technology")
}

class ResearchItem(Item): pass

class ResearchData(object):
    def __init__(self, research, level):
        self.research = research
        self.level = level


class Research(Scraper):
    def __init__(self, browser, config):
        super(Research, self).__init__(browser, config)
        self.general_client = General(browser, config)

    @staticmethod
    def parse_research(research):
        planet_research = {}
        count = 0
        for research_type in researchTypes:
            planet_research[research_type] = ResearchItem(research[count][0], research[count][1])
            count += 1
        return planet_research

    def get_research(self, planet):
        self.logger.info('Getting research data for planet %s' % planet.name)
        url = self.url_provider.get_page_url('research', planet)
        res = self.open_url(url)
        soup = BeautifulSoup(res.read(), "lxml")
        research_buttons = soup(attrs={'class': "detail_button"})

        research = []
        for research_button in research_buttons:
            research_data = self.get_research_data_from_button(research_button)
            if research_data is not None:
                research.append(research_data)

        return research

    @staticmethod
    def get_research_data_from_button(research_button):
        """ Read the research data from the research button """

        id = research_button['ref']
        research_data = RESEARCH_DATA.get(id)

        # ensures that execution will not break if there is a new item
        if research_data is not None:
            try:
                research_info = "".join(research_button.find("span", {"class": "level"})
                                        .findAll(text=True, recursive=False)[1])
            # If we get an exception here it means the research is in construction mode, so we
            # the info we need will be at index 0
            except IndexError:
                research_info = "".join(research_button.find("span", {"class": "level"})
                                        .findAll(text=True, recursive=False)[0])

            level = int(re.sub("[^0-9]", "", research_info))
            return ItemAction(ResearchItem(research_data.id, research_data.name), level)
        else:
            return None
