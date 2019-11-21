from enum import Enum
import numpy as np
import random as random

# Creating the sarsa class
class Sarsa:
    d = 200
    rho = 36
    theta = 36
    na = 5
    ns = d * rho * theta
    explore = 0.1
    alpha = 0.5
    lamda = 0.2

    def __init__(self, state):
        # Values to store
        self.Q = np.zeros((Sarsa.ns, Sarsa.na))
        self.reward = 0
        self.oldAction = 0
        self.nextAction = 0
        self.oldState = state
        self.nextState = state
        self.oldIndex = 0
        self.nextIndex = 0
        self.distance = state.d
        self.angle = state.rho
        self.heading = state.theta

    def update(self, state):
        self.nextState = state
        self.distance = state.d
        self.angle = state.rho
        self.heading = state.theta
        self.nextIndex = self.angle * (Sarsa.theta * Sarsa.d) + self.heading * Sarsa.d + self.distance # error: out of bounds
        self.nextAction = self.chooseAction()
        self.rewardFunction(self.oldState.d)
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
            #print(action)
        return action

    def rewardFunction(self, distance):
        # ------- Need to implement +100 using the airport distance
        self.reward = -(Sarsa.d**2-(distance**2))/(Sarsa.d**2/500)


    def updateQ(self):
        Q_val = self.Q[self.oldIndex][self.oldAction]
        self.Q[self.oldIndex][self.oldAction] += Sarsa.alpha*(self.reward + Sarsa.lamda*self.Q[self.nextIndex, self.nextAction] - Q_val)
        #print(self.Q)

# Create the action enumeration
class Action(Enum):
    N = 0   # Nothing
    HL = 1  # Hard Left
    ML = 2  # Mid Left
    MR = 3  # Mid Right
    HR = 4  # Hard Right

# Create the state object 
class State:
    def __init__(self, d=0, rho=0, theta=0):
        self.d = d
        self.rho = rho
        self.theta = theta

