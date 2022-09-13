# ____________ BASIC PARAMETERS _______________________________________________________________________________________
# Setup used for evaluation
DRAW_SOURCE = True  # if False, episodes will continue until the source is almost surely found (Bayesian setting)
TRUE_SOURCE_IS_FAKE_SOURCE = True
# Discount factor
DISCOUNT = 0.9
# Reward shaping
REWARD_SHAPING = "D"
# Neural network (NN) architecture
FC_LAYERS = 3  # number of hidden layers
FC_UNITS = 8  # number of units per layers
# Experience replay
MEMORY_SIZE = 1000  # number of transitions (s, s') to keep in memory
# Max number of training iterations
ALGO_MAX_IT = 5  # max number of training iterations
# Evaluation of the RL policy
EVALUATE_PERFORMANCE_EVERY = 2  # how often is the RL policy evaluated, in number of training iterations
N_RUNS_STATS = 50
# Restart from saved model, if None start from scratch
MODEL_PATH = None  # path to saved model, e.g., "./models/20220201-230054/20220201-230054_model"
# Parallelization: how many episodes are computed in parallel (how many cores are used)
N_PARALLEL = 1    # -1 for using all cores, 1 for sequential (useful as parallel code may hang with larger NN)
