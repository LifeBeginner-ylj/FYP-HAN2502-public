# Bayesian Persuasion Game Simulator with LLM Strategy Generation

## Project Overview

This project implements a **Bayesian Persuasion Game Simulator** that evaluates the capability of Large Language Models (LLMs) to design optimal signaling schemes. The simulator acts as a "referee" that evaluates strategies proposed by LLMs against theoretical baselines and optimal solutions.

### What is Bayesian Persuasion?

Bayesian Persuasion is a game-theoretic framework where an informed **Sender** (e.g., a seller) strategically reveals information to an uninformed **Receiver** (e.g., a buyer) to influence their decision-making. The Sender designs a **signaling scheme** that maximizes their expected utility while the Receiver acts rationally based on the information received.

## Project Structure

```
FYP-HAN2502-Bayesian-Persuation/
│
├── simulator.py         # Game Environment Simulator (the "Referee")
├── baselines.py         # Baseline Strategies and Theoretical Optimum
├── llm_client.py        # LLM Strategy Generator (OpenAI/Mock)
├── scenarios.py         # Game Scenario Definitions
├── main.py              # Main Experiment Pipeline
├── requirements.txt     # Python Dependencies
├── results/             # Experiment Output Directory
│   └── experiment_results.csv
└── README.md            # This file
```

## Core Components

### 1. Game Environment Simulator (`simulator.py`)

The core "referee" that:
- Calculates **posterior beliefs** using Bayes' Rule: `P(ω | m) = [P(m | ω) × P(ω)] / P(m)`
- Determines the **Receiver's optimal action** `a*(m)` given a signal
- Computes the **Sender's expected utility**: `E[U_S] = Σ_ω P(ω) × [Σ_m P(m | ω) × U_S(a*(m), ω)]`

### 2. Baseline Strategies (`baselines.py`)

Implements three benchmark strategies:
- **Full Revelation**: Signal set M equals state set Ω (complete transparency)
- **No Revelation**: Always sends the same signal regardless of state (no information)
- **Theoretical Optimum**: Pre-calculated mathematically optimal strategy (hardcoded for each scenario)

### 3. LLM Strategy Generator (`llm_client.py`)

- Formats structured prompts describing the game to LLMs
- Supports multiple providers:
  - **OpenAI** (GPT-4, GPT-3.5)
  - **Mock** (hardcoded strategies for testing)
- Validates LLM output as proper probability distributions
- Extensible architecture for adding new providers (Anthropic, Google Gemini, etc.)

### 4. Scenario Definitions (`scenarios.py`)

Defines test cases with:
- **States** (Ω): Possible world states
- **Actions** (A): Receiver's available actions
- **Prior beliefs** (μ₀): Initial probability distribution over states
- **Utility matrices**: U_S(a,ω) and U_R(a,ω) for Sender and Receiver

**Current Scenarios:**
1. **QualityControl**: 3 states (High/Medium/Low Quality), 2 actions (Buy/Don't Buy)
2. **SimpleBinaryGame**: 2 states (Good/Bad), 2 actions (Accept/Reject)

### 5. Main Experiment Pipeline (`main.py`)

Orchestrates the complete experimental workflow:
1. Initializes game simulator for each scenario
2. Calculates baseline utilities
3. Runs LLM multiple times per scenario (configurable robustness testing)
4. Computes evaluation metrics
5. Saves results to CSV

## Evaluation Metrics

The framework evaluates LLM performance using three key metrics:

1. **Scheme Validity Rate (SVR)**
   - Percentage of LLM outputs that are valid probability distributions
   - Formula: `SVR = (Valid Schemes) / (Total Attempts)`

2. **Optimality Gap**
   - Measures how far the LLM is from the theoretical optimum
   - Formula: `Gap = (U_opt - U_llm) / U_opt`
   - Lower is better (0 = optimal)

3. **Relative Performance Level (RPL)**
   - Measures improvement over the worst baseline
   - Formula: `RPL = (U_llm - U_worst) / (U_opt - U_worst)`
   - Range: [0, 1], where 1 = optimal performance

## Installation

### Setup

1. Clone the repository:
```bash
git clone https://github.com/LifeBeginner-ylj/FYP-HAN2502-Bayesian-Persuation.git
cd FYP-HAN2502-Bayesian-Persuation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up OpenAI API key:
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

## Usage

### Quick Start (Mock Mode)

Test the framework without API calls:

```bash
python3 main.py
```

By default, the code is configured to use the **mock provider** for testing.

### Using Real LLM (OpenAI)

1. Edit `main.py` and change the provider:
```python
LLM_PROVIDER = "openai"  # Change from "mock" to "openai"
```

2. Run the experiment:
```bash
python3 main.py
```

### Configuration

In `main.py`, you can configure:
- `NUM_RUNS_PER_SCENARIO`: Number of times to query the LLM per scenario (default: 5)
- `LLM_PROVIDER`: Choice of "openai" or "mock"

## Example Output

```
--- Running Scenario: QualityControl ---
  Baseline - Full Revelation: 7.0000
  Baseline - No Revelation: 0.0000
  Theoretical Optimum: 7.0000
  LLM Run 1/5...
    LLM Utility: 7.0000 (Valid)
  ...

--- Experiment Complete ---
Scheme Validity Rate (SVR): 100.00%

Average Performance (on valid runs only):
                  optimality_gap  rpl
scenario                             
QualityControl               0.0  1.0
SimpleBinaryGame             0.0  NaN

Detailed results saved to results/experiment_results.csv
```

## Results

All experimental results are saved to `results/experiment_results.csv` with the following columns:
- `scenario`: Name of the game scenario
- `run`: Run number
- `u_llm`: LLM strategy utility
- `u_theoretical_optimum`: Theoretical maximum utility
- `u_full_revelation`: Full revelation baseline utility
- `u_no_revelation`: No revelation baseline utility
- `u_worst_baseline`: Worst of the two baselines
- `optimality_gap`: Optimality gap metric
- `rpl`: Relative Performance Level
- `is_valid_scheme`: Whether the LLM output was valid
- `llm_provider`: Provider used (openai/mock)
