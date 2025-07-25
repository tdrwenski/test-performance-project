#!/usr/bin/env python3

import pytest
import time
import json
import os

@pytest.mark.benchmark(group="basic_operations")
def test_simple_computation(benchmark):
    """Simple CPU-intensive benchmark"""
    def compute():
        result = 0
        for i in range(10):
            result += i * i
        return result

    result = benchmark(compute)
    assert result > 0
