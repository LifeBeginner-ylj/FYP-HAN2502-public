import numpy as np

class BayesianGameSimulator:
    
    def __init__(self, states, actions, prior, sender_utility, receiver_utility):
        self.states = states
        self.actions = actions
        self.prior = prior
        self.u_s = sender_utility
        self.u_r = receiver_utility

    def _calculate_posterior_belief(self, signal, signaling_scheme):
        """
        Calculate Receiver's posterior belief P(state | signal) using Bayes' Rule.
        P(state | signal) = [P(signal | state) * P(state)] / P(signal)
        """
        prob_signal = 0.0 # P(signal)
        for state in self.states: 
            # P(signal | state) * P(state)
            prob_signal += signaling_scheme[state].get(signal, 0) * self.prior[state]
            
        if prob_signal == 0:
            # Avoid division by zero if signal is impossible
            # Return prior belief and 0 probability
            return self.prior, 0.0 

        posterior_belief = {}
        for state in self.states:
            prob_signal_given_state = signaling_scheme[state].get(signal, 0)
            prob_state = self.prior[state]
            # Bayes' Rule
            posterior_belief[state] = (prob_signal_given_state * prob_state) / prob_signal
            
        return posterior_belief, prob_signal

    def _get_receiver_optimal_action(self, posterior_belief):
        """
        Determine the rational Receiver's optimal action a*(m).
        """
        max_expected_utility = -float('inf')
        optimal_action = None
        
        for action in self.actions:
            expected_utility = 0.0
            for state in self.states:
                # E[U_R(a, w) | signal] = Sum [ U_R(a, w) * P(w | signal) ]
                expected_utility += self.u_r[action][state] * posterior_belief[state]
            
            if expected_utility > max_expected_utility:
                max_expected_utility = expected_utility
                optimal_action = action
                
        return optimal_action # a*(m)

    def calculate_sender_expected_utility(self, signaling_scheme):
        """
        Calculate the Sender's total expected utility.
        E[U_S] = Sum_w P(w) * [ Sum_m P(m | w) * U_S(a*(m), w) ]
        """
        # 1. Get all possible signals M from the scheme
        signals = set()
        for state_signals in signaling_scheme.values():
            signals.update(state_signals.keys())
            
        # 2. For each signal m, find the receiver's optimal action a*(m)
        optimal_action_for_signal = {}
        prob_of_signal = {} # Store P(m)
        
        for signal in signals:
            posterior_belief, prob_m = self._calculate_posterior_belief(signal, signaling_scheme)
            optimal_action_for_signal[signal] = self._get_receiver_optimal_action(posterior_belief)
            prob_of_signal[signal] = prob_m

        # 3. Calculate Sender's total expected utility
        total_expected_utility = 0.0
        
        for state in self.states:
            utility_for_state = 0.0
            for signal in signals:
                prob_signal_given_state = signaling_scheme[state].get(signal, 0) # P(m | w)
                action_taken = optimal_action_for_signal[signal] # a*(m)
                sender_utility = self.u_s[action_taken][state] # U_S(a*(m), w)
                
                utility_for_state += prob_signal_given_state * sender_utility
                
            total_expected_utility += self.prior[state] * utility_for_state # Sum_w P(w) * [...]
            
        return total_expected_utility