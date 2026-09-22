"""
app.py
------
Thin launcher. All UI logic now lives in `ui.py`.
Run with:
    streamlit run app.py
"""

# Importing ui.py is enough — Streamlit executes the whole module on import,
# which renders the page.
import ui  # noqa: F401
