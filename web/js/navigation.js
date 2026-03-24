/**
 * التنقل بين لوحة القيادة وصفحات الأدوات
 */
function openToolPage(pageId) {
    const hero = document.getElementById("dashboardHome");
    const home = document.getElementById("homeSection");
    if (hero) hero.style.display = "none";
    if (home) home.style.display = "none";
    document.querySelectorAll(".tool-page").forEach((page) => page.classList.remove("active"));
    const page = document.getElementById(pageId);
    if (page) page.classList.add("active");
    const labels = {
        "tool-main": "نظام التدقيق",
        "tool-missing": "تقرير النواقص",
        "tool-stamper": "وحدة الختم ZN",
        "tool-pv": "المعالج PV",
        "tool-kgo": "أداة KGO ToRinex",
        "tool-converter": "المحول",
        "tool-splitter": "مقص الخرائط",
        "tool-dxf": "DXF / Acme",
    };
    setLogScope(pageId, labels[pageId] || "أداة");
    if (pageId === "tool-stamper" && typeof loadStamperPdfList === "function") {
        loadStamperPdfList();
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function backToHome() {
    document.querySelectorAll(".tool-page").forEach((p) => p.classList.remove("active"));
    const hero = document.getElementById("dashboardHome");
    const home = document.getElementById("homeSection");
    if (hero) hero.style.display = "flex";
    if (home) home.style.display = "block";
    setLogScope("dashboard", "لوحة القيادة");
    window.scrollTo({ top: 0, behavior: "smooth" });
}
