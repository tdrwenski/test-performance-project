#!/bin/bash

set -e

echo "Setting up performance test environment..."

# Install dependencies
python3 -m venv test_venv
source test_venv/bin/activate
python3 -m pip install pytest pytest-benchmark

# Create performance results directory
RESULTS_DIR=performance-results
mkdir -p ${RESULTS_DIR}

# Run the benchmark tests
echo "Running performance benchmarks..."
pytest test_script.py --benchmark-json=${RESULTS_DIR}/benchmark_results.json

echo "Performance tests completed. Results saved to ${RESULTS_DIR}/benchmark_results.json"