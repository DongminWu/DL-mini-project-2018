
import gym
import numpy as np
import random

from environment import Environment, BOARD_SIZE, BOARD_WIDTH
from logger import logger



# env = gym.make('FrozenLake-v0')
env = Environment()


#Initialize table with all zeros
# Q = np.zeros([env.observation_space.n,env.action_space.n])
Q = np.zeros([BOARD_SIZE,5])
# Set learning parameters
lr = .8
y = .95
num_episodes = 20000
#create lists to contain total rewards and steps per episode
#jList = []
rList = []

env.render()

for i in range(num_episodes):
    #Reset environment and get first new observation
    s = env.reset().argmax()
    rAll = 0
    d = False
    j = 0
    #The Q-Table learning algorithm
    while j < 999:
        j+=1
        #Choose an action by greedily (with noise) picking from Q table
        a = np.argmax(Q[s,:] + np.random.randn(1,5)*(1./(i+1)))
        #Get new state and reward from environment
        s1,r,d,_ = env.step(a)
        s1 = s1.argmax()
        #Update Q-Table with new knowledge
        Q[s,a] = Q[s,a] + lr*(r + y*np.max(Q[s1,:]) - Q[s,a])
        rAll += r
        s = s1
        if d == True:
            break
    #jList.append(j)
    rList.append(rAll)

print("Score over time: " +  str(sum(rList)/num_episodes))

import plot_helper as ph

# ph.draw_plot(rList)
# ph.draw_plot(rList[0:100])

import pickle
with open("result_q_table_16x16.list","wb") as f:
    pickle.dump(rList,f)

print("Final Q-Table Values")
env.render()
print(Q)