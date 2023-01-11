R_BAR = 0.25
DRAW_SOURCE = False  # if False, episodes will continue until the source is almost surely found (Bayesian setting)
POLICY = -2  # -1=RL, O=infotaxis, 1=space-aware infotaxis
MODEL_PATH = None  # saved model for POLICY=-1, e.g., "../learn/models/20220201-230054/20220201-230054_model"
# ALPHAVEC_PATH = "../../perseus/vf_rate_5.0_gamma_0.98_ic2_it_21_shaping_factor_0.1_shaping_power_1.0_nb_45000_epsilon_0.0_v2.pkl"
ALPHAVEC_PATH = "../../sarsop/sarsop_policy_windy_low_emission_compact.pkl"

ADAPTIVE_N_RUNS = False  # if true, N_RUNS is increased until the estimated error is less than REL_TOL
N_RUNS = 10000  # number of episodes to compute (starting guess if ADAPTIVE_N_RUNS)
REL_TOL = 0.01  # tolerance on the relative error on the mean number of steps to find the source (if ADAPTIVE_N_RUNS)
MAX_N_RUNS = 10000  # maximum number of runs (if ADAPTIVE_N_RUNS)
if POLICY < 0:
    N_PARALLEL = 1
else:
    N_PARALLEL = -1
