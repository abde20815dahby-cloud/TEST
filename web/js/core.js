/**
 * نواة الواجهة — حالة عامة وسجل وحالة الاتصال
 * لتغيير السلوك العام (سجل، انتظار): عدّل هذا الملف فقط
 */
/* global eel */

const statusText = document.getElementById("statusText");
const launchBtnText = document.querySelector("#launchBtn .text");
const projectPathText = document.getElementById("projectPathText");
const projectPathHero = document.getElementById("projectPathHero");
const _logScopes = {};
let _currentLogScope = "dashboard";

function setStatus(message, isError = false) {
    if (statusText) {
        statusText.textContent = message;
        statusText.style.color = isError ? "#f87171" : "#7dd3fc";
    }
}

function appendLog(msg, type = "info") {
    const scope = _currentLogScope || "dashboard";
    if (!_logScopes[scope]) _logScopes[scope] = [];
    _logScopes[scope].push({ msg: String(msg), type: type || "info", ts: new Date().toLocaleTimeString("ar-EG") });

    const logEl = document.getElementById("liveLog");
    if (!logEl) return;
    const now = _logScopes[scope][_logScopes[scope].length - 1].ts;
    const cls = type === "error" ? "log-error" : type === "success" ? "log-ok" : "log-msg";
    const icon = type === "error" ? "❌" : type === "success" ? "✅" : "➤";
    const div = document.createElement("div");
    div.className = "log-line " + cls;
    div.innerHTML = `<span class="log-time">${now}</span> <span class="log-icon">${icon}</span> ${escapeHtml(String(msg))}`;
    logEl.appendChild(div);
    logEl.scrollTop = logEl.scrollHeight;
}

function escapeHtml(s) {
    const div = document.createElement("div");
    div.textContent = s;
    return div.innerHTML;
}

function clearLog() {
    const scope = _currentLogScope || "dashboard";
    _logScopes[scope] = [];
    const logEl = document.getElementById("liveLog");
    if (logEl) logEl.innerHTML = "";
    if (statusText) statusText.textContent = "جاهز.";
}

function setLogScope(scopeKey, label) {
    _currentLogScope = scopeKey || "dashboard";
    const titleEl = document.querySelector(".log-title");
    if (titleEl) titleEl.textContent = `سجل: ${label || "عام"}`;
    renderCurrentScopeLogs();
}

function renderCurrentScopeLogs() {
    const logEl = document.getElementById("liveLog");
    if (!logEl) return;
    const rows = _logScopes[_currentLogScope] || [];
    logEl.innerHTML = "";
    rows.forEach((row) => {
        const cls = row.type === "error" ? "log-error" : row.type === "success" ? "log-ok" : "log-msg";
        const icon = row.type === "error" ? "❌" : row.type === "success" ? "✅" : "➤";
        const div = document.createElement("div");
        div.className = "log-line " + cls;
        div.innerHTML = `<span class="log-time">${row.ts}</span> <span class="log-icon">${icon}</span> ${escapeHtml(row.msg)}`;
        logEl.appendChild(div);
    });
    logEl.scrollTop = logEl.scrollHeight;
}

function isBackendReady() {
    if (typeof eel === "undefined") {
        setStatus("الاتصال مع Python غير جاهز. أعد تشغيل التطبيق.", true);
        return false;
    }
    return true;
}

function showWaitingOverlay() {
    const el = document.getElementById("waitingOverlay");
    if (el) {
        el.classList.add("active");
        el.style.pointerEvents = "auto";
    }
}

function hideWaitingOverlay() {
    const el = document.getElementById("waitingOverlay");
    if (el) {
        el.classList.remove("active");
        el.style.pointerEvents = "none";
    }
}

eel.expose(update_live_log);
function update_live_log(msg, type) {
    appendLog(msg || "", type || "info");
}
