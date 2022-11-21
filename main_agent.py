import RacingEnv
import pygame
import numpy as np
from DQNAgent import DQNAgent
from collections import deque
import random, math


TOTAL_GAMETIME = 1000 # Max game time for one episode
N_EPISODES = 10000
REPLACE_TARGET = 50 

game = RacingEnv.RacingEnv()
game.fps = 60

GameTime = 0 
GameHistory = []
renderFlag = False

dqnAgent = DQNAgent()

# if you want to load the existing model uncomment this line.
# careful an existing model might be overwritten
#ddqn_agent.load_model()
# dqnAgent.load_model()
ddqn_scores = []
eps_history = []

def run():

    for e in range(N_EPISODES):
        
        game.reset() #reset env 
        # dqnAgent.load_model()
        done = False
        score = 0
        counter = 0
        
        current_state , reward, done = game.step(0)
        current_state = np.array(current_state)

        gtime = 0 # set game time back to 0
        
        renderFlag = True # if you want to render every episode set to true

        if e % 10 == 0 and e > 0: # render every 10 episodes
            renderFlag = True

        while not done:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    return

            action = dqnAgent.choose_action(current_state)
            new_state, reward, done = game.step(action)
            new_state = np.array(new_state)

            # This is a countdown if no reward is collected the car will be done within 100 ticks
            # if reward == 0:
            #     counter += 1
            #     if counter > 100:
            #         done = True
            # else:
            #     counter = 0

            score += reward
            if not done:
                dqnAgent.update_replay_memory((current_state, action, reward, new_state, int(done)))
                current_state = new_state
            dqnAgent.train()
            
            gtime += 1

            if gtime >= TOTAL_GAMETIME:
                done = True

            if renderFlag:
                game.render(action)

        eps_history.append(dqnAgent.epsilon)
        ddqn_scores.append(score)
        avg_score = np.mean(ddqn_scores[max(0, e-100):(e+1)])

        # if e % REPLACE_TARGET == 0 and e > REPLACE_TARGET:
        #     dqnAgent.update_network_parameters()

        if e % 10 == 0 and e > 10:
            dqnAgent.save_model()
            print("save model")
            
        print('episode: ', e,'score: %.2f' % score,
              ' average score %.2f' % avg_score,
              ' epsolon: ', dqnAgent.epsilon,
              ' memory size', len(dqnAgent.replay_memory))   

run()        
