#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Provides the SourceTracking class, to simulate the source-tracking POMDP."""

import numpy as np
import warnings
from copy import deepcopy
from scipy.special import kv
from scipy.special import kn
from scipy.special import gamma as Gamma
from scipy.stats import poisson as Poisson_distribution

# _____________________  parameters  _____________________
EPSILON = 1e-10
DEBUG = False
# ________________________________________________________


class SourceTracking:
    """Environment used to simulate the source-tracking POMDP.

    Args:
        R_bar (float):
            dimensionless source emission rate
        V_bar (float):
            dimensionless mean wind
        tau_bar (float):
            dimensionless turbulence coherence time
        draw_source (bool, optional):
            whether to actually draw the source location (otherwise uses Bayesian framework) (default=False)
        dummy (bool, optional):
                set automatic parameters but does not initialize the POMDP (default=False)

    Attributes:
        R_bar (float):
            dimensionless source emission rate
        V_bar (float):
            dimensionless mean wind
        tau_bar (float):
            dimensionless turbulence coherence time
        shape (tuple of int):
            grid size
        Ndim (int):
            number of space dimensions
        Nhits (int):
            number of possible hit values
        norm_Poisson ('Euclidean', 'Manhattan' or 'Chebyshev', optional):
            norm used for hit detections (default='Euclidean')
        draw_source (bool):
            whether a source location is actually drawn  (otherwise uses Bayesian framework)
        initial_hit (int):
            value of the initial hit
        Nactions (int):
            number of possible actions
        NN_input_shape (tuple(int)):
            shape of the input array for neural network models
        agent (list(int)):
            current agent location
        p_source (ndarray):
            current probability distribution of the source location)
        obs (dict):
            current observation ("hit" and "done")
        hit_map (ndarray):
            number of hits received for each location (-1 for cells not visited yet)
        cumulative_hits (int):
            cumulated sum of hits received (ignoring initial hit)
        agent_near_boundaries (bool):
            whether the agent is currently near a boundary
        agent_stuck (bool):
            whether the agent is currently stuck in an "infinite" loop



    """

    def __init__(
        self,
        R_bar=2.5,
        V_bar=2,
        tau_bar=150,
        draw_source=False,
        dummy=False,
    ):
        self.shape = (81, 41)
        if DEBUG:
            self.shape = (21, 11)
        self.Ndim = len(self.shape)
        self.Nhits = 2

        self.R_bar = R_bar
        self.V_bar = V_bar
        self.tau_bar = tau_bar
        self.lambda_bar = np.sqrt((self.tau_bar/self.V_bar**2)/(1 + self.tau_bar / 4))

        self.norm_Poisson = 'Euclidean'
        if not (self.norm_Poisson in ('Euclidean', 'Manhattan', 'Chebyshev')):
            raise Exception("norm_Poisson must be 'Euclidean', 'Manhattan' or 'Chebyshev'")

        self.Nactions = 2 * self.Ndim
        # if stand_still:
        #     self.Nactions += 1

        self.draw_source = draw_source

        self.NN_input_shape = tuple([2 * n - 1 for n in self.shape])

        self.initial_hit = None
        self.p_source = None
        self.agent = None
        self.hit_map = None
        self.cumulative_hits = None
        self.agent_near_boundaries = None
        self.agent_stuck = None
        self.obs = None
        self._agento, self._agentoo = None, None
        self._repeated_visits = None

        if not dummy:
            self.restart()

    def restart(self):
        """Restart the search.
        """
        self.initial_hit = 1
        if self.initial_hit > self.Nhits - 1:
            raise Exception("initial_hit cannot be > Nhits - 1")

        self.hit_map = -np.ones(self.shape, dtype=int)
        if self.Ndim == 2:
            self.agent = [65, 20]
            if DEBUG:
                self.agent = [15, 5]
        else:
            raise Exception("Only 2D is implemented")
        self._init_distributed_source()
        if self.draw_source:
            self._draw_a_source()

        self.cumulative_hits = 0
        self.agent_near_boundaries = 0
        self.agent_stuck = False
        self.obs = {"hit": 1, "done": False}

        self._agento = [1] * self.Ndim  # position 1 step ago (arbitrary init value)
        self._agentoo = [2] * self.Ndim  # position 2 steps ago (arbitrary init value)
        self._repeated_visits = 0  # to detect back and forth motion

    def step(self, action, hit=None, quiet=False):
        """
        Make a step in the source-tracking environment:

           1. The agent moves to its new position according to `action`,
           2. The agent receives a hit or the source is found,
           3. The belief (self.p_source) and the hit map (self.hit_map) are updated.

        Args:
            action (int): action of the agent
            hit (int, optional): prescribed number of hits,
                if None (default) the number of hits is chosen randomly according to its probability
            quiet (bool, optional): whether to print when agent is attempting a forbidden move (default=False)

        Returns:
            hit (int): number of hits received
            p_end (float): probability of having found the source (relevant only if not draw_source)
            done (bool): whether the source has been found (relevant only if draw_source)

        """
        hit, p_end, done = self._execute_action(action, hit, quiet)
        self._update_after_hit(hit, done)

        return hit, p_end, done

    # __ POMDP UPDATES _______________________________________
    def _execute_action(self, action, hit=None, quiet=False):
        self._agentoo = self._agento
        self._agento = self.agent

        # move agent
        self.agent, is_move_possible = self._move(action, self.agent)
        if (not is_move_possible) and (not quiet):
            print("This move is not possible: agent =", self.agent, "cannot do action =",  action)
        self.agent_near_boundaries = self._is_agent_near_boundaries(n_boundary=1)
        self.agent_stuck = self._is_agent_stuck()

        if self.draw_source:
            if self.norm_Poisson == 'Manhattan':
                ord = 1
            elif self.norm_Poisson == 'Euclidean':
                ord = 2
            elif self.norm_Poisson == 'Chebyshev':
                ord = float("inf")
            else:
                raise Exception("This norm is not implemented")
            d = np.linalg.norm(np.asarray(self.agent) - np.asarray(self.source), ord=ord)
            x = self.agent[0] - self.source[0]

            if d > EPSILON:
                done = False
                p_end = 0

                # Picking randomly the number of hits
                mu = self._mean_number_of_hits(d, x)
                probability = np.zeros(self.Nhits)
                sum_proba = 0
                for h in range(self.Nhits - 1):
                    probability[h] = self._Poisson(mu, h)
                    sum_proba += self._Poisson(mu, h)
                probability[self.Nhits - 1] = np.maximum(0, 1.0 - sum_proba)
                if hit is None:
                    hit = np.random.RandomState().choice(
                        range(self.Nhits), p=probability
                    )
            else:
                done = True
                p_end = 1
                hit = -2

        else:
            done = False

            p_end = self.p_source[tuple(self.agent)]
            if p_end > 1 - EPSILON:
                done = True

            # Source not in self.agent
            new_p_source = deepcopy(self.p_source)
            new_p_source[tuple(self.agent)] = 0.0
            if np.sum(new_p_source) > EPSILON:
                new_p_source /= np.sum(new_p_source)
            else:
                done = True

            if not done:
                # extracting the evidence matrix for Bayesian inference
                p_evidence = self._extract_N_from_2N(input=self.p_Poisson, origin=self.agent)

                # Compute hit proba
                p_hit_table = np.zeros(self.Nhits)
                for h in range(self.Nhits):
                    p_hit_table[h] = np.maximum(
                        0,
                        np.sum(new_p_source * p_evidence[h])
                    )
                sum_p_hit = np.sum(p_hit_table)
                if np.abs(sum_p_hit - 1.0) < EPSILON:
                    p_hit_table /= sum_p_hit
                else:
                    print("sum_p_hit_table = ", sum_p_hit)
                    raise Exception("p_hit_table does not sum to 1")

                # Picking randomly the number of hits
                if hit is None:
                    hit = np.random.RandomState().choice(range(self.Nhits), p=p_hit_table)

            else:
                hit = -2

        if not done:
            self.cumulative_hits += hit

        return hit, p_end, done
    
    def _update_after_hit(self, hit, done=None):
        """Update of the hit_map and p_source when receiving hits.

        Args:
            hit (int): number of hits received
            done (bool): whether the unique source is found
        """
        if hit is not None:
            self._update_hit_map(hit)
            self._update_obs(hit, done)
            self._update_p_source(hit, done)
            
    def _update_hit_map(self, hit=0):
        self.hit_map[tuple(self.agent)] = hit

    def _update_obs(self, hit, done):
        self.obs["hit"] = hit
        self.obs["done"] = done

    def _update_p_source(self, hit=0, done=None):
        if done:
            self.p_source = np.zeros(self.shape)
            self.p_source[tuple(self.agent)] = 1.0
            self.entropy = 0.0
        else:
            self.p_source[tuple(self.agent)] = 0
            p_evidence = self._extract_N_from_2N(input=self.p_Poisson, origin=self.agent)
            self.p_source *= p_evidence[hit]
            self.p_source[(self.p_source < 0.0) & (self.p_source > -1e-15)] = 0.0

            if np.sum(self.p_source) > EPSILON:
                self.p_source /= np.sum(self.p_source)
            self.entropy = self._entropy(self.p_source)

    def _move(self, action, agent):
        """Move the agent according to action.

        Args:
            action (int): action chosen
            agent (list of int): position of the agent

        Returns:
            new_agent (list of int): new position of the agent
            is_move_possible (bool): whether the action was allowed

        """
        is_move_possible = True
        new_agent = deepcopy(agent)
        axis = action // 2
        if axis < self.Ndim:
            direction = 2 * (action % 2) - 1
            if direction == -1:
                if agent[axis] > 0:
                    new_agent[axis] -= 1
                else:
                    is_move_possible = False
            elif direction == 1:
                if agent[axis] < self.shape[axis] - 1:
                    new_agent[axis] += 1
                else:
                    is_move_possible = False
        elif action == 2 * self.Ndim:
            pass  # do not move
        else:
            raise Exception("This action is outside the allowed range")

        return new_agent, is_move_possible
    
    # __ HIT DETECTION _______________________________________
    def _mean_number_of_hits(self, distance, x_position):
        # x_position = x_agent - x_source
        distance = np.array(distance)
        distance[distance == 0] = 1.0
        x_position = np.array(x_position)
        if self.Ndim == 2:
            mu = self.R_bar / distance * np.exp(0.5 * self.V_bar * x_position - distance / self.lambda_bar)
        else:
            raise Exception("Problem with the number of dimensions")
        return mu

    def _Poisson_unbounded(self, mu, h):
        p = Poisson_distribution(mu).pmf(h)
        return p

    def _Poisson(self, mu, h):
        if h < self.Nhits - 1:   # = Poisson(mu,hit=h)
            p = self._Poisson_unbounded(mu, h)
        elif h == self.Nhits - 1:     # = Poisson(mu,hit>=h)
            sum = 0.0
            for k in range(h):
                sum += self._Poisson_unbounded(mu, k)
            p = 1 - sum
        else:
            raise Exception("h cannot be > Nhits - 1")
        return p
    
    def _compute_p_Poisson(self):
        shape = [1 + 2 * n for n in self.shape]  # note: this could be reduced to size 2N - 1
        origin = list(self.shape)
        d = self._distance(shape=shape, origin=origin, norm=self.norm_Poisson)
        x = self._x_position(shape=shape, origin=origin)
        mu = self._mean_number_of_hits(d, x)
        mu[tuple(origin)] = 0.0

        self.p_Poisson = np.zeros([self.Nhits] + list(shape))
        sum_proba = np.zeros(shape)
        for h in range(self.Nhits):
            self.p_Poisson[h] = self._Poisson(mu, h)
            sum_proba += self.p_Poisson[h]
            if h < self.Nhits - 1:
                sum_is_one = np.all(abs(sum_proba - 1) < EPSILON)
                if sum_is_one:
                    raise Exception(str('Nhits is too large, reduce it to Nhits = ' + str(h + 1)
                                        + ' or lower (higher values have zero probabilities)'))

        if not np.all(sum_proba == 1.0):
            raise Exception("_compute_p_Poisson: sum proba is not 1")

        # by definition: p_Poisson(origin) = 0
        for h in range(self.Nhits):
            self.p_Poisson[tuple([h] + origin)] = 0.0

    # __ INITIALIZATION AND AUTOSET _______________________________________
    def _draw_a_source(self):
        prob = self.p_source.flatten()
        index = np.random.RandomState().choice(np.prod(self.shape), size=1, p=prob)[0]
        self.source = list(np.unravel_index(index, shape=self.shape))

    def _init_distributed_source(self, ):
        if not hasattr(self, 'p_Poisson'):
            self._compute_p_Poisson()
        self.p_source = np.ones(self.shape) / (np.prod(self.shape) - 1)
        self.p_source[tuple(self.agent)] = 0.0
        self._update_p_source(hit=self.initial_hit)
        self._update_hit_map(hit=self.initial_hit)

    # __ LOW LEVEL UTILITIES _______________________________________
    def _entropy(self, array, axes=None):
        log2 = np.zeros(array.shape)
        indices = array > EPSILON
        log2[indices] = -np.log2(array[indices])
        return np.sum(array * log2, axis=axes)

    def _distance(self, shape, origin, norm='Euclidean'):
        Ndim = len(shape)
        coord = np.mgrid[tuple([range(n) for n in shape])]
        for i in range(Ndim):
            coord[i] -= origin[i]
        d = np.zeros(shape)
        if norm == 'Manhattan':
            for i in range(Ndim):
                d += np.abs(coord[i])
            return d
        elif norm == 'Euclidean':
            for i in range(Ndim):
                d += (coord[i]) ** 2
            d = np.sqrt(d)
            return d
        elif norm == 'Chebyshev':
            d = np.amax(np.abs(coord), axis=0)
            return d
        else:
            raise Exception("This norm is not implemented")

    def _x_position(self, shape, origin):  # agent relative to source, origin=agent
        coord = np.mgrid[tuple([range(n) for n in shape])]
        x = origin[0] - coord[0]
        return x

    def _is_agent_near_boundaries(self, n_boundary):
        # is the agent within n_boundary cell(s) of a boundary of the computational domain?
        for axis in range(self.Ndim):
            if (self.agent[axis] >= self.shape[axis] - 1 - n_boundary) or (
                    self.agent[axis] <= n_boundary
            ):
                return 1
        return 0

    def _is_agent_stuck(self):
        return False  # disabled
        # agent_stuck = False
        # if self._agentoo == self.agent:
        #     self._repeated_visits += 1
        # else:
        #     self._repeated_visits = 0
        # if self._repeated_visits > 8:
        #     agent_stuck = True
        # return agent_stuck

    def _extract_N_from_2N(self, input, origin):
        if len(origin) != self.Ndim:
            raise Exception("_extract_N_from_2N: len(origin) is different from Ndim")
        off = len(input.shape) - len(self.shape)
        if off < 0:
            raise Exception("bug, should not happen")
        if np.all([input.shape[off + axis] == 2 * self.shape[axis] + 1 for axis in range(self.Ndim)]):
            index = np.array(self.shape) - origin
        elif np.all([input.shape[off + axis] == 2 * self.shape[axis] - 1 for axis in range(self.Ndim)]):
            index = np.array([n - 1 for n in self.shape]) - origin
        else:
            raise Exception("_extract_N_from_2N(): dimension of input must be 2N-1 or 2N+1")
        if self.Ndim == 1:
            output = input[..., index[0]:index[0] + self.shape[0]]
        elif self.Ndim == 2:
            output = input[...,
                         index[0]:index[0] + self.shape[0],
                         index[1]:index[1] + self.shape[1]]
        elif self.Ndim == 3:
            output = input[...,
                         index[0]:index[0] + self.shape[0],
                         index[1]:index[1] + self.shape[1],
                         index[2]:index[2] + self.shape[2]]
        elif self.Ndim == 4:
            output = input[...,
                         index[0]:index[0] + self.shape[0],
                         index[1]:index[1] + self.shape[1],
                         index[2]:index[2] + self.shape[2],
                         index[3]:index[3] + self.shape[3]]
        else:
            raise Exception("_extract_N_from_2N() not implemented for Ndim > 4")
        return output

    # __ INPUT TO VALUE FUNCTION _______________________________________
    def _centeragent(self, p, agent):
        """Return the probability density of the source centered on the agent

        Args:
            p (numpy array): initial probability in a non-centered environment
            agent (list): vector position of the agent

        Returns:
            numpy array: probability density centered on the agent (tensor of size (2 * N - 1) ** Ndim)
        """
        result = np.zeros([2 * n - 1 for n in self.shape])
        if self.Ndim == 1:
            result[self.shape[0] - 1 - agent[0]:2 * self.shape[0] - 1 - agent[0]] = p
        elif self.Ndim == 2:
            result[
                self.shape[0] - 1 - agent[0]:2 * self.shape[0] - 1 - agent[0],
                self.shape[1] - 1 - agent[1]:2 * self.shape[1] - 1 - agent[1],
            ] = p
        elif self.Ndim == 3:
            result[
                self.shape[0] - 1 - agent[0]:2 * self.shape[0] - 1 - agent[0],
                self.shape[1] - 1 - agent[1]:2 * self.shape[1] - 1 - agent[1],
                self.shape[2] - 1 - agent[2]:2 * self.shape[2] - 1 - agent[2],
            ] = p
        else:
            raise Exception("_centeragent is not implemented for Ndim > 3")

        return result

    # __ REWARD SHAPING _______________________________________
    def shaping(self, which, p_source, agent):
        if which == "0":
            return 0
        else:
            # WARNING: must be zero for the terminal state
            if not hasattr(self, 'Manhattan_array'):
                shape = tuple([2 * n + 1 for n in self.shape])
                self.Manhattan_array = self._distance(shape=shape, origin=self.shape, norm="Manhattan")

            dist = self._extract_N_from_2N(input=self.Manhattan_array, origin=agent)
            D = np.sum(p_source * dist)

            if which == "D":
                return D
            else:
                # WARNING: if using something else, may need to remove the positivity constraint on the NN
                raise Exception("This reward shaping function is not implemented")


