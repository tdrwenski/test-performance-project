#!/usr/bin/env python3

import pytest

@pytest.mark.benchmark(group="basic_operations")
def test_simple_computation(benchmark):
    """Simple CPU-intensive benchmark"""
    def compute():
        result = 0
        for i in range(10000):
            result += i * i
        return result

    result = benchmark.pedantic(compute, iterations=1, rounds=10)
    assert result > 0
