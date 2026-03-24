from datetime import datetime


def run(engine, options):
    ts = datetime.now().strftime("%H:%M:%S")
    res = engine.stamp_pdfs(
        filter_mode=options.get("filter_mode", "zn_only"),
        x=float(options.get("x", 20)),
        y=float(options.get("y", 20)),
        w=float(options.get("w", 150)),
        h=float(options.get("h", 80)),
    )
    if not res.get("ok"):
        return {"ok": False, "message": res.get("message", "فشل التنفيذ"), "timestamp": ts}
    return {
        "ok": True,
        "message": f"تم ختم {res['success']} من أصل {res['total']} ملف PDF.",
        "timestamp": ts,
    }
