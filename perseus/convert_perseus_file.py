"""Load Perseus policy, extract useful data and save it."""
import numpy as np
import pickle

FILENAME = "vf_rate_5.0_gamma_0.98_ic2_it_21_shaping_factor_0.1_shaping_power_1.0_nb_45000_epsilon_0.0_v2.pkl"
INPUT_FILENAME = "/home/aurore/Downloads/" + FILENAME
OUTPUT_FILENAME = "./" + FILENAME
OUTPUT = {
    "alphas": None,
    "actions": None,
    "discount": 0.98,
    "shaping": "D",
    "shaping_coef": 0.1,
}


def convert(input_filename, output):
    with open(input_filename, 'rb') as f:
        vf = pickle.load(f)
    output["alphas"] = []
    output["actions"] = []
    for alphavec in vf.alphas:
        output["alphas"].append(alphavec.data)
        if np.array_equal(alphavec.action, [1, 0]):
            action = 1
        elif np.array_equal(alphavec.action, [-1, 0]):
            action = 0
        elif np.array_equal(alphavec.action, [0, 1]):
            action = 3
        elif np.array_equal(alphavec.action, [0, -1]):
            action = 2
        else:
            raise Exception("This action is not defined")
        output["actions"].append(action)
    return output


if __name__ == "__main__":
    OUTPUT = convert(INPUT_FILENAME, OUTPUT)
    with open(OUTPUT_FILENAME, 'wb') as f:
        pickle.dump(OUTPUT, f, pickle.HIGHEST_PROTOCOL)
