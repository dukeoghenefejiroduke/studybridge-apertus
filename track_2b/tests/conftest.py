"""
Pytest configuration for StudyBridge AI tests.
Automatically flags the environment as TESTING so unit tests use local fallback
instead of attempting external LLM network calls.
"""

import os

def pytest_configure(config):
    os.environ["TESTING"] = "1"
