#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Definition of the Perseus policy (policy based on alpha vectors)."""

import os
import numpy as np
import pickle
from copy import deepcopy
import tensorflow as tf
from .policy import Policy, policy_name

# _____________________  parameters  _____________________
EPSILON = 1e-10
EPSILON_CHOICE = EPSILON
# ________________________________________________________


def einsum_value_single_belief(belief, alphas):
    if len(belief.shape) == 3:
        dot = np.einsum('klm,jklm->j', belief, alphas)
        index = np.argmax(dot)
        value = dot[index]
        return value, index
    dot = np.einsum('kl,jkl->j', belief, alphas)
    index = np.argmax(dot)
    value = dot[index]
    return value, index


class ValueFunction:
    """
    Args:
            alphas (list of ndarray):
                list of alpha vectors
            actions (list of int):
                list of action associated to alpha vectors
            alpha_array (ndarray):
                alpha vectors, with shape (n_alphas, n_grid_x, n_grid_y)
    """
    def __init__(self, alphas, actions):
        self.alphas = alphas
        self.actions = actions
        self.alpha_array = np.array(alphas)

    def value(self, belief, alpha_set=None, parallel=False):
        """Compute the current estimated value of a belief.
        Usually should be done with parallel=True if multiple cores are available

        """
        if alpha_set is None:
            alpha_set = self.alphas

        if parallel:
            value, index = einsum_value_single_belief(belief, self.alpha_array)
            return value, int(index)

        else:
            best_val = -np.inf
            best_index = None
            for index, alpha in enumerate(alpha_set):
                val = np.sum(belief * alpha.data)
                if val > best_val:
                    best_val = val
                    best_index = index
            if best_index is None:
                raise RuntimeError('best index is None')
            return best_val, best_index

    def load(self, filename):
        with open(filename + '.pkl', 'rb') as f:
            vf = pickle.load(f)
            self.alphas = vf.alphas
            self.alpha_array = vf.alpha_array


class PerseusPolicy(Policy):
    """
        A Perseus policy, that is, a policy based on alpha vectors

        Args:
            env (SourceTracking):
                an instance of the source-tracking POMDP
            filepath (str):
                path to the file containing the Perseus policy


        Attributes:
            env (SourceTracking):
                source-tracking POMDP
            vf (ValueFunction):
                value function defined from alpha vector
            discount (float):
                discount factor
            shaping (str):
                shaping function
            shaping_coef (float):
                shaping coef
            policy_index (int):
                policy index, set to -2
            policy_name (str):
                name of the policy



    """
    def __init__(
            self,
            env,
            filepath,
            parallel=False,
    ):
        super().__init__(policy=-2)  # sets policy_index and policy_name

        self.env = env
        self.parallel = parallel

        perseus = self._load(filepath)
        self.vf = ValueFunction(alphas=perseus["alphas"], actions=perseus["actions"])
        self.discount = perseus["discount"]
        self.shaping = perseus["shaping"]
        self.shaping_coef = perseus["shaping_coef"]

        self.policy_name = self.policy_name + \
                           " (discount=" + str(self.discount) + \
                           ", shaping=" + str(self.shaping_coef) + self.shaping + \
                           ", alphas=" + str(len(self.vf.alphas)) + ")"

    def _choose_action(self, ):

        if self.policy_index == -2:
            assert policy_name(self.policy_index) == "Perseus"
            action_chosen, _ = self._get_perseus_action(self.env.p_source, self.env.agent)
        else:
            raise Exception("The policy " + str(self.policy) + " does not exist (yet)!")

        return action_chosen

    # __ POLICY DEFINITIONS _______________________________________

    def _get_perseus_action(self, p, agent):
        belief = self._perseus_belief(p, agent)
        value, best_index = self.vf.value(belief, parallel=self.parallel)
        return self.vf.actions[best_index], value

    def _perseus_belief(self, p, agent):
        dims = p.shape
        b = np.pad(p, ((0, dims[0] - 1), (0, dims[1] - 1)))
        b = np.flip(b)
        b = np.roll(b, (1 + agent[0], 1 + agent[1]), axis=(0, 1))
        return b

    def _load(self, filename):
        with open(filename, 'rb') as f:
            perseus = pickle.load(f)
        return perseus

