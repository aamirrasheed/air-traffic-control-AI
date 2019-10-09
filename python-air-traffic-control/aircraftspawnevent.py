#	File: aircraftspawnevent.py

import conf
import random

class AircraftSpawnEvent:

    """
    Constructor to initialize:
    1. Spawn Location
    2. Destination
    """
    def __init__(self, spawnpoint, destination):
        self.spawnpoint = spawnpoint
        self.destination = destination

    def getSpawnPoint(self):
        return self.spawnpoint

    def getDestination(self):
        return self.destination

    def __str__(self):
        return "<" + str(self.spawnpoint) + ", " + str(self.destination.getLocation()) + ">"

    @staticmethod
    def valid_destinations(destinations,test1,test2):
        #d = filter(test1,destinations)
        d = [item for item in destinations if test1(item)]
        if (len(d) == 0):
            return destinations
        else:
            return d


    @staticmethod
    def generateGameSpawnEvents(screen_w, screen_h, destinations):
        randtime = [1]
        randspawnevent = []
        for x in range(1, conf.get()['game']['n_aircraft']): # Number of aircrafts = 30 default
            randtime.append(random.randint(1, conf.get()['game']['gametime']))
        randtime.sort()
        for x in randtime:
            randspawn, side = AircraftSpawnEvent.__generateRandomSpawnPoint(screen_w, screen_h)
            if (side == 1):
                def t1(d):
                    l = d.getLocation()
                    return l[1] > screen_h/2
                def t2(p1,p2):                  # What does this do????
                    return 1
            elif (side == 2):
                def t1(d):
                    l = d.getLocation()
                    return l[0] < screen_w/2
                def t2(p1,p2):
                    return 1
            elif (side == 3):
                def t1(d):
                    l = d.getLocation()
                    return l[1] < screen_h/2
                def t2(p1,p2):
                    return 1
            elif (side == 4):
                def t1(d):
                    l = d.getLocation()
                    return l[0] > screen_w/2
                def t2(p1,p2):
                    return 1
            d = AircraftSpawnEvent.valid_destinations(destinations,t1,t2)
            randdest = random.choice(d)
            randspawnevent.append(AircraftSpawnEvent(randspawn, randdest)) # I am interested in location: randspawn
        print("Write spawn points")
        for i in randspawnevent:
            print(i)
            print()
        return (randtime, randspawnevent)

    @staticmethod
    def __generateRandomSpawnPoint(screen_w, screen_h):
        #side = random.randint(1, 4)     # I guess screen is split into 4 sides (left, right, top, right)
        side = 4                        # I modified (Have to delete this and remove earlier line)
        previous = 7                    # Magic Number ?????????????????????????????????
        if side == 1 and side != previous:
            loc = (random.randint(0, screen_w), 0)          # Spawn in the top region
        elif side == 2 and side != previous:
            loc = (screen_w, random.randint(0, screen_h))   # Spawn in the right region
        elif side == 3 and side != previous:
            loc = (random.randint(0, screen_w), screen_h)   # Spawn in the bottom region
        elif side == 4 and side != previous:
            loc = (0, random.randint(0, screen_h))          # Spawn in the left region

        #previous = side               # Have to remove comment
        return (loc), side
