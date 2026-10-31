import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_login():
    from auth import login

    assert login("student") == "Welcome, student!"