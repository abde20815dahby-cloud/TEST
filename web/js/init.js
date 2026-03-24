/**
 * تهيئة نهائية: أخطاء عامة، Tilt، مستمعات النوافذ
 */
window.addEventListener("error", () => {
    setStatus("حدث خطأ JavaScript داخلي في الواجهة.", true);
});

document.addEventListener("DOMContentLoaded", () => {
    if (typeof VanillaTilt !== "undefined") {
        VanillaTilt.init(document.querySelectorAll(".card-3d"), {
            max: 15,
            speed: 400,
            glare: true,
            "max-glare": 0.4,
        });
    }
    const seq = document.getElementById("sequentialModal");
    if (seq) {
        seq.addEventListener("click", (e) => {
            if (e.target.id === "sequentialModal") closeSequentialModal();
        });
    }
    const stampM = document.getElementById("stampPreviewModal");
    if (stampM) {
        stampM.addEventListener("click", (e) => {
            if (e.target.id === "stampPreviewModal") closeStampPreview();
        });
    }
    setLogScope("dashboard", "لوحة القيادة");
    injectToolIntros();
    beautifyButtons();
    mountLogoFx();
    if (typeof refreshRunButtonsState === "function") refreshRunButtonsState();
});

function injectToolIntros() {
    const data = [
        { id: "tool-main", icon: "fa-broom-ball", text: "تنظيف المشروع وفحص النواقص والتدقيق الشامل." },
        { id: "tool-missing", icon: "fa-triangle-exclamation", text: "عرض الملفات الناقصة وإصلاحها يدوياً أو بالختم الجماعي." },
        { id: "tool-stamper", icon: "fa-stamp", text: "معاينة PDF، سحب الختم، وتطبيق المصادقة بدقة." },
        { id: "tool-pv", icon: "fa-file-signature", text: "تحويل وفرز وتجميع محاضر PV تلقائياً." },
        { id: "tool-kgo", icon: "fa-satellite-dish", text: "تشغيل ToRinex4 وتحويل ملفات GNSS إلى RINEX 3.02." },
        { id: "tool-converter", icon: "fa-file-arrow-down", text: "تحويل ملفات Office إلى PDF بالحجم المحدد." },
        { id: "tool-splitter", icon: "fa-scissors", text: "تقطيع الخرائط إلى شبكات جاهزة للطباعة." },
        { id: "tool-dxf", icon: "fa-compass-drafting", text: "إطلاق Acme CAD وعمليات DXF والتصدير." },
    ];
    data.forEach((t) => {
        const sec = document.getElementById(t.id);
        if (!sec || sec.querySelector(".tool-intro")) return;
        const card = sec.querySelector(".workspace-card");
        if (!card) return;
        const intro = document.createElement("div");
        intro.className = "tool-intro";
        intro.innerHTML = `<i class="fa-solid ${t.icon}"></i><span>${t.text}</span>`;
        card.insertBefore(intro, card.firstChild);
    });
}

function beautifyButtons() {
    const map = [
        ["عزل وتطهير الملفات", "fa-broom-ball"],
        ["فحص النواقص", "fa-magnifying-glass-chart"],
        ["تدقيق شامل", "fa-shield-heart"],
        ["استرداد من المخزن", "fa-box-open"],
        ["ختم جماعي", "fa-stamp"],
        ["نسخ أرقام الملفات الناقصة", "fa-copy"],
        ["تحديد مجلد المشروع", "fa-folder-tree"],
        ["تحديد مجلد الوثائق", "fa-folder-open"],
        ["تحديد مستودع PV", "fa-database"],
        ["تحديد مجلد التحويل", "fa-folder-plus"],
        ["تحديد ملف PDF", "fa-file-pdf"],
        ["تشغيل PV Processor", "fa-rocket"],
        ["تشغيل KGO ToRinex", "fa-satellite-dish"],
        ["تحديد مجلد KGO", "fa-folder-tree"],
        ["تشغيل Converter", "fa-repeat"],
        ["تشغيل Splitter", "fa-scissors"],
        ["فتح Acme CAD", "fa-compass-drafting"],
        ["تصدير الحزم ZIP", "fa-file-zipper"],
        ["النسخ الاحتياطية", "fa-hard-drive"],
        ["تراجع", "fa-rotate-left"],
        ["إعادة", "fa-rotate-right"],
    ];
    document.querySelectorAll("button.tool-btn,button.path-btn").forEach((btn) => {
        const txt = (btn.textContent || "").trim();
        for (const [needle, icon] of map) {
            if (txt.includes(needle) && !btn.querySelector("i.fa-solid")) {
                btn.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${txt}</span>`;
                btn.classList.add("btn-iconic");
                break;
            }
        }
    });
}

function mountLogoFx() {
    const logo = document.querySelector(".logo");
    if (!logo) return;
    const fx = document.createElement("div");
    fx.id = "logoFx";
    fx.className = "logo-fx";
    fx.innerHTML = `
      <div class="logo-fx-card">
        <div class="logo-fx-rings">
          <span></span><span></span><span></span>
        </div>
        <div class="logo-fx-img-wrap">
          <img src="logo.png" alt="logo">
        </div>
        <div class="logo-fx-title">ANCFCC PRO</div>
        <div class="logo-fx-sub">EDIT By DAHBY</div>
      </div>
    `;
    document.body.appendChild(fx);
    logo.addEventListener("click", () => {
        fx.classList.add("active");
        setTimeout(() => fx.classList.remove("active"), 2200);
    });
}

function futureToolNotice(name) {
    setStatus(`أداة ${name} ستتوفر قريباً. الواجهة جاهزة لها من الشريط العلوي.`);
    appendLog(`FUTURE TOOL: ${name} — placeholder ready`, "info");
}
