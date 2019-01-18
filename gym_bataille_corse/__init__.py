from gym.envs.registration import register

register(
    id='bataille_corse-v0',
    entry_point='gym_bataille_corse.envs:BatailleCorseEnv',
    kwargs={'playersNumber': 2}
)
