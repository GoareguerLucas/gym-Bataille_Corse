import gym
from gym import Env
from .Card import *
import numpy as np

class BatailleCorseEnv(Env):
	# Set this in SOME subclasses
	metadata = {'render.modes': ['human']}
	reward_range = (-float('inf'), float('inf'))
	spec = None

	# Set these in ALL subclasses
	action_space = ['Beat','Play','Pass']
	observation_space = None
	
	def __init__(self, playersNumber=2):
		self.round = 0 # Indice du joueur courant, l'agent a l'indice 0
		self.playersNumber = playersNumber
		
		self.deck = Deck() # Jeu complet
		self.decks = None  # Jeux distribués aux joueurs
		self.know_cards = np.zeros(playersNumber) # Nombre de cartes ayant été vues par tous dans les decks de chaque joueur
		
		self.played_cards = Deck(fill=False) # Cartes dans le pli courant
		self.lost_cards = Deck(fill=False)   # Cartes perdus pour pénalité
		
		self.lets_chance = True # True si on doit laisser une chance de taper à l'agent et False sinon
		
		# Information sur la dernière tête jouer
		self.last_head_value = None
		self.last_head_position = None # Position part rapport au sommet du tas (self.played_card), de 0(sommet) à 4
		self.last_head_player = None # Indice du joueur ayant poser la tête
		
	def print_observation(self,observation):
		print("Round : ",observation['round'])	
		print("Cartes jouées : ")	
		observation['played_cards'].print()
		print("Cartes perdues : ")
		observation['lost_cards'].print()
		
		for i in range(self.playersNumber): # Affichage des cartes connues 
			name = "cards player"+str(i)
			print("Cartes connus du joueur",i," :")
			observation[name].print()
		
	def compute_observation(self):
		observation = {	'round' : self.round,
						'played_cards': self.played_cards,
						'lost_cards': self.lost_cards}
		
		#know_cards = list()
		for i,deck in enumerate(self.decks): # Réccupération des cartes connues
			knows = deck.view_cards(int(self.know_cards[i]))
			#know_cards.append(cards)
			name = "cards player"+str(i)
			observation[name] = knows

		return observation				
	
	def compute_info(self):
		len_decks = list()
		for deck in self.decks:
			len_decks.append(deck.len())
		
		info = {'len_decks' : len_decks,
				'len_played_cards': self.played_cards.len(),
				'len_lost_cards': self.lost_cards.len(),
				'last_head_value': self.last_head_value,
				'last_head_position': self.last_head_position,
				'last_head_player': self.last_head_player}	
		return info	
	
	def need_to_take(self):
		"""
		Retourne True si self.played_cards contient une tête gagnante
		Retourne False sinon
		"""
		position = self.last_head_position
		value = self.last_head_value
		
		if position == 1 and value == 11: # Valet gagnant
			return True
		if position == 2 and value == 12: # Dame gagnant
			return True
		if position == 3 and value == 13: # Roi gagnant
			return True
		if position == 4 and value == 1: # As gagnant
			return True
			
		return False
		
	def need_to_beat(self):
		"""
		Retourne True si self.played_cards contient une suite de carte qui nécessite de taper
		Retourne False sinon
		"""
		# Observation des trois dernière cartes jouées 
		if self.played_cards.len() >= 1:
			first = self.played_cards.cards[-1].value
			if first == 10:# Pour un 10
				return True
				
			if self.played_cards.len() >= 2:
				seconde = self.played_cards.cards[-2].value
				if first == seconde: # Pour un double
					return True
				if first+seconde == 10: # Pour une addition de 10
					return True
				
				if self.played_cards.len() >= 3:
					third = self.played_cards.cards[-3].value
					if first == third: # Pour un sandwish
						return True
		return False
			
	def play(self,agent=False):
		"""
		Fait jouer le joueur dont c'est le tour, si c'est l'agent alors agent
		doit être égale à True sinon personne ne joue.
		Met à jour self.round et les infos de la dernière tête.
		Retourne True si la partie est fini et False sinon.
		"""
		#print("Round in:",self.round)
		# Recherche du joueur qui doit jouer et à qui il reste des cartes
		while self.decks[self.round].len() == 0:
			self.round = (self.round + 1) % self.playersNumber
		
		if self.round != 0 or agent:
			card = self.decks[self.round].get_card() # Prend une de ses cartes
			
			"""print("Value :")
			value = input()
			card = Card(int(value),'Ca')"""
			
			self.played_cards.add_card_above(card) # Joue la carte
			
			#print("Card played :",card.__str__(),"by",self.round)
			
			# Mise à jour des infos de la dernière tête
			if card.value > 10 or card.value == 1: # Si la carte jouée est une tête
				self.last_head_value = card.value
				self.last_head_position = 0
				self.last_head_player = self.round
			elif self.last_head_position != None: # Si une tête a déjà était posée
				self.last_head_position += 1
				
			# Mise à jour du tour de jeu
			if card.value > 10 or card.value == 1 or self.last_head_value == None: # Si la carte jouée est une tête ou qu'il n'y a pas eu de tête avant
				self.round = (self.round + 1) % self.playersNumber
				while self.decks[self.round].len() == 0: # Le tour passe au prochain joueur qui a des cartes
					self.round = (self.round + 1) % self.playersNumber
			elif self.need_to_take(): # La carte posée n'est pas une tête et une tête a déjà était posée
				self.round = self.last_head_player # Le tour pase a celui qui peut prendre
			
			#print("Round out:",self.round)
			
		return self.end_game()	
		
	def end_game(self):
		"""
		Retourne True si la partie est fini et False sinon
		La partie est fini quand il n'y a plus qu'un joueur qui a des cartes,
		si une tête est en jeu elle appartient a ce joueur et que l'ont 
		ne peut ni taper ni prendre le tas.
		"""
		if self.need_to_beat() or self.need_to_take(): # Rien à taper et aucune tête gagnante
			return False
		
		have_cards = 0 # Nombre de joueur à qui il reste des cartes
		for deck in self.decks:
			if deck.len() != 0:
				have_cards+=1
		if have_cards != 1:
			return False
		
		if self.last_head_player != None and self.decks[self.last_head_player].len() == 0: # Si une tête est en jeu et elle n'appartient pas au joueur à qui il reste des cartes
			return False
			
		return True
		
	def take(self,player):
		"""
		Le joueur d'indice player réccupére dans sont deck les cartes 
		des decks played_cards et lost_cards
		"""
		# Mise à jour du nombre de cartes connus
		nb_card = self.played_cards.len() + self.lost_cards.len()
		self.know_cards[player] += nb_card
		
		# Reccupération des cartes
		self.decks[player].add_deck_below(self.played_cards)
		self.decks[player].add_deck_below(self.lost_cards)
		
		# Reset des infos sur la dernière tête
		self.last_head_value = None
		self.last_head_position = None
		self.last_head_player = None
		
		# Mise à jour du tour de jeu
		self.round = player
		#print("Round take:",self.round)
	
	def beat(self,player):
		"""
		Retourne True si la partie est fini et False sinon
		Fait taper le player et le fait jouer si ce n'est pas la fin de la partie
		"""
		self.take(player)
		if self.end_game():
			return True
		else:
			return self.play()
		
	
	def step(self, action):
		"""Run one timestep of the environment's dynamics. When end of
		episode is reached, you are responsible for calling `reset()`
		to reset this environment's state.
		Accepts an action and returns a tuple (observation, reward, done, info).
		Args:
			action (object): an action provided by the environment
		Returns:
			observation (object): agent's observation of the current environment
			reward (float) : amount of reward returned after previous action
			done (boolean): whether the episode has ended, in which case further step() calls will return undefined results
			info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)
		"""
		info = None
		done = False
		
		need_beat = self.need_to_beat()
		need_take = self.need_to_take()
		
		if action == 'Beat':
			if need_beat or (need_take and self.last_head_player == 0): # Si il faut taper ou que l'agent doit prendre
				reward = self.played_cards.len() + self.lost_cards.len()
				self.take(0)
				done = self.end_game()
			else: # Penalité
				if self.decks[0].len() > 0: # Il a encore des cartes
					card = self.decks[0].get_card() # Il pause une carte
					self.lost_cards.add_card_above(card) 
					reward = -1
					done = self.end_game()
				else: # Il n'a plus de cartes
					reward = 0
					
				if need_take:
					self.take(self.last_head_player)
					done = self.end_game()
				if (self.round != 0 or self.decks[0].len() == 0) and not done: # Ce n'est pas la fin et ce n'est pas a l'agent de jouer
					done = self.play()
			
		elif action == 'Play':
			if self.round == 0: # C'est le tour de l'agent 
				if need_take:
					if self.last_head_player == 0:
						reward = self.played_cards.len() + self.lost_cards.len()
						self.take(self.last_head_player)
						done = self.end_game()
					else:
						print("Erreur : Quelqu'un d'autreque l'agent doit prendre mais c'est le tour de l'agent.")
						exit()
				else:	
					done = self.play(agent = True)
					reward = -1
			else: # Penalité
				if self.decks[0].len() > 0: # Il a encore des cartes
					card = self.decks[0].get_card() # Il pause une carte
					self.lost_cards.add_card_above(card) 
					reward = -1
					done = self.end_game()
					
				else: # Il n'a plus de cartes
					reward = 0
					
				if need_beat: # Si on peut taper
					winner = random.choice(range(1,self.playersNumber))
					done = self.beat(winner)
				elif self.need_to_take():
					if self.last_head_player == 0: # Si l'agent doit prendre
						reward += self.played_cards.len() + self.lost_cards.len()
					self.take(self.last_head_player)
					done = self.end_game()
					
				if not done: # Si ce n'est pas la fin 
					done = self.play()
				
		elif action == 'Pass':
			reward = 0
			if need_beat: # Si il faut taper
				winner = random.choice(range(1,self.playersNumber))
				self.take(winner)
				if self.end_game():
					done = True
				else:
					done = self.play()
			elif need_take:
				if self.last_head_player == 0: # Si l'agent doit prendre
					reward = self.played_cards.len() + self.lost_cards.len()
					
				self.take(self.last_head_player)	
				done = self.end_game()
			elif self.round != 0: # Ce n'est pas le tour de l'agent
				done = self.play()
				
		else:
			print("Erreur : Action inconnue !")
			exit(0)
			
		observation = self.compute_observation()
		
		info = self.compute_info()
		
		return observation, reward, done, info
		
	def reset(self):
		"""Resets the state of the environment and returns an initial observation.
		Returns: observation (object): the initial observation of the
			space.
		"""
		self.round = 0
		
		# Distribution des cartes
		self.deck.shuffle()
		self.decks = self.deck.distributed(self.playersNumber)
		self.know_cards = np.zeros(self.playersNumber)
		
		# Reset des decks centraux
		self.played_cards = Deck(fill=False)
		self.lost_cards = Deck(fill=False)
		
		self.lets_chance = True
		
		return self.compute_observation()

	def render(self, mode='human'):
		"""Renders the environment.
		The set of supported modes varies per environment. (And some
		environments do not support rendering at all.) By convention,
		if mode is:
		- human: render to the current display or terminal and
			return nothing. Usually for human consumption.
		- rgb_array: Return an numpy.ndarray with shape (x, y, 3),
			representing RGB values for an x-by-y pixel image, suitable
			for turning into a video.
		- ansi: Return a string (str) or StringIO.StringIO containing a
			terminal-style text representation. The text can include newlines
			and ANSI escape sequences (e.g. for colors).
		Note:
			Make sure that your class's metadata 'render.modes' key includes
				the list of supported modes. It's recommended to call super()
				in implementations to use the functionality of this method.
		Args:
			mode (str): the mode to render with
			close (bool): close all open renderings
		Example:
		class MyEnv(Env):
			metadata = {'render.modes': ['human', 'rgb_array']}
			def render(self, mode='human'):
				if mode == 'rgb_array':
					return np.array(...) # return RGB frame suitable for video
				elif mode is 'human':
					... # pop up a window and render
				else:
					super(MyEnv, self).render(mode=mode) # just raise an exception
		"""
		if mode is 'human':
			observation = self.compute_observation()
			self.print_observation(observation)
		else:
			raise NotImplementedError
