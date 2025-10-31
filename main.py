import pandas as pd
import os # Added for creating 'results' directory
from simulator import BayesianGameSimulator
import baselines
import llm_client
from scenarios import all_scenarios

# --- Configuration ---

# Number of times to run the LLM for each scenario to test robustness
NUM_RUNS_PER_SCENARIO = 5 

# Specify the LLM provider. Use "openai" for real calls,
# or "mock" for fast, free testing (as defined in llm_client.py)
# LLM_PROVIDER = "openai" 
LLM_PROVIDER = "poe-Claude-3.5-Sonnet"

def run_experiment(scenarios, num_runs_per_scenario=NUM_RUNS_PER_SCENARIO):
    """
    Main experiment loop.
    """
    
    results = []
    total_llm_attempts = 0
    successful_llm_runs = 0
    
    # Ensure the 'results' directory exists
    os.makedirs("results", exist_ok=True)
    
    for scenario in scenarios:
        print(f"--- Running Scenario: {scenario['name']} ---")
        
        # 1. Initialize the game simulator (the "Referee")
        game_def = {
            'states': scenario['states'],
            'actions': scenario['actions'],
            'prior': scenario['prior'],
            'u_s': scenario['u_s'],
            'u_r': scenario['u_r']
        }
        sim = BayesianGameSimulator(
            states=scenario['states'],
            actions=scenario['actions'],
            prior=scenario['prior'],
            sender_utility=scenario['u_s'],
            receiver_utility=scenario['u_r']
        )
        
        # 2. Calculate Baseline Utilities
        full_rev_scheme = baselines.get_full_revelation_scheme(scenario['states'])
        u_full_rev = sim.calculate_sender_expected_utility(full_rev_scheme)
        
        no_rev_scheme = baselines.get_no_revelation_scheme(scenario['states'])
        u_no_rev = sim.calculate_sender_expected_utility(no_rev_scheme)
        
        # Find the worst of the two simple baselines
        worst_baseline_util = min(u_full_rev, u_no_rev)
        
        # 3. Calculate Theoretical Optimum (the "ceiling")
        opt_scheme, u_opt = baselines.calculate_theoretical_optimum(scenario['name'], game_def)
        
        print(f"  Baseline - Full Revelation: {u_full_rev:.4f}")
        print(f"  Baseline - No Revelation: {u_no_rev:.4f}")
        print(f"  Theoretical Optimum: {u_opt:.4f}")
        
        # 4. Run LLM multiple times
        for i in range(num_runs_per_scenario):
            print(f"  LLM Run {i+1}/{num_runs_per_scenario}...")
            total_llm_attempts += 1
            
            # 3. Get LLM-generated strategy
            llm_scheme, is_valid, message = llm_client.get_llm_strategy(
                **game_def, 
                provider=LLM_PROVIDER
            )
            
            # Initialize metrics for this run
            u_llm = None
            optimality_gap = None
            rpl = None
            
            if is_valid:
                successful_llm_runs += 1
                # 5. Run the valid LLM strategy in the simulator
                u_llm = sim.calculate_sender_expected_utility(llm_scheme)
                print(f"    LLM Utility: {u_llm:.4f} (Valid)")
                
                # 6. Calculate Evaluation Metrics
                
                # Metric 1: Optimality Gap
                # (How far is the LLM from the perfect score?)
                if u_opt > 0: # Avoid division by zero
                    optimality_gap = (u_opt - u_llm) / u_opt #
                
                # Metric 2: Relative Performance Level (RPL)
                # (How much did the LLM improve over the worst baseline?)
                denom_rpl = u_opt - worst_baseline_util
                if denom_rpl > 0: # Avoid division by zero
                    rpl = (u_llm - worst_baseline_util) / denom_rpl #
                
            else:
                print(f"    LLM Run Failed: {message}")

            # Store results for this run
            results.append({
                "scenario": scenario['name'],
                "run": i + 1,
                "u_llm": u_llm,
                "u_theoretical_optimum": u_opt, #
                "u_full_revelation": u_full_rev,
                "u_no_revelation": u_no_rev,
                "u_worst_baseline": worst_baseline_util, #
                "optimality_gap": optimality_gap, #
                "rpl": rpl, #
                "is_valid_scheme": is_valid, #
                "llm_provider": LLM_PROVIDER
            })

    # --- Experiment Finished ---
    
    # Calculate final metrics
    scheme_validity_rate = successful_llm_runs / total_llm_attempts if total_llm_attempts > 0 else 0 #
    
    # Save all results to CSV
    results_df = pd.DataFrame(results)
    output_path = "results/experiment_results.csv"
    results_df.to_csv(output_path, index=False)
    
    print("\n--- Experiment Complete ---")
    print(f"Scheme Validity Rate (SVR): {scheme_validity_rate * 100:.2f}%") #
    
    print("\nAverage Performance (on valid runs only):")
    valid_results_df = results_df[results_df['is_valid_scheme'] == True]
    
    if not valid_results_df.empty:
        # Calculate mean metrics per scenario
        print(valid_results_df.groupby('scenario')[['optimality_gap', 'rpl']].mean())
    else:
        print("No valid LLM runs were recorded.")
        
    print(f"\nDetailed results saved to {output_path}")

if __name__ == "__main__":
    run_experiment(all_scenarios, num_runs_per_scenario=NUM_RUNS_PER_SCENARIO) #