from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock


def pytest_configure() -> None:
    project_root = Path(__file__).resolve().parents[1]
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    
    # Mock streamlit before any engine imports to avoid cache_resource issues in tests
    if "streamlit" not in sys.modules:
        mock_st = MagicMock()
        # Make cache_resource a pass-through decorator
        mock_st.cache_resource = lambda *args, **kwargs: (lambda fn: fn)
        sys.modules["streamlit"] = mock_st

