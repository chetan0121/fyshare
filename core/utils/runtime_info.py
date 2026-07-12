"""Runtime and environment information utilities."""

import os
import sys

def is_interactive_terminal() -> bool:
    """Check if the script is running in an interactive terminal."""
    return sys.stdin is not None and sys.stdin.isatty()

def ran_as_compiled_bin() -> bool:
    """Check if the application is running as a compiled binary (PyInstaller)."""
    return getattr(sys, 'frozen', False)

def testing_in_ci() -> bool:
    return os.getenv("FYSHARE_CI", "0") == "1"
