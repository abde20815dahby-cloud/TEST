import eel
import sys
import json
import subprocess
from datetime import datetime
from threading import Lock

from ancfcc_engine import AncfccEngine
from tools import (
    audit_tool,
    stamper_tool,
    pv_tool,
    kgo_tool,
    converter_tool,
    splitter_tool,
    dxf_tool,
    support_tool,
)

# تهيئة مجلد الويب
eel.init("web")
engine = AncfccEngine()

# قفل لمنع فتح حوارات متعددة بنفس الوقت (سبب شائع للتعليق)
_dialog_lock = Lock()


def _run_dialog_subprocess(mode: str, title: str, filetypes=None) -> str:
    """
    تشغيل حوار Tk في عملية Python منفصلة.
    هذا يتجنب تعليق Eel/Chrome عند بعض بيئات Windows.
    """
    filetypes = filetypes or []
    helper = (
        "import sys, json, tkinter as tk\n"
        "from tkinter import filedialog\n"
        "mode = sys.argv[1]\n"
        "title = sys.argv[2]\n"
        "fts = json.loads(sys.argv[3]) if len(sys.argv) > 3 else []\n"
        "root = tk.Tk()\n"
        "root.withdraw()\n"
        "root.attributes('-topmost', True)\n"
        "root.update_idletasks()\n"
        "value = filedialog.askdirectory(title=title, parent=root) if mode == 'dir' else filedialog.askopenfilename(title=title, filetypes=fts, parent=root)\n"
        "print(value or '', end='')\n"
        "root.destroy()\n"
    )
    with _dialog_lock:
        try:
            cp = subprocess.run(
                [sys.executable, "-c", helper, mode, title, json.dumps(filetypes, ensure_ascii=False)],
                capture_output=True,
                text=True,
                timeout=300,  # وقت كافٍ للمستخدم لاختيار المجلد/الملف
            )
            return (cp.stdout or "").strip()
        except Exception:
            return ""

def _pick_directory(title):
    return _run_dialog_subprocess("dir", title)

def _pick_file(title, filetypes):
    return _run_dialog_subprocess("file", title, filetypes)


# ==========================================
# السر لي غيخلي السكربت يولي خدام بفعالية قوية
# هاد الدالة غادي تصيفط الأخبار (Logs) مباشرة للويب
# ==========================================
def live_log_callback(message, msg_type="info"):
    try:
        # كتعيط لدالة الجافاسكريبت فـ index.html
        eel.update_live_log(message, msg_type)()
    except Exception:
        pass


# كنلصقو هاد الدالة فالمحرك باش يخدم بيها
engine.log_callback = live_log_callback


# دالة بايثون سيتم استدعاؤها من الواجهة
@eel.expose
def start_processing(task_name):
    print(f"[{task_name}] - يتم الآن معالجة الطلب في الخلفية...")
    return f"تم بدء {task_name} بنجاح! المحرك يعمل بأقصى طاقة ⚡"


@eel.expose
def select_project_folder():
    folder = _pick_directory("تحديد مسار مشروع التحديد")
    if folder:
        engine.set_project_root(folder)
        return {"ok": True, "path": folder}
    return {"ok": False, "path": ""}


@eel.expose
def select_folder_for(tool_key):
    titles = {"stamper": "تحديد مجلد الوثائق", "pv": "تحديد مستودع PV", "kgo": "تحديد مجلد الملفات الخام لـ KGO", "converter": "تحديد مجلد التحويل", "zip": "تحديد مجلد التصدير ZIP", "recovery": "تحديد مسار المخزن للاسترداد"}
    title = titles.get(tool_key, "تحديد المجلد")
    folder = _pick_directory(title)
    if not folder:
        return {"ok": False, "path": ""}
    if tool_key == "stamper":
        engine.set_stamp_source(folder)
    elif tool_key == "pv":
        engine.set_pv_source(folder)
    elif tool_key == "kgo":
        engine.set_kgo_source(folder)
    elif tool_key == "converter":
        engine.set_conv_source(folder)
    elif tool_key in ("zip", "recovery"):
        return {"ok": True, "path": folder}
    else:
        return {"ok": False, "path": ""}
    return {"ok": True, "path": folder}


@eel.expose
def select_split_pdf():
    path = _pick_file("تحديد ملف PDF", [("PDF Files", "*.pdf")])
    if not path:
        return {"ok": False, "path": ""}
    engine.set_split_pdf(path)
    return {"ok": True, "path": path}


@eel.expose
def select_source_file(title="اختر المستند المرجعي", filetypes=None):
    if filetypes is None:
        filetypes = [("PDF Files", "*.pdf"), ("All Files", "*.*")]
    path = _pick_file(title, filetypes)
    return {"ok": bool(path), "path": path or ""}


@eel.expose
def open_folder(path):
    import os
    if path and os.path.isdir(path):
        os.startfile(path)
        return {"ok": True}
    return {"ok": False}


@eel.expose
def select_acme_exe():
    path = _pick_file("تحديد Acme CAD", [("Executable", "*.exe")])
    if not path:
        return {"ok": False, "path": ""}
    engine.set_acme_path(path)
    return {"ok": True, "path": path}


@eel.expose
def run_engineering_tool(tool_key):
    try:
        return audit_tool.run(engine, tool_key)
    except Exception as exc:
        return {
            "ok": False,
            "tool": tool_key,
            "message": f"خطأ أثناء التنفيذ: {exc}",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }


@eel.expose
def run_advanced_tool(tool_key, options=None):
    options = options or {}
    try:
        if tool_key == "stamper":
            return stamper_tool.run(engine, options)

        if tool_key == "pv":
            return pv_tool.run(engine, options)

        if tool_key == "kgo":
            return kgo_tool.run(engine, options)

        if tool_key == "converter":
            return converter_tool.run(engine, options)

        if tool_key == "splitter":
            return splitter_tool.run(engine, options)

        if tool_key == "dxf":
            return dxf_tool.run(engine)

        return {"ok": False, "message": "أداة غير معروفة.", "timestamp": datetime.now().strftime("%H:%M:%S")}
    except Exception as exc:
        return {"ok": False, "message": f"خطأ أثناء التنفيذ: {exc}", "timestamp": datetime.now().strftime("%H:%M:%S")}


@eel.expose
def get_missing_zn_pdfs():
    """
    قائمة ملفات PDF التي تحتوي على ZN ضمن مجلدات تقرير النواقص (حيث zn2.pdf لا يزال ناقصاً).
    تُستخدم لمعاينة موضع الختم بنفس آلية وحدة ZN.
    """
    import os

    data = getattr(engine, "global_missing_dict", None) or {}
    pdfs = []
    for folder, missing_list in data.items():
        if not folder or not os.path.isdir(folder):
            continue
        if "zn2.pdf" not in [m.lower() for m in (missing_list or [])]:
            continue
        try:
            for f in os.listdir(folder):
                fl = f.lower()
                if "zn" in fl and fl.endswith(".pdf"):
                    fp = os.path.join(folder, f)
                    if os.path.isfile(fp):
                        full = os.path.normpath(os.path.abspath(fp))
                        label = f"{os.path.basename(folder)} / {f}"
                        pdfs.append({"path": full, "name": label.replace("\\", " / ")})
        except Exception:
            continue
    pdfs.sort(key=lambda x: x["name"].lower())
    return {"ok": True, "pdfs": pdfs[:80]}


@eel.expose
def get_stamp_folder_pdfs():
    """إرجاع قائمة ملفات PDF من المجلد وجميع المجلدات الفرعية"""
    import os
    folder = engine.stamp_source if engine.stamp_source else ""
    if not folder or not os.path.isdir(folder):
        return {"ok": False, "pdfs": [], "message": "لم يُحدد مجلد صالح"}
    pdfs = []
    folder = os.path.normpath(os.path.abspath(folder))
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(".pdf"):
                full = os.path.normpath(os.path.join(root, f))
                rel = os.path.relpath(full, folder)
                pdfs.append({"path": full, "name": rel.replace("\\", " / ")})
    pdfs.sort(key=lambda x: x["name"].lower())
    return {"ok": True, "pdfs": pdfs[:80]}


def _render_pdf_page_to_b64(pdf_path: str, page_num: int = 0):
    """فتح PDF وإرجاع معاينة الصفحة أو None مع رسالة خطأ."""
    import base64
    import os
    import fitz

    pdf_path = os.path.normpath(os.path.abspath(pdf_path))
    if not os.path.isfile(pdf_path):
        return None, "الملف غير موجود على القرص"

    doc = None
    try:
        doc = fitz.open(pdf_path)
        n = doc.page_count
        if n < 1:
            return None, "ملف PDF بدون صفحات (فارغ أو تالف)"

        idx = max(0, min(int(page_num), n - 1))
        page = doc.load_page(idx)
        if page is None:
            return None, "لا يمكن قراءة الصفحة"

        pix = page.get_pixmap(dpi=120, alpha=False)
        img_bytes = pix.tobytes("png")
        pdf_w = float(page.rect.width)
        pdf_h = float(page.rect.height)
        b64 = base64.b64encode(img_bytes).decode()
        return (
            {
                "ok": True,
                "b64": b64,
                "width": pix.width,
                "height": pix.height,
                "pdf_w": pdf_w,
                "pdf_h": pdf_h,
                "path_used": pdf_path,
            },
            None,
        )
    except Exception as e:
        return None, str(e)
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass


@eel.expose
def get_pdf_preview(pdf_path, page_num=0):
    """إرجاع صفحة PDF كصورة base64 للمعاينة التفاعلية"""
    data, err = _render_pdf_page_to_b64(pdf_path, int(page_num) if page_num is not None else 0)
    if err:
        return {"ok": False, "message": err}
    return data


@eel.expose
def get_stamp_preview_auto():
    """
    يجرب أول ملف PDF صالح من مجلد الختم (بما فيه المجلدات الفرعية)
    لمعاينة بدون طلب اختيار ملف يدوياً.
    """
    res = get_stamp_folder_pdfs()
    if not res.get("ok") or not res.get("pdfs"):
        return {"ok": False, "message": res.get("message", "لا توجد ملفات PDF في المجلد")}
    for item in res["pdfs"]:
        path = item["path"]
        data, err = _render_pdf_page_to_b64(path, 0)
        if data:
            data["pdf_label"] = item["name"]
            return data
    return {"ok": False, "message": "لم يُعثر على PDF صالح للمعاينة (جميع الملفات فارغة أو تالفة)"}


@eel.expose
def run_support_tool(tool_key, options=None):
    options = options or {}
    try:
        return support_tool.run(engine, tool_key, options)
    except Exception as exc:
        return {"ok": False, "message": f"خطأ أثناء التنفيذ: {exc}", "timestamp": datetime.now().strftime("%H:%M:%S")}


# تشغيل البرنامج
try:
    # فتح نافذة بحجم احترافي
    eel.start("index.html", size=(1300, 850), mode="chrome")
except (SystemExit, MemoryError, KeyboardInterrupt):
    sys.exit()
