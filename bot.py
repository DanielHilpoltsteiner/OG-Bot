from authentication import AuthenticationProvider
import logging
import general
import defense
import buildings
import hangar
import fleet
import galaxy
import messages
import datetime
import time

class OgameBot:

    def __init__(self, username, password, universe, target_planet_name):
        self.universe = universe
        self.browser = AuthenticationProvider(username, password, universe).get_browser();
        self.general_client = general.General(self.browser, self.universe)
        self.defense_client = defense.Defense(self.browser, self.universe)
        self.hangar_client = hangar.Hangar(self.browser, self.universe)
        self.fleet_client = fleet.Fleet(self.browser, self.universe)
        self.buildings_client = buildings.Buildings(self.browser, self.universe)
        self.logger = logging.getLogger('ogame-bot')
        self.target_planet_name = target_planet_name
        self.planets = self.general_client.get_planets()
        self.galaxy_client = galaxy.Galaxy(self.browser, self.universe)
        self.messages_client = messages.Messages(self.browser, self.universe)

    # Bot functions
    def auto_build_defenses(self):
        planets = self.planets
        for planet in planets:
            self.defense_client.auto_build_defenses(planet)

    def auto_build_defenses_to_planet(self):
        target_planet = self.get_target_planet()
        self.defense_client.auto_build_defenses(target_planet)

    def transport_resources_to_planet(self):
        planets = self.planets
        target_planet = self.get_target_planet()
        self.logger.info("Main planet found: %s"  % target_planet)
        for planet in [planet for planet in planets if planet != target_planet]:
            resources = general.Resources(1000000, 1000000, 0)
            self.fleet_client.transport_resources(planet, target_planet, resources)

    def auto_build_structure_to_planet(self):
        target_planet = self.get_target_planet()
        self.buildings_client.auto_build_structure(target_planet)


    def auto_build_structures(self):
        for planet in self.planets:
            self.buildings_client.auto_build_structure(planet)

    def spy_nearest_planets(self):
        target_planet = self.get_target_planet()
        planets = self.get_nearest_planets(10)

        for planet in planets:
            self.fleet_client.spy_planet(target_planet, planet)

    def spy_nearest_inactive_planets(self):
        target_planet = self.get_target_planet()
        planets = self.get_nearest_inactive_planets(10)

        for planet in planets:
            self.fleet_client.spy_planet(target_planet, planet)

    def attack_inactive_planets_from_spy_reports(self):
        origin_planet = self.get_target_planet()
        game_date = self.general_client.get_game_datetime()
        reports = self.get_spy_reports()

        self.logger.info("Got %d reports" % len(reports))

        inactive_planets = [ report for report
                                    in reports
                                    # Get reports from inactive players only
                                    if report.player_state == galaxy.PlayerState.Inactive
                                    # Get reports from last 2 minutes
                                    and report.report_datetime >= (game_date - datetime.timedelta(minutes=2))]

        if len(inactive_planets) == 0:
            self.logger.info("There isn't any recent spy reports of inactive players")
            return False
        else:
            self.logger.info("Found %d recent spy reports of inactive players" % len(inactive_planets))

        targets = sorted(inactive_planets, key=self.get_target_value, reverse=True)

        for target in targets:
            if target.defenses == 0:
                self.attack_inactive_planet(origin_planet, target)
        return True

    def auto_attack_inactive_planets(self):
        result = self.attack_inactive_planets_from_spy_reports()
        if result == False:
            self.logger.info("Senting Spy Probes")
            self.spy_nearest_inactive_planets()
            self.logger.info("Waiting for probes to return")
            time.sleep(60)
            self.attack_inactive_planets_from_spy_reports()


    def attack_inactive_planet(self, origin_planet, target_planet):
        self.fleet_client.attack_inactive_planet(origin_planet, target_planet)

    # Logging functions
    def log_planets(self):
        planets = self.planets
        self.logger.info("Logging planets")
        for planet in planets:
            self.logger.info(planet)

    def log_defenses(self):
        planets = self.planets
        self.logger.info("Logging defenses")
        for planet in planets:
            self.logger.info(self.defense_client.get_defenses(planet))

    def log_ships(self):
        planets = self.planets
        for planet in planets:
            ships = self.hangar_client.get_ships(planet)
            self.logger.info("Logging ships for planet %s:" % planet.name)
            for ship in ships:
                self.logger.info(ship)

    def log_overview(self):
        results = []
        for planet in self.planets:
            resources = self.general_client.get_resources(planet)
            results.append((planet, resources))
        for res in results:
            self.logger.info("Planet %s:", res[0])
            self.logger.info("Resources: [%s]", res[1])

    def log_planets_in_same_system(self):
        planets = self.get_planets_in_same_ss()
        for planet in planets:
            self.logger.info(planet)

    def log_nearest_planets(self):
        planets = self.get_nearest_planets(50)
        for planet in planets:
            self.logger.info(planet)

    def log_nearest_inactive_planets(self):
        planets = self.get_nearest_inactive_planets(50)
        for planet in planets:
            self.logger.info(planet)

    def log_spy_reports(self):
        spy_reports = self.get_spy_reports()
        for spy_report in spy_reports:
            self.logger.info("Date:%s - %s" % (spy_report.report_datetime, spy_report))

    def log_game_datetime(self):
        time = self.general_client.get_game_datetime()
        # test = time - datetime.timedelta(minutes=10)
        # self.logger.info(test)
        self.logger.info(datetime)

    # Util functions
    def get_target_planet(self):
        planets = self.planets
        if self.target_planet_name == None:
            return planets[0]
        target_planet = [planet for planet
                                in planets
                                if planet.name.lower() == self.target_planet_name.lower()][0]
        return target_planet

    def get_planets_in_same_system(self):
        target_planet = self.get_target_planet()
        planets = self.galaxy_client.get_planets(target_planet.coordinates.split(':')[0], target_planet.coordinates.split(':')[1])
        return planets

    def get_nearest_planets(self, systems_count):
        target_planet = self.get_target_planet()
        planets = []
        galaxy = target_planet.coordinates.split(':')[0]
        system =  target_planet.coordinates.split(':')[1]
        for i in range(systems_count):
            target_previous_system = str(int(system) - i)
            target_later_system = str(int(system) + i)
            previous_planets = self.galaxy_client.get_planets(galaxy, target_previous_system)
            later_planets = self.galaxy_client.get_planets(galaxy, target_later_system)
            planets.extend(previous_planets)
            planets.extend(later_planets)
        return planets

    def get_nearest_inactive_planets(self, systems_count):
        planets = [planet for planet
                          in self.get_nearest_planets(systems_count)
                          if planet.player_state == galaxy.PlayerState.Inactive]
        return planets

    def get_spy_reports(self):
        """Get spy reports from the messages"""
        spy_reports = self.messages_client.get_spy_reports()
        return spy_reports

    def get_target_value(self, target):
        """Get the value of a target by its resources"""
        return target.resources.total() * target.loot

    def log_index_page(self):
        """Log the index page"""
        self.general_client.log_index_page()
