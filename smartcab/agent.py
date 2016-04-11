import random
import pandas as pd
import numpy as np
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import math
from collections import namedtuple
import csv

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.prevReward = 0
        self.prevAction = None
        self.Q = {}
        self.alpha    = 0.6
        self.epsilon  = 0.0 
        self.gamma    = 0.35 #discount value
        self.totalReward = 0.0
        self.totalActions = 0.0
        self.success = 0.0
        self.negativeRewards = 0.0

    def flipCoin(self, p ):
        r = random.random()
        return r < p

    def reset(self, destination=None):
        self.planner.route_to(destination)

    def getQValue(self, state, action):
        return self.Q.get((state, action), 1)  

    def getValue(self, state):

        for action in Environment.valid_actions:
            if(self.getQValue(state, action) > 0):
                bestQValue = self.getQValue(state, action)

        return bestQValue

    def getPolicy(self, state):

        bestQValue = 0
        for action in Environment.valid_actions:
            if(self.getQValue(state, action) > bestQValue):
                bestQValue = self.getQValue(state, action)
                bestAction = action
            if(self.getQValue(state, action) == bestQValue):
                random.choice(Environment.valid_actions)
                bestQValue = self.getQValue(state, action)
                bestAction = action
        return bestAction

    def getAction(self, state):
        action = None
        if (self.flipCoin(self.epsilon)):
            action = random.choice(Environment.valid_actions)
        else:
            action = self.getPolicy(state)
        return action

    def qTable(self, state, action, nextState, reward):
    
        if((state, action) not in self.Q): 
            self.Q[(state, action)] = 1
        else:
            self.Q[(state, action)] = self.Q[(state, action)] + self.alpha*(reward + self.gamma*self.getValue(nextState) - self.Q[(state, action)]) 


    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (inputs['light'], self.next_waypoint)

        # TODO: Select action according to your policy
        action = self.getAction(self.state)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward

        self.prevAction = action
        self.prevState = self.state
        self.prevReward = reward
        self.totalReward += reward
        self.totalActions += 1.0

        if reward < 0:
            self.negativeRewards += 1.0

        if self.prevReward != None:
            self.qTable(self.prevState,self.prevAction,self.state,self.prevReward)

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]

        self.stats()

    def stats(self):
        alphaValues =[self.alpha]
        gammaValues = [self.gamma]
        epsilonValues =[self.epsilon]
        rewardTotal = [self.totalReward]
        negativeRewards = [self.negativeRewards]
        

        pd.DataFrame({'Alpha': alphaValues, 'Gamma': gammaValues, 'Epsilon': epsilonValues, 
            'Total Reward': rewardTotal, 'Negative Rewards': negativeRewards}).to_csv('smartcabStats.csv')

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track


    # Now simulate it
    sim = Simulator(e, update_delay=0.00000001)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()