"""Offline checks for the Streamlit entry point and registered pages."""
from pathlib import Path

from streamlit.navigation.page import StreamlitPage
from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_loads_and_registers_navigation(monkeypatch):
    # Execute real imports, page creation and navigation, but do not fetch the
    # selected page's live weather/news data in this entry-point smoke test.
    selected = []
    monkeypatch.setattr(StreamlitPage, "run", lambda self: selected.append(self))
    app = AppTest.from_file(str(ROOT / "Dashboard.py")).run()
    assert not app.exception, [error.value for error in app.exception]
    assert len(selected) == 1
    assert selected[0].title == "홈"


def test_entry_point_and_views_compile():
    paths = [ROOT / "Dashboard.py", *sorted((ROOT / "views").glob("*.py"))]
    assert len(paths) > 1
    for path in paths:
        compile(path.read_bytes(), str(path), "exec")
