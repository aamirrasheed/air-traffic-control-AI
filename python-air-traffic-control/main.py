#!/usr/bin/env python
#   File: main.py

from pygame import *
from game import *
from highs import *
import os
import info_logger
import menu_base
import conf
import argparse

STATE_MENU = 1
STATE_GAME = 2
STATE_DEMO = 3
STATE_HIGH = 4
STATE_KILL = 5
STATE_AGES = 6

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
        state = STATE_MENU
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
                game = Game(self.screen, False)
                (gameEndCode, score) = game.start()
                self.infologger.add_value(self.id,'score',score)
                if (gameEndCode == conf.get()['codes']['kill']):
                    state = STATE_KILL
                elif (gameEndCode == conf.get()['codes']['user_end']):
                    state = STATE_MENU
                elif (gameEndCode == conf.get()['codes']['ac_collide']):
                    state = STATE_HIGH
            elif (state == STATE_DEMO):
               game = Game(self.screen, True)
               (gameEndCode, score) = game.start()
               state = STATE_MENU
            elif (state == STATE_HIGH):
                highEndCode = self.high.start(score)
                state = STATE_MENU
                score = 0
            elif (state == STATE_KILL):
                exit = 1
            elif (state == STATE_AGES):
                self.infologger.add_value(self.id,'agegroup',self.ages.main_loop())
                state = STATE_GAME
            game = None


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
