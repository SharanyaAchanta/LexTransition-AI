"""Pages package for LexTransition AI."""
from app.pages.home import render_home_page
from app.pages.mapper import render_mapper_page
from app.pages.ocr import render_ocr_page
from app.pages.glossary import render_glossary_page
from app.pages.fact_checker import render_fact_checker_page
from app.pages.community import render_community_page
from app.pages.settings import render_settings_page
from app.pages.faq import render_faq_page
from app.pages.privacy import render_privacy_page

__all__ = [
    "render_home_page",
    "render_mapper_page",
    "render_ocr_page",
    "render_glossary_page",
    "render_fact_checker_page",
    "render_community_page",
    "render_settings_page",
    "render_faq_page",
    "render_privacy_page"
]