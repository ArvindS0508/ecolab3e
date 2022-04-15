import numpy as np
import matplotlib.pyplot as plt

#Helper functions to calculate distances
def calcdistsqr(v):
    """Get euclidean distance^2 of v"""
    return np.sum(v**2)

def calcdist(v):
    """Get euclidean distance of v"""
    return np.sqrt(np.sum(v**2))


class Agent:
    """
    Base class for all types of agent
    """
    def __init__(self,position,age,food,speed,lastbreed, breedtype=0, breedfreq=10, breedfood=2):
        """
        age = age of agent in iterations
        food = how much food the agent has 'inside' (0=empty, 1=full)
        position = x,y position of the agent
        speed = how fast it can move (tiles/iteration)
        lastbreed = how long ago it last reproduced (iterations)
        """
        self.food = food
        self.age = age
        self.position = position
        self.speed = speed
        self.lastbreed = lastbreed
        self.breedtype = breedtype # 0 for asexual, 1 for sexual
        self.breedfreq = breedfreq # frequency of breeding
        self.breedfood = breedfood # minimum food for breeding


    def call(self, env, agents):
        """
        perform all the necessary actions and retun any new agents from breeding.
        Meant to be called as an all-in-one run implementation, instead of the  restrictive 
        move-eat-breed version currently used in __init__ of ecolab3
        """
        self.move(env, agents)
        self.eat(env,agents)
        if self.breedtype == 0:
            a = self.breed_asexual(agents)
        else:
            a = self.breed_sexual(agents)
        return a
    
    def breed_asexual(self, agents):
        """
        This will either return None, or a new agent object
        """
        new_agent = None
        if (self.lastbreed>self.breedfreq) and (self.food>self.breedfood):
            self.lastbreed = -1
            new_agent = type(self)(self.position,0,self.food/2,self.speed,10)
            self.food = self.food/2
        self.age+=1
        self.lastbreed+=1
        return new_agent

    def breed_sexual(self, agents):
        pass #depends on if Agent is male or female, so passed onto child class to implement
       
    def move(self,env, agents):
        pass #to implement by child class
    
    def trymove(self,newposition,env):
        if env.check_position(newposition):
            self.position = newposition
        #ensures it's in the environment and rounds to nearest cell
        #env.fix_position(self.position)

    
    def eat(self,env,agents):
        pass #to implement by child class
    
    def summary_vector(self):
        """
        Returns a list of the location (x,y), the agent type.
        """
        return [self.position[0],self.position[1],type(self)] # changed to return agent instead of 0 or 1 in third entry

    def die(self):
        """
        Returns true if it needs to expire, due to several factors specifiable
    
        """
        if self.food<=0: return True
        # examples of conditions that could be used here:
        #if self.age>self.maxage: return True
        #if self.eaten: return True
        #if self.health < 0: return True
        return False

class Male(Agent):
    """
    not meant to be used itself, meant to be a demonstration and/or inherited
    (likely you'd want to change the implementation yourself since it isn't one size fits all)

    sexual reproduction works by using two variables in the female agent:
    * mated - boolean controlling whether or not female has mated
    * mate type - type of male that mated. Could be genetic information such as morph, colour, etc.
    This implementation assumes that the different "choices" for children are different Agent classes
    If yours is not the same, you can pass in a specific variable to use in the constructor (height, weight, etc.)

    Males transfer this data to the female, who uses it to breed.

    Possible changes for more complexity: add more variables to use in the constructor of the new agent (child)
    """
    def __init__(self,position,age=None,food=10,speed=1,lastbreed=0):
        if age is None: age = np.random.randint(self.maxage)
        super().__init__(position,age,food,speed,lastbreed)
    def mate_female(self, env, agents):
        """
        mate with nearby female agent within a certain range
        """
        mate_range = 5
        nearest_female = self.get_nearby_female(self.position,self.Range,agents)
        if nearest_female is not None:
            female_position = nearest_female.position
            relative_female_position = female_position - self.position
            if calcdistsqr(relative_female_position)<mate_range**2:
                nearest_female.mated = True
                nearest_female.mate_type = type(self)

class Female(Agent):
    """
    not meant to be used itself, meant to be a demonstration and/or inherited (inheritance untested)
    (likely you'd want to change the implementation yourself since it isn't one size fits all)

    sexual reproduction works by using two variables in the female agent:
    * mated - boolean controlling whether or not female has mated
    * mate type - type of male that mated. Could be genetic information such as height, colour, etc.

    Males transfer this data to the female, who uses it to breed.

    Possible changes for more complexity: add more variables to use in the constructor of the new agent (child)
    """
    mated = False
    mate_type = None
    def __init__(self,position,age=None,food=10,speed=1,lastbreed=0):
        if age is None: age = np.random.randint(self.maxage)
        super().__init__(position,age,food,speed,lastbreed)
        self.mated = False
        self.mate_type = None

    def breed_sexual(self, agents):
        new_agent = None
        if self.mate==True and self.mate_type is not None: # you can add more conditions here as needed, like minimum food, a frequency counter, etc.
            #determine the sex of new agent
            sex = ["male", "female"]
            if(np.random.choice(sex)=="female"):
                new_agent = type(self)(self.position,0,self.food/2,self.speed,10)
            else:
                new_agent = self.mate_type(self.position,0,self.food/2,self.speed,10)
                # This implementation assumes the males are all different class implementations
                # If yours have smaller differences, then you can for instance pass in variables
                # to be used in a constructor instead, and change the above line accordingly
            
            self.mate = False
            self.mate_type = None
            self.food = self.food/2
        return new_agent

class Predator(Agent):
    """
    not meant to be used itself, meant to be a demonstration and/or inherited (inheritance untested)
    (likely you'd want to change the implementation yourself since it isn't one size fits all)

    Predators can kill other agents for their own food, or this code can also be used for agents who kill other agents
    for other purposes such as territory, etc.
    """

    def __init__(self,position,age=None,food=10,speed=1,lastbreed=0):
        if age is None: age = np.random.randint(self.maxage)
        super().__init__(position,age,food,speed,lastbreed)
        self.prey_type = None # this could be hard coded or set to be sent in as a parameter in the constructor
        # just make sure to change it from None!

    def kill(self,env,agents, killrange):
        """
            - will kill prey if there's prey within range
        """
        count = 2 # number of agents it can kill within a certain range
        for a in agents:
            if count<=0: break # remove this to kill all agents within range
            if calcdistsqr(a.position - self.position) < killrange**2: # killrange is the physical range within which it can kill
                if type(a)==self.prey_type:
                    a.dead=True
                    #self.food += 1 # food increases if the killed agent is eaten
                    #return #if you want to kill just one agent, a return statement can be used here instead of count
            count-=1