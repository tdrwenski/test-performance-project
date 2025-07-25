#!/usr/bin/env python3

import pytest

@pytest.mark.benchmark(group="basic_operations")
def test_simple_computation(benchmark):
    """Simple CPU-intensive benchmark"""
    def compute():
        result = 0
        for i in range(1000):
            result += i * i
        return result

    result = benchmark(compute, iterations=1, rounds=10)
    assert result > 0
