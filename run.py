#!/usr/bin/env python3
"""
Prompt Forge Studio - Launcher
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    import sys

    sys.argv = ["streamlit", "run", "src/ui/app.py"]
    sys.exit(stcli.main())
