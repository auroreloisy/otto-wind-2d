# ____________ BASIC PARAMETERS _______________________________________________________________________________________
# Setup used for evaluation
EVAL_DRAW_SOURCE = [True, False]  # if False, episodes will continue until the source is almost surely found (Bayesian setting)
EVAL_TRUE_SOURCE_IS_FIXED_SOURCE = [True, False]  # only used if EVAL_DRAW_SOURCE = TRUE
# Discount factor
DISCOUNT = 1.0
# Reward shaping
REWARD_SHAPING = "D"
# Neural network (NN) architecture
FC_LAYERS = 3  # number of hidden layers
FC_UNITS = 8  # number of units per layers
# Experience replay
MEMORY_SIZE = 1000  # number of transitions (s, s') to keep in memory
# Max number of training iterations
ALGO_MAX_IT = 20  # max number of training iterations
# Evaluation of the RL policy
EVALUATE_PERFORMANCE_EVERY = 10  # how often is the RL policy evaluated, in number of training iterations
N_RUNS_STATS = 10
# Monitoring/Saving during the training
PRINT_INFO_EVERY = 1  # how often to print info on screen, in number of training iterations
# Restart from saved model, if None start from scratch
MODEL_PATH = None  # path to saved model, e.g., "./models/20220201-230054/20220201-230054_model"
# Parallelization: how many episodes are computed in parallel (how many cores are used)
N_PARALLEL = 1    # -1 for using all cores, 1 for sequential (useful as parallel code may hang with larger NN)
