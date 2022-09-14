# ____________ BASIC PARAMETERS _______________________________________________________________________________________
# Source-tracking POMDP
R_BAR = 2.5
# Setup used for evaluation
DRAW_SOURCE = True  # if False, episodes will continue until the source is almost surely found (Bayesian setting)
TRUE_SOURCE_IS_FAKE_SOURCE = True
# Discount factor
DISCOUNT = 1.0
# Reward shaping
REWARD_SHAPING = "0"
# Neural network (NN) architecture
FC_LAYERS = 3  # number of hidden layers
FC_UNITS = 1024  # number of units per layers
# Experience replay
MEMORY_SIZE = 1000  # number of transitions (s, s') to keep in memory
# Exploration: eps is the probability of taking a random action when executing the policy
E_GREEDY_DECAY = 10000   # timescale for eps decay, in number of training iterations
# Evaluation of the RL policy
EVALUATE_PERFORMANCE_EVERY = 5000  # how often is the RL policy evaluated, in number of training iterations
# Restart from saved model, if None start from scratch
MODEL_PATH = None  # path to saved model, e.g., "./models/20220201-230054/20220201-230054_model"
# Parallelization: how many episodes are computed in parallel (how many cores are used)
N_PARALLEL = 1    # -1 for using all cores, 1 for sequential (useful as parallel code may hang with larger NN)
