R_BAR = 2.5
DRAW_SOURCE = True  # if False, episodes will continue until the source is almost surely found (Bayesian setting)
POLICY = -2  # -1=RL, O=infotaxis, 1=space-aware infotaxis
# MODEL_PATH = "../learn/models/20220907-084621/20220907-084621_model"  # saved model for POLICY=-1, e.g., "../learn/models/20220201-230054/20220201-230054_model"
PERSEUS_PATH = "../../perseus/vf_rate_5.0_gamma_0.98_ic2_it_21_shaping_factor_0.1_shaping_power_1.0_nb_45000_epsilon_0.0_v2.pkl"
VISU_MODE = 1 # 0: run without video, 1: create video in the background, 2: create video and show live preview (slower)