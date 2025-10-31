def get_full_revelation_scheme(states):
    """
    Generates the Full Revelation scheme.
    Signal M is identical to state Ω. π(ω) = ω.
    """
    scheme = {}
    for state_omega in states:
        scheme[state_omega] = {}
        for state_m in states:
            # Send signal 'state_m' with 100% prob if state is 'state_omega'
            scheme[state_omega][state_m] = 1.0 if state_omega == state_m else 0.0
    return scheme

def get_no_revelation_scheme(states):
    """
    Generates the No Revelation scheme.
    Always sends the same signal regardless of the state.
    """
    scheme = {}
    single_signal = "NoSignal"
    for state in states:
        scheme[state] = {single_signal: 1.0}
    return scheme

def calculate_theoretical_optimum(scenario_name, game_definition):
    """
    Returns the pre-calculated theoretical optimum utility and scheme.
    
    MUST hardcode your mathematically calculated results here.
    """

    # Example 1: Hardcoded results for 'SimpleBinaryGame'
    if scenario_name == "SimpleBinaryGame":
        # Optimal strategy: No Revelation (pooling)
        # The receiver's expected utility from Accept is 0.5*1 + 0.5*(-1) = 0
        # When indifferent, if receiver chooses Accept, sender gets 1.0
        # E[U_S] = 0.5 * 1 + 0.5 * 1 = 1.0
        optimal_scheme = get_no_revelation_scheme(game_definition['states'])
        max_utility = 1.0 
        return optimal_scheme, max_utility
        
    # Example 2: Hardcoded results for 'QualityControl'
    elif scenario_name == "QualityControl":
        # Optimal strategy: Pool High & Medium Quality, Separate Low Quality
        # Or equivalently: Full Revelation (both achieve the same utility)
        # SignalA triggers Buy (from H or M), SignalB triggers Dont Buy (from L)
        # E[U_S] = P(H)*10 + P(M)*10 + P(L)*0 = 0.5*10 + 0.2*10 + 0.3*0 = 7.0
        optimal_scheme = {
            'High Quality': {'SignalA': 1.0, 'SignalB': 0.0},
            'Medium Quality': {'SignalA': 1.0, 'SignalB': 0.0},
            'Low Quality': {'SignalA': 0.0, 'SignalB': 1.0} 
        }
        max_utility = 7.0
        return optimal_scheme, max_utility
        
    else:
        # Undefined scenarios
        print(f"Warning: Theoretical optimum for {scenario_name} is not defined.")
        return None, -float('inf')