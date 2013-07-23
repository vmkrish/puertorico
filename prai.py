from collections import Counter
import random
import itertools
import heapq
import copy



MAX_BUILDINGS = 12
MAX_PLANTATIONS = 12
NUM_PLAYERS = 3
BALANCED = False

def eval(state):
	me = 0
	others = []
	for player in state.players:
		points = 0
		points += player.victoryPoints
		for building in player.buildings.keys():
			points += building.victory
		if player.buildings[GuildHall] == 1:
			for building in player.buidlings.keys():
				if building == SmallIndigo:
					points += 1
				elif building == LargeIndigo:
					points += 2
				elif building == SmallSugar:
					points += 1
				elif building == LargeSugar:
					points += 2
				elif building == TobaccoStorage:
					points += 2
				elif building == CoffeeRoaster:
					points += 2
		if player.buildings[Residence] == 1:
			count = 0
			for plantation in player.plantations:
				if plantation[1]:
					count += 1
			if count <= 9:
				points += 4
			elif count == 10:
				points += 5
			elif count == 11:
				points += 6
			elif count == 12:
				points += 7
				
		if player.buildings[Fortress] == 1:
			points += player.colonists / 3
			
		if player.buildings[CustomsHouse] == 1:
			points += player.victoryPoints / 4
			
		if player.buildings[CityHall] == 1:
			for building in player.buidlings.keys():
				if not building == SmallIndigo and not building == LargeIndigo and not building == SmallSugar and not building == LargeSugar and not building == TobaccoStorage and not building == CoffeeRoaster:
					points += 1
		
		points += player.doubloons
		
		points += len(player.buildings.keys()) * 2
		
		points += sum(player.goods.values())
		
		if player.index == state.me:
			me = points
		else:
			others.append(points)
	for i in range(len(others)):
		others[i] = me - others[i]
	return (others, [])
			

class State:
	"""A state of the game"""
	def __init__(self, me):
		self.players = []
		self.currentPlayer = 0
		self.governor = 0
		self.me = me
		for i in range(NUM_PLAYERS):
			self.players.append(Player(i, me))
		self.sharedBoard = SharedBoard()
		self.situation = [None, 0]
		self.captainPointGotten = True
		self.captainLoops = 0
		self.lastTurn = False
		self.gameOver = False
	
	def terminalTest(self):
		return self.gameOver
		
	def canBuild(self, player, building):
		
		if building in player.buildings.keys():
			return False
			
		if self.sharedBoard.leftoverBuildings[building] == 0:
			return False
		
		buildingCount = 0
		for build in player.buildings.keys():
			buildingCount += build.squares
		if building.squares + buildingCount > MAX_BUILDINGS:
			return False	
		
		quarryCount = player.plantations.count([Quarry,True])
		discount = min(quarryCount, building.maxDiscount)
		additional = 0
		if self.currentPlayer == player.index:
			additional = 1
		if discount + additional + player.doubloons >= building.cost:
			return True
		return False
			
	def generateMoves(self):
		if self.situation[0] == None:
			moves = self.sharedBoard.leftoverRoles.keys()
			return moves
					
		elif self.situation[0] == Trader:
			moves = [None]
			for good in self.players[self.situation[1]].goods.keys():
				if self.sharedBoard.canTrade(good, Office in self.players[self.situation[1]].buildings.keys()):
					moves.append(good)
					
		elif self.situation[0] == Captain:
			moves = []
			if not self.players[self.situation[1]].wharfUsed:
				for good in self.players[self.situation[1]].goods.keys():
					moves.append((None, 0, 15), good)
			for good in self.players[self.situation[1]].goods.keys():
				if self.players[self.situation[1]].goods[good] >= 1:
					if self.sharedBoard.canShip(self.sharedBoard.ship4, good):
						moves.append((self.sharedBoard.ship4, good))
					if self.sharedBoard.canShip(self.sharedBoard.ship5, good):
						moves.append((self.sharedBoard.ship5, good))
					if self.sharedBoard.canShip(self.sharedBoard.ship6, good):
						moves.append((self.sharedBoard.ship6, good))
			if len(moves) == 0:
				moves = [None]
				
		elif self.situation[0] == Builder:
			moves = [None]
			for building in self.sharedBoard.leftoverBuildings.keys():
				if self.canBuild(self.players[self.situation[1]], building):
					moves.append(building)
			
		elif self.situation[0] == Settler:
			moves = [(False, None)]
			if len(self.players[self.situation[1]].plantations) == MAX_PLANTATIONS:
				return moves
			if self.players[self.situation[1]].buildings[Hacienda] == 1:
				for plantation in self.sharedBoard.plantations:
					if (True, plantation) not in moves:
						if len(self.players[self.situation[1]].plantations) < MAX_PLANTATIONS - 1:
							moves.append((True, plantation))
						moves.append((False, plantation))
						moves.append((True, None))
				if self.players[self.situation[1]].buildings[ConstructionHut] == 1 or self.situation[1] == self.currentPlayer:
					if self.sharedBoard.quarry > 0:
						moves.append((False, Quarry))
						moves.append((True, Quarry))
					
			else:
				for plantation in self.sharedBoard.plantations:
					if plantation not in moves:
						moves.append((False, plantation))
				if self.players[self.situation[1]].buildings[ConstructionHut] == 1 or self.situation[1] == self.currentPlayer:
					if self.sharedBoard.quarry > 0:
						if self.players[self.situation[1]].buildings[Hacienda] == 1:
							moves.append((True, Quarry))	
						moves.append((False, Quarry))
						
		elif self.situation[0] == Mayor:
			moves = []
			buildingSpaces = 0
			for building in self.players[self.situation[1]].buildings.keys():
				buildingSpaces += building.spaces
			if buildingSpaces + len(self.players[self.situation[1]].plantations) <= self.players[self.situation[1]].colonists:
				move = []
				for building in self.players[self.situation[1]].buildings.keys():
					move.append(building)
				for plantation in  self.players[self.situation[1]].plantations:
					move.append(plantation[0])
				moves.append(move)
				return moves
			indexes = tuple(itertools.combinations(range(buildingSpaces + len(self.players[self.situation[1]].plantations)), self.players[self.situation[1]].colonists))
			for possible in indexes:
				move = []
				for index in possible:
					if index < len(self.players[self.situation[1]].plantations):
						move.append(self.players[self.situation[1]].plantations[index][0])
					else:
						bSpaces = 0
						i = -1
						while bSpaces < index + 1 - len(self.players[self.situation[1]].plantations):
							i += 1
							bSpaces += self.players[self.situation[1]].buildings.keys()[i].spaces
						move.append(self.players[self.situation[1]].buildings.keys()[i])
				moves.append(move)
						
		elif self.situation[0] == Craftsman:
			moves = [None]
			if self.situation[1] == self.currentPlayer:
				for plantation in self.players[self.situation[1]].plantations:
					if plantation[1] == True:
						for building in self.players[self.situation[1]].buildings.keys():
							if building.produceType == plantation[0] and self.players[self.situation[1]].buildings[building] > 0:
								if plantation[0] not in moves:
									if self.leftoverGoods[plantation[0]] > 0:
										moves.append(plantation[0])
								
		else:
			moves = [None]
			if self.players[self.situation[1]].buildings[LargeWarehouse] == 1 and self.players[self.situation[1]].buildings[SmallWarehouse] == 1:
				for good in self.players[self.situation[1]].goods.keys():
					k = self.players[self.situation[1]].goods.keys()
					k.remove(good)
					random.shuffle(k)
					moves.append(tuple(k))
			elif self.players[self.situation[1]].buildings[LargeWarehouse] == 1:
				for good in self.players[self.situation[1]].goods.keys():
					for good2 in self.players[self.situation[1]].goods.keys():
						for good3 in self.players[self.situation[1]].goods.keys():
							if not good == good2 and not good2 == good3 and not good == good3:
								moves.append((good, good2, good3))
			elif self.players[self.situation[1]].buildings[SmallWarehouse] == 1:
				for good in self.players[self.situation[1]].goods.keys():
					for good2 in self.players[self.situation[1]].goods.keys():
						if not good == good2:
							moves.append((good, good2))
			else:	
				for good in self.players[self.situation[1]].goods.keys():
					moves.append([good]) 
				
		return moves
				
		
		
	def playMove(self, move):
		if self.situation[0] == None:
			if move == Trader:
				self.situation[0] = Trader
				self.players[self.situation[1]].doubloons += self.sharedBoard.leftoverRoles[Trader]
				del self.sharedBoard.leftoverRoles[Trader]
			elif move == Captain:
				self.situation[0] = Captain
				self.players[self.situation[1]].doubloons += self.sharedBoard.leftoverRoles[Captain]
				del self.sharedBoard.leftoverRoles[Captain]
				self.captainPointGotten = False
				for player in self.players:
					if player.buildings[Wharf] == 1:
						player.wharfUsed = False
			elif move == Builder:
				self.situation[0] = Builder
				self.players[self.situation[1]].doubloons += self.sharedBoard.leftoverRoles[Builder]
				del self.sharedBoard.leftoverRoles[Builder]
			elif move == Settler:
				self.situation[0] = Settler
				self.players[self.situation[1]].doubloons += self.sharedBoard.leftoverRoles[Settler]
				del self.sharedBoard.leftoverRoles[Settler]
			elif move == Mayor:
				self.situation[0] = Mayor
				self.players[self.situation[1]].doubloons += self.sharedBoard.leftoverRoles[Mayor]
				del self.sharedBoard.leftoverRoles[Mayor]
				self.players[self.situation[1]].colonists += 1
				self.sharedBoard.colonists -= 1
				index = self.situation[1]
				for i in range(self.sharedBoard.colonistShip):
					self.players[index].colonists += 1
					index += 1
					if index == len(self.players):
						index = 0
			elif move == Craftsman:
				self.situation[0] = Craftsman
				self.players[self.situation[1]].doubloons += self.sharedBoard.leftoverRoles[Craftsman]
				del self.sharedBoard.leftoverRoles[Craftsman]
				index = self.situation[1]
				for i in range(len(self.players)):
					self.sharedBoard.takeGoods(self.players[index])
					index += 1
					if index == len(self.players):
						index = 0
			return
		
		if self.situation[0] == Trader:
			if not move == None:
				role = 0
				if self.situation[1] == self.currentPlayer:
					role = 1
				markets = 0
				for building in self.players[self.situation[1]].buildings.keys():
					if building == SmallMarket:
						if self.players[self.situation[1]].buildings[building] == 1:
							markets += 1
					if building == LargeMarket:
						if self.players[self.situation[1]].buildings[building] == 1:
							markets += 2
				goodValue = 0
				if move == Indigo:
					goodValue = 1
				if move == Sugar:
					goodValue = 2
				if move == Tobacco:
					goodValue = 3
				if move == Coffee:
					goodValue = 4
				
				self.players[self.situation[1]].doubloons += goodValue + markets + role
				c = Counter()
				c[move] = 1
				self.players[self.situation[1]].goods -= c
		
		if self.situation[0] == Captain:
			if not move == None:
				captain = 0
				if self.situation[1] == self.currentPlayer and not self.captainPointGotten:
					captain = 1
					self.captainPointGotten = True
				harbor = 0
				if self.players[self.situation[1]].buildings[Harbor] == 1:
					harbor = 1
				goodsShipped = min(self.players[self.situation[1]].goods[move[1]], move[0][2] - move[0][1])
				if move[0][2] == 4:
					self.sharedBoard.ship4[0] = move[1]
					self.sharedBoard.ship4[1] += goodsShipped
				elif move[0][2] == 5:
					self.sharedBoard.ship5[0] = move[1]
					self.sharedBoard.ship5[1] += goodsShipped
				elif move[0][2] == 6:
					self.sharedBoard.ship6[0] = move[1]
					self.sharedBoard.ship6[1] += goodsShipped
				else:
					self.sharedBoard.leftoverGoods[move[1]] += goodsShipped
					self.players[self.situation[1]].wharfUsed = True
				self.players[self.situation[1]].victoryPoints += goodsShipped + harbor + captain
				self.sharedBoard.victoryPoints -= goodsShipped + harbor + captain
				c = Counter()
				c[move[1]] = goodsShipped
				self.players[self.situation[1]].goods -= c
				
		if self.situation[0] == Warehouse:
			if not move == None:
				self.sharedBoard.leftoverGoods[move[0]] += self.players[self.situation[1]].goods[move[0]] - 1
				self.players[self.situation[1]].goods[move[0]] = 1
				for good in self.players[self.situation[1]].goods.keys():
					if not good in move:
						self.sharedBoard.leftoverGoods[good] += self.players[self.situation[1]].goods[good]
						self.players[self.situation[1]].goods[move[0]] = 0
					
				
		if self.situation[0] == Builder:
			if not move == None:
				if self.players[self.situation[1]].buildings[University] == 1:
					self.players[self.situation[1]].buildings[move] = 1
					self.players[self.situation[1]].colonists += 1
					self.sharedBoard.colonists -= 1
				else:
					self.players[self.situation[1]].buildings[move] = 0
					
				self.sharedBoard.leftoverBuildings[move] -= 1
				quarryCount = self.players[self.situation[1]].plantations.count([Quarry,True])
				discount = min(quarryCount, move.maxDiscount)
				additional = 0
				if self.currentPlayer == self.situation[1]:
						additional = 1
				self.players[self.situation[1]].doubloons -= (move.cost - (additional + discount))
				
		if self.situation[0] == Settler:
			if not move == (False, None):
				if move[0]:
					rand = random.randrange(sum(self.sharedBoard.leftoverPlantations.values()))
					chosen = next(itertools.islice(self.sharedBoard.leftoverPlantations.elements(), rand, None))
					self.players[self.situation[1]].plantations.append([chosen, False])
					self.sharedBoard.leftoverPlantations -= Counter({chosen:1})
				if move[1] == Quarry:
					if self.players[self.situation[1]].buildings[Hospice] == 1:
						self.players[self.situation[1]].plantations.append([move[1], True])
						self.players[self.situation[1]].colonists += 1
					else:
						self.players[self.situation[1]].plantations.append([move[1], False])
					self.sharedBoard.quarry -= 1
						
					
				elif not move[1] == None:
					if self.players[self.situation[1]].buildings[Hospice] == 1:
						self.players[self.situation[1]].plantations.append([move[1], True])
						self.players[self.situation[1]].colonists += 1
						self.sharedBoard.colonists -= 1
					else:
						self.players[self.situation[1]].plantations.append([move[1], False])
					self.sharedBoard.plantations.remove(move[1])
					
		if self.situation[0] == Mayor:
			for building in self.players[self.situation[1]].buildings.keys():
				self.players[self.situation[1]].buildings[building] = 0
			for plantation in self.players[self.situation[1]].plantations:
				plantation[1] = False
			for m in move:
				if m in self.players[self.situation[1]].buildings.keys():
					self.players[self.situation[1]].buildings[m] += 1
				else:
					for plantation in self.players[self.situation[1]].plantations:
						if plantation[0] == m and not plantation[1]:
							plantation[1] = True
							break
							
		if self.situation[0] == Craftsman:
			if not move == None:
				self.players[self.situation[1]].goods[move] += 1
				self.sharedBoard.leftoverGoods[move] -= 1
							
							
		self.situation[1] += 1
		if self.situation[1] == len(self.players):
			self.situation[1] = 0
		
		if self.situation[1] == self.currentPlayer:
			if self.situation[0] == Trader:
				if len(self.sharedBoard.tradingHouse) == 4:
					for good in self.sharedBoard.tradingHouse:
						self.leftoverGoods[good] += 1
					self.sharedBoard.tradingHouse = []
				self.situation[0] = None
				self.currentPlayer += 1
				self.situation[1] += 1
				
			elif self.situation[0] == Captain:
				self.captainLoops += 1
				if self.captainLoops == 6:
					if self.sharedBoard.victoryPoints <= 0:
						self.lastTurn = True	
					self.situation[0] = Warehouse
					self.captainLoops = 0
					self.captainPointGotten = True
					for player in self.players:
						player.wharfUsed = True	
						
			elif self.situation[0] == Warehouse:
				self.situation[0] = None
				self.currentPlayer += 1
				self.situation[1] += 1
						
			elif self.situation[0] == Builder:
				self.situation[0] = None
				self.currentPlayer += 1
				for player in self.players:
					squares = 0
					for building in player.buildings:
						squares += building.squares
					if squares == MAX_BUILDINGS:
						self.lastTurn = True
				self.situation[1] += 1
				
				
			elif self.situation[0] == Settler:
				self.situation[0] = None
				self.currentPlayer += 1
				self.plantations = []
				for i in range(len(self.players) + 1):
					rand = random.randrange(sum(self.sharedBoard.leftoverPlantations.values()))
					chosen = next(itertools.islice(self.sharedBoard.leftoverPlantations.elements(), rand, None))
					self.plantations.append(chosen)
					self.sharedBoard.leftoverPlantations -= Counter({chosen:1})
				self.situation[1] += 1
					
			elif self.situation[0] == Mayor:
				colonists = 0
				for player in self.players:
					for building in player.buildings.keys():
						colonists += (building.spaces - player.buildings[building])
				colonists = max(len(self.players), colonists)
				self.sharedBoard.colonistShip = min(colonists, self.sharedBoard.colonists)
				self.sharedBoard.colonists -= self.sharedBoard.colonistShip
				if self.sharedBoard.colonists <= 0 and self.sharedBoard.colonistShip < colonists:
					self.lastTurn = True
				self.situation[0] = None
				self.currentPlayer += 1
				self.situation[1] += 1
			
			elif self.situation[0] == Craftsman:
				self.situation[0] = None
				self.currentPlayer += 1 
				self.situation[1] += 1
			
			if self.situation[1] == len(self.players):
				self.situation[1] = 0
			if self.currentPlayer == len(self.players):
				self.currentPlayer = 0
			
			if self.currentPlayer == self.governor and not self.situation[0] == Captain and not self.situation[0] == Warehouse:
				if self.lastTurn:
					self.gameOver = True
				self.governor += 1
				self.situation[1] += 1
				self.currentPlayer += 1
				for role in self.sharedBoard.leftoverRoles.keys():
					self.sharedBoard.leftoverRoles[role] += 1
				for role in self.sharedBoard.roles:
					if role not in self.sharedBoard.leftoverRoles.keys():
						self.sharedBoard.leftoverRoles[role] = 0
				
				if self.governor == len(self.players):
					self.governor = 0
					self.situation[1] = 0
					self.currentPlayer = 0


class Player:
	"""The state of a player"""
	def __init__(self, index, me):
		self.index = index
		self.me = me
		self.colonists = 0
		self.goods = Counter()
		self.buildings = Counter()
		self.wharfUsed = True
		self.victoryPoints = 0
		if NUM_PLAYERS == 3:
			if index == 0 or index == 1:
				self.plantations = [[Indigo,False]]
				self.doubloons = 2 	
			else:
				self.plantations = [[Corn,False]]
				if not BALANCED:
					self.doubloons = 2
				else:
					self.doubloons = 1 
				

class SharedBoard:
	"""The state of the middle board"""
	def __init__(self):
		if NUM_PLAYERS == 3:
			self.victoryPoints = 75
			self.colonists = 52
			self.colonistShip = 3
			self.roles = (Settler, Mayor, Captain, Builder, Trader, Craftsman)
			self.leftoverRoles = Counter()
			for role in self.roles:
				self.leftoverRoles[role] = 0
			
			self.leftoverPlantations = Counter()
			self.leftoverPlantations[Corn] = 10
			self.leftoverPlantations[Tobacco] = 9
			self.leftoverPlantations[Coffee] = 8
			self.leftoverPlantations[Sugar] = 11
			self.leftoverPlantations[Indigo] = 12
			
			self.quarry = 8
			
			self.leftoverGoods = Counter()
			self.leftoverGoods[Coffee] = 9
			self.leftoverGoods[Tobacco] = 9
			self.leftoverGoods[Sugar] = 11
			self.leftoverGoods[Corn] = 9
			self.leftoverGoods[Indigo] = 9
			
			self.plantations = []
			
			self.ship4 = [None, 0, 4]
			self.ship5 = [None, 0, 5]
			self.ship6 = [None, 0, 6]
			
			self.tradingHouse = []
			
			for i in range(4):
				rand = random.randrange(sum(self.leftoverPlantations.values()))
				chosen = next(itertools.islice(self.leftoverPlantations.elements(), rand, None))
				self.plantations.append(chosen)
				self.leftoverPlantations -= Counter({chosen:1})
		# TODO 2 players
		elif NUM_PLAYERS == 2:
			pass
			
		self.leftoverBuildings = Counter()
		self.leftoverBuildings[SmallIndigo] = 4
		self.leftoverBuildings[LargeIndigo] = 3
		self.leftoverBuildings[SmallSugar] = 4
		self.leftoverBuildings[LargeSugar] = 3
		self.leftoverBuildings[CoffeeRoaster] = 3
		self.leftoverBuildings[TobaccoStorage] = 3
		self.leftoverBuildings[SmallMarket] = 2
		self.leftoverBuildings[Hacienda] = 2
		self.leftoverBuildings[ConstructionHut] = 2
		self.leftoverBuildings[SmallWarehouse] = 2
		self.leftoverBuildings[Hospice] = 2
		self.leftoverBuildings[Office] = 2
		self.leftoverBuildings[LargeMarket] = 2
		self.leftoverBuildings[LargeWarehouse] = 2
		self.leftoverBuildings[Factory] = 2
		self.leftoverBuildings[University] = 2
		self.leftoverBuildings[Harbor] = 2
		self.leftoverBuildings[Wharf] = 2
		self.leftoverBuildings[GuildHall] = 1
		self.leftoverBuildings[Residence] = 1
		self.leftoverBuildings[Fortress] = 1
		self.leftoverBuildings[CustomsHouse] = 1
		self.leftoverBuildings[CityHall] = 1
	
	def canTrade(self, good, office):
		if len(self.tradingHouse) == 4:
			return False
		if good not in self.tradingHouse:
			return True
		elif office:
			if self.tradingHouse.count(good) < 2:
				return True
		return False
		
	def canShip(self, ship, good):
		if ship[0] == None or ship[0] == good:
			return not ship[1] == ship[2]
		return False
		
	def takeGoods(self, player):
		differentTypes = 0		
		good = player.plantations.count([Corn, True])
		good = min(good, self.leftoverGoods[Corn])
		player.goods[Corn] += good
		self.leftoverGoods[Corn] -= good
		if good > 0:
			differentTypes += 1
		for Type in [Indigo, Sugar, Tobacco, Coffee] :
			good = 0
			for building in player.buildings.keys():
				occupied = 0
				if building.produceType == Type:
					occupied += player.buildings[building]			
				good += min(player.plantations.count([Type,True]), occupied)
			good = min(good, self.leftoverGoods[Type])
			player.goods[Type] += good
			self.leftoverGoods[Type] -= good
			if good > 0:
				differentTypes += 1
		if player.buildings[Factory] == 1:
			if differentTypes == 2:
				player.doubloons += 1
			
			elif differentTypes == 3:
				player.doubloons += 2
			
			elif differentTypes == 4:
				player.doubloons += 3	
			
			elif differentTypes == 5:
				player.doubloons += 5
		
					
			
class Settler:
	pass
	
class Mayor:
	pass
	
class Captain:
	pass
	
class Builder:
	pass
	
class Trader:
	pass
	
class Craftsman:
	pass
	
	
class Corn:
	baseValue = 0
	
class Indigo:
	baseValue = 1
	
class Sugar:
	baseValue = 2
	
class Tobacco:
	baseValue = 3
	
class Coffee:
	baseValue = 4
	
class Quarry:
	pass
	

class SmallIndigo:
	spaces = 1
	victory = 1
	cost = 1
	maxDiscount = 1
	squares = 1
	produceType = Indigo
	
class LargeIndigo:
	spaces = 3
	victory = 2
	cost = 3
	maxDiscount = 2
	squares = 1
	produceType = Indigo
	
class SmallSugar:
	spaces = 1
	victory = 1
	cost = 2
	maxDiscount = 1
	squares = 1
	produceType = Sugar
	
class LargeSugar:
	spaces = 3
	victory = 2
	cost = 4
	maxDiscount = 2
	squares = 1
	produceType = Sugar
	
class TobaccoStorage:
	spaces = 3
	victory = 3
	cost = 5
	maxDiscount = 3
	squares = 1
	produceType = Tobacco
	
class CoffeeRoaster:
	spaces = 2
	victory = 3
	cost = 6
	maxDiscount = 3
	squares = 1
	produceType = Coffee
	
class SmallMarket:
	spaces = 1
	victory = 1
	cost = 1
	maxDiscount = 1
	squares = 1
	produceType = None
	
class Hacienda:
	spaces = 1
	victory = 1
	cost = 2
	maxDiscount = 1
	squares = 1
	produceType = None
	
class ConstructionHut:
	spaces = 1
	victory = 1
	cost = 2
	maxDiscount = 1
	squares = 1
	produceType = None

class SmallWarehouse:
	spaces = 1
	victory = 1
	cost = 3
	maxDiscount = 1
	squares = 1
	produceType = None
	
class Hospice:
	spaces = 1
	victory = 2
	cost = 4
	maxDiscount = 2
	squares = 1
	produceType = None
	
class Office:
	spaces = 1
	victory = 2
	cost = 5
	maxDiscount = 2
	squares = 1
	produceType = None
	
class LargeMarket:
	spaces = 1
	victory = 2
	cost = 5
	maxDiscount = 2
	squares = 1 
	produceType = None
	
class LargeWarehouse:
	spaces = 1
	victory = 2
	cost = 6
	maxDiscount = 2
	squares = 1
	produceType = None
	
class Factory:
	spaces = 1
	victory = 3
	if BALANCED:
		cost = 8
	else:
		cost = 7
	maxDiscount = 3
	squares = 1
	produceType = None
	
class University:
	spaces = 1
	victory = 3
	if BALANCED:
		cost = 7
	else:
		cost = 8
	maxDiscount = 3
	squares = 1
	produceType = None

class Harbor:
	spaces = 1
	victory = 3
	cost = 8
	maxDiscount = 3
	squares = 1
	produceType = None
	
class Wharf:
	spaces = 1
	victory = 3
	cost = 9
	maxDiscount = 3
	squares = 1
	produceType = None
	
class GuildHall:
	spaces = 1
	victory = 4
	cost = 10
	maxDiscount = 4
	squares = 2
	produceType = None
	
class Residence:
	spaces = 1
	victory = 4
	cost = 10
	maxDiscount = 4
	squares = 2
	produceType = None
	
class Fortress:
	spaces = 1
	victory = 4
	cost = 10
	maxDiscount = 4
	squares = 2
	produceType = None
	
class CustomsHouse:
	spaces = 1
	victory = 4
	cost = 10
	maxDiscount = 4
	squares = 2
	produceType = None
	
class CityHall:
	spaces = 1
	victory = 4
	cost = 10
	maxDiscount = 4
	squares = 2
	produceType = None
	
class Warehouse:
	pass
		
	
def minimax_value(game, maxply, eval_fn = None):
	"""Find the utility value of the game w.r.t. 'me' player.""" 
	newPly = maxply
	if game.situation[0] == None:
		newPly -= 1
	if newPly == 0 or game.terminalTest():
		return eval_fn(game)
		
	# If you need to speed things up
	"""if min(eval_fn(game)) < -4:
		return (-99, -99)"""

	whichIndex = 0
	if not game.me == game.situation[1]:
		if game.situation[1] > game.me:
			whichIndex = game.situation[1] - 1

	bestVal = -999999999
	bestMoves = []
	bestMove = 0
	bestMoveScores = []
	# try each move
	for move in game.generateMoves():
		g = copy.deepcopy(game)
		earlierSituation = g.situation[1]
		g.playMove(move)
		tempBest = minimax_value(g, newPly, eval_fn)
		vals = tempBest[0]
		tempBest = tempBest[1]
		if g.me == earlierSituation:
			if min(vals) > bestVal:
				bestVal = min(vals)
				bestMove = move
				bestMoveScores = vals
				bestMoves = tempBest
		else:
			goAfterMe = True
			for val in vals:
				if val < 0:
					goAfterMe = False
					break
			if goAfterMe:
				if -1 * vals[whichIndex] > bestVal:
					bestVal = -1 * vals[whichIndex]
					bestMove = move
					bestMoveScores = vals
					bestMoves = tempBest
			else:
				if min(vals)  == vals[whichIndex]:
					if  min([heapq.nsmallest(2, vals)[1] - vals[whichIndex], -1 * vals[whichIndex]]) > bestVal:
						bestVal = vals[whichIndex] - heapq.nsmallest(2, vals)[1]
						bestMove = move
						bestMoveScores = vals
						bestMoves = tempBest
				else:
					if min(vals) - vals[whichIndex] > bestVal:
						bestVal = min(vals) - vals[whichIndex]
						bestMove = move
						bestMoveScores = vals
						bestMoves = tempBest
	bestMoves.append(bestMove)					
	return (bestMoveScores, bestMoves)

s = State(0)
for move in s.generateMoves():
	g = copy.deepcopy(s)
	g.playMove(move)
	print minimax_value(g, 3, eval)
	print move