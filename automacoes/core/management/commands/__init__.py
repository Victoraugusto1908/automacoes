# core/management/commands/__init__.py
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent.resolve()
sys.path.append(str(PROJECT_ROOT))