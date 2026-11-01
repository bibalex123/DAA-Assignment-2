# Design and Analysis of Algorithms — Assignment 2
## Smart Password Cracking Time Estimator

### 1. Problem Statement
Password security is influenced by password length, the characters used, and the size of the set of possible guesses. This project provides a graphical educational tool that estimates the theoretical search space and illustrates how exhaustive-search work grows with password length. It also demonstrates a small toy search step by step.

### 2. Objectives
- Build a user-friendly Python GUI.
- Analyze password length and character categories.
- Calculate an approximate theoretical search space and entropy.
- Estimate exhaustive-search time under a configurable guessing-rate assumption.
- Visualize exponential growth and demonstrate a toy brute-force sequence.
- Test normal and boundary inputs.

### 3. Algorithm
Let:
- `L` be the length of the sample password.
- `R` be the estimated size of the character pool selected by the characters present.
- `N` be the number of possible candidates.

The estimator calculates:
1. Read the sample password and guessing-rate assumption.
2. Determine which character categories appear.
3. Estimate `R` from the active categories.
4. Calculate `N = R^L` using logarithms to avoid numeric overflow.
5. Calculate approximate entropy as `H = L × log₂(R)` bits.
6. Estimate the theoretical time as `N / guessing_rate`.
7. Display the strength heuristic, categories, estimates, and graph.

The toy demonstration is separate from the entered password. It tests the sequence `a, b, c, d, e, f` against a one-character toy target and shows each step.

### 4. Complexity Analysis
For exhaustive search, let `N = R^L`.
- Best case: `O(1)` if the first candidate matches.
- Average case: `O(N)` if the target is equally likely at any position.
- Worst case: `O(N)` if the final candidate matches or no candidate matches.
- Auxiliary space: `O(1)` for a generator-based candidate search that stores one candidate at a time.

The application does not enumerate all `N` candidates; it computes the theoretical count mathematically. The graph calculates a fixed number of points, so its time and space use are `O(k)` where `k` is the number of displayed password lengths (16 in this implementation).

### 5. Tools and Technologies
- Python
- Tkinter
- Matplotlib
- Python `math` module
- `unittest`

### 6. Test Cases
| Test | Input | Expected result |
|---|---|---|
| Empty input | Empty password | Validation error |
| Lowercase-only | `abcd` | Character pool is 26 |
| Mixed categories | `Ab3!` | Pool includes lowercase, uppercase, digits, and symbols |
| Invalid rate | Rate = 0 | Validation error |
| Entropy comparison | `abcd` vs `abcdefgh` | Longer input has greater estimated entropy under the model |
| Toy search | Target `c` | Steps through `a`, `b`, then finds `c` |

Run automated tests using `python -m unittest discover -s tests -v`.

### 7. Screenshots
Insert screenshots captured from the running application:
1. Main dashboard
2. Sample password analysis
3. Search-space growth chart and toy demo

### 8. Limitations
The character-pool and entropy model is approximate and assumes each position can be chosen independently from the same pool. Real-world password guessing can exploit common patterns and depends on the hashing algorithm, salts, hardware, and attacker strategy. The estimated cracking time is not a guarantee of security. The application is educational and does not attempt to crack the entered password.

### 9. Conclusion
The application demonstrates combinatorial search-space growth and the basic complexity of exhaustive search through a graphical interface. It combines analysis, visualization, a toy step-by-step demonstration, and automated tests in a compact project suitable for a DAA assignment.
