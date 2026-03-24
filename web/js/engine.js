/**
 * منطق الاتصال بالمحرك — مجلدات، أدوات أساسية، أدوات متقدمة
 */
/* global eel */
window.__folderDialogBusy = false;

function _callWithTimeout(promiseFactory, timeoutMs = 180000) {
    return Promise.race([
        promiseFactory(),
        new Promise((_, reject) => {
            setTimeout(() => reject(new Error("TIMEOUT_DIALOG")), timeoutMs);
        }),
    ]);
}

function _hasValueLabel(id, emptyText = "غير محدد") {
    const el = document.getElementById(id);
    if (!el) return false;
    const v = (el.textContent || "").trim();
    return v && v !== emptyText;
}

function _ensureProjectPath(showError = true) {
    const p = (projectPathText && projectPathText.textContent ? projectPathText.textContent : "").trim();
    const ok = p && p !== "لا يوجد مسار محدد حاليا";
    if (!ok && showError) setStatus("حدد مجلد المشروع أولاً ثم شغّل الأداة.", true);
    return ok;
}

function refreshRunButtonsState() {
    const projectOk = _ensureProjectPath(false);
    const setDisabled = (selector, flag) => {
        document.querySelectorAll(selector).forEach((btn) => {
            btn.disabled = !!flag;
            btn.classList.toggle("is-locked", !!flag);
        });
    };
    setDisabled('button[onclick*="runCoreTool("]', !projectOk);
    setDisabled('button[onclick*="runZipExportMain("]', !projectOk);
    setDisabled("button[onclick*=\"runAdvanced('stamper')\"]", !_hasValueLabel("stamperPath"));
    setDisabled("button[onclick*=\"runAdvanced('pv')\"]", !_hasValueLabel("pvPath"));
    setDisabled("button[onclick*=\"runAdvanced('kgo')\"]", !_hasValueLabel("kgoPath"));
    setDisabled("button[onclick*=\"runAdvanced('converter')\"]", !_hasValueLabel("convPath"));
    setDisabled("button[onclick*=\"runAdvanced('splitter')\"]", !_hasValueLabel("splitPath"));
}

async function startTask(task) {
    if (!isBackendReady()) return;
    const originalText = launchBtnText.innerText;
    launchBtnText.innerText = "جاري الاتصال...";
    setStatus("جاري تهيئة النظام الذكي...");
    try {
        const response = await eel.start_processing(task)();
        launchBtnText.innerText = "تم التفعيل!";
        launchBtnText.style.color = "#34d399";
        setStatus(response, false);
    } catch (error) {
        setStatus("تعذر الاتصال بالمحرك الخلفي.", true);
    } finally {
        setTimeout(() => {
            launchBtnText.innerText = originalText;
            launchBtnText.style.color = "#FFFFFF";
        }, 1800);
    }
}

async function pickProjectFolder() {
    if (!isBackendReady()) return;
    if (window.__folderDialogBusy) return;
    window.__folderDialogBusy = true;
    showWaitingOverlay();
    try {
        const response = await _callWithTimeout(() => eel.select_project_folder()());
        if (response.ok) {
            projectPathText.textContent = response.path;
            projectPathHero.textContent = response.path;
            document.getElementById("mainZipPath").textContent = response.path;
            setStatus("تم اعتماد مسار المشروع. يمكنك تشغيل الأدوات الآن.");
            refreshRunButtonsState();
        } else {
            setStatus("لم يتم اختيار أي مسار.", true);
        }
    } catch (error) {
        if (String(error).includes("TIMEOUT_DIALOG")) {
            setStatus("نافذة اختيار المجلد لم تستجب. أغلق أي نافذة اختيار مفتوحة ثم أعد المحاولة.", true);
        } else {
            setStatus("تعذر فتح نافذة اختيار المجلد.", true);
        }
    } finally {
        hideWaitingOverlay();
        window.__folderDialogBusy = false;
    }
}

async function runCoreTool(toolKey) {
    if (!isBackendReady()) return;
    if (!_ensureProjectPath()) return;
    try {
        appendLog("بدء أداة التدقيق: " + toolKey, "info");
        setStatus("جاري تنفيذ...");
        const result = await eel.run_engineering_tool(toolKey)();
        setStatus(`[${result.timestamp}] ${result.message}`, !result.ok);
        appendLog(`[${result.timestamp}] ${result.message}`, result.ok ? "success" : "error");
        if (result.has_missing) {
            openToolPage("tool-missing");
            loadMissingReport();
        }
    } catch (error) {
        setStatus("حدث خطأ أو تجمد أثناء التشغيل.", true);
        appendLog("❌ خطأ: " + error, "error");
    }
}

async function pickToolFolder(toolKey, labelId) {
    if (!isBackendReady()) return;
    if (window.__folderDialogBusy) return;
    window.__folderDialogBusy = true;
    showWaitingOverlay();
    try {
        const response = await _callWithTimeout(() => eel.select_folder_for(toolKey)());
        if (response.ok) {
            document.getElementById(labelId).textContent = response.path;
            setStatus("تم اعتماد المسار بنجاح.");
            refreshRunButtonsState();
            if (toolKey === "stamper") {
                loadStamperPdfList();
            }
        } else {
            setStatus("لم يتم اختيار أي مسار.", true);
        }
    } catch (error) {
        if (String(error).includes("TIMEOUT_DIALOG")) {
            setStatus("نافذة اختيار المجلد استغرقت وقتاً طويلاً. حاول مرة أخرى.", true);
        } else {
            setStatus("خطأ في اختيار المجلد.", true);
        }
    } finally {
        hideWaitingOverlay();
        window.__folderDialogBusy = false;
    }
}

async function pickSplitPdf(targetId = "splitPath") {
    if (!isBackendReady()) return;
    if (window.__folderDialogBusy) return;
    window.__folderDialogBusy = true;
    showWaitingOverlay();
    try {
        const response = await _callWithTimeout(() => eel.select_split_pdf()());
        if (response.ok) {
            document.getElementById(targetId).textContent = response.path;
            setStatus("تم اعتماد ملف PDF للتقطيع.");
            refreshRunButtonsState();
        } else {
            setStatus("لم يتم اختيار ملف.", true);
        }
    } catch (error) {
        if (String(error).includes("TIMEOUT_DIALOG")) {
            setStatus("نافذة اختيار الملف لم تستجب. أعد المحاولة.", true);
        } else {
            setStatus("خطأ في اختيار ملف PDF.", true);
        }
    } finally {
        hideWaitingOverlay();
        window.__folderDialogBusy = false;
    }
}

async function pickAcmeExe(targetId = "acmePath") {
    if (!isBackendReady()) return;
    if (window.__folderDialogBusy) return;
    window.__folderDialogBusy = true;
    showWaitingOverlay();
    try {
        const response = await _callWithTimeout(() => eel.select_acme_exe()());
        if (response.ok) {
            document.getElementById(targetId).textContent = response.path;
            setStatus("تم اعتماد مسار Acme CAD.");
        } else {
            setStatus("لم يتم اختيار ملف Acme.", true);
        }
    } catch (error) {
        if (String(error).includes("TIMEOUT_DIALOG")) {
            setStatus("نافذة اختيار ملف Acme لم تستجب. أعد المحاولة.", true);
        } else {
            setStatus("خطأ في اختيار Acme CAD.", true);
        }
    } finally {
        hideWaitingOverlay();
        window.__folderDialogBusy = false;
    }
}

function getStampParamsForBackend() {
    const gx = (id, d) => {
        const el = document.getElementById(id);
        const v = el ? parseFloat(el.value) : NaN;
        return Number.isFinite(v) ? v : d;
    };
    return {
        x: gx("stampX", 20),
        y: gx("stampY", 20),
        w: gx("stampW", 150),
        h: gx("stampH", 80),
    };
}

async function runAdvanced(toolKey, paperSizeId = "paperSize", splitLayoutId = "splitLayout") {
    if (!isBackendReady()) return;
    if (toolKey === "stamper" && !_hasValueLabel("stamperPath")) {
        setStatus("حدد مجلد الوثائق أولاً لوحدة الختم.", true);
        return;
    }
    if (toolKey === "pv" && !_hasValueLabel("pvPath")) {
        setStatus("حدد مستودع PV أولاً.", true);
        return;
    }
    if (toolKey === "kgo" && !_hasValueLabel("kgoPath")) {
        setStatus("حدد مجلد الملفات الخام لـ KGO أولاً.", true);
        return;
    }
    if (toolKey === "converter" && !_hasValueLabel("convPath")) {
        setStatus("حدد مجلد التحويل أولاً.", true);
        return;
    }
    if (toolKey === "splitter" && !_hasValueLabel("splitPath")) {
        setStatus("حدد ملف PDF أولاً للمقص.", true);
        return;
    }
    const options = {};
    if (toolKey === "stamper") {
        const sel = document.getElementById("stampFilterMode");
        options.filter_mode = sel && sel.value === "all_pdf" ? "all_pdf" : "zn_only";
        const sp = getStampParamsForBackend();
        options.x = sp.x;
        options.y = sp.y;
        options.w = sp.w;
        options.h = sp.h;
    } else if (toolKey === "converter") {
        options.do_word = true;
        options.do_excel = true;
        options.paper_size = document.getElementById(paperSizeId).value;
    } else if (toolKey === "pv") {
        options.do_convert = true;
        options.do_merge = true;
        options.do_sort = true;
    } else if (toolKey === "kgo") {
        options.source_folder = (document.getElementById("kgoPath")?.textContent || "").trim();
        options.exe_path = (document.getElementById("kgoExe")?.value || "").trim();
    } else if (toolKey === "splitter") {
        options.layout = document.getElementById(splitLayoutId).value;
    }

    try {
        appendLog("بدء: " + toolKey, "info");
        setStatus("جاري التنفيذ...");
        const result = await eel.run_advanced_tool(toolKey, options)();
        setStatus(`[${result.timestamp}] ${result.message}`, !result.ok);
        appendLog(`[${result.timestamp}] ${result.message}`, result.ok ? "success" : "error");
    } catch (error) {
        setStatus("خطأ أو تجمد أثناء التنفيذ.", true);
        appendLog("❌ " + error, "error");
    }
}

async function runSupport(toolKey) {
    if (!isBackendReady()) return;
    try {
        const result = await eel.run_support_tool(toolKey, {})();
        setStatus(`[${result.timestamp}] ${result.message}`, !result.ok);
    } catch (error) {
        setStatus("حدث خطأ أثناء تشغيل أداة الدعم.", true);
    }
}

async function runZipExport() {
    if (!isBackendReady()) return;
    const folder = document.getElementById("zipPath").textContent;
    if (!folder || folder === "غير محدد") {
        setStatus("حدد مجلد التصدير ZIP أولا.", true);
        return;
    }
    try {
        const result = await eel.run_support_tool("zip_export", { folder })();
        setStatus(`[${result.timestamp}] ${result.message}`, !result.ok);
    } catch (error) {
        setStatus("حدث خطأ أثناء تصدير ZIP.", true);
    }
}

async function runZipExportMain() {
    let folder = document.getElementById("mainZipPath").textContent;
    if (!folder || folder === "غير محدد") {
        folder = projectPathText.textContent;
    }
    if (!folder || folder === "لا يوجد مسار محدد حاليا") {
        setStatus("حدد مجلد المشروع أو مجلد التصدير ZIP أولا.", true);
        return;
    }
    if (!isBackendReady()) return;
    try {
        const result = await eel.run_support_tool("zip_export", { folder })();
        setStatus(`[${result.timestamp}] ${result.message}`, !result.ok);
    } catch (error) {
        setStatus("حدث خطأ أثناء تصدير ZIP.", true);
    }
}
