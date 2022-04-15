import numpy as np
import ecolab3e.agents
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import rc

def run_ecolab(env,agents,Niterations=1000,earlystop=True):
    """
    Run ecolab, this applies the rules to the agents and the environment. It records
    the grass array and the locations (and type) of agents in a list it returns.
    
    Arguments:
    - env = an Environment object
    - agents = a list of agents (all inherited from Agent)
    - Niterations = number of iterations to run (default = 1000)
    - earlystop = if true (default), will stop the simulation early if no agents left.
    """

    record = []
    for it in range(Niterations):
        if (it+1)%100==0: print("%5d" % (it+1), end="\r") #progress message
            
        #for each agent, apply rules (move, eat, breed)
        for agent in agents:
            # a singular call method is used, more flexible since it can be modified to use more methods for different agent types
            a = agent.call(env, agents)
            if a is not None: agents.append(a)

        #removed dead agents
        agents = [a for a in agents if not a.die()]

        #grow more grass
        env.grow()

        #record the grass and agent locations (and types) for later plotting & analysis
        record.append({'grass':env.grass.copy(),'agents':np.array([a.summary_vector() for a in agents])})

        #stop early if we run out of rabbits and foxes
        if earlystop:
            if len(agents)==0: break
    return record

def draw_animation(fig,record,fps=20,saveto=None):
    """
    Draw the animation for the content of record. This doesn't use the draw
    functions of the classes.
    - fig figure to draw to
    - record = the data to draw
    - fps = frames per second
    - saveto = where to save it to
    """
    #rc('animation', html='html5')
    if len(record)==0: return None

    im = plt.imshow(np.zeros_like(record[0]['grass']), interpolation='none', aspect='auto', vmin=0, vmax=3, cmap='gray')
    ax = plt.gca()

    # here we split the graph into 4 test types, Agent, Male, Predator and Female
    # this is only to showcase how to extrapolate the draw function for multiple agent types (beyond 2)
    # change this to your own agent types!
    # for more info on the colours and symbols available, read the documentation of ax.plot
    aplot = ax.plot(np.zeros(1),np.zeros(1),'bo',markersize=10, mew=3)
    mplot = ax.plot(np.zeros(1),np.zeros(1),'ro',markersize=10,mew=3)
    pplot = ax.plot(np.zeros(1),np.zeros(1),'yo',markersize=10, mew=3)
    fplot = ax.plot(np.zeros(1),np.zeros(1),'gx',markersize=10,mew=3)

    def animate_func(i):
            im.set_array(record[i]['grass'])
            ags = record[i]['agents']
            if len(ags)==0:
                aplot[0].set_data([],[])
                mplot[0].set_data([],[])
                pplot[0].set_data([],[])
                fplot[0].set_data([],[])
                return
            coords = ags[ags[:,-1]==ecolab3e.agents.Agent,0:2]
            aplot[0].set_data(coords[:,1],coords[:,0])
            coords = ags[ags[:,-1]==ecolab3e.agents.Male,0:2]
            mplot[0].set_data(coords[:,1],coords[:,0])
            coords = ags[ags[:,-1]==ecolab3e.agents.Predator,0:2]
            pplot[0].set_data(coords[:,1],coords[:,0])
            coords = ags[ags[:,-1]==ecolab3e.agents.Female,0:2]
            fplot[0].set_data(coords[:,1],coords[:,0])
            #return [im]#,rabbits,foxes]

    anim = animation.FuncAnimation(
                                   fig, 
                                   animate_func, 
                                   frames = len(record),
                                   interval = 1000 / fps, repeat=False # in ms
                                   )
    if saveto is not None: anim.save(saveto, fps=fps, extra_args=['-vcodec', 'libx264']) 
    from IPython.display import HTML
    return HTML(anim.to_jshtml())

def get_agent_counts(record):
    """
    Returns the number of agents and number of grass in an np array
    the array has a size equal to the number of agent types in use, plus one more for the grass type

    In this example, the 4 types used are Agent, Male, Predator and Female. Change these to your own defined classes' types
    """
    counts = []
    for r in record:
        ags = r['agents']
        if len(ags)==0:
            nA = 0
            nM = 0
            nP = 0
            nF = 0
        else:
            nA = np.sum(ags[:,-1]==ecolab3e.agents.Agent)
            nM = np.sum(ags[:,-1]==ecolab3e.agents.Male)
            nP = np.sum(ags[:,-1]==ecolab3e.agents.Predator)
            nF = np.sum(ags[:,-1]==ecolab3e.agents.Female)
        nG = np.sum(r['grass'])
        counts.append([nA,nM,nP,nF,nG])
    counts = np.array(counts)
    return counts
