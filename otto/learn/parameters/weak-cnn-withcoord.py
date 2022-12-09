# ____________ BASIC PARAMETERS _______________________________________________________________________________________
# Source-tracking POMDP
R_BAR = 0.25
# Discount factor
DISCOUNT = 1.0
# Reward shaping
REWARD_SHAPING = "0"
# Neural network (NN) architecture
CONV_LAYERS = 3  # number of convolutional layers
CONV_COORD = True  # whether to add coordinates to input (if CONV_LAYERS > 0)
CONV_FILTERS = (8, 16, 32)  # number of filters, for each convolutional layer
CONV_SIZES = (3, 3, 3)  # size of the filter, for each convolutional layer
POOL_SIZES = (2, 2, 2)  # size of the max pooling (done after convolution), for each convolutional layer
FC_LAYERS = 1  # number of hidden fully connected layers
FC_UNITS = (1024, )  # number of units, for each fully connected layers
# Experience replay
MEMORY_SIZE = 1000  # number of transitions (s, s') to keep in memory
REPLAY_NTIMES = 2  # how many times a transition is used for training before being deleted, on average
# Learning rate
LEARNING_RATE = 1e-3  # usual learning rate
# Exploration: eps is the probability of taking a random action when executing the policy
E_GREEDY_FLOOR = 0.1  # floor value of eps (cannot be smaller than that)
E_GREEDY_0 = 1.0  # initial value of eps
E_GREEDY_DECAY = 50000   # timescale for eps decay, in number of training iterations
# Evaluation of the RL policy
EVALUATE_PERFORMANCE_EVERY = 5000  # how often is the RL policy evaluated, in number of training iterations
# Evaluation of the RL policy
POLICY_REF = 0  # heuristic policy to use for comparison
N_RUNS_STATS = 500  # number of episodes used to compute the stats of a policy, set automatically if None
# Restart from saved model, if None start from scratch
MODEL_PATH = None  # path to saved model, e.g., "./models/20220201-230054/20220201-230054_model"
# Parallelization: how many episodes are computed in parallel (how many cores are used)
N_PARALLEL = 1    # -1 for using all cores, 1 for sequential (useful as parallel code may hang with larger NN)
