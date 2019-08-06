import math
import arrow
import numpy as np
from collections import defaultdict

class HypercubeQ(object):
    """
    Hypercube Queueing Model with Zero-line or Infinite-line Capacity

    For the ease of the implementation, there are two simplification comparing to the full model:
    * 1. We consider eta_{ij} = 1, i.e., there is only one optimal unit for each dispatch.
    * 2. We consider t_{ij} = tau_{ij}, i.e., the unit is always in its home atom when it is available.

    Reference:
    * Richard C. Larson. A hypercube queuing model for facility location and redistricting in urban 
      emergency services. Computers & Operations Research, 1(1):67 – 95, 1974.
    """


    def __init__(self, n_atoms, Lam=None, T=None, P=None, cap="zero", max_iter=10, q_len=100):
        """
        Params:
        * n_atoms:  number of geographical atoms (= number of response units),
        * Lam:      a vector of arrival rates of each geographical atoms,
        * T:        a matrix of average traffic time per dispatch (from atom i to atom j),
        * P:        a matrix of dispatch policy (the n-th unit at atom j),
        * cap:      `zero` or `inf`,
        * max_iter: maximum number of iteration for obtaining the steady-state probabilities,
        * q_len:    the reserved length of the queue.
        """
        # Model configuration
        # - line capacity
        self.cap     = cap
        # - number of geographical atoms (response units)
        self.n_atoms = n_atoms                    
        # - arrival rates vector: arrival rates for each atom
        self.Lam     = np.array(Lam, dtype=float) if Lam is not None else np.random.rand(self.n_atoms)
        # - traffic matrix:       average traffic time from atom i to atom j
        self.T       = np.array(T, dtype=float) if T is not None else np.random.rand(self.n_atoms, self.n_atoms)
        # - preference matrix:    preference matrix indicates the priority of response units to each atom
        self.P       = np.array(P, dtype=int) if P is not None else np.random.rand(self.n_atoms, self.n_atoms).argsort()

        assert self.n_atoms == self.Lam.shape[0] == self.T.shape[0] == \
               self.T.shape[1] == self.P.shape[0] == self.P.shape[1], \
               "Invalid shape of input parameters."

        # Model status
        # - state space ordered as a sequence represents a complete unit-step tour of the hypercube
        self.S                  = self._tour()
        self.all_busy_state_idx = np.array([ self.S[i].sum() for i in range(2 ** self.n_atoms) ]).argmax()
        self.all_zero_state_idx = 0
        # - upward transition rates matrix: a dictionary { (i,j) : lam_ij } (due to the sparsity of the matrix in nature)
        print("[%s] calculating upward transition rates ..." % arrow.now())
        self.Lam_ij = self._upward_transition_rates()
        # - steady-state probability for unsaturate states
        print("[%s] calculating steady-state probabilities ..." % arrow.now())
        self.Pi         = self._steady_state_probs(cap=self.cap, max_iter=max_iter)
        # - steady-state probability for saturate states (only for infinite-line capacity)
        self.Pi_Q       = np.array([ self._steady_state_probs_in_queue(j) for j in range(1, q_len) ]) if self.cap == "inf" else []
        # the probability that a randomly arriving call incurs a queue delay
        self.Pi_Q_prime = self.Pi_Q.sum() + self.Pi[self.all_busy_state_idx] if self.cap == "inf" else 0

        # Model evaluation metrics
        # - fraction of dispatches that send a unit n to a particular geographical atom j
        print("[%s] calculating dispatch fraction ..." % arrow.now())
        self.Rho_1, self.Rho_2 = self._dispatch_fraction(cap=self.cap)
        # - average travel time of each disptach for each response unit
        print("[%s] calculating average travel time ..." % arrow.now())
        self.Tu = self._average_travel_time(cap=self.cap)

    def _tour(self):
        """
        Tour Algorithm

        In order to tour the hypercube in a unit-step manner, this function is able to generate a 
        complete sequence S_1, S_2, ... of N-digit binary numbers, with 2^N unique members in the 
        sequence and with adjacent members being exactly unit-Hamming distance apart. Such a 
        sequence represents a complete unit-step tour of the hypercube.
        """
        # initialization
        S      = np.zeros((2 ** self.n_atoms, self.n_atoms))
        S[1,0] = 1    # S_0 = 0, S_1 = 1
        m, i   = 2, 2 # m: number of states that needs step backwards; i: index of the state
        # add "one" at i-th position and step backwards
        for n in range(1, self.n_atoms):
            S[i:i+m,n]  = 1                                 # add "one" at i-th position
            S[i:i+m,:n] = np.flip(S[int(i-m):i,:n], axis=0) # step backwards
            i          += m                                 # update index of the state
            m          *= 2                                 # update the number of states that needs step backwards
        return S

    def _upward_transition_rates(self):
        """
        An efficient method for generating upward transition rates from state i to state j of the  
        hypercube queueing model.

        For each geographical atom j we shall tour the hypercube in a unit-step fashion. 
        """
        Upoptn = self.__upward_optimal_neighbor() # upward optimal neighbor matrix
        Lam_ij = defaultdict(lambda: 0)           # upward transition rates dictionary initialization

        # iterative algorithm for generating upward transition rates
        for k in range(self.n_atoms):          # for each atom k
            for i in range(2 ** self.n_atoms): # for each state i
                if self.S[i].sum() < self.n_atoms:
                    Lam_ij[(i,Upoptn[k,i])] += self.Lam[k]
        return Lam_ij
    
    def __upward_optimal_neighbor(self):
        """
        A function that collects the upward optimal neighbor given atom k at state i according 
        to the dispatch policy.
        """
        # helper function that returns the state index given the state
        def state_index(s):
            for i in range(2 ** self.n_atoms):
                if np.count_nonzero(s - self.S[i]) == 0:
                    return i

        # calculate upward optimal neighbors matrix
        Upopts = np.zeros((self.n_atoms, 2 ** self.n_atoms), dtype=int)
        for k in range(self.n_atoms):                # for each atom k
            for i in range(2 ** self.n_atoms):       # for each state i (last state is excluded)
                idle_u = np.where(self.S[i] == 0)[0] # indices of idle response units
                if len(idle_u) != 0:
                    disp_u = self.P[k]               # ordered indices of response units for atom k according to dispatch policy 
                    for u in disp_u:                 # find out the first available idle unit to be assigned to atom k
                        if u in idle_u:
                            add         = np.zeros(self.n_atoms, dtype=int)
                            add[u]      = 1
                            upopts      = self.S[i] + add
                            Upopts[k,i] = state_index(upopts)
                            break
                else:
                    Upopts[k,i] = -1                 # for the all busy state, there is no upward neighbor
        return Upopts

    def _steady_state_probs(self, cap, max_iter):
        """
        A iterative procedure for obtaining the steady state probability on the hypercube. In a manner
        similar to point Jacobi iteration, we use the equation of detailed balance to determine the 
        values at successive iterations. 

        For all idle state, all busy state, and S_Q (more than N customers in the system), the steady   
        state probabilities can be calculated as a normal M/M/N queue with infinite-line capacity.
        """
        # steady state probabilities initialization
        def init_steady_state_prob(cap):
            Pi_0 = np.zeros(2 ** self.n_atoms)
            for n_busy in range(self.n_atoms + 1):
                denominator = sum([
                    self.Lam.sum() ** j / math.factorial(j)
                    for j in range(self.n_atoms + 1) ]) \
                    if cap == "zero" else \
                    sum([ 
                        (self.Lam.sum() ** j / math.factorial(j)) 
                        for j in range(self.n_atoms + 1) ]) + \
                    (self.Lam.sum() ** self.n_atoms / math.factorial(self.n_atoms)) * \
                    (self.Lam.sum() / self.n_atoms / (1 - self.Lam.sum() / self.n_atoms))
                n_states    = sum([ 1 for i in range(2 ** self.n_atoms) if self.S[i].sum() == n_busy ])
                init_P      = (self.Lam.sum() ** n_busy / math.factorial(n_busy)) / denominator / n_states
                for i in range(2 ** self.n_atoms):
                    if self.S[i].sum() == n_busy:
                        Pi_0[i] = init_P
            return Pi_0

        # point Jacobi iteration for all states except for all idle state, all busy state
        def iter_steady_state_prob(Pi_n):
            # initialize the steady state probabilities Pi_{n+1} for the next iteration
            Pi_n_1 = np.copy(Pi_n)
            # update the steady state probability of each state i
            for j in range(2 ** self.n_atoms):
                # except for all idle state, all busy state
                if self.S[j].sum() != 0 and self.S[j].sum() != self.n_atoms:
                    upward_sum   = 0
                    downward_sum = 0
                    for i in range(2 ** self.n_atoms):
                        # the k-th response unit that changed status (upward and downward in total)
                        changed_k = np.nonzero(self.S[j] - self.S[i])[0]
                        # only consider one-step changed states
                        if len(changed_k) == 1:
                            # upward transition state
                            if (self.S[j] - self.S[i]).sum() == 1:
                                upward_sum += Pi_n[i] * self.Lam_ij[(i,j)]
                            # downward transition state
                            elif (self.S[j] - self.S[i]).sum() == -1:
                                downward_sum += Pi_n[i] * 1 # self.Mu[changed_k[0]]
                    # update the j-th state in Pi_{n+1}
                    Pi_n_1[j] = (upward_sum + downward_sum) / (self.Lam.sum() + self.S[j].sum())
            return Pi_n_1
        
        # initialize all states
        Pi = init_steady_state_prob(cap)
        # update all states except for all idle state, all busy state
        for n in range(max_iter):
            Pi = iter_steady_state_prob(Pi)
        return Pi
    
    def _steady_state_probs_in_queue(self, n_waiting):
        """
        Return the probability of exactly `n_waiting` calls in queue, assuming steady state 
        conditions.
        """
        assert n_waiting >= 1, "n_waiting should larger than 1."
        denominator = sum([ 
            (self.Lam.sum() ** j / math.factorial(j)) 
            for j in range(self.n_atoms + 1) ]) + \
            (self.Lam.sum() ** self.n_atoms / math.factorial(self.n_atoms)) * \
            (self.Lam.sum() / self.n_atoms / (1 - self.Lam.sum() / self.n_atoms))
        Pi_Q_j = (self.Lam.sum() ** self.n_atoms / math.factorial(self.n_atoms)) * \
                 (self.Lam.sum() / self.n_atoms) ** n_waiting / denominator
        return Pi_Q_j

    def _dispatch_fraction(self, cap):
        """
        Return the fraction of dispatches that send a unit n to a particular geographical atom j
        as a matrix Rho. 

        * For zero-line capacity queue, the final result is Rho_1 while Rho_2 is 0.
        * For infinite-line capacity queue, 
          Rho_1 is the fraction of all dispatches that send unit n to atom j and incur no queue delay,
          Rho_2 is the fraction of all dispatches that send unit n to atom j and do incur a positive
          queue delay.
          The final result is the sum of Rho_1 and Rho_2.
        """
        # a helper function that returns the set of states in which unit n is an optimal unit to 
        # assign to a call from atom j.
        def states_optimal_dispatch(n, j):
            states = []
            for i in range(2 ** self.n_atoms):
                disp_u = self.P[j]
                idle_u = np.where(self.S[i] == 0)[0]
                if n in idle_u:
                    priority_u_n     = disp_u.tolist().index(n)                             # priority of unit n 
                    priority_u_other = [ 
                        disp_u.tolist().index(u) 
                        for u in idle_u if u != n]                                          # priority of other units
                    if len(priority_u_other) == 0 or priority_u_n <= min(priority_u_other): # if unit n has the highest priority
                        states.append(i)
            return states

        # E_{nj} dictionary
        E_nj = {}
        for n in range(self.n_atoms):
            for j in range(self.n_atoms):
                E_nj[(n,j)] = states_optimal_dispatch(n, j)
        E_nj[(n,j)] = states_optimal_dispatch(n, j)
        # fraction of all dispatches that send unit n to atom j and incur no queue delay
        Rho_1 = np.zeros((self.n_atoms, self.n_atoms), dtype=float)
        # fraction of all dispatches that send unit n to atom j and do incur a positive queue delay
        Rho_2 = np.zeros((self.n_atoms, self.n_atoms), dtype=float)
        # calculate Rho_1 and Rho_2
        for n in range(self.n_atoms):
            for j in range(self.n_atoms):
                if cap == "zero":
                    denominator = self.Lam.sum() * (1 - self.Pi[self.all_busy_state_idx])
                    numerator   = sum([ self.Lam[j] * self.Pi[i] 
                        for i in E_nj[(n, j)] ])
                    Rho_1[n,j]  = numerator / denominator
                else:
                    Rho_2[n,j]  = self.Lam[j] / self.Lam.sum() * self.Pi_Q_prime / self.n_atoms
                    Rho_1[n,j]  = sum([ self.Lam[j] / self.Lam.sum() * self.Pi[i] 
                        for i in E_nj[(n, j)] ])
        return  Rho_1, Rho_2

    def _average_travel_time(self, cap):
        """
        Return the average travel time of each dispatch for each response unit.
        """
        Tu  = np.zeros(self.n_atoms)
        f   = self.Lam / self.Lam.sum()
        T_Q = np.matmul(f, np.matmul(self.T, f))
        for n in range(self.n_atoms):
            if cap == "zero":
                numerator   = (self.T[n,:] * self.Rho_1[n,:]).sum() 
                denominator = self.Rho_1[n,:].sum()
                Tu[n]       = numerator / denominator
            else:
                numerator   = (self.T[n,:] * self.Rho_1[n,:]).sum() + T_Q * self.Pi_Q_prime / self.n_atoms
                denominator = self.Rho_1[n,:].sum() + self.Pi_Q_prime / self.n_atoms
                Tu[n]       = numerator / denominator
        return Tu