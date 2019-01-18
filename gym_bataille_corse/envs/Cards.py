import random

values = range(1,14)
suits = ['Ca','Co','Pi','Tr']

class Card():
	"""
	value in [1-13]
	string est une chaine de caractère qui corespond à value
	suit in ['Ca','Co','Pi','Tr']
	"""
	def __init__(self,value,suit):
		self.value = value
		self.suit = suit
		
		if value == 11:
			self.string = "V"
		elif value == 12:
			self.string = "Q"
		elif value == 13:
			self.string = "K"
		elif value == 1:
			self.string = "A"
		elif value > 1 and value < 11:
			self.string = str(value)
		else:
			self.string = "Error"
			print("Valeur de la carte invalide !")
			
		if suit not in suits:
			self.suit = "Error"
			print("Couleur de la carte invalide !")
			
	def __str__(self):
		return self.string +"-"+ self.suit
	
class Deck():
	"""
	Le deck est un ensemble de cards
	Le dessus du packet est le dernier indice de self.deck et inverssement
	"""
	def __init__(self,fill=True):
		self.cards = list()
		
		if fill:
			for suit in suits:
				for value in values:
					self.cards.append(Card(value,suit))
	
	def add_card_above(self,card):
		"""
		Ajoute card en dernière position de self.deck
		"""
		self.cards.append(card)
		
	def add_deck_below(self,deck):
		"""
		Ajoute deck au début de self.deck
		"""
		deck.cards.extend(self.cards)
		self.cards = deck.cards
		deck.cards = list()
		
	def get_card(self):
		"""
		Renvoie et retire la carte au sommet du deck
		"""
		if self.len() == 0:
			print("Le deck est vide ! Impossible de prendre une carte.")
			return None
		
		card = self.cards[-1]
		del self.cards[-1]
		
		return card
		
	def shuffle(self):
		random.shuffle(self.cards)
	
	def distributed(self,nb_players):
		"""
		Renvoie nb_players decks en utilisant toutes les cartes du deck
		"""
		decks = list()
		for player in range(nb_players):
			decks.append(Deck(fill=False))
			
		current = 0
		for card in range(52):
			decks[current%nb_players].cards.append(self.cards[card])
			current+=1
			
		return decks
	
	def len(self):
		return len(self.cards)
	
	def print(self):
		"""
		Affiche les cartes du deck de la dernière à la première
		"""
		for card in self.cards:
			print(card.__str__())
		print()
			
deck = Deck(fill=False)
print(deck.len())

card = Card(10,'Ca')

deck.add_card_above(card)

deck.print()
