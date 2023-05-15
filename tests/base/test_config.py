"""
Test cases for the Config class, which handles the Configuration settings
for the AI and ensures it behaves as a singleton.
"""

import pytest

from uglygpt.base import config

def test_initial_values():
    """
    Test if the initial values of the Config class attributes are set correctly.
    """
    assert config.debug_mode == False

def test_set_debug_mode():
    """
    Test if the set_debug_mode() method updates the debug_mode attribute.
    """
    # Store debug mode to reset it after the test
    debug_mode = config.debug_mode

    config.set_debug_mode(False)
    assert config.debug_mode == False

    # Reset debug mode
    config.set_debug_mode(debug_mode)