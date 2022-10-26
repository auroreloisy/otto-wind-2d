# ____________ BASIC PARAMETERS _______________________________________________________________________________________
# Source-tracking POMDP
R_BAR = 2.5
# Setup used for training
TRAIN_DRAW_SOURCE = False  # if False, episodes will continue until the source is almost surely found (Bayesian setting)
# Setup used for evaluation
EVAL_DRAW_SOURCE = False  # if False, episodes will continue until the source is almost surely found (Bayesian setting)
# Discount factor
DISCOUNT = 1.0
# Reward shaping
REWARD_SHAPING = "0"
# Neural network (NN) architecture
FC_LAYERS = 3  # number of hidden layers
FC_UNITS = 1024  # number of units per layers
# Experience replay
MEMORY_SIZE = 500  # number of transitions (s, s') to keep in memory
# Exploration: eps is the probability of taking a random action when executing the policy
E_GREEDY_DECAY = 10000   # timescale for eps decay, in number of training iterations
# Max number of training iterations
ALGO_MAX_IT = 10000000  # max number of training iterations
# Evaluation of the RL policy
EVALUATE_PERFORMANCE_EVERY = 5000  # how often is the RL policy evaluated, in number of training iterations
# Restart from saved model, if None start from scratch
MODEL_PATH = None  # path to saved model, e.g., "./models/20220201-230054/20220201-230054_model"
# Parallelization: how many episodes are computed in parallel (how many cores are used)
N_PARALLEL = 1    # -1 for using all cores, 1 for sequential (useful as parallel code may hang with larger NN)

# ____________ ADVANCED RL PARAMETERS _________________________________________________________________________________
# Stochastic gradient descent
BATCH_SIZE = 64  # size of the mini-batch
N_GD_STEPS = 12  # number of gradient descent steps per training iteration
LEARNING_RATE = 0.001  # usual learning rate
# Experience replay
REPLAY_NTIMES = 4  # how many times a transition is used for training before being deleted, on average
# Exploration: eps is the probability of taking a random action when executing the policy
E_GREEDY_FLOOR = 0.1  # floor value of eps (cannot be smaller than that)
E_GREEDY_0 = 1.0  # initial value of eps
# Accounting for symmetries
SYM_EVAL_ENSEMBLE_AVG = True  # whether to average value over symmetric duplicates during evaluation
SYM_TRAIN_ADD_DUPLICATES = False  # whether to augment data by including symmetric duplicates during training step
SYM_TRAIN_RANDOMIZE = True  # whether to apply random symmetry transformations when generating the data (no duplicates)
# Additional DQN algo parameters
UPDATE_FROZEN_MODEL_EVERY = 1
DDQN = False  # whether to use Double DQN instead of original DQN
# Evaluation of the RL policy
POLICY_REF = 1  # heuristic policy to use for comparison
N_RUNS_STATS = None  # number of episodes used to compute the stats of a policy, set automatically if None
# Monitoring/Saving during the training
PRINT_INFO_EVERY = 10  # how often to print info on screen, in number of training iterations
SAVE_MODEL_EVERY = 50  # how often to save the current model, in number of training iterations

# ____________ ADVANCED OTHER PARAMETERS ______________________________________________________________________________
# Criteria for terminating an episode
STOP_t = None  # maximum number of steps per episode, set automatically if None
STOP_p = 1E-6  # episode stops when the probability that the source has been found is greater than 1 - STOP_p
# Saving
RUN_NAME = None  # prefix used for all output files, if None will use timestamp



