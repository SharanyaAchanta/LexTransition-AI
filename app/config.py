"""Page configuration for LexTransition AI."""

# Navigation items for sidebar and header
NAV_ITEMS = [
    ("Home", "Home"),
    ("Mapper", "IPC -> BNS Mapper"),
    ("OCR", "Document OCR"),
    ("Glossary", "Glossary"),
    ("Fact", "Fact Checker"),
    ("Settings", "Settings / About"),
    ("FAQ", "FAQ"),
    ("Privacy", "Privacy Policy"),
]

# Page configuration
PAGES = {
    "Home": {"title": "Home", "icon": "🏠"},
    "Mapper": {"title": "IPC → BNS Mapper", "icon": "🔄"},
    "OCR": {"title": "Document OCR", "icon": "📄"},
    "Fact": {"title": "Fact Checker", "icon": "📚"},
    "Settings": {"title": "Settings / About", "icon": "⚙️"},
    "FAQ": {"title": "FAQ", "icon": "❓"},
    "Privacy": {"title": "Privacy Policy", "icon": "🔒"},
    "Community": {"title": "Community Hub", "icon": "🤝"},
}

# Valid page names
VALID_PAGES = {item[0] for item in NAV_ITEMS} | {"Community", "Glossary"}
