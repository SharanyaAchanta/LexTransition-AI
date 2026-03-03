from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock


def pytest_configure() -> None:
    project_root = Path(__file__).resolve().parents[1]
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    
    # Ensure Streamlit cache decorators are always no-ops during tests,
    # whether streamlit is installed or not.
    if "streamlit" not in sys.modules:
        mock_st = MagicMock()
        mock_st.cache_resource = lambda *args, **kwargs: (lambda fn: fn)
        mock_st.cache_data = lambda *args, **kwargs: (lambda fn: fn)
        sys.modules["streamlit"] = mock_st
    else:
        import streamlit as st
        st.cache_data = lambda *args, **kwargs: (lambda fn: fn)
        st.cache_resource = lambda *args, **kwargs: (lambda fn: fn)

