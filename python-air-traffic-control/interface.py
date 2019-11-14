#!/usr/bin/env python
#   File: main.py

from pygame import *
from game_ai import *
from highs import *
from waypoint import *
import os
import info_logger
import menu_base
import conf
import argparse
from enum import Enum

STATE_MENU = 1
STATE_GAME = 2
STATE_DEMO = 3
STATE_HIGH = 4
STATE_KILL = 5
STATE_AGES = 6


# Create the action enumeration
class Action(Enum):
    N = 0   # Nothing
    HL = 1  # Hard Left
    ML = 2  # Mid Left
    MR = 3  # Mid Right
    HR = 4  # Hard Right

# Define the distance a plane should be re-routed to when given an action
REROUTE_DISTANCE = 50

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
        return None

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
        def wrapToPi(a):
            if isinstance(a, list):
                return [(x + np.pi) % (2*np.pi) - np.pi for x in a]
            return (a + np.pi) % (2*np.pi) - np.pi

        location = plane.getLocation()
        # Initialize the Waypoint with the plane's current location as a placeholder
        newWaypoint = Waypoint(location)
        # Heading is returned as degrees to convert to radians
        # Heading is also with respect to the top of the screen so that is accounted for
        heading = wrapToPi(plane.getHeading()*np.pi/180.0 - np.pi/2)

        # Calculate the new heading that the plane must go to inact the desired action
        if action == Action.HL:
            newHeading = wrapToPi(heading-np.pi/2)
        elif action == Action.ML:
            newHeading = wrapToPi(heading-np.pi/4)
        elif action == Action.HR:
            newHeading = wrapToPi(heading+np.pi/2)
        elif action == Action.MR:
            newHeading = wrapToPi(heading+np.pi/4)
        else:
            print("Doing nothing")
            newWaypoint = None

        if (newWaypoint):
            # Using the new heading and the reroute distance, calculate a point along that heading
            reroutePoint = REROUTE_DISTANCE*np.array([np.cos(newHeading), np.sin(newHeading)])
            # Re-set the waypoint object
            newWaypoint.setLocation(location + reroutePoint)
            # Add the waypoint to the plane trajectory
            plane.addWaypoint(newWaypoint)



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
