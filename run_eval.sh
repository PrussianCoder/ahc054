#!/bin/bash
# Wrapper script to run eval.py in the virtual environment

# Activate virtual environment
source .venv/bin/activate

# Run eval.py with all passed arguments
# Usage examples:
# ./run_eval.sh main.py -s 0 -v
# ./run_eval.sh solution.py -s 0 9
# ./run_eval.sh -s 0 9  (uses default main.py)
python eval.py "$@"
