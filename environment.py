import numpy as np
from logger import logger

ENEMY_ATTACK="soft_attack"

ENV_OBSTACLE = 255
ENV_EMPTY = 0
ENV_AGENT = 1
ENV_ENEMY = 2
ENV_GOAL = 3

ACT_STAY = 0
ACT_UP = 1
ACT_LEFT = 2
ACT_DOWN = 3
ACT_RIGHT = 4




BOARD_WIDTH = 5
BOARD_SIZE = BOARD_WIDTH * BOARD_WIDTH



def generate_grid_world(num_agent=1, num_enemy=1,num_goal=1):
    sum_up = num_agent+num_enemy+num_goal

    matrix = np.zeros([BOARD_SIZE])
    matrix_idx = np.arrange(BOARD_SIZE)
    
    chosen_idx = np.random.choice(matrix_idx, sum_up, False)

    matrix[chosen_idx[0:num_agent]] = ENV_AGENT
    matrix[chosen_idx[num_agent:num_enemy]] = ENV_ENEMY
    matrix[chosen_idx[num_enemy:num_goal]] = ENV_GOAL


class Environment:
    
    def __init__(self):

        self.enemy_reward = 0
        self.goal_reward = 1
        self.life_reward = -1
        self.agent_pos, self.enemy_pos, self.goal_pos= [],[],[]
        self.board = self.generate_grid_world()
        self.ori_agent_pos = self.agent_pos[:]
        self.ori_board = self.board.copy()
        self.reset()

    def generate_grid_world(self, num_agent=1, num_enemy=1,num_goal=1):

        def position_translate(idxs):
            ret = []
            for each in idxs:
                pos = np.zeros(2)
                pos[0] = each % BOARD_WIDTH  #x
                pos[1] = each // BOARD_WIDTH #y
                ret.append(pos)
            return ret

        sum_up = num_agent+num_enemy+num_goal

        matrix = np.zeros([BOARD_SIZE])
        matrix_idx = np.arange(BOARD_SIZE)
        
        chosen_idx = np.random.choice(matrix_idx, sum_up, False)

        agent_idxs = chosen_idx[0:num_agent]
        enemy_idxs = chosen_idx[num_agent:num_agent+num_enemy]
        goal_idxs = chosen_idx[num_agent+num_enemy:num_agent+num_enemy+num_goal]
        
        matrix[agent_idxs] = ENV_AGENT
        matrix[enemy_idxs] = ENV_ENEMY
        matrix[goal_idxs] = ENV_GOAL


        ret = matrix.reshape((BOARD_WIDTH, BOARD_WIDTH))

        self.agent_pos = position_translate(agent_idxs)
        self.enemy_pos = position_translate(enemy_idxs)
        self.goal_pos = position_translate(goal_idxs)
        return ret
    
    def render(self):


        print("")
        for m in self.board:
            for n in m:
                if n == ENV_EMPTY:
                    print(". ",end="")
                elif n == ENV_ENEMY:
                    print("X ", end="")
                elif n == ENV_AGENT:
                    print("@ ", end="")
                elif n == ENV_GOAL:
                    print("O ", end="")
                    
            print("")
        print("")
        
            

    def reset(self):
        
        # self.board = np.zeros([BOARD_WIDTH,BOARD_WIDTH])
        # self.board = self.generate_grid_world()

        #self.render()

        # return self.board
        self.board = self.ori_board.copy()
        self.agent_pos = self.ori_agent_pos[:]
        return self.get_observation(self.agent_pos[0])


    def try_move(self, cur_pos, action):
        new_pos = cur_pos.copy()
        new_pos[1] = new_pos[1] - 1 if action == ACT_UP else new_pos[1]
        new_pos[0] = new_pos[0] - 1 if action == ACT_LEFT else new_pos[0]
        new_pos[1] = new_pos[1] + 1 if action == ACT_DOWN else new_pos[1]
        new_pos[0] = new_pos[0] + 1 if action == ACT_RIGHT  else new_pos[0]

        if (new_pos[0]<0 or new_pos[0]>BOARD_WIDTH-1 or new_pos[1]<0 or new_pos[1]>BOARD_WIDTH-1):
            return False, cur_pos.copy()

        else:
            return True, new_pos

    def apply_new_pos(self, old_pos, new_pos, who):
        self.board[int(old_pos[1])][int(old_pos[0])] = ENV_EMPTY
        self.board[int(new_pos[1])][int(new_pos[0])] = who
        return new_pos.copy()


        

    def step(self,action):

        print("action: %s" %  action)

        new_board = self.board
        reward = 0
        done = False
        info = ""


        observation = self.get_observation(self.agent_pos[0])

                
        ret, new_pos = self.try_move(self.agent_pos[0], action)
        if ret == False: #hit the wall, stop
            reward = self.enemy_reward
            done = True
            return observation, reward, done, info

        if self.collition(new_pos, self.enemy_pos):
            #meet enemy, done
            reward = self.enemy_reward
            done = True
        elif self.collition(new_pos, self.goal_pos):
            reward = self.goal_reward
            done = True
            # print ("success!")
        else:

            #move the enemy first
            if ENEMY_ATTACK == "random":
                enemy_action = np.random.randint(0,5)
            elif ENEMY_ATTACK == "soft_attack":
                enemy_action = ACT_STAY
                rnd = np.random.rand(1) < 0.2 #20% chance to attack the agent
                if rnd:
                    if self.enemy_pos[0][0] < self.agent_pos[0][0]:
                        enemy_action = ACT_RIGHT
                    elif self.enemy_pos[0][0] > self.agent_pos[0][0]:
                        enemy_action = ACT_LEFT
                    elif self.enemy_pos[0][1] < self.agent_pos[0][1]:
                        enemy_action = ACT_DOWN
                    elif self.enemy_pos[0][1] > self.agent_pos[0][1]:
                        enemy_action = ACT_UP


            ret, new_enemy = self.try_move(self.enemy_pos[0],enemy_action)
            if ret:
                if (self.collition(new_enemy, self.agent_pos[0]) and \
                    self.collition(new_enemy, self.goal_pos[0])) == False :
                    self.enemy_pos[0] = self.apply_new_pos(self.enemy_pos[0], new_enemy, ENV_ENEMY)         

            #moving the agent
            self.agent_pos[0] = self.apply_new_pos(self.agent_pos[0], new_pos, ENV_AGENT)  



            observation = self.get_observation(self.agent_pos[0])
        

        
        return observation, reward, done, info


    def collition(self, pos1, pos2):
        return np.all(pos1==pos2)

    def get_observation(self,ag_pos):

        #only return agent pos
        # return np.identity(BOARD_SIZE)[int(ag_pos[1])*BOARD_WIDTH + int(ag_pos[0])]


        #return full view of map
        # s = self.board.reshape(-1)
        # s[int(self.enemy_pos[0][1])*BOARD_WIDTH + int(self.enemy_pos[0][0])]=0
        # s[int(self.goal_pos[0][1])*BOARD_WIDTH + int(self.goal_pos[0][0])]=0

        #only in this way, the result will converge, misteriously

        b = np.identity(BOARD_SIZE)[int(ag_pos[1])*BOARD_WIDTH + int(ag_pos[0])]

        b_ene = np.identity(BOARD_SIZE)[int(self.enemy_pos[0][1])*BOARD_WIDTH + int(self.enemy_pos[0][0])]*ENV_ENEMY
        b_goal = np.identity(BOARD_SIZE)[int(self.goal_pos[0][1])*BOARD_WIDTH + int(self.goal_pos[0][0])]*ENV_GOAL

        b=b+b_ene+b_goal
       
        # print(b)

        return b
        

        







if __name__ == "__main__":
    print(__file__)
    print("test mode")

    env = Environment()

    print(env.board)
    print(env.agent_pos)
    print(env.enemy_pos)
    print(env.goal_pos)

    d = False
    for m in range(200):
        ob, r, d, i = env.step(np.random.randint(0,5))
        env.render()

        if d:
            env.render()
            print("Done in %d times with reward %d" % (m,r))
            break

    print(env.reset())

    

    



