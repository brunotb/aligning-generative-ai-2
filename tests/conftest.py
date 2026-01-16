"""
Pytest configuration and shared fixtures for the test suite.
This file is automatically discovered by pytest.
"""

import sys
import os

# Add the project root to the path so tests can import from api and other modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
