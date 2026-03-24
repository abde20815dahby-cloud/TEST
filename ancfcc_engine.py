import os
import re
import shutil
import time
import subprocess
from typing import Dict, List

import fitz
import pythoncom
import win32com.client
try:
    from pywinauto import Application
except Exception:
    Application = None


USER_DOCS = os.path.join(os.path.expanduser("~"), "Documents")
TRASH_DIR = os.path.join(USER_DOCS, "ANCFCC_Trash")
BACKUP_DIR = os.path.join(USER_DOCS, "ANCFCC_Backups")
os.makedirs(TRASH_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

SUFFIXES_REQUIS = [
    "MINUTE-PV.pdf",
    "PHOTO-A4.pdf",
    "PLAN.dxf",
    "PLAN.PDF",
    "ST284.pdf",
    "TAB-A.pdf",
    "ZN2.pdf",
]


class AncfccEngine:
    def __init__(self) -> None:
        self.project_root = ""
        self.stamp_source = ""
        self.pv_source = ""
        self.conv_source = ""
        self.kgo_source = ""
        self.split_pdf_path = ""
        self.acme_cad_path = r"C:\Program Files (x86)\Acme CAD Converter\AcmeCADConverter.exe"
        self.kgo_exe_path = r"C:\KolidaKGO\KGO\bin\ToRinex4\ToRinex4-64.exe"
        base_dir = os.path.dirname(os.path.realpath(__file__))
        web_dir = os.path.join(base_dir, "web")
        self.stamp_img = ""
        for d in (web_dir, base_dir):
            for ext in ("png", "jpg"):
                p = os.path.join(d, f"stamp.{ext}")
                if os.path.exists(p):
                    self.stamp_img = p
                    break
            if self.stamp_img:
                break
        self.history = ActionHistoryManager()
        self.global_missing_dict: Dict[str, List[str]] = {}
        self.log_callback = None

    def _log(self, msg: str, msg_type: str = "info") -> None:
        if self.log_callback:
            try:
                self.log_callback(msg, msg_type)
            except Exception:
                pass

    def set_project_root(self, project_root: str) -> None:
        self.project_root = project_root

    def set_stamp_source(self, path: str) -> None:
        self.stamp_source = path

    def set_pv_source(self, path: str) -> None:
        self.pv_source = path

    def set_conv_source(self, path: str) -> None:
        self.conv_source = path

    def set_kgo_source(self, path: str) -> None:
        self.kgo_source = path

    def set_split_pdf(self, path: str) -> None:
        self.split_pdf_path = path

    def set_acme_path(self, path: str) -> None:
        self.acme_cad_path = path

    def set_kgo_exe_path(self, path: str) -> None:
        self.kgo_exe_path = path

    @staticmethod
    def _kgo_get_folder_size(folder: str) -> int:
        total_size = 0
        try:
            for dirpath, _, filenames in os.walk(folder):
                for filename in filenames:
                    fp = os.path.join(dirpath, filename)
                    if not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
        except Exception:
            pass
        return total_size

    @staticmethod
    def _kgo_force_close(proc=None) -> None:
        os.system("taskkill /f /t /im ToRinex4-64.exe >nul 2>&1")
        os.system("taskkill /f /t /im ToRinex4.exe >nul 2>&1")
        if proc is not None:
            try:
                proc.kill()
            except Exception:
                pass

    def run_kgo_torinex(self, src_folder: str = "", exe_path: str = "") -> Dict[str, object]:
        """
        تشغيل ToRinex4 عبر KGO بشكل آلي ثم انتظار اكتمال التحويل.
        """
        source = (src_folder or self.kgo_source or "").strip()
        exe = (exe_path or self.kgo_exe_path or "").strip()
        if not source or not os.path.isdir(source):
            return {"ok": False, "message": "حدد مجلد KGO الصحيح أولاً."}
        if not exe or not os.path.isfile(exe):
            return {"ok": False, "message": "مسار ToRinex4 غير صحيح."}
        if Application is None:
            return {"ok": False, "message": "مكتبة pywinauto غير متاحة. ثبّت الحزمة أولاً."}

        self._log("🚀 إغلاق أي نسخة قديمة لضمان بدء نظيف...", "info")
        proc = None
        try:
            self._kgo_force_close()
            time.sleep(1)

            out_folder = os.path.join(source, "RINEX_CONVERTED")
            os.makedirs(out_folder, exist_ok=True)
            self._log("📂 [1/5] تهيئة المسارات...", "info")
            os.chdir(source)

            connected = False
            main_dlg = None
            self._log("🚀 [2/5] تشغيل ToRinex4...", "info")
            for attempt in range(1, 4):
                self._log(f"   - محاولة التشغيل رقم {attempt}...", "info")
                proc = subprocess.Popen([exe])
                time.sleep(4)
                try:
                    app = Application(backend="win32").connect(title_re=".*ToRinex.*", timeout=2)
                    main_dlg = app.window(title_re=".*ToRinex.*")
                    if main_dlg.exists():
                        connected = True
                        self._log("✅ ظهرت الواجهة والملفات مقروءة بداخلها!", "success")
                        break
                except Exception:
                    self._log("⚠️ البرنامج لم يفتح، سيتم إعادة المحاولة...", "error")

            if not connected or main_dlg is None:
                return {"ok": False, "message": "فشل تشغيل برنامج ToRinex4."}

            main_dlg.set_focus()
            self._log("📂 [3/5] تحديد مسار مجلد الحفظ...", "info")
            all_edits = main_dlg.children(class_name="Edit")
            if len(all_edits) >= 2:
                all_edits[1].set_edit_text(out_folder)
                time.sleep(1)

            self._log("⚙️ [4/5] اختيار صيغة RINEX وتحديد الكل...", "info")
            try:
                all_combos = main_dlg.children(class_name="ComboBox")
                for combo in all_combos:
                    combo.select("3.02")
                    break
            except Exception:
                pass
            time.sleep(1)
            try:
                main_dlg.child_window(title="Select All", class_name="Button").click()
            except Exception:
                self._log("⚠️ تعذر النقر على زر Select All.", "error")
            time.sleep(1)

            self._log("▶️ [5/5] بدء التحويل...", "info")
            try:
                main_dlg.child_window(title="Convert", class_name="Button").click()
            except Exception:
                return {"ok": False, "message": "تعذر النقر على زر Convert."}

            start = time.time()
            time.sleep(3)
            last_size = -1
            unchanged_count = 0
            self._log("⏳ جاري المعالجة... مراقبة حجم الملفات المستخرجة.", "info")
            while time.time() - start < 3600:
                current_size = self._kgo_get_folder_size(out_folder)
                if current_size > 0 and current_size == last_size:
                    unchanged_count += 1
                else:
                    unchanged_count = 0
                last_size = current_size
                if unchanged_count >= 3:
                    self._log("🎉 اكتمل التحويل 100%!", "success")
                    self._kgo_force_close(proc)
                    return {"ok": True, "message": f"تم تحويل الملفات بنجاح داخل: {out_folder}"}
                time.sleep(2)

            self._log("⚠️ انتهى الوقت الأقصى وسيتم الإغلاق.", "error")
            self._kgo_force_close(proc)
            return {"ok": False, "message": "انتهى الوقت الأقصى قبل اكتمال التحويل."}
        except Exception as exc:
            self._kgo_force_close(proc)
            return {"ok": False, "message": f"خطأ KGO: {exc}"}

    def backup_file(self, original_path: str) -> None:
        if os.path.exists(original_path):
            try:
                backup_name = f"{os.path.basename(original_path)}.bak_{int(time.time())}"
                shutil.copy2(original_path, os.path.join(BACKUP_DIR, backup_name))
            except Exception:
                pass

    def open_backup_folder(self) -> Dict[str, object]:
        try:
            os.startfile(BACKUP_DIR)
            return {"ok": True, "message": "تم فتح مجلد النسخ الاحتياطية."}
        except Exception as exc:
            return {"ok": False, "message": f"تعذر فتح المجلد: {exc}"}

    def _all_subfolders(self) -> List[str]:
        if not self.project_root or not os.path.isdir(self.project_root):
            return []
        subfolders = [
            os.path.join(self.project_root, d)
            for d in os.listdir(self.project_root)
            if os.path.isdir(os.path.join(self.project_root, d))
        ]
        return subfolders if subfolders else [self.project_root]

    def _is_file_allowed(self, filename: str, has_final_pv: bool) -> bool:
        name_lower = filename.lower()
        for req in SUFFIXES_REQUIS:
            req_lower = req.lower()
            if req_lower == "zn2.pdf" and "zn" in name_lower and name_lower.endswith(".pdf"):
                return True
            if name_lower.endswith(req_lower):
                return True
        if not has_final_pv and ("minute-pv" in name_lower or name_lower.endswith((".doc", ".docx"))):
            return True
        return False

    def _verifier_cachet_zn2(self, pdf_path: str) -> bool:
        try:
            doc = fitz.open(pdf_path)
            found = False
            for page in doc:
                annots = page.annots()
                if annots and any(a.type[0] == 8 for a in annots):
                    found = True
                    break
                if len(page.get_images(full=True)) >= 2:
                    found = True
                    break
                text = page.get_text().lower()
                if "soritopo" in text or "sarl" in text or "topographiques" in text:
                    found = True
                    break
            doc.close()
            return found
        except Exception:
            return False

    def clean_extras(self) -> Dict[str, object]:
        self._log("بدء عزل وتطهير الملفات الدخيلة...", "info")
        moved = 0
        touched = 0
        self.history.start_batch("تطهير الملفات الدخيلة")
        for folder in self._all_subfolders():
            if folder in (TRASH_DIR, BACKUP_DIR):
                continue
            try:
                items = os.listdir(folder)
            except Exception:
                continue
            touched += 1
            has_final_pv = any(
                f.lower().endswith("minute-pv.pdf")
                for f in items
                if os.path.isfile(os.path.join(folder, f))
            )
            for item in items:
                item_path = os.path.join(folder, item)
                if os.path.isdir(item_path) or not self._is_file_allowed(item, has_final_pv):
                    try:
                        self.history.record_before(item_path)
                        shutil.move(item_path, os.path.join(TRASH_DIR, f"{item}_{int(time.time())}"))
                        self.history.record_after(item_path)
                        moved += 1
                    except Exception:
                        continue
        self.history.commit_batch()
        self._log(f"تم التطهير: نقل {moved} عنصر من {touched} مجلد.", "success")
        return {"moved_count": moved, "folders_scanned": touched}

    def check_missing(self) -> Dict[str, List[str]]:
        self._log("جاري فحص النواقص...", "info")
        missing_map: Dict[str, List[str]] = {}
        for folder in self._all_subfolders():
            if folder in (TRASH_DIR, BACKUP_DIR):
                continue
            try:
                files = os.listdir(folder)
            except Exception:
                continue
            errors = []
            for req in SUFFIXES_REQUIS:
                req_lower = req.lower()
                matching = [
                    f
                    for f in files
                    if (
                        req_lower == "zn2.pdf"
                        and "zn" in f.lower()
                        and f.lower().endswith(".pdf")
                    )
                    or (req_lower != "zn2.pdf" and f.lower().endswith(req_lower))
                ]
                if not matching:
                    errors.append(req_lower)
                elif req_lower == "zn2.pdf" and not any(
                    self._verifier_cachet_zn2(os.path.join(folder, f)) for f in matching
                ):
                    errors.append(req_lower)
            if errors:
                missing_map[folder] = errors
        self._log(f"انتهى الفحص: {len(missing_map)} مجلد به نواقص." if missing_map else "لا توجد نواقص.", "success" if not missing_map else "info")
        return missing_map

    @staticmethod
    def missing_numbers(missing_map: Dict[str, List[str]]) -> str:
        numbers_only = [
            re.sub(r"[^\d]", "", os.path.basename(folder))
            for folder in missing_map.keys()
            if re.sub(r"[^\d]", "", os.path.basename(folder))
        ]
        return ", ".join(filter(None, numbers_only))

    def stamp_pdfs(
        self,
        filter_mode: str = "zn_only",
        x: float = 20.0,
        y: float = 20.0,
        w: float = 150.0,
        h: float = 80.0,
    ) -> Dict[str, object]:
        if not self.stamp_source or not os.path.isdir(self.stamp_source):
            return {"ok": False, "message": "مسار وثائق الختم غير صالح."}
        if not self.stamp_img or not os.path.exists(self.stamp_img):
            return {"ok": False, "message": "ملف الختم (stamp.png/jpg) غير موجود."}

        self._log("جاري ختم الوثائق...", "info")
        targets = []
        for dirpath, _, filenames in os.walk(self.stamp_source):
            for filename in filenames:
                if not filename.lower().endswith(".pdf"):
                    continue
                if filter_mode == "zn_only" and "zn" not in filename.lower():
                    continue
                targets.append(os.path.join(dirpath, filename))

        success = 0
        self.history.start_batch("ختم وثائق ZN")
        for src_path in targets:
            temp = src_path + ".tmp"
            try:
                self.backup_file(src_path)
                self.history.record_before(src_path)
                doc = fitz.open(src_path)
                rect = fitz.Rect(x, y, x + w, y + h)
                for page in doc:
                    page.insert_image(rect, filename=self.stamp_img)
                doc.save(temp, deflate=False)
                doc.close()
                os.replace(temp, src_path)
                self.history.record_after(src_path)
                success += 1
            except Exception:
                continue
        self.history.commit_batch()
        self._log(f"تم ختم {success} من {len(targets)} ملف.", "success")
        return {"ok": True, "total": len(targets), "success": success}

    def process_pv(self, do_convert: bool, do_merge: bool, do_sort: bool) -> Dict[str, object]:
        if not self.pv_source or not os.path.isdir(self.pv_source):
            return {"ok": False, "message": "مسار PV غير صالح."}
        logs = []
        errors = 0
        self.history.start_batch("معالجة PV")

        if do_convert:
            word = None
            try:
                pythoncom.CoInitialize()
                word = win32com.client.DispatchEx("Word.Application")
                try:
                    word.Visible = False
                except Exception:
                    pass
                for root_dir, _, files in os.walk(self.pv_source):
                    for filename in [f for f in files if f.lower().endswith((".doc", ".docx"))]:
                        file_path = os.path.abspath(os.path.join(root_dir, filename))
                        pdf_path = os.path.abspath(
                            os.path.join(root_dir, os.path.splitext(filename)[0] + ".pdf")
                        )
                        if os.path.exists(pdf_path):
                            continue
                        try:
                            self.history.record_before(pdf_path)
                            doc = word.Documents.Open(file_path)
                            for section in doc.Sections:
                                if "-A3" in filename.upper():
                                    section.PageSetup.PaperSize = 8
                                elif "-A4" in filename.upper():
                                    section.PageSetup.PaperSize = 7
                            doc.ExportAsFixedFormat(pdf_path, 17, OptimizeFor=0)
                            doc.Close(False)
                            self.history.record_after(pdf_path)
                            logs.append(f"تم تحويل: {os.path.basename(pdf_path)}")
                        except Exception:
                            errors += 1
            except Exception:
                errors += 1
            finally:
                if word:
                    try:
                        word.Quit()
                    except Exception:
                        pass
                pythoncom.CoUninitialize()

        if do_merge:
            for root_dir, _, files in os.walk(self.pv_source):
                pdf_files = [f for f in files if f.lower().endswith(".pdf")]
                parrels_groups = {}
                for file in pdf_files:
                    base_name = re.sub(r"(?i)-A3\.pdf|-A4\.pdf|\.pdf", "", file)
                    if file.lower() == f"{base_name.lower()}.pdf":
                        continue
                    if "-A3" in file.upper() or "-A4" in file.upper():
                        parrels_groups.setdefault(base_name, []).append(file)
                for base_name, group_files in parrels_groups.items():
                    if len(group_files) <= 1:
                        continue
                    group_files.sort(reverse=True)
                    final_pdf_path = os.path.join(root_dir, f"{base_name}.pdf")
                    try:
                        self.history.record_before(final_pdf_path)
                        merged_doc = fitz.open()
                        for file in group_files:
                            with fitz.open(os.path.join(root_dir, file)) as sub_doc:
                                merged_doc.insert_pdf(sub_doc)
                        merged_doc.save(final_pdf_path, deflate=False)
                        merged_doc.close()
                        self.history.record_after(final_pdf_path)
                        logs.append(f"تم دمج: {base_name}.pdf")
                    except Exception:
                        errors += 1

        if do_sort:
            for root_dir, _, files in os.walk(self.pv_source):
                for filename in files:
                    file_path = os.path.join(root_dir, filename)
                    if not (
                        filename.lower().endswith(".pdf")
                        and "MINUTE-PV" in filename.upper()
                        and "-A3" not in filename.upper()
                        and "-A4" not in filename.upper()
                    ):
                        continue
                    try:
                        doc = fitz.open(file_path)
                        valid_pages = []
                        for i, page in enumerate(doc):
                            text = page.get_text().upper()
                            if not text or len(text.strip()) <= 5:
                                continue
                            weight = 100
                            if re.search(r"PROC[EÉÈ]S.*BORNAGE", text):
                                weight = 10
                            elif re.search(r"REP[EÉÈ]RAGE|RIVERAINS", text):
                                match = re.search(r"PAGE[^\d]*(\d+)", text)
                                weight = 20 + int(match.group(1)) if match else 29
                            elif re.search(r"CONTENANCE|DROITS R[EÉÈ]ELS", text):
                                weight = 80
                            elif re.search(r"OPPOSITION|REVENDICATION|D[EÉÈ]L[EÉÈ]GU[EÉÈ]", text):
                                weight = 90
                            valid_pages.append((weight, i))
                        if valid_pages:
                            valid_pages.sort(key=lambda x: (x[0], x[1]))
                            doc.select([p[1] for p in valid_pages])
                            new_filename = (
                                filename.upper()
                                .replace("-AQUISSEMENT", "")
                                .replace("AQUISSEMENT", "")
                                .replace(".PDF", ".pdf")
                            )
                            new_file_path = os.path.join(root_dir, new_filename)
                            temp_path = file_path + ".tmp"
                            self.backup_file(file_path)
                            self.history.record_before(file_path)
                            self.history.record_before(new_file_path)
                            doc.save(temp_path, deflate=False)
                            doc.close()
                            os.replace(temp_path, new_file_path)
                            if file_path != new_file_path and os.path.exists(file_path):
                                os.remove(file_path)
                            self.history.record_after(file_path)
                            self.history.record_after(new_file_path)
                            logs.append(f"تم ترتيب: {new_filename}")
                        else:
                            doc.close()
                    except Exception:
                        errors += 1

        self.history.commit_batch()
        return {"ok": True, "errors": errors, "log_count": len(logs)}

    def convert_office(self, do_word: bool, do_excel: bool, paper_size: str) -> Dict[str, object]:
        if not self.conv_source or not os.path.isdir(self.conv_source):
            return {"ok": False, "message": "مسار التحويل غير صالح."}
        pythoncom.CoInitialize()
        word_app = None
        excel_app = None
        success = 0
        errors = 0
        self.history.start_batch("تحويل وثائق إدارية")
        try:
            if do_word:
                try:
                    word_app = win32com.client.DispatchEx("Word.Application")
                    try:
                        word_app.Visible = False
                    except Exception:
                        pass
                except Exception:
                    do_word = False
            if do_excel:
                try:
                    excel_app = win32com.client.DispatchEx("Excel.Application")
                    excel_app.DisplayAlerts = False
                    try:
                        excel_app.Visible = False
                    except Exception:
                        pass
                except Exception:
                    do_excel = False

            for root_dir, _, files in os.walk(self.conv_source):
                for filename in files:
                    if filename.startswith("~$"):
                        continue
                    file_path = os.path.abspath(os.path.join(root_dir, filename))
                    file_name_no_ext, file_ext = os.path.splitext(file_path)
                    output_path = file_name_no_ext + ".pdf"
                    if os.path.exists(output_path):
                        continue
                    ext = file_ext.lower()
                    if do_word and ext in [".docx", ".doc", ".rtf"]:
                        try:
                            self.history.record_before(output_path)
                            doc = word_app.Documents.Open(file_path)
                            for section in doc.Sections:
                                section.PageSetup.PaperSize = 8 if paper_size == "A3" else 7
                            doc.ExportAsFixedFormat(output_path, 17, OptimizeFor=0)
                            doc.Close(False)
                            self.history.record_after(output_path)
                            success += 1
                        except Exception:
                            errors += 1
                    elif do_excel and ext in [".xlsx", ".xls", ".csv"]:
                        try:
                            self.history.record_before(output_path)
                            wb = excel_app.Workbooks.Open(file_path)
                            for sheet in wb.Sheets:
                                sheet.PageSetup.PaperSize = 8 if paper_size == "A3" else 9
                                sheet.PageSetup.Zoom = False
                                sheet.PageSetup.FitToPagesWide = 1
                                sheet.PageSetup.FitToPagesTall = False
                            wb.ExportAsFixedFormat(0, output_path, Quality=0)
                            wb.Close(False)
                            self.history.record_after(output_path)
                            success += 1
                        except Exception:
                            errors += 1
        finally:
            if word_app:
                try:
                    word_app.Quit()
                except Exception:
                    pass
            if excel_app:
                try:
                    excel_app.DisplayAlerts = True
                    excel_app.Quit()
                except Exception:
                    pass
            pythoncom.CoUninitialize()
        self.history.commit_batch()
        return {"ok": True, "success": success, "errors": errors}

    def split_pdf(self, layout: str) -> Dict[str, object]:
        if not self.split_pdf_path or not os.path.isfile(self.split_pdf_path):
            return {"ok": False, "message": "ملف PDF للتقطيع غير صالح."}
        base_dir = os.path.dirname(self.split_pdf_path)
        base_name = os.path.splitext(os.path.basename(self.split_pdf_path))[0]
        parts = 0
        self.history.start_batch("تقطيع خرائط PDF")
        try:
            doc = fitz.open(self.split_pdf_path)
            page = doc[0]
            w, h = page.rect.width, page.rect.height
            if layout == "2x2":
                rects = [
                    fitz.Rect(0, 0, w / 2, h / 2),
                    fitz.Rect(w / 2, 0, w, h / 2),
                    fitz.Rect(0, h / 2, w / 2, h),
                    fitz.Rect(w / 2, h / 2, w, h),
                ]
            elif layout == "4x1":
                rects = [fitz.Rect(0, i * (h / 4), w, (i + 1) * (h / 4)) for i in range(4)]
            else:
                rects = [fitz.Rect(i * (w / 4), 0, (i + 1) * (w / 4), h) for i in range(4)]

            for i, rect in enumerate(rects):
                out_path = os.path.join(base_dir, f"{base_name}_Partie_{i + 1}.pdf")
                self.history.record_before(out_path)
                out_pdf = fitz.open()
                out_page = out_pdf.new_page(width=rect.width, height=rect.height)
                out_page.show_pdf_page(out_page.rect, doc, 0, clip=rect)
                out_pdf.save(out_path, deflate=False)
                out_pdf.close()
                self.history.record_after(out_path)
                parts += 1
            doc.close()
            self.history.commit_batch()
            return {"ok": True, "parts": parts}
        except Exception as exc:
            self.history.commit_batch()
            return {"ok": False, "message": str(exc)}

    def launch_acme(self) -> Dict[str, object]:
        if not os.path.exists(self.acme_cad_path):
            return {"ok": False, "message": "مسار برنامج Acme CAD غير صحيح."}
        try:
            subprocess.Popen([self.acme_cad_path])
            return {"ok": True, "message": "تم فتح واجهة Acme CAD بنجاح."}
        except Exception as exc:
            return {"ok": False, "message": f"تعذر فتح البرنامج: {exc}"}

    def export_zip_packages(self, parent_folder: str) -> Dict[str, object]:
        if not parent_folder or not os.path.isdir(parent_folder):
            return {"ok": False, "message": "مجلد ZIP غير صالح."}
        count = 0
        for folder in os.listdir(parent_folder):
            folder_path = os.path.join(parent_folder, folder)
            if not os.path.isdir(folder_path):
                continue
            try:
                shutil.make_archive(
                    base_name=folder_path, format="zip", root_dir=parent_folder, base_dir=folder
                )
                count += 1
            except Exception:
                continue
        return {"ok": True, "count": count}

    def auto_distribute_from_source(self, source_folder: str) -> Dict[str, object]:
        """استرداد الملفات الناقصة من مجلد المخزن بناءً على أرقام المجلدات."""
        if not source_folder or not os.path.isdir(source_folder):
            return {"ok": False, "message": "مسار المخزن غير صالح.", "copied": 0}
        if not self.global_missing_dict:
            return {"ok": True, "message": "لا توجد نواقص للاسترداد.", "copied": 0}

        def num_from_path(p: str) -> str:
            return re.sub(r"[^\d]", "", os.path.basename(p))

        store_subfolders = {}
        for d in os.listdir(source_folder):
            path = os.path.join(source_folder, d)
            if os.path.isdir(path):
                n = num_from_path(d)
                if n:
                    store_subfolders.setdefault(n, []).append(path)

        copied = 0
        self.history.start_batch("استرداد من المخزن")
        still_missing = {}
        for folder, missing_list in list(self.global_missing_dict.items()):
            fnum = num_from_path(folder)
            if not fnum:
                still_missing[folder] = missing_list
                continue
            store_candidates = store_subfolders.get(fnum, [])
            remaining = []
            for req in missing_list:
                req_lower = req.lower()
                found = False
                for store_path in store_candidates:
                    try:
                        files = os.listdir(store_path)
                    except Exception:
                        continue
                    for f in files:
                        fp = os.path.join(store_path, f)
                        if not os.path.isfile(fp):
                            continue
                        fl = f.lower()
                        match = False
                        if req_lower == "zn2.pdf":
                            match = "zn" in fl and fl.endswith(".pdf")
                        else:
                            match = fl.endswith(req_lower)
                        if match:
                            dest = os.path.join(folder, f)
                            if os.path.exists(dest):
                                self.backup_file(dest)
                            self.history.record_before(dest)
                            shutil.copy2(fp, dest)
                            self.history.record_after(dest)
                            copied += 1
                            found = True
                            break
                    if found:
                        break
                if not found:
                    remaining.append(req)
            if remaining:
                still_missing[folder] = remaining
        self.history.commit_batch()
        self.global_missing_dict = still_missing
        return {"ok": True, "copied": copied, "message": f"تم استرداد {copied} وثيقة."}

    def batch_stamp_missing_zn2(self, x: float = 20.0, y: float = 20.0, w: float = 150.0, h: float = 80.0) -> Dict[str, object]:
        """ختم جماعي لملفات ZN غير المختمة في المجلدات الناقصة.

        نفس آلية insert_image لوحدة stamp_pdfs (نقاط PDF: x,y وعرض وارتفاع الصورة).
        """
        if not self.stamp_img or not os.path.exists(self.stamp_img):
            return {"ok": False, "message": "ملف الختم غير موجود.", "stamped": 0}
        if not self.global_missing_dict:
            return {"ok": True, "message": "لا توجد نواقص.", "stamped": 0}

        stamped = 0
        self.history.start_batch("ختم جماعي ZN2")
        still_missing = {}
        for folder, missing_list in list(self.global_missing_dict.items()):
            if "zn2.pdf" not in [m.lower() for m in missing_list]:
                still_missing[folder] = missing_list
                continue
            zn_files = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if "zn" in f.lower() and f.lower().endswith(".pdf") and os.path.isfile(os.path.join(folder, f))
            ]
            stamped_this = False
            for src_path in zn_files:
                if self._verifier_cachet_zn2(src_path):
                    continue
                temp = src_path + ".tmp"
                try:
                    self.backup_file(src_path)
                    self.history.record_before(src_path)
                    doc = fitz.open(src_path)
                    rect = fitz.Rect(x, y, x + w, y + h)
                    for page in doc:
                        page.insert_image(rect, filename=self.stamp_img)
                    doc.save(temp, deflate=False)
                    doc.close()
                    os.replace(temp, src_path)
                    self.history.record_after(src_path)
                    stamped += 1
                    stamped_this = True
                except Exception:
                    pass
            remaining = [m for m in missing_list if m.lower() != "zn2.pdf"]
            if not stamped_this and "zn2.pdf" in [x.lower() for x in missing_list]:
                remaining.append("zn2.pdf")
            if remaining:
                still_missing[folder] = remaining
        self.history.commit_batch()
        self.global_missing_dict = still_missing
        return {"ok": True, "stamped": stamped, "message": f"تم ختم {stamped} ملف بنجاح."}

    def manual_insert_missing(
        self, target_folder: str, source_file_path: str, missing_file_name: str
    ) -> Dict[str, object]:
        """إدراج يدوي لملف ناقص من مستند مرجعي."""
        if not source_file_path or not os.path.isfile(source_file_path):
            return {"ok": False, "message": "الملف المصدري غير صالح."}
        if not target_folder or not os.path.isdir(target_folder):
            return {"ok": False, "message": "المجلد الهدف غير صالح."}
        req = missing_file_name.lower()
        req_ext = os.path.splitext(req)[1].lower()
        src_ext = os.path.splitext(source_file_path)[1].lower()
        if req == "zn2.pdf":
            if src_ext != ".pdf":
                return {"ok": False, "message": "ملف ZN يجب أن يكون PDF."}
            base = re.sub(r"[^\d]", "", os.path.basename(target_folder)) or "zn"
            dest_name = f"{base}_ZN.pdf"
        else:
            if src_ext != req_ext:
                return {"ok": False, "message": f"امتداد الملف يجب أن يكون {req_ext}"}
            dest_name = req
        dest_path = os.path.join(target_folder, dest_name)
        try:
            self.backup_file(dest_path) if os.path.exists(dest_path) else None
            self.history.start_batch("إدراج يدوي")
            self.history.record_before(dest_path)
            shutil.copy2(source_file_path, dest_path)
            self.history.record_after(dest_path)
            self.history.commit_batch()
            lst = self.global_missing_dict.get(target_folder, [])
            lst = [m for m in lst if m.lower() != req]
            if lst:
                self.global_missing_dict[target_folder] = lst
            else:
                self.global_missing_dict.pop(target_folder, None)
            return {"ok": True, "message": f"تم إدراج {dest_name} بنجاح."}
        except Exception as exc:
            return {"ok": False, "message": str(exc)}

    def undo(self) -> Dict[str, object]:
        ok, msg = self.history.undo()
        return {"ok": ok, "message": msg}

    def redo(self) -> Dict[str, object]:
        ok, msg = self.history.redo()
        return {"ok": ok, "message": msg}

    def history_state(self) -> Dict[str, object]:
        return {
            "undo_count": len(self.history.undo_stack),
            "redo_count": len(self.history.redo_stack),
        }


class ActionHistoryManager:
    def __init__(self):
        self.history_dir = os.path.join(USER_DOCS, "ANCFCC_Action_History")
        os.makedirs(self.history_dir, exist_ok=True)
        self.undo_stack = []
        self.redo_stack = []
        self.current_batch = None

    def start_batch(self, name):
        if self.current_batch:
            self.commit_batch()
        self.current_batch = {"name": name, "id": str(int(time.time() * 1000)), "changes": {}}

    def record_before(self, path):
        if not self.current_batch:
            return
        if path not in self.current_batch["changes"]:
            self.current_batch["changes"][path] = {"before": None, "after": None}
        if os.path.exists(path):
            safe_path = os.path.join(
                self.history_dir,
                f"{os.path.basename(path)}_{self.current_batch['id']}_before.bak",
            )
            shutil.copy2(path, safe_path)
            self.current_batch["changes"][path]["before"] = safe_path

    def record_after(self, path):
        if not self.current_batch:
            return
        if path not in self.current_batch["changes"]:
            self.current_batch["changes"][path] = {"before": None, "after": None}
        if os.path.exists(path):
            safe_path = os.path.join(
                self.history_dir,
                f"{os.path.basename(path)}_{self.current_batch['id']}_after.bak",
            )
            shutil.copy2(path, safe_path)
            self.current_batch["changes"][path]["after"] = safe_path

    def commit_batch(self):
        if self.current_batch and self.current_batch["changes"]:
            self.undo_stack.append(self.current_batch)
            self.redo_stack.clear()
        self.current_batch = None

    def undo(self):
        if not self.undo_stack:
            return False, "لا توجد عمليات"
        batch = self.undo_stack.pop()
        for path, states in batch["changes"].items():
            before = states.get("before")
            if before and os.path.exists(before):
                os.makedirs(os.path.dirname(path), exist_ok=True)
                shutil.copy2(before, path)
            elif os.path.exists(path):
                os.remove(path)
        self.redo_stack.append(batch)
        return True, batch["name"]

    def redo(self):
        if not self.redo_stack:
            return False, "لا توجد عمليات"
        batch = self.redo_stack.pop()
        for path, states in batch["changes"].items():
            after = states.get("after")
            if after and os.path.exists(after):
                os.makedirs(os.path.dirname(path), exist_ok=True)
                shutil.copy2(after, path)
            elif os.path.exists(path):
                os.remove(path)
        self.undo_stack.append(batch)
        return True, batch["name"]
