/**
 * تقرير النواقص والختم الجماعي — منطق فقط (المظهر في css/tools/missing.css)
 */
/* global eel */

function backToMissingReport() {
    openToolPage("tool-main");
}

async function loadMissingReport() {
    if (!isBackendReady()) return;
    try {
        const result = await eel.run_support_tool("get_missing_report", {})();
        if (!result.ok) return;
        const listEl = document.getElementById("missingList");
        const singleEl = document.getElementById("singleView");
        singleEl.style.display = "none";
        listEl.innerHTML = "";
        const report = result.report || [];
        if (report.length === 0) {
            listEl.innerHTML = "<p class='no-missing'>لا توجد نواقص.</p>";
            window._missingReport = [];
            return;
        }
        window._missingReport = report;
        listEl.style.display = "block";
        report.forEach((item, idx) => {
            const card = document.createElement("div");
            card.className = "missing-card";
            card.dataset.idx = idx;
            const baseName = item.folder.split(/[/\\\\]/).pop();
            card.innerHTML = `<div class="missing-info"><strong>${baseName}</strong><span class="missing-types">${(item.missing || []).join(", ").toUpperCase()}</span></div><div class="missing-btns"><button class="tool-btn" onclick="showSingleViewFromIdx(${idx})">⚙️ فحص وتعديل</button><button class="tool-btn" onclick="openFolderFromIdx(${idx})">📂 فتح المجلد</button></div>`;
            listEl.appendChild(card);
        });
    } catch (e) {
        setStatus("فشل تحميل التقرير.", true);
    }
}

function showSingleViewFromIdx(idx) {
    const report = window._missingReport || [];
    const item = report[idx];
    if (!item) return;
    const folderPath = item.folder;
    document.getElementById("missingList").style.display = "none";
    const singleEl = document.getElementById("singleView");
    const singleList = document.getElementById("singleMissingList");
    const titleEl = document.getElementById("singleViewTitle");
    singleEl.style.display = "block";
    singleEl.dataset.folderIdx = idx;
    const baseName = folderPath.split(/[/\\\\]/).pop();
    titleEl.textContent = "إصلاح يدوي: " + baseName;
    singleList.innerHTML = "";
    (item.missing || []).forEach((m, mi) => {
        const row = document.createElement("div");
        row.className = "missing-row";
        const btn = document.createElement("button");
        btn.className = "tool-btn primary";
        btn.textContent = "🔍 إدراج المستند المرجعي";
        btn.onclick = () => manualInsertByIdx(idx, mi);
        row.innerHTML = `<span class="missing-type">${m.toUpperCase()}</span>`;
        row.appendChild(btn);
        singleList.appendChild(row);
    });
    const openBtn = document.createElement("button");
    openBtn.className = "tool-btn";
    openBtn.textContent = "📁 فتح المجلد";
    openBtn.onclick = () => openFolderFromIdx(idx);
    singleList.appendChild(openBtn);
    const backBtn = document.createElement("button");
    backBtn.className = "tool-btn";
    backBtn.textContent = "🔙 رجوع للتقرير";
    backBtn.onclick = () => {
        document.getElementById("singleView").style.display = "none";
        document.getElementById("missingList").style.display = "block";
    };
    singleList.appendChild(backBtn);
}

function openFolderFromIdx(idx) {
    const item = (window._missingReport || [])[idx];
    if (!item || !isBackendReady()) return;
    eel.open_folder(item.folder)();
}

async function copyMissingNumbers() {
    if (!isBackendReady()) return;
    try {
        const result = await eel.run_support_tool("copy_missing_numbers", {})();
        setStatus(`[${result.timestamp}] ${result.message}`, !result.ok);
        if (result.ok && result.text) {
            navigator.clipboard.writeText(result.text);
        }
    } catch (e) {
        setStatus("فشل نسخ الأرقام.", true);
    }
}

async function pickRecoveryFolder() {
    if (!isBackendReady()) return;
    if (window.__folderDialogBusy) return;
    window.__folderDialogBusy = true;
    showWaitingOverlay();
    try {
        const r = await _callWithTimeout(() => eel.select_folder_for("recovery")());
        if (!r.ok) return;
        const result = await eel.run_support_tool("auto_distribute", { folder: r.path })();
        setStatus(`[${result.timestamp}] ${result.message}`, !result.ok);
        if (result.ok) loadMissingReport();
    } catch (e) {
        setStatus("فشل الاسترداد.", true);
    } finally {
        hideWaitingOverlay();
        window.__folderDialogBusy = false;
    }
}

async function batchStampZn2() {
    if (!isBackendReady()) return;
    const opts = getStampParamsForBackend();
    try {
        const result = await eel.run_support_tool("batch_stamp_zn2", opts)();
        setStatus(`[${result.timestamp}] ${result.message}`, !result.ok);
        if (result.ok) loadMissingReport();
    } catch (e) {
        setStatus("فشل الختم الجماعي.", true);
    }
}

async function manualInsertByIdx(folderIdx, missingIdx) {
    const item = (window._missingReport || [])[folderIdx];
    if (!item || !isBackendReady()) return;
    const missingFileName = (item.missing || [])[missingIdx];
    if (!missingFileName) return;
    showWaitingOverlay();
    try {
        const r = await eel.select_source_file("اختر المستند المرجعي لـ " + missingFileName)();
        if (!r.ok || !r.path) return;
        const result = await eel.run_support_tool("manual_insert", {
            target_folder: item.folder,
            source_file: r.path,
            missing_file_name: missingFileName,
        })();
        setStatus(`[${result.timestamp}] ${result.message}`, !result.ok);
        if (result.ok) {
            const res = await eel.run_support_tool("get_missing_report", {})();
            window._missingReport = res.report || [];
            if (window._missingReport.length === 0) {
                openToolPage("tool-main");
            } else {
                loadMissingReport();
                const newIdx = window._missingReport.findIndex((x) => x.folder === item.folder);
                if (newIdx >= 0) showSingleViewFromIdx(newIdx);
                else loadMissingReport();
            }
        }
    } catch (e) {
        setStatus("فشل الإدراج.", true);
    } finally {
        hideWaitingOverlay();
    }
}
