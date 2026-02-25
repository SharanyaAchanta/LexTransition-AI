"""Components package for LexTransition AI."""
from app.components.header import render_header
from app.components.sidebar import render_sidebar
from app.components.footer import render_footer
from app.components.theme import init_theme, toggle_theme, render_theme_toggle, apply_theme
from app.components.tts_helper import render_agent_audio, generate_tts_and_play

__all__ = [
    "render_header",
    "render_sidebar",
    "render_footer",
    "init_theme",
    "toggle_theme",
    "render_theme_toggle",
    "apply_theme",
    "render_agent_audio",
    "generate_tts_and_play",
]
