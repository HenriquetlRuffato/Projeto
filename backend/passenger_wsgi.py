import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from run import app as application
from run import db  # noqa: F401

with application.app_context():
    try:
        db.create_all()
    except Exception:
        pass
