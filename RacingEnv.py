import pygame
import math
from Walls import Wall
from Walls import getWalls
from Goals import Goal
from Goals import getGoals

from Cars import Car

LIFE_REWARD = 0
NEG_SPEED_PENALTY = -10
LOW_SPEED_PENALTY = 1
RUN_REWARD = 5
CRASH_PENALTY = -1000
GOAL_REWARD = 100

class RacingEnv:

    def __init__(self):
        pygame.init()
        self.font = pygame.font.Font(pygame.font.get_default_font(), 36)

        self.fps = 120
        self.width = 1000
        self.height = 600
        self.history = []

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("RACING DQN")
        self.screen.fill((0,0,0))
        self.back_image = pygame.image.load("track.png").convert()
        self.back_rect = self.back_image.get_rect().move(0, 0)
        self.action_space = None
        self.observation_space = None
        self.game_reward = 0
        self.score = 0
 
        self.reset()

    def reset(self):
        self.screen.fill((0, 0, 0))

        self.car = Car(50, 360)
        self.walls = getWalls()
        self.goals = getGoals()
        self.game_reward = 0   

    def step(self, action):

        done = False
        self.car.action(action)
        self.car.update()
        reward = LIFE_REWARD

        # Check if speed of the car
        if self.car.vel > 0:
            reward = NEG_SPEED_PENALTY
        elif self.car.vel > -3:
            reward = LOW_SPEED_PENALTY
        else:
            reward = RUN_REWARD

        # Check if car passes Goal and scores
        index = 1
        for goal in self.goals:
            
            if index > len(self.goals):
                index = 1
            if goal.isactiv:
                if self.car.cross_goal(goal):
                    goal.isactiv = False
                    self.goals[index-2].isactiv = True
                    reward += GOAL_REWARD

            index = index + 1

        #check if car crashed in the wall
        for wall in self.walls:
            if self.car.collision(wall):
                reward += CRASH_PENALTY
                done = True

        new_state = self.car.cast(self.walls)
        #normalize states
        if done:
            new_state = None

        return new_state, reward, done

    def render(self, action):

        DRAW_WALLS = False
        DRAW_GOALS = True
        DRAW_RAYS = False

        pygame.time.delay(10)

        self.clock = pygame.time.Clock()
        self.screen.fill((0, 0, 0))

        self.screen.blit(self.back_image, self.back_rect)

        if DRAW_WALLS:
            for wall in self.walls:
                wall.draw(self.screen)
        
        if DRAW_GOALS:
            for goal in self.goals:
                goal.draw(self.screen)
                if goal.isactiv:
                    goal.draw(self.screen)
        
        self.car.draw(self.screen)

        if DRAW_RAYS:
            i = 0
            for pt in self.car.close_rays:
                pygame.draw.circle(self.screen, (0,0,255), (pt.x, pt.y), 5)
                i += 1
                if i < 15:
                    pygame.draw.line(self.screen, (255,255,255), (self.car.x, self.car.y), (pt.x, pt.y), 1)
                elif i >=15 and i < 17:
                    pygame.draw.line(self.screen, (255,255,255), ((self.car.p1.x + self.car.p2.x)/2, (self.car.p1.y + self.car.p2.y)/2), (pt.x, pt.y), 1)
                elif i == 17:
                    pygame.draw.line(self.screen, (255,255,255), (self.car.p1.x , self.car.p1.y ), (pt.x, pt.y), 1)
                else:
                    pygame.draw.line(self.screen, (255,255,255), (self.car.p2.x, self.car.p2.y), (pt.x, pt.y), 1)

        #render controll
        pygame.draw.rect(self.screen,(255,255,255),(800, 100, 40, 40),2)
        pygame.draw.rect(self.screen,(255,255,255),(850, 100, 40, 40),2)
        pygame.draw.rect(self.screen,(255,255,255),(900, 100, 40, 40),2)
        pygame.draw.rect(self.screen,(255,255,255),(850, 50, 40, 40),2)

        if action == 1:
            # turn right
            pygame.draw.rect(self.screen,(0,255,0),(900, 100, 40, 40))
        elif action == 2:
            # turn left
            pygame.draw.rect(self.screen,(0,255,0),(800, 100, 40, 40))
        elif action == 3:
            # acc
            pygame.draw.rect(self.screen,(0,255,0),(850, 100, 40, 40)) 
        elif action == 4:
            # acc
            pygame.draw.rect(self.screen,(0,255,0),(850, 100, 40, 40))
            # turn right
            pygame.draw.rect(self.screen,(0,255,0),(900, 100, 40, 40))
        elif action == 5:
            # acc
            pygame.draw.rect(self.screen,(0,255,0),(850, 100, 40, 40))
            # turn left
            pygame.draw.rect(self.screen,(0,255,0),(800, 100, 40, 40))
        elif action == 6:
            # deacc
            pygame.draw.rect(self.screen,(0,255,0),(850, 50, 40, 40)) 

        elif action == 7:
            # deacc
            pygame.draw.rect(self.screen,(0,255,0),(850, 50, 40, 40))
            # turn right
            pygame.draw.rect(self.screen,(0,255,0),(900, 100, 40, 40))
        elif action == 8:
            # deacc
            pygame.draw.rect(self.screen,(0,255,0),(850, 50, 40, 40))
            # turn left
            pygame.draw.rect(self.screen,(0,255,0),(800, 100, 40, 40))

        # score
        text_surface = self.font.render(f'Points {self.car.points}', True, pygame.Color('green'))
        self.screen.blit(text_surface, dest=(0, 0))
        # speed
        text_surface = self.font.render(f'Speed {self.car.vel*-1}', True, pygame.Color('green'))
        self.screen.blit(text_surface, dest=(800, 0))

        self.clock.tick(self.fps)
        pygame.display.update()

    def close(self):
        pygame.quit()