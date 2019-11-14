#!/usr/bin/env python
#   File: main.py

from pygame import *
from game_ai import *
from highs import *
import os
import info_logger
import menu_base
import conf
import argparse
import numpy as np
import random as random
from enum import Enum

STATE_MENU = 1
STATE_GAME = 2
STATE_DEMO = 3
STATE_HIGH = 4
STATE_KILL = 5
STATE_AGES = 6

# Creating the sarsa class
class Sarsa:
    d = 50
    rho = 36
    theta = 36
    na = 5
    ns = d * rho * theta
    explore = 0.1
    alpha = 0.5
    lamda = 0.2

    def __init__(self, State):
        # Values to store
        self.Q = np.zeros((Sarsa.ns, Sarsa.na))
        self.reward = 0
        self.oldAction = 0
        self.nextAction = 0
        self.oldState = State
        self.nextState = State
        self.oldIndex = 0
        self.nextIndex = 0
        self.distance, self.angle, self.heading = State

    def update(self, State):
        self.nextState = State
        self.distance, self.angle, self.heading = State
        self.nextIndex = self.angle * (Sarsa.theta * Sarsa.d) + self.heading * Sarsa.d + self.distance # error: out of bounds
        self.nextAction = self.chooseAction()
        self.rewardFunction(self.oldState[0])
        self.updateQ()
        self.oldState = self.nextState
        self.oldAction = self.nextAction
        self.oldIndex = self.nextIndex
        return self.nextAction


    def chooseAction(self):
        # Setting a random threshold
        rand = random.random()
        if rand < Sarsa.explore:
            action = random.randint(0, Sarsa.na-1)
        else:
            action = np.argmax(self.Q[self.nextIndex])
        return action

    def rewardFunction(self, distance):
        # ------- Need to implement +100 using the airport distance
        self.reward = -(2500-(distance**2))/5

    def updateQ(self):
        Q_val = self.Q[self.oldIndex][self.oldAction]
        self.Q[self.oldIndex][self.oldAction] += Sarsa.alpha*(self.reward + Sarsa.lamda*self.Q[self.nextIndex, self.nextAction] - Q_val)


# Create the action enumeration
class Action(Enum):
    N = 0   # Nothing
    HL = 1  # Hard Left
    ML = 2  # Mid Left
    MR = 3  # Mid Right
    HR = 4  # Hard Right

class Main:

    BG_COLOR = (0, 0, 0)

    def __init__(self):
        #Init the modules we need
        display.init()
        pygame.mixer.init()
        font.init()

        if(conf.get()['game']['fullscreen'] == True):
            self.screen = display.set_mode((1024, 768), pygame.FULLSCREEN)
        else:
            self.screen = display.set_mode((1024, 768))

        display.set_caption('ATC Version 2')

        self.menu = menu_base.menu_base(self.screen,150,25)
        self.menu.from_file('main_menu')
        self.ages = menu_base.menu_base(self.screen,150,25)
        self.ages.from_file('ages_menu')
        self.high = HighScore(self.screen)
        self.infologger = info_logger.info_logger()
        #Current visitor number
        self.id = int(self.infologger.get_id())

    def run(self):
        state = STATE_GAME
        exit = 0
        score = 0

        while (exit == 0):
            if (state == STATE_MENU):
                menuEndCode = None
                menuEndCode = self.menu.main_loop()
                self.infologger.writeout()
                if (menuEndCode == conf.get()['codes']['start']):
                    state = STATE_AGES
                    self.id += 1
                    self.infologger.add_value(self.id,'id',self.id)
                elif (menuEndCode == conf.get()['codes']['demo']):
                    state = STATE_DEMO
                elif (menuEndCode == conf.get()['codes']['high_score']):
                    state = STATE_HIGH
                elif (menuEndCode == conf.get()['codes']['kill']):
                    state = STATE_KILL
            elif (state == STATE_GAME):

                ##########################################################
                ##########################################################
                #                   MAIN GAME SEQUENCE                   #
                ##########################################################
                ##########################################################

                game = AIGame(self.screen, False)
                gameEndCode = 0
                game.start()
                while (gameEndCode == 0):
                    aircraft, rewards, collidingAircraft, gameEndCode, score = game.step()
                    if (len(collidingAircraft) != 0):
                        #print(aircraft[collidingAircraft[0][0]].getLocation())
                        plane1 = aircraft[collidingAircraft[0][0]]
                        plane2 = aircraft[collidingAircraft[0][1]]
                        print(self.getState(plane1, plane2))
                self.infologger.add_value(self.id,'score',score)
                if (gameEndCode == conf.get()['codes']['kill']):
                    state = STATE_KILL
                elif (gameEndCode == conf.get()['codes']['user_end']):
                    state = STATE_MENU
                elif (gameEndCode == conf.get()['codes']['ac_collide']):
                    state = STATE_HIGH
                ##########################################################
                ##########################################################
                #                 END MAIN GAME SEQUENCE                 #
                ##########################################################
                ##########################################################
            elif (state == STATE_KILL):
                exit = 1
            game = None

    def getState(self, plane1, plane2):
        '''
            Calculates the state for plane1, given that plane2, is within the
            potential collision radius of plane1.

            Params:
                plane1                          Aircraft object; The plane of interest (ownship)
                plane2                          Aircraft object; The intruder plane

            Returns:
                (distance, angle, heading)      Tuple that describes the state for plane1

            The returned state should contain:
                - The distance between the two planes, based on the norm of each plane's
                location field within the plane objects
                - The angle of the plane2's location relative to the heading of plane1
                - The heading of plane1

            NOTE: In order to get the state of plane2, you have to call the function
            again with the order of the planes reversed.
        '''
        loc1 = plane1.getLocation()
        loc2 = plane2.getLocation()
        heading = plane1.getHeading()   # The heading is clockwise
        distance = np.linalg.norm(loc1 - loc2)
        angle = (np.arctan2(loc2[1] - loc1[1], loc2[0] - loc1[0]))*180/np.pi
        return (distance, angle, heading)

    def queueAction(self, plane, action):
        '''
            Modifies the plane object to take the desired action set out by the
            agent.

            Params:
                plane                           Aircraft object; Plane to take the action
                action                          Action Class; The action to take

            Returns:
                None                            Modifies the plane object directly.
        '''
        if action == Action.HL:
            print("Taking hard left")
        elif action == Action.ML:
            print("Taking mid left")
        elif action == Action.HR:
            print("Taking hard right")
        elif action == Action.MR:
            print("Taking mid right")
        else:
            print("Doing nothing")



def getArgs(parser):
    '''
        Parses the command line arguments passed into the program call to change
        the game configurations.
    '''
    parser.add_argument("-g", "--gametime", type=int, help="Gametime in seconds")
    parser.add_argument("-p", "--planes", type=int, help="Number of planes to spawn")
    parser.add_argument("-s", "--spawnpoints", type=int, help="Number of spawnpoints for planes")
    parser.add_argument("-d", "--destinations", type=int, help="Number of airport destinations")
    parser.add_argument("-o", "--obstacles", type=int, help="Number of obstacles")
    parser.add_argument("-f", "--fullscreen", action="store_true", help="Toggle fullscreen mode")
    parser.add_argument("-fr", "--framerate", type=int, help="Framerate of the game")
    return parser.parse_args()


def override_config(args):
    '''
        Overrides the desired configurations from the command line. This only works because
        main is the first to initialize the configuration dictionary, allowing us to change
        the global variable here and having the changes propagate to the rest of the files.
        Hacky but it works.
    '''
    if (args.gametime is not None):
        conf.get()['game']['gametime'] = args.gametime * 1000 # Since gametime is measured in milliseconds
    if (args.planes is not None):
        conf.get()['game']['n_aircraft'] = args.planes
    if (args.spawnpoints is not None):
        conf.get()['game']['n_spawnpoints'] = args.spawnpoints
    if (args.destinations is not None):
        conf.get()['game']['n_destinations'] = args.destinations
    if (args.obstacles is not None):
        conf.get()['game']['n_obstacles'] = args.obstacles
    if (args.fullscreen):
        conf.get()['game']['fullscreen'] = True
    if (args.framerate is not None):
        conf.get()['game']['n_framerate'] = args.framerate


if __name__ == '__main__':

    # Initialize the command line parser
    parser = argparse.ArgumentParser("Configuration overrides for testing purposes.")
    # Get the arguments
    args = getArgs(parser)
    # Make the necessary changes to the game configuration
    override_config(args)

    game_main = Main()
    game_main.run()
