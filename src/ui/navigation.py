"""UI navigation helpers.

This module centralizes navigation utilities for the CustomTkinter UI.

- `clear_root` enforces a single-screen model by destroying the current screen.
"""

from __future__ import annotations

from typing import Tuple, Type

import tkinter as tk

from src.logmgr import logger


def clear_root(parent, keep_types: Tuple[Type, ...] = ()) -> None:
    """Destroy all direct children of parent except instances of keep_types."""
    for child in list(parent.winfo_children()):
        if keep_types and isinstance(child, keep_types):
            continue
        try:
            child.destroy()
        except (tk.TclError, RuntimeError):
            logger.exception(
                "clear_root failed destroying %s#%s",
                child.__class__.__name__,
                id(child),
            )
