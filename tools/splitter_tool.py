from datetime import datetime


def run(engine, options):
    ts = datetime.now().strftime("%H:%M:%S")
    res = engine.split_pdf(layout=options.get("layout", "2x2"))
    if res.get("ok"):
        return {"ok": True, "message": f"تم استخراج {res.get('parts', 0)} أجزاء.", "timestamp": ts}
    return {"ok": False, "message": res.get("message", "فشل التنفيذ"), "timestamp": ts}
