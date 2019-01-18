import gym
from gym import Env
from .Cards import *

class BatailleCorseEnv(Env):
	# Set this in SOME subclasses
	metadata = {'render.modes': ['human']}
	reward_range = (-float('inf'), float('inf'))
	spec = None

	# Set these in ALL subclasses
	action_space = ['Beat','Play','Pass']
	observation_space = None
	
	def __init__(self, playersNumber=2):
		self.round = 0 # Indice du joueur courant
		self.playersNumber = playersNumber
		
		self.deck = Deck() # Jeu complet
		self.decks = None  # Jeux distribués aux joueurs
		
		self.played_cards = Deck(fill=False) # Cartes dans le pli courant
		self.lost_cards = Deck(fill=False)   # Cartes perdus pour pénalité
		
		self.lets_chance = True # True si on doit laisser une chance de taper à l'agent et False sinon
		
	def print_observation(observation):
		print("Round : ",observation['round'])	
		observation['played_cards'].print()
		observation['lost_cards'].print()
		
	def compute_observation(self): 
		observation = {	'round' : self.round,
						'played_cards': self.played_cards,
						'lost_cards': self.lost_cards}
		return observation				
		
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
		
		if action is in action_space:
			if action == 'Beat':
				# Verification de frappe
				if need_to_beat():
					reward = 0
					done = False
				else:
					reward = -1
					done = False
					
				return self.compute_observation(),reward,done,info
				
			elif action == 'Play':
				
				
			elif action == 'Pass':
				reward = 0
				done = False
				return self.compute_observation(),reward,done,info
			
		else:
			print("Erreur : Action inconnue !")
		
	def reset(self):
		"""Resets the state of the environment and returns an initial observation.
		Returns: observation (object): the initial observation of the
			space.
		"""
		self.round = 0
		
		# Distribution des cartes
		self.deck.shuffle()
		self.decks = self.deck.distributed(self.playersNumber)
		
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
			obersvation = self.compute_observation()
			print_observation(observation)
		else:
			raise NotImplementedError

	def seed(self, seed=None):
		"""Sets the seed for this env's random number generator(s).
		Note:
			Some environments use multiple pseudorandom number generators.
			We want to capture all such seeds used in order to ensure that
			there aren't accidental correlations between multiple generators.
		Returns:
			list<bigint>: Returns the list of seeds used in this env's random
				number generators. The first value in the list should be the
				"main" seed, or the value which a reproducer should pass to
				'seed'. Often, the main seed equals the provided 'seed', but
				this won't be true if seed=None, for example.
		"""
		logger.warn("Could not seed environment %s", self)
		return

	def __str__(self):
		if self.spec is None:
			return '<{} instance>'.format(type(self).__name__)
		else:
			return '<{}<{}>>'.format(type(self).__name__, self.spec.id)
