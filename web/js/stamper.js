/**
 * وحدة الختم والمعاينة — منطق فقط (المظهر: css/tools/stamper.css + stamp-modal.css)
 */
/* global eel */

let _stampPreviewPdfPath = null;
let _stampRect = { x: 20, y: 20, w: 150, h: 80 };
let _stampPdfDims = { w: 595, h: 842 };
let _stampFolderPdfs = [];
let _missingReportStampFlow = false;

async function loadStamperPdfList() {
    const pathEl = document.getElementById("stamperPath");
    const path = pathEl ? pathEl.textContent : "";
    const block = document.getElementById("stamperPreviewBlock");
    const noFolder = document.getElementById("stamperNoFolder");
    if (!path || path === "غير محدد") {
        if (block) block.style.display = "none";
        if (noFolder) noFolder.style.display = "block";
        return;
    }
    if (noFolder) noFolder.style.display = "none";
    if (block) block.style.display = "block";
    const res = await eel.get_stamp_folder_pdfs()();
    const sel = document.getElementById("stampPdfSelect");
    sel.innerHTML = '<option value="">-- اختر ملف PDF --</option>';
    _stampFolderPdfs = res.pdfs || [];
    _stampFolderPdfs.forEach((p, i) => {
        const opt = document.createElement("option");
        opt.value = i;
        opt.textContent = p.name;
        sel.appendChild(opt);
    });
    if (_stampFolderPdfs.length > 0) {
        sel.value = "0";
        appendLog(`تم العثور على ${_stampFolderPdfs.length} ملف PDF (من المجلد والمجلدات الفرعية).`, "success");
    }
}

function updateStampModalUi() {
    const flow = _missingReportStampFlow;
    const title = document.getElementById("stampModalTitle");
    const sub = document.getElementById("stampModalSubtitle");
    const run = document.getElementById("stamp-btn-stamper-run");
    const miss = document.getElementById("stamp-btn-missing-batch");
    const applyOnly = document.getElementById("stamp-btn-apply-only");
    if (title) title.textContent = flow ? "معاينة الختم — تقرير النواقص" : "معاينة واختيار موضع الختم";
    if (sub) {
        sub.textContent = flow
            ? "ضبّط موضع وحجم الختم، ثم اضغط «تنفيذ الختم الجماعي» — لا يُطبَّق الختم على الملفات قبل ذلك."
            : "الصفحة كاملة مصغّرة — اسحب صورة الختم للموضع، ثم ضبط العرض والارتفاع أدناه";
    }
    if (run) run.style.display = flow ? "none" : "";
    if (miss) miss.style.display = flow ? "" : "none";
    if (applyOnly) applyOnly.style.display = flow ? "none" : "";
}

function resetStampModalUi() {
    _missingReportStampFlow = false;
    updateStampModalUi();
}

async function applyMissingBatchStampFromModal() {
    if (!isBackendReady()) return;
    _stampRect.w = parseInt(document.getElementById("stampPreviewW").value, 10) || 150;
    _stampRect.h = parseInt(document.getElementById("stampPreviewH").value, 10) || 80;
    document.getElementById("stampX").value = _stampRect.x;
    document.getElementById("stampY").value = _stampRect.y;
    document.getElementById("stampW").value = _stampRect.w;
    document.getElementById("stampH").value = _stampRect.h;
    document.getElementById("stampPreviewModal").classList.remove("active");
    resetStampModalUi();
    await batchStampZn2();
}

async function openStampPreviewFromFolder(fromMissing = false) {
    _missingReportStampFlow = !!fromMissing;
    if (!_stampFolderPdfs.length) {
        _missingReportStampFlow = false;
        updateStampModalUi();
        appendLog("لا توجد ملفات PDF في المجلد.", "error");
        return;
    }
    const sel = document.getElementById("stampPdfSelect");
    let startIdx = sel ? parseInt(sel.value, 10) : 0;
    if (isNaN(startIdx) || startIdx < 0) startIdx = 0;
    const order = [];
    for (let i = 0; i < _stampFolderPdfs.length; i++) {
        const j = (startIdx + i) % _stampFolderPdfs.length;
        order.push(j);
    }
    let res = null;
    let usedIdx = -1;
    for (const j of order) {
        const path = _stampFolderPdfs[j].path;
        const tryRes = await eel.get_pdf_preview(path, 0)();
        if (tryRes.ok) {
            res = tryRes;
            usedIdx = j;
            break;
        }
    }
    if (!res || !res.ok) {
        _missingReportStampFlow = false;
        updateStampModalUi();
        appendLog("فشل تحميل المعاينة: لا يوجد PDF صالح (فارغ، تالف، أو بدون صفحات).", "error");
        setStatus("تأكد من وجود PDF صالح داخل المجلد أو المجلدات الفرعية.", true);
        return;
    }
    if (sel && usedIdx >= 0) sel.value = String(usedIdx);
    _stampPreviewPdfPath = _stampFolderPdfs[usedIdx].path;
    if (res.path_used) _stampPreviewPdfPath = res.path_used;
    try {
        if (!res.ok) throw new Error(res.message);
        _stampPdfDims = { w: res.pdf_w, h: res.pdf_h };
        _stampRect.x = parseInt(document.getElementById("stampX").value, 10) || 20;
        _stampRect.y = parseInt(document.getElementById("stampY").value, 10) || 20;
        _stampRect.w = parseInt(document.getElementById("stampW").value, 10) || 150;
        _stampRect.h = parseInt(document.getElementById("stampH").value, 10) || 80;
        document.getElementById("stampPreviewW").value = _stampRect.w;
        document.getElementById("stampPreviewH").value = _stampRect.h;
        (function () {
            const wr = document.getElementById("stampPreviewWRange");
            const hr = document.getElementById("stampPreviewHRange");
            if (wr) wr.value = Math.min(parseInt(wr.max, 10), Math.max(parseInt(wr.min, 10), _stampRect.w));
            if (hr) hr.value = Math.min(parseInt(hr.max, 10), Math.max(parseInt(hr.min, 10), _stampRect.h));
        })();
        const img = document.getElementById("stampPreviewImg");
        img.src = "data:image/png;base64," + res.b64;
        img.onload = () => {
            loadStampOverlayImage();
            updateStampOverlayFromRect();
            document.getElementById("stampPreviewModal").classList.add("active");
            wireStampSizeControls();
            initStampDragPositionOnly(res.pdf_w, res.pdf_h);
            updateStampModalUi();
        };
        if (img.complete) img.onload();
    } catch (e) {
        _missingReportStampFlow = false;
        updateStampModalUi();
        appendLog("فشل تحميل المعاينة: " + e, "error");
    }
}

async function openStampPreviewFromMissing() {
    if (!isBackendReady()) return;
    if (!_ensureProjectPath()) return;
    showWaitingOverlay();
    try {
        const res = await eel.get_missing_zn_pdfs()();
        if (!res.ok || !res.pdfs || !res.pdfs.length) {
            appendLog("لا يوجد ملف ZN للمعاينة — يجب أن يظهر zn2.pdf ضمن النواقص وأن يوجد PDF يحتوي على ZN في المجلد.", "error");
            setStatus("لا توجد معاينة: أضف ملف ZN أو استخدم وحدة المصادقة ZN لضبط الختم.", true);
            return;
        }
        _stampFolderPdfs = res.pdfs;
        const sel = document.getElementById("stampPdfSelect");
        if (sel) {
            sel.innerHTML = '<option value="">-- اختر ملف PDF --</option>';
            _stampFolderPdfs.forEach((p, i) => {
                const opt = document.createElement("option");
                opt.value = i;
                opt.textContent = p.name;
                sel.appendChild(opt);
            });
            sel.value = "0";
        }
        appendLog(`معاينة من تقرير النواقص: ${_stampFolderPdfs.length} ملف ZN.`, "success");
        await openStampPreviewFromFolder(true);
    } catch (e) {
        appendLog("فشل تحميل قائمة المعاينة: " + e, "error");
    } finally {
        hideWaitingOverlay();
    }
}

function loadStampOverlayImage() {
    const o = document.getElementById("stampOverlayImg");
    if (!o) return;
    o.onerror = function () {
        if (this.src.indexOf("stamp.jpg") >= 0) {
            this.style.display = "none";
            return;
        }
        this.src = "stamp.jpg";
    };
    o.style.display = "";
    o.src = "stamp.png";
}

function wireStampSizeControls() {
    const wIn = document.getElementById("stampPreviewW");
    const hIn = document.getElementById("stampPreviewH");
    const wRg = document.getElementById("stampPreviewWRange");
    const hRg = document.getElementById("stampPreviewHRange");
    const sync = () => {
        _stampRect.w = parseInt(wIn.value, 10) || 150;
        _stampRect.h = parseInt(hIn.value, 10) || 80;
        if (wRg) wRg.value = Math.min(parseInt(wRg.max, 10), Math.max(parseInt(wRg.min, 10), _stampRect.w));
        if (hRg) hRg.value = Math.min(parseInt(hRg.max, 10), Math.max(parseInt(hRg.min, 10), _stampRect.h));
        updateStampOverlayFromRect();
    };
    wIn.oninput = hIn.oninput = sync;
    wRg.oninput = () => {
        wIn.value = wRg.value;
        sync();
    };
    hRg.oninput = () => {
        hIn.value = hRg.value;
        sync();
    };
    sync();
}

function updateStampOverlayFromRect() {
    const overlay = document.getElementById("stampOverlay");
    if (!overlay || !_stampPdfDims.w) return;
    const pw = _stampPdfDims.w;
    const ph = _stampPdfDims.h;
    overlay.style.left = ((_stampRect.x / pw) * 100).toFixed(3) + "%";
    overlay.style.top = ((_stampRect.y / ph) * 100).toFixed(3) + "%";
    overlay.style.width = ((_stampRect.w / pw) * 100).toFixed(3) + "%";
    overlay.style.height = ((_stampRect.h / ph) * 100).toFixed(3) + "%";
}

function initStampDragPositionOnly(pdfW, pdfH) {
    const overlay = document.getElementById("stampOverlay");
    const imgEl = document.getElementById("stampPreviewImg");
    let isDown = false;
    let startX;
    let startY;
    let startLeft;
    let startTop;
    overlay.onmousedown = (e) => {
        e.preventDefault();
        isDown = true;
        const rect = overlay.getBoundingClientRect();
        const ir = imgEl.getBoundingClientRect();
        startX = e.clientX;
        startY = e.clientY;
        startLeft = ((rect.left - ir.left) / ir.width) * 100;
        startTop = ((rect.top - ir.top) / ir.height) * 100;
    };
    document.onmousemove = (e) => {
        if (!isDown) return;
        const ir = imgEl.getBoundingClientRect();
        const dx = ((e.clientX - startX) / ir.width) * 100;
        const dy = ((e.clientY - startY) / ir.height) * 100;
        const w = parseFloat(overlay.style.width) || (_stampRect.w / pdfW) * 100;
        const h = parseFloat(overlay.style.height) || (_stampRect.h / pdfH) * 100;
        const newLeft = Math.max(0, Math.min(100 - w, startLeft + dx));
        const newTop = Math.max(0, Math.min(100 - h, startTop + dy));
        overlay.style.left = newLeft + "%";
        overlay.style.top = newTop + "%";
        _stampRect.x = Math.round((newLeft / 100) * _stampPdfDims.w);
        _stampRect.y = Math.round((newTop / 100) * _stampPdfDims.h);
        syncStampToMainForm();
    };
    document.onmouseup = () => {
        if (isDown) {
            updateStampCoordsFromOverlay();
            syncStampToMainForm();
        }
        isDown = false;
        document.onmousemove = null;
        document.onmouseup = null;
    };
}

function syncStampToMainForm() {
    const sx = document.getElementById("stampX");
    const sy = document.getElementById("stampY");
    if (sx) sx.value = _stampRect.x;
    if (sy) sy.value = _stampRect.y;
}

function updateStampCoordsFromOverlay() {
    const overlay = document.getElementById("stampOverlay");
    const img = document.getElementById("stampPreviewImg");
    if (!overlay || !img || !_stampPdfDims.w) return;
    const ir = img.getBoundingClientRect();
    const ol = overlay.getBoundingClientRect();
    const relLeft = ol.left - ir.left;
    const relTop = ol.top - ir.top;
    _stampRect.x = Math.max(0, Math.round((relLeft / ir.width) * _stampPdfDims.w));
    _stampRect.y = Math.max(0, Math.round((relTop / ir.height) * _stampPdfDims.h));
    _stampRect.w = parseInt(document.getElementById("stampPreviewW").value, 10) || 150;
    _stampRect.h = parseInt(document.getElementById("stampPreviewH").value, 10) || 80;
}

function closeStampPreview() {
    document.getElementById("stampPreviewModal").classList.remove("active");
    resetStampModalUi();
}

function applyStampPositionOnly() {
    _stampRect.w = parseInt(document.getElementById("stampPreviewW").value, 10) || 150;
    _stampRect.h = parseInt(document.getElementById("stampPreviewH").value, 10) || 80;
    document.getElementById("stampX").value = _stampRect.x;
    document.getElementById("stampY").value = _stampRect.y;
    document.getElementById("stampW").value = _stampRect.w;
    document.getElementById("stampH").value = _stampRect.h;
    closeStampPreview();
    setStatus("تم تطبيق الموضع. اضغط مصادقة على الكل لتنفيذ الختم.");
}

function applyStampAndRunAll() {
    _stampRect.w = parseInt(document.getElementById("stampPreviewW").value, 10) || 150;
    _stampRect.h = parseInt(document.getElementById("stampPreviewH").value, 10) || 80;
    document.getElementById("stampX").value = _stampRect.x;
    document.getElementById("stampY").value = _stampRect.y;
    document.getElementById("stampW").value = _stampRect.w;
    document.getElementById("stampH").value = _stampRect.h;
    closeStampPreview();
    runAdvanced("stamper");
}
