from datetime import datetime


def run(engine, options):
    ts = datetime.now().strftime("%H:%M:%S")
    res = engine.convert_office(
        do_word=bool(options.get("do_word", True)),
        do_excel=bool(options.get("do_excel", True)),
        paper_size=options.get("paper_size", "A4"),
    )
    if not res.get("ok"):
        return {"ok": False, "message": res.get("message", "فشل التنفيذ"), "timestamp": ts}
    return {
        "ok": True,
        "message": f"تم تحويل {res['success']} ملف، مع {res['errors']} أخطاء.",
        "timestamp": ts,
    }
