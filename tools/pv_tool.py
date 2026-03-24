from datetime import datetime


def run(engine, options):
    ts = datetime.now().strftime("%H:%M:%S")
    res = engine.process_pv(
        do_convert=bool(options.get("do_convert", True)),
        do_merge=bool(options.get("do_merge", True)),
        do_sort=bool(options.get("do_sort", True)),
    )
    if not res.get("ok"):
        return {"ok": False, "message": res.get("message", "فشل التنفيذ"), "timestamp": ts}
    return {
        "ok": True,
        "message": f"PV اكتمل بعدد عمليات: {res['log_count']}، وأخطاء: {res['errors']}.",
        "timestamp": ts,
    }
