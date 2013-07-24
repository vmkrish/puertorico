from __future__ import print_function
from __future__ import division

from random import shuffle
from collections import Counter

"""
static methods: annotate with @staticmethod or say
def f():
    ...
f = staticmethod(f)


Could have a "workable" class with n_colonists_working
"""

class Tile(object):
    """
    This class represents a tile, such as a Corn square or a Small
    Indigo Plant building.
    """
    n_tiles = 0

class Plantation(Tile):
    pass

class Resource(Plantation):
    value = 0

class Phase(object):
    def __init__(self):
        pass
    @staticmethod
    def priviledge(player):
        print(player)

class Player(object):
    n_colonists = 0
    buildings = list()
    plantations = list()
    n_vp = 0
    def __repr__(self):
        return str(
            ("player",
             self.n_colonists,
             self.n_vp)
            )
            

class Building(Tile):
    #base fields
    vp = 0
    size = 1
    cost = 0
    colonists = 1
    n_tiles = 2
    #additional bldg specific fields
    resources = dict()
    for resource in Resource.__subclasses__():
        resources[resource] = 0#don't want to get KeyErrors, so just init all to 0

class Ship(object):
    def __init__(self, n):
        self.size = n

class TradingHouse(object):
    resources = {resource : 0 for resource in Resource.__subclasses__()}

class Corn(Resource):
    value = 0
    n_tiles = 10
class Indigo(Resource):
    value = 1
    n_tiles = 12
class Sugar(Resource):
    value = 2
    n_tiles = 11
class Tobacco(Resource):
    value = 3
    n_tiles = 9
class Coffee(Resource):
    value = 4
    n_tiles = 8
class Quarry(Plantation):
    """
    need to fix this:
    want Plantation
            Resource
                Corn, Indigo, Sugar, Tobacco, Coffee
            Quarry
    """
    n_tiles = 8

class Mayor(Phase):
    def __repr__(self):
        return "Mayor"
    pass
class Settler(Phase):
    pass
class Trader(Phase):
    pass
class Captain(Phase):
    pass
class Craftsman(Phase):
    pass
class Builder(Phase):
    pass
class Prospector(Phase):
    pass

class Building1(Building):
    vp = 1
class Building2(Building):
    vp = 2
class Building3(Building):
    vp = 3
class Building4(Building):
    size = 2
    vp = 4
    cost = 10
    n_tiles = 1
#Row 1
class SmallIndigoPlant(Building1):
    n_tiles = 4
    cost = 1
class SmallSugarMill(Building1):
    n_tiles = 3
    cost = 2
class SmallMarket(Building1):
    cost = 1
class Hacienda(Building1):
    cost = 2
class ConstructionHut(Building1):
    cost = 2
class SmallWarehouse(Building1):
    cost = 3
#Row 2    
class LargeIndigoPlant(Building2):
    n_tiles = 3
    cost = 3
    colonists = 3
class LargeSugarMill(Building2):
    n_tiles = 3
    cost = 4
    colonists = 3
class Hospice(Building2):
    cost = 4
class Office(Building2):
    cost = 5
class LargeMarket(Building2):
    cost = 5
class LargeWarehouse(Building2):
    cost = 6
#Row 3
class TobaccoStorage(Building3):
    n_tiles = 3
    cost = 5
class CoffeeRoaster(Building3):
    n_tiles = 3
    cost = 6
class Factory(Building3):
    cost = 7
class University(Building3):
    cost = 8
class Harbor(Building3):
    cost = 8
class Wharf(Building3):
    cost = 9
#Row 4    
class GuildHall(Building4):
    pass
class Residence(Building4):
    pass
class Fortress(Building4):
    pass
class CustomsHouse(Building4):
    pass
class CityHall(Building4):
    pass

class BuildingList(object):
    buildings = []
    def add(self, building):
        self.buildings.append(building)
    def get_vp(self):
        return sum(building.cost for building in self.buildings)
    def get_size(self):
        return sum(building.size for building in self.buildings)

class Players(object):
    def __init__(self, n):
        self.players = [Player() for i in range(0, n)]
class Buildings(object):
    def __init__(self):
        buildings_map = {building : building.n_tiles for building in
                          [bldg for bldg_t in Building.__subclasses__()
                           for bldg in bldg_t.__subclasses__()]}
        self.buildings = Counter(buildings_map)
    def buy(self, player, building):
        pass
class Resources(object):
    def __init__(self, n):
        self.n = n
        self.pile = [resource for resource_t in Resource.__subclasses__()
                     for resource in [resource_t]*resource_t.n_tiles]
        shuffle(self.pile)
        self.new_stack()
        self.quarries = Counter([Quarry() for i in range(0, 8)])
    def new_stack(self):
        #need to check that there's enough resources left
        stack_list = [self.pile.pop() for i in range(0, self.n+1)]
        self.stack = Counter(stack_list)
    def take(self, resource):
        pass
class Phases(object):
    def __init__(self, n):
        self.phases = {phase : 1 for phase in Phase.__subclasses__()}
class Ships(object):
    def __init__(self, n):
        self.ships = [Ship(i) for i in range(n+1, n+4)]
        


class Game(object):
    def __init__(self, n):
        self.players = Players(n)
        self.resources = Resources(n)
        self.phases = Phases(n)
        self.buildings = Buildings()
        self.ships = Ships(n)
        
        self.govenor = 0
