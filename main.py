#!/usr/bin/env python3
"""LMPTS Application Entry Point."""

import sys
from pathlib import Path

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from lmpts.gui.main_window import LMPTSApplication
from lmpts.services.container import ServiceContainer
from lmpts.utils.logging_config import setup_logging


def main() -> None:
    """Launch the LMPTS GUI application."""
    setup_logging()
    container = ServiceContainer()
    app = LMPTSApplication(container)
    app.run()


if __name__ == "__main__":
    main()
