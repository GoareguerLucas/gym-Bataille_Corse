import gym
import random
from gym_bataille_corse.envs import *

playersNumber = 2

# Test de l'environement
env = gym.make('bataille_corse-v0')
env.__init__(playersNumber)

for i_episode in range(20):
    observation = env.reset()
    for t in range(100):
        env.render()
        print_observation(observation)
        action = random.choice(env.action_space)
        #observation, reward, done, info = env.step(action)
        if done:
            print("Episode finished after {} timesteps".format(t+1))
            break
