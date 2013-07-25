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

class Effect(object):
    game = None
    phase = None            #override
    @staticmethod
    def register(_game):
        Effect.game = _game
    @staticmethod
    def effect(player):     #override
        pass
class Phase(Effect):
    def __init__(self):
        pass
    @staticmethod
    def priviledge(player):
        print(player)
    def __str__(self):
        return self.__class__.__name__

class Mayor(Phase):
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

class Tile(Effect, object):
    """
    This class represents a tile, such as a Corn square or a Small
    Indigo Plant building.
    """
    n_tiles = 0             # number of starting tiles
    colonists = 1           # max colonists

"""
Resources:
    represents both the tiles and the resource barrels
"""
class Plantation(Tile):
    pass
class Resource(Plantation):
    value = 0               # trading value
    n_goods = 0             # number of starting barrels

class Corn(Resource):
    value = 0
    n_tiles = 10
    n_goods = 10
class Indigo(Resource):
    value = 1
    n_tiles = 12
    n_goods = 11
class Sugar(Resource):
    value = 2
    n_tiles = 11
    n_goods = 11
class Tobacco(Resource):
    value = 3
    n_tiles = 9
    n_goods = 9
class Coffee(Resource):
    value = 4
    n_tiles = 8
    n_goods = 9
class Quarry(Plantation):
    n_tiles = 8            

"""
Buildings:
    Stuff related to buildings
"""
class Building(Tile):
    vp = 0
    size = 1
    cost = 0
    colonists = 1
    n_tiles = 2
    phase = Phase       #phase(s?) which the building impacts
    ##additional bldg specific fields
    #resources = dict()
    #for resource in Resource.__subclasses__():
    #    resources[resource] = 0#don't want to get KeyErrors, so just init all to 0
    def register(_game):
        game = _game
    def effect(player): #effect the building has during its phase
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
    phase = Craftsman
class SmallSugarMill(Building1):
    n_tiles = 3
    cost = 2
    phase = Craftsman
class SmallMarket(Building1):
    cost = 1
    phase = Trader
class Hacienda(Building1):
    cost = 2
    phase = Settler
class ConstructionHut(Building1):
    cost = 2
    phase = Settler
class SmallWarehouse(Building1):
    cost = 3
    phase = Captain
#Row 2    
class LargeIndigoPlant(Building2):
    n_tiles = 3
    cost = 3
    colonists = 3
    phase = Craftsman
class LargeSugarMill(Building2):
    n_tiles = 3
    cost = 4
    colonists = 3
    phase = Craftsman
class Hospice(Building2):
    cost = 4
    phase = Settler
class Office(Building2):
    cost = 5
    phase = Trader
class LargeMarket(Building2):
    cost = 5
    phase = Trader
class LargeWarehouse(Building2):
    cost = 6
    phase = Captain
#Row 3
class TobaccoStorage(Building3):
    n_tiles = 3
    cost = 5
    phase = Craftsman
class CoffeeRoaster(Building3):
    n_tiles = 3
    cost = 6
    phase = Craftsman
class Factory(Building3):
    cost = 7
    phase = Craftsman
class University(Building3):
    cost = 8
    phase = Builder
class Harbor(Building3):
    cost = 8
    phase = Captain
class Wharf(Building3):
    cost = 9
    phase = Captain
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

"""
Shipping stuff
"""
class Ship(object):
    def __init__(self, n):
        self.size = n

class TradingHouse(object):
    resources = {resource : 0 for resource in Resource.__subclasses__()}



class Player(object):
    n_colonists = 0
    unworked_buildings = list()
    worked_buildings = list()
    plantations = Counter()
    n_vp = 0
    def __str__(self):
        return str(
            ("player",
             self.n_colonists,
             self.n_vp)
            )
    def acquire(self, obj):
        pass
    def acquireBuilding(self, building):
        pass
    def acquirePlantation(self, plantation):
        pass

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

        Effect.register(self)
