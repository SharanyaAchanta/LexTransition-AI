"""Pages package for LexTransition AI."""
from app.pages.home import render as render_home
from app.pages.mapper import render as render_mapper
from app.pages.ocr import render as render_ocr
from app.pages.fact_checker import render as render_fact_checker
from app.pages.settings import render as render_settings
from app.pages.faq import render as render_faq
from app.pages.privacy import render as render_privacy
from app.pages.community import render as render_community

__all__ = [
    "render_home",
    "render_mapper",
    "render_ocr",
    "render_fact_checker",
    "render_settings",
    "render_faq",
    "render_privacy",
    "render_community",
]
