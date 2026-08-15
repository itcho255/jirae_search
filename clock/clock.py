import tkinter as tk
import time
import json
import os


TRANSPARENT_KEY = "#ab00ab"  # chroma-key color; must not be used anywhere in the drawing

POSITION_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".clock_position.json")

BEZEL_FILL = "#161616"
BEZEL_EDGE = "#3d3d3d"
BEZEL_HIGHLIGHT = "#2a2a2a"
ACCENT = "#3b82f6"
BUTTON_FILL = "#2e2e2e"
BUTTON_EDGE = "#4a4a4a"
POWER_LED = "#39ff14"

PANEL_BG = "#050505"
PANEL_BORDER = "#000000"
LED_ON = "#3b82f6"
LED_OFF = "#122544"

# classic 7-segment layout: (a, b, c, d, e, f, g)
#      a
#    f   b
#      g
#    e   c
#      d
SEGMENTS = {
    "0": (1, 1, 1, 1, 1, 1, 0),
    "1": (0, 1, 1, 0, 0, 0, 0),
    "2": (1, 1, 0, 1, 1, 0, 1),
    "3": (1, 1, 1, 1, 0, 0, 1),
    "4": (0, 1, 1, 0, 0, 1, 1),
    "5": (1, 0, 1, 1, 0, 1, 1),
    "6": (1, 0, 1, 1, 1, 1, 1),
    "7": (1, 1, 1, 0, 0, 0, 0),
    "8": (1, 1, 1, 1, 1, 1, 1),
    "9": (1, 1, 1, 1, 0, 1, 1),
}


def rounded_rect_points(x0, y0, x1, y1, r):
    return [
        x0 + r, y0,
        x1 - r, y0,
        x1, y0,
        x1, y0 + r,
        x1, y1 - r,
        x1, y1,
        x1 - r, y1,
        x0 + r, y1,
        x0, y1,
        x0, y1 - r,
        x0, y0 + r,
        x0, y0,
    ]


class DigitalClock:
    def __init__(self, width=150, height=62, padding=12):
        self.width = width
        self.height = height
        self.padding = padding

        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg=TRANSPARENT_KEY)
        self.root.attributes("-transparentcolor", TRANSPARENT_KEY)

        self.canvas = tk.Canvas(
            self.root, width=width, height=height,
            bg=TRANSPARENT_KEY, highlightthickness=0, bd=0,
        )
        self.canvas.pack()

        self._drag_data = (0, 0)
        self.canvas.bind("<Button-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", lambda e: self.root.destroy())

        self._draw_clock_body()

        self._restore_position()
        self.update_loop()

    # ---- drawing: digital clock body ----
    def _draw_clock_body(self):
        c = self.canvas
        w, h = self.width, self.height

        # outer bezel
        c.create_polygon(
            rounded_rect_points(2, 2, w - 2, h - 2, 10),
            smooth=True, fill=BEZEL_FILL, outline=BEZEL_EDGE, width=1.5,
        )
        # subtle top sheen
        c.create_polygon(
            rounded_rect_points(6, 5, w - 6, h * 0.30, 6),
            smooth=True, fill=BEZEL_HIGHLIGHT, outline="",
        )

        # LED screen
        screen_x0, screen_y0 = w * 0.10, h * 0.17
        screen_x1, screen_y1 = w * 0.90, h * 0.74
        c.create_polygon(
            rounded_rect_points(screen_x0, screen_y0, screen_x1, screen_y1, 5),
            smooth=True, fill=PANEL_BG, outline=PANEL_BORDER, width=1,
        )
        self._panel_cx = (screen_x0 + screen_x1) / 2
        self._panel_cy = (screen_y0 + screen_y1) / 2
        self._digit_h = (screen_y1 - screen_y0) * 0.62

        # bottom accent stripe
        c.create_polygon(
            rounded_rect_points(w * 0.10, h * 0.83, w * 0.90, h * 0.89, 2),
            smooth=True, fill=ACCENT, outline="",
        )

        # power indicator LED
        c.create_oval(w * 0.045, h * 0.10, w * 0.045 + 5, h * 0.10 + 5, fill=POWER_LED, outline="")

        # small top buttons
        for i in range(2):
            bx0 = w - 0.11 * w - i * (w * 0.09)
            c.create_polygon(
                rounded_rect_points(bx0, h * 0.06, bx0 + w * 0.07, h * 0.115, 2),
                smooth=True, fill=BUTTON_FILL, outline=BUTTON_EDGE,
            )

    # ---- digital (7-segment) display ----
    def _draw_digit(self, x, y, dw, dh, segs, seg_t, tag):
        a, b, c_, d, e, f, g = segs
        c = self.canvas
        half = dh / 2
        c.create_rectangle(x + seg_t * 0.5, y, x + dw - seg_t * 0.5, y + seg_t,
                            fill=LED_ON if a else LED_OFF, outline="", tags=tag)
        c.create_rectangle(x + seg_t * 0.5, y + half - seg_t / 2, x + dw - seg_t * 0.5, y + half + seg_t / 2,
                            fill=LED_ON if g else LED_OFF, outline="", tags=tag)
        c.create_rectangle(x + seg_t * 0.5, y + dh - seg_t, x + dw - seg_t * 0.5, y + dh,
                            fill=LED_ON if d else LED_OFF, outline="", tags=tag)
        c.create_rectangle(x, y + seg_t * 0.5, x + seg_t, y + half - seg_t * 0.5,
                            fill=LED_ON if f else LED_OFF, outline="", tags=tag)
        c.create_rectangle(x + dw - seg_t, y + seg_t * 0.5, x + dw, y + half - seg_t * 0.5,
                            fill=LED_ON if b else LED_OFF, outline="", tags=tag)
        c.create_rectangle(x, y + half + seg_t * 0.5, x + seg_t, y + dh - seg_t * 0.5,
                            fill=LED_ON if e else LED_OFF, outline="", tags=tag)
        c.create_rectangle(x + dw - seg_t, y + half + seg_t * 0.5, x + dw, y + dh - seg_t * 0.5,
                            fill=LED_ON if c_ else LED_OFF, outline="", tags=tag)

    def _render_display(self, time_str):
        self.canvas.delete("digits")
        dh = self._digit_h
        dw = dh * 0.55
        seg_t = dh * 0.16
        gap = dh * 0.18
        colon_w = dh * 0.28

        total = sum(colon_w if ch == ":" else dw for ch in time_str)
        total += gap * (len(time_str) - 1)

        x = self._panel_cx - total / 2
        y = self._panel_cy - dh / 2

        for ch in time_str:
            if ch == ":":
                r = dh * 0.075
                dot_x = x + colon_w / 2
                self.canvas.create_oval(dot_x - r, y + dh * 0.26 - r, dot_x + r, y + dh * 0.26 + r,
                                         fill=LED_ON, outline="", tags="digits")
                self.canvas.create_oval(dot_x - r, y + dh * 0.74 - r, dot_x + r, y + dh * 0.74 + r,
                                         fill=LED_ON, outline="", tags="digits")
                x += colon_w + gap
            else:
                self._draw_digit(x, y, dw, dh, SEGMENTS[ch], seg_t, "digits")
                x += dw + gap

    # ---- interaction ----
    def _on_press(self, event):
        self._drag_data = (event.x, event.y)

    def _on_motion(self, event):
        dx = event.x - self._drag_data[0]
        dy = event.y - self._drag_data[1]
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def _on_release(self, event):
        self._save_position(self.root.winfo_x(), self.root.winfo_y())

    # ---- clock ----
    def update_loop(self):
        now = time.strftime("%H:%M:%S")
        self._render_display(now)
        self.root.after(500, self.update_loop)

    def _restore_position(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()

        pos = self._load_position()
        if pos is None:
            x = sw - self.width - self.padding
            y = self.padding
        else:
            x, y = pos
            x = max(0, min(x, sw - self.width))
            y = max(0, min(y, sh - self.height))

        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")

    def _load_position(self):
        try:
            with open(POSITION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return int(data["x"]), int(data["y"])
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            return None

    def _save_position(self, x, y):
        try:
            with open(POSITION_FILE, "w", encoding="utf-8") as f:
                json.dump({"x": x, "y": y}, f)
        except OSError:
            pass

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass


def main():
    clock = DigitalClock()
    clock.run()


if __name__ == '__main__':
    main()
