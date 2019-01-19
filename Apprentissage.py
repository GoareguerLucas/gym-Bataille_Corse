import gym
import random
import matplotlib.pyplot as plt
from gym_bataille_corse.envs.Agent import *
from gym_bataille_corse.envs import *

def info_print(info):
	
	print("Longueur des decks : ")
	for i,deck in enumerate(info["len_decks"]):
		print("Joueur(",i,") ",deck)
	
	print("Played cards ",info["len_played_cards"])
	print("Lost cards ",info["len_lost_cards"])
	
	print('LH Value ',info["last_head_value"])
	print('LH Position ',info["last_head_position"])
	print('LH Player ',info["last_head_player"])
	
	print()

def winner(info):
	"""
	Détermine qui a gagner et retourne sont indice
	"""
	for i,deck in enumerate(info["len_decks"]):
		if deck > 0:
			#print("Le gagnant est le joueur",i)
			return i
	
	print("Erreur : Personne n'a gagner")
	exit(0)

action_space = ['Beat','Play','Pass']
playersNumber = 2

# Déclaration de l'environement
env = gym.make('bataille_corse-v0')
env.__init__(playersNumber)

# Déclaration de l'agent
agent = AgentSimple(action_space)
print("Taille du dictionnaire :",len(agent.q))

# Courbes
etapes = list()
agent_winner = list()
somme = 0
somme_etapes = 0

for i_episode in range(1000):
	observation = env.reset()
	t = 0
	while True: # Non déterministe
		#action = input()
		state1 = agent.observation_reduce(observation) # Reduction de l'observation1
		action = agent.choose_action(state1) # Choix de l'action
		
		observation, reward, done, info = env.step(action) # Application de l'action
		
		state2 = agent.observation_reduce(observation) # Reduction de l'observation2
		agent.learn(state1,action,state2,reward) # Apprentissage
		
		#print("Action :",action,"Reward :",reward)
		#env.render()
		#info_print(info)
		#print("State1 :",state1)
		#print("State2 :",state2)
		
		if done:
			#print("Episode finished after {} timesteps".format(t+1))
			somme_etapes += t+1
			break
		t += 1
	if winner(info) == 0: # Si l'agent a gagner
		somme+=1
	
	if i_episode%50 == 0:
		etapes.append(somme_etapes/50)
		agent_winner.append(somme/50)
		somme = 0
		somme_etapes = 0
		
	if i_episode%100 == 0:
		print("Episode ",i_episode)
		print("Taille du dictionnaire :",len(agent.q))
		
# Courbe du nombres d'étapes par partie	
plt.plot(etapes)
plt.show()

# Courbe du nombre de victoire de l'agent toute les 10 parties
plt.plot(agent_winner)
plt.show()
