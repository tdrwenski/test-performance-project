#!/bin/bash

set -e

echo "Setting up performance test environment..."

# Install dependencies
python3 -m venv test_venv
source test_venv/bin/activate
python3 -m pip install pytest pytest-benchmark

# Create performance results directory
PERF_ARTIFACT_DIR=performance-results
mkdir -p ${PERF_ARTIFACT_DIR}

# Run the benchmark tests
echo "Running performance benchmarks..."
pytest test_script.py --benchmark-json=${PERF_ARTIFACT_DIR}/processed_results.json

echo "Performance tests completed. Results saved to ${PERF_ARTIFACT_DIR}/processed_results.json"
