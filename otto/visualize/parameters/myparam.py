R_BAR = 2.5
DRAW_SOURCE = True  # if False, episodes will continue until the source is almost surely found (Bayesian setting)
TRUE_SOURCE_IS_FAKE_SOURCE = True
POLICY = -1  # -1=RL, O=infotaxis, 1=space-aware infotaxis
MODEL_PATH = "../learn/models/20220907-084621/20220907-084621_model"  # saved model for POLICY=-1, e.g., "../learn/models/20220201-230054/20220201-230054_model"