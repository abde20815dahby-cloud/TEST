import os
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from core.config import (
    CARD_BG,
    TEXT_MUTED,
    ACCENT_CYAN,
    ACCENT_MAGENTA,
    ACCENT_YELLOW,
)


class FrameMain(ctk.CTkFrame):
    def __init__(self, master, app_instance):
        super().__init__(master, fg_color="transparent")
        self.app = app_instance
        self.engine = getattr(self.app, "engine", None)  # التأكد من ربط المحرك

        # الحاويات (Frames) الرئيسية باش نقدرو نبدلو بيناتهم
        self.container_main = ctk.CTkFrame(self, fg_color="transparent")
        self.container_global = ctk.CTkFrame(self, fg_color="transparent")
        self.container_single = ctk.CTkFrame(self, fg_color="transparent")

        self.build_main_view()
        self.show_main_view()

    def show_main_view(self):
        self.container_global.pack_forget()
        self.container_single.pack_forget()
        self.container_main.pack(fill="both", expand=True)

    def show_global_view(self):
        self.container_main.pack_forget()
        self.container_single.pack_forget()
        self.build_global_view()
        self.container_global.pack(fill="both", expand=True)

    def show_single_view(self, dossier):
        self.container_main.pack_forget()
        self.container_global.pack_forget()
        self.build_single_view(dossier)
        self.container_single.pack(fill="both", expand=True)

    def build_main_view(self):
        # القسم العلوي - ألوان حية ومبهجة
        hero_section = ctk.CTkFrame(self.container_main, fg_color="transparent")
        hero_section.pack(fill="x", pady=(10, 30))

        title = ctk.CTkLabel(
            hero_section,
            text="التدقيق والتطهير الفوري 🚀",
            font=("Segoe UI Black", 48),
            text_color=ACCENT_YELLOW,
        )
        title.pack(anchor="e")

        subtitle = ctk.CTkLabel(
            hero_section,
            text="برنامج ديناميكي لمعالجة ملفاتك بسرعة وقوة لا مثيل لها.",
            font=("Segoe UI", 20, "bold"),
            text_color=TEXT_MUTED,
        )
        subtitle.pack(anchor="e", pady=(5, 25))

        self.btn_select = ctk.CTkButton(
            hero_section,
            text="🔥 اختيار مسار المشروع الآن",
            font=("Segoe UI", 20, "bold"),
            fg_color=ACCENT_CYAN,
            text_color="#000000",
            hover_color="#FFFFFF",
            height=65,
            corner_radius=35,
            command=self.select_project_folder,  # ربط الزر بدالة اختيار المجلد
        )
        self.btn_select.pack(anchor="e")

        # شبكة البطاقات (بإطارات مشعة)
        cards_section = ctk.CTkFrame(self.container_main, fg_color="transparent")
        cards_section.pack(fill="x", pady=20)
        cards_section.columnconfigure((0, 1), weight=1)

        # بطاقة 1: التطهير
        card_clean = ctk.CTkFrame(
            cards_section,
            fg_color=CARD_BG,
            corner_radius=20,
            border_width=3,
            border_color=ACCENT_CYAN,
        )
        card_clean.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

        ctk.CTkLabel(
            card_clean,
            text="التطهير الذكي",
            font=("Segoe UI Black", 26),
            text_color=ACCENT_CYAN,
        ).pack(pady=(30, 10), padx=25, anchor="e")
        ctk.CTkLabel(
            card_clean,
            text="عزل الملفات الدخيلة وتنظيف المشروع بقوة الذكاء الاصطناعي.",
            font=("Segoe UI", 16),
            text_color="#FFFFFF",
        ).pack(padx=25, anchor="e")

        self.btn_clean = ctk.CTkButton(
            card_clean,
            text="بدء التطهير 🌪️",
            font=("Segoe UI", 18, "bold"),
            fg_color=ACCENT_CYAN,
            text_color="#000000",
            hover_color="#FFFFFF",
            height=55,
            corner_radius=15,
            command=self.run_cleaning,  # ربط الزر بالعملية
        )
        self.btn_clean.pack(pady=30, padx=25, anchor="e", fill="x")

        # بطاقة 2: الفحص
        card_scan = ctk.CTkFrame(
            cards_section,
            fg_color=CARD_BG,
            corner_radius=20,
            border_width=3,
            border_color=ACCENT_MAGENTA,
        )
        card_scan.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

        ctk.CTkLabel(
            card_scan,
            text="فحص النواقص",
            font=("Segoe UI Black", 26),
            text_color=ACCENT_MAGENTA,
        ).pack(pady=(30, 10), padx=25, anchor="e")
        ctk.CTkLabel(
            card_scan,
            text="فحص شامل وتدقيق صارم لسلامة الملفات المرجعية.",
            font=("Segoe UI", 16),
            text_color="#FFFFFF",
        ).pack(padx=25, anchor="e")

        self.btn_scan = ctk.CTkButton(
            card_scan,
            text="فحص الملفات 👁️",
            font=("Segoe UI", 18, "bold"),
            fg_color=ACCENT_MAGENTA,
            text_color="#000000",
            hover_color="#FFFFFF",
            height=55,
            corner_radius=15,
            command=self.run_missing_check,  # ربط الزر بالعملية
        )
        self.btn_scan.pack(pady=30, padx=25, anchor="e", fill="x")

    def select_project_folder(self):
        folder = filedialog.askdirectory(title="تحديد مسار مشروع التحديد")
        if folder and self.engine:
            self.engine.set_project_root(folder)
            messagebox.showinfo("تم", f"تم تحديد المسار:\n{folder}")

    def run_cleaning(self):
        if not self.engine or not self.engine.project_root:
            messagebox.showwarning("تنبيه", "المرجو اختيار مسار المشروع أولا.")
            return
        res = self.engine.clean_extras()
        messagebox.showinfo(
            "نتيجة التطهير", f"تم تطهير {res['moved_count']} ملف غير معتمد."
        )

    def run_missing_check(self):
        if not self.engine or not self.engine.project_root:
            messagebox.showwarning("تنبيه", "المرجو اختيار مسار المشروع أولا.")
            return

        missing = self.engine.check_missing()
        self.engine.global_missing_dict = missing

        if not missing:
            messagebox.showinfo(
                "فحص النواقص", "✅ توافق تام: جميع متطلبات المحافظة مكتملة."
            )
        else:
            self.show_global_view()  # فتح نافذة التقرير عند وجود نواقص

    # ==========================================
    # واجهات التقرير والمراقبة (الإصلاح)
    # ==========================================
    def build_global_view(self):
        for w in self.container_global.winfo_children():
            w.destroy()

        header_lbl = ctk.CTkLabel(
            self.container_global,
            text="⚠️ تقرير النظام: اكتشاف نواقص في ملفات المشروع",
            font=("Segoe UI Black", 24),
            text_color="#EF4444",
        )
        header_lbl.pack(pady=(10, 20), anchor="e")

        btn_frame = ctk.CTkFrame(self.container_global, fg_color="transparent")
        btn_frame.pack(pady=5, fill="x")

        ctk.CTkButton(
            btn_frame,
            text="⚡ استرداد من المخزن",
            fg_color="#10B981",
            font=("Segoe UI", 14, "bold"),
            command=self.auto_distribute_global,
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="🔏 ختم جماعي (ZN)",
            fg_color="#8B5CF6",
            font=("Segoe UI", 14, "bold"),
            command=self.batch_stamp_missing_zn2,
        ).pack(side="right", padx=5)
        ctk.CTkButton(
            btn_frame,
            text="📋 نسخ أرقام الملفات الناقصة",
            fg_color="#3B82F6",
            font=("Segoe UI", 14, "bold"),
            command=self.copy_missing_numbers,
        ).pack(side="left", padx=5)

        list_f = ctk.CTkScrollableFrame(self.container_global, fg_color="transparent")
        list_f.pack(pady=10, fill="both", expand=True)

        if self.engine and hasattr(self.engine, "global_missing_dict"):
            for d, m in list(self.engine.global_missing_dict.items()):
                r = ctk.CTkFrame(list_f, fg_color=CARD_BG, corner_radius=10)
                r.pack(fill="x", pady=5)

                btn_group = ctk.CTkFrame(r, fg_color="transparent")
                btn_group.pack(side="left", padx=15, pady=15)

                ctk.CTkButton(
                    btn_group,
                    text="⚙️ فحص وتعديل يدوياً",
                    width=120,
                    fg_color=ACCENT_CYAN,
                    text_color="#000000",
                    command=lambda d=d: self.show_single_view(d),
                ).pack(side="left", padx=5)
                ctk.CTkButton(
                    btn_group,
                    text="📂 فتح المجلد",
                    width=100,
                    fg_color="#475569",
                    command=lambda path=d: os.startfile(path),
                ).pack(side="left", padx=5)

                ctk.CTkLabel(
                    r,
                    text=f"{os.path.basename(d)}\n{', '.join(m).upper()}",
                    font=("Segoe UI", 14, "bold"),
                    text_color="#EF4444",
                    justify="right",
                ).pack(side="right", padx=15, pady=10)

        ctk.CTkButton(
            self.container_global,
            text="🔙 الرجوع للوحة الرئيسية",
            fg_color="transparent",
            border_width=1,
            hover_color="#334155",
            command=self.show_main_view,
        ).pack(pady=10)

    def build_single_view(self, dossier):
        for w in self.container_single.winfo_children():
            w.destroy()

        header_lbl = ctk.CTkLabel(
            self.container_single,
            text=f"📂 نافذة الإصلاح اليدوي: {os.path.basename(dossier)}",
            font=("Segoe UI Black", 20),
            text_color=ACCENT_YELLOW,
        )
        header_lbl.pack(pady=(10, 20), anchor="e")

        ctk.CTkButton(
            self.container_single,
            text="📁 فتح مسار الملف في الويندوز",
            fg_color="#475569",
            command=lambda path=dossier: os.startfile(path),
        ).pack(pady=(0, 10))

        list_f = ctk.CTkScrollableFrame(self.container_single, fg_color="transparent")
        list_f.pack(pady=10, fill="both", expand=True)

        if self.engine and hasattr(self.engine, "global_missing_dict"):
            for m in self.engine.global_missing_dict.get(dossier, []):
                r = ctk.CTkFrame(list_f, fg_color=CARD_BG, corner_radius=10)
                r.pack(fill="x", pady=5)

                ctk.CTkButton(
                    r,
                    text="🔍 إدراج المستند المرجعي",
                    fg_color=ACCENT_CYAN,
                    text_color="#000000",
                    command=lambda m=m: self.remplace_manuel(dossier, m),
                ).pack(side="left", padx=15, pady=15)
                ctk.CTkLabel(
                    r,
                    text=f"{m} 📄",
                    font=("Segoe UI", 15, "bold"),
                    text_color="#EF4444",
                ).pack(side="right", padx=15)

        ctk.CTkButton(
            self.container_single,
            text="🔙 الرجوع للتقرير الشامل",
            fg_color="transparent",
            border_width=1,
            hover_color="#334155",
            command=self.show_global_view,
        ).pack(pady=10)

    # ==========================================
    # العمليات المساعدة لواجهات التقرير
    # ==========================================
    def copy_missing_numbers(self):
        if (
            self.engine
            and hasattr(self.engine, "global_missing_dict")
            and self.engine.global_missing_dict
        ):
            numbers = self.engine.missing_numbers(self.engine.global_missing_dict)
            self.clipboard_clear()
            self.clipboard_append(numbers)
            self.update()
            messagebox.showinfo("تأكيد", f"تم نسخ الأرقام بنجاح:\n\n{numbers}")
        else:
            messagebox.showwarning("تنبيه", "لا توجد أرقام لنسخها.")

    def auto_distribute_global(self):
        src = filedialog.askdirectory(title="توجيه النظام لمسار المخزن")
        if not src or not self.engine:
            return
        res = self.engine.auto_distribute_from_source(src)
        if res.get("ok"):
            messagebox.showinfo("نجاح", f"تم استرداد {res['copied']} وثيقة.")
            if self.engine.global_missing_dict:
                self.show_global_view()
            else:
                self.show_main_view()
        else:
            messagebox.showerror("خطأ", res.get("message", "فشلت العملية."))

    def batch_stamp_missing_zn2(self):
        if not self.engine:
            return
        res = self.engine.batch_stamp_missing_zn2()
        if res.get("ok"):
            messagebox.showinfo("نجاح", f"تم ختم {res['stamped']} ملف بنجاح.")
            if self.engine.global_missing_dict:
                self.show_global_view()
            else:
                self.show_main_view()
        else:
            messagebox.showwarning("تنبيه", res.get("message", "فشلت العملية."))

    def remplace_manuel(self, target_folder, missing_file_name):
        path = filedialog.askopenfilename(title=f"اختر ملف {missing_file_name}")
        if path and self.engine:
            res = self.engine.manual_insert_missing(target_folder, path)
            if res.get("ok"):
                # تحديث الواجهة بعد الإدراج
                if self.engine.global_missing_dict.get(target_folder):
                    self.show_single_view(target_folder)
                elif self.engine.global_missing_dict:
                    self.show_global_view()
                else:
                    self.show_main_view()
            else:
                messagebox.showerror("خطأ", res.get("message", "فشل الإدراج."))
