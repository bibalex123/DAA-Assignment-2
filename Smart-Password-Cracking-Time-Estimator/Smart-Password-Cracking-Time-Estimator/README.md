# Smart Password Security Estimator

A Python desktop GUI for a Design and Analysis of Algorithms assignment. It demonstrates combinatorial search-space growth and a small, safe brute-force concept simulation.

## Features
- Password character-category analysis
- Approximate entropy and search-space calculations
- Theoretical exhaustive-search time estimate using a user-selected rate
- Search-space growth chart for lengths 1–16
- Step-by-step toy search over the alphabet `a` through `f`
- DAA complexity notes in the interface

## Requirements
- Python 3.10+
- Tkinter (usually included with standard Python installations)
- Matplotlib

## Run
```bash
python -m pip install -r requirements.txt
python main.py
```

On Ubuntu/Debian, if Tkinter is missing:
```bash
sudo apt install python3-tk
```

## Run tests
From the project root:
```bash
python -m unittest discover -s tests -v
```

## Important limitations
The estimator uses a simplified character-pool model. Real password guessing depends on password patterns, hashing algorithm, salts, hardware, and attacker strategy. Entropy and time figures are theoretical estimates, not guarantees. Do not enter a password that you actively use. The toy demonstration only checks six single-character candidates and does not attempt to crack the entered sample password.

## DAA analysis
Let `R` be the number of possible characters and `L` the password length. The theoretical candidate count is `N = R^L`.
- Worst-case exhaustive search time: `O(N) = O(R^L)`
- Average-case time: `O(N)` under a uniform target-position assumption
- Best-case time: `O(1)` when the first candidate matches
- Auxiliary space: `O(1)` for a generator-based implementation that stores one candidate at a time

The GUI computes the candidate count mathematically; it does not enumerate the full search space.

## Suggested screenshots for your report
Run the application and capture:
1. Main dashboard before analysis
2. Analysis results for a sample password
3. Search-space graph and toy demonstration
Save images under `screenshots/`.
