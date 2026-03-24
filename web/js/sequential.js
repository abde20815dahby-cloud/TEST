/**
 * التشغيل التسلسلي للأدوات
 */
const SEQUENTIAL_TOOLS = [
    { id: "cleaning", label: "عزل وتطهير الملفات", run: () => runCoreTool("cleaning") },
    { id: "missing_check", label: "فحص النواقص", run: () => runCoreTool("missing_check") },
    { id: "auto_validation", label: "تدقيق شامل", run: () => runCoreTool("auto_validation") },
    { id: "stamper", label: "ختم ZN", run: () => runAdvanced("stamper") },
    { id: "pv", label: "المعالج PV", run: () => runAdvanced("pv") },
    { id: "converter", label: "المحول", run: () => runAdvanced("converter") },
    { id: "splitter", label: "مقص PDF", run: () => runAdvanced("splitter") },
    { id: "dxf", label: "فتح Acme CAD", run: () => runAdvanced("dxf") },
    { id: "zip", label: "تصدير ZIP", run: () => runZipExportMain() },
];

let _sequentialOrder = [];

function openSequentialModal() {
    _sequentialOrder = [];
    const modal = document.getElementById("sequentialModal");
    const avail = document.getElementById("sequentialAvailable");
    const ordered = document.getElementById("sequentialOrdered");
    avail.innerHTML = "";
    ordered.innerHTML = "";
    SEQUENTIAL_TOOLS.forEach((t, i) => {
        const btn = document.createElement("button");
        btn.className = "sequential-opt-btn";
        btn.textContent = t.label;
        btn.dataset.idx = i;
        btn.onclick = () => addToSequentialOrder(i);
        avail.appendChild(btn);
    });
    modal.classList.add("active");
}

function addToSequentialOrder(idx) {
    _sequentialOrder.push(idx);
    renderSequentialOrdered();
}

function removeFromSequentialOrder(pos) {
    _sequentialOrder.splice(pos, 1);
    renderSequentialOrdered();
}

function clearSequentialOrder() {
    _sequentialOrder = [];
    renderSequentialOrdered();
}

function renderSequentialOrdered() {
    const ordered = document.getElementById("sequentialOrdered");
    ordered.innerHTML = "";
    _sequentialOrder.forEach((idx, pos) => {
        const t = SEQUENTIAL_TOOLS[idx];
        const div = document.createElement("div");
        div.className = "ordered-item";
        div.innerHTML = `<span class="order-num">${pos + 1}</span> ${t.label} <button class="remove-btn" onclick="removeFromSequentialOrder(${pos})">✕</button>`;
        ordered.appendChild(div);
    });
}

function closeSequentialModal() {
    document.getElementById("sequentialModal").classList.remove("active");
}

async function runSequentialTools() {
    if (!_sequentialOrder.length) {
        appendLog("لم تختر أي أداة. اضغط على الأدوات لترتيبها.", "error");
        return;
    }
    closeSequentialModal();
    for (let i = 0; i < _sequentialOrder.length; i++) {
        const idx = _sequentialOrder[i];
        const t = SEQUENTIAL_TOOLS[idx];
        appendLog(`── تشغيل ${i + 1}/${_sequentialOrder.length}: ${t.label} ──`, "info");
        try {
            await t.run();
        } catch (e) {
            appendLog("توقف بسبب خطأ: " + e, "error");
            break;
        }
    }
    appendLog("انتهى التشغيل التسلسلي.", "success");
}
