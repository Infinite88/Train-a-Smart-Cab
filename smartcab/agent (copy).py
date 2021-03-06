import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from qlearn import QLearningAgent

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.prevReward = 0
        self.prevAction = None

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.state = None
        self.prevReward = 0
        self.prevAction = None

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        state = None
        validActions = []
        
        if inputs['light'] == 'red':
            if inputs['oncoming'] != 'left':
                validActions = ['right', None]
        else:
            if inputs['oncoming'] == 'forward':
                validActions = [ 'forward','right']
            else:
                validActions = ['right','forward', 'left']

        # TODO: Select action according to your policy
        if validActions != []:
            action = random.choice(validActions)
        else:
            action = random.choice(Environment.valid_actions)

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        if action != None:
            if reward > self.prevReward:
                self.state = (inputs,self.next_waypoint,deadline) 
                self.prevAction = action
                self.prevReward = reward
            else:
                self.state = (inputs,self.next_waypoint,deadline)
                self.prevAction = action
                self.prevReward = reward


        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


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
