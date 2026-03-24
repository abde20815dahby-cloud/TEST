from datetime import datetime


def run(engine, options):
    ts = datetime.now().strftime("%H:%M:%S")
    src_folder = options.get("source_folder", "")
    exe_path = options.get("exe_path", "")
    res = engine.run_kgo_torinex(src_folder=src_folder, exe_path=exe_path)
    return {
        "ok": bool(res.get("ok", False)),
        "message": res.get("message", "فشل تنفيذ KGO"),
        "timestamp": ts,
    }

