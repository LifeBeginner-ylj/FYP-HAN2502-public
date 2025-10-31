import json
import os
import time

# --- API-Specific Imports ---
try:
    import openai
except ImportError:
    print("Warning: 'openai' library not found. OpenAI provider will not work.")

# --- Helper Functions (API-Agnostic) ---

def _format_prompt(states, actions, prior, u_s, u_r):
    """
    Formats the detailed prompt for the LLM based on the game definition.
    (This function is API-agnostic and defines the "task")
    """
    # 1. Role and Goal Definition
    role_goal = "You are an expert game theorist. Your task is to design an optimal signaling scheme for a Bayesian Persuasion scenario to maximize the Sender's expected utility."
    
    # 2. Game Definition
    game_def = f"""
Game Definition:
- World States (Ω): {states}
- Receiver's Available Actions (A): {actions}
- Prior Belief (μ₀): {prior}
- Sender Utility Matrix (U_S(a,ω)): {u_s}
- Receiver Utility Matrix (U_R(a,ω)): {u_r}
"""

    # 3. Required Output Format (Strict JSON)
    output_format = """
Required Output Format:
You MUST output ONLY a valid JSON object. Do not include any text before or after the JSON.
The JSON must represent the signaling scheme π: Ω -> Δ(M).
It should be a dictionary where keys are the states (from Ω) and values are dictionaries.
Each inner dictionary maps signal names (M) to their probabilities P(m | ω).
For each state, the probabilities of its signals must sum to 1.0.

Example Format:
{
  "High Quality": { "Recommend": 1.0, "DoNotRecommend": 0.0 },
  "Low Quality": { "Recommend": 0.2, "DoNotRecommend": 0.8 }
}
"""
    
    return f"{role_goal}\n\n{game_def}\n{output_format}"

def validate_llm_scheme(scheme, states):
    """
    Checks if the LLM output is a valid probability distribution.
    (This function is API-agnostic and validates the "output")
    """
    if not isinstance(scheme, dict):
        return False, "Output is not a dictionary."
    
    if set(scheme.keys()) != set(states):
        return False, f"Scheme keys {list(scheme.keys())} do not match states {states}."
        
    for state, signals in scheme.items():
        if not isinstance(signals, dict):
            return False, f"Signals for state {state} is not a dictionary."
        if not signals:
            return False, f"No signals defined for state {state}."
            
        prob_sum = sum(signals.values())
        if not abs(prob_sum - 1.0) < 1e-6:
            return False, f"Probabilities for state {state} sum to {prob_sum}, not 1.0."
            
    return True, "Valid scheme."

# --- API-Specific Implementations ---

def _get_openai_strategy(prompt):
    """
    Calls the OpenAI API.
    """
    try:
        # Initialize client here to ensure API key is read at call time
        client = openai.OpenAI()
        if not client.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
            
        completion = client.chat.completions.create(
            model="gpt-4-turbo", # Or "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You must output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"} # Enforce JSON output
        )
        return completion.choices[0].message.content, None
    except Exception as e:
        return None, f"OpenAI API call failed: {e}"

def _get_mock_strategy(prompt, states):
    """
    Returns a hardcoded "mock" strategy for testing.
    This does NOT call any API and is useful for debugging main.py.
    Now adapted to return valid schemes for different scenarios.
    """
    print("--- Using MOCK provider ---")
    
    # For SimpleBinaryGame - use full revelation (optimal)
    if set(states) == {'Good', 'Bad'}:
        mock_scheme = {
            'Good': {'Good': 1.0, 'Bad': 0.0},
            'Bad': {'Good': 0.0, 'Bad': 1.0}
        }
    # For QualityControl - use full revelation
    elif set(states) == {'High Quality', 'Medium Quality', 'Low Quality'}:
        mock_scheme = {
            'High Quality': {'High Quality': 1.0, 'Medium Quality': 0.0, 'Low Quality': 0.0},
            'Medium Quality': {'High Quality': 0.0, 'Medium Quality': 1.0, 'Low Quality': 0.0},
            'Low Quality': {'High Quality': 0.0, 'Medium Quality': 0.0, 'Low Quality': 1.0}
        }
    else:
        # Generic full revelation for unknown scenarios
        mock_scheme = {}
        for state in states:
            mock_scheme[state] = {s: (1.0 if s == state else 0.0) for s in states}
    
    time.sleep(0.5) # Simulate network delay
    return json.dumps(mock_scheme), None

def _get_poe_strategy(prompt, model_name="Claude-3.5-Sonnet"):
    """
    Calls the Poe API to access various models using OpenAI-compatible format.
    
    Poe uses OpenAI-compatible API with base_url="https://api.poe.com/v1"
    """
    try:
        api_key = os.environ.get("POE_API_KEY")
        if not api_key:
            raise ValueError("POE_API_KEY environment variable not set.")
        
        # Create OpenAI client with Poe's base URL
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.poe.com/v1"
        )
        
        # Call the API (non-streaming for simpler JSON parsing)
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You must output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            # Note: Poe may not support response_format, so we rely on prompt
            temperature=0.7
        )
        
        return completion.choices[0].message.content, None
        
    except Exception as e:
        return None, f"Poe API call failed: {e}"

# --- Main Router Function ---

def get_llm_strategy(states, actions, prior, u_s, u_r, provider="openai"):
    """
    Main entry point for getting an LLM strategy.
    It formats the prompt, routes to the correct API provider, and validates the output.
    
    :param provider: str, "openai", "mock", or others you add
    :return: (scheme_dict, is_valid, status_message)
    """
    # 1. Format the API-agnostic prompt
    prompt = _format_prompt(states, actions, prior, u_s, u_r)
    
    raw_output = None
    error = None
    
    # 2. Route to the specified provider
    if provider == "openai":
        raw_output, error = _get_openai_strategy(prompt)
    elif provider == "mock":
        raw_output, error = _get_mock_strategy(prompt, states)
    elif provider.startswith("poe-"):
        # Format: "poe-GPT-4" or "poe-Claude-3-Opus"
        model_name = provider[4:]  # Remove "poe-" prefix
        raw_output, error = _get_poe_strategy(prompt, model_name)
    # --- Future-proofing ---
    # elif provider == "anthropic":
    #     raw_output, error = _get_anthropic_strategy(prompt)
    # elif provider == "google_gemini":
    #     raw_output, error = _get_gemini_strategy(prompt)
    else:
        return None, False, f"Error: Unknown provider '{provider}'."

    if error:
        return None, False, error
        
    # 3. Parse and Validate the output (API-agnostic)
    try:
        llm_scheme = json.loads(raw_output)
        
        is_valid, message = validate_llm_scheme(llm_scheme, states)
        
        if is_valid:
            return llm_scheme, True, "Success"
        else:
            return None, False, f"Invalid scheme: {message}"

    except json.JSONDecodeError:
        return None, False, f"Failed to decode LLM output as JSON. Output was: {raw_output}"
    except Exception as e:
        return None, False, f"An unexpected error occurred: {e}"