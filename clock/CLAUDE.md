# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A single-file Python/tkinter desktop widget (`clock.py`) that renders an always-on-top digital (LED-style) clock, defaulting to the top-right corner and remembering wherever the user drags it. No build step, no external dependencies (`requirements.txt` notes it uses only the built-in `tkinter`). Windows-only in its current form, since it relies on the Tk `-transparentcolor` window attribute.

## Commands

- **Run**: `python clock.py` (shows a console window) or `pythonw clock.py` (no console window — used for autostart).
- **Register autostart**: run `install_autostart.ps1` in PowerShell from this folder; it creates a Startup-folder shortcut (`DesktopClock.lnk`) that launches `clock.py` with `pythonw.exe` (falling back to `python.exe`) on user login.
- There is no lint, test, or build tooling in this repo.

## Architecture

Everything lives in `clock.py`, structured around a single `DigitalClock` class:

- **Window/transparency trick**: the Tk root is borderless (`overrideredirect`), always-on-top, and uses `-transparentcolor` set to a chroma-key color (`TRANSPARENT_KEY`) that must never appear in any drawn shape — any pixel of that exact color becomes see-through, which is how the clock body gets a non-rectangular silhouette against the desktop.
- **Drawing is manual, not native widgets**: the clock face (bezel, screen, accent stripe, power LED, buttons) is drawn once in `_draw_clock_body()` using `tk.Canvas` primitives. Rounded rectangles are built via the `rounded_rect_points()` helper (a smoothed polygon), since Canvas has no native rounded-rect primitive.
- **Digits are hand-rendered 7-segment LEDs**, not text/fonts: `SEGMENTS` maps each character `'0'`-`'9'` to which of the 7 segments (a–g) are lit, and `_draw_digit()` draws each segment as a small rectangle in `LED_ON` or `LED_OFF` color. This keeps the digital-clock look consistent regardless of installed fonts.
- **Redraw strategy**: `_render_display()` is called every tick from `update_loop()` (500ms via `root.after`); it does `canvas.delete("digits")` and redraws all digit/colon shapes tagged `"digits"` rather than diffing — the static clock body (bezel/screen/etc.) is drawn once and never touched again.
- **Layout is computed from `self._panel_cx`/`_panel_cy`/`_digit_h`**, set when the LED screen is drawn in `_draw_clock_body()`, so digit size and centering scale automatically off the window's `width`/`height`.
- **Dragging**: bound on the canvas (`<Button-1>` / `<B1-Motion>`), moves the window via `root.geometry()`. Right-click (`<Button-3>`) destroys the window (i.e. this is how the app is closed).
- **Position persistence**: on `<ButtonRelease-1>` (end of a drag), `_save_position()` writes `{x, y}` to `POSITION_FILE` (`.clock_position.json`, next to `clock.py`). On startup, `_restore_position()` loads that file and reopens at the same coordinates, clamped to the current screen bounds; if the file is missing or unreadable it falls back to the original top-right default.

## Notes for changes

- Any new color constant must be visually distinct from `TRANSPARENT_KEY` (`#ab00ab`) or it will render as a transparent hole instead of a solid fill.
- When changing the window's `width`/`height` in `DigitalClock.__init__`, the body/screen/segment layout is expressed in fractions of `w`/`h`, so it should rescale automatically — check that digit segments still fit inside the LED screen bounds after large size changes.
