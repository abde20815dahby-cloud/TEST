from datetime import datetime


def run(engine):
    ts = datetime.now().strftime("%H:%M:%S")
    res = engine.launch_acme()
    return {"ok": bool(res.get("ok")), "message": res.get("message", ""), "timestamp": ts}
