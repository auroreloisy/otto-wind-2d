R_BAR = 2.5
DRAW_SOURCE = True  # if False, episodes will continue until the source is almost surely found (Bayesian setting)
TRUE_SOURCE_IS_FAKE_SOURCE = True
POLICY = 0  # -1=RL, O=infotaxis, 1=space-aware infotaxis
MODEL_PATH = None  # saved model for POLICY=-1, e.g., "../learn/models/20220201-230054/20220201-230054_model"

ADAPTIVE_N_RUNS = True  # if true, N_RUNS is increased until the estimated error is less than REL_TOL
N_RUNS = None  # number of episodes to compute (starting guess if ADAPTIVE_N_RUNS)
REL_TOL = 0.01  # tolerance on the relative error on the mean number of steps to find the source (if ADAPTIVE_N_RUNS)
MAX_N_RUNS = 10000  # maximum number of runs (if ADAPTIVE_N_RUNS)