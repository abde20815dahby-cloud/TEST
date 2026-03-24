import customtkinter as ctk
import tkinter as tk
import random

from core.config import NAV_BG, ACCENT_CYAN, THEMES
from core.history import ActionHistoryManager
from frames.frame_main import FrameMain


class AppANCFCC_UI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ANCFCC Pro Suite - Animated Vibrant Edition")
        self.geometry("1400x900")

        # 1. إنشاء الخلفية المتحركة (Animated Canvas)
        self.bg_canvas = tk.Canvas(self, bg="#05020f", highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)

        self.particles = []
        self._init_particles()
        self._animate_background()

        self.hist_mgr = ActionHistoryManager()
        self.frames = {}
        self.current_frame = None

        self._build_top_navbar()

        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=60, pady=40)

        self.frames["main"] = FrameMain(self.content_area, self)
        self.open_page("main")

    def _init_particles(self):
        """توليد الجزيئات المضيئة بألوان حية"""
        colors = ["#00E5FF", "#FF00FF", "#FFE600", "#7000FF", "#00FF66"]
        for _ in range(40):  # 40 كرة متحركة
            x, y = random.randint(0, 1400), random.randint(0, 900)
            vx = random.choice([-1, 1]) * random.uniform(0.2, 1.5)
            vy = random.choice([-1, 1]) * random.uniform(0.2, 1.5)
            r = random.randint(5, 25)
            color = random.choice(colors)

            item = self.bg_canvas.create_oval(
                x - r, y - r, x + r, y + r, fill=color, outline=""
            )
            self.particles.append({"item": item, "vx": vx, "vy": vy, "r": r})

    def _animate_background(self):
        """تحريك الجزيئات باستمرار لتكوين خلفية حية"""
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 1:
            w, h = 1400, 900  # حجم افتراضي قبل ظهور النافذة

        for p in self.particles:
            self.bg_canvas.move(p["item"], p["vx"], p["vy"])
            pos = self.bg_canvas.coords(p["item"])

            # ارتداد الجزيئات عند الاصطدام بحواف الشاشة
            if pos[0] <= 0 or pos[2] >= w:
                p["vx"] *= -1
            if pos[1] <= 0 or pos[3] >= h:
                p["vy"] *= -1

        # تكرار الحركة كل 30 ملي ثانية (حركة سلسة)
        self.after(30, self._animate_background)

    def _build_top_navbar(self):
        # شريط علوي شفاف جزئياً ليتناغم مع الخلفية
        self.navbar = ctk.CTkFrame(
            self,
            height=85,
            fg_color=NAV_BG,
            corner_radius=0,
            border_width=2,
            border_color="#FF00FF",
        )
        self.navbar.pack(fill="x", side="top")
        self.navbar.pack_propagate(False)

        logo_lbl = ctk.CTkLabel(
            self.navbar,
            text="⚡ IFE DAHBY",
            font=("Segoe UI Black", 28),
            text_color=ACCENT_CYAN,
        )
        logo_lbl.pack(side="left", padx=40)

        links_frame = ctk.CTkFrame(self.navbar, fg_color="transparent")
        links_frame.pack(side="right", padx=40)

        self.nav_buttons = {}
        for key, theme in THEMES.items():
            btn = ctk.CTkButton(
                links_frame,
                text=theme["name"],
                font=("Segoe UI", 16, "bold"),
                fg_color="transparent",
                text_color="#FFFFFF",
                hover_color="#7000FF",
                corner_radius=12,
                height=45,
            )
            btn.configure(command=lambda k=key: self.open_page(k))
            btn.pack(side="right", padx=10)
            self.nav_buttons[key] = btn

    def open_page(self, key):
        if self.current_frame == key:
            return

        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(text_color="#000000", fg_color=THEMES[k]["color"])
            else:
                btn.configure(text_color="#FFFFFF", fg_color="transparent")

        if self.current_frame and self.current_frame in self.frames:
            self.frames[self.current_frame].pack_forget()

        if key not in self.frames:
            self.frames[key] = FrameMain(self.content_area, self)

        self.frames[key].pack(fill="both", expand=True)
        self.current_frame = key
